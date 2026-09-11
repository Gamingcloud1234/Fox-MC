import os
import uuid
from datetime import datetime, timezone

import bcrypt
import pandas as pd
import streamlit as st
from supabase import create_client, Client

st.set_page_config(
    page_title="Staff Applications",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Configuration ----------
SUPABASE_URL = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL", ""))
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", os.getenv("SUPABASE_KEY", ""))
DISCORD_URL = st.secrets.get(
    "DISCORD_URL",
    os.getenv("DISCORD_URL", "https://discord.com/")
)
ADMIN_USERNAME = st.secrets.get("ADMIN_USERNAME", os.getenv("ADMIN_USERNAME", "admin"))
ADMIN_PASSWORD_HASH = st.secrets.get(
    "ADMIN_PASSWORD_HASH",
    os.getenv("ADMIN_PASSWORD_HASH", "")
)

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Database is not configured. Add SUPABASE_URL and SUPABASE_KEY to Streamlit Secrets.")
    st.stop()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------- Styling ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 10% 0%, rgba(59,130,246,.10), transparent 28%),
        radial-gradient(circle at 90% 10%, rgba(124,58,237,.10), transparent 28%),
        #080b12;
}

.block-container {
    max-width: 1200px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

.hero {
    padding: 30px;
    border: 1px solid rgba(255,255,255,.08);
    border-radius: 24px;
    background: linear-gradient(135deg, rgba(20,28,45,.95), rgba(12,15,25,.96));
    box-shadow: 0 20px 70px rgba(0,0,0,.25);
    margin-bottom: 22px;
}

.hero h1 {
    font-size: 42px;
    margin: 0;
    font-weight: 800;
    letter-spacing: -1px;
}

.hero p {
    color: #aab4c5;
    font-size: 16px;
    margin-top: 10px;
}

.card {
    padding: 22px;
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,.08);
    background: rgba(17,23,35,.78);
    margin-bottom: 16px;
}

.small {
    color: #8d99ad;
    font-size: 13px;
}

.status {
    display: inline-block;
    padding: 6px 11px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 700;
    background: #1f2937;
}

