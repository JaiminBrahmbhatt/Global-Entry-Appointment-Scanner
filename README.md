# Global-Entry-Appointment-Scanner

## Overview
This Python script automatically checks for available appointments at specified locations and notifies the user when new appointments are available for global entry / NEXUS locations. 

The script fetches appointment data from an API, processes the data to find new available slots, and sends notifications to the user. It is set up to check for appointments every 15 minutes, but this interval can be adjusted as needed.

## Prerequisites
Before running the script, ensure you have the following installed:
- Python 3.6 or higher
- `requests` library
- `python-dateutil` library

You can install the required Python libraries using pip:
```bash
pip install requests python-dateutil
