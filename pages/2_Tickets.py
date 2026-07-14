"""
Ticket queue page for SupportFlow.

This page allows the user to:

- Create a support ticket.
- Filter tickets by status.
- Filter tickets by priority.
- Search ticket subjects and descriptions.
- Review a compact list of matching tickets.

Detailed ticket management, including status updates, internal notes, and
activity history, is handled on the Ticket Detail page.
"""

import streamlit as st

# or_ combines search conditions using OR logic.
# select creates SQLAlchemy SELECT queries.
from sqlalchemy import or_, select

# selectinload loads each ticket's related customer record before the database
# session closes.
from sqlalchemy.orm import selectinload

# Import the database session factory and initialization function.
from db import SessionLocal, init_db

# This page only needs the Customer and Ticket models.
from models import Customer, Ticket

def suggest_priority(subject: str, description: str) -> str:
    """
    Recommend a ticket priority using simple keyword-based triage rules.

    The function combines the subject and description, converts the text to
    lowercase, and checks for terms associated with urgent or high-impact
    support problems.

    This is a transparent rule-based recommendation rather than a machine
    learning model. The user can still override the suggested value.
    """

    # Combine both ticket fields into one searchable string.
    ticket_text = f"{subject} {description}".lower()

    # Terms that suggest a severe outage, security issue, or complete blocker.
    urgent_terms = [
        "outage",
        "system down",
        "production down",
        "critical",
        "security breach",
        "data loss",
        "cannot access",
        "completely blocked",
    ]

    # Terms that suggest major degradation without a complete outage.
    high_terms = [
        "blocked",
        "error",
        "failing",
        "unable to",
        "not working",
        "delayed",
        "degraded",
        "login issue",
    ]

    # Return Urgent as soon as one urgent term is found.
    if any(term in ticket_text for term in urgent_terms):
        return "Urgent"

    # Return High when no urgent term matched but a high-impact term did.
    if any(term in ticket_text for term in high_terms):
        return "High"

    # Use Medium as the default recommendation for ordinary support requests.
    return "Medium"

# Configure the browser tab and use a wide layout for the ticket queue.
st.set_page_config(
    page_title="Tickets | SupportFlow",
    page_icon="🎫",
    layout="wide",
)


# Create any missing database tables.
#
# Existing tables and data are not overwritten.
init_db()


# Display the main page heading.
st.title("Tickets")

st.caption(
    "Create, search, and filter support tickets. "
    "Use the Ticket Detail page to update a ticket or add notes."
)


# Load all customers for the ticket creation form.
#
# Customers are sorted alphabetically by company name.
with SessionLocal() as db:
    customers = db.scalars(
        select(Customer).order_by(Customer.company_name)
    ).all()


# A ticket must belong to an existing customer.
#
# If no customer records exist, stop this page and direct the user to create
# one first.
if not customers:
    st.warning(
        "Add at least one customer before creating a ticket."
    )
    st.stop()


# Build a dictionary for the customer dropdown.
#
# The user sees a readable company and contact label, while the application
# stores the corresponding customer database ID.
customer_options = {
    f"{customer.company_name} — {customer.contact_name}": customer.id
    for customer in customers
}


# Place the ticket creation controls inside an expandable section.
#
# These widgets are not inside a Streamlit form so the page reruns whenever
# the subject or description changes. This allows the priority recommendation
# to update immediately while the user enters the ticket.
with st.expander("Create ticket", expanded=False):
    # Select the customer connected to the new ticket.
    selected_customer = st.selectbox(
        "Customer",
        list(customer_options.keys()),
        key="new_ticket_customer",
    )

    # Enter the ticket subject.
    subject = st.text_input(
        "Subject",
        key="new_ticket_subject",
    )

    # Enter the complete support-request description.
    description = st.text_area(
        "Description",
        key="new_ticket_description",
    )

    # Calculate the recommendation every time Streamlit reruns the page.
    suggested_priority = suggest_priority(
        subject,
        description,
    )

    # Only display a recommendation after the user has entered ticket text.
    if subject.strip() or description.strip():
        st.info(
            f"Suggested priority: {suggested_priority}"
        )
    else:
        st.caption(
            "Enter a subject or description to receive "
            "a priority recommendation."
        )

    # Define the valid priority choices.
    priority_choices = [
        "Low",
        "Medium",
        "High",
        "Urgent",
    ]

    # Allow the user to choose the final priority.
    #
    # The recommendation is displayed above, but the user remains in control
    # of the stored priority value.
    priority = st.selectbox(
        "Priority",
        priority_choices,
        index=priority_choices.index(
            suggested_priority
        ),
        key="new_ticket_priority",
    )

    # Identify where the support request originated.
    channel = st.selectbox(
        "Channel",
        [
            "Slack",
            "Microsoft Teams",
            "Email",
            "Web Chat",
            "Manual",
        ],
        key="new_ticket_channel",
    )

    # Optionally assign the ticket to a support employee.
    assigned_to = st.text_input(
        "Assigned to",
        key="new_ticket_assigned_to",
    )

    # Process ticket creation when the user clicks the button.
    if st.button(
        "Create ticket",
        key="create_ticket_button",
    ):
        # Reject missing or whitespace-only subjects and descriptions.
        if not subject.strip() or not description.strip():
            st.error(
                "Subject and description are required."
            )
        else:
            # Open a database session for the insert operation.
            with SessionLocal() as db:
                ticket = Ticket(
                    customer_id=customer_options[selected_customer],
                    subject=subject.strip(),
                    description=description.strip(),
                    priority=priority,
                    channel=channel,
                    assigned_to=assigned_to.strip() or None,
                )

                db.add(ticket)
                db.commit()

            st.success("Ticket created.")

            # Clear the ticket-entry widgets after the database commit.
            st.session_state["new_ticket_subject"] = ""
            st.session_state["new_ticket_description"] = ""
            st.session_state["new_ticket_assigned_to"] = ""

            # Reload the page so the new ticket appears in the queue.
            st.rerun()


