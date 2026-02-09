import os
import logging
import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from src.state import AgentState


def curator_node(state: AgentState):

    logger = logging.getLogger(__name__)

    # Use DeepSeek to curate answers outputed by researcher and return best 5
    deepseek = ChatOpenAI(
        api_key=os.environ.get("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com",
        model="deepseek-chat",
        temperature=0.1,
        model_kwargs={
            "response_format": {"type": "json_object"}
        }
    )

    raw_results = state.get("search_results", [])
    topic = state.get("topic")
    logger.info(f"Curator analyzes {len(raw_results)} sources with DeepSeek")

    if len(raw_results) == 0:
        return {"curated_items": []}
    
    formatted_data = [
        {
            "id": i,
            "title": res["title"],
            "url": res["url"],
            "snippet": res["content"][:500]
        }
      for i, res in enumerate(raw_results)
    ]

    sys_prompt = '''
    You are an editor. Your goal is to filter a list of news items
    Criteria for selection:
        1. Relevance to user's topic
        2. Quality - prefer official, reputable sources
        3. Discard listicles or marketing fluff
        4. Novelty - must be recent

    You must return a JSON object with a single key 'selected_ids' containing the IDs of the top 5 items.
    Example: { "selected_ids": [0, 2, 4, 5, 8] }
    '''

    user_message = f'''
        Topic: {topic}
        Candidates: {json.dumps(formatted_data)}
    '''

    try:
        response = deepseek.invoke([
            SystemMessage(sys_prompt),
            HumanMessage(user_message)
        ])

        decision = json.loads(response.content)
        selected_ids = decision.get("selected_ids", [])

        curated_items = [raw_results[i] for i in selected_ids if i>=0 and i<len(raw_results)]
        logger.info(f"Curator selected {len(curated_items)} items")
        return {"curated_items": curated_items}

    except Exception as e:
        logger.warning(f"Curator ran into error: {e} \n Taking first 5 results")
        #take first 5 results if curator fails
        return {"curated_items": raw_results[:5]}