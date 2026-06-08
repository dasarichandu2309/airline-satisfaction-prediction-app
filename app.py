import streamlit as st
import joblib
import pandas as pd
import time

# ---------------- LOAD MODEL ----------------
model = joblib.load("model.pkl")
features = joblib.load("features.pkl")

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Airline Satisfaction", layout="wide")

# ---------------- CSS ----------------
st.markdown("""
<style>
.stApp { background:#020617; }

.title {
    font-size:40px;
    font-weight:bold;
    color:#60A5FA;
    text-align:center;
}

label { color:#93c5fd !important; }

/* 🔥 BUTTON */
.stButton {
    display:flex;
    justify-content:center;
}

.stButton>button {
    background: linear-gradient(90deg,#2563eb,#3b82f6);
    color:white !important;
    border-radius:20px;
    height:70px !important;
    width:100% !important;
    max-width:750px;
    font-size:22px !important;
}

/* 🔥 POPUP */
</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.markdown("<div class='title'>✈️ Airline Passenger Satisfaction</div>", unsafe_allow_html=True)
st.write("😊 Satisfied | 😐 Neutral | 😞 Not Satisfied")
st.markdown("---")

# ---------------- INPUT ----------------
col1,col2,col3,col4,col5 = st.columns(5)

with col1:
    gender = st.selectbox("Gender", ["Male","Female"])

with col2:
    customer_type = st.selectbox("Customer Type", ["Loyal Customer","Disloyal Customer"])

with col3:
    age = st.slider("Age", 7, 85, 30)

with col4:
    travel_type = st.selectbox("Travel Type", ["Business travel","Personal Travel"])

with col5:
    class_type = st.selectbox("Class", ["Eco","Eco Plus","Business"])

# ---------------- SERVICE ----------------
col6,col7,col8,col9 = st.columns(4)

with col6:
    flight_distance = st.slider("Flight Distance", 31, 4983, 500)

with col7:
    wifi = st.slider("WiFi",0,5,3)

with col8:
    time_conv = st.slider("Time Convenience",0,5,3)

with col9:
    booking = st.slider("Booking",0,5,3)

col10,col11,col12 = st.columns(3)

with col10:
    food = st.slider("Food",0,5,3)

with col11:
    service = st.slider("Service",0,5,3)

with col12:
    clean = st.slider("Cleanliness",0,5,3)

# ---------------- BUTTON ----------------
st.markdown("<br>", unsafe_allow_html=True)

col1,col2,col3 = st.columns([1,6,1])

with col2:
    predict = st.button("🚀 Predict Satisfaction", use_container_width=True)

# ---------------- PREDICTION ----------------
if predict:

    with st.spinner("Analyzing..."):
        time.sleep(1)

    # -------- ENCODING --------
    gender = 1 if gender=="Male" else 0
    customer_map = {"Loyal Customer":1,"Disloyal Customer":0}
    travel_map = {"Business travel":1,"Personal Travel":0}
    class_map = {"Eco":0,"Eco Plus":1,"Business":2}

    input_data = pd.DataFrame({
        "Gender":[gender],
        "Customer Type":[customer_map[customer_type]],
        "Age":[age],
        "Type of Travel":[travel_map[travel_type]],
        "Class":[class_map[class_type]],
        "Flight Distance":[flight_distance],

        "Inflight WiFi service":[wifi],
        "Departure and Arrival Time Convenience":[time_conv],
        "Ease of Online Booking":[booking],
        "Food and Drink":[food],
        "Inflight Service":[service],
        "Cleanliness":[clean],

        "Baggage Handling":[3],
        "Check-in Service":[3],
        "Departure Delay":[0],
        "Arrival Delay":[0]
    })

    input_data = input_data.reindex(columns=features, fill_value=0)

    # -------- ML PREDICTION --------
    prediction = model.predict(input_data)[0]

    # -------- RULE SMOOTHING --------
    avg_rating = (wifi+food+service+clean+booking+time_conv)/6

    if prediction == 1 and avg_rating >= 4:
        result = "😊 Passenger is SATISFIED"
        color = "#60A5FA"
        st.balloons()

    elif prediction == 0 and avg_rating <= 2:
        result = "😞 Passenger is NOT SATISFIED"
        color = "#ef4444"

    else:
        result = "😐 Passenger is NEUTRAL"
        color = "#facc15"

    # -------- POPUP (CLICK ANYWHERE CLOSE) --------
    st.markdown(f"""
    <div id="popup" style="
        position:fixed;
        top:50%;
        left:50%;
        transform:translate(-50%,-50%);
        background:linear-gradient(135deg,#0f172a,#020617);
        padding:30px;
        border-radius:20px;
        border:2px solid {color};
        text-align:center;
        box-shadow:0px 0px 40px {color};
        z-index:9999;
    ">

    <h2 style="color:{color};">{result}</h2>
    <p style="color:#9CA3AF;">Click anywhere to close</p>

    </div>

    <script>
    document.addEventListener("click", function() {{
        var popup = document.getElementById("popup");
        if (popup) {{
            popup.style.display = "none";
        }}
    }});

    setTimeout(function() {{
        var popup = document.getElementById("popup");
        if (popup) {{
            popup.style.display = "none";
        }}
    }}, 4000);
    </script>
    """, unsafe_allow_html=True)

# ---------------- FOOTER ----------------
st.markdown("---")
st.markdown("💡 ML + Rule Hybrid Model 🚀")