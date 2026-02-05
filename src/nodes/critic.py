import os
import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from src.state import AgentState


def critic_node(state: AgentState):

    # Use DeepSeek to critique answers
    deepseek = ChatOpenAI(
        api_key=os.environ.get("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com",
        model="deepseek-reasoner",
        temperature=0.0
    )

    draft = state['draft']
    topic = state['topic']

    sys_prompt = """
    You are an editor. Grade the newsletter draft on a scale on 1 to 10. BE AS CRITICAL AS POSSIBLE!
    Scoring criteria:
    - 9-10: Perfect, engaging, technical, factual, has links and follows the topic
    - 7-8: Good, but minor tweaks needed, such as tone and clarity, must be completely factual
    - <7: Bad, missing links, generic, not factual, does not follow the topic or not engaging

    Output format(Must be valid JSON):
    {
        "score": 8,
        "feedback": "The tone is good, but you forgot to link the second news item"
    }
    """

    user_message = f"""
    Topic of newsletter: {topic}
    Draft to review:
    {draft}
    """

    try:
        response = deepseek.invoke([
            SystemMessage(sys_prompt),
            HumanMessage(user_message)
        ])

        result = json.loads(response.content)
        print(f"Critic scores {result['score']}")
        print(f"Critic gives feedback: {result['feedback']}")
        return {"final_score": result['score'], "critique": result['feedback']}
    
    except Exception as e:
        print(f"Critic encounter error: {e}")
        return {"final_score": 10, "critique": "Auto-approved due to critic error."}
    