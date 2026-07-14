"""
Insert sample data into the local SupportFlow database.

Run this script once during development:

    python seed.py

The script skips insertion when customer data already exists so the same sample
records are not added repeatedly.
"""

from sqlalchemy import select

from db import SessionLocal, init_db
from models import Customer, Ticket


# Ensure the database tables exist before inserting sample records.
init_db()


with SessionLocal() as db:
    # Check for one existing customer rather than loading every customer row.
    existing_customer = db.scalar(
        select(Customer).limit(1)
    )

    if existing_customer is not None:
        print(
            "Database already contains data. Seed skipped."
        )
    else:
        # Create two fictional B2B customer accounts.
        acme = Customer(
            company_name="Acme Analytics",
            contact_name="Maya Chen",
            email="maya@acme.example",
            account_tier="Enterprise",
        )

        northstar = Customer(
            company_name="Northstar Labs",
            contact_name="Jordan Patel",
            email="jordan@northstar.example",
            account_tier="Growth",
        )

        db.add_all([acme, northstar])

        # flush() assigns database IDs without committing the transaction.
        # Those IDs are needed to create the related sample tickets.
        db.flush()

        # Create realistic sample support requests.
        db.add_all(
            [
                Ticket(
                    customer_id=acme.id,
                    subject="Slack notifications are delayed",
                    description=(
                        "Support notifications arrive "
                        "10–15 minutes late."
                    ),
                    priority="High",
                    assigned_to="Richard",
                ),
                Ticket(
                    customer_id=northstar.id,
                    subject="Unable to invite new support agent",
                    description=(
                        "Admin receives an error while "
                        "inviting a teammate."
                    ),
                    priority="Urgent",
                    assigned_to=None,
                ),
            ]
        )

        # Commit customers and tickets as one transaction.
        db.commit()

        print("Sample data created.")
