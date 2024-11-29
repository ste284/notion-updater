import os
import requests
from datetime import datetime, timedelta

# Autenticazione e configurazione
database_id = os.getenv('14b513ef-1961-80a8-8d60-c4437bc114b0')  # Inserisci l'ID del tuo database
notion_token = os.getenv('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')  # Inserisci il token API di Notion
headers = {
    "Authorization": f"Bearer {notion_token}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def get_data():
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    response = requests.post(url, headers=headers)

    if response.status_code != 200:
        print(f"Errore: {response.status_code}, Messaggio: {response.json()}")
        return {}

    print(response.json())  # Per vedere i dati restituiti dall'API
    return response.json()

def day_of_week(date):
    # Restituisce le ore in base al giorno della settimana
    day = date.weekday()  # 0=Monday, 1=Tuesday, ..., 5=Saturday, 6=Sunday
    if day >= 0 and day <= 3:  # Lunedì - Giovedì
        return 8
    elif day == 4:  # Venerdì
        return 4
    return 0  # Sabato e Domenica

def calculate_hours(start_date, end_date):
    # Calcola le ore totali tra due date
    current_date = start_date
    total_hours = 0
    while current_date <= end_date:
        total_hours += day_of_week(current_date)
        current_date += timedelta(days=1)
    return total_hours

# Ottieni i dati dal database
data = get_data()

for entry in data['results']:
    # Estrai le date di inizio e fine dalla colonna "Data inizio/fine attività"
    date_property = entry['properties'].get('Data inizio/fine attività', {}).get('date', None)

    if date_property:
        start_date_str = date_property.get('start', None)
        end_date_str = date_property.get('end', None)

        if start_date_str and end_date_str:
            # Converte le date da stringa a oggetto datetime
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

            # Calcola le ore totali tra Data Inizio e Data Fine
            total_hours = calculate_hours(start_date, end_date)

            # Aggiorna la riga con le ore totali
            update_url = f"https://api.notion.com/v1/pages/{entry['id']}"
            update_data = {
                "properties": {
                    "ore utilizzate": {
                        "number": total_hours
                    }
                }
            }

            update_response = requests.patch(update_url, headers=headers, json=update_data)
            print(f"Ore totali per {entry['id']}: {total_hours}")
        else:
            print(f"Le date di inizio e fine non sono complete per {entry['id']}")
    else:
        print(f"'Data inizio/fine attività' non è presente o è vuota per {entry['id']}")
