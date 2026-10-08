# Aqua Rover 

**An AI-integrated semi-autonomous water-surface rover designed to detect and help collect floating waste, especially plastic.**

Aqua Rover combines computer vision, edge computing, backend services, and a web dashboard to monitor water bodies and identify floating debris in real-time.

---

##  Project Overview

- **Primary Product:** Aqua Rover
- **Core Mission:** Detect floating plastic waste (bottles, bags, wrappers, cups, mixed waste)
- **AI Inference:** Runs locally on **Jetson Orin Nano Super** for low-latency operation
- **Cloud:** AWS used selectively for storage, deployment, and monitoring
- **Offline Capability:** Rover retains essential local operation without internet

---

##  System Architecture
  
```text
Camera
  ↓
Jetson Orin Nano Super (Edge AI)
  ↓
YOLO / Computer Vision
  ↓
Detection + Telemetry (JSON)
  ↓
FastAPI Backend
  ↓
PostgreSQL
  ↓
AWS (where required)
  ↓
React Web Dashboard
