"""
Scan for available appointments using specific APIs,
send notifications via email or SMS, and manage appointment data.
"""

import logging
import os
import sys
import time
import datetime
import heapq
import smtplib
from typing import Dict, List, Optional, NoReturn
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import dotenv
import requests
from dateutil import parser
from dateutil.tz import gettz
from cachetools import cached, TTLCache
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

# Set up the logger
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()

# Cache configuration:
CACHE_MAXSIZE = 100  # maxsize is the maximum number of items in the cache
CACHE_TTL = 15 * 24 * 60 * 60  # 15 days # ttl is the time to live in seconds
CACHE = TTLCache(maxsize=CACHE_MAXSIZE, ttl=CACHE_TTL)

# API parameters
LIMIT = 5
MINIMUM = 1
APPOINTMENTS_API_URL = (
    "https://ttp.cbp.dhs.gov/schedulerapi/"
    "slots?orderBy=soonest&limit={}&locationId={}&minimum={}"
)

LOCATIONS_API_URL = (
    "https://ttp.cbp.dhs.gov/schedulerapi/locations/?"
    "temporary=false&inviteOnly=false&operational=true&serviceName=Global+Entry"
)

# Check Interval
CHECK_INTERVAL = 60 * 15  # 15 minutes
ERROR_INTERVAL = 60  # 1 minute

# EMAIL configuration
SMTP_SERVER = "smtp.gmail.com"  # SMTP server for Gmail
SMTP_PORT = 587

# Email credentials
dotenv.load_dotenv()
FROM_EMAIL = os.getenv("FROM_EMAIL")
TO_EMAIL = os.getenv("TO_EMAIL")
PASSWORD = os.getenv("PASSWORD")

# Twilio credentials and phone numbers
ACCOUNT_SID = os.getenv("ACCOUNT_SID")  # Replace with your Twilio Account SID
AUTH_TOKEN = os.getenv("AUTH_TOKEN")  # Replace with your Twilio Auth Token
TO_NUMBER = os.getenv("TO_NUMBER")  # Replace with the recipient's phone number
FROM_NUMBER = os.getenv("FROM_NUMBER")  # Replace with your Twilio phone number

appointment_history: Dict[int, List[str]] = {}


@cached(CACHE)
def fetch_locations() -> Dict[str, Dict[str, str]]:
    """Fetches location data from the API and organizes it by city."""
    try:
        response = requests.get(LOCATIONS_API_URL, timeout=10)
        response.raise_for_status()
        return {loc["city"].strip().lower(): loc for loc in response.json()}
    except requests.RequestException as e:
        logger.error("Error fetching locations from API - %s", e)
        return {}
    except TimeoutError as err:
        logger.error("Timeout fetching locations from API - %s", err)
        return {}


