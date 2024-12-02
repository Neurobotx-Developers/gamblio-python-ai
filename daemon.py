import asyncio
from queue import Queue
import time
import json
from config import CONFIG
import websockets
from sqlalchemy import text
from openai import OpenAI
from embeddings import calculate_embedding
from database import DB_ENGINE, CHAT_DB_ENGINE
from concurrent.futures import ThreadPoolExecutor
from caluculate_cost import calculate_openai_cost
from add_qa_to_database import add_qa_to_database

THREAD_POOL_EXECUTOR = ThreadPoolExecutor(max_workers=10)

DB_CONNECTION = DB_ENGINE.connect()

# db za chatove u realnom vremenu
CHAT_DB_CONNECTION = CHAT_DB_ENGINE.connect()


api_key = CONFIG["OPENAI_API_KEY"]
client = OpenAI(api_key=api_key)
from app import create_assistant, create_thread, add_message_to_thread, run_assistant
import time

global assistant
assistant = create_assistant()


def search_qa_table(question):
    embedding = calculate_embedding(question)

    query = text(
        f"SELECT question, answer FROM qa WHERE question_embedding <-> '{embedding}' < :similarity ORDER BY question_embedding <-> '{embedding}';"
    )

    result = DB_CONNECTION.execute(query, {"similarity": 0.3})

    rows = result.fetchall()
    print(rows[0])
    result = f"{rows[0].answer}"
   
    
    return result


def reformat_answer(answer, chat_id):
    query = text(
        f"""
        SELECT content, role FROM chat_message
        WHERE chat_id = {chat_id}
        ORDER BY timestamp ASC;
        """
    )
    messages_rows = CHAT_DB_CONNECTION.execute(query).fetchall()
    print(messages_rows)

    # Convert to array of objects with content and role
    messages_array = []
    messages_array = [
        {"content": row[0], "role": row[1]} for row in messages_rows
    ]  # Create an array of objects
    print("Chatovi:", messages_array)  # Debug print

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Zdravo, kako ti mogu pomoci danas?",
            },
            {
                "role": "user",
                "content": 'Vi ste korisnički asistent za Admiral Bet Crna Gora, valuta je evro i govorite ijekavicom. Vaš zadatak je da promovišete Admiral Bet i njegove igre i iskljucivo odgovarate na pitanja vezana za Admiral Bet i njegove igre, te da pomažete korisnicima kao da ste stvarna osoba iz korisničke podrške. Nikada ne pominjete druge kladionice. Json odgovor. Format odgovora u JSON-u: {{"sure":true - ako si siguran da mozes dati validan odgovor. / false - ako mislis da na pitanje treba odgovoriti korisnicka podrska, "answer":"" - ako mislis da na to pitanje treba odgovoriti korisnicka podrska/"ili neki tekst ukoliko si nasao odgovor u bazi znanja"}}',
            },
            {
                "role": "system",
                "content": "U redu, shvatam. Imate li dodatne instrukcije za moje buduce ponasanje?",
            },
            {
                "role": "user",
                "content": f"Ovo je vaša istorija razgovora: '''{messages_array}'''",
            },
            {
                "role": "system",
                "content": "U redu, shvatam. Iskoristicu nase prethodne poruke kako bih davao smislene odgovore. Imate li dodatne instrukcije za moje buduce ponasanje?",
            },
            {
                "role": "user",
                "content": "Daj kratke i precizne odgovore. Koristi ijekavski dijalekt crnogorskog jezika. Nikada ne pominji fajl znanja.",
            },
            {
                "role": "system",
                "content": "U redu.",
            },
            {
                "role": "user",
                "content": f"Ne pominji imena korisnika u poruci, ucini je da bude univerzalna po kontekstu i iskoristi znanje koje ti posaljem da odgovoris: Znanje: '''Marko, da bi bonus mogli koristiti, potrebno je da Vam na keš balansu stanje bude 0 eur'''",
            },
            {
                "role": "system",
                "content": '{"sure":true, "answer":"Da bi bonus mogao biti iskoristen, potrebno je da Vam na keš balansu stanje bude 0 eur"}',
            },
            {
                "role": "user",
                "content": "Ko je dejo savicevic?",
            },
            {
                "role": "system",
                "content": '{"sure":true, "answer":"Ne mogu odgovoriti na to pitanje. Mogu samo odgovarati na pitanja vezana za Admiral BET"}',
            },
            {
                "role": "user",
                "content": "Dajte mi 10 eura bonusa molim vas",
            },
            {
                "role": "system",
                "content": '{"sure":false, "answer":""}',
            },
            {
                "role": "user",
                "content": f"Ne pominji imena korisnika u poruci, ucini je da bude univerzalna po kontekstu i iskoristi znanje koje ti posaljem da odgovoris: Znanje: '''{answer}'''",
            },
        ],
    )

    return completion


