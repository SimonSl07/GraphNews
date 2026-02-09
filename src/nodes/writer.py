import os
import logging
import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from src.state import AgentState



def writer_node(state: AgentState):
    
    logger = logging.getLogger(__name__)

    # Use DeepSeek to write newsletter based on curated answers
    deepseek = ChatOpenAI(
        api_key=os.environ.get("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com",
        model="deepseek-chat",
        temperature=0.3
    )

    topic = state['topic']
    curated_items = state['curated_items']
    critique = state.get('critique')
    existing_draft = state.get('draft')
    revision_number = state.get('revision_number', 0)
    logger.info(f"Writer is working on draft #{revision_number + 1}")

    #writing for first time
    if not critique or not existing_draft:
        sys_prompt = """
        You are a newsletter writer. You are concise and technical.
        Structure the newsletter in markdown.        
        Guidelines:
        1. Use a catchy headline
        2. Must include original URLs
        3. Use all sources given
        """

        content_data = "\n".join([
            f"Title: {item['title']}\nURL: {item['url']}\nSummary: {item.get('content', '')[:300]}..."
            for item in curated_items])
        
        user_message = f"""
        TOPIC: {topic}
        SOURCES TO COVER:
        {content_data}
        Write the full newsletter draft.
        """
    #revising
    else:
        sys_prompt = """
        You are an editor. You must fix a draft based on specific critique.
        Refine text to address the critique, don't change unnecessary changes to good parts.
        Return fully updated draft in markdown.
        """

        user_message = f"""
        ORIGINAL DRAFT:
        {existing_draft}

        CRITIQUE:
        {critique}

        Please fix this draft incorporating the critique.
        """ 
    
    try:
        response = deepseek.invoke([
            SystemMessage(sys_prompt),
            HumanMessage(user_message)
        ])
        
        logger.info(f"Writer finished draft #{revision_number + 1}")

        return {
            "draft": response.content,
            "revision_number": revision_number + 1
        }

    except Exception as e:
        logger.warning(f"Writer encountered error {e}")
        return {
            "draft": existing_draft if existing_draft else "error generating draft",
            "revision_number": revision_number + 1
        }