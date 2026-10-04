import os
import json
import streamlit as st

from dotenv import load_dotenv
from google import genai

from database import check_inventory
from delivery import get_delivery_eta
from pricing import get_offer_price
from scheduler import schedule_call


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

MODEL = "gemini-3.1-flash-lite"

client = genai.Client()

file_search_store = os.getenv("GEMINI_FILE_SEARCH_STORE")

if not file_search_store:
    st.error("GEMINI_FILE_SEARCH_STORE is missing from .env")
    st.stop()


# ============================================================
# TOOL DEFINITIONS
# ============================================================

check_inventory_tool = {
    "type": "function",
    "name": "check_inventory",
    "description": "Checks vehicle inventory based on customer requirements.",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string"
            },
            "body_type": {
                "type": "string"
            },
            "transmission": {
                "type": "string"
            },
            "max_price_lakh": {
                "type": "number"
            }
        },
        "required": [
            "city",
            "body_type",
            "transmission",
            "max_price_lakh"
        ]
    }
}


get_delivery_eta_tool = {
    "type": "function",
    "name": "get_delivery_eta",
    "description": "Gets estimated vehicle delivery time.",
    "parameters": {
        "type": "object",
        "properties": {
            "vehicle_model": {
                "type": "string"
            },
            "city": {
                "type": "string"
            }
        },
        "required": [
            "vehicle_model",
            "city"
        ]
    }
}


get_offer_price_tool = {
    "type": "function",
    "name": "get_offer_price",
    "description": "Gets indicative offer pricing for a vehicle.",
    "parameters": {
        "type": "object",
        "properties": {
            "vehicle_model": {
                "type": "string"
            },
            "city": {
                "type": "string"
            },
            "customer_type": {
                "type": "string",
                "enum": [
                    "retail",
                    "fleet"
                ]
            }
        },
        "required": [
            "vehicle_model",
            "city",
            "customer_type"
        ]
    }
}


file_search_tool = {
    "type": "file_search",
    "file_search_store_names": [
        file_search_store
    ]
}


schedule_call_tool = {
    "type": "function",
    "name": "schedule_call",
    "description": "Schedules a sales call after dealer approval.",
    "parameters": {
        "type": "object",
        "properties": {
            "vehicle_model": {
                "type": "string"
            },
            "city": {
                "type": "string"
            }
        },
        "required": [
            "vehicle_model",
            "city"
        ]
    }
}


# ============================================================
# SESSION STATE
# ============================================================

if "interaction_id" not in st.session_state:
    st.session_state.interaction_id = None

if "stage" not in st.session_state:
    st.session_state.stage = "requirement"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "customer_city" not in st.session_state:
    st.session_state.customer_city = None

if "recommended_vehicles" not in st.session_state:
    st.session_state.recommended_vehicles = []

if "selected_vehicle" not in st.session_state:
    st.session_state.selected_vehicle = None

if "tool_log" not in st.session_state:
    st.session_state.tool_log = []

if "appointment_id" not in st.session_state:
    st.session_state.appointment_id = None


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_output_text(interaction):
    """
    Extract text from Gemini model output.
    """

    if getattr(interaction, "output_text", None):
        return interaction.output_text

    output = []

    for step in interaction.steps:

        if step.type == "model_output":

            for content in step.content:

                if getattr(content, "type", None) == "text":
                    output.append(content.text)

    return "\n".join(output)


def validate_tool_args(tool_name, args):

    if tool_name == "get_offer_price":

        customer_type = args.get("customer_type")

        if customer_type not in ["retail", "fleet"]:
            return False, (
                "customer_type must be 'retail' or 'fleet'."
            )

        if not args.get("vehicle_model"):
            return False, "vehicle_model is required."


    if tool_name == "get_delivery_eta":

        if not args.get("vehicle_model"):
            return False, "vehicle_model is required."

        if not args.get("city"):
            return False, "city is required."


    if tool_name == "check_inventory":

        if not args.get("city"):
            return False, "city is required."

        if not args.get("body_type"):
            return False, "body_type is required."


    return True, None


def execute_tool(call):

    tool_name = call.name
    args = call.arguments

    st.session_state.tool_log.append({
        "tool": tool_name,
        "arguments": args
    })

    valid, error = validate_tool_args(
        tool_name,
        args
    )

    if not valid:

        return {
            "error": error,
            "instruction": "Correct the arguments and retry."
        }


    if tool_name == "check_inventory":

        return check_inventory(**args)


    elif tool_name == "get_delivery_eta":

        return get_delivery_eta(**args)


    elif tool_name == "get_offer_price":

        return get_offer_price(**args)


    elif tool_name == "schedule_call":

        return schedule_call(**args)


    return {
        "error": f"Unknown tool: {tool_name}"
    }


