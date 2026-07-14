"""
SQLAlchemy database models for SupportFlow.

The application currently uses three related tables:

1. Customer stores information about each business account.
2. Ticket stores support requests submitted by those customers.
3. TicketUpdate stores notes and activity connected to a ticket.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import Base


class Customer(Base):
    """
    Represent a company that receives support.

    One customer can have many support tickets. The tickets relationship makes
    it possible to access all tickets belonging to a customer through
    customer.tickets.
    """

    # Explicitly name the database table.
    __tablename__ = "customers"

    # Integer primary key generated automatically by the database.
    id: Mapped[int] = mapped_column(primary_key=True)

    # Company name is indexed because it may be searched or sorted frequently.
    company_name: Mapped[str] = mapped_column(String(150), index=True)

    # Name and email address of the customer's primary contact.
    contact_name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(180))

    # Simple account classification used for filtering and reporting.
    account_tier: Mapped[str] = mapped_column(
        String(30),
        default="Standard",
    )


    # Represent the overall condition of the customer account.
    #
    # Post-sales teams use account health to quickly identify customers who may
    # need additional attention, follow-up, or escalation.
    health_status: Mapped[str] = mapped_column(
        String(20),
        default="Healthy",
    )
    
    # Record when the customer account was created.
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    # Define the one-to-many relationship between Customer and Ticket.
    #
    # back_populates connects this relationship to Ticket.customer.
    # delete-orphan means tickets are deleted if their parent customer is
    # deleted from the database.
    tickets: Mapped[list["Ticket"]] = relationship(
        back_populates="customer",
        cascade="all, delete-orphan",
    )


class Ticket(Base):
    """
    Represent a support request submitted by a customer.

    A ticket belongs to one customer and can contain many activity updates.
    """

    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Foreign key connecting this ticket to a record in customers.id.
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id"),
    )

    # Main ticket content.
    subject: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)

    # Workflow fields used by the ticket queue.
    priority: Mapped[str] = mapped_column(
        String(20),
        default="Medium",
    )
    status: Mapped[str] = mapped_column(
        String(30),
        default="Open",
    )

    # Record where the support request originated.
    #
    # This helps model an omnichannel B2B support workflow such as Slack,
    # Microsoft Teams, email, web chat, or a manually entered request.
    channel: Mapped[str] = mapped_column(
        String(30),
        default="Manual",
    )
    # assigned_to is optional because a new ticket may initially be unassigned.
    assigned_to: Mapped[Optional[str]] = mapped_column(
        String(120),
        nullable=True,
    )

    # Record ticket creation and resolution times.
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
    )

    # Connect each ticket back to its parent Customer object.
    customer: Mapped["Customer"] = relationship(
        back_populates="tickets",
    )

    # A ticket can contain many notes or activity updates.
    updates: Mapped[list["TicketUpdate"]] = relationship(
        back_populates="ticket",
        cascade="all, delete-orphan",
    )


class TicketUpdate(Base):
    """
    Represent one note or activity entry associated with a support ticket.

    The first version uses this table for internal notes. Later versions can
    also store public replies, automated events, assignment changes, or
    imported Slack and Microsoft Teams messages.
    """

    __tablename__ = "ticket_updates"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Foreign key connecting this update to a ticket.
    ticket_id: Mapped[int] = mapped_column(
        ForeignKey("tickets.id"),
    )

    # Store the content of the conversation message or activity event.
    update_text: Mapped[str] = mapped_column(Text)


    # Identify what kind of activity occurred.
    # Supported types currently include:
    #
    # - Customer message
    # - Agent reply
    # - Internal note
    # - Status change
    update_type: Mapped[str] = mapped_column(
        String(30),
        default="Internal note",
    )


    # Record the person or system responsible for the activity.
    #
    # Examples include:
    #
    # - A customer contact name
    # - A support-agent name
    # - "System" for automated status changes
    author: Mapped[str] = mapped_column(
        String(120),
        default="System",
    )


    # Preserve the time each update was added.
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    # Connect the update back to its parent Ticket object.
    ticket: Mapped["Ticket"] = relationship(
        back_populates="updates",
    )
