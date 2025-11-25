"""
Utility script to populate the database with synthetic transactions.
Intended for Docker Compose bootstrap and local demos.
"""

from __future__ import annotations

import argparse

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
