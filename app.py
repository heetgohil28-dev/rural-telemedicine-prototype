import os
import re
import sqlite3
import streamlit as st

st.set_page_config(page_title="Rural Telemedicine", page_icon="🏥")

DOCTOR_PASSWORD = "doctor123"   # demo only
DB_FILE = os.environ.get("DB_PATH", "telemed.db")
SLOTS = ["10:00 AM", "11:00 AM", "2:00 PM", "4:00 PM"]


# ---------- Database ----------
@st.cache_resource
def get_db():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.execute("""CREATE TABLE IF NOT EXISTS appointments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, age INTEGER, village TEXT, phone TEXT,
        symptoms TEXT, slot TEXT,
        status TEXT DEFAULT 'Pending',
        prescription TEXT DEFAULT '')""")
    conn.commit()
    return conn


db = get_db()


def video_link(appt_id):
    return f"https://meet.jit.si/telemed-appointment-{appt_id}"


# ---------- Language ----------
T = {
    "English": dict(
        title="Rural Telemedicine", book="Book Appointment",
        status="Check Status", doctor="Doctor Panel",
        name="Name", age="Age", village="Village", phone="Phone (10 digits)",
        symptoms="Symptoms", slot="Time slot", submit="Submit",
        ok="Appointment booked! Your ID is", fill="Please fill name, phone and symptoms",
        bad_phone="Phone number must be exactly 10 digits",
        none="No records found", rx="Prescription / Advice",
        pw="Doctor password", wrong="Wrong password",
        save="Save prescription", rx_empty="Write a prescription first",
        pending="Pending", completed="Completed",
        no_pending="No pending requests", no_completed="No completed consultations",
        video="Join video consult", status_lbl="Status"),
    "हिन्दी": dict(
        title="ग्रामीण टेलीमेडिसिन", book="अपॉइंटमेंट बुक करें",
        status="स्थिति देखें", doctor="डॉक्टर पैनल",
        name="नाम", age="उम्र", village="गाँव", phone="फोन (10 अंक)",
        symptoms="लक्षण", slot="समय", submit="जमा करें",
        ok="अपॉइंटमेंट बुक हो गया! आपकी आईडी है", fill="कृपया नाम, फोन और लक्षण भरें",
        bad_phone="फोन नंबर ठीक 10 अंकों का होना चाहिए",
        none="कोई रिकॉर्ड नहीं मिला", rx="दवा / सलाह",
        pw="डॉक्टर पासवर्ड", wrong="गलत पासवर्ड",
        save="सलाह सेव करें", rx_empty="पहले सलाह लिखें",
        pending="लंबित", completed="पूर्ण",
        no_pending="कोई लंबित अनुरोध नहीं", no_completed="कोई पूर्ण परामर्श नहीं",
        video="वीडियो परामर्श से जुड़ें", status_lbl="स्थिति"),
}

lang = st.sidebar.selectbox("Language / भाषा", list(T))
t = T[lang]
page = st.sidebar.radio("Menu", [t["book"], t["status"], t["doctor"]])
st.title("🏥 " + t["title"])


# ---------- Page 1: Book appointment (patient) ----------
if page == t["book"]:
    with st.form("book_form", clear_on_submit=True):
        name = st.text_input(t["name"])
        age = st.number_input(t["age"], 1, 120, 30)
        village = st.text_input(t["village"])
        phone = st.text_input(t["phone"], max_chars=10)
        symptoms = st.text_area(t["symptoms"])
        slot = st.selectbox(t["slot"], SLOTS)
        submitted = st.form_submit_button(t["submit"])

    if submitted:
        if not (name.strip() and phone.strip() and symptoms.strip()):
            st.error(t["fill"])
        elif not re.fullmatch(r"\d{10}", phone):
            st.error(t["bad_phone"])
        else:
            cur = db.execute(
                "INSERT INTO appointments(name,age,village,phone,symptoms,slot) "
                "VALUES(?,?,?,?,?,?)",
                (name.strip(), age, village.strip(), phone, symptoms.strip(), slot))
            db.commit()
            st.success(f"{t['ok']} #{cur.lastrowid}")
            st.markdown(f"[{t['video']}]({video_link(cur.lastrowid)})")


# ---------- Page 2: Check status (patient) ----------
elif page == t["status"]:
    phone = st.text_input(t["phone"], max_chars=10)
    if phone:
        rows = db.execute(
            "SELECT id, slot, status, prescription FROM appointments "
            "WHERE phone=? ORDER BY id DESC", (phone,)).fetchall()
        if not rows:
            st.info(t["none"])
        for appt_id, slot, status, rx in rows:
            with st.container(border=True):
                st.write(f"**#{appt_id}** | {slot} | {t['status_lbl']}: **{status}**")
                if rx:
                    st.success(f"{t['rx']}: {rx}")
                else:
                    st.markdown(f"[{t['video']}]({video_link(appt_id)})")


# ---------- Page 3: Doctor panel ----------
else:
    pw = st.text_input(t["pw"], type="password")
    if pw == "":
        pass
    elif pw != DOCTOR_PASSWORD:
        st.warning(t["wrong"])
    else:
        tab_pending, tab_done = st.tabs([t["pending"], t["completed"]])

        with tab_pending:
            rows = db.execute(
                "SELECT id,name,age,village,symptoms,slot FROM appointments "
                "WHERE status='Pending' ORDER BY id").fetchall()
            if not rows:
                st.info(t["no_pending"])
            for appt_id, name, age, village, symptoms, slot in rows:
                with st.expander(f"#{appt_id} {name} ({age}), {village} | {slot}"):
                    st.write(symptoms)
                    st.markdown(f"[{t['video']}]({video_link(appt_id)})")
                    rx = st.text_area(t["rx"], key=f"rx{appt_id}")
                    if st.button(t["save"], key=f"btn{appt_id}"):
                        if rx.strip():
                            db.execute(
                                "UPDATE appointments SET prescription=?, "
                                "status='Completed' WHERE id=?", (rx.strip(), appt_id))
                            db.commit()
                            st.rerun()
                        else:
                            st.error(t["rx_empty"])

        with tab_done:
            rows = db.execute(
                "SELECT id,name,village,symptoms,prescription FROM appointments "
                "WHERE status='Completed' ORDER BY id DESC").fetchall()
            if not rows:
                st.info(t["no_completed"])
            for appt_id, name, village, symptoms, rx in rows:
                with st.container(border=True):
                    st.write(f"**#{appt_id} {name}**, {village}")
                    st.caption(symptoms)
                    st.success(rx)