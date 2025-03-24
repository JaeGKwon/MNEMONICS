import openai

# Initialize OpenAI API key
openai.api_key = 'YOUR_OPENAI_API_KEY'

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

def generate_mnemonic(event, year, description):
    """
    Generate a mnemonic for a historical event by removing the first digit of the year.
    
    Parameters:
    - event (str): The name of the historical event.
    - year (int): The year the event occurred.
    - description (str): A brief description of the event.
    
    Returns:
    - str: A mnemonic phrase for the event.
    """
    # Convert year to string and remove the first digit
    year_str = str(year)[1:]
    
    # Convert remaining year digits to mnemonic letters
    mnemonic_letters = ' '.join(digit_to_letter[digit] for digit in year_str)
    
    # Create the prompt
    prompt = (
        f"Event: {event}\n"
        f"Year: {year}\n"
        f"Description: {description}\n"
        f"Digit-to-Letter Mapping: {digit_to_letter}\n"
        f"Mnemonic Letters: {mnemonic_letters}\n\n"
        f"Using the mnemonic letters '{mnemonic_letters}', create a fun and memorable mnemonic phrase for the event '{event}' that occurred in {year}."
    )
    
    # Generate mnemonic using OpenAI API
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a creative assistant who generates mnemonic phrases to help remember historical events and their dates."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=50
    )
    
    mnemonic = response.choices[0].message['content'].strip()
    return mnemonic

# Example list of historical events
historical_events = [
    {
        'event': 'Gaspee Affair',
        'year': 1772,
        'description': 'Colonists burned the British schooner Gaspee, escalating tensions leading up to the American Revolution.'
    },
    {
        'event': 'Declaration of Independence',
        'year': 1776,
        'description': 'The thirteen American colonies declared independence from British rule.'
    },
    {
        'event': 'Moon Landing',
        'year': 1969,
        'description': 'Apollo 11 mission successfully landed the first humans on the Moon.'
    }
    # Add more events as needed
]

# Generate mnemonics for each event
for event_info in historical_events:
    event = event_info['event']
    year = event_info['year']
    description = event_info['description']
    mnemonic = generate_mnemonic(event, year, description)
    print(f"Event: {event} ({year})\nMnemonic: {mnemonic}\n")
