import streamlit as st
import fitz  # PyMuPDF
import os
from openai import OpenAI

# 🔐 Get API key from environment variable (set in Streamlit Cloud later)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 🧾 App config
st.set_page_config(page_title="Quote Summary Generator", layout="centered")
st.title("📄 Quote Summary Generator")
st.subheader("Step 1: Upload Quote PDFs")
st.markdown("You can upload 1 quote PDF per request per week on the Free Plan. This is currently the only plan available while we are in our testing phase.")

st.divider()

st.subheader("Step 2: Generate Summary")

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
        # 🧑 Optional: Client name and goal
    client_name = st.text_input("Client Name (optional)")

    goal = st.radio(
        "What's most important to your client?",
        options=["Lowest Price", "Broadest Coverage", "Balanced"],
        index=2,
        help="This helps shape the summary tone"
    )

        # 🆕 Preview Example Summary based on goal
    if st.button("📄 Preview Example Summary"):
        if goal == "Lowest Price":
            preview = f"""
Hi {client_name or '[Client Name]'},

Based on your preferences, we've included the most competitively priced quote below:

---

**Carrier: AmTrust**
- Premium: $1,950
- Deductible: $2,500  
- Coverage: Basic General Liability  
- Exclusions: Cyber, EPLI

This option offers lower upfront cost, but excludes certain risk protections.

Let us know if you'd like to review broader options.
"""
        elif goal == "Broadest Coverage":
            preview = f"""
Hi {client_name or '[Client Name]'},

We've highlighted the quote with the most comprehensive coverage below:

---

**Carrier: Guard**
- Premium: $2,450  
- Deductible: $1,000  
- Coverage: Includes Cyber, EPLI, and Blanket AI  
- Exclusions: Minimal

This option provides broader protection for a slightly higher premium.

Let us know if you'd like to compare cost-saving options as well.
"""
        else:  # Balanced
            preview = f"""
Hi {client_name or '[Client Name]'},

Here’s a well-balanced quote offering solid coverage at a reasonable price:

---

**Carrier: Liberty Mutual**
- Premium: $2,200  
- Deductible: $1,500  
- Coverage: General Liability, Cyber  
- Exclusions: EPLI not included

This is a great middle-ground option for price and protection.

Let us know if you'd like to explore more tailored options.
"""

        st.markdown(f"### 📧 Example Email Summary\n\n{preview}")


    # 🚀 Actual GPT summary trigger
    if st.button("Generate Summary"):
        text = extract_text_from_pdfs(uploaded_files)
        summary = generate_summary(text)
        st.subheader("📧 Email Summary")
        st.text_area("Copy this summary into your email to the client:", summary, height=300)

# 🧾 Info box for Free Plan limits
with st.expander("📦 Free Plan Limits"):
    st.markdown("""
**Current Usage Limits:**

- ✅ 1 PDF per request
- ✅ 1 summary per week (based on IP address, coming soon)
- ❌ No custom branding or proposal downloads yet
- 🚀 [Upgrade options coming soon]
""")

# 💬 Optional Feedback Form
st.divider()
st.subheader("💡 Got Feedback?")

with st.form("feedback_form"):
    suggestion = st.text_input("What's one thing you'd like this tool to do better?")
    email = st.text_input("Your email (optional)")
    submitted = st.form_submit_button("Submit Feedback")
    if submitted:
        st.success("✅ Thanks for your feedback! We'll use it to make the tool better.")
