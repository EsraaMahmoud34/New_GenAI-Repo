import os
from pathlib import Path
from typing import TypedDict

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("Missing GROQ_API_KEY in .env file")

model = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=api_key,
    temperature=0
)

class State(TypedDict):
    task: str
    plan: list[str]
    current_step: int
    result: str
    success: bool
def analyze_task(state: State):
    task = state["task"]

    print(f"Analyzing task: {task}")

    return {}

def create_plan(state: State):
    task = state["task"]

    prompt = f"""
You are a task planner.

Break the user's task into clear, practical steps.

User task:
{task}

Return only the steps.
Put each step on a separate line.
Do not number the steps.
"""

    response = model.invoke(prompt)

    plan = response.content.strip().split("\n")

    return {
        "plan": plan,
        "current_step": 0
    }

def execute_step(state: State):
    plan = state["plan"]
    current_step = state["current_step"]

    step = plan[current_step]

    print(f"Executing step {current_step + 1}: {step}")

    prompt = f"""
You are executing a task.

Original task:
{state["task"]}

Current step:
{step}

Explain briefly what would be done to complete this step.
"""

    response = model.invoke(prompt)

    return {
        "result": response.content,
        "current_step": current_step + 1
    }

def check_result(state: State):
    result = state["result"]

    print(f"Checking result: {result}")

    prompt = f"""
Evaluate whether the following task step was successfully completed.

Task:
{state["task"]}

Current step:
{state["plan"][state["current_step"]]}

Execution result:
{result}

Return exactly one word:
SUCCESS
or
FAILED
"""

    response = model.invoke(prompt)

    decision = response.content.strip().upper()

    return {
        "success": decision == "SUCCESS"
    }


def replan(state: State):
    print("Re-planning...")

    return {
        "current_step": state["current_step"]
    }
#nodes
workflow = StateGraph(State)
workflow.add_node("analyze_task", analyze_task)
workflow.add_node("create_plan", create_plan)
workflow.add_node("execute_step", execute_step)
workflow.add_node("check_result", check_result)
workflow.add_node("replan", replan)

#edges
workflow.add_edge(START, "analyze_task")
workflow.add_edge("analyze_task", "create_plan")
workflow.add_edge("create_plan", "execute_step")
workflow.add_edge("execute_step", "check_result")

def route_after_check(state: State):
    if not state["success"]:
        return "failed"

    if state["current_step"] < len(state["plan"]) - 1:
        return "continue"

    return "success"

workflow.add_edge("replan", "execute_step")
graph = workflow.compile()
initial_state = {
    "task": "Prepare for firs langgraph project",
    "plan": [],
    "current_step": 0,
    "result": "",
    "success": False
}

result = graph.invoke(initial_state)

print(result)