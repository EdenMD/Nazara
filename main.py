import os
import requests
import json
from datetime import datetime
import pytz
import random
from dotenv import load_dotenv

# Load environment variables from .env file (for local testing)
load_dotenv()

# --- Configuration from Environment Variables ---
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAMBOTTOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAMCHATID')

if not all([TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID]):
    print("Error: Missing one or more environment variables. Please check your GitHub Secrets.")
    exit(1) # Exit if essential variables are missing

# --- Telegram API Helper ---
def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'Markdown' # Allows for bold, italics, etc.
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
        print(f"Telegram message sent: {text[:50]}...")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error sending Telegram message: {e}")
        # Print the full response content for debugging
        if 'response' in locals() and response.text:
            print(f"Telegram API Response: {response.text}")
        return False

# --- Manual Greeting Messages ---
def get_time_based_greeting_message(utc_hour):
    # Using different messages for variety
    morning_greetings = [
        "Good Morning, tech explorers! Rise and shine, it's a new day to build and innovate!",
        "Mornin' geeks! Time to debug your sleep and compile some productivity. Have a great one!",
        "Top of the morning! May your code be bug-free and your coffee strong today.",
        "Wake up, world-changers! The servers of opportunity are online. Good Morning!",
        "Hello, bright minds! Hope your day is as organized as a well-commented codebase. Good Morning!"
    ]
    afternoon_greetings = [
        "Good Afternoon, everyone! Hope your projects are compiling nicely and your algorithms are efficient.",
        "Midday greetings! Just a friendly reminder to take a break from your screens and recharge.",
        "Afternoon, tech fam! Keep those innovation engines running! Only a few more hours till day's end.",
        "Happy afternoon coding! May your debug sessions be short and your breakthroughs many.",
        "Greetings from the digital realm! Enjoy your afternoon."
    ]
    evening_greetings = [
        "Good Evening! Time to wind down and reflect on a day of digital adventures. What did you learn today?",
        "Evening, team! Hope your sprints were successful and your systems stable. Enjoy your night!",
        "As the day winds down, may your tech dreams be filled with clean code and new ideas. Good evening!",
        "Unplug and unwind. Wishing you a peaceful evening after a day of tech triumphs. Good Evening!",
        "The day's code is committed, now it's time to relax. Good Evening, everyone!"
    ]
    night_greetings = [
        "Good Night, fellow coders! Rest well, and may your dreams be of perfectly optimized solutions.",
        "Sweet dreams to all the tech minds out there! Recharge for another day of innovation.",
        "Time to power down! Wishing you a peaceful night and a fresh start tomorrow.",
        "Sending sleepy bytes your way. Good Night, and happy dreaming of future tech!",
        "The network is quiet. Time for some offline processing. Good Night!"
    ]

    if 5 <= utc_hour < 12: # Morning (e.g., 5 AM to 11:59 AM UTC)
        return random.choice(morning_greetings)
    elif 12 <= utc_hour < 17: # Afternoon (e.g., 12 PM to 4:59 PM UTC)
        return random.choice(afternoon_greetings)
    elif 17 <= utc_hour < 23: # Evening (e.g., 5 PM to 10:59 PM UTC)
        return random.choice(evening_greetings)
    elif 23 <= utc_hour or utc_hour < 5: # Night (e.g., 11 PM to 4:59 AM UTC)
        return random.choice(night_greetings)
    else:
        return None

def get_holiday_greeting(today):
    holidays = {
        (1, 1): "Happy New Year! Wishing you a year of exciting tech breakthroughs and successful projects!",
        (2, 14): "Happy Valentine's Day! Sending love and good vibes to all our tech community!",
        (3, 17): "Happy St. Patrick's Day! May your code be green and your bugs be few!",
        (4, 1): "Happy April Fools' Day! Don't let your code play any tricks on you today!",
        (5, 1): "Happy May Day! Celebrating the spirit of innovation and collaboration in tech!",
        (7, 4): "Happy Independence Day! May your freedoms be as strong as your Wi-Fi signal! (For US)",
        (9, 5): "Happy Labor Day! Taking a break from the grind to appreciate all tech workers! (Example - adjust for your region)",
        (10, 31): "Happy Halloween! May your night be spooky and your data secure!",
        (11, 11): "Happy Veterans Day! Honoring those who served, building a better future through tech! (For US)",
        (12, 25): "Merry Christmas! May your holidays be filled with joy, and your gadgets fully charged!",
        (12, 31): "Happy New Year's Eve! Reflect on a year of tech advancements and get ready for more!"
        # Add more holidays as (month, day): "Greeting Message"
        # e.g., (1, 26): "Happy Australia Day! (For AU)"
        # e.g., (8, 15): "Happy Independence Day! (For India)"
    }

    # Check for date-specific holidays
    if (today.month, today.day) in holidays:
        return holidays[(today.month, today.day)]
    
    # Add logic for holidays that might span multiple days or are calculated (e.g., Easter, Thanksgiving)
    # For example, to check for Thanksgiving (4th Thursday in November) for US:
    # if today.month == 11 and today.weekday() == 3 and 22 <= today.day <= 28:
    #     return "Happy Thanksgiving! Grateful for all the amazing tech and community!"

    return None

# --- Main Bot Logic ---
def run_bot():
    now_utc = datetime.now(pytz.utc)
    utc_hour = now_utc.hour
    today_utc = now_utc.date()

    # 1. Check for Holiday Greeting First
    holiday_greeting = get_holiday_greeting(today_utc)
    if holiday_greeting:
        send_telegram_message(TELEGRAM_CHAT_ID, holiday_greeting)
    else:
        # 2. Send Time-Based Greeting if no holiday
        greeting_message = get_time_based_greeting_message(utc_hour)
        if greeting_message:
            send_telegram_message(TELEGRAM_CHAT_ID, greeting_message)

if __name__ == "__main__":
    run_bot()
