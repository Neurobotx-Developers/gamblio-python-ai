import requests
import os
def add_qa_to_database(question, answer):
    url = "https://gamblio-back.neurobotx.dev/api/knowledge/add-qa/"
    body = {
        "question": question,
        "answer": answer.answer
    }
    response = requests.post(url, json=body)
    return response.json()  # Vraća odgovor u JSON formatu
