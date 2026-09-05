from langchain.agents.middleware import AgentMiddleware
from state import AgentState, UserProfile
from langchain.agents.middleware import after_model, after_agent

from langchain.agents.middleware import AgentMiddleware
from state import AgentState
import json


class ProfileMiddleware(AgentMiddleware):

    state_schema = AgentState

    def __init__(self, model):
        self.model = model

    def before_model(self, state, runtime):

        user_message = state["messages"][-1].content

        prompt = f"""
You extract skincare profile information from the user's message.

Return ONLY valid JSON.

Possible fields:
- skin_type
- concerns
- budget
- preferences

Rules:
- Only include fields that are explicitly mentioned or clearly changed.
- Do not include fields that are not mentioned.
- skin_type must be one of: oily, dry, combination, normal.
- concerns must be a list of strings.
- preferences must be a list of strings.
- budget must be a number.
- Do not add explanations.

Examples:

User: "I have oily skin and acne"
Output:
{{"skin_type": "oily", "concerns": ["acne"]}}

User: "Actually my skin is combination"
Output:
{{"skin_type": "combination"}}

User: "My budget is 1000 EGP"
Output:
{{"budget": 1000}}

User message:
{user_message}
"""

        response = self.model.invoke(prompt)

        try:
            updates = json.loads(response.content)
        except json.JSONDecodeError:
            return None

        return updates


#custome middlewares, @afetr the model and @afteragent decorators 
@after_model
def check_model_response(state, runtime):
    """Check the model's response after each model call."""

    last_message = state["messages"][-1]

    # Check that the model returned something
    if not last_message.content:
        print("⚠️ Warning: Model returned an empty response.")

    # Check if the model wants to call a tool
    if getattr(last_message, "tool_calls", None):
        print("🔧 Model requested a tool call.")

    else:
        print("💬 Model returned a normal response.")

    return None


@after_agent
def validate_final_response(state, runtime):
    """Validate the final response after the agent finishes."""

    final_message = state["messages"][-1]
    response = final_message.content

    print("\n--- AFTER AGENT VALIDATION ---")

    # 1. Check that the final response is not empty
    if not response:
        print("Final response is empty.")
        return None

    print("Final response is not empty.")

    # 2. Check for medical diagnosis claims
    unsafe_phrases = [
        "you have",
        "you are diagnosed with",
        "this will cure",
        "this cures",
        "take this medicine",
    ]

    response_lower = response.lower()

    for phrase in unsafe_phrases:
        if phrase in response_lower:
            print(f"⚠️ Possible medical claim detected: '{phrase}'")

    # 3. Display the user's budget and check if the output is within the budget
    
    budget = state.get("budget")

    if budget is not None:
        print(f"User budget: {budget} EGP")

    # 4. Display the user's skin profile
    print(f"🧴 Skin type: {state.get('skin_type')}")
    print(f"🎯 Concerns: {state.get('concerns')}")

    return None