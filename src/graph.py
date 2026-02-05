from langgraph.graph import StateGraph, END
from src.state import AgentState
from src.nodes.researcher import researcher_node
from src.nodes.curator import curator_node
from src.nodes.writer import writer_node
from src.nodes.critic import critic_node

def should_continue(state: AgentState):
    score = state.get("final_score", 0)
    revision_number = state.get("revision_number", 0)
    if score >= 8 or revision_number >=3:
        return "end"
    else:
        return "loop"

def build_graph():
    workflow = StateGraph(AgentState)

    # Adding nodes
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("curator", curator_node)
    workflow.add_node("writer", writer_node)
    workflow.add_node("critic", critic_node)

    #Adding edges
    workflow.set_entry_point("researcher")
    workflow.add_edge("researcher", "curator")
    workflow.add_edge("curator", "writer")
    workflow.add_edge("writer", "critic")

    #Conditional edge to make sure answer is of quality (and to stop infinite loop)
    workflow.add_conditional_edges(
        "critic", #node we finished
        should_continue,
        {
            "loop": "writer", #if function returns "loop", go to Writer
            "end": END        #if function returns "end", stop
        }
    )

    return workflow.compile()