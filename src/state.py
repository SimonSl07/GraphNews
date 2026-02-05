from typing import TypedDict, List

class AgentState(TypedDict):
    topic: str
    search_results: List[str]
    curated_items: List[str]
    draft: str
    critique: str
    revision_number: int
    final_score: int