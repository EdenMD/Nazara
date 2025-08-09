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
# The user provided https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent
# The base endpoint for `v1beta` is generativelanguage.googleapis.com
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

# --- Gemini Content Generation ---
# Use the exact model name provided by the user in their endpoint URL
# Note: 'gemini-2.5-flash' is not a standard publicly documented model as of my last update.
# If this causes a 'model not found' or 'permission denied' error after these changes,
# it would indicate that this specific model is not available for your API key/project.
model = genai.GenerativeModel('gemini-2.5-flash')

def generate_content_with_gemini(prompt, is_greeting=False):
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
        error_message = f"Sorry, I couldn't generate that content right now. Error: {e}"
        # Send the error to Telegram immediately if it's a critical AI failure
        # This helps in real-time debugging for scheduled runs
        send_telegram_message(TELEGRAM_CHAT_ID, f"**Gemini API Error:**\n{error_message}")
        return None

# --- Time-based Greeting Logic ---
def get_time_based_greeting_prompt(utc_hour):
    # This logic assumes GitHub Actions runs are in UTC
    if 5 <= utc_hour < 12: # Morning (e.g., 5 AM to 11:59 AM UTC)
        return "Generate a warm and positive 'Good Morning' message (max 200 characters) for a tech community, mentioning something exciting about the day or technology. Keep it concise."
    elif 12 <= utc_hour < 17: # Afternoon (e.g., 12 PM to 4:59 PM UTC)
        return "Generate an energetic and positive 'Good Afternoon' message (max 200 characters) for a tech community, maybe a quick tech fact or a mid-day thought. Keep it concise."
    elif 17 <= utc_hour < 23: # Evening (e.g., 5 PM to 10:59 PM UTC)
        return "Generate a relaxing and insightful 'Good Evening' message (max 200 characters) for a tech community, perhaps encouraging winding down or reflecting on tech trends. Keep it concise."
    else: # Late night/early morning, don't send a greeting
        return None

# --- Main Bot Logic ---
def run_bot():
    now_utc = datetime.now(pytz.utc)
    utc_hour = now_utc.hour

    # 1. Send Time-Based Greeting if applicable
    greeting_prompt = get_time_based_greeting_prompt(utc_hour)
    if greeting_prompt:
        greeting = generate_content_with_gemini(greeting_prompt, is_greeting=True)
        if greeting:
            send_telegram_message(TELEGRAM_CHAT_ID, greeting)
            # Add a small delay if sending multiple messages rapidly to avoid API rate limits
            # import time # Uncomment this line and the one below
            # time.sleep(2)

    # 2. Send Funny Tech Blog
    blog_prompt = "Generate a short, funny, and engaging blog post (around 150-250 words) about a random technology category. Make it light-hearted and humorous. Examples: the struggles of debugging, AI mishaps, quantum computing for dummies, the internet of things gone wrong, tech memes explained. Include a catchy title and keep paragraphs short."
    blog_content = generate_content_with_gemini(blog_prompt)
    if blog_content:
        send_telegram_message(TELEGRAM_CHAT_ID, f"**Tech Tidbit:**\n\n{blog_content}")

if __name__ == "__main__":
    run_bot()
