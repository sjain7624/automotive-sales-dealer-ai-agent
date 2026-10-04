# Automotive Sales & Dealer Operations Agent

An AI-powered dealer assistant that combines LLM reasoning, enterprise-style tools, RAG, conversational state, and human-approved actions to support automotive sales operations.

## 1. Project Overview

Automotive dealers and sales representatives often need to combine information from multiple systems before responding to a customer:

- Vehicle availability
- Delivery timelines
- Indicative pricing
- Product and warranty information
- Follow-up actions

This project demonstrates an agentic workflow in which an AI agent interprets a dealer's request, selects the appropriate tools, retrieves grounded product information, and executes an approved business action.

## 2. What the Agent Does

The agent supports the following workflow:

1. Understand a customer requirement such as:
   - Vehicle type
   - Transmission
   - Budget
   - City
   - Delivery requirement

2. Search vehicle inventory.

3. Retrieve estimated delivery time.

4. Retrieve indicative offer pricing.

5. Recommend suitable vehicles.

6. Maintain conversational context when the dealer selects a vehicle.

7. Answer product, specification, warranty and policy questions using RAG.

8. Ask for dealer approval before performing an action.

9. Schedule a sales call through a controlled tool.

10. Persist the appointment in SQLite.

## 3. Example Workflow

### Dealer Requirement

> Customer is looking for an automatic SUV under ₹18 lakh in Ranchi and needs delivery within 5 days.

### Agent Workflow

```text
Dealer Requirement
        |
        v
Gemini Agent
        |
        +-------------------+
        |                   |
        v                   v
  Inventory Tool       Business Tools
                         |
                   +-----+-----+
                   |           |
                   v           v
                Delivery     Pricing
                   |
                   v
            Vehicle Recommendation
                   |
                   v
            Dealer Vehicle Selection
                   |
                   v
              Product / Policy Q&A
                   |
                   v
                 RAG
                   |
                   v
          Human Approval Required
                   |
                "Yes"
                   |
                   v
           Schedule Call Tool
                   |
                   v
               SQLite DB

4. Agent Architecture
                    Dealer / Sales RM
                           |
                           v
                    Streamlit Interface
                           |
                           v
                    Gemini Agent
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
      Inventory        Delivery          Pricing
         Tool             Tool             Tool
          |                |                |
          +----------------+----------------+
                           |
                           v
                  Product Knowledge
                           |
                           v
                     File Search
                         / RAG
                           |
                           v
                  Human Approval Gate
                           |
                           v
                   Schedule Call Tool
                           |
                           v
                       SQLite

5. Key Agentic AI Concepts Demonstrated
LLM Reasoning

Gemini interprets natural-language dealer requirements and determines which tools are relevant.

Function Calling

The agent can invoke controlled business functions such as:

check_inventory
get_delivery_eta
get_offer_price
schedule_call
Retrieval-Augmented Generation

Product and policy questions are answered using a Gemini File Search knowledge base rather than relying only on model memory.

Stateful Conversation

The application maintains the Gemini interaction across multiple dealer messages, allowing the agent to retain context such as the selected vehicle and city.

Human-in-the-Loop

The scheduling action is not performed merely because the agent recommends it. The dealer must explicitly approve the action before the scheduling tool is invoked.

Tool Validation

LLM-generated tool arguments are validated before business functions are executed. This prevents malformed arguments from directly reaching the underlying business logic.

6. Technology Stack
Layer	Technology
LLM	Google Gemini 3.1 Flash-Lite
Agent interaction	Gemini Interactions API
RAG	Gemini File Search
Frontend	Streamlit
Backend logic	Python
Data storage	SQLite
Data processing	Python / JSON
Environment management	python-dotenv
Version control	Git / GitHub
7. Project Structure
automotive-sales-dealer-ai-agent/
|
├── streamlit_app.py
├── database.py
├── delivery.py
├── pricing.py
├── scheduler.py
├── setup_rag.py
|
├── knowledge/
│   ├── vehicle_catalog.txt
│   └── warranty_policy.txt
|
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
8. Tool Responsibilities
Inventory Tool

Checks vehicle availability using:

City
Body type
Transmission
Maximum budget
Delivery Tool

Returns the estimated delivery time for a vehicle in a specified city.

Pricing Tool

Returns indicative base price, discount and offer price for supported vehicle configurations.

Scheduling Tool

Creates a sales-call appointment and stores it in the SQLite database.

Example output:

Status: Scheduled
Appointment ID: CALL-0004
Vehicle: Tata Nexon
City: Ranchi
9. RAG Knowledge Base

The current knowledge base contains demo product and policy information such as:

Vehicle information
Features
Warranty-related information
Policy rules

The knowledge files are intentionally treated as prototype data and should not be interpreted as official manufacturer policy.

10. Why This Is Agentic AI

This project is not designed as a simple question-answering chatbot.

The agent:

Understand
    ↓
Reason
    ↓
Select Tool
    ↓
Observe Tool Result
    ↓
Continue Workflow
    ↓
Retrieve Knowledge When Needed
    ↓
Request Human Approval
    ↓
Execute Action

The LLM is responsible for interpreting the conversation and deciding which capability is required, while deterministic Python functions remain responsible for business data access and action execution.

11. Example Use Case

A dealer receives a customer request:

Customer wants an automatic SUV under ₹18 lakh in Ranchi within 5 days.

The agent:

Searches inventory.
Checks delivery ETA for matching vehicles.
Retrieves indicative pricing.
Presents qualifying options.
Records the dealer's selection.
Answers a warranty question through RAG.
Requests approval to schedule a call.
Invokes the scheduling tool after approval.
Creates an appointment ID in SQLite.
12. Setup
Clone the repository
git clone https://github.com/YOUR_USERNAME/automotive-sales-dealer-ai-agent.git
cd automotive-sales-dealer-ai-agent
Create a virtual environment
python -m venv .venv

Activate it on Windows:

.venv\Scripts\Activate.ps1
Install dependencies
pip install -r requirements.txt
Configure environment variables

Create a .env file based on .env.example.

GEMINI_API_KEY=your_api_key
GEMINI_FILE_SEARCH_STORE=your_file_search_store

Never commit .env or API credentials to GitHub.

Start the application
streamlit run streamlit_app.py
13. Current Prototype Limitations

This is an interview-focused prototype rather than a production automotive platform.

Current limitations include:

Demo inventory data
Demo pricing data
Demo product/policy knowledge
SQLite instead of enterprise CRM/ERP systems
Mock scheduling rather than a production calendar integration
Limited vehicle dataset
Prototype-level conversation and entity handling
14. Production Evolution

A production version could integrate:

Dealer CRM
ERP / DMS
Live Inventory APIs
Pricing & Promotion Engine
Logistics / ETA APIs
Enterprise Knowledge Base
Calendar / Communication Platform
Identity & Access Management
Observability & Audit Logging

Additional capabilities could include:

Lead creation and CRM updates
Customer profile retrieval
Test-drive scheduling
Next-best vehicle recommendation
Dealer follow-up automation
Lead prioritization
Sales performance analytics
Voice-based dealer interaction
15. Learning Outcomes

This project provided hands-on experience with:

Agentic AI architecture
Gemini function calling
RAG / File Search
Stateful multi-turn interactions
Tool orchestration
Human-in-the-loop design
Business-rule validation
Python backend development
Streamlit application development
SQLite persistence
Git and GitHub
16. Author

Shubham Jain

MBA – Business Analytics
IIM Ranchi


