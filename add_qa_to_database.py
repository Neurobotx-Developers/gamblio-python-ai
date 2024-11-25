import requests
import json

def add_qa_to_database(question, answer):
    url = "https://gamblio-back.neurobotx.dev/api/knowledge/add-qa/"

    
    if isinstance(answer, str):
        try:
            answer = json.loads(answer)  
        except json.JSONDecodeError:
            raise ValueError("The `answer` must be a valid JSON string or a dictionary.")

    
    body = {
        "question": question,
        "answer": answer.get('answer')  
    }
    
    response = requests.post(url, json=body)  
    return response.json()  