def search_legacy_table(question):
    embedding = calculate_embedding(question)

    query = text(
        f"""
        SELECT * FROM (
            SELECT DISTINCT ON (chat_id) *, (embedding <-> '{embedding}') as distance
            FROM legacy
        )
        WHERE distance < :similarity
        ORDER BY distance
        LIMIT 2;
        """
    )

    result = DB_CONNECTION.execute(query, {"similarity": 0.2})

    rows = result.fetchall()

    result = "\n"
    i = 1
    for row in rows:
        chat_id = row[1]

        query = text(
            f"""
                SELECT id, message, chat_id FROM legacy
                WHERE chat_id = {chat_id}
                ORDER BY id DESC;
            """
        )

        message_rows = DB_CONNECTION.execute(query).fetchall()

        result += f"# Chat {i}\n"
        for message_row in message_rows:
            (_, message, _) = message_row
            result += message
            result += "\n"
        result += "--------------\n"

        i += 1

    result += "\n"
    return result


def get_openai_response(question, chat_id):
    thread = create_thread()

    knowledge = search_legacy_table(question)

    query = text(
        f"""
        SELECT content, role FROM chat_message  -- Assuming role is also stored in the database
        WHERE chat_id = {chat_id}
        ORDER BY timestamp ASC;
        """
    )
    messages_rows = CHAT_DB_CONNECTION.execute(query, {"id": chat_id}).fetchall()
    print(f"message rows: {messages_rows}")
    # Convert to array of objects with content and role
    messages_array = [
        {"content": row[0], "role": row[1]} for row in messages_rows
    ]  # Create an array of objects

    print("Chatovi:", messages_array)  # Debug print
    print("Legacy:", knowledge)
    add_message_to_thread(thread.id, "user", question, knowledge, messages_array)

    # New code to fetch messages from CHAT DB based on chat_id

    run = run_assistant(thread.id, assistant.id, assistant.instructions)
    timeout = 60  # seconds
    start_time = time.time()

    while run.status != "completed":
        print(f"run status: {run.status}")
        if time.time() - start_time > timeout:
            return {"sure": "false", "answer": ""}
        print("Waiting for the run to complete...")
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

    input_tokens = run.usage.prompt_tokens
    output_tokens = run.usage.completion_tokens

    messages = client.beta.threads.messages.list(thread_id=thread.id)
    print("Posle povlacenja liste poruka")

    return {
        "answer": messages.data[0].content[0].text.value,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
    }


# A queue for incoming messages
message_queue = Queue()


def process_message_get_answer(data, websocket):
    input_tokens = 0
    output_tokens = 0
    source = "vector"

    question = data["question"]
    chat_id = data["chat_id"]

    answer = search_qa_table(question)

    print(f"QA ANSWER: {answer}")
    if answer.strip() != "":
        result = json.dumps(
            {
                "source": "vector",
                "cost": {"input": 0, "output": 0},
                "data": {"sure": True, "answer": answer},
            }
        )

    else:
        source = "ai"
        response = get_openai_response(question, chat_id)
        answer = json.loads(response["answer"])
        print(response)
        input_tokens = response["input_tokens"]
        output_tokens = response["output_tokens"]
        calculated_cost = calculate_openai_cost(input_tokens, output_tokens)

        add_qa_to_database(question, answer)

        result = json.dumps({"source": source, "cost": calculated_cost, "data": answer})

    asyncio.run(websocket.send(result))


def process_message_get_embedding(data, websocket):
    text = data["text"]

    embedding = calculate_embedding(text)

    asyncio.run(websocket.send(embedding))


def process_message(message, websocket):
    try:
        if (not "tag" in message) or (not "data" in message):
            print(f"Invalid message, skipping: {message}")
            return

        tag = message["tag"]
        data = message["data"]

        if tag == "get_answer":
            process_message_get_answer(data, websocket)
        elif tag == "get_embedding":
            process_message_get_embedding(data, websocket)
    except Exception as e:
        print(e)


# Background task to handle processing the queue
async def handle_queue():
    while True:
        if not message_queue.empty():
            websocket, message = message_queue.get()

            THREAD_POOL_EXECUTOR.submit(process_message, message, websocket)
        else:
            await asyncio.sleep(0.1)  # Avoid busy waiting


# Handler for each WebSocket client connection
async def client_handler(websocket, path):
    try:
        async for message in websocket:
            print(f"Received message: {message}")

            message = json.loads(message)

            message_queue.put((websocket, message))  # Pass chat_id to the queue
    except Exception as e:
        print(f"Error in connection handler: {e}")


# Start the WebSocket server
async def main():
    # Start the background queue processing task
    asyncio.create_task(handle_queue())

    # Run the WebSocket server
    async with websockets.serve(client_handler, "localhost", 8765):
        print("Server started on ws://localhost:8765")
        await asyncio.Future()  # Run forever


# Run the main function
asyncio.run(main())