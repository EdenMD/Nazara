import os
import requests
import google.generativeai as genai
import datetime

# --- Configuration from Environment Variables ---
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAMBOTTOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAMCHATID")
GEMINI_API_KEY = os.environ.get("GEMINIAPIKEY")

# --- Gemini API Configuration ---
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

def get_gemini_response(prompt_text):
    """Fetches a text response from the Gemini API."""
    try:
        response = model.generate_content(prompt_text)
        # Access text from parts, as response.text might not always be directly available if multiple parts
        if response.parts:
            return " ".join(part.text for part in response.parts if hasattr(part, 'text'))
        return "Failed to generate content." # Fallback if no text parts
    except Exception as e:
        print(f"Error getting Gemini response: {e}")
        return f"Sorry, I couldn't generate that content right now. Error: {e}"

def send_telegram_message(message):
    """Sends a message to the specified Telegram chat."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown' # Allows for bolding, italics, etc.
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors
        print("Message sent successfully!")
    except requests.exceptions.RequestException as e:
        print(f"Error sending message: {e}")
        print(f"Response content: {e.response.text if e.response else 'No response'}")

def get_time_based_greeting():
    """Generates a greeting based on the current UTC time."""
    current_hour_utc = datetime.datetime.utcnow().hour

    if 5 <= current_hour_utc < 12: # 5 AM to 11:59 AM UTC
        time_of_day = "Morning"
    elif 12 <= current_hour_utc < 18: # 12 PM to 5:59 PM UTC
        time_of_day = "Afternoon"
    elif 18 <= current_hour_utc < 23: # 6 PM to 10:59 PM UTC
        time_of_day = "Evening"
    else: # 11 PM to 4:59 AM UTC (or any other time we might run it)
        # If it's a late-night run, we might just send a blog, or a general greeting.
        # For simplicity, let's say we only generate specific greetings during prime times.
        return None # No specific time-based greeting for other hours, just blog
    
    greeting_prompt = (
        f"Generate a very short, cheerful, and creative 'Good {time_of_day}' message, "
        "specifically for a Telegram bot that sends daily tech updates. "
        "Make it concise, inviting, and include a positive, tech-related touch. Avoid emojis." # Added tech-related touch
    )
    return get_gemini_response(greeting_prompt)

def get_tech_blog():
    """Generates a funny, technology-focused blog post."""
    blog_prompt = (
        "Generate a short, engaging, and funny blog post (around 150-200 words) "
        "about a random, interesting, and often humorous aspect of technology. "
        "The topic should be quirky, cutting-edge, or a relatable observation about tech culture. "
        "Make it suitable for a casual audience on Telegram. Focus on a single, specific topic. "
        "Do not include a title. Start directly with the content. Avoid lists or bullet points. "
        "Make sure it's genuinely amusing and light-hearted."
    )
    return get_gemini_response(blog_prompt)


if __name__ == "__main__":
    # Check if essential environment variables are set
    if not all([TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, GEMINI_API_KEY]):
        print("Error: Missing one or more environment variables (TELEGRAMBOTTOKEN, TELEGRAMCHATID, GEMINIAPIKEY).")
        print("Please ensure they are set as GitHub Secrets.")
        exit(1)

    # Attempt to send time-based greeting if applicable
    greeting_message = get_time_based_greeting()
    if greeting_message:
        print(f"Generated Greeting:\n{greeting_message}")
        send_telegram_message(f"_{greeting_message}_") # Italicize greeting

    # Always send a tech blog
    tech_blog_content = get_tech_blog()
    print(f"Generated Tech Blog:\n{tech_blog_content}")
    # Bold the entire blog for better visibility
    send_telegram_message(f"*Tech Tidbit:*{os.linesep}{tech_blog_content}")
