from langchain.agents.middleware import after_agent
import re

#before the model and after the agent, @inputgardrails and @outputgardrails are used to validate the input and output
def skincare_scope_guardrail(user_message: str) -> bool:
    """
    Check whether the user's request is related to skincare.
    Returns True if the request is allowed.
    """

    skincare_keywords = [
        "skin",
        "skincare",
        "acne",
        "pimple",
        "dryness",
        "oily",
        "dry skin",
        "combination",
        "moisturizer",
        "cleanser",
        "serum",
        "sunscreen",
        "routine",
        "blackheads",
        "pores",
    ]

    message = user_message.lower()

    return any(keyword in message for keyword in skincare_keywords)


@after_agent
def budget_guardrail(state, runtime):

    budget = state.get("budget")

    if budget is None:
        return None

    final_message = state["messages"][-1]
    response = final_message.content

    prices = re.findall(
        r"(\d+(?:\.\d+)?)\s*(?:EGP|LE)",
        response
    )

    if not prices:
        return None

    total = sum(float(price) for price in prices)

    print("\n--- BUDGET GUARDRAIL ---")
    print(f"User budget: {budget} EGP")
    print(f"Detected total: {total} EGP")

    if total > budget:
        print("🛑 Budget guardrail triggered!")
        print("The recommendation exceeds the user's budget.")

    else:
        print("✅ Recommendation is within budget.")

    return None