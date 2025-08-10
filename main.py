import os
import requests
import json
import google.generativeai as genai
from datetime import datetime
import pytz # We will need to add this to requirements.txt
from dotenv import load_dotenv

# Load environment variables from .env file (for local testing)
load_dotenv()

# --- Configuration from Environment Variables ---
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAMBOTTOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAMCHATID')
GEMINI_API_KEY = os.getenv('GEMINIAPIKEY')

if not all([TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, GEMINI_API_KEY]):
    print("Error: Missing one or more environment variables. Please check your GitHub Secrets.")
    # In a real bot, you might want to send a message to admin or log this.
    exit(1) # Exit if essential variables are missing

# Configure Gemini API with the specified endpoint.
genai.configure(api_key=GEMINI_API_KEY, client_options={"api_endpoint": "generativelanguage.googleapis.com"})

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

# --- Gemini Content Generation (for blogs only) ---
# Using the model specified in our previous discussions.
# Note: 'gemini-2.5-flash' is not a standard publicly documented model as of my last update.
# If this causes a 'model not found' or 'permission denied' error after these changes,
# it would indicate that this specific model is not available for your API key/project.
model = genai.GenerativeModel('gemini-2.5-flash')

def generate_blog_with_gemini(prompt):
    try:
        # Set a timeout for the API call to prevent indefinite waiting.
        # A 60-second timeout should be sufficient for most generative AI responses.
        response = model.generate_content(prompt, request_options={'timeout': 60})

        # Check for candidates and text in the response
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            # Join all parts to form the full text
            full_text = "".join(part.text for part in response.candidates[0].content.parts)
            if full_text:
                return full_text
            else:
                return "Sorry, I couldn't generate that content. Empty text response from AI."
        else:
            # This handles cases where response is not None but has no valid content
            return "Sorry, I couldn't generate that content. Invalid response structure from AI."

    except Exception as e:
        error_message = f"Sorry, I couldn't generate the blog content right now. Error: {e}"
        # Send the error to Telegram immediately if it's a critical AI failure
        send_telegram_message(TELEGRAM_CHAT_ID, f"**Gemini Blog Error:**\n{error_message}")
        return None

# --- Hardcoded Time-based Greeting Logic ---
def get_time_based_greeting_message(utc_hour):
    # This logic assumes GitHub Actions runs are in UTC
    if 5 <= utc_hour < 12: # Morning (e.g., 5 AM to 11:59 AM UTC)
        return "Good morning, tech enthusiasts! Rise and shine, it's a brand new day filled with endless possibilities in the world of code, innovation, and digital marvels. May your coffee be strong and your bugs be few!"
    elif 12 <= utc_hour < 17: # Afternoon (e.g., 12 PM to 4:59 PM UTC)
        return "Greetings, afternoon tech warriors! As the day progresses, let's keep that innovation spirit burning bright. Whether you're debugging, designing, or deploying, may your afternoon be productive and your breakthroughs impactful!"
    elif 17 <= utc_hour < 23: # Evening (e.g., 5 PM to 10:59 PM UTC)
        return "Good evening, fellow innovators! As the day winds down, take a moment to reflect on the amazing strides you've made. Perhaps a quiet evening of learning, or connecting with the global tech community awaits. Sweet dreams of efficient algorithms!"
    elif 23 <= utc_hour or utc_hour < 5: # Night (e.g., 11 PM to 4:59 AM UTC)
        return "Good night, digital dreamers! The stars are out, and it's time to rest your minds from the circuits and screens. Recharge those brain cells for another day of pushing technological boundaries. May your sleep be peaceful and your tech ideas brilliant!"
    else:
        return None # No greeting for times not covered (e.g., if there's a tiny gap, or if you prefer no message)

# --- Main Bot Logic ---
def run_bot():
    now_utc = datetime.now(pytz.utc)
    utc_hour = now_utc.hour

    # 1. Send Time-Based Greeting (hardcoded)
    greeting_message = get_time_based_greeting_message(utc_hour)
    if greeting_message:
        send_telegram_message(TELEGRAM_CHAT_ID, greeting_message)
        # Add a small delay if sending multiple messages rapidly to avoid API rate limits
        # import time # Uncomment this line and the one below
        # time.sleep(2)

    # 2. Send Funny Tech Blog (uses Gemini API)
    blog_prompt = "Generate a short, funny, and engaging blog post (around 150-250 words) about a random technology category. Make it light-hearted and humorous. Examples: the struggles of debugging, AI mishaps, quantum computing for dummies, the internet of things gone wrong, tech memes explained. Include a catchy title and keep paragraphs short."
    blog_content = generate_blog_with_gemini(blog_prompt)
    if blog_content:
        send_telegram_message(TELEGRAM_CHAT_ID, f"**Tech Tidbit:**\n\n{blog_content}")

if __name__ == "__main__":
    run_bot()
