import streamlit as st
import fitz  # PyMuPDF
import os
from openai import OpenAI

# 🔐 Get API key from environment variable (set in Streamlit Cloud later)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 🧾 App config
st.set_page_config(page_title="Quote Summary Generator", layout="centered")
st.title("📄 Quote Summary Generator")

st.markdown("""
Upload your quote PDFs below. We'll generate a clean, client-ready summary that you can copy and paste into an email.
""")

# 📥 File upload
uploaded_files = st.file_uploader("Upload Quote PDFs", type="pdf", accept_multiple_files=True)

# 🔐 Free plan upload limit (adjust per pricing tier)
MAX_FILES = 1

if uploaded_files and len(uploaded_files) > MAX_FILES:
    st.error(f"Your plan allows a maximum of {MAX_FILES} PDF(s) per request.")
    st.stop()

# 📃 Extract all text from uploaded PDFs
def extract_text_from_pdfs(files):
    all_text = ""
    for file in files:
        with fitz.open(stream=file.read(), filetype="pdf") as doc:
            for page in doc:
                all_text += page.get_text()
    return all_text

# 🤖 Generate plain-language email summary
def generate_summary(text):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an assistant helping insurance agents summarize quote PDFs."},
            {"role": "user", "content": f"""
You're a commercial insurance assistant helping brokers summarize and communicate quotes to their clients.

Read the following quote(s) and prepare a professional, plain-English email summary for the insured. Your summary should:
- Highlight total premium, limits, deductibles, and carrier
- Clearly explain any major coverage differences and/or exclusions
- Flag any missing coverages or unusual endorsements
- Help the broker appear informed and helpful

Quotes:
{text}
"""}

        ],
        temperature=0.4,
    )
    return response.choices[0].message.content.strip()

# ▶️ Generate summary button logic
if uploaded_files:
    if st.button("Generate Summary"):
        text = extract_text_from_pdfs(uploaded_files)
        summary = generate_summary(text)
        st.subheader("📧 Email Summary")
        st.text_area("Copy this summary into your email to the client:", summary, height=300)
