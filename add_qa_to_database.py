import requests
import os
import json
def add_qa_to_database(question, answer):
    url = "https://gamblio-back.neurobotx.dev/api/knowledge/add-qa/"
    answer = json.load(answer)
    body = {
        "question": question,
        "answer": answer.answer
    }
    response = requests.post(url, json=body)
    return response.json()  # Vraća odgovor u JSON formatu
