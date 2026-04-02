from datetime import datetime, timedelta
import zoneinfo
from pytexbot.schedule_data import CONFERENCE_DATA

def get_next_session():
    # PyTexas is in Dallas (Central Time)
    # Use ZoneInfo for reliable timezone handling
    try:
        tz = zoneinfo.ZoneInfo("America/Chicago")
    except Exception:
        # Fallback if zoneinfo is not properly set up on Windows
        # Central Time is usually UTC-6 (Standard) or UTC-5 (Daylight)
        # For simplicity in this script, we'll try to use local time if aligned
        # but the ideal is ZoneInfo.
        tz = None

    now = datetime.now(tz)
    
    # Format for matching
    today_str = now.strftime("%Y-%m-%d")
    current_time_str = now.strftime("%H:%M")

    if today_str not in CONFERENCE_DATA:
        # Check if conference is in the future
        first_day = sorted(CONFERENCE_DATA.keys())[0]
        if today_str < first_day:
            return None, f"The conference hasn't started yet! First session is on {first_day}."
        return None, "There are no sessions scheduled for today!"

    todays_talks = CONFERENCE_DATA[today_str]
    sorted_times = sorted(todays_talks.keys())

    for start_time in sorted_times:
        if start_time > current_time_str:
            return todays_talks[start_time], start_time

    return None, "All sessions for today have concluded. See you tomorrow!"
