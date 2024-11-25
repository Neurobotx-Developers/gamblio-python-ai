import requests
import json

def add_qa_to_database(question, answer):
    url = "https://gamblio-back.neurobotx.dev/api/knowledge/add-qa/"
    
    # Parse the answer JSON string into a Python object (dictionary)
    answer_obj = json.loads(answer)  # Ensure answer is a JSON string
    
    # Extract the "answer" field from the parsed object
    body = {
        "question": question,
        "answer": answer_obj["answer"]  # Access the "answer" field
    }
    
    # Send the POST request
    response = requests.post(url, json=body)
    
    # Return the response in JSON format
    return response.json()
