import streamlit as st
import joblib
import pandas as pd
import time

# ---------------- LOAD MODEL (optional now) ----------------
model = joblib.load("model.pkl")
features = joblib.load("features.pkl")

# ---------------- PAGE ----------------
st.set_page_config(page_title="Airline Satisfaction", layout="wide")

# ---------------- CSS ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #020617, #020617);
}

.title {
    font-size: 40px;
    font-weight: bold;
    color: #60A5FA;
    text-align: center;
}

label {
    color: #93c5fd !important;
    font-weight: 500;
}

.stButton>button {
    background: linear-gradient(90deg, #2563eb, #3b82f6);
    color: white;
    border-radius: 12px;
    height: 3em;
    width: 50%;
    font-size: 18px;
    margin: auto;
    display: block;
}

.popup {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: linear-gradient(135deg, #0f172a, #020617);
    padding: 30px;
    border-radius: 20px;
    border: 2px solid;
    box-shadow: 0px 0px 40px;
    z-index: 9999;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.markdown("<div class='title'>✈️ Airline Passenger Satisfaction Prediction</div>", unsafe_allow_html=True)
st.write("😊 Satisfied | 😐 Neutral | 😞 Not Satisfied")
st.markdown("---")

# ---------------- INPUT ----------------
st.markdown("## 👤 Passenger Information")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    gender = st.selectbox("👤 Gender", ["Male", "Female"])

with col2:
    customer_type = st.selectbox("🧑‍💼 Customer Type", ["Loyal Customer", "Disloyal Customer"])

with col3:
    age = st.slider("🎂 Age", 10, 80, 30)

with col4:
    travel_type = st.selectbox("🧳 Type of Travel", ["Business travel", "Personal Travel"])

with col5:
    class_type = st.selectbox("💺 Class", ["Eco", "Eco Plus", "Business"])

# ---------------- SERVICE ----------------
st.markdown("## ✈️ Flight & Service Ratings")

col6, col7, col8, col9 = st.columns(4)

with col6:
    flight_distance = st.number_input("🛫 Flight Distance", 0, 5000, 500)

with col7:
    wifi = st.slider("📶 Inflight WiFi", 0, 5, 3)

with col8:
    time_conv = st.slider("⏰ Departure Time", 0, 5, 3)

with col9:
    booking = st.slider("🌐 Online Booking", 0, 5, 3)

col10, col11, col12 = st.columns(3)

with col10:
    food = st.slider("🍽️ Food & Drink", 0, 5, 3)

with col11:
    service = st.slider("🧑‍✈️ Inflight Service", 0, 5, 3)

with col12:
    clean = st.slider("✨ Cleanliness", 0, 5, 3)

# ---------------- BUTTON ----------------
predict = st.button("🚀 Predict Satisfaction")

# ---------------- PREDICTION ----------------
if predict:

    with st.spinner("🔍 Analyzing passenger data..."):
        time.sleep(1.5)

    # ---------------- RULE-BASED SYSTEM ----------------
    avg_rating = (wifi + food + service + clean + booking + time_conv) / 6

    # ⭐ HIGH QUALITY → SATISFIED
    if avg_rating >= 4:
        result_text = "😊 Passenger is SATISFIED"
        color = "#60A5FA"
        st.balloons()

    # ⭐ MID → NEUTRAL
    elif 2.5 <= avg_rating < 4:
        result_text = "😐 Passenger is NEUTRAL"
        color = "#facc15"
        st.markdown("<div style='font-size:60px;text-align:center;'>😐</div>", unsafe_allow_html=True)

    # ⭐ LOW → NOT SATISFIED
    else:
        result_text = "😞 Passenger is NOT SATISFIED"
        color = "#ef4444"
        st.markdown("<div style='font-size:60px;text-align:center;'>😞💔</div>", unsafe_allow_html=True)

    # ---------------- POPUP ----------------
    st.markdown(f"""
    <div class='popup' style='border-color:{color}; box-shadow:0px 0px 40px {color};'>
        <h2 style='color:{color};'>{result_text}</h2>
        <p style='color:#9CA3AF;'>Based on service & travel features</p>
    </div>
    """, unsafe_allow_html=True)

# ---------------- FOOTER ----------------
st.markdown("---")
st.markdown("💡 Built with Streamlit | ML Project 🚀")