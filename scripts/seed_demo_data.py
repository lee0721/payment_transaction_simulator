"""
Utility script to populate the database with synthetic transactions.
Intended for Docker Compose bootstrap and local demos.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.database import Base, engine
from worker import tasks


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed demo transactions.")
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="Number of synthetic transactions to create.",
    )
    args = parser.parse_args()

    Base.metadata.create_all(bind=engine)
    created = tasks.seed_synthetic_transactions(batch_size=args.batch_size)
    print(f"Seeded {len(created)} demo transactions.")


if __name__ == "__main__":
    main()
