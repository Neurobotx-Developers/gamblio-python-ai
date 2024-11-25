import requests
import os
import json
def add_qa_to_database(question, answer):
    url = "https://gamblio-back.neurobotx.dev/api/knowledge/add-qa/"
    print(f"ANSWER U FUNK: {answer}")
    answer_json = json.dumps(answer)  # Convert answer to JSON
    print(f"ANSWER U JSON: {answer_json}")

    body = {
        "question": question,
        "answer": answer_json["answer"]
    }
    response = requests.post(url, json=body)
    return response.json()  # Vraća odgovor u JSON formatu
