import streamlit as st
import google.generativeai as genai # Corrected import
import re
import base64
import random
import json
import os

# ✅ Gemini API configuration
genai.configure(api_key="AIzaSyArTiUlURnBw_Zy41hzJtPg4pKoN4obTdw")
model = genai.GenerativeModel("gemini-2.0-flash") # Corrected GenerativeModel typo

# ✅ Streamlit config
st.set_page_config(layout="wide")

# Define the file path for flashcard storage
FLASHCARDS_FILE = "flashcards.json"

# Function to load flashcards from a JSON file
def load_flashcards():
    if os.path.exists(FLASHCARDS_FILE):
        with open(FLASHCARDS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# Function to save flashcards to a JSON file
def save_flashcards(flashcards):
    # Corrected the typo: FLASHCARCS_FILE -> FLASHCARDS_FILE
    with open(FLASHCARDS_FILE, "w", encoding="utf-8") as f:
        json.dump(flashcards, f, indent=4)

# ---------- Inject Dark Velvet Blush Theme CSS (More Aggressive & Refined) ----------
SUBTLE_PATTERN_SVG = """
<svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
    <pattern id="lines" x="0" y="0" width="10" height="10" patternUnits="userSpaceOnUse">
        <path d="M-1 1 l2 -2 M0 10 l10 -10 M9 11 l2 -2" stroke="#FFFFFF" stroke-width="0.2" opacity="0.1"/>
    </pattern>
    <rect width="100%" height="100%" fill="url(#lines)" />
</svg>
"""
ENCODED_PATTERN = base64.b64encode(SUBTLE_PATTERN_SVG.encode()).decode()
BACKGROUND_IMAGE_CSS = f"url(\"data:image/svg+xml;base64,{ENCODED_PATTERN}\")"

st.markdown(
    f"""
    <style>
    /* Define new primary accent color variables */
    :root {{
        --primary-accent-color: #DA70D6; /* Orchid - a strong but pleasant pink/purple for general theme */
        --accent-main-highlight: #E063B2; /* Muted Fuchsia - for primary highlights like borders and foreign text */
        --secondary-accent-color: #B22222; /* Firebrick - for danger/remove buttons */
        --text-color-light: #F0F0F0; /* Almost white for main text and headers */
        --text-color-medium: #C0C0C0; /* For T.S. responses, explanations */
        --text-color-dark: #A0A0A0;  /* For labels or less prominent text, placeholders */
        --background-dark: #121212 !important; /* Even Deeper Charcoal */
        --background-medium: #2A2A2A; /* Dark Grey for inputs/containers */
        --background-light: #222222; /* Slightly lighter for expanders */
        --divider-color: #4A4A4A; /* Darker, clearer divider line */
    }}

    /* ---------- Base Layout ---------- */
    body, .stApp {{
        background-color: var(--background-dark) !important;
        opacity: 1; /* Ensure overall opacity is 1 */
        color: var(--text-color-light) !important; /* General app text color */
    }}
    /* Apply pattern with very low opacity specifically for the pattern effect across the whole app */
    body::before, .stApp::before {{
        content: "";
        position: fixed; /* Use fixed to cover entire viewport consistently */
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: {BACKGROUND_IMAGE_CSS};
        background-repeat: repeat;
        background-size: 10px 10px;
        opacity: 0.03; /* Very low opacity for subtle effect */
        pointer-events: none; /* Allow interaction with elements below */
        z-index: -1; /* Place it behind content */
    }}

    /* Vertical Separator */
    .stSidebar {{
        border-right: none !important;
    }}

    /* MAIN CONTENT AREA BACKGROUND - Corrected lines */
    [data-testid="stAppViewBlock"] {{
        background-color: var(--background-dark) !important;
        background-image: none !important;
    }}

    .css-1dp5vir {{
        background-color: var(--background-dark) !important;
        background-image: none !important;
        border-left: 1px solid var(--divider-color) !important;
        padding-left: 20px !important;
    }}

    main {{
        background-color: var(--background-dark) !important;
        background-image: none !important;
    }}

    .block-container {{
        background-color: var(--background-dark) !important;
        background-image: none !important;
    }}

    /* ---------- Input fields ---------- */
    input, textarea, .stTextInput > div > div > input, .stTextArea > div > div > textarea {{
        background-color: var(--background-medium) !important;
        color: var(--text-color-light) !important;
        border: 1px solid var(--accent-main-highlight) !important;
        border-radius: 6px !important;
        padding: 0.5rem !important;
    }}
    /* Placeholder text color and style */
    input::placeholder, textarea::placeholder {{
        color: var(--text-color-dark) !important;
        font-style: italic !important;
    }}

    /* ---------- Buttons ---------- */
    button[kind="primary"] {{
        background-color: var(--primary-accent-color) !important;
        color: var(--background-dark) !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        padding: 0.6rem 1.2rem !important;
    }}

    button[kind="primary"]:hover {{
        background-color: #E28AD2 !important;
    }}

    /* General Streamlit buttons (like remove flashcard) */
    button[data-testid*="stButton"] {{
        background-color: var(--secondary-accent-color) !important;
        color: var(--text-color-light) !important;
        border: none !important;
        border-radius: 5px !important;
        padding: 0.3rem 0.8rem !important;
        font-size: 0.8em !important;
        margin-top: 10px !important;
    }}
    button[data-testid*="stButton"]:hover {{
        background-color: #DC143C !important;
    }}
    /* Override for the primary 'Send Chat' button if it gets caught by the above */
    form button[data-testid*="stFormSubmitButton"] {{
        background-color: var(--primary-accent-color) !important;
        color: var(--background-dark) !important;
        padding: 0.6rem 1.2rem !important;
    }}
    

    /* ---------- Section Dividers ---------- */
    hr {{
        border: none;
        height: 1px;
        background: var(--divider-color) !important;
        margin: 20px 0 !important;
    }}

    /* ---------- Headings (Main Content Area) ---------- */
    h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{
        color: var(--text-color-light) !important;
        font-family: "Times New Roman", serif !important;
    }}
    h1 {{ font-size: 2.5em !important; }}
    h2 {{ font-size: 2em !important; }}
    h3 {{ font-size: 1.75em !important; }}


    /* ---------- Sidebar ---------- */
    .css-1d391kg, .stSidebar > div:first-child {{
        font-family: system-ui, sans-serif !important;
        color: var(--text-color-light) !important;
        display: flex;
        flex-direction: column;
        height: 100vh;
        background-color: var(--background-dark) !important;
    }}
    
    /* TheeStallion Chat Header */
    .theestallion-chat-header {{
        font-family: "Times New Roman", serif !important;
        font-weight: bold !important;
        color: var(--primary-accent-color) !important;
        font-size: 1.5em !important;
        margin-top: 10px !important;
        margin-bottom: 20px !important;
        text-align: center;
        width: 100%;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}
    .stSidebar .stMarkdown p.theestallion-chat-header {{
        font-size: 1.5em !important;
    }}


    /* Chat History Container (Scrollable) */
    .chat-history-container {{
        flex-grow: 1;
        overflow-y: auto;
        padding-right: 10px;
        padding-top: 10px;
        padding-bottom: 10px;
        scrollbar-width: thin;
        scrollbar-color: var(--primary-accent-color) var(--background-medium);
    }}
    .chat-history-container::-webkit-scrollbar {{
        width: 8px;
    }}
    .chat-history-container::-webkit-scrollbar-track {{
        background: var(--background-medium);
        border-radius: 10px;
    }}
    .chat-history-container::-webkit-scrollbar-thumb {{
        background: var(--primary-accent-color);
        border-radius: 10px;
    }}
    .chat-history-container::-webkit-scrollbar-thumb:hover {{
        background: #E28AD2;
    }}

    /* Chat Input Section (sticky to bottom) */
    .chat-input-sticky {{
        position: sticky;
        bottom: 0;
        background-color: var(--background-dark) !important;
        padding: 10px 0 !important;
        border-top: 1px solid var(--divider-color) !important;
        z-index: 10;
        margin-top: auto;
    }}

    /* Adjust Streamlit form padding to be more compact for chat input */
    .stForm {{
        padding: 0 !important;
        border: none !important;
    }}
    .stForm > div {{
        margin-bottom: 0 !important;
    }}

    /* Chat History Text Colors */
    .chat-user-text {{
        color: var(--text-color-light) !important;
        margin-bottom: 0.5em;
    }}
    .chat-ts-text {{
        color: var(--text-color-medium) !important;
        margin-bottom: 0.5em !important;
    }}
    .chat-ts-text strong {{
        color: inherit !important;
    }}

    /* Labels for input fields */
    .stTextInput label, .stRadio label {{
        color: var(--text-color-light) !important;
        font-weight: normal !important;
    }}

    /* Ensure specific markdown elements within chat history get proper styling */
    .chat-user-text strong, .chat-ts-text strong {{
        color: inherit !important;
    }}

    /* ---------- Main content font - ensuring Times New Roman ---------- */
    .stMarkdown p, .stText, .stMarkdown ul, .stMarkdown ol, .stMarkdown li,
    .stExpander p, .stExpander li,
    div[data-testid="stMarkdownContainer"] p, .stSidebar .stMarkdown {{
        font-family: "Times New Roman", serif !important;
        font-size: 16px !important;
        line-height: 1.6 !important;
        color: var(--text-color-light) !important;
    }}

    .translation-section-header {{
        font-weight: bold !important;
        color: var(--text-color-light) !important;
        margin-top: 1em !important;
        margin-bottom: 0.5em !important;
        font-size: 1.1em !important;
    }}

    .foreign-word-bold {{
        font-weight: bold !important;
        color: var(--accent-main-highlight) !important;
    }}

    .explanation-content {{
        font-size: 15px !important;
        font-style: italic !important;
        color: var(--text-color-medium) !important;
    }}

    .streamlit-expanderHeader {{
        color: var(--primary-accent-color) !important;
        font-weight: bold !important;
        font-family: "Times New Roman", serif !important;
        background-color: var(--background-light) !important;
        border: 1px solid var(--divider-color) !important;
        border-radius: 6px !important;
        padding: 0.5rem 1rem !important;
        cursor: pointer !important;
    }}

    .stExpander {{
        background-color: var(--background-light) !important;
        border: 1px solid var(--divider-color) !important;
        border-radius: 6px !important;
        margin-top: 10px !important;
        margin-bottom: 10px !important;
    }}

    /* Adjust Streamlit radio buttons for better visibility */
    .stRadio > label {{
        color: var(--text-color-light) !important;
    }}
    .stRadio div[data-testid="stRadio"] label {{
        color: var(--text-color-light) !important;
    }}
    .stRadio div[data-testid="stRadio"] input[type="radio"]:checked + div {{
        background-color: var(--primary-accent-color) !important;
        border-color: var(--primary-accent-color) !important;
    }}
    .stRadio div[data-testid="stRadio"] input[type="radio"] + div {{
        border-color: var(--divider-color) !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------- Title ----------
st.markdown("<h1 style='font-family: Times New Roman, serif; font-weight: bold;' title='Your personal language hype-woman.'>Translator Baddie 💅</h1>", unsafe_allow_html=True)

# ---------------------- Sidebar Chat ---------------------
st.sidebar.markdown("<p class='theestallion-chat-header'>💬 Chat with TheeStallion</p>", unsafe_allow_html=True)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "chat_lang" not in st.session_state:
    st.session_state.chat_lang = ""

if "chat_vibe" not in st.session_state:
    st.session_state.chat_vibe = "" # Default empty for custom input

# Define generate_chat_response function
def generate_chat_response(history, lang, message, vibe):
    # Default tone if user leaves vibe input empty
    tone_instruction = "Adopt a neutral tone, suitable for both formal and informal speaking."
    if vibe:
        tone_instruction = f"Adopt a {vibe} tone. Ensure your language, word choice, and overall style reflect this tone."

    prompt = (
        f"You are an AI assistant designed for chat in {lang}. {tone_instruction}\n"
        f"After your main response (in {lang} with pronunciation), provide an English translation on a new line prefixed with 'Translation: '.\n"
        f"Then, on another new line, provide a breakdown of the translation choices prefixed with 'Breakdown:'. List items with bullet points.\n\n"
        f"User: {message}\nT.S.:"
    )
    
    full_prompt_with_history = ""
    # Only include the last few turns to manage prompt length
    for turn in history[-5:]:
        full_prompt_with_history += f"User: {turn['user']}\nT.S.: {turn['ai']}\n"
    full_prompt_with_history += prompt

    response = model.generate_content(full_prompt_with_history)
    return response.text

# --- Sidebar Content ---
with st.sidebar:
    # Language input
    st.text_input("Language for Chat (e.g., Japanese, Thai):", value=st.session_state.chat_lang, key="chat_lang_input", on_change=lambda: st.session_state.update(chat_lang=st.session_state.chat_lang_input.strip()))
    
    # Custom Vibe/Tone input
    st.text_input(
        "TheeStallion's Vibe (e.g., Sassy, Formal, Playful):",
        value=st.session_state.chat_vibe,
        key="chat_vibe_input",
        on_change=lambda: st.session_state.update(chat_vibe=st.session_state.chat_vibe_input.strip())
    )

    # Chat History Container (scrollable)
    st.markdown('<div class="chat-history-container">', unsafe_allow_html=True)
    for i, turn in enumerate(st.session_state.chat_history):
        st.markdown(f"<p class='chat-user-text'>You: {turn['user']}</p>", unsafe_allow_html=True)
        
        ai_response_text = turn['ai']
        
        # Regex to find main response, translation, and breakdown sections
        main_response_match = re.match(r"(.*?)(?:Translation:|$)", ai_response_text, re.DOTALL | re.IGNORECASE)
        main_ai_response_content = main_response_match.group(1).strip() if main_response_match else ai_response_text.strip()
        
        translation_match = re.search(r"Translation:\s*(.*?)(?=(?:Breakdown:|$))", ai_response_text, re.DOTALL | re.IGNORECASE)
        breakdown_match = re.search(r"Breakdown:\s*(.*)", ai_response_text, re.DOTALL | re.IGNORECASE)

        translation_section = translation_match.group(1).strip() if translation_match else ""
        explanation_section = breakdown_match.group(1).strip() if breakdown_match else ""

        # Display the main T.S. response with new style
        st.markdown(f"<p class='chat-ts-text'>T.S.: {main_ai_response_content}</p>", unsafe_allow_html=True)

        # Display English Translation explicitly
        if translation_section:
            st.markdown(f"<p class='chat-ts-text'>English Translation: {translation_section}</p>", unsafe_allow_html=True)

        # Display Breakdown/Explanation in an expander
        if explanation_section:
            with st.expander("Explanation of choices:"):
                st.markdown(explanation_section)
    st.markdown('</div>', unsafe_allow_html=True) # Close chat history container

    # Chat Input Section (sticky to bottom)
    st.markdown('<div class="chat-input-sticky">', unsafe_allow_html=True)
    
    # Use a form for the chat input and send button
    with st.form(key="chat_form", clear_on_submit=True):
        st.markdown("<p style='margin-bottom: 0.5rem; color: var(--text-color-light); font-weight: normal; font-size: 14px;'>Say something:</p>", unsafe_allow_html=True)
        chat_message_input = st.text_input(
            "",
            key="chat_message_input_form_key_unique",
            placeholder="Type your message here...",
            label_visibility="collapsed"
        )
        send_button = st.form_submit_button("Send Chat", help="Send your message to TheeStallion.", use_container_width=True)

        if send_button:
            if chat_message_input and st.session_state.chat_lang:
                with st.spinner("T.S. is typing..."):
                    try:
                        response = generate_chat_response(
                            st.session_state.chat_history,
                            st.session_state.chat_lang,
                            chat_message_input,
                            st.session_state.chat_vibe
                        )
                        st.session_state.chat_history.append({"user": chat_message_input, "ai": response})
                    except Exception as e:
                        st.sidebar.error(f"Chat error: {e}")
                st.rerun()
            elif not st.session_state.chat_lang:
                st.sidebar.warning("Please specify a language for chat.")
            else:
                st.sidebar.warning("Please type a message to send.")
            
    st.markdown('</div>', unsafe_allow_html=True) # Close sticky input div

# ---------------------- Translator Input ---------------------
st.markdown("## 📖 TranslATE & lEARN")

word = st.text_input("Enter a word or phrase in English:")
target_language = st.text_input("Translate to (language):")

def get_translation_prompt(word, lang):
    return (
        f"Translate the English word or phrase '{word}' into {lang}.\n"
        f"Provide the translation and details in the following structured format. "
        f"If a section is not applicable or you have no specific information, state 'N/A' or similar.\n\n"
        f"---START_TRANSLATION_OUTPUT---\n"
        f"**FORMAL:**\n"
        f"<Foreign Formal Word/Phrase> (pronunciation) - English meaning\n"
        f"\n"
        f"**INFORMAL:**\n"
        f"<Foreign Informal Word/Phrase> (pronunciation) - English meaning\n"
        f"\n"
        f"**SLANG_CONVERSATION_USE:**\n"
        f"- <Foreign Slang 1> (pronunciation) - Explanation/Use Case\n"
        f"- <Foreign Slang 2> (pronunciation) - Explanation/Use Case (if any, otherwise N/A)\n"
        f"\n"
        f"**EXAMPLE_SENTENCE:**\n"
        f"<Foreign Example Sentence> (pronunciation)\n"
        f"English Translation: <English Translation of Sentence>\n"
        f"\n"
        f"**EXPLANATION:**\n"
        f"<Detailed explanation about contexts, nuances, usage tips. If not much to add, keep it concise or state N/A.>\n"
        f"---END_TRANSLATION_OUTPUT---"
    )

# Initialize flashcards by loading them or setting to empty list
if "flashcards" not in st.session_state:
    st.session_state.flashcards = load_flashcards()

if "current_translation" not in st.session_state:
    st.session_state.current_translation = ""

if "current_word" not in st.session_state:
    st.session_state.current_word = ""

if "current_lang" not in st.session_state:
    st.session_state.current_lang = ""


if st.button("Translate", help="Get your translation and breakdown."):
    if word and target_language:
        with st.spinner("Translating..."):
            try:
                prompt = get_translation_prompt(word, target_language)
                response = model.generate_content(prompt).text
                st.session_state.current_translation = response
                st.session_state.current_word = word
                st.session_state.current_lang = target_language
            except Exception as e:
                st.error("Translation failed.")
                st.code(str(e))
    else:
        st.warning("Please enter both a word and a target language.")

# ---------------------- Helper function to format translation text ---------------------
def format_translation_output(raw_text, lang_for_tts=None, prefix_key=""):
    match = re.search(r"---START_TRANSLATION_OUTPUT---\n(.*?)---END_TRANSLATION_OUTPUT---", raw_text, re.DOTALL)
    
    content_to_parse = raw_text

    if match:
        content_to_parse = match.group(1).strip()
    else:
        # Only show this warning if it's the main translation output, not for flashcard labels
        if not prefix_key: 
            st.warning("AI response format markers (---START/END_TRANSLATION_OUTPUT---) not found. Attempting to parse general structure. Please ensure AI follows the prompt strictly.")

    parsed_data = {}

    formal_pattern = r"\*\*(?:FORMAL|FORMAL TRANSLATION):\*\*\s*\n*(.*?)(?=\*\*INFORMAL|\*\*SLANG_CONVERSATION_USE|\*\*EXAMPLE_SENTENCE|\*\*EXPLANATION|$)"
    informal_pattern = r"\*\*(?:INFORMAL|INFORMAL TRANSLATION):\*\*\s*\n*(.*?)(?=\*\*SLANG_CONVERSATION_USE|\*\*EXAMPLE_SENTENCE|\*\*EXPLANATION|$)"
    slang_pattern = r"\*\*(?:SLANG_CONVERSATION_USE|EVERYDAY_SLANGS_OR_CASUAL_VARIATIONS|EVERYDAY_SLANGS):\*\*\s*\n*(.*?)(?=\*\*EXAMPLE_SENTENCE|\*\*EXPLANATION|$)"
    example_pattern = r"\*\*(?:EXAMPLE_SENTENCE):\*\*\s*\n*(.*?)(?=\*\*EXPLANATION|$)"
    explanation_pattern = r"\*\*(?:EXPLANATION|EXPLANATION_OF_CHOICES):\*\*\s*\n*(.*)"

    parsed_data['FORMAL'] = re.search(formal_pattern, content_to_parse, re.DOTALL | re.IGNORECASE)
    parsed_data['INFORMAL'] = re.search(informal_pattern, content_to_parse, re.DOTALL | re.IGNORECASE)
    parsed_data['SLANG_CONVERSATION_USE'] = re.search(slang_pattern, content_to_parse, re.DOTALL | re.IGNORECASE)
    parsed_data['EXAMPLE_SENTENCE'] = re.search(example_pattern, content_to_parse, re.DOTALL | re.IGNORECASE)
    parsed_data['EXPLANATION'] = re.search(explanation_pattern, content_to_parse, re.DOTALL | re.IGNORECASE)

    for key in parsed_data:
        if parsed_data[key]:
            parsed_data[key] = parsed_data[key].group(1).strip()
        else:
            parsed_data[key] = ""

    explanation_content = parsed_data.get('EXPLANATION', '').strip()
    
    def render_line_with_bold(st_obj, line_content, section_name_prefix=None, key_suffix=""):
        clean_content = line_content
        if section_name_prefix:
            pattern = r"^\s*" + re.escape(section_name_prefix) + r"(?:\s*TRANSLATION)?\s*:\s*\**"
            clean_content = re.sub(pattern, '', clean_content, flags=re.IGNORECASE).strip()

        clean_content = re.sub(r"^\*\*", "", clean_content).strip()
        clean_content = re.sub(r"\*\*$", "", clean_content).strip()

        display_html = ""

        if clean_content.startswith('- '):
            content_after_bullet = clean_content[2:].strip()
            match_foreign = re.match(r"([^-(]+(?:\([^)]*\))?)(.*)", content_after_bullet)
            if match_foreign:
                foreign_part = match_foreign.group(1).strip()
                rest_of_line = match_foreign.group(2).strip()
                display_html = f"- <span class='foreign-word-bold'>{foreign_part}</span> {rest_of_line}"
            else:
                display_html = f"- <span class='foreign-word-bold'>{content_after_bullet}</span>"
        else:
            match_foreign = re.match(r"([^-(]+(?:\([^)]*\))?)(.*)", clean_content)
            if match_foreign:
                foreign_part = match_foreign.group(1).strip()
                rest_of_line = match_foreign.group(2).strip()
                display_html = f"<span class='foreign-word-bold'>{foreign_part}</span> {rest_of_line}"
            else:
                display_html = f"{clean_content}"
        
        st_obj.markdown(f"<p style='display:inline-block; margin-right: 10px;'>{display_html}</p>", unsafe_allow_html=True)
        
    
    # Use st.markdown directly to render headers and content
    formal_text = parsed_data.get('FORMAL', '').strip()
    if formal_text and formal_text.lower() not in ['n/a', '']:
        st.markdown(f"<p class='translation-section-header'>Formal Translation:</p>", unsafe_allow_html=True)
        render_line_with_bold(st, formal_text, 'FORMAL', key_suffix=f"{prefix_key}formal")
    else:
        st.markdown(f"<p class='translation-section-header'>Formal Translation:</p><p>N/A</p>", unsafe_allow_html=True)

    informal_text = parsed_data.get('INFORMAL', '').strip()
    if informal_text and informal_text.lower() not in ['n/a', '']:
        st.markdown(f"<p class='translation-section-header'>Informal Translation:</p>", unsafe_allow_html=True)
        render_line_with_bold(st, informal_text, 'INFORMAL', key_suffix=f"{prefix_key}informal")
    else:
        st.markdown(f"<p class='translation-section-header'>Informal Translation:</p><p>N/A</p>", unsafe_allow_html=True)

    slang_text = parsed_data.get('SLANG_CONVERSATION_USE', '').strip()
    if slang_text and slang_text.lower() not in ['n/a', '']:
        st.markdown(f"<p class='translation-section-header'>Slang/Conversation Use:</p>", unsafe_allow_html=True)
        slang_entries = slang_text.split('\n')
        for i, entry in enumerate(slang_entries):
            entry = entry.strip()
            if entry:
                render_line_with_bold(st, entry, key_suffix=f"{prefix_key}slang{i}")
    else:
        st.markdown(f"<p class='translation-section-header'>Slang/Conversation Use:</p><p>N/A</p>", unsafe_allow_html=True)

    example_text = parsed_data.get('EXAMPLE_SENTENCE', '').strip()
    if example_text and example_text.lower() not in ['n/a', '']:
        st.markdown(f"<p class='translation-section-header'>Example Sentence:</p>", unsafe_allow_html=True)
        
        lines = example_text.split('\n')
        foreign_sentence = ""
        english_translation = ""

        for line in lines:
            if line.strip().lower().startswith("english translation:"):
                english_translation = line.strip()
            else:
                if not foreign_sentence:
                    foreign_sentence = line.strip()

        if foreign_sentence:
            render_line_with_bold(st, foreign_sentence, key_suffix=f"{prefix_key}example_foreign")
        if english_translation:
            st.markdown(f"<p>{english_translation}</p>", unsafe_allow_html=True)
        else:
            st.markdown(f"<p><em>English Translation: N/A (could not parse)</em></p>", unsafe_allow_html=True)
    else:
        st.markdown(f"<p class='translation-section-header'>Example Sentence:</p><p>N/A</p>", unsafe_allow_html=True)

    return explanation_content


# ---------------------- Show English-to-Foreign Translation Result Section ---------------------
if st.session_state.current_translation:
    with st.expander("✨ Translation & Example", expanded=True): # Expand by default for new translations
        explanation_text = format_translation_output(
            st.session_state.current_translation,
            lang_for_tts=st.session_state.current_lang,
            prefix_key="current_trans_" 
        )

        if explanation_text and explanation_text.lower() not in ['n/a', '', 'nan']:
            with st.expander("Explanation (Click to expand)"):
                st.markdown(f"<div class='explanation-content'>{explanation_text}</div>", unsafe_allow_html=True)

        if st.button("❤️ Save flashcard", help="Add this translation to your flashcards for review."):
            existing = any(
                fc["word"].lower() == st.session_state.current_word.lower()
                and fc["language"].lower() == st.session_state.current_lang.lower()
                for fc in st.session_state.flashcards
            )
            if not existing:
                st.session_state.flashcards.append({
                    "word": st.session_state.current_word,
                    "language": st.session_state.current_lang,
                    "translation_raw": st.session_state.current_translation
                })
                save_flashcards(st.session_state.flashcards) # Save after adding
                st.success("Flashcard saved!")
            else:
                st.info("Flashcard already saved.")

# ---------------------- Reverse Translation Section ---------------------
st.markdown("---")
st.markdown("## 🔄 Reverse Translate & Understand") #

foreign_word = st.text_input("Enter a word or phrase in the foreign language:") #
original_language_reverse = st.text_input("Original language of the word (e.g., Japanese, Thai):") #

if "current_reverse_translation" not in st.session_state:
    st.session_state.current_reverse_translation = ""
if "current_foreign_word" not in st.session_state:
    st.session_state.current_foreign_word = ""
if "current_original_lang_reverse" not in st.session_state:
    st.session_state.current_original_lang_reverse = ""


def get_reverse_translation_prompt(foreign_word, original_lang):
    return (
        f"Analyze the {original_lang} word or phrase '{foreign_word}'.\n"
        f"Provide its English meaning, formal/informal English equivalents, example sentences in English, "
        f"and an explanation of its nuances in the original language.\n"
        f"Use the following structured format. If a section is not applicable or you have no specific information, state 'N/A' or similar.\n\n"
        f"---START_REVERSE_TRANSLATION_OUTPUT---\n"
        f"**ENGLISH_MEANING:**\n"
        f"<Direct English meaning(s) of the word/phrase>\n"
        f"\n"
        f"**FORMAL_EQUIVALENT_ENGLISH:**\n"
        f"<Formal English equivalent(s)>\n"
        f"\n"
        f"**INFORMAL_EQUIVALENT_ENGLISH:**\n"
        f"<Informal English equivalent(s)>\n"
        f"\n"
        f"**EXAMPLE_SENTENCE_ENGLISH:**\n"
        f"<English Example Sentence 1>\n"
        f"<English Example Sentence 2> (if applicable)\n"
        f"\n"
        f"**NUANCES_AND_USAGE:**\n"
        f"<Detailed explanation about contexts, cultural nuances, common usage, grammar tips for the original word. If not much to add, keep it concise or state N/A.>\n"
        f"---END_REVERSE_TRANSLATION_OUTPUT---"
    )

def format_reverse_translation_output(raw_text, lang_for_tts=None, prefix_key=""):
    match = re.search(r"---START_REVERSE_TRANSLATION_OUTPUT---\n(.*?)---END_REVERSE_TRANSLATION_OUTPUT---", raw_text, re.DOTALL)
    
    content_to_parse = raw_text

    if match:
        content_to_parse = match.group(1).strip()
    else:
        st.warning("AI response format markers (---START/END_REVERSE_TRANSLATION_OUTPUT---) not found. Attempting to parse general structure. Please ensure AI follows the prompt strictly.")

    parsed_data = {}

    meaning_pattern = r"\*\*(?:ENGLISH_MEANING):\*\*\s*\n*(.*?)(?=\*\*FORMAL_EQUIVALENT_ENGLISH|\*\*INFORMAL_EQUIVALENT_ENGLISH|\*\*EXAMPLE_SENTENCE_ENGLISH|\*\*NUANCES_AND_USAGE|$)"
    formal_eq_pattern = r"\*\*(?:FORMAL_EQUIVALENT_ENGLISH):\*\*\s*\n*(.*?)(?=\*\*INFORMAL_EQUIVALENT_ENGLISH|\*\*EXAMPLE_SENTENCE_ENGLISH|\*\*NUANCES_AND_USAGE|$)"
    informal_eq_pattern = r"\*\*(?:INFORMAL_EQUIVALENT_ENGLISH):\*\*\s*\n*(.*?)(?=\*\*EXAMPLE_SENTENCE_ENGLISH|\*\*NUANCES_AND_USAGE|$)"
    example_eng_pattern = r"\*\*(?:EXAMPLE_SENTENCE_ENGLISH):\*\*\s*\n*(.*?)(?=\*\*NUANCES_AND_USAGE|$)"
    nuances_pattern = r"\*\*(?:NUANCES_AND_USAGE):\*\*\s*\n*(.*)"

    parsed_data['ENGLISH_MEANING'] = re.search(meaning_pattern, content_to_parse, re.DOTALL | re.IGNORECASE)
    parsed_data['FORMAL_EQUIVALENT_ENGLISH'] = re.search(formal_eq_pattern, content_to_parse, re.DOTALL | re.IGNORECASE)
    parsed_data['INFORMAL_EQUIVALENT_ENGLISH'] = re.search(informal_eq_pattern, content_to_parse, re.DOTALL | re.IGNORECASE)
    parsed_data['EXAMPLE_SENTENCE_ENGLISH'] = re.search(example_eng_pattern, content_to_parse, re.DOTALL | re.IGNORECASE)
    parsed_data['NUANCES_AND_USAGE'] = re.search(nuances_pattern, content_to_parse, re.DOTALL | re.IGNORECASE)

    for key in parsed_data:
        if parsed_data[key]:
            parsed_data[key] = parsed_data[key].group(1).strip()
        else:
            parsed_data[key] = ""

    nuances_content = parsed_data.get('NUANCES_AND_USAGE', '').strip()

    def render_text_without_tts_button(st_obj, text_content, lang_code, key_prefix):
        st_obj.markdown(f"<p style='display:inline-block; margin-right: 10px;'>{text_content}</p>", unsafe_allow_html=True)
    
    # Display the original foreign word for reverse translation
    if st.session_state.current_foreign_word:
        st.markdown(f"<p class='translation-section-header'>Original Foreign Word/Phrase:</p>", unsafe_allow_html=True)
        render_text_without_tts_button(st, st.session_state.current_foreign_word, st.session_state.current_original_lang_reverse, key_prefix="reverse_foreign_word")
    
    meaning_text = parsed_data.get('ENGLISH_MEANING', '').strip()
    if meaning_text and meaning_text.lower() not in ['n/a', '']:
        st.markdown(f"<p class='translation-section-header'>English Meaning:</p>", unsafe_allow_html=True)
        st.markdown(f"<p>{meaning_text}</p>", unsafe_allow_html=True)
    else:
        st.markdown(f"<p class='translation-section-header'>English Meaning:</p><p>N/A</p>", unsafe_allow_html=True)

    formal_eq_text = parsed_data.get('FORMAL_EQUIVALENT_ENGLISH', '').strip()
    if formal_eq_text and formal_eq_text.lower() not in ['n/a', '']:
        st.markdown(f"<p class='translation-section-header'>Formal English Equivalent:</p>", unsafe_allow_html=True)
        st.markdown(f"<p>{formal_eq_text}</p>", unsafe_allow_html=True)
    else:
        st.markdown(f"<p class='translation-section-header'>Formal English Equivalent:</p><p>N/A</p>", unsafe_allow_html=True)

    informal_eq_text = parsed_data.get('INFORMAL_EQUIVALENT_ENGLISH', '').strip()
    if informal_eq_text and informal_eq_text.lower() not in ['n/a', '']:
        st.markdown(f"<p class='translation-section-header'>Informal English Equivalent:</p>", unsafe_allow_html=True)
        st.markdown(f"<p>{informal_eq_text}</p>", unsafe_allow_html=True)
    else:
        st.markdown(f"<p class='translation-section-header'>Informal English Equivalent:</p><p>N/A</p>", unsafe_allow_html=True)

    example_eng_text = parsed_data.get('EXAMPLE_SENTENCE_ENGLISH', '').strip()
    if example_eng_text and example_eng_text.lower() not in ['n/a', '']:
        st.markdown(f"<p class='translation-section-header'>English Example Sentences:</p><ul>", unsafe_allow_html=True)
        example_entries = example_eng_text.split('\n')
        for i, entry in enumerate(example_entries):
            entry = entry.strip()
            if entry:
                st.markdown(f"<li>{entry}</li>", unsafe_allow_html=True)
        st.markdown("</ul>", unsafe_allow_html=True)
    else:
        st.markdown(f"<p class='translation-section-header'>English Example Sentences:</p><p>N/A</p>", unsafe_allow_html=True)

    return nuances_content


if st.button("Reverse Translate", key="reverse_translate_button", help="Understand a foreign word in English."):
    if foreign_word and original_language_reverse:
        with st.spinner("Understanding..."):
            try:
                prompt = get_reverse_translation_prompt(foreign_word, original_language_reverse)
                response = model.generate_content(prompt).text
                st.session_state.current_reverse_translation = response
                st.session_state.current_foreign_word = foreign_word
                st.session_state.current_original_lang_reverse = original_language_reverse
            except Exception as e:
                st.error("Reverse translation failed.")
                st.code(str(e))
    else:
        st.warning("Please enter both the foreign word and its original language.")

if st.session_state.current_reverse_translation:
    with st.expander("📚 Understanding the Word", expanded=True): # Expand by default
        nuances_text = format_reverse_translation_output(
            st.session_state.current_reverse_translation,
            lang_for_tts=st.session_state.current_original_lang_reverse,
            prefix_key="reverse_trans_" 
        )

        if nuances_text and nuances_text.lower() not in ['n/a', '', 'nan']:
            with st.expander("Nuances & Usage (Click to expand)"):
                st.markdown(f"<div class='explanation-content'>{nuances_text}</div>", unsafe_allow_html=True)


# ---------------------- Flashcard Review Session ---------------------
st.markdown("---")
st.markdown("## 🧠 Flashcard Review Session")

if "review_cards" not in st.session_state:
    st.session_state.review_cards = []
if "current_review_card_idx" not in st.session_state:
    st.session_state.current_review_card_idx = -1
if "show_review_answer" not in st.session_state:
    st.session_state.show_review_answer = False
# Initialize score
if "score" not in st.session_state:
    st.session_state.score = 0

def start_review():
    if not st.session_state.flashcards:
        st.warning("You need to save some flashcards first!")
        return
    st.session_state.review_cards = random.sample(st.session_state.flashcards, len(st.session_state.flashcards))
    st.session_state.current_review_card_idx = 0
    st.session_state.show_review_answer = False
    # Reset score when a new review session starts
    st.session_state.score = 0 

def next_review_card(correctly_answered=False):
    if correctly_answered:
        st.session_state.score += 1
    
    st.session_state.current_review_card_idx += 1
    if st.session_state.current_review_card_idx >= len(st.session_state.review_cards):
        st.info(f"You've reviewed all cards in this session! Your final score is: {st.session_state.score}")
        st.session_state.current_review_card_idx = -1 # End review session
    st.session_state.show_review_answer = False
    st.rerun()

def reset_score():
    st.session_state.score = 0
    st.success("Score reset!")
    st.rerun() # Rerun to update the display immediately

# Display current score
st.markdown(f"### Current Score: {st.session_state.score}")

col_review_buttons = st.columns(2)
with col_review_buttons[0]:
    if st.button("Start Review Session", key="start_review_button", help="Begin a new flashcard review session."):
        start_review()
        st.rerun()
with col_review_buttons[1]:
    st.button("Reset Score", key="reset_score_button", on_click=reset_score, help="Reset your current review session score.")


if st.session_state.current_review_card_idx != -1 and st.session_state.review_cards:
    current_card = st.session_state.review_cards[st.session_state.current_review_card_idx]

    st.markdown(f"### Card {st.session_state.current_review_card_idx + 1} of {len(st.session_state.review_cards)}")
    
    st.markdown(f"<p class='translation-section-header'>English Word:</p>", unsafe_allow_html=True)
    st.markdown(f"<h2>{current_card['word']}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: var(--text-color-medium); font-style: italic;'>({current_card['language']})</p>", unsafe_allow_html=True)

    if not st.session_state.show_review_answer:
        st.button("Show Answer", key="show_answer_button", on_click=lambda: st.session_state.update(show_review_answer=True))
    else:
        st.markdown("<p class='translation-section-header'>Translation & Details:</p>", unsafe_allow_html=True)
        explanation = format_translation_output(
            current_card['translation_raw'], 
            lang_for_tts=current_card['language'], 
            prefix_key=f"review_card_{st.session_state.current_review_card_idx}_" 
        )

        if explanation and explanation.lower() not in ['n/a', '', 'nan']:
            with st.expander("Explanation (Click to expand)"):
                st.markdown(f"<div class='explanation-content'>{explanation}</div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.button("✅ Got it Right!", key="next_right", on_click=lambda: next_review_card(True), use_container_width=True, help="Award 1 point and move to the next card.")
        with col2:
            st.button("🤔 Needs Practice", key="next_wrong", on_click=lambda: next_review_card(False), use_container_width=True, help="No points, move to the next card.")

# ---------------------- List All Flashcards (Original Section) ---------------------
st.markdown("---")
st.markdown("## 📚 All Your Saved Flashcards")

with st.expander("Click to view/manage your saved flashcards"):
    if not st.session_state.flashcards:
        st.info("No flashcards saved yet. Use the 'Translate' section to save some!")

    for idx, card in enumerate(st.session_state.flashcards):
        raw_translation_content = card.get("translation_raw", "")
        
        # We need to re-parse the raw content to get the first line for the expander label
        temp_match = re.search(r"\*\*(?:FORMAL|FORMAL TRANSLATION):\*\*\s*\n*([^\n]+)", raw_translation_content, re.IGNORECASE)
        first_line_for_label = ""
        if temp_match:
            first_line_for_label = temp_match.group(1).strip()
        
        if not first_line_for_label:
            lines = raw_translation_content.split('\n')
            for line in lines:
                if line.strip() and not line.strip().startswith('**'):
                    first_line_for_label = line.strip()
                    break

        if len(first_line_for_label) > 60:
            first_line_for_label = first_line_for_label[:57] + "..."

        expander_label = f"🔹 Word/Phrase: {card['word']} : {first_line_for_label} [{card['language']}]"

        col_expander, col_button = st.columns([0.8, 0.2])

        with col_expander:
            with st.expander(expander_label, expanded=False):
                flashcard_explanation = format_translation_output(
                    card["translation_raw"],
                    lang_for_tts=card['language'],
                    prefix_key=f"flashcard_list_{idx}_" 
                )

                if flashcard_explanation and flashcard_explanation.lower() not in ['n/a', '', 'nan']:
                    with st.expander("Explanation (Click to expand)"):
                        st.markdown(f"<div class='explanation-content'>{flashcard_explanation}</div>", unsafe_allow_html=True)

        with col_button:
            remove_key = f"remove_{idx}"
            st.markdown("<div style='height: 2.5em;'></div>", unsafe_allow_html=True)
            if st.button("🗑️ Remove", key=remove_key, help="Remove this flashcard."):
                st.session_state.flashcards = [fc for i, fc in enumerate(st.session_state.flashcards) if i != idx]
                save_flashcards(st.session_state.flashcards) # Save after removing
                st.rerun()