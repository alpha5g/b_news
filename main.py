import json
import time
from datetime import datetime
from zoneinfo import ZoneInfo

import requests


URL = (
    "https://www.binance.com/bapi/apex/v1/public/apex/cms/article/"
    "list/query?type=1&pageNo=1&pageSize=20&catalogId=48"
)

INTERVAL = 0.2  # 200 ms between requests
TIMEOUT = 10
ERROR_FILE = "error.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json, text/plain, */*",
}

# India Standard Time
IST = ZoneInfo("Asia/Kolkata")


def save_error(request_number: int, error: Exception) -> dict:
    error_data = {
        "timestamp": datetime.now(IST).isoformat(timespec="milliseconds"),
        "request_number": request_number,
        "url": URL,
        "error_type": type(error).__name__,
        "error": str(error),
    }

    # Creates error.json if it does not exist.
    # If it already exists, it is overwritten.
    with open(ERROR_FILE, "w", encoding="utf-8") as file:
        json.dump(
            error_data,
            file,
            indent=4,
            ensure_ascii=False
        )

    return error_data


def main() -> None:
    request_count = 0

    print("Started. Requesting every 0.2 seconds...")
    print("Timestamp timezone: IST (Asia/Kolkata)")
    print("The program will stop immediately after the first error.")
    print()

    with requests.Session() as session:
        session.headers.update(HEADERS)

        try:
            while True:
                start = time.monotonic()
                request_count += 1

                try:
                    response = session.get(
                        URL,
                        timeout=TIMEOUT
                    )

                    # Treat HTTP 4xx/5xx responses as errors
                    response.raise_for_status()

                    # Make sure Binance returned valid JSON
                    response.json()

                    timestamp = datetime.now(IST).strftime(
                        "%Y-%m-%d %H:%M:%S.%f"
                    )[:-3]

                    print(
                        f"[{timestamp} IST] "
                        f"Request #{request_count} | "
                        f"HTTP {response.status_code}"
                    )

                except Exception as error:
                    error_data = save_error(
                        request_count,
                        error
                    )

                    print("\nERROR OCCURRED")
                    print(
                        json.dumps(
                            error_data,
                            indent=4,
                            ensure_ascii=False
                        )
                    )

                    print(f"\nError saved to: {ERROR_FILE}")
                    print("Stopping...")

                    break

                # Maintain approximately 0.2 seconds between requests
                elapsed = time.monotonic() - start
                sleep_time = max(0, INTERVAL - elapsed)

                time.sleep(sleep_time)

        except KeyboardInterrupt:
            print("\nStopped by user.")


if __name__ == "__main__":
    main()
