import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# ===================== PAGE SETUP =====================
st.set_page_config(page_title="Hospital Management System", layout="centered")

st.markdown(
    """
    <style>
    .main {background-color: #e6f0fa;}
    h1, h2, h3 {color: #2c3e50;}
    .banner {
        background: linear-gradient(90deg, #2c3e50, #3b82f6);
        color: white;
        padding: 24px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 20px;
        font-weight: 600;
        letter-spacing: 0.3px;
    }
    .footer {
        text-align: center;
        color: gray;
        font-size: 12px;
        margin-top: 50px;
    }
    .footer hr {
        border: none;
        border-top: 1px solid #ccc;
        margin: 20px 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ===================== BANNER =====================
st.markdown('<div class="banner">🏥 Digital Hospital Management System</div>', unsafe_allow_html=True)

# ===================== FILES =====================
PATIENT_FILE = "patients.csv"
APPOINTMENT_FILE = "appointments.csv"
DOCTOR_FILE = "doctors.json"

# ===================== HELPERS =====================
def ensure_csv_schema(file_path: str, required_columns: list):
    """Create CSV if missing; if present, add missing columns and reorder."""
    if not os.path.exists(file_path):
        pd.DataFrame(columns=required_columns).to_csv(file_path, index=False)
        return
    try:
        df = pd.read_csv(file_path)
    except Exception:
        pd.DataFrame(columns=required_columns).to_csv(file_path, index=False)
        return
    for col in required_columns:
        if col not in df.columns:
            df[col] = ""
    # Keep only required columns in defined order
    df = df[required_columns]
    df.to_csv(file_path, index=False)

def append_row_safe(file_path: str, row_dict: dict, required_columns: list):
    """Append a row safely using dict + concat after enforcing schema."""
    ensure_csv_schema(file_path, required_columns)
    df = pd.read_csv(file_path)
    safe_row = {col: row_dict.get(col, "") for col in required_columns}
    df = pd.concat([df, pd.DataFrame([safe_row])], ignore_index=True)
    df.to_csv(file_path, index=False)

def sanitize_phone(raw: str) -> str:
    """Keep only digits from phone input."""
    return "".join(ch for ch in (raw or "") if ch.isdigit())

def generate_patient_id():
    """Simple timestamp-based Patient ID."""
    return "P" + str(int(datetime.now().timestamp()))

def load_doctors():
    """Ensure doctors.json exists and return dict."""
    if not os.path.exists(DOCTOR_FILE):
        doctors = {
            "Dr Ali": ["Monday 10 to 1", "Wednesday 2 to 5"],
            "Dr Sara": ["Tuesday 9 to 12", "Thursday 1 to 4"]
        }
        with open(DOCTOR_FILE, "w") as f:
            json.dump(doctors, f, indent=4)
    with open(DOCTOR_FILE, "r") as f:
        return json.load(f)

# ===================== INITIAL DATA =====================
ensure_csv_schema(PATIENT_FILE, ["PatientID", "Name", "Age", "Gender", "Phone"])
ensure_csv_schema(APPOINTMENT_FILE, ["PatientID", "Doctor", "Date", "Time"])
_ = load_doctors()

# ===================== SESSION STATE =====================
if "logged_in_pid" not in st.session_state:
    st.session_state.logged_in_pid = None

# ===================== SIDEBAR =====================
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2966/2966327.png", width=180)
st.sidebar.markdown("## 🏥 Digital Hospital Management System")
st.sidebar.markdown("Made by **Rabia Muneeb**")

menu = st.sidebar.radio("Select Option", ["Patient Registration", "Patient Login", "Staff Dashboard"])

# ===================== PATIENT REGISTRATION =====================
if menu == "Patient Registration":
    st.subheader("📝 Register New Patient")

    with st.form(key="patient_registration_form", clear_on_submit=False):
        name = st.text_input("Full Name", key="reg_name")
        age = st.number_input("Age", min_value=1, max_value=120, key="reg_age")
        gender = st.selectbox("Gender", ["Male", "Female", "Other"], key="reg_gender")
        phone_input = st.text_input("Phone Number", placeholder="03XXXXXXXXX", key="reg_phone")
        submitted = st.form_submit_button("Register")

    if submitted:
        name_clean = (name or "").strip()
        phone_clean = sanitize_phone(phone_input)
        if not name_clean:
            st.warning("Please enter your name")
        elif not phone_clean or len(phone_clean) < 10:
            st.warning("Please enter your phone number (at least 10 digits)")
        else:
            pid = generate_patient_id()
            new_patient = {
                "PatientID": pid,
                "Name": name_clean,
                "Age": age,
                "Gender": gender,
                "Phone": phone_clean
            }
            append_row_safe(PATIENT_FILE, new_patient, ["PatientID", "Name", "Age", "Gender", "Phone"])
            st.session_state.logged_in_pid = pid  # optional convenience
            st.success("Registration successful")
            st.info(f"Your Patient ID is {pid}")

# ===================== PATIENT LOGIN + APPOINTMENT BOOKING =====================
elif menu == "Patient Login":
    st.subheader("🔐 Patient Login")

    # Login form
    with st.form(key="patient_login_form"):
        pid_input = st.text_input("Enter Patient ID", value=st.session_state.logged_in_pid or "")
        login_submitted = st.form_submit_button("Login")

    if login_submitted:
        ensure_csv_schema(PATIENT_FILE, ["PatientID", "Name", "Age", "Gender", "Phone"])
        df = pd.read_csv(PATIENT_FILE)
        pid = (pid_input or "").strip()
        if pid and pid in df["PatientID"].astype(str).values:
            st.session_state.logged_in_pid = pid
            st.success("Login successful")
        else:
            st.session_state.logged_in_pid = None
            st.error("Invalid Patient ID")

    # If logged in, show appointment booking
    if st.session_state.logged_in_pid:
        st.markdown("### 📅 Book Appointment")
        doctors = load_doctors()

        # Unified form: doctor + date + time captured together
        with st.form(key="appointment_form"):
            doctor = st.selectbox("Select Doctor", list(doctors.keys()))
            st.write("Available slots:", doctors.get(doctor, []))
            date = st.date_input("Appointment Date")
            time = st.text_input("Appointment Time (e.g., 10:00 AM)")
            appt_submitted = st.form_submit_button("Confirm Appointment")

        if appt_submitted:
            time_clean = (time or "").strip()
            if not time_clean:
                st.warning("Please enter appointment time")
            else:
                new_appt = {
                    "PatientID": str(st.session_state.logged_in_pid),
                    "Doctor": doctor,
                    "Date": str(date),
                    "Time": time_clean
                }
                append_row_safe(APPOINTMENT_FILE, new_appt, ["PatientID", "Doctor", "Date", "Time"])
                st.success(f"Appointment booked successfully with {doctor} on {date} at {time_clean}")

        st.markdown("### 📄 Your Appointments")
        ensure_csv_schema(APPOINTMENT_FILE, ["PatientID", "Doctor", "Date", "Time"])
        ap_df = pd.read_csv(APPOINTMENT_FILE)
        filtered = ap_df[ap_df["PatientID"].astype(str) == str(st.session_state.logged_in_pid)]
        st.dataframe(filtered, use_container_width=True)

# ===================== STAFF DASHBOARD =====================
elif menu == "Staff Dashboard":
    st.subheader("🧑‍⚕️ Staff Dashboard")

    with st.form(key="staff_form"):
        password = st.text_input("Enter Staff Password", type="password")
        staff_submitted = st.form_submit_button("Enter")

    if staff_submitted:
        if password == "admin123":
            st.success("Access granted")

            st.markdown("### 👥 Registered Patients")
            ensure_csv_schema(PATIENT_FILE, ["PatientID", "Name", "Age", "Gender", "Phone"])
            st.dataframe(pd.read_csv(PATIENT_FILE), use_container_width=True)

            st.markdown("### 📅 Booked Appointments")
            ensure_csv_schema(APPOINTMENT_FILE, ["PatientID", "Doctor", "Date", "Time"])
            ap_df = pd.read_csv(APPOINTMENT_FILE)
            # Show all columns clearly
            st.dataframe(ap_df[["PatientID", "Doctor", "Date", "Time"]], use_container_width=True)

            st.markdown("### 🩺 Available Doctors")
            doctors = load_doctors()
            doctor_df = pd.DataFrame(
                [{"Doctor": doc, "Available Slots": ", ".join(slots)} for doc, slots in doctors.items()]
            )
            st.dataframe(doctor_df, use_container_width=True)
        else:
            st.warning("Enter correct password")

# ===================== FOOTER =====================
st.markdown(
    """
    <div class="footer">
        <hr>
        © 2025 Digital Hospital Management System | All Rights Reserved
    </div>
    """,
    unsafe_allow_html=True
)