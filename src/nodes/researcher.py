import os
from tavily import TavilyClient
from src.state import AgentState


def researcher_node(state: AgentState):
    tavily = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
    print(f"Research starts searching for {state['topic']}")
    # try running tavily to research topic
    try:
        response = tavily.search(
            query=state['topic'],
            search_depth="advanced",
            max_results = 10
        )
    except Exception as e:
        print(f"Error in Tavily Search: {e}")
        return {"search_results": []}
    
    raw_results = response.get("results", [])
    seen_urls = set()
    final_results = []

    #remove duplicate urls
    for result in raw_results:
        url = result.get("url")
        if url in seen_urls:
            continue
        seen_urls.add(url)
        final_results.append({
            "title": result.get("title"),
            "url": url,
            "content": result.get("content"),
            "score": result.get("score")
        })
    
    print(f"Researcher found {len(final_results)} results")
    #return unique answers
    return {"search_results": final_results}


