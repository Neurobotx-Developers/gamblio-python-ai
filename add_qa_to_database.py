import requests
import json

def add_qa_to_database(question, answer):
    url = "https://gamblio-back.neurobotx.dev/api/knowledge/add-qa/"
    print(f"ANSWER U FUNK: {answer}")

    # Ensure `answer` is a dictionary before dumping it to JSON
    if isinstance(answer, str):
        try:
            answer = json.loads(answer)  # Convert string to dictionary
        except json.JSONDecodeError:
            raise ValueError("The `answer` must be a valid JSON string or a dictionary.")

    print(f"ANSWER AS DICTIONARY: {answer}")
    
    # No need to dump the `answer` to JSON if it will be part of the body
    body = {
        "question": question,
        "answer": answer.get('answer')  # Safely access 'answer' field from the dictionary
    }
    
    print(f"REQUEST BODY: {body}")
    response = requests.post(url, json=body)  # Automatically serializes the body to JSON
    print(f"RESPONSE: {response.status_code} - {response.text}")
    return response.json()  # Return response in JSON format
