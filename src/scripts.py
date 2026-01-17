#Імпорт даних з CSV: Створимо CLI-скрипт для імпорту історичних подій з CS
import pandas as pd


def import_events(file_path):
    df = pd.read_csv(file_path)
    events = df.to_dict(orient="records")
    response = requests.post("http://localhost:8000/events", json=events)
    if response.status_code == 200:
        print("Events imported successfully")
    else:
        print("Error importing events")

import_events('../events_sample.csv')
