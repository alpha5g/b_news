import requests
import time
import json
from datetime import datetime, timezone

URL = "https://www.binance.com/bapi/apex/v1/public/apex/cms/article/list/query?type=1&pageNo=1&pageSize=20&catalogId=48"

INTERVAL = 0.2       # 200 ms = 5 requests/second
TIMEOUT = 10         # seconds
ERROR_FILE = "error.json"

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json, text/plain, */*",
}

session = requests.Session()
session.headers.update(headers)

request_count = 0

print("Started. Requesting every 0.2 seconds...")
print("The program will stop immediately after the first error.")

try:
    while True:
        start = time.monotonic()
        request_count += 1

        try:
            response = session.get(
                URL,
                timeout=TIMEOUT
            )

            # Treat HTTP 4xx/5xx as an error
            response.raise_for_status()

            # Make sure Binance returned valid JSON
            data = response.json()

            print(
                f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}] "
                f"Request #{request_count} | "
                f"HTTP {response.status_code}"
            )

        except Exception as e:
            error_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "request_number": request_count,
                "url": URL,
                "error_type": type(e).__name__,
                "error": str(e),
            }

            # Store the error in JSON
            with open(ERROR_FILE, "w", encoding="utf-8") as f:
                json.dump(error_data, f, indent=4, ensure_ascii=False)

            print("\nERROR OCCURRED")
            print(json.dumps(error_data, indent=4, ensure_ascii=False))
            print(f"\nError saved to: {ERROR_FILE}")
            print("Stopping...")

            break

        # Maintain approximately 0.2 seconds between requests
        elapsed = time.monotonic() - start
        sleep_time = max(0, INTERVAL - elapsed)

        time.sleep(sleep_time)

finally:
    session.close()
