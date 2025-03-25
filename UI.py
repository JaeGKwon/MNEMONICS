import streamlit as st
import openai
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

# App config
st.set_page_config(
    page_title="Historical Event Mnemonics",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load OpenAI API key from Streamlit secrets
openai.api_key = st.secrets.get("openai_api_key", "")

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-family: 'Georgia', serif;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .input-section, .output-section {
        background-color: #f8f9fa;
        padding: 25px;
        border-radius: 10px;
        border: 1px solid #ccc;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        margin-bottom: 30px;
    }
    .divider {
        margin: 30px 0;
        height: 2px;
        background-color: #dee2e6;
    }
    .stButton>button {
        background-color: #dc3545;
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        transition: 0.2s ease-in-out;
    }
    .stButton>button:hover {
        background-color: #bb2d3b;
    }
</style>
""", unsafe_allow_html=True)

# Digit-to-letter mapping
digit_to_letter = {
    '0': 'O', '1': 'A', '2': 'T', '3': 'E', '4': 'F',
    '5': 'S', '6': 'G', '7': 'L', '8': 'B', '9': 'P'
}

# Historical events database
historical_events_db = {
    1492: ["Columbus reaches the Americas"],
    1776: ["Declaration of Independence"],
    1865: ["Civil War ends", "Lincoln assassinated"],
    1914: ["World War I begins"],
    1945: ["World War II ends", "United Nations founded", "Atomic bombs dropped"],
    1969: ["Moon Landing", "Woodstock Festival", "Stonewall Riots"],
    2001: ["9/11 terrorist attacks"],
    2020: ["COVID-19 pandemic", "George Floyd protests"],
    2022: ["Russia invades Ukraine", "Queen Elizabeth II dies"]
}

# Get event info from Wikipedia
def get_event_info(event):
    event_url = event.replace(" ", "_")
    wiki_link = f"https://en.wikipedia.org/wiki/{event_url}"
    default_description = f"The {event} was a significant historical event."
    try:
        response = requests.get(wiki_link)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            paragraphs = soup.find_all('p')
            for p in paragraphs:
                if len(p.text.strip()) > 100:
                    description = re.sub(r'\[\d+\]', '', p.text).strip()
                    return description[:500] + "..." if len(description) > 500 else description, wiki_link
        return default_description, wiki_link
    except:
        return default_description, wiki_link

# Generate mnemonic
def generate_mnemonic(event, year, api_key):
    if not api_key:
        return "Missing OpenAI API key.", "", ""
    description, wiki_link = get_event_info(event)
    year_str = str(year)[1:]
    mnemonic_letters = ' '.join(digit_to_letter[d] for d in year_str)
    prompt = (
        f"Create a memorable mnemonic phrase for high school students about the historical event '{event}' that occurred in {year}.\n\n"
        f"The mnemonic should use the letters {mnemonic_letters} (from the last 3 digits of the year).\n\n"
        f"Each letter should be the first letter of each word. Make it engaging and educational. Here's the event summary: {description}"
    )
    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a creative educational assistant who creates memorable mnemonics for historical events."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150
        )
        mnemonic = response.choices[
