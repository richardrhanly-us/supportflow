"""
Customer-management page for SupportFlow.

Users can create a customer account and review all existing customer records.
A customer must exist before a support ticket can be created.
"""

import streamlit as st
from sqlalchemy import select

from db import SessionLocal, init_db
from models import Customer


# Configure this page's title and icon.
st.set_page_config(
    page_title="Customers | SupportFlow",
    page_icon="🏢",
)


# Create missing database tables before reading or writing customer data.
init_db()


st.title("Customers")


# A Streamlit form groups all customer fields into one submission.
#
# clear_on_submit=True empties the form after a successful submission.
with st.form("new_customer", clear_on_submit=True):
    company_name = st.text_input("Company name")
    contact_name = st.text_input("Primary contact")
    email = st.text_input("Contact email")
    account_tier = st.selectbox(
        "Account tier",
        ["Standard", "Growth", "Enterprise"],
    )

    submitted = st.form_submit_button("Add customer")

    if submitted:
        # Basic validation prevents incomplete customer records.
        if (
            not company_name.strip()
            or not contact_name.strip()
            or not email.strip()
        ):
            st.error(
                "Company name, contact name, and email are required."
            )
        else:
            # Create and save the new Customer object.
            with SessionLocal() as db:
                customer = Customer(
                    company_name=company_name.strip(),
                    contact_name=contact_name.strip(),
                    email=email.strip(),
                    account_tier=account_tier,
                )

                db.add(customer)
                db.commit()

            st.success("Customer added.")


st.subheader("Customer accounts")


# Retrieve customer records alphabetically by company name.
with SessionLocal() as db:
    customers = db.scalars(
        select(Customer).order_by(Customer.company_name)
    ).all()


# Display a message when no customer records exist.
if not customers:
    st.info("No customers have been added.")
else:
    # Render one account card for each customer.
    for customer in customers:
        with st.container(border=True):
            # Separate the account information from the navigation button.
            details_column, action_column = st.columns(
                [4, 1]
            )

            with details_column:
                # Display the company name as the card heading.
                st.markdown(
                    f"### {customer.company_name}"
                )

                # Display the primary account details.
                st.write(
                    f"**Contact:** "
                    f"{customer.contact_name}  \n"
                    f"**Email:** "
                    f"{customer.email}  \n"
                    f"**Account tier:** "
                    f"{customer.account_tier}"
                )

            with action_column:
                # Open this customer directly on the Customer Detail page.
                if st.button(
                    "Open customer",
                    key=f"open_customer_{customer.id}",
                ):
                    # Store the selected customer's database ID.
                    st.session_state[
                        "selected_customer_id"
                    ] = customer.id

                    # Switch directly to the Customer Detail page.
                    st.switch_page(
                        "pages/4_Customer_Detail.py"
                    )
