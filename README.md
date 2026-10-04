# Automotive Sales & Dealer Operations Agent

An AI-powered dealer-assistance prototype for automotive sales operations. The agent combines conversational AI, enterprise-style business tools, retrieval-augmented generation (RAG), and human-approved actions to help dealers identify suitable vehicles and initiate follow-up calls.

> **Project status:** MVP / interview-ready prototype
>
> **Data note:** Inventory, pricing, delivery ETA, scheduling records, and knowledge-base content are demo data created for this prototype. They are not live manufacturer or dealer data.

## Business Problem

Dealer sales teams often need to answer several questions before they can move a customer forward:

- Which vehicles are available for the customer's requirements?
- Can a vehicle be delivered within the requested timeline?
- What indicative offer price is available?
- What does the product or warranty policy say?
- Can the dealer initiate a follow-up action after approval?

The agent brings these steps into one conversational workflow.

## What the Agent Does

1. Accepts a complete or partially specified customer requirement.
2. Uses tools to check inventory, delivery ETA, and indicative pricing.
3. Recommends suitable vehicles.
4. Maintains conversation context for vehicle selection and follow-up questions.
5. Uses Gemini File Search / RAG for product and policy questions.
6. Requires dealer confirmation before scheduling a call.
7. Executes a scheduling tool and stores the appointment in SQLite.

## Architecture

```text
Dealer / Sales RM
       |
       v
Streamlit Chat UI
       |
       v
Gemini Agent
       |
       +--------------------+--------------------+
       |                    |                    |
       v                    v                    v
Inventory Tool          RAG / File Search    Action Tool
Delivery ETA            Product/Policy       Schedule Call
Pricing                 Knowledge                 |
       |                    |                    v
       +--------------------+---------------  SQLite
```

### Design principle

The LLM is used for intent understanding, reasoning, tool selection, and natural-language responses. Authoritative transactional data and actions are handled by controlled application tools rather than relying on the model to invent business data.

## Tech Stack

- Python
- Streamlit
- Google Gemini (`google-genai`)
- Gemini File Search for RAG
- SQLite
- Python-dotenv
- Function calling / tool use

## Project Structure

```text
automotive-sales-agent/
│
├── streamlit_app.py        # Main Streamlit application
├── database.py             # Inventory database / inventory tool
├── delivery.py             # Delivery ETA tool
├── pricing.py              # Indicative pricing tool
├── scheduler.py            # Call scheduling tool
├── setup_rag.py            # Creates and populates Gemini File Search store
│
├── knowledge/
│   ├── vehicle_catalog.txt
│   └── warranty_policy.txt
│
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Setup

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd automotive-sales-agent
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file from `.env.example`:

```text
GEMINI_API_KEY=your_gemini_api_key
GEMINI_FILE_SEARCH_STORE=your_file_search_store_name
```

Never commit `.env` or API keys to GitHub.

### 5. Configure RAG

The project uses a Gemini File Search store containing the vehicle and policy knowledge files.

Run the setup script when creating a new store:

```powershell
python setup_rag.py
```

Copy the resulting File Search store name into `.env` as `GEMINI_FILE_SEARCH_STORE`.

### 6. Run the application

```powershell
streamlit run streamlit_app.py
```

Open the local Streamlit URL shown in the terminal.

## Example Workflow

```text
Dealer:
Customer is looking for an automatic SUV under ₹18 lakh in Ranchi and needs delivery within 5 days.

Agent:
Checks inventory, delivery ETA and indicative pricing.

Agent:
Presents suitable vehicle options.

Dealer:
Tata Nexon

Agent:
Would you like me to schedule a call?

Dealer:
Yes

Agent:
schedule_call → SQLite → Appointment ID
```

The dealer can also ask product or policy questions after vehicle selection. These are answered using the configured RAG knowledge base.

## Agentic AI Components

### LLM

Gemini interprets dealer/customer language, maintains conversational context, selects tools, and generates responses.

### Tool Calling

The application exposes controlled tools for:

- `check_inventory`
- `get_delivery_eta`
- `get_offer_price`
- `schedule_call`

### RAG

Gemini File Search grounds product and policy questions in uploaded knowledge documents instead of relying only on model memory.

### Human-in-the-Loop

The scheduling action is gated by explicit dealer approval before the scheduling tool is executed.

### State

The Streamlit application maintains conversation and workflow state using `st.session_state`, while Gemini interaction IDs preserve model-side conversation context.

## Guardrails Implemented

- Tool argument validation
- Controlled function schemas
- Human approval before scheduling
- Separation of transactional tools and document retrieval
- No API credentials stored in source code
- Demo data explicitly separated from live enterprise data

## Limitations

This is an MVP prototype rather than a production dealer platform.

- Inventory, ETA and pricing are mock data.
- Scheduling is represented by a local SQLite action rather than a live calendar/CRM integration.
- RAG knowledge is limited to the supplied demo documents.
- Production deployment would require authentication, RBAC, audit logging, monitoring, API integrations, better error handling, and formal evaluation.

## Future Enhancements

- CRM / lead creation after dealer approval
- Google Calendar or enterprise scheduling integration
- Live dealer inventory and pricing APIs
- Customer profile and lead history
- Structured evaluation suite for tool-call accuracy and task success
- Authentication and role-based access
- Production observability and audit logging

## Interview Positioning

This project demonstrates an end-to-end agentic AI workflow rather than a simple chatbot:

```text
Natural-language requirement
        ↓
LLM reasoning
        ↓
Tool orchestration
        ↓
Structured enterprise data
        ↓
RAG for unstructured knowledge
        ↓
Human approval
        ↓
Tool-based action
        ↓
Persistent business record
```

A key design decision is to keep authoritative business data and deterministic actions outside the LLM. The model proposes and coordinates actions; application tools execute controlled operations.