# Separate the creation form from the search and filtering controls.
st.divider()


# Display the queue heading.
st.subheader("Ticket queue")


# Place the search and filters in one horizontal row.
search_column, status_column, priority_column = st.columns(
    [2, 1, 1]
)


# Search ticket subjects and descriptions.
with search_column:
    search_text = st.text_input(
        "Search tickets",
        placeholder="Search by subject or description",
    )


# Filter the queue by workflow status.
with status_column:
    status_filter = st.selectbox(
        "Status",
        [
            "All",
            "Open",
            "In Progress",
            "Waiting on Customer",
            "Resolved",
        ],
    )


# Filter the queue by priority level.
with priority_column:
    priority_filter = st.selectbox(
        "Priority",
        [
            "All",
            "Low",
            "Medium",
            "High",
            "Urgent",
        ],
    )


# Open a database session and construct the ticket query.
with SessionLocal() as db:
    # Begin with every ticket.
    query = (
        select(Ticket)

        # Load the related customer while the session remains open.
        .options(
            selectinload(Ticket.customer)
        )

        # Show the newest tickets first.
        .order_by(
            Ticket.created_at.desc()
        )
    )

    # Add a status condition only when a specific status is selected.
    if status_filter != "All":
        query = query.where(
            Ticket.status == status_filter
        )

    # Add a priority condition only when a specific priority is selected.
    if priority_filter != "All":
        query = query.where(
            Ticket.priority == priority_filter
        )

    # Apply a case-insensitive text search when the user enters text.
    if search_text.strip():
        # Percent signs are SQL wildcard characters.
        #
        # Searching for "login" becomes "%login%", which matches the word
        # anywhere inside the subject or description.
        search_term = f"%{search_text.strip()}%"

        query = query.where(
            or_(
                Ticket.subject.ilike(search_term),
                Ticket.description.ilike(search_term),
            )
        )

    # Execute the completed query and return Ticket objects.
    tickets = db.scalars(query).all()


# Show how many records matched the current search and filters.
st.caption(
    f"{len(tickets)} ticket"
    f"{'' if len(tickets) == 1 else 's'} found"
)


# Display a helpful message when no records match.
if not tickets:
    st.info(
        "No tickets match the current search and filters."
    )
else:
    # Display each matching ticket as a compact queue card.
    for ticket in tickets:
        with st.container(border=True):
            # Keep the ticket summary on the left and status on the right.
            details_column, status_display_column = st.columns(
                [4, 1]
            )

            with details_column:
                # Display the ticket number and subject.
                st.markdown(
                    f"### #{ticket.id} — {ticket.subject}"
                )

                # Display the most important queue information.
                st.write(
                    f"**Customer:** "
                    f"{ticket.customer.company_name}  \n"
                    f"**Priority:** {ticket.priority}  \n"
                    f"**Channel:** {ticket.channel}  \n"
                    f"**Assigned to:** "
                    f"{ticket.assigned_to or 'Unassigned'}  \n"
                    f"**Created:** "
                    f"{ticket.created_at:%Y-%m-%d %I:%M %p}"
                )

                # Show a shortened description so the queue remains compact.
                if len(ticket.description) > 200:
                    description_preview = (
                        ticket.description[:200].rstrip()
                        + "..."
                    )
                else:
                    description_preview = ticket.description

                st.write(description_preview)

                # Open this ticket directly on the Ticket Detail page.
                #
                # Session State stores the selected ticket ID so the next page
                # knows which ticket the user chose.
                if st.button(
                    "Open ticket",
                    key=f"open_ticket_{ticket.id}",
                ):
                    # Save the selected ticket's database ID.
                    st.session_state["selected_ticket_id"] = ticket.id

                    # Switch directly to the Ticket Detail page.
                    st.switch_page("pages/3_Ticket_Detail.py")

            with status_display_column:
                # Display the current workflow status separately so it is easy
                # to identify while scanning the queue.
                st.markdown("**Status**")
                st.write(ticket.status)