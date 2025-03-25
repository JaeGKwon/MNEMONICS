import streamlit as st
import openai
import requests
from bs4 import BeautifulSoup
import re
import json
import os
import pandas as pd

# Set page config
st.set_page_config(
    page_title="Historical Event Mnemonics",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load OpenAI API key from secrets
openai.api_key = st.secrets.get("openai_api_key", "")

# Custom CSS for better styling
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
    # Add more as needed...
}

# Function: Get event description from Wikipedia
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

# Function: Generate mnemonic
def generate_mnemonic(event, year, api_key):
    if not api_key:
        return "Please enter an OpenAI API key to generate mnemonics.", "", ""
    description, wiki_link = get_event_info(event)
    year_str = str(year)[1:]
    mnemonic_letters = ' '.join(digit_to_letter[d] for d in year_str)
    prompt = (
        f"Create a memorable mnemonic phrase for high school students about the historical event '{event}' that occurred in {year}.\n\n"
        f"The mnemonic should use the letters {mnemonic_letters} (which come from the year {year} without the first digit).\n\n"
        f"Each letter should start a word in the mnemonic phrase. Relate the phrase to what happened: {description}"
    )
    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a creative educational assistant who creates memorable mnemonics for high school students."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150
        )
        mnemonic = response.choices[0].message.content.strip()
        return mnemonic, description, wiki_link
    except Exception as e:
        return f"Error generating mnemonic: {str(e)}", "", ""

# === UI Starts ===

st.title("🏛️ Historical Event Mnemonics Generator")
st.markdown("### Learn history dates with memorable mnemonics!")

# Sidebar
with st.sidebar:
    st.header("How It Works")
    st.markdown("""
    This app creates mnemonics to help remember historical dates:
    
    1. Select a year from history  
    2. Choose or enter an event  
    3. Get a mnemonic based on letter codes from the date

    **Digit → Letter Mapping:**

    - 0 = O, 1 = A, 2 = T, 3 = E, 4 = F  
    - 5 = S, 6 = G, 7 = L, 8 = B, 9 = P  
    """)

# Input Section
with st.container():
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])

    with col1:
        years = sorted(historical_events_db.keys(), reverse=True)
        selected_year = st.selectbox("Select a Year:", years)
        event_options = historical_events_db[selected_year]
        input_type = st.radio("Event Input:", ["Select from database", "Enter my own event"])
        selected_event = st.text_input("Enter the historical event:") if input_type == "Enter my own event" else st.selectbox("Select an Event:", event_options)

    with col2:
        col_btn1, _ = st.columns([2, 1])
        with col_btn1:
            generate_button = st.button("Generate Mnemonic", use_container_width=True)

        if generate_button:
            if not openai.api_key:
                st.error("API key not found in secrets.")
            elif not selected_event.strip():
                st.error("Please enter or select an event.")
            else:
                with st.spinner("Generating mnemonic..."):
                    mnemonic, desc, link = generate_mnemonic(selected_event, selected_year, openai.api_key)
                    st.session_state.mnemonic = mnemonic
                    st.session_state.description = desc
                    st.session_state.wiki_link = link
                    st.session_state.event = selected_event
                    st.session_state.year = selected_year
    st.markdown('</div>', unsafe_allow_html=True)

# Divider
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# Output Section
with st.container():
    st.markdown('<div class="output-section">', unsafe_allow_html=True)
    st.markdown("## 📋 Results")
    st.markdown("---")

    if 'mnemonic' in st.session_state:
        st.header(f"{st.session_state.event} ({st.session_state.year})")
        year_str = str(st.session_state.year)[1:]
        letters = [digit_to_letter[d] for d in year_str]
        conversion_df = pd.DataFrame({"Digit": list(year_str), "Letter": letters})
        
        st.markdown("### Year Digits to Letters:")
        st.dataframe(conversion_df, hide_index=True, use_container_width=False)

        st.markdown("### Your Mnemonic:")
        st.markdown(f"""
        <div style="padding: 15px; border-radius: 5px; background-color: #e8f4f8; border-left: 5px solid #4CAF50;">
            <h4 style="margin-top: 0;">Mnemonic Phrase:</h4>
            <p>{st.session_state.mnemonic}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### Event Description:")
        st.markdown(f"""
        <div style="padding: 15px; border-radius: 5px; background-color: #f5f5f5; border: 1px solid #ddd;">
            {st.session_state.description}
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <a href="{st.session_state.wiki_link}" target="_blank" style="text-decoration: none;">
            <div style="padding: 10px; text-align: center; background-color: #4169E1; color: white; border-radius: 5px; margin-top: 15px;">
                Learn more about this event on Wikipedia
            </div>
        </a>
        """, unsafe_allow_html=True)

    else:
        st.info("Select a year and event, then click 'Generate Mnemonic' to see results here.")
        st.image("https://via.placeholder.com/600x300.png?text=Historical+Event+Mnemonics", caption="Select an event to generate a mnemonic")
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("*Built to make history fun and memorable for students!*")
