import os
import logging
import sys
from datetime import date, timedelta
import argparse
from src.graph import build_graph
from dotenv import load_dotenv

#define logging configuration
logging.basicConfig(
        level = logging.WARNING,
        format='%(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)  # Print to console
        ]
    )
logger = logging.getLogger(__name__)


def save_newsletter(content: str, path: str):
    #attempt to save to given path
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Newsletter saved at {path} successfully.")
        return True
    except Exception as e:
        logger.error(f"Failed to save newsletter at {path}: {e}")
    
    #attempt to save at fallback path
    fallback_path = "newsletter.md"
    print(f"Attempting to save to fallback path: {fallback_path}")
   
    try:
        with open(fallback_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Newsletter saved at {fallback_path} successfully.")
    except Exception as e:
        logger.critical(f"Could not save file: {e}")

if __name__ == "__main__":

    #create default topic
    yesterday = date.today() - timedelta(days=1)
    formatted = yesterday.strftime("%B %d %Y")
    default_topic = f"News of {formatted}" 

    #create argument parser
    parser = argparse.ArgumentParser(
        prog="GraphNews",
        description="GraphNews: multi-agent system that acts as a self-correcting editorial team, generating newsletters"
    )
    parser.add_argument("--topic", default=default_topic, help=f"topic to be created by newsletter (default: {default_topic})")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--dest", "-d", default="newsletter.md", help="File path to store newsletter (default: newsletter.md)")
    args = parser.parse_args()
    
    #define logger configuration based on verbose argument value
    logging.getLogger().setLevel(logging.INFO if args.verbose else logging.WARNING)

    load_dotenv() #load environment

    try:
        app = build_graph()


        initial_state = {"topic": args.topic, "revision_number": 0}
        print("Starting newsletter team")
        result = app.invoke(initial_state)

        #print newsletter draft to console
        print("Final Newsletter Draft:\n")
        print("-" * 40)
        print(result['draft'])
        print("-" * 40)
        print(f"\nFinal Score: {result['final_score']}/10")

        save_newsletter(result['draft'], args.dest) #save newsletter at destination
    except Exception as e:
        logger.critical(f"Execution failed: {e}")
        sys.exit(1)