# SupportFlow

SupportFlow is a multi-page B2B post-sales support operations application built to model the core workflow of a modern customer support platform.

The application allows support teams to manage customer accounts, create and organize support tickets, track status changes, assign priorities and owners, record customer messages and agent replies, monitor account health, and review customer and ticket history.

SupportFlow was designed as a portfolio project focused on real-world B2B support workflows, conversational data, account management, and operational visibility.

## Features

### Customer and account management

- Create customer accounts
- Store primary contact information
- Assign account tiers
- Track account health as Healthy, At Risk, or Critical
- Update customer health status
- View customer-specific ticket history
- Review customer support metrics
- Open individual tickets directly from a customer record

### Ticket management

- Create support tickets
- Assign priority and owner
- Record the originating support channel
- Support Slack, Microsoft Teams, Email, Web Chat, and Manual channels
- Search ticket subjects and descriptions
- Filter tickets by status
- Filter tickets by priority
- Open tickets directly from the queue
- Update ticket status
- Record resolution timestamps
- Maintain a conversation and activity timeline

### Conversation and activity tracking

- Record customer messages
- Record agent replies
- Add internal support notes
- Log ticket status changes
- Track the author of each activity entry
- Review account-level recent activity
- Preserve a chronological support history for each ticket

### Ticket triage

- Analyze ticket subject and description text
- Suggest a priority using transparent keyword-based rules
- Recommend High or Urgent priority for outage, access, blocking, and production-impact language
- Allow the user to override the suggested priority

### Dashboard

- View total customer count
- View open ticket count
- View urgent ticket count
- View resolved ticket count
- Review recently created tickets
- See ticket channel, priority, assignment, and status at a glance

## Technology Stack

- Python
- Streamlit
- SQLAlchemy
- SQLite for local development
- PostgreSQL-ready through `DATABASE_URL`
- Git and GitHub

## Application Structure

```text
supportflow/
│
├── app.py
├── db.py
├── models.py
├── seed.py
├── requirements.txt
├── README.md
│
├── docs/
│   └── screenshots/
│       ├── dashboard.png
│       ├── customers.png
│       ├── tickets.png
│       ├── create_ticket.png
│       ├── ticket_detail.png
│       └── customer_detail.png
│
└── pages/
    ├── 1_Customers.py
    ├── 2_Tickets.py
    ├── 3_Ticket_Detail.py
    └── 4_Customer_Detail.py
```

## Screenshots

### Dashboard

The dashboard provides a quick operational overview of customer and ticket activity.

![SupportFlow dashboard](docs/screenshots/dashboard.png)

### Customer Accounts

The Customers page allows users to create accounts, assign account tiers and health status, and open detailed customer records.

![SupportFlow customer accounts](docs/screenshots/customers.png)

### Ticket Queue

The Tickets page supports search, filtering, queue review, channel visibility, and direct navigation to ticket details.

![SupportFlow ticket queue](docs/screenshots/tickets.png)

### Ticket Creation and Priority Suggestion

The ticket creation workflow includes omnichannel source selection and live rule-based priority recommendations.

![SupportFlow ticket creation](docs/screenshots/create_ticket.png)

### Ticket Detail and Conversation Timeline

The Ticket Detail page displays account information, ticket workflow data, customer messages, agent replies, internal notes, and status-change events.

![SupportFlow ticket detail](docs/screenshots/ticket_detail.png)

### Customer Detail and Account Health

The Customer Detail page combines account information, support metrics, health status, ticket history, and recent conversation activity.

![SupportFlow customer detail](docs/screenshots/customer_detail.png)

## Database Design

SupportFlow currently uses three related database models.

### Customer

Stores account-level information including:

- Company name
- Primary contact
- Contact email
- Account tier
- Health status
- Account creation time

### Ticket

Stores support-request and workflow information including:

- Customer relationship
- Subject
- Description
- Priority
- Status
- Channel
- Assigned support agent
- Creation timestamp
- Resolution timestamp

Each ticket belongs to one customer.

### TicketUpdate

Stores conversation entries and activity events including:

- Customer messages
- Agent replies
- Internal notes
- Status changes
- Author
- Timestamp

Each update belongs to one ticket.

The primary relationships are:

```text
Customer
└── Ticket
    └── TicketUpdate
```

## Priority Recommendation Logic

SupportFlow includes a transparent rule-based triage helper.

The helper combines the ticket subject and description, converts the text to lowercase, and checks for high-impact phrases.

Examples of urgent terms include:

```text
outage
system down
production down
critical
security breach
data loss
cannot access
completely blocked
```

Examples of high-priority terms include:

```text
blocked
error
failing
unable to
not working
delayed
degraded
login issue
```

The recommendation is shown while the user enters the ticket, but the user remains in control of the final priority.

## Run Locally

### 1. Clone the repository

```powershell
git clone https://github.com/richardrhanly-us/supportflow.git
cd supportflow
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Add sample data

```powershell
python seed.py
```

### 5. Start the application

```powershell
python -m streamlit run app.py
```

The application will usually open at:

```text
http://localhost:8501
```

## PostgreSQL Configuration

SupportFlow uses SQLite by default for local development.

To connect to PostgreSQL, create a `.env` file or set the `DATABASE_URL` environment variable:

```text
DATABASE_URL=postgresql+psycopg://username:password@host/database?sslmode=require
```

The application will use PostgreSQL automatically when `DATABASE_URL` is available.

## Current Status

SupportFlow is a functional local MVP.

Completed work includes:

- Relational database models
- Customer and ticket creation
- Multi-page navigation
- Search and filtering
- Cross-page selection with Streamlit Session State
- Ticket status management
- Omnichannel ticket tracking
- Customer messages and agent replies
- Internal notes
- Activity logging
- Account health tracking
- Customer-level ticket history
- Live rule-based priority suggestions
- Dashboard metrics
- GitHub documentation and screenshots

## Planned Improvements

- Migrate production data to PostgreSQL
- Deploy the application publicly
- Add automated tests with pytest
- Add dashboard charts
- Add email validation
- Prevent duplicate customer records
- Add support-agent user accounts
- Add authentication
- Add role-based permissions
- Add first-response-time metrics
- Add average resolution-time metrics
- Add overdue ticket indicators
- Add automatic account-health calculations
- Add external customer replies
- Add Slack or Microsoft Teams conversation imports
- Build a React frontend
- Create a Go or FastAPI backend
- Add a GraphQL API
- Deploy services through AWS

## Purpose

This project was created to demonstrate:

- Relational database design
- Object-relational mapping with SQLAlchemy
- CRUD application workflows
- Multi-page Streamlit development
- Search and filtering
- State management
- Cross-page navigation
- Omnichannel support workflows
- Conversational data modeling
- Account-health tracking
- Rule-based ticket triage
- Activity logging
- Technical documentation