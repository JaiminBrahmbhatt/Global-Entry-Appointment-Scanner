import time
# from twilio.rest import Client
import requests
from dateutil import parser
from dateutil.tz import gettz
import logging
import sys
import heapq
from typing import Optional, Dict, List, Tuple, Set
import datetime


# Create client
account_sid = ''  # TODO: Grab from Twilio
auth_token = ''  # TODO: Grab from Twilio
# client = Client(account_sid, auth_token)

# Configuration
API_URL_TEMPLATE: str = 'https://ttp.cbp.dhs.gov/schedulerapi/slots?orderBy=soonest&limit=5&locationId={}&minimum=1'
LOCATION_DETAILS: Dict[int, str] = {
    7820: 'Austin',
    5141: 'Houston',
    7520: 'San Antonio'
}
CHECK_INTERVAL: int = 60 * 15  # 15 minutes
ERROR_INTERVAL: int = 60  # 1 minute

# Global variable to track the last notified appointment start time for each location
appointment_history: Dict[int, List[str]] = {}

def notify(message: str) -> None:
    print(f"🔔 Notification: {message}")
    # client.messages.create(
    #     to='',  # TODO: Grab from Twilio
    #     from_='',  # TODO: Grab from Twilio
    #     body=message
    # )

def fetch_appointments(location_id: int) -> Optional[List[Dict[str, str]]]:
    """Fetches the earliest available appointments for a given location."""
    api_url: str = API_URL_TEMPLATE.format(location_id)

    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        return response.json()

    except requests.RequestException as error:
        notify(f"Error for location ID {location_id}: {error}")
        return None

def format_timestamp(timestamp: str) -> str:
    """Formats the ISO 8601 timestamp into a more readable format and converts it to CST."""
    date_time_obj = parser.parse(timestamp)
    cst_timezone = gettz('America/Chicago')
    cst_time = date_time_obj.astimezone(cst_timezone)
    return cst_time.strftime('%Y-%m-%d %H:%M CST')

def process_appointments(location_id: int, city_name: str) -> bool:
    """Processes appointments for a specific location."""
    appointments = fetch_appointments(location_id)

    if not appointments:
        print(f"🚫 No appointments found in {city_name}.")
        return True
    # Initialize the location's history if not already present
    if location_id not in appointment_history:
        appointment_history[location_id] = []

    current_year = datetime.datetime.now().year
    next_year = current_year + 1

    for appointment in appointments:
        appointment_start = appointment.get('startTimestamp', '2099-01-01T00:00')
        formatted_start = format_timestamp(appointment_start)

        # Check if the appointment is in the current year or next year and not already notified
        if (str(current_year) in formatted_start or str(next_year) in formatted_start) and formatted_start not in appointment_history[location_id]:
            notify(f"✨ New appointment available on {formatted_start} in {city_name}!")

        # Manage the appointment history using a min-heap
        if len(appointment_history[location_id]) < 5:
            heapq.heappush(appointment_history[location_id], formatted_start)
        elif formatted_start < appointment_history[location_id][0]:
            heapq.heapreplace(appointment_history[location_id], formatted_start)

    print(f"📅 Updated appointments for {city_name}: {sorted(appointment_history[location_id])}")
    return False

def main() -> None:
    """Main function to run the script."""
    try:
      print("⏰ Checking for appointments...")
      while True:
          errors: List[bool] = [process_appointments(loc_id, city) for loc_id, city in LOCATION_DETAILS.items()]

          print("⏰ Waiting for {} seconds before next check...".format(ERROR_INTERVAL if any(errors) else CHECK_INTERVAL))
          time.sleep(ERROR_INTERVAL if any(errors) else CHECK_INTERVAL)
    except KeyboardInterrupt:
        print("🛑 Exiting...")
        sys.exit(0)

if __name__ == "__main__":
    main()
