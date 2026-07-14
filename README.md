# SupportFlow

SupportFlow is a multi-page B2B customer-support operations application built to model the core workflow of a post-sales support platform.

The application allows support teams to manage customer accounts, create and organize support tickets, track status changes, assign priorities and owners, record internal notes, and review customer and ticket history.

## Features

### Customer management

- Create customer accounts
- Store primary contact information
- Assign account tiers
- View customer-specific ticket history
- Review customer support metrics
- Open individual tickets directly from a customer record

### Ticket management

- Create support tickets
- Assign priority and owner
- Search ticket subjects and descriptions
- Filter tickets by status
- Filter tickets by priority
- Open tickets directly from the queue
- Update ticket status
- Record resolution timestamps
- Add internal notes
- Maintain ticket activity history

### Dashboard

- View total customer count
- View open ticket count
- View urgent ticket count
- View resolved ticket count
- Review recently created tickets

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
└── pages/
    ├── 1_Customers.py
    ├── 2_Tickets.py
    ├── 3_Ticket_Detail.py
    └── 4_Customer_Detail.py
```

## Database Design

SupportFlow currently uses three related database models.

### Customer

Stores company and primary-contact information.

### Ticket

Stores support requests, workflow status, priority, assignment, creation time, and resolution time.

Each ticket belongs to one customer.

### TicketUpdate

Stores ticket activity such as:

- Internal notes
- Status changes

Each update belongs to one ticket.

The primary relationships are:

```text
Customer
└── Ticket
    └── TicketUpdate
```

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
- Internal notes
- Activity logging
- Customer-level ticket history
- Dashboard metrics

## Planned Improvements

- Deploy the application publicly
- Migrate production data to PostgreSQL
- Add automated tests with pytest
- Add dashboard charts
- Add email validation and duplicate-customer checks
- Add support-agent user accounts
- Add authentication and role-based permissions
- Add response-time and resolution-time metrics
- Add customer health scoring
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
- Activity logging
- Technical documentation
