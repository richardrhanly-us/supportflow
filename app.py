"""
Main dashboard page for SupportFlow.

Streamlit runs this file when the application starts. The page summarizes
customer and ticket activity and displays the most recently created tickets.
"""

import streamlit as st
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from db import SessionLocal, init_db
from models import Customer, Ticket


# Configure the browser tab and use a wide layout for dashboard metrics.
st.set_page_config(
    page_title="SupportFlow",
    page_icon="🎫",
    layout="wide",
)


# Ensure the required database tables exist before running any queries.
init_db()


# Page heading and brief product description.
st.title("SupportFlow")
st.caption("B2B customer support operations dashboard")


# Open one database session and calculate the dashboard totals.
with SessionLocal() as db:
    # Count every customer account.
    total_customers = (
        db.scalar(select(func.count(Customer.id))) or 0
    )

    # Treat every ticket except Resolved as open work.
    open_tickets = (
        db.scalar(
            select(func.count(Ticket.id)).where(
                Ticket.status != "Resolved"
            )
        )
        or 0
    )

    # Count urgent tickets that still need attention.
    urgent_tickets = (
        db.scalar(
            select(func.count(Ticket.id)).where(
                Ticket.priority == "Urgent",
                Ticket.status != "Resolved",
            )
        )
        or 0
    )

    # Count tickets that have completed the support workflow.
    resolved_tickets = (
        db.scalar(
            select(func.count(Ticket.id)).where(
                Ticket.status == "Resolved"
            )
        )
        or 0
    )


# Display the four summary measurements in one horizontal row.
col1, col2, col3, col4 = st.columns(4)
col1.metric("Customers", total_customers)
col2.metric("Open tickets", open_tickets)
col3.metric("Urgent tickets", urgent_tickets)
col4.metric("Resolved tickets", resolved_tickets)


st.subheader("Recent tickets")


# Retrieve only the ten newest tickets for the dashboard preview.
with SessionLocal() as db:
    tickets = db.scalars(
        select(Ticket)
        .options(selectinload(Ticket.customer))
        .order_by(Ticket.created_at.desc())
        .limit(10)
    ).all()


# Show an instructional message when the database contains no tickets.
if not tickets:
    st.info(
        "No tickets yet. Add a customer, then create your first ticket."
    )
else:
    # Display each ticket in a bordered container for easy scanning.
    for ticket in tickets:
        with st.container(border=True):
            left, right = st.columns([4, 1])

            left.markdown(
                f"**#{ticket.id} — {ticket.subject}**"
            )
            left.write(
                f"{ticket.customer.company_name} · "
                f"{ticket.priority} priority · "
                f"Assigned to: {ticket.assigned_to or 'Unassigned'}"
            )

            # Keep the current status visually separated on the right.
            right.write(f"**{ticket.status}**")
