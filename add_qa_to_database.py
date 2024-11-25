import requests
import os
def send_qa_to_api(question, answer):
    url = os.getenv("QA_API_URL")
    body = {
        "question": question,
        "answer": answer
    }
    response = requests.post(url, json=body)
    return response.json()  # Vraća odgovor u JSON formatu
