from websockets.sync.client import connect
import json
from config import WEBSOCKET_URL
import asyncio
import websockets
from sqlalchemy import create_engine, text
import os
from openai import OpenAI
from embeddings import calculate_embedding
from database import DB_ENGINE

DB_CONNECTION = DB_ENGINE.connect()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)
from app import create_assistant, create_thread, add_message_to_thread, run_assistant
import time

global assistant
assistant = create_assistant()


async def send(websocket, message):
    await websocket.send(json.dumps(message))
    print(f"Sent: {message}")


async def receive(websocket):
    response = json.loads(await websocket.recv())
    print(f"Received: {response}")

    return response


def search_qa_table(question):
    embedding = calculate_embedding(question)

    query = text(
        f"SELECT question, answer FROM qa WHERE question_embedding <-> '{embedding}' < :similarity ORDER BY question_embedding <-> '{embedding}';"
    )

    result = DB_CONNECTION.execute(query, {"similarity": 0.5})

    rows = result.fetchall()

    result = "\n"
    for row in rows:
        question, answer = row

        result += f"# Pitanje: {question}\n"
        result += f"Odgovor: {answer}\n"
        result += "--------------\n"

    result += "\n"
    return result


def reformat_answer(answer):
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

    return completion.choices[0].message.content


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

    result = DB_CONNECTION.execute(query, {"similarity": 0.5})

    rows = result.fetchall()

    result = "\n"
    i = 1
    for row in rows:
        chat_id = row[0]

        query = text(
            f"""
                SELECT id, message, chat_id FROM legacy
                WHERE chat_id = {chat_id}
                ORDER BY id DESC;
            """
        )

        message_rows = DB_CONNECTION.execute(query).fetchall()

        result += "# Chat {i}\n"
        for message_row in message_rows:
            (_, message, _) = message_row
            result += f"{message}\n"
        result += "--------------\n"

        i += 1

    result += "\n"
    return result


def get_openai_response(question):
    # Ispod izvuci poruke iz legacy baze i proslijedit ih u create thread kao param
    thread = create_thread()

    knowledge = search_legacy_table(question)
    add_message_to_thread(thread.id, "user", question, knowledge)

    run = run_assistant(thread.id, assistant.id, assistant.instructions)

    timeout = 60  # seconds
    start_time = time.time()

    while run.status != "completed":
        if time.time() - start_time > timeout:
            return {"sure": "false", "answer": ""}
        print("Waiting for the run to complete...")
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

    messages = client.beta.threads.messages.list(thread_id=thread.id)
    print(messages.data[0].content[0].text.value)
    return messages.data[0].content[0].text.value


async def connect_and_communicate():

    async with websockets.connect(WEBSOCKET_URL) as websocket:
        await send(websocket, {"tag": "bot_subscribe", "chat_id": 349})

        while True:
            received = await receive(websocket)
            if not "text" in received:
                continue

            question = received["text"]

            answer = search_qa_table(question)
            print(f"QA ANSWER: {answer}")
            if answer.strip() != "":
                answer = reformat_answer(answer)
                print(f"FORMATTED QA ANSWER: {answer}")
            else:
                answer = get_openai_response(question)
                print(f"OPENAI ANSWER: {answer}")

            await send(websocket, {"tag": "bot_send", "chat_id": 349, "text": answer})


# Run the client connection
asyncio.get_event_loop().run_until_complete(connect_and_communicate())