.status-pending { color: #fbbf24; }
.status-approved { color: #34d399; }
.status-rejected { color: #fb7185; }
.status-review { color: #60a5fa; }

div.stButton > button {
    border-radius: 11px;
    font-weight: 700;
}

section[data-testid="stSidebar"] {
    background: #0a0e17;
    border-right: 1px solid rgba(255,255,255,.06);
}
</style>
""", unsafe_allow_html=True)

# ---------- Helpers ----------
def require_admin_config():
    if not ADMIN_PASSWORD_HASH:
        st.warning("Admin password is not configured. Add ADMIN_PASSWORD_HASH to Streamlit Secrets.")
        st.stop()

def verify_password(password: str) -> bool:
    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            ADMIN_PASSWORD_HASH.encode("utf-8")
        )
    except Exception:
        return False

def insert_application(data):
    result = supabase.table("applications").insert(data).execute()
    return result.data[0] if result.data else None

def get_applications():
    result = supabase.table("applications").select("*").order("created_at", desc=True).execute()
    return result.data or []

def update_application(app_id, values):
    return supabase.table("applications").update(values).eq("id", app_id).execute()

def app_status_badge(status):
    css = {
        "Pending": "status-pending",
        "Under Review": "status-review",
        "Approved": "status-approved",
        "Rejected": "status-rejected",
    }.get(status, "status-review")
    return f'<span class="status {css}">{status}</span>'

# ---------- Session ----------
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("## 🛡️ Staff Portal")
    st.caption("Professional application management")
    st.divider()

    page = st.radio(
        "Navigation",
        ["Apply for Staff", "Join Discord", "Admin Panel"],
        index=0
    )

    st.divider()
    st.caption("Secure staff recruitment system")

# ---------- Apply ----------
if page == "Apply for Staff":
    st.markdown("""
    <div class="hero">
        <h1>FOXMC Staff Application</h1>
        <p>Welcome to the official FOXMC Staff Application. Please answer every question honestly and carefully.</p>
    </div>
    """, unsafe_allow_html=True)

    st.link_button("💬 Join FOXMC Discord", DISCORD_URL, use_container_width=True)

    st.markdown("## 📝 FILL THIS FORM")
    st.caption("Time of filling this form: 10–15 minutes max. Make sure to answer all questions honestly.")

    with st.form("foxmc_staff_application", clear_on_submit=False):

        st.markdown("### 1. Basic Information")
        discord = st.text_input("I. Discord Username *", max_chars=80)
        minecraft = st.text_input("II. Minecraft Username *", max_chars=80)
        age = st.number_input("III. Age *", min_value=13, max_value=100, value=16)
        timezone_name = st.text_input("IV. Country / Timezone *", placeholder="e.g. Pakistan / UTC+5")

        st.markdown("---")
        st.markdown("### 2. Staff Experience")
        position = st.selectbox(
            "I. Which position are you applying for? *",
            ["Moderator", "Trial Moderator", "Helper", "Support", "Builder", "Event Team", "Other"]
        )
        previous_experience = st.radio(
            "II. Do you have any previous staff experience? *",
            ["Yes", "No"],
            horizontal=True
        )
        experience = st.text_area(
            "III. If yes, briefly describe your experience :",
            height=120,
            placeholder="Describe your previous server/staff experience. If none, write N/A."
        )

        st.markdown("---")
        st.markdown("### 3. About You")
        why_us = st.text_area(
            "I. Why do you want to join the FOXMC Staff Team? *",
            height=130
        )
        why_choose = st.text_area(
            "II. Why should we choose you? *",
            height=130
        )
        activity = st.text_area(
            "III. How active can you be on FOXMC? *",
            height=120,
            placeholder="Tell us approximately how often you can be online."
        )

        st.markdown("---")
        st.markdown("### 4. Situational Questions")
        scenario_rule = st.text_area(
            "I. A player repeatedly breaks the rules after being warned. What would you do? *",
            height=150
        )
        scenario_friend = st.text_area(
            "II. What would you do if your friend broke a server rule? *",
            height=150
        )

        st.markdown("---")
        st.markdown("### 5. Final")
        agree = st.radio(
            "I. Do you agree to follow all FOXMC rules and staff guidelines? *",
            ["Yes", "No"],
            horizontal=True
        )
        anything_else = st.text_area(
            "II. Is there anything else you would like to tell us?",
            height=120
        )

        confirm = st.checkbox(
            "I confirm that my answers are honest and that I agree to follow FOXMC rules and staff guidelines. *"
        )

        submitted = st.form_submit_button("🚀 SUBMIT STAFF APPLICATION", use_container_width=True)

    if submitted:
        required = [
            discord.strip(), minecraft.strip(), timezone_name.strip(),
            experience.strip(), why_us.strip(), why_choose.strip(),
            activity.strip(), scenario_rule.strip(), scenario_friend.strip()
        ]

        if not all(required):
            st.error("Please answer all required questions.")
        elif agree != "Yes":
            st.error("You must agree to follow FOXMC rules and staff guidelines.")
        elif not confirm:
            st.error("Please confirm that your answers are honest.")
        else:
            application_id = "FOX-" + uuid.uuid4().hex[:8].upper()

            data = {
                "application_id": application_id,
                "name": minecraft.strip(),
                "discord": discord.strip(),
                "age": int(age),
                "minecraft": minecraft.strip(),
                "timezone": timezone_name.strip(),
                "hours_per_week": 0,
                "experience": experience.strip(),
                "why_us": why_us.strip(),
                "strengths": why_choose.strip(),
                "scenario": (
                    f"Repeated rule breaking: {scenario_rule.strip()}\n\n"
                    f"Friend breaking a rule: {scenario_friend.strip()}"
                ),
                "position": position,
                "previous_staff_experience": previous_experience,
                "activity": activity.strip(),
                "agreed_to_rules": agree,
                "anything_else": anything_else.strip(),
                "status": "Pending",
                "admin_notes": "",
                "created_at": datetime.now(timezone.utc).isoformat(),
            }

            try:
                saved = insert_application(data)
                if saved:
                    st.success(
                        f"Application submitted successfully! Your application ID is **{application_id}**."
                    )
                    st.info("Keep your application ID for future reference.")
                else:
                    st.error("The application could not be saved.")
            except Exception as e:
                st.error("Database error. Please try again later.")
                st.caption(str(e))

# ---------- Discord ----------
elif page == "Join Discord":
    st.markdown("""
    <div class="hero">
        <h1>Join the Community</h1>
        <p>Join our Discord to stay updated, communicate with staff, and receive application updates.</p>
    </div>
    """, unsafe_allow_html=True)

    st.link_button("💬 Join Discord Server", DISCORD_URL, use_container_width=True)

    st.markdown("""
    <div class="card">
        <h3>Why join Discord?</h3>
        <p>• Community announcements</p>
        <p>• Staff communication</p>
        <p>• Recruitment updates</p>
        <p>• Support and questions</p>
    </div>
    """, unsafe_allow_html=True)

# ---------- Admin Login / Panel ----------
else:
    if not st.session_state.admin_logged_in:
        st.markdown("""
        <div class="hero">
            <h1>Admin Panel</h1>
            <p>Authorized staff only. Sign in to review and manage applications.</p>
        </div>
        """, unsafe_allow_html=True)

        require_admin_config()

        with st.form("admin_login"):
            username = st.text_input("Admin Username")
            password = st.text_input("Admin Password", type="password")
            login = st.form_submit_button("🔐 Sign In", use_container_width=True)

        if login:
            if username == ADMIN_USERNAME and verify_password(password):
                st.session_state.admin_logged_in = True
                st.rerun()
            else:
                st.error("Invalid admin credentials.")
        st.stop()

    st.markdown("""
    <div class="hero">
        <h1>Admin Dashboard</h1>
        <p>Review applications, update statuses, and leave internal notes.</p>
    </div>
    """, unsafe_allow_html=True)

    top1, top2 = st.columns([4, 1])
    with top1:
        st.success("You are signed in as an administrator.")
    with top2:
        if st.button("Log out", use_container_width=True):
            st.session_state.admin_logged_in = False
            st.rerun()

    try:
        applications = get_applications()
    except Exception as e:
        st.error("Could not load applications.")
        st.caption(str(e))
        st.stop()

    df = pd.DataFrame(applications)

    if df.empty:
        st.info("No applications have been submitted yet.")
        st.stop()

    statuses = df["status"].fillna("Pending")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total", len(df))
    m2.metric("Pending", int((statuses == "Pending").sum()))
    m3.metric("Approved", int((statuses == "Approved").sum()))
    m4.metric("Rejected", int((statuses == "Rejected").sum()))

    st.divider()

    f1, f2 = st.columns([2, 3])
    with f1:
        filter_status = st.selectbox(
            "Filter status",
            ["All", "Pending", "Under Review", "Approved", "Rejected"]
        )
    with f2:
        search = st.text_input("Search", placeholder="Name, Discord, Minecraft username, or application ID")

    filtered = df.copy()
    if filter_status != "All":
        filtered = filtered[filtered["status"] == filter_status]

    if search.strip():
        q = search.strip().lower()
        mask = (
            filtered["name"].fillna("").str.lower().str.contains(q, na=False)
            | filtered["discord"].fillna("").str.lower().str.contains(q, na=False)
            | filtered["minecraft"].fillna("").str.lower().str.contains(q, na=False)
            | filtered["application_id"].fillna("").str.lower().str.contains(q, na=False)
        )
        filtered = filtered[mask]

    st.markdown(f"### Applications ({len(filtered)})")

    for _, row in filtered.iterrows():
        app_id = row["id"]
        title = f'{row.get("application_id", "Unknown")} • {row.get("name", "Unknown")} • {row.get("discord", "")}'

        with st.expander(title):
            left, right = st.columns([2, 1])

            with left:
                st.markdown(f"**Status:** {app_status_badge(row.get('status', 'Pending'))}", unsafe_allow_html=True)
                st.write(f"**Minecraft:** {row.get('minecraft') or 'Not provided'}")
                st.write(f"**Age:** {row.get('age')}")
                st.write(f"**Timezone:** {row.get('timezone') or 'Not provided'}")
                st.write(f"**Availability:** {row.get('hours_per_week')} hours/week")

                st.markdown("**Previous Staff Experience**")
                st.write(row.get("experience") or "Not provided")

                st.markdown("**Why should we choose you?**")
                st.write(row.get("why_us") or "Not provided")

                st.markdown("**Strengths**")
                st.write(row.get("strengths") or "Not provided")

                st.markdown("**Scenario Answer**")
                st.write(row.get("scenario") or "Not provided")

            with right:
                current_status = row.get("status") or "Pending"
                new_status = st.selectbox(
                    "Update status",
                    ["Pending", "Under Review", "Approved", "Rejected"],
                    index=["Pending", "Under Review", "Approved", "Rejected"].index(current_status),
                    key=f"status_{app_id}"
                )

                notes = st.text_area(
                    "Internal admin notes",
                    value=row.get("admin_notes") or "",
                    height=160,
                    key=f"notes_{app_id}"
                )

                if st.button("Save Changes", key=f"save_{app_id}", use_container_width=True):
                    try:
                        update_application(app_id, {
                            "status": new_status,
                            "admin_notes": notes
                        })
                        st.success("Application updated.")
                        st.rerun()
                    except Exception as e:
                        st.error("Could not update application.")
                        st.caption(str(e))

            st.caption(f"Submitted: {row.get('created_at', 'Unknown')}")
