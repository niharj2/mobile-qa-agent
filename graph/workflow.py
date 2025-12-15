from langgraph.graph import StateGraph, END
from graph.state import QAState
from agents.planner import planner
from agents.executor import executor
from agents.supervisor import supervisor

def build_graph():
    graph = StateGraph(QAState)

    graph.add_node("planner", planner)
    graph.add_node("executor", executor)
    graph.add_node("supervisor", supervisor)

    graph.set_entry_point("planner")
    graph.add_edge("planner", "executor")
    graph.add_edge("executor", "supervisor")
    graph.add_edge("supervisor", END)

    return graph.compile()
