# SupportFlow

SupportFlow is a lightweight B2B customer-support operations dashboard. It models
the core workflow of a post-sales support platform: customer accounts, support
tickets, assignments, priorities, status changes, and internal notes.

## Current features

- Create and view customer accounts
- Create support tickets
- Assign priority and owner
- Filter tickets by status
- Update ticket status
- Add internal notes
- View dashboard metrics

## Technology stack

- Python
- Streamlit
- SQLAlchemy
- SQLite for local development
- PostgreSQL-ready through `DATABASE_URL`

## Run locally

### 1. Create a virtual environment

Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Add sample data

```powershell
python seed.py
```

### 4. Start the application

```powershell
streamlit run app.py
```

## PostgreSQL setup

Create a `.env` file or set the `DATABASE_URL` environment variable:

```text
DATABASE_URL=postgresql+psycopg://username:password@host/database?sslmode=require
```

## Planned improvements

- User authentication and agent roles
- Ticket search and sorting
- Customer health scoring
- Response-time and resolution-time metrics
- External customer replies
- Slack-style conversation import
- React frontend
- Go or FastAPI backend
- GraphQL API
- AWS deployment
