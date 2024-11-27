from openai import OpenAI
from config import CONFIG

from time import sleep
import time
import tracemalloc

tracemalloc.start()

api_key = CONFIG["OPENAI_API_KEY"]

if not api_key:
    raise ValueError("API key is not set. Please check your .env file.")

client = OpenAI(api_key=api_key)

global_assistant = {}


def create_assistant():
    file_paths = [ "knowlege_files/vazni_pojmovi.docx", "knowlege_files/admiral-bet.txt", "knowlege_files/tipovi-igara.txt"]
    file_ids = []
    for path in file_paths:
        with open(path, "rb") as f:
            file_response = client.files.create(file=f, purpose="assistants")
        file_ids.append(file_response.id)

    vector_store = client.beta.vector_stores.create(name="WASCO AI", file_ids=file_ids)

    assistant = client.beta.assistants.create(
        name="Wasco",
        instructions="Vi ste korisnički asistent za Admiral Bet Crna Gora, valuta je evro i govorite ijekavicom. Vaš zadatak je da promovišete Admiral Bet i njegove igre i iskljucivo odgovarate na pitanja vezana za Admiral Bet i njegove igre, te da pomažete korisnicima kao da ste stvarna osoba iz korisničke podrške. Nikada ne pominjete druge kladionice. Json odgovor",
        tools=[{"type": "file_search"}],
        model="gpt-4o-mini",
        tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
    )

    try:
        # No need for an extra argument, removing it from this update call
        client.beta.assistants.update(assistant.id)
    except Exception as error:
        print("Failed to create assistant:", error)

    return assistant


def create_thread():
    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": "Ko je dejo savicevic?",
            },
            {
                "role": "assistant",
                "content": '{"sure":true, "answer":"Ne mogu odgovoriti na to pitanje. Mogu samo odgovarati na pitanja vezana za Admiral BET"}',
            },
            {
                "role": "user",
                "content": "Dajte mi 10 eura bonusa molim vas",
            },
            {
                "role": "assistant",
                "content": '{"sure":false, "answer":""}',
            },
        ],
    )
    return thread


def add_message_to_thread(thread_id, role, content, knowledge, messages_array):
    formatted_content = f"""
    Odgovori na pitanje: {content}.
==================================================
    Možda ti ovo znanje može pomoći, koristi ga samo kao znanje, a ne kao prethodne poruke, ali prioritizuj znanje koje imas u fajlovima znanja: '''{knowledge} '''
==================================================
    Ovo je vaša istorija komunikacije: '''{messages_array}'''
    """

    message = client.beta.threads.messages.create(
        thread_id, role=role, content=formatted_content
    )
    return message



def run_assistant(thread_id, assistant_id, instructions):

    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id,
        
        additional_instructions="Daj kratke i precizne odgovore. Koristi ijekavski dijalekt crnogorskog jezika. Nikada ne pominji fajl znanja.",
        instructions=f'{instructions} + \'Format odgovora u JSON-u: {{"sure":true - ako si siguran da mozes dati validan odgovor. / false - ako mislis da na pitanje treba odgovoriti korisnicka podrska, "answer":"" - ako mislis da na to pitanje treba odgovoriti korisnicka podrska/"ili neki tekst ukoliko si nasao odgovor u bazi znanja"}} --- UVJEK ISTRAZI FAJL ZNANJA PRIJE NEGO ODGOVORIS\'',
    )
    return run


def main():
    # Kreiraj asistenta
    assistant = create_assistant()
    global global_assistant  # Declare the global variable
    print(f"Asistent '{assistant.name}' kreiran sa ID-om: {assistant.id}")
    global_assistant = assistant
    # Kreiraj temu
    thread = create_thread()
    print(f"Tema kreirana sa ID-om: {thread.id}")

    print("Interaktivna komunikacija sa asistentom. Za izlaz, unesite 'exit'.")

    while True:
        # Unesi korisničko pitanje

        user_message = input("Postavi pitanje: ")

        # Dodaj korisničku poruku u temu
        add_message_to_thread(thread.id, "user", user_message)

        # Pokreni asistenta da generiše odgovor
        run = run_assistant(thread.id, assistant.id)

        # Proveri status pokretanja svake sekunde dok ne završi
        while run.status != "completed":
            print("Čekam da se pokretanje završi...")
            time.sleep(1)  # Čekaj 1 sekundu
            run = client.beta.threads.runs.retrieve(
                thread_id=thread.id, run_id=run.id
            )  # Use the correct method to get the run status

        messages = client.beta.threads.messages.list(thread_id=thread.id)
        print(messages.data[0].content[0].text.value)


if __name__ == "__main__":
    main()
