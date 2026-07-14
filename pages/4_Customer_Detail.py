"""
Customer detail page for SupportFlow.

This page displays:

- Customer account information.
- Total, open, and resolved ticket counts.
- All support tickets connected to the customer.
- Recent ticket activity.
- Direct navigation to an individual Ticket Detail page.
"""

import streamlit as st
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from db import SessionLocal, init_db
from models import Customer, Ticket, TicketUpdate


# Configure the Streamlit browser tab and page layout.
st.set_page_config(
    page_title="Customer Detail | SupportFlow",
    page_icon="🏢",
    layout="wide",
)


# Create any missing database tables.
#
# Existing tables and data are not changed.
init_db()


# Display the page heading.
st.title("Customer Detail")


# Load all customers in alphabetical order.
with SessionLocal() as db:
    customers = db.scalars(
        select(Customer).order_by(Customer.company_name)
    ).all()


# Stop the page when no customers exist.
if not customers:
    st.info("No customers are available.")
    st.stop()


# Build readable dropdown labels connected to customer database IDs.
#
# Example:
#
#     "Acme Analytics — Maya Chen": 1
customer_options = {
    (
        f"{customer.company_name} — "
        f"{customer.contact_name}"
    ): customer.id
    for customer in customers
}


# Create a list of the labels that will appear in the dropdown.
customer_labels = list(customer_options.keys())


# Check whether another page stored a selected customer ID.
#
# The Customers page will save this value when the user clicks Open customer.
stored_customer_id = st.session_state.get(
    "selected_customer_id"
)


# Default to the first customer in the dropdown.
default_customer_index = 0


# If a selected customer ID exists, find its position in the dropdown list.
if stored_customer_id is not None:
    for index, label in enumerate(customer_labels):
        if customer_options[label] == stored_customer_id:
            default_customer_index = index
            break


# Allow the user to choose a customer.
#
# When the page was opened from the Customers page, the correct customer will
# already be selected.
selected_customer_label = st.selectbox(
    "Select a customer",
    customer_labels,
    index=default_customer_index,
)


# Convert the readable dropdown label into a database customer ID.
selected_customer_id = customer_options[
    selected_customer_label
]


# Keep Session State synchronized when the user manually selects another
# customer.
st.session_state["selected_customer_id"] = (
    selected_customer_id
)


# Load the selected customer and all related tickets.
#
# selectinload() ensures the tickets remain available after the database
# session closes.
with SessionLocal() as db:
    selected_customer = db.scalar(
        select(Customer)
        .options(
            selectinload(Customer.tickets)
        )
        .where(
            Customer.id == selected_customer_id
        )
    )


# Protect against the customer being deleted or unavailable.
if selected_customer is None:
    st.error("The selected customer could not be found.")
    st.stop()


# Load ticket statistics for the selected customer.
with SessionLocal() as db:
    total_tickets = (
        db.scalar(
            select(func.count(Ticket.id))
            .where(
                Ticket.customer_id
                == selected_customer.id
            )
        )
        or 0
    )

    open_tickets = (
        db.scalar(
            select(func.count(Ticket.id))
            .where(
                Ticket.customer_id
                == selected_customer.id,
                Ticket.status != "Resolved",
            )
        )
        or 0
    )

    resolved_tickets = (
        db.scalar(
            select(func.count(Ticket.id))
            .where(
                Ticket.customer_id
                == selected_customer.id,
                Ticket.status == "Resolved",
            )
        )
        or 0
    )

    urgent_tickets = (
        db.scalar(
            select(func.count(Ticket.id))
            .where(
                Ticket.customer_id
                == selected_customer.id,
                Ticket.priority == "Urgent",
                Ticket.status != "Resolved",
            )
        )
        or 0
    )


# Display the customer company name prominently.
st.subheader(selected_customer.company_name)


# Display customer information and account statistics side by side.
customer_column, metrics_column = st.columns(
    [2, 3]
)


