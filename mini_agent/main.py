import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from tools import build_routine, get_product, compare_products
from state import AgentState, UserProfile
from middlewares import ProfileMiddleware, check_model_response, validate_final_response
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents.middleware import SummarizationMiddleware, ToolCallLimitMiddleware, ToolRetryMiddleware
from gardrails import skincare_scope_guardrail, budget_guardrail
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("Missing GROQ_API_KEY in .env file")

model = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=api_key,
    temperature=0
)
config = {
    "configurable": {
        "thread_id": "skincare_session_1"
    }
}
#structured model for extracting user profile and middleware for updating the agent state with the extracted profile
profile_middleware = ProfileMiddleware(model)

Agent=create_agent(
    model=model,
    tools=[build_routine, get_product, compare_products],
    system_prompt="""
    You are an AI skincare routine advisor.

    Your job is to help users build a simple skincare
    routine and recommend suitable skincare products.

    First understand the user's:
    - skin type
    - skincare concerns
    - budget
    - preferences

    Use the build_routine tool to determine the required
    routine steps.

    Use the search_products tool to find products that
    match the user's requirements.

    Explain your recommendations clearly.

    Do not make medical diagnoses or claim to treat
    medical conditions.
    """,
    checkpointer=InMemorySaver(),
    state_schema=AgentState,
    middleware=[profile_middleware,
                SummarizationMiddleware(model=model,
                                        trigger=("messages", 20),
                                        keep=("messages", 10)),
                ToolCallLimitMiddleware(run_limit=5),
                ToolRetryMiddleware(max_retries=3),
                check_model_response,
                validate_final_response,
                budget_guardrail],
)
while True:

    user_input = input("\nYou: ")
    if not skincare_scope_guardrail(user_input):
        print("🛑 Request is outside the skincare scope.")
        continue

    if user_input.lower() in ["exit", "quit"]:
        break

    response = Agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": user_input
                }
            ]
        },
        config=config
    )

    print("\nAgent:", response["messages"][-1].content)