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
openai.api_key = st.secrets.get("OPENAI_API_KEY", "")
#openai.api_key = st.secrets["OPENAI_API_KEY"]

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-family: 'Georgia', serif;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 900px;
        margin: auto;
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
    1607: ["Jamestown Colony established"],
    1619: ["First enslaved Africans arrive in Virginia"],
    1620: ["Mayflower Compact", "Plymouth Colony founded"],
    1754: ["French and Indian War begins"],
    1765: ["Stamp Act"],
    1770: ["Boston Massacre"],
    1772: ["Gaspee Affair"],
    1773: ["Boston Tea Party"],
    1775: ["Battles of Lexington and Concord", "Second Continental Congress"],
    1776: ["Declaration of Independence"],
    1781: ["Articles of Confederation ratified", "Battle of Yorktown"],
    1783: ["Treaty of Paris ends Revolutionary War"],
    1787: ["Constitutional Convention"],
    1789: ["George Washington becomes president", "French Revolution begins"],
    1791: ["Bill of Rights ratified"],
    1803: ["Louisiana Purchase"],
    1812: ["War of 1812 begins"],
    1815: ["Battle of New Orleans"],
    1823: ["Monroe Doctrine"],
    1846: ["Mexican-American War begins"],
    1848: ["Gold discovered in California"],
    1854: ["Kansas-Nebraska Act"],
    1861: ["American Civil War begins"],
    1863: ["Emancipation Proclamation", "Battle of Gettysburg"],
    1865: ["Civil War ends", "Lincoln assassinated"],
    1869: ["Transcontinental Railroad completed"],
    1876: ["Battle of Little Bighorn"],
    1886: ["Statue of Liberty dedicated"],
    1898: ["Spanish-American War"],
    1903: ["Wright Brothers' first flight"],
    1912: ["Titanic sinks"],
    1914: ["World War I begins"],
    1917: ["US enters World War I"],
    1918: ["World War I ends"],
    1920: ["Women's suffrage (19th Amendment)"],
    1929: ["Stock Market Crash", "Great Depression begins"],
    1933: ["New Deal begins"],
    1939: ["World War II begins"],
    1941: ["Pearl Harbor", "US enters World War II"],
    1945: ["World War II ends", "United Nations founded", "Atomic bombs dropped"],
    1947: ["Cold War begins", "Jackie Robinson breaks MLB color barrier"],
    1950: ["Korean War begins"],
    1954: ["Brown v. Board of Education"],
    1955: ["Rosa Parks and Montgomery Bus Boycott"],
    1957: ["Sputnik launch"],
    1961: ["Berlin Wall built", "First human in space"],
    1962: ["Cuban Missile Crisis"],
    1963: ["JFK assassination", "March on Washington"],
    1964: ["Civil Rights Act", "Gulf of Tonkin Resolution"],
    1965: ["Voting Rights Act", "Medicare established"],
    1968: ["MLK & RFK assassinations", "Tet Offensive"],
    1969: ["Moon Landing", "Woodstock Festival", "Stonewall Riots"],
    1972: ["Watergate Scandal begins"],
    1973: ["Roe v. Wade", "U.S. withdraws from Vietnam"],
    1974: ["Nixon resigns"],
    1979: ["Three Mile Island accident", "Iran Hostage Crisis"],
    1981: ["AIDS epidemic recognized", "Reagan becomes president"],
    1986: ["Challenger disaster", "Iran-Contra affair"],
    1989: ["Berlin Wall falls", "Tiananmen Square protests"],
    1990: ["World Wide Web invented"],
    1991: ["Soviet Union dissolves", "Gulf War"],
    2001: ["9/11 terrorist attacks"],
    2003: ["Iraq War begins"],
    2008: ["Global financial crisis", "Obama elected president"],
    2010: ["Affordable Care Act (Obamacare)"],
    2011: ["Osama bin Laden killed"],
    2016: ["Brexit referendum", "Trump elected president"],
    2020: ["COVID-19 pandemic", "George Floyd protests"],
    2021: ["January 6 Capitol riot", "Biden becomes president"],
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
        mnemonic = response.choices[0].message.content.strip()
        return mnemonic, description, wiki_link
    except Exception as e:
        return f"Error: {str(e)}", "", ""

# === App UI ===
with st.container():
    st.markdown("## 🏛️ Historical Event Mnemonics Generator", unsafe_allow_html=True)

# Sidebar instructions
with st.sidebar:
    st.header("How It Works")
    st.markdown("""
    1. Choose a year  
    2. Select or enter a historical event  
    3. Get a mnemonic using letter mapping from the year  

    **Digit → Letter Mapping:**

    - 0 = O, 1 = A, 2 = T, 3 = E, 4 = F  
    - 5 = S, 6 = G, 7 = L, 8 = B, 9 = P  
    """)

# Input section
with st.container():
    years = sorted(historical_events_db.keys(), reverse=True)
    selected_year = st.selectbox("Select a Year:", years)

    event_options = historical_events_db[selected_year]
    input_type = st.radio("Event Input:", ["Select from database", "Enter my own event"])

    if input_type == "Enter my own event":
        selected_event = st.text_input("Enter the historical event:")
    else:
        selected_event = st.selectbox("Select an Event:", event_options)

    generate_button = st.button("Generate Mnemonic", use_container_width=True)

    if generate_button:
        if not openai.api_key:
            st.error("API key not found.")
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

# Divider
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# Output section
with st.container():
    st.markdown("## 📋 Results")
    st.markdown("---")

    if 'mnemonic' in st.session_state:
        st.header(f"{st.session_state.event} ({st.session_state.year})")

        year_str = str(st.session_state.year)[1:]
        letters = [digit_to_letter[d] for d in year_str]
        df = pd.DataFrame({"Digit": list(year_str), "Letter": letters})

        st.markdown("### Year Digits to Letters:")
        st.dataframe(df, hide_index=True)

        st.markdown("### Your Mnemonic:")
        st.markdown(f"""
        <div style="padding: 15px; border-radius: 5px; background-color: #e8f4f8; border-left: 5px solid #4CAF50;">
            <strong>Mnemonic Phrase:</strong>
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

# Footer
st.markdown("---")
st.markdown("*This app helps students remember historical events using mnemonics based on dates.*")
