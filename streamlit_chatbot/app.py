import streamlit as st
import google.generativeai as genai

# ✅ Gemini API configuration
genai.configure(api_key="AIzaSyArTiUlURnBw_Zy41hzJtPg4pKoN4obTdw")  # Replace with your Gemini API key
model = genai.GenerativeModel("gemini-2.0-flash")

# ✅ Streamlit config
st.set_page_config(layout="wide")
st.markdown("<h1 style='font-family: Times New Roman, serif; font-weight: bold;'>Translator Baddie 💅</h1>", unsafe_allow_html=True)

# Add this CSS here, right after page config:
st.markdown(
    """
    <style>
    /* Apply Times New Roman to all main page content */
    div[role="main"] * {
        font-family: "Times New Roman", serif !important;
    }

    /* Keep sidebar font default */
    .css-1d391kg {
        font-family: system-ui, sans-serif !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------- Sidebar Chat ---------------------
st.sidebar.header("💬 Chat with AI")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "chat_lang" not in st.session_state:
    st.session_state.chat_lang = ""

chat_lang = st.sidebar.text_input("Language for Chat (e.g., Japanese, Thai):", value=st.session_state.chat_lang)
st.session_state.chat_lang = chat_lang.strip()

chat_input = st.sidebar.text_input("Say something:")

def generate_chat_response(history, lang, message):
    prompt = (
        f"You're an AI chatting casually in {lang}. Use natural tone and include everyday slang if appropriate.\n"
        f"User: {message}\nAI:"
    )
    response = model.generate_content(prompt)
    return response.text

if chat_input and chat_lang:
    with st.spinner("AI is typing..."):
        try:
            response = generate_chat_response(st.session_state.chat_history, chat_lang, chat_input)
            st.session_state.chat_history.append({"user": chat_input, "ai": response})
        except Exception as e:
            st.sidebar.error(f"Chat error: {e}")

for turn in st.session_state.chat_history:
    st.sidebar.markdown(f"**You:** {turn['user']}")
    st.sidebar.markdown(f"**AI:** {turn['ai']}")

# ---------------------- Translator Input ---------------------
st.markdown("## 📖 TranslATE & lEARN")

word = st.text_input("Enter a word or phrase in English:")
target_language = st.text_input("Translate to (language):")

def get_translation_prompt(word, lang):
    return (
        f"Translate '{word}' into {lang}.\n"
        f"Format the output like this:\n\n"
        f"• Formal Translation:\n<your formal translation here>\n\n"
        f"• Informal Translation:\n<your informal translation here>\n\n"
        f"• Explanation:\nExplain the contexts where formal or informal is used.\n\n"
        f"• Everyday Slangs or Casual Variations:\nList a few slangs or informal variants, each with a short explanation.\n\n"
        f"• Example Sentence:\nGive one sentence using the translated word and provide its English translation."
    )

if "flashcards" not in st.session_state:
    st.session_state.flashcards = []

if "current_translation" not in st.session_state:
    st.session_state.current_translation = ""

if st.button("Translate"):
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
def format_translation_text(text):
    # Split by bullet points "• " and wrap English content in Times New Roman spans
    sections = text.split("• ")
    result = ""

    for section in sections:
        if not section.strip():
            continue
        parts = section.split(":", 1)
        if len(parts) < 2:
            result += section
            continue
        header, content = parts[0].strip(), parts[1].strip()
        # Bold header and break line
        result += f"<b>{header}:</b><br>"
        # Wrap content with Times New Roman, keep line breaks
        content_html = content.replace("\n", "<br>")
        result += f'<span style="font-family: Times New Roman, serif;">{content_html}</span><br><br>'
    return result

# ---------------------- Show Result Section ---------------------
if st.session_state.current_translation:
    st.markdown("## ✨ Translation & Example")

    styled_translation = format_translation_text(st.session_state.current_translation)

    st.markdown(
        f"<div style='font-family: system-ui, sans-serif; font-size: 18px;'>{styled_translation}</div>",
        unsafe_allow_html=True
    )

    if st.button("❤️ Save flashcard"):
        existing = any(
            fc["word"].lower() == st.session_state.current_word.lower()
            and fc["language"].lower() == st.session_state.current_lang.lower()
            for fc in st.session_state.flashcards
        )
        if not existing:
            st.session_state.flashcards.append({
                "word": st.session_state.current_word,
                "language": st.session_state.current_lang,
                "translation": st.session_state.current_translation
            })
            st.success("Flashcard saved!")
        else:
            st.info("Flashcard already saved.")

# ---------------------- Flashcard Review Section ---------------------
st.markdown("---")
st.markdown("## 📚 Review Your Flashcards")

for idx, card in enumerate(st.session_state.flashcards):
    first_line = card["translation"].split('\n')[1] if '\n' in card["translation"] else ""
    first_line = first_line.strip()
    expander_label = f"🔹 Word/Phrase: {card['word']} : {first_line} [{card['language']}]"

    with st.expander(expander_label):
        formatted_text = format_translation_text(card["translation"])
        st.markdown(
            f"<div style='font-family: system-ui, sans-serif; font-size: 17px;'>{formatted_text}</div>",
            unsafe_allow_html=True
        )
    remove_key = f"remove_{idx}"
    if st.button("🗑️ Remove", key=remove_key):
        # Remove the flashcard by filtering out the index
        st.session_state.flashcards = [fc for i, fc in enumerate(st.session_state.flashcards) if i != idx]
        # Streamlit automatically reruns after interaction, so no manual rerun needed
