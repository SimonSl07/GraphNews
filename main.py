from src.graph import build_graph
from dotenv import load_dotenv
import os
from datetime import date, timedelta


if __name__ == "__main__":
    load_dotenv()
    app = build_graph()
    yesterday = date.today() - timedelta(days=1)
    formatted = yesterday.strftime("%B %d %Y")
    initial_state = {"topic": f"News of {formatted}", "revision_number": 0}
    print("Starting newsletter team...")
    result = app.invoke(initial_state)
    
    print("Final Newsletter Draft:\n")
    print(result['draft'])
    with open("newsletter.md", "w", encoding="utf-8") as f:
        f.write(result['draft'])

    print("File 'newsletter.md' created successfully.")
    print(f"\nFinal Score: {result['final_score']}/10")