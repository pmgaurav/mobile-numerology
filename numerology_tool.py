import streamlit as st
from datetime import datetime
from fpdf import FPDF
import random
import os

st.set_page_config(page_title="Numerology Tool", layout="centered")

# Mappings
RISK_PATTERNS = [
    '13', '31', '14', '41', '16', '61', '18', '81', '19', '91',
    '22', '222', '26', '62', '28', '82', '29', '92',
    '35', '53', '44', '45', '54', '49', '94', '69', '96', '72', '27',
    '777', '888', '444'
]

MOOLANK_RISKY_DIGITS = {
    1: {'6', '7', '8'},
    2: {'5', '8', '9'},
    3: {'2', '4', '8'},
    4: {'1', '6', '9'},
    5: {'2', '4', '9'},
    6: {'1', '3', '8'},
    7: {'1', '5', '6'},
    8: {'1', '2', '3'},
    9: {'2', '4', '5'},
}
BHAGYANK_RISKY_DIGITS = MOOLANK_RISKY_DIGITS.copy()

CHALDEAN_MAPPING = {
    1: "AIJQY",
    2: "BKR",
    3: "CGLS",
    4: "DMT",
    5: "EHNX",
    6: "UVW",
    7: "OZ",
    8: "FP"
}
letter_to_num = {char: num for num, chars in CHALDEAN_MAPPING.items() for char in chars}

def chaldean_number(name):
    total = sum(letter_to_num.get(char, 0) for char in name.upper())
    while total > 9:
        total = sum(int(d) for d in str(total))
    return total

def sum_to_root(number_str):
    total = sum(int(d) for d in number_str)
    while total > 9:
        total = sum(int(d) for d in str(total))
    return total

def is_safe_number(number):
    if any(p in number for p in RISK_PATTERNS):
        return False
    if number.endswith('00') or number.endswith('000'):
        return False
    if any(number.count(d) > 1 for d in set(number)):
        return False
    if number.count('7') >= 2 or number.endswith('6'):
        return False
    return True

def get_digits_to_avoid(moolank, bhagyank, name_number):
    risky = MOOLANK_RISKY_DIGITS.get(moolank, set()) | BHAGYANK_RISKY_DIGITS.get(bhagyank, set())
    return {d for d in risky if int(d) not in {moolank, bhagyank, name_number}}

def generate_combinations(preferred_roots, avoid_digits, length, limit):
    combinations = set()
    while len(combinations) < limit:
        digits = [d for d in '0123456789' if d not in avoid_digits]
        candidate = ''.join(random.sample(digits, length))
        if sum_to_root(candidate) not in preferred_roots or not is_safe_number(candidate):
            continue
        combinations.add(candidate)
    return sorted(combinations)

def generate_recommendation_pdf(name, dob_str, name_number, moolank, bhagyank, avoid_digits, preferred_roots, combos_4, combos_5):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Your Numerology Mobile Number Report", ln=True, align='C')
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Name: {name}", ln=True)
    pdf.cell(200, 10, txt=f"Date of Birth: {dob_str}", ln=True)
    pdf.cell(200, 10, txt=f"Name Number (Chaldean): {name_number}", ln=True)
    pdf.cell(200, 10, txt=f"Moolank: {moolank}", ln=True)
    pdf.cell(200, 10, txt=f"Bhagyank: {bhagyank}", ln=True)
    pdf.cell(200, 10, txt=f"Digits to Avoid: {', '.join(sorted(avoid_digits))}", ln=True)
    pdf.cell(200, 10, txt=f"Preferred Roots: {', '.join(map(str, preferred_roots))}", ln=True)
    pdf.ln(5)

    pdf.cell(200, 10, txt="Preferred 4-digit combinations:", ln=True)
    for combo in combos_4:
        pdf.cell(200, 10, txt=f"✔ {combo}", ln=True)

    pdf.ln(5)
    pdf.cell(200, 10, txt="Preferred 5-digit combinations:", ln=True)
    for combo in combos_5:
        pdf.cell(200, 10, txt=f"✔ {combo}", ln=True)

    path = "numerology_recommendation.pdf"
    pdf.output(path)
    return path