def run_tool_loop(
    interaction,
    tools,
    system_instruction
):

    while True:

        function_calls = [
            step
            for step in interaction.steps
            if step.type == "function_call"
        ]

        if not function_calls:
            return interaction

        function_results = []

        for call in function_calls:

            result = execute_tool(call)

            function_results.append({
                "type": "function_result",
                "name": call.name,
                "call_id": call.id,
                "result": [
                    {
                        "type": "text",
                        "text": str(result)
                    }
                ]
            })

        interaction = client.interactions.create(
            model=MODEL,
            previous_interaction_id=interaction.id,
            input=function_results,
            tools=tools,
            system_instruction=system_instruction,
            generation_config={
                "thinking_level": "minimal"
            }
        )


def find_selected_vehicle(user_input):

    text = user_input.strip().lower()

    for vehicle in st.session_state.recommended_vehicles:

        model = vehicle["model"]

        if model.lower() in text:
            return model

    return None


# ============================================================
# UI
# ============================================================

st.set_page_config(
    page_title="Automotive Sales Agent",
    page_icon="🚗",
    layout="wide"
)

st.title("Automotive Sales & Dealer Operations Agent")

st.caption(
    "AI-powered vehicle recommendation, product knowledge and dealer action assistant"
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.subheader("Agent Status")

    st.write(
        f"**Stage:** {st.session_state.stage.title()}"
    )

    if st.session_state.customer_city:

        st.write(
            f"**City:** {st.session_state.customer_city}"
        )

    if st.session_state.selected_vehicle:

        st.write(
            f"**Selected Vehicle:** "
            f"{st.session_state.selected_vehicle}"
        )

    if st.session_state.appointment_id:

        st.success(
            f"Appointment: "
            f"{st.session_state.appointment_id}"
        )


    st.divider()

    if st.session_state.tool_log:

        with st.expander("Agent Tool Activity"):

            for item in st.session_state.tool_log:

                st.write(
                    f"**{item['tool']}**"
                )

                st.code(
                    json.dumps(
                        item["arguments"],
                        indent=2
                    ),
                    language="json"
                )


    if st.button("Start New Conversation"):

        st.session_state.clear()
        st.rerun()


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# ============================================================
# CHAT INPUT
# ============================================================

user_input = st.chat_input(
    "Enter customer requirement or ask a question..."
)


if user_input:

    # --------------------------------------------------------
    # DISPLAY USER MESSAGE
    # --------------------------------------------------------

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)


    # ========================================================
    # STAGE 1 — CUSTOMER REQUIREMENT
    # ========================================================

    if st.session_state.stage == "requirement":

        system_instruction = """
You are an Automotive Sales & Dealer Operations Agent.

The dealer has provided a complete customer requirement.

You MUST:

1. Understand the customer's:
   - city
   - vehicle body type
   - transmission
   - maximum budget
   - required delivery timeline

2. Call check_inventory.

3. For every vehicle returned by inventory:
   - call get_delivery_eta
   - call get_offer_price

4. Only recommend vehicles that satisfy the customer's
   stated budget and delivery requirement.

5. Do not ask follow-up questions.

6. End with:
"Which vehicle would you like to proceed with?"

Use retail as the customer_type unless the dealer
explicitly specifies fleet.

Never invent live inventory, pricing or delivery data.
"""

        interaction = client.interactions.create(
            model=MODEL,
            input=user_input,
            tools=[
                check_inventory_tool,
                get_delivery_eta_tool,
                get_offer_price_tool
            ],
            system_instruction=system_instruction,
            generation_config={
                "thinking_level": "minimal"
            }
        )


        interaction = run_tool_loop(
            interaction,
            [
                check_inventory_tool,
                get_delivery_eta_tool,
                get_offer_price_tool
            ],
            system_instruction
        )


        st.session_state.interaction_id = interaction.id

        answer = get_output_text(interaction)


        # Extract city and inventory information from
        # logged tool activity

        for item in st.session_state.tool_log:

            if item["tool"] == "check_inventory":

                args = item["arguments"]

                st.session_state.customer_city = (
                    args.get("city")
                )


        # Ask inventory again only through the logged
        # business result isn't available here, so the
        # recommended vehicle names are extracted from
        # the final answer as a simple prototype method.

        known_models = [
            "Tata Nexon",
            "Hyundai Venue",
            "Kia Seltos",
            "Hyundai Creta",
            "Toyota Urban Cruiser Hyryder",
            "Honda City"
        ]

        st.session_state.recommended_vehicles = []

        for model in known_models:

            if model.lower() in answer.lower():

                st.session_state.recommended_vehicles.append({
                    "model": model
                })


        st.session_state.stage = "selection"


        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })


        with st.chat_message("assistant"):
            st.markdown(answer)


    # ========================================================
    # STAGE 2 — VEHICLE SELECTION
    # ========================================================

    elif st.session_state.stage == "selection":

        selected_vehicle = find_selected_vehicle(
            user_input
        )


        if not selected_vehicle:

            response = (
                "Please select one of the vehicles "
                "from the recommendation."
            )

            st.session_state.messages.append({
                "role": "assistant",
                "content": response
            })

            with st.chat_message("assistant"):
                st.markdown(response)

        else:

            st.session_state.selected_vehicle = (
                selected_vehicle
            )

            interaction = client.interactions.create(
                model=MODEL,
                previous_interaction_id=(
                    st.session_state.interaction_id
                ),
                input=f"""
The dealer has selected the vehicle:
{selected_vehicle}
""",
                system_instruction="""
A vehicle has been selected by the dealer.

Respond concisely:

"I have noted your selection of the
[selected vehicle]."

Then ask exactly:

"Would you like me to schedule a call?"
""",
                generation_config={
                    "thinking_level": "minimal"
                }
            )


            st.session_state.interaction_id = (
                interaction.id
            )

            answer = get_output_text(
                interaction
            )

            st.session_state.stage = "confirmation"


            st.session_state.messages.append({
                "role": "assistant",
                "content": answer
            })


            with st.chat_message("assistant"):
                st.markdown(answer)


    # ========================================================
    # STAGE 3 — QUESTIONS + CALL CONFIRMATION
    # ========================================================

    elif st.session_state.stage == "confirmation":

        # ----------------------------------------------------
        # YES → SCHEDULE
        # ----------------------------------------------------

        if user_input.strip().lower() in [
            "yes",
            "y"
        ]:

            scheduling_instruction = f"""
The dealer has approved call scheduling.

Selected vehicle:
{st.session_state.selected_vehicle}

Customer city:
{st.session_state.customer_city}

You MUST call schedule_call.

Use exactly:
vehicle_model = "{st.session_state.selected_vehicle}"
city = "{st.session_state.customer_city}"

Do not ask another question.
"""

            interaction = client.interactions.create(
                model=MODEL,
                previous_interaction_id=(
                    st.session_state.interaction_id
                ),
                input=user_input,
                tools=[schedule_call_tool],
                system_instruction=scheduling_instruction,
                generation_config={
                    "thinking_level": "minimal",
                    "tool_choice": {
                        "allowed_tools": {
                            "mode": "any",
                            "tools": [
                                "schedule_call"
                            ]
                        }
                    }
                }
            )


            interaction = run_tool_loop(
                interaction,
                [schedule_call_tool],
                scheduling_instruction
            )


            st.session_state.interaction_id = (
                interaction.id
            )

            answer = get_output_text(
                interaction
            )


            # Get appointment ID from the latest
            # scheduling result

            for item in st.session_state.tool_log:

                if item["tool"] == "schedule_call":
                    pass


            # The model output confirms the action,
            # while the actual appointment was created
            # by Python.

            st.session_state.stage = "completed"


            st.session_state.messages.append({
                "role": "assistant",
                "content": answer
            })


            with st.chat_message("assistant"):
                st.success(answer)


        # ----------------------------------------------------
        # NO → END
        # ----------------------------------------------------

        elif user_input.strip().lower() in [
            "no",
            "n"
        ]:

            answer = (
                "No problem. The selected vehicle "
                "remains unchanged."
            )

            st.session_state.stage = "completed"

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer
            })

            with st.chat_message("assistant"):
                st.markdown(answer)


        # ----------------------------------------------------
        # ANY OTHER INPUT → RAG QUESTION
        # ----------------------------------------------------

        else:

            qa_instruction = f"""
You are an Automotive Sales & Dealer Operations Agent.

The dealer has selected:
{st.session_state.selected_vehicle}

The dealer is asking a product or policy question.

Use file_search for:
- warranty
- vehicle features
- specifications
- product information
- policies

Do not invent information.

After answering, ask exactly:

"Would you like me to schedule a call?"
"""

            interaction = client.interactions.create(
                model=MODEL,
                previous_interaction_id=(
                    st.session_state.interaction_id
                ),
                input=user_input,
                tools=[
                    file_search_tool
                ],
                system_instruction=qa_instruction,
                generation_config={
                    "thinking_level": "minimal"
                }
            )


            st.session_state.interaction_id = (
                interaction.id
            )

            answer = get_output_text(
                interaction
            )


            st.session_state.messages.append({
                "role": "assistant",
                "content": answer
            })


            with st.chat_message("assistant"):
                st.markdown(answer)