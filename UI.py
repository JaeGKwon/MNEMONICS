import streamlit as st
import openai
import requests
from bs4 import BeautifulSoup
import re
import json
import os

# Set page config
st.set_page_config(
    page_title="Historical Event Mnemonics",
    page_icon="📚",
    layout="wide"
)

# Initialize OpenAI API key (use environment variable in production)
openai.api_key = st.sidebar.text_input("Enter your OpenAI API key:", type="password")

# Digit-to-letter mapping
digit_to_letter = {
    '0': 'O',
    '1': 'A',
    '2': 'T',
    '3': 'E',
    '4': 'F',
    '5': 'S',
    '6': 'G',
    '7': 'L',
    '8': 'B',
    '9': 'P'
}

# Historical events database with years
# This could be expanded or loaded from a file
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

def generate_mnemonic(event, year, api_key):
    """
    Generate a mnemonic for a historical event by using the digits of the year (except first digit).
    
    Parameters:
    - event (str): The name of the historical event.
    - year (int): The year the event occurred.
    - api_key (str): OpenAI API key
    
    Returns:
    - str: A mnemonic phrase for the event.
    """
    if not api_key:
        return "Please enter an OpenAI API key to generate mnemonics."
    
    # Get event description and Wikipedia link
    description, wiki_link = get_event_info(event)
    
    # Convert year to string and remove the first digit
    year_str = str(year)[1:]
    
    # Convert remaining year digits to mnemonic letters
    mnemonic_letters = ' '.join(digit_to_letter[digit] for digit in year_str)
    
    # Create the prompt for the LLM
    prompt = (
        f"Create a memorable mnemonic phrase for high school students about the historical event '{event}' that occurred in {year}.\n\n"
        f"The mnemonic should use the letters {mnemonic_letters} (which come from the year {year} without the first digit).\n\n"
        f"Each letter ({mnemonic_letters}) should be the first letter of a word in the mnemonic phrase.\n\n"
        f"Make the mnemonic phrase engaging, educational, and appropriate for high school students.\n\n"
        f"The phrase should relate to what happened during the event: {description}"
    )
    
    try:
        # Generate mnemonic using OpenAI API (using a more advanced model)
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o",  # Using a more advanced model
            messages=[
                {"role": "system", "content": "You are a creative educational assistant who creates memorable mnemonics for high school students to remember historical events and their dates."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150
        )
        
        mnemonic = response.choices[0].message.content.strip()
        return mnemonic, description, wiki_link
    except Exception as e:
        return f"Error generating mnemonic: {str(e)}", "", ""

def get_event_info(event):
    """
    Get a short description and Wikipedia link for a historical event.
    
    Parameters:
    - event (str): The name of the historical event.
    
    Returns:
    - tuple: (description, wikipedia_link)
    """
    # Clean event name for URL
    event_url = event.replace(" ", "_")
    wiki_link = f"https://en.wikipedia.org/wiki/{event_url}"
    
    # Default description in case we can't fetch one
    default_description = f"The {event} was a significant historical event."
    
    try:
        # Try to get the first paragraph from Wikipedia
        response = requests.get(wiki_link)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try to get the first paragraph that's not a table or infobox
            paragraphs = soup.find_all('p')
            for p in paragraphs:
                if len(p.text.strip()) > 100:  # Skip short paragraphs
                    # Clean up the text
                    description = re.sub(r'\[\d+\]', '', p.text)  # Remove citation numbers
                    description = description.strip()
                    return description[:500] + "..." if len(description) > 500 else description, wiki_link
        
        return default_description, wiki_link
    except:
        return default_description, wiki_link

# Streamlit UI
st.title("🏛️ Historical Event Mnemonics Generator")
st.markdown("### Learn history dates with memorable mnemonics!")

# Sidebar with information
with st.sidebar:
    st.header("How It Works")
    st.markdown("""
    This app creates mnemonics to help remember historical dates:
    
    1. Select a year from history
    2. Choose or enter an event from that year
    3. Get a mnemonic using letters derived from the year digits
    
    **Letter Mapping:**
    - 0 = O
    - 1 = A
    - 2 = T
    - 3 = E
    - 4 = F
    - 5 = S
    - 6 = G
    - 7 = L
    - 8 = B
    - 9 = P
    
    For example, for the year 1776, we use the digits 7-7-6 → L-L-G
    """)

# Main interface
# Add a brief introduction
st.markdown("""
This app helps you create memorable mnemonics for historical events using a special letter coding system.
Simply select a year, enter any historical event, and get a custom mnemonic to help remember the date!
""")

col1, col2 = st.columns([1, 2])

with col1:
    # Year selection
    years = sorted(historical_events_db.keys(), reverse=True)
    selected_year = st.selectbox("Select a Year:", years)
    
    # Event selection based on year with direct input option
    event_options = historical_events_db[selected_year]
    
    # Option to select from database or enter custom
    event_input_type = st.radio(
        "Choose event input method:",
        ["Select from database", "Enter my own event"]
    )
    
    if event_input_type == "Enter my own event":
        selected_event = st.text_input("Enter the historical event:", 
                                      placeholder="e.g., Treaty of Versailles")
    else:
        selected_event = st.selectbox("Select an Event:", event_options, 
                                     help="These are common events from this year")
    
    # Generate button
    if st.button("Generate Mnemonic"):
        if not openai.api_key:
            st.error("Please enter your OpenAI API key in the sidebar.")
        elif not selected_event.strip():
            st.error("Please enter an event name.")
        else:
            with st.spinner("Generating mnemonic..."):
                mnemonic_result, description, wiki_link = generate_mnemonic(selected_event, selected_year, openai.api_key)
                
                # Store the results in session state
                st.session_state.mnemonic = mnemonic_result
                st.session_state.description = description
                st.session_state.wiki_link = wiki_link
                st.session_state.event = selected_event
                st.session_state.year = selected_year

with col2:
    # Display mnemonic and event info
    if 'mnemonic' in st.session_state:
        st.header(f"{st.session_state.event} ({st.session_state.year})")
        
        # Display the year digits and corresponding letters
        year_str = str(st.session_state.year)[1:]  # Remove first digit
        letters = [digit_to_letter[digit] for digit in year_str]
        
        st.markdown("### Year Digits → Letters:")
        digit_cols = st.columns(len(year_str))
        for i, (digit, letter) in enumerate(zip(year_str, letters)):
            with digit_cols[i]:
                st.markdown(f"**{digit} → {letter}**")
        
        st.markdown("### Your Mnemonic:")
        st.success(st.session_state.mnemonic)
        
        st.markdown("### Event Description:")
        st.info(st.session_state.description)
        
        st.markdown(f"[Learn more about this event on Wikipedia]({st.session_state.wiki_link})")
    else:
        st.info("Select a year and event, then click 'Generate Mnemonic' to create a memorable phrase.")
        st.image("https://via.placeholder.com/600x300.png?text=Historical+Event+Mnemonics", 
                 caption="Select an event to generate a mnemonic")

# Footer
st.markdown("---")
st.markdown("*This app helps create mnemonics for historical events using digit-to-letter mapping. Perfect for history students!*")
