import requests
import os
def add_qa_to_database(question, answer):
    url = os.getenv("QA_API_URL")
    body = {
        "question": question,
        "answer": answer
    }
    response = requests.post(url, json=body)
    return response.json()  # Vraća odgovor u JSON formatu
