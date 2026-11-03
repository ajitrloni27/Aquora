import sys
from pathlib import Path
from typing import Optional
from sqlalchemy.orm import Session

# Add backend root to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.db.session import SessionLocal
from app.models.rover import Rover


def seed_rover(
    rover_id: str = "AR-001",
    name: str = "Aqua Rover Alpha",
    status: str = "active",
    db: Optional[Session] = None,
) -> Rover:
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True
    try:
        rover = db.query(Rover).filter(Rover.rover_id == rover_id).first()
        if rover:
            print(f"[Seed] Rover '{rover_id}' already exists (ID: {rover.id}). Skipping.")
            return rover

        new_rover = Rover(
            rover_id=rover_id,
            name=name,
            status=status,
        )
        db.add(new_rover)
        db.commit()
        db.refresh(new_rover)
        print(f"[Seed] Successfully seeded rover '{rover_id}' ({name}) with status '{status}' (ID: {new_rover.id}).")
        return new_rover
    finally:
        if close_db:
            db.close()


if __name__ == "__main__":
    seed_rover()