def fetch_appointments(location_id: int) -> Optional[List[Dict[str, str]]]:
    """Fetches the earliest available appointments for a given location."""
    try:
        response = requests.get(
            APPOINTMENTS_API_URL.format(LIMIT, location_id, MINIMUM), timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error("Error for location ID %s - %s", location_id, e)
        return None
    except TimeoutError as err:
        logger.error("Timeout error for location ID %s - %s", location_id, err)
        return None


def process_appointments(location_id: int, city_name: str) -> bool:
    """Processes appointments for a specific location."""
    appointments = fetch_appointments(location_id)
    if not appointments:
        logger.info("No appointments found for %s", city_name)
        return True

    if location_id not in appointment_history:
        appointment_history[location_id] = []

    current_year = datetime.datetime.now().year
    for appointment in appointments:
        formatted_start = format_timestamp(appointment["startTimestamp"])
        if (
            formatted_start not in appointment_history[location_id]
            and str(current_year) in formatted_start
        ):
            notify(f"New appointment available on {formatted_start} in {city_name}")
            heapq.heappush(appointment_history[location_id], formatted_start)
    logger.info(
        "Updated appointments for %s - %s",
        city_name,
        sorted(appointment_history[location_id]),
    )
    return False


# Notification Options
def notify(message: str) -> None:
    """Notify based on the preferred method"""

    if (
        len(message.strip()) == 0
    ):
        raise ValueError("Message cannot be empty")

    logger.info("🔔 Notification : %s", message)

    try:
        # send_sms_notification(message)  # uncomment to enable SMS notifications
        send_email_notification("Appointment Available", message)
    except ValueError as ve:
        logger.error("Invalid value: %s", str(ve))


def send_email_notification(subject: str, message: str) -> None:
    """
    Sends an email notification.
    """

    # Validate input parameters
    if not FROM_EMAIL or not TO_EMAIL:
        raise ValueError("FROM_EMAIL and TO_EMAIL are required")
    if not subject:
        raise ValueError("Subject is required")
    if not message:
        raise ValueError("Message is required")
    if not PASSWORD:
        raise ValueError("Password is required")

    # Create MIME multipart message
    msg = MIMEMultipart()
    msg["From"] = FROM_EMAIL
    msg["To"] = TO_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(message, "plain"))

    try:
        # Connect to the SMTP server and send the email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Secure the connection
        server.login(FROM_EMAIL, PASSWORD)
        server.send_message(msg)
        server.quit()
        logger.info("Email sent successfully!")
    except smtplib.SMTPException as e:
        logger.error("Error sending email: %s", e)


def send_sms_notification(message: str) -> NoReturn:
    """
    Sends an SMS message using Twilio's service.
    Args:
    message (str): The message to be sent via SMS.
    Returns:
    NoReturn
    """

    # Validate input parameters
    if not TO_NUMBER or not FROM_NUMBER:
        raise ValueError("To and From numbers are required")
    if not ACCOUNT_SID or not AUTH_TOKEN:
        raise ValueError("Account SID and Auth Token are required")
    if not message:
        raise ValueError("Message is required")

    try:
        # Create the Twilio client
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        # Send the SMS
        client.messages.create(to=TO_NUMBER, from_=FROM_NUMBER, body=message)
        logger.info("SMS sent successfully!")
    except TwilioRestException as e:
        logger.error("Error sending SMS: %s", e)


# Utility Functions
def format_timestamp(timestamp: str) -> str:
    """Formats the ISO 8601 timestamp into a more readable format and converts it to CST."""
    cst_time = parser.parse(timestamp).astimezone(gettz("America/Chicago"))
    return cst_time.strftime("%Y-%m-%d %H:%M CST")


def lookup_by_city(
    locations_by_city: Dict[str, Dict[str, str]], city: str
) -> Optional[Dict[int, str]]:
    """Looks up location details by city name and returns a dictionary mapping ID to city."""
    location_info = locations_by_city.get(city.lower())
    return (
        {int(location_info["id"]): location_info["city"]}
        if location_info
        else f"No location found for city: {city}"
    )


def main() -> NoReturn:
    """Main function to run the scanner"""

    locations_by_city = fetch_locations()
    logger.info("Fetching available locations...")
    logger.info("Available cities: %s", ', '.join(sorted(locations_by_city.keys())).title())

    cities = input("Enter cities of interest (comma-separated): ").split(",")
    location_details = {
        int(locations_by_city[city.strip().lower()]["id"]): city.strip()
        for city in cities
        if city.strip().lower() in locations_by_city
    }

    logger.info("Location Details : %s", location_details)
    if not location_details:
        logger.error("No locations found!")
        sys.exit(-1)
    logger.info("⏰ Checking for appointments...")

    while True:
        errors = [
            process_appointments(loc_id, city)
            for loc_id, city in location_details.items()
        ]
        logger.info(
            "⏰ Waiting for %s seconds before next check...",
            ERROR_INTERVAL if any(errors) else CHECK_INTERVAL,
        )
        time.sleep(ERROR_INTERVAL if any(errors) else CHECK_INTERVAL)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("🛑 Exiting...")
        sys.exit(0)
