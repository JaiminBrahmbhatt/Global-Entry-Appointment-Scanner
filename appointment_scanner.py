import requests
from twilio.rest import Client
import time
from dateutil import parser
from dateutil.tz import gettz
import datetime
import heapq
from typing import Dict, List, Optional, NoReturn
from cachetools import cached, TTLCache

# Cache configuration: maxsize is the maximum number of items in the cache, ttl is the time to live in seconds
CACHE_MAXSIZE = 100
CACHE_TTL = 15 * 24 * 60 * 60  # 15 days
cache = TTLCache(maxsize=CACHE_MAXSIZE, ttl=CACHE_TTL)

# API parameters
LIMIT = 5
MINIMUM = 1

APPOINTMENTS_API_URL = 'https://ttp.cbp.dhs.gov/schedulerapi/slots?orderBy=soonest&limit={}&locationId={}&minimum={}'
LOCATIONS_API_URL = 'https://ttp.cbp.dhs.gov/schedulerapi/locations/?temporary=false&inviteOnly=false&operational=true&serviceName=Global%20Entry'
CHECK_INTERVAL = 60 * 15  # 15 minutes
ERROR_INTERVAL = 60  # 1 minute

appointment_history: Dict[int, List[str]] = {}

@cached(cache)
def fetch_locations() -> Dict[str, Dict[str, str]]:
    """Fetches location data from the API and organizes it by city."""
    try:
        response = requests.get(LOCATIONS_API_URL)
        response.raise_for_status()
        return {loc['city'].strip().lower(): loc for loc in response.json()}
    except requests.RequestException as err:
        print(f"HTTP error occurred: {err}")
        return {}

def fetch_appointments(location_id: int) -> Optional[List[Dict[str, str]]]:
    """Fetches the earliest available appointments for a given location."""
    try:
        response = requests.get(APPOINTMENTS_API_URL.format(LIMIT, location_id, MINIMUM), timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as error:
        notify(f"Error for location ID {location_id}: {error}")
        return None

def process_appointments(location_id: int, city_name: str) -> bool:
    """Processes appointments for a specific location."""
    appointments = fetch_appointments(location_id)
    if not appointments:
        print(f"🚫 No appointments found in {city_name}.")
        return True

    if location_id not in appointment_history:
        appointment_history[location_id] = []

    current_year = datetime.datetime.now().year
    for appointment in appointments:
        formatted_start = format_timestamp(appointment['startTimestamp'])
        if formatted_start not in appointment_history[location_id] and str(current_year) in formatted_start:
            notify(f"New appointment available on {formatted_start} in {city_name}")
            heapq.heappush(appointment_history[location_id], formatted_start)
    
    print(f"📅 Updated appointments for {city_name}: {sorted(appointment_history[location_id])}")
    return False

# Notification Options
def notify(message: str) -> None:
    """Notify based on the preferred method"""
    print(f"🔔 Notification: {message}")
    twilio_sms_notify(message)

def twilio_sms_notify(message: str) -> NoReturn:
    """
    Sends an SMS message using Twilio's service.
    Args:
    message (str): The message to be sent via SMS.
    Returns:
    NoReturn
    """
    # Twilio credentials and phone numbers
    account_sid = 'your_account_sid_here'  # Replace with your Twilio Account SID
    auth_token = 'your_auth_token_here'    # Replace with your Twilio Auth Token
    to_number = 'recipient_phone_number'   # Replace with the recipient's phone number
    from_number = 'your_twilio_phone_number'  # Replace with your Twilio phone number
    try:
        # Create the Twilio client
        client = Client(account_sid, auth_token)
        # Send the SMS
        client.messages.create(
            to=to_number,
            from_=from_number,
            body=message
        )
        print("Message sent successfully!")
    except Exception as e:
        print(f"Failed to send message: {e}")

# Utility Functions
def format_timestamp(timestamp: str) -> str:
    """Formats the ISO 8601 timestamp into a more readable format and converts it to CST."""
    cst_time = parser.parse(timestamp).astimezone(gettz('America/Chicago'))
    return cst_time.strftime('%Y-%m-%d %H:%M CST')
    
def lookup_by_city(locations_by_city: Dict[str, Dict[str, str]], city: str) -> Optional[Dict[int, str]]:
    """Looks up location details by city name and returns a dictionary mapping ID to city."""
    location_info = locations_by_city.get(city.lower())
    return {int(location_info['id']): location_info['city']} if location_info else f"No location found for city: {city}"

def main():
    locations_by_city = fetch_locations()
    print("Available cities:", ", ".join(sorted(locations_by_city.keys())).title())
    cities = input("Enter cities of interest (comma-separated): ").split(',')
    location_details = {int(locations_by_city[city.strip().lower()]['id']): city.strip() for city in cities if city.strip().lower() in locations_by_city}

    print("LOCATION_DETAILS:", location_details)
    print("⏰ Checking for appointments...")

    while True:
        errors = [process_appointments(loc_id, city) for loc_id, city in location_details.items()]
        print("⏰ Waiting for {} seconds before next check...".format(ERROR_INTERVAL if any(errors) else CHECK_INTERVAL))
        time.sleep(ERROR_INTERVAL if any(errors) else CHECK_INTERVAL)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("🛑 Exiting...")
