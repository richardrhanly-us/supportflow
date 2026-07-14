"""
Ticket detail page for SupportFlow.

This page allows the user to select one support ticket, review its full details,
change its status, add an internal note, and view its activity history.
"""

from datetime import datetime

import streamlit as st
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from db import SessionLocal, init_db
from models import Ticket, TicketUpdate


# Configure this Streamlit page.
st.set_page_config(
    page_title="Ticket Detail | SupportFlow",
    page_icon="🔎",
    layout="wide",
)


# Ensure the required database tables exist.
init_db()


# Display the page title.
st.title("Ticket Detail")


# Load all tickets and their related customer records.
#
# selectinload() ensures the customer data is available after the database
# session closes.
with SessionLocal() as db:
    tickets = db.scalars(
        select(Ticket)
        .options(selectinload(Ticket.customer))
        .order_by(Ticket.created_at.desc())
    ).all()


# Stop the page if no tickets exist yet.
if not tickets:
    st.info("No tickets are available.")
    st.stop()


# Build a dictionary for the ticket selection dropdown.
#
# The user sees a readable label, while the application stores the ticket ID.
ticket_options = {
    (
        f"#{ticket.id} — {ticket.subject} "
        f"({ticket.customer.company_name})"
    ): ticket.id
    for ticket in tickets
}


# Create a list of the readable ticket labels used by the dropdown.
ticket_labels = list(ticket_options.keys())


# Check whether another page stored a selected ticket ID in Session State.
#
# This happens when the user clicks Open ticket on the Tickets page.
stored_ticket_id = st.session_state.get("selected_ticket_id")


# Default to the first ticket in the dropdown.
default_ticket_index = 0


# If a stored ticket ID exists, find the matching position in the dropdown.
if stored_ticket_id is not None:
    for index, label in enumerate(ticket_labels):
        if ticket_options[label] == stored_ticket_id:
            default_ticket_index = index
            break


# Display the ticket dropdown.
#
# The index value automatically selects the ticket that was opened from the
# Tickets page.
selected_ticket_label = st.selectbox(
    "Select a ticket",
    ticket_labels,
    index=default_ticket_index,
)


# Convert the readable dropdown selection into a database ticket ID.
selected_ticket_id = ticket_options[selected_ticket_label]


# Keep Session State synchronized if the user manually chooses another ticket.
st.session_state["selected_ticket_id"] = selected_ticket_id


# Reload the selected ticket in a new database session.
#
# Load both the customer and updates relationships while the session is open.
with SessionLocal() as db:
    selected_ticket = db.scalar(
        select(Ticket)
        .options(
            selectinload(Ticket.customer),
        )
        .where(Ticket.id == selected_ticket_id)
    )


# Protect against the ticket being deleted or unavailable.
if selected_ticket is None:
    st.error("The selected ticket could not be found.")
    st.stop()


# Display the ticket heading.
st.subheader(
    f"#{selected_ticket.id} — {selected_ticket.subject}"
)


# Create two columns for ticket and customer information.
left_column, right_column = st.columns(2)


# Display the ticket workflow information.
with left_column:
    st.markdown("### Ticket information")

    st.write(
        f"**Status:** {selected_ticket.status}"
    )

    st.write(
        f"**Priority:** {selected_ticket.priority}"
    )

    # Display the communication source for the support request.
    #
    # This helps model an omnichannel B2B support workflow such as Slack,
    # Microsoft Teams, email, web chat, or manually entered tickets.
    st.write(
        f"**Channel:** {selected_ticket.channel}"
    )

    st.write(
        f"**Assigned to:** "
        f"{selected_ticket.assigned_to or 'Unassigned'}"
    )

    st.write(
        f"**Created:** "
        f"{selected_ticket.created_at:%Y-%m-%d %I:%M %p}"
    )

    if selected_ticket.resolved_at:
        st.write(
            f"**Resolved:** "
            f"{selected_ticket.resolved_at:%Y-%m-%d %I:%M %p}"
        )


# Display information about the customer connected to the ticket.
with right_column:
    st.markdown("### Customer information")

    st.write(
        f"**Company:** "
        f"{selected_ticket.customer.company_name}"
    )

    st.write(
        f"**Contact:** "
        f"{selected_ticket.customer.contact_name}"
    )

    st.write(
        f"**Email:** "
        f"{selected_ticket.customer.email}"
    )

    st.write(
        f"**Account tier:** "
        f"{selected_ticket.customer.account_tier}"
    )


