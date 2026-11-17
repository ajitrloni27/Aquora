#!/usr/bin/env python3
"""
Aqua Rover Jetson Edge Simulator.

Simulates an on-board NVIDIA Jetson Orin Nano Super running YOLO inference
and sensor acquisitions. Periodically sends JSON telemetry and detection
payloads to the FastAPI backend over HTTP.

Features:
- Periodic telemetry transmission (battery, GPS location, speed, temperature, signal).
- Periodic YOLO-style plastic detection batches with valid bounding boxes.
- Resilient offline buffering: if the backend is unreachable, payloads are
  queued locally and automatically retried once connectivity is restored.
- Configurable via CLI flags: --base-url, --rover-id, --interval, --max-iterations.
"""

import argparse
import random
import sys
import time
from collections import deque
from datetime import datetime, timezone
from typing import Any, Deque, Dict, List, Optional

import httpx

# Classes commonly detected in floating marine plastic waste
DETECTION_CLASSES = [
    "plastic_bottle",
    "plastic_bag",
    "plastic_wrapper",
    "plastic_cup",
    "styrofoam_fragment",
    "mixed_plastic",
]

# Operational statuses for the rover
ROVER_STATUSES = ["moving", "scanning", "collecting", "patrolling"]


class JetsonSimulator:
    def __init__(
        self,
        base_url: str,
        rover_id: str,
        interval: float = 3.0,
        detection_chance: float = 0.6,
        max_buffer_size: int = 1000,
    ):
        self.base_url = base_url.rstrip("/")
        self.rover_id = rover_id
        self.interval = interval
        self.detection_chance = detection_chance

        # Offline FIFO buffers
        self.telemetry_buffer: Deque[Dict[str, Any]] = deque(maxlen=max_buffer_size)
        self.detections_buffer: Deque[Dict[str, Any]] = deque(maxlen=max_buffer_size)

        # Initial simulated state
        self.battery = 98.0
        self.latitude = 15.3015
        self.longitude = 74.1270
        self.speed = 0.75
        self.temperature = 28.5
        self.signal = 92.0
        self.detection_counter = 0

    def generate_telemetry_payload(self) -> Dict[str, Any]:
        """Generates realistic telemetry simulating rover movement and battery drain."""
        # Realistic slow battery drain
        self.battery = max(5.0, round(self.battery - random.uniform(0.02, 0.08), 2))

        # Small GPS drift simulating autonomous patrol on a water body
        self.latitude = round(self.latitude + random.uniform(-0.00015, 0.00015), 6)
        self.longitude = round(self.longitude + random.uniform(-0.00015, 0.00015), 6)

        # Fluctuations in speed, temperature, and wireless signal
        self.speed = round(max(0.0, random.uniform(0.3, 1.4)), 2)
        self.temperature = round(28.0 + random.uniform(-1.5, 2.5), 1)
        self.signal = round(min(100.0, max(20.0, 90.0 + random.uniform(-10.0, 8.0))), 1)
        status = random.choice(ROVER_STATUSES)

        return {
            "rover_id": self.rover_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "battery": self.battery,
            "speed": self.speed,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "status": status,
            "temperature": self.temperature,
            "signal": self.signal,
        }

    def generate_detections_payload(self) -> Dict[str, Any]:
        """Generates YOLO detection batches with valid bounding box coordinates."""
        num_items = random.randint(1, 3)
        detections: List[Dict[str, Any]] = []

        # Assume 1280x720 video frame
        frame_w, frame_h = 1280.0, 720.0

        for _ in range(num_items):
            self.detection_counter += 1
            class_name = random.choice(DETECTION_CLASSES)
            confidence = round(random.uniform(0.72, 0.98), 2)

            # Generate valid bbox: x1 < x2, y1 < y2
            w = random.uniform(60.0, 250.0)
            h = random.uniform(40.0, 200.0)
            x1 = round(random.uniform(20.0, frame_w - w - 20.0), 1)
            y1 = round(random.uniform(20.0, frame_h - h - 20.0), 1)
            x2 = round(x1 + w, 1)
            y2 = round(y1 + h, 1)

            detections.append(
                {
                    "class_name": class_name,
                    "confidence": confidence,
                    "bbox": [x1, y1, x2, y2],
                    "image_ref": f"snapshots/{self.rover_id}_det_{self.detection_counter}.jpg",
                }
            )

        return {
            "rover_id": self.rover_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "detections": detections,
        }

    def _flush_buffer(
        self, client: httpx.Client, endpoint: str, buffer: Deque[Dict[str, Any]], label: str
    ) -> bool:
        """Flushes buffered payloads. Returns False immediately if connectivity is lost."""
        if not buffer:
            return True

        print(f"[BUFFER] Attempting to flush {len(buffer)} queued {label} item(s)...")
        while buffer:
            payload = buffer[0]
            try:
                resp = client.post(f"{self.base_url}{endpoint}", json=payload, timeout=3.0)
                if resp.status_code == 201:
                    buffer.popleft()
                elif resp.status_code == 404:
                    print(f"[ERROR] 404 Rover '{self.rover_id}' not registered on server! Register rover first.")
                    return False
                else:
                    print(f"[WARN] Server returned status {resp.status_code} while flushing {label}. Leaving in buffer.")
                    return False
            except httpx.RequestError as exc:
                print(f"[RETRY] Connection failed during {label} flush ({exc}). Remaining in queue: {len(buffer)}")
                return False

        print(f"[SUCCESS] All queued {label} records successfully synced.")
        return True

    def _send_payload(
        self, client: httpx.Client, endpoint: str, payload: Dict[str, Any], buffer: Deque[Dict[str, Any]], label: str
    ):
        """Sends payload or appends to buffer if offline."""
        # Try flushing older buffered items first
        if buffer:
            if not self._flush_buffer(client, endpoint, buffer, label):
                buffer.append(payload)
                print(f"[OFFLINE] Connection down. Queued current {label} (Buffer: {len(buffer)})")
                return

        try:
            resp = client.post(f"{self.base_url}{endpoint}", json=payload, timeout=3.0)
            if resp.status_code == 201:
                if label == "telemetry":
                    print(
                        f"[TELEMETRY] Sent: Battery={payload['battery']}% | Speed={payload['speed']}m/s | "
                        f"Lat={payload['latitude']}, Lon={payload['longitude']} | Status={payload['status']}"
                    )
                else:
                    dets = ", ".join(f"{d['class_name']}({int(d['confidence']*100)}%)" for d in payload["detections"])
                    print(f"[DETECTION] Sent batch ({len(payload['detections'])} items): {dets}")
            elif resp.status_code == 404:
                print(f"[ERROR] Rover '{self.rover_id}' not found (404). Ensure rover is seeded/registered on backend.")
            else:
                print(f"[WARN] HTTP {resp.status_code} on {endpoint}: {resp.text}. Queuing to buffer.")
                buffer.append(payload)
        except httpx.RequestError as exc:
            buffer.append(payload)
            print(f"[OFFLINE] Failed to send {label} ({type(exc).__name__}). Queued to buffer (Total queued: {len(buffer)})")

    def run(self, max_iterations: Optional[int] = None):
        """Main simulator execution loop."""
        print("=" * 70)
        print("  Aqua Rover Jetson Edge Simulator")
        print(f"  Target: {self.base_url}  |  Rover ID: {self.rover_id}  |  Interval: {self.interval}s")
        print("  Press Ctrl+C to terminate.")
        print("=" * 70)

        with httpx.Client() as client:
            iterations = 0
            try:
                while True:
                    iterations += 1

                    # 1. Generate & send telemetry
                    telemetry = self.generate_telemetry_payload()
                    self._send_payload(
                        client, "/rover/telemetry", telemetry, self.telemetry_buffer, "telemetry"
                    )

                    # 2. Periodically generate & send YOLO detection batch
                    if random.random() < self.detection_chance:
                        detections = self.generate_detections_payload()
                        self._send_payload(
                            client, "/detections", detections, self.detections_buffer, "detections"
                        )

                    if max_iterations and iterations >= max_iterations:
                        print(f"[DONE] Completed {max_iterations} iteration(s). Exiting cleanly.")
                        break

                    time.sleep(self.interval)
            except KeyboardInterrupt:
                print("\n[STOP] Simulator stopped by user. Cleaning up.")


def main():
    parser = argparse.ArgumentParser(description="Simulate Jetson Orin Nano edge client for Aqua Rover")
    parser.add_argument(
        "--base-url",
        type=str,
        default="http://localhost:8000",
        help="FastAPI backend base URL (default: http://localhost:8000)",
    )
    parser.add_argument(
        "--rover-id",
        type=str,
        default="AR-001",
        help="Rover identifier to transmit as (default: AR-001)",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=3.0,
        help="Transmission interval in seconds (default: 3.0)",
    )
    parser.add_argument(
        "--detection-chance",
        type=float,
        default=0.6,
        help="Probability of detecting floating waste per cycle (default: 0.6)",
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=None,
        help="Max cycles to run before terminating (default: infinite)",
    )

    args = parser.parse_args()
    simulator = JetsonSimulator(
        base_url=args.base_url,
        rover_id=args.rover_id,
        interval=args.interval,
        detection_chance=args.detection_chance,
    )
    simulator.run(max_iterations=args.max_iterations)


if __name__ == "__main__":
    main()
