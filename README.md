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
pip install -r requirements.txt
```

## Setup
- (Optional) Twilio Account: The script uses Twilio to send SMS notifications. You need to create a Twilio account and get your account_sid and auth_token. You also need a Twilio phone number to send SMS messages.
- API Endpoint: The script is configured to fetch data from a specific API endpoint. Make sure the endpoint is correct and operational.

## Configuration Variables
- `APPOINTMENTS_API_URL`: URL for the API endpoint.
- `CHECK_INTERVAL`: Time interval (in seconds) between checks when no errors occur.
- `ERROR_INTERVAL`: Time interval (in seconds) between checks when an error occurs.

## Running the Script
To run the script, simply execute it from the command line:

```bash
python3 appointment_scanner.py
```

The script will continuously check for new appointments and print updates to the console. If a new appointment is found, it will send an SMS notification.

## SMS and Email Notifications
To enable SMS notifications, add following credentials in `.env` file:
- `account_sid` (Twilio account SID)
- `auth_token` (Twilio account auth token)
- `to_number` (recipient phone number)
- `from_number` (Twilio phone number)

To enable email notifications, add following credentials in `.env` file:
- `to_email` (recipient email address)
- `from_` (sender email address)
- `password` (sender email password)

## Thank you to the following open source projects for inspiration:
- https://gist.github.com/serg06/ac46defe2d9f568ac39665bd50d2e1b1
- https://gist.github.com/clay584/bcbbe3803ca6414ce09426a2c3d4abfb