# Display the original ticket description.
st.markdown("### Description")

st.write(selected_ticket.description)


# Define valid status values.
status_choices = [
    "Open",
    "In Progress",
    "Waiting on Customer",
    "Resolved",
]


# Create a dropdown that begins on the ticket's current status.
new_status = st.selectbox(
    "Update status",
    status_choices,
    index=status_choices.index(selected_ticket.status),
)


# Select the kind of conversation message or activity being recorded.
#
# Customer messages and agent replies represent the external conversation.
# Internal notes remain visible only as support-team context in this MVP.
activity_type = st.selectbox(
    "Activity type",
    [
        "Customer message",
        "Agent reply",
        "Internal note",
    ],
)


# Suggest an appropriate author based on the selected activity type.
#
# The user can still replace the suggested value before saving.
if activity_type == "Customer message":
    suggested_author = selected_ticket.customer.contact_name
elif activity_type == "Agent reply":
    suggested_author = (
        selected_ticket.assigned_to
        or "Support Agent"
    )
else:
    suggested_author = "Support Team"


# Record who wrote the message or note.
activity_author = st.text_input(
    "Author",
    value=suggested_author,
)


# Collect the content that will be stored in the conversation timeline.
activity_text = st.text_area(
    "Message or note",
    placeholder=(
        "Enter a customer message, agent reply, "
        "or internal support note."
    ),
)


# Place the status and conversation actions side by side.
status_column, activity_column = st.columns(2)


# Update the ticket status.
# Update the ticket status and record the change in the activity history.
if status_column.button("Save status"):
    with SessionLocal() as db:
        db_ticket = db.get(
            Ticket,
            selected_ticket.id,
        )

        if db_ticket is None:
            st.error("The ticket could not be found.")
        else:
            # Preserve the old status so the activity log can describe
            # exactly what changed.
            previous_status = db_ticket.status

            db_ticket.status = new_status

            # Add a resolution timestamp only when the ticket is resolved.
            db_ticket.resolved_at = (
                datetime.utcnow()
                if new_status == "Resolved"
                else None
            )

            db.add(
                TicketUpdate(
                    ticket_id=db_ticket.id,
                    update_text=(
                        f"Status changed from "
                        f"{previous_status} to {new_status}."
                    ),
                    update_type="Status change",

                    # Status changes are generated by the application rather than
                    # entered as customer or agent conversation messages.
                    author="System",
                )
            )

            db.commit()

        st.success("Status updated.")
        st.rerun()


# Add a customer message, agent reply, or internal note to the timeline.
if activity_column.button("Add activity"):
    # Prevent empty authors and empty messages from being saved.
    if not activity_author.strip():
        st.error("Enter an author.")
    elif not activity_text.strip():
        st.error("Enter a message or note.")
    else:
        with SessionLocal() as db:
            # Store the new conversation entry as a TicketUpdate record.
            db.add(
                TicketUpdate(
                    ticket_id=selected_ticket.id,
                    update_text=activity_text.strip(),
                    update_type=activity_type,
                    author=activity_author.strip(),
                )
            )

            db.commit()

        st.success("Activity added.")
        st.rerun()


# Display the activity history.
st.markdown("### Conversation and Activity Timeline")


# Query the activity table directly so the page always displays the newest
# saved notes and status changes.
with SessionLocal() as db:
    updates = db.scalars(
        select(TicketUpdate)
        .where(
            TicketUpdate.ticket_id == selected_ticket.id
        )
        .order_by(
            TicketUpdate.created_at.desc()
        )
    ).all()


if not updates:
    st.info("No activity has been recorded for this ticket.")
else:
    for update in updates:
        with st.container(border=True):
            # Display the activity type as the entry heading.
            st.write(
                f"**{update.update_type}**"
            )

            # Show who created the conversation entry or system event.
            st.caption(
                f"Author: {update.author}"
            )

            # Display the message, note, or event description.
            st.write(update.update_text)

            # Display the time the entry was recorded.
            st.caption(
                f"{update.created_at:%Y-%m-%d %I:%M %p}"
            )