# Display the primary customer account details.
with customer_column:
    st.markdown("### Account information")

    st.write(
        f"**Primary contact:** "
        f"{selected_customer.contact_name}"
    )

    st.write(
        f"**Email:** "
        f"{selected_customer.email}"
    )

    st.write(
        f"**Account tier:** "
        f"{selected_customer.account_tier}"
    )

    st.write(
        f"**Customer since:** "
        f"{selected_customer.created_at:%Y-%m-%d}"
    )


# Display customer support statistics.
with metrics_column:
    st.markdown("### Support summary")

    metric_1, metric_2, metric_3, metric_4 = st.columns(
        4
    )

    metric_1.metric(
        "Total tickets",
        total_tickets,
    )

    metric_2.metric(
        "Open tickets",
        open_tickets,
    )

    metric_3.metric(
        "Resolved",
        resolved_tickets,
    )

    metric_4.metric(
        "Urgent",
        urgent_tickets,
    )


st.divider()


# Display the customer's tickets.
st.markdown("### Ticket history")


# Sort the already-loaded tickets so the newest tickets appear first.
customer_tickets = sorted(
    selected_customer.tickets,
    key=lambda ticket: ticket.created_at,
    reverse=True,
)


# Display a message when the customer has never submitted a ticket.
if not customer_tickets:
    st.info(
        "This customer does not have any support tickets."
    )
else:
    # Display each ticket inside a compact bordered card.
    for ticket in customer_tickets:
        with st.container(border=True):
            details_column, status_column = st.columns(
                [4, 1]
            )

            with details_column:
                # Display the ticket number and subject.
                st.markdown(
                    f"#### #{ticket.id} — "
                    f"{ticket.subject}"
                )

                # Display the ticket's main workflow information, including the
                # communication channel that created the request.
                st.write(
                    f"**Priority:** "
                    f"{ticket.priority}  \n"
                    f"**Channel:** "
                    f"{ticket.channel}  \n"
                    f"**Assigned to:** "
                    f"{ticket.assigned_to or 'Unassigned'}  \n"
                    f"**Created:** "
                    f"{ticket.created_at:%Y-%m-%d %I:%M %p}"
                )

                # Display a shortened description in the customer history.
                if len(ticket.description) > 200:
                    description_preview = (
                        ticket.description[:200].rstrip()
                        + "..."
                    )
                else:
                    description_preview = (
                        ticket.description
                    )

                st.write(description_preview)

                # Open this ticket directly on the Ticket Detail page.
                if st.button(
                    "Open ticket",
                    key=(
                        f"customer_open_ticket_"
                        f"{ticket.id}"
                    ),
                ):
                    # Store the selected ticket ID.
                    st.session_state[
                        "selected_ticket_id"
                    ] = ticket.id

                    # Switch to the Ticket Detail page.
                    st.switch_page(
                        "pages/3_Ticket_Detail.py"
                    )

            with status_column:
                # Keep the current status easy to scan.
                st.markdown("**Status**")
                st.write(ticket.status)


st.divider()


# Display recent activity connected to this customer's tickets.
st.markdown("### Recent activity")


# Query activity records through the customer's ticket IDs.
with SessionLocal() as db:
    recent_updates = db.execute(
        select(
            TicketUpdate,
            Ticket.subject,
            Ticket.id,
        )
        .join(
            Ticket,
            TicketUpdate.ticket_id == Ticket.id,
        )
        .where(
            Ticket.customer_id
            == selected_customer.id
        )
        .order_by(
            TicketUpdate.created_at.desc()
        )
        .limit(10)
    ).all()


# Display a message when no ticket activity exists.
if not recent_updates:
    st.info(
        "No ticket activity has been recorded "
        "for this customer."
    )
else:
    # Each result contains the TicketUpdate object, ticket subject, and ID.
    for update, ticket_subject, ticket_id in recent_updates:
        with st.container(border=True):
            # Display the type of conversation entry or activity event.
            st.write(
                f"**{update.update_type}**"
            )

            # Show who created the message, note, or system event.
            st.caption(
                f"Author: {update.author}"
            )

            # Display the message, note, or event description.
            st.write(update.update_text)

            # Show the related ticket and the time the activity was recorded.
            st.caption(
                f"Ticket #{ticket_id} — "
                f"{ticket_subject} · "
                f"{update.created_at:%Y-%m-%d %I:%M %p}"
            )