import requests
import json

def add_qa_to_database(question, answer):
    url = "https://gamblio-back.neurobotx.dev/api/knowledge/add-qa/"

    # Extract the 'answer' field from the answer dictionary
    if isinstance(answer, dict):
        answer_json_str = answer['answer']  # Get the JSON string nested in the dictionary
        answer_obj = json.loads(answer_json_str)  # Convert JSON string to a Python object
    else:
        raise ValueError("The 'answer' parameter must be a dictionary containing an 'answer' key.")

    # Prepare the body with the question and the extracted "answer"
    body = {
        "question": question,
        "answer": answer_obj["answer"]  # Access the "answer" field from the extracted object
    }

    # Send the POST request
    response = requests.post(url, json=body)

    # Return the response in JSON format
    return response.json()
