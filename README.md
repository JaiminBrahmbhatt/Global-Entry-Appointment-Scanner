# Global-Entry-Appointment-Scanner

## Overview
This Python script automatically checks for available appointments at specified locations and notifies the user when new appointments are available for global entry / NEXUS locations. 

The script fetches appointment data from an API, processes the data to find new available slots, and sends notifications to the user. It is set up to check for appointments every 15 minutes, but this interval can be adjusted as needed.

## Build Status
[![Pylint](https://github.com/JaiminBrahmbhatt/Global-Entry-Appointment-Scanner/actions/workflows/pylint.yml/badge.svg)](https://github.com/JaiminBrahmbhatt/Global-Entry-Appointment-Scanner/actions/workflows/pylint.yml)

[![CodeQL](https://github.com/JaiminBrahmbhatt/Global-Entry-Appointment-Scanner/actions/workflows/codeql.yml/badge.svg)](https://github.com/JaiminBrahmbhatt/Global-Entry-Appointment-Scanner/actions/workflows/codeql.yml)



## Prerequisites
Before running the script, ensure you have the following installed:
- Python 3.6 or higher

You can install the required Python libraries using pip:
```bash
pip install requirements.txt
```

## Setup
- Twilio Account: The script uses Twilio to send SMS notifications. You need to create a Twilio account and get your account_sid and auth_token. You also need a Twilio phone number to send SMS messages.
- API Endpoint: The script is configured to fetch data from a specific API endpoint. Make sure the endpoint is correct and operational.
- Configuration: Update the LOCATION_DETAILS dictionary in the script to include the location IDs and names for which you want to check appointments.

## Configuration Variables
- `API_URL_TEMPLATE`: URL template for the API endpoint.
- `LOCATION_DETAILS`: Dictionary mapping location IDs to their names.
- `CHECK_INTERVAL`: Time interval (in seconds) between checks when no errors occur.
- `ERROR_INTERVAL`: Time interval (in seconds) between checks when an error occurs.

## Running the Script
To run the script, simply execute it from the command line:

```bash
python appointment_scanner.py
```

The script will continuously check for new appointments and print updates to the console. If a new appointment is found, it will send an SMS notification.

## Notification
To enable SMS notifications, uncomment the Twilio client creation and message sending lines in the notify function, and fill in the necessary Twilio information:
- `account_sid`
- `auth_token`
- to (recipient phone number)
- from_ (Twilio phone number)

##  Thank you to these two amazing folks for the inspiration
- https://gist.github.com/serg06/ac46defe2d9f568ac39665bd50d2e1b1
- https://gist.github.com/clay584/bcbbe3803ca6414ce09426a2c3d4abfb
