from openai import OpenAI
import os

# DB_ENGINE = create_engine('your_database_url')
# DB_CONNECTION = DB_ENGINE.connect()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

question = input("Postavite pitanje: ")

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
            "content": "U redu, shvatam.",
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
            "content": question,
        },
    ],
)

print(completion.choices[0].message.content)
