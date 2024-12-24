import requests
from typing import Dict, Union
import time
import sys
from pathlib import Path
import json
from sqlalchemy.exc import IntegrityError
from psycopg2.errorcodes import UNIQUE_VIOLATION
from psycopg2 import errors
from datetime import datetime

sys.path.append(str(Path(__file__).resolve().parent.parent / "code"))
from db import SessionLocal
from models import Market


API_KEY = "579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b"


def validate(obj):
    for key in ["min_price", "max_price", "modal_price"]:
        if not obj[key].isnumeric():
            obj[key] = 0

    obj["arrival_date"] = datetime.strptime(obj["arrival_date"], "%d/%m/%Y").isoformat()

    return obj


if __name__ == "__main__":
    print(
        "Starting data scraping for Current Daily Price Of Various Commodities From Various Markets"
    )

    start_time = time.time()

    # API Params
    URL = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
    params: Dict[str, Union[str, int]] = {
        "api-key": API_KEY,
        "format": "json",
        "offset": 0,
    }
    db = SessionLocal()

    while True:
        print(f"Sending with offset:{params['offset']}")

        try:
            response = requests.get(URL, params)
            if response.status_code == 200:
                results = response.json()
            else:
                print(
                    f"Request failed with status code: {response.status_code}", response
                )
                print("Continuing to the next request")
                continue
        except Exception as e:
            print("Exception occured while sending request. Check the script", e)
            sys.exit(1)

        data = results["records"]
        updated_date = results["updated_date"]
        if len(data) == 0:
            print("All data seeded. Exiting now...")
            break
        else:
            print(f"Adding data to the DB for offset:{params['offset']}")
            for value in data:
                try:
                    db_objet = Market(**validate(value), updated_date=updated_date)
                    db.add(db_objet)
                    db.commit()
                    print("Data added successfully")
                except IntegrityError as e:
                    print("Duplicate data found, Skipping")
                    db.rollback()
                    pass
                except Exception as e:
                    print("Exception occured while adding data. Check the script", e)
                    db.close()
                    sys.exit(1)

        params["offset"] = int(params["offset"]) + 10
        # Delay the next request by 1 second
        time.sleep(1)

    db.close()
    end_time = time.time()
    total_time = round(time.time() - start_time, 2)
    print("Took", total_time, "seconds to complete")