def generate_analysis_pdf(name, dob_str, number, analysis):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Your Mobile Number Analysis", ln=True, align='C')
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Name: {name}", ln=True)
    pdf.cell(200, 10, txt=f"Date of Birth: {dob_str}", ln=True)
    pdf.cell(200, 10, txt=f"Number Analyzed: {number}", ln=True)
    pdf.ln(5)
    for line in analysis:
        pdf.multi_cell(0, 10, txt=f"• {line}")
    path = "numerology_analysis.pdf"
    pdf.output(path)
    return path

# -------- Streamlit UI --------
st.title("🔢 Your Numerology Tool")

if 'submitted' not in st.session_state:
    st.session_state.submitted = False
if 'selected_option' not in st.session_state:
    st.session_state.selected_option = None
if 'analyzed' not in st.session_state:
    st.session_state.analyzed = False

name = st.text_input("Enter your name:")
dob_str = st.date_input("Enter your date of birth:", min_value=datetime(1900,1,1), max_value=datetime.today()).strftime("%d/%m/%Y")
option = st.radio("What would you like to do?", ["Get Number Recommendations", "Analyze an Existing Number"])
if st.button("Submit"):
    st.session_state.submitted = True
    st.session_state.selected_option = option
    st.session_state.analyzed = False

if st.session_state.submitted:
    day = int(dob_str.split("/")[0])
    moolank = day % 9 or 9
    digits = [int(d) for d in dob_str if d.isdigit()]
    bhagyank = sum(digits)
    while bhagyank > 9:
        bhagyank = sum(int(d) for d in str(bhagyank))
    name_number = chaldean_number(name)
    avoid_digits = get_digits_to_avoid(moolank, bhagyank, name_number)
    preferred_roots = list({moolank, bhagyank, name_number})

    st.markdown(f"""
    ### 🧘 Hello {name}
    - 🌟 Moolank (Birth Number): `{moolank}`
    - 💫 Bhagyank (Life Path Number): `{bhagyank}`
    - 🔢 Name Number: `{name_number}`
    - ❌ Digits to Avoid: `{', '.join(sorted(avoid_digits))}`
    - 📌 Preferred Roots: `{', '.join(map(str, preferred_roots))}`
    """)

    if st.session_state.selected_option == "Get Number Recommendations":
        combos_4 = generate_combinations(preferred_roots, avoid_digits, 4, 5)
        combos_5 = generate_combinations(preferred_roots, avoid_digits, 5, 5)

        st.subheader("✅ 4-digit Combinations:")
        st.write(", ".join(combos_4))
        st.subheader("✅ 5-digit Combinations:")
        st.write(", ".join(combos_5))

        if st.button("Download PDF Report"):
            path = generate_recommendation_pdf(name, dob_str, name_number, moolank, bhagyank, avoid_digits, preferred_roots, combos_4, combos_5)
            with open(path, "rb") as f:
                st.download_button("📄 Download PDF", f, file_name=path)

    elif st.session_state.selected_option == "Analyze an Existing Number":
        number = st.text_input("Enter the number to analyze:")
        if st.button("Analyze Number"):
            st.session_state.analyzed = True
            st.session_state.number = number

    if st.session_state.analyzed and st.session_state.number:
        number = st.session_state.number
        analysis = []

        root = sum_to_root(number)
        analysis.append(f"Final Root: {root}")
        if root in preferred_roots:
            analysis.append("✅ This number aligns with your preferred roots.")
        else:
            analysis.append("❌ This number does NOT align with your preferred roots.")

        if any(d in avoid_digits for d in number):
            analysis.append(f"❌ Contains risky digits: {', '.join(sorted(set(number) & avoid_digits))}")
        else:
            analysis.append("✅ No risky digits detected.")

        if is_safe_number(number):
            analysis.append("✅ The number passed safety checks.")
        else:
            analysis.append("❌ The number failed safety checks.")

        st.subheader("📊 Number Analysis Result:")
        for line in analysis:
            st.write(f"- {line}")

        if st.button("Download Analysis PDF"):
            path = generate_analysis_pdf(name, dob_str, number, analysis)
            with open(path, "rb") as f:
                st.download_button("📄 Download PDF", f, file_name=path)
