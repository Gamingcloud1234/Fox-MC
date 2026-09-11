import os
import uuid
from datetime import datetime, timezone

import bcrypt
import pandas as pd
import streamlit as st
from supabase import create_client, Client


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="FOXMC Staff Applications",
    page_icon="🦊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# SECRETS / CONFIG
# =========================================================

SUPABASE_URL = st.secrets.get(
    "SUPABASE_URL",
    os.getenv("SUPABASE_URL", "")
)

SUPABASE_KEY = st.secrets.get(
    "SUPABASE_KEY",
    os.getenv("SUPABASE_KEY", "")
)

DISCORD_URL = st.secrets.get(
    "DISCORD_URL",
    os.getenv("DISCORD_URL", "https://discord.gg/EnRHX6qW")
)

ADMIN_USERNAME = st.secrets.get(
    "ADMIN_USERNAME",
    os.getenv("ADMIN_USERNAME", "admin")
)

ADMIN_PASSWORD_HASH = st.secrets.get(
    "ADMIN_PASSWORD_HASH",
    os.getenv("ADMIN_PASSWORD_HASH", "")
)


if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Database is not configured.")
    st.info(
        "Add SUPABASE_URL and SUPABASE_KEY to "
        "Streamlit Cloud → Settings → Secrets."
    )
    st.stop()


supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


# =========================================================
# WHITE / PROFESSIONAL THEME
# =========================================================

st.markdown(
    """
    <style>

    @import url(
        'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap'
    );

    * {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: #ffffff;
        color: #111827;
    }

    .main {
        background: #ffffff;
    }

    .block-container {
        max-width: 1180px;
        padding-top: 35px;
        padding-bottom: 60px;
    }

    /* Sidebar */

    section[data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e5e7eb;
    }

    section[data-testid="stSidebar"] * {
        color: #111827 !important;
    }

    /* Hero */

    .hero {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 22px;
        padding: 35px;
        margin-bottom: 25px;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.05);
    }

    .hero h1 {
        margin: 0;
        color: #111827;
        font-size: 42px;
        font-weight: 800;
        letter-spacing: -1px;
    }

    .hero p {
        color: #6b7280;
        font-size: 16px;
        margin-top: 10px;
        margin-bottom: 0;
    }

    /* Cards */

    .card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        padding: 25px;
        margin-bottom: 18px;
        box-shadow: 0 6px 25px rgba(0, 0, 0, 0.04);
    }

    /* Section headers */

    .section-title {
        color: #111827;
        font-size: 21px;
        font-weight: 800;
        margin-top: 25px;
        margin-bottom: 15px;
    }

    /* Text */

    h1, h2, h3, h4 {
        color: #111827 !important;
    }

    p, label, span {
        color: #374151;
    }

    /* Inputs */

    div[data-baseweb="input"] > div,
    div[data-baseweb="textarea"] > div,
    div[data-baseweb="select"] > div {
        background: #ffffff !important;
        border-color: #d1d5db !important;
        border-radius: 10px !important;
    }

    input,
    textarea {
        color: #111827 !important;
        background: #ffffff !important;
    }

    /* Buttons */

    div.stButton > button,
    div.stLinkButton > a {
        border-radius: 11px !important;
        font-weight: 700 !important;
        min-height: 45px;
    }

    div.stButton > button {
        background: #111827 !important;
        color: #ffffff !important;
        border: none !important;
    }

    div.stButton > button:hover {
        background: #374151 !important;
    }

    div.stLinkButton > a {
        background: #5865F2 !important;
        color: #ffffff !important;
        border: none !important;
    }

    /* Status badges */

    .status {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 700;
    }

    .status-pending {
        background: #fef3c7;
        color: #92400e !important;
    }

    .status-review {
        background: #dbeafe;
        color: #1d4ed8 !important;
    }

    .status-approved {
        background: #dcfce7;
        color: #166534 !important;
    }

    .status-rejected {
        background: #fee2e2;
        color: #991b1b !important;
    }

    /* Metrics */

    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 15px;
        padding: 15px;
        box-shadow: 0 5px 20px rgba(0,0,0,.04);
    }

    /* Expander */

    div[data-testid="stExpander"] {
        border: 1px solid #e5e7eb !important;
        border-radius: 15px !important;
        background: #ffffff !important;
        margin-bottom: 12px;
    }

    /* Divider */

    hr {
        border-color: #e5e7eb !important;
    }

    /* Footer */

    .footer {
        text-align: center;
        color: #9ca3af;
        font-size: 13px;
        margin-top: 50px;
        padding-top: 20px;
        border-top: 1px solid #e5e7eb;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# DATABASE FUNCTIONS
# =========================================================

def insert_application(data):
    result = (
        supabase
        .table("applications")
        .insert(data)
        .execute()
    )

    return result.data[0] if result.data else None


def get_applications():
    result = (
        supabase
        .table("applications")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )

    return result.data or []


def update_application(app_id, values):
    return (
        supabase
        .table("applications")
        .update(values)
        .eq("id", app_id)
        .execute()
    )


def verify_password(password):
    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            ADMIN_PASSWORD_HASH.encode("utf-8")
        )
    except Exception:
        return False


def status_badge(status):

    classes = {
        "Pending": "status-pending",
        "Under Review": "status-review",
        "Approved": "status-approved",
        "Rejected": "status-rejected",
    }

    css = classes.get(status, "status-review")

    return (
        f'<span class="status {css}">'
        f'{status}'
        f'</span>'
    )


# =========================================================
# SESSION
# =========================================================

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("## 🦊 FOXMC")

    st.caption("Official Staff Recruitment")

    st.divider()

    page = st.radio(
        "Navigation",
        [
            "📝 Staff Application",
            "💬 Join Discord",
            "🔐 Admin Panel"
        ]
    )

    st.divider()

    st.caption("FOXMC Staff Recruitment System")


# =========================================================
# STAFF APPLICATION
# =========================================================

if page == "📝 Staff Application":

    st.markdown(
        """
        <div class="hero">

            <h1>FOXMC Staff Application</h1>

            <p>
                Want to become part of the FOXMC Staff Team?
                Complete the application below carefully and honestly.
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.link_button(
        "💬 Join FOXMC Discord",
        DISCORD_URL,
        use_container_width=True
    )

    st.markdown(
        """
        <div class="card">

        <h2>📝 FILL THIS FORM</h2>

        <p>
        Please answer all questions honestly.
        The application should take approximately
        <b>10–15 minutes maximum</b>.
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )


    with st.form(
        "foxmc_staff_application",
        clear_on_submit=False
    ):

        # =================================================
        # 1 BASIC INFORMATION
        # =================================================

        st.markdown(
            '<div class="section-title">1. Basic Information</div>',
            unsafe_allow_html=True
        )

        discord = st.text_input(
            "I. Discord Username *",
            placeholder="Example: username"
        )

        minecraft = st.text_input(
            "II. Minecraft Username *",
            placeholder="Example: Steve123"
        )

        age = st.number_input(
            "III. Age *",
            min_value=13,
            max_value=100,
            value=16
        )

        timezone_name = st.text_input(
            "IV. Country / Timezone *",
            placeholder="Example: Pakistan / UTC+5"
        )


        st.divider()


        # =================================================
        # 2 STAFF EXPERIENCE
        # =================================================

        st.markdown(
            '<div class="section-title">2. Staff Experience</div>',
            unsafe_allow_html=True
        )

        position = st.selectbox(
            "I. Which position are you applying for? *",
            [
                "Moderator",
                "Trial Moderator",
                "Helper",
                "Support",
                "Builder",
                "Event Team",
                "Other"
            ]
        )

        previous_experience = st.radio(
            "II. Do you have any previous staff experience? *",
            ["Yes", "No"],
            horizontal=True
        )

        experience = st.text_area(
            "III. If yes, briefly describe your experience :",
            placeholder=(
                "Tell us about your previous staff experience. "
                "If you have none, write N/A."
            ),
            height=130
        )


        st.divider()


        # =================================================
        # 3 ABOUT YOU
        # =================================================

        st.markdown(
            '<div class="section-title">3. About You</div>',
            unsafe_allow_html=True
        )

        why_us = st.text_area(
            "I. Why do you want to join the FOXMC Staff Team? *",
            height=140
        )

        why_choose = st.text_area(
            "II. Why should we choose you? *",
            height=140
        )

        activity = st.text_area(
            "III. How active can you be on FOXMC? *",
            placeholder=(
                "Tell us how often you can play/be active "
                "on the server and Discord."
            ),
            height=120
        )


        st.divider()


        # =================================================
        # 4 SITUATIONAL QUESTIONS
        # =================================================

        st.markdown(
            '<div class="section-title">4. Situational Questions</div>',
            unsafe_allow_html=True
        )

        scenario_rule = st.text_area(
            "I. A player repeatedly breaks the rules after being warned. What would you do? *",
            height=160
        )

        scenario_friend = st.text_area(
            "II. What would you do if your friend broke a server rule? *",
            height=160
        )


        st.divider()


        # =================================================
        # 5 FINAL
        # =================================================

        st.markdown(
            '<div class="section-title">5. Final</div>',
            unsafe_allow_html=True
        )

        agree = st.radio(
            "I. Do you agree to follow all FOXMC rules and staff guidelines? *",
            ["Yes", "No"],
            horizontal=True
        )

        anything_else = st.text_area(
            "II. Is there anything else you would like to tell us?",
            height=130
        )


        st.divider()


        confirm = st.checkbox(
            "I confirm that all information provided is honest and accurate."
        )


        submitted = st.form_submit_button(
            "🚀 SUBMIT APPLICATION",
            use_container_width=True
        )


    # =====================================================
    # PROCESS APPLICATION
    # =====================================================

    if submitted:

        required = [
            discord.strip(),
            minecraft.strip(),
            timezone_name.strip(),
            experience.strip(),
            why_us.strip(),
            why_choose.strip(),
            activity.strip(),
            scenario_rule.strip(),
            scenario_friend.strip()
        ]

        if not all(required):

            st.error(
                "❌ Please answer all required questions."
            )

        elif agree != "Yes":

            st.error(
                "❌ You must agree to follow FOXMC rules and staff guidelines."
            )

        elif not confirm:

            st.error(
                "❌ Please confirm that your information is honest."
            )

        else:

            application_id = (
                "FOX-"
                + uuid.uuid4().hex[:8].upper()
            )

            data = {

                "application_id": application_id,

                "name": minecraft.strip(),

                "discord": discord.strip(),

                "age": int(age),

                "minecraft": minecraft.strip(),

                "timezone": timezone_name.strip(),

                "position": position,

                "previous_staff_experience":
                    previous_experience,

                "experience":
                    experience.strip(),

                "why_us":
                    why_us.strip(),

                "strengths":
                    why_choose.strip(),

                "activity":
                    activity.strip(),

                "scenario":
                    (
                        "Player repeatedly breaking rules:\n"
                        + scenario_rule.strip()
                        + "\n\n"
                        + "Friend breaking a rule:\n"
                        + scenario_friend.strip()
                    ),

                "agreed_to_rules":
                    agree,

                "anything_else":
                    anything_else.strip(),

                "status":
                    "Pending",

                "admin_notes":
                    "",

                "created_at":
                    datetime.now(timezone.utc).isoformat(),

            }


            try:

                saved = insert_application(data)

                if saved:

                    st.success(
                        "✅ Application submitted successfully!"
                    )

                    st.markdown(
                        f"""
                        <div class="card">

                        <h3>Application Submitted 🎉</h3>

                        <p>
                        Your FOXMC application has been received.
                        </p>

                        <p>
                        <b>Application ID:</b>
                        </p>

                        <h2>{application_id}</h2>

                        <p>
                        Please save this ID for future reference.
                        </p>

                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                else:

                    st.error(
                        "The application could not be saved."
                    )

            except Exception as e:

                st.error(
                    "Database error. Please try again."
                )

                st.caption(str(e))


# =========================================================
# DISCORD
# =========================================================

elif page == "💬 Join Discord":

    st.markdown(
        """
        <div class="hero">

            <h1>Join FOXMC Discord</h1>

            <p>
                Join the official FOXMC Discord community
                for announcements, support and staff updates.
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )


    st.link_button(
        "💬 JOIN FOXMC DISCORD",
        DISCORD_URL,
        use_container_width=True
    )


    st.markdown(
        """
        <div class="card">

        <h2>Why join our Discord?</h2>

        <p>📢 Server announcements</p>
        <p>🎮 Community events</p>
        <p>🛡️ Staff recruitment updates</p>
        <p>💬 Community support</p>
        <p>👥 Meet other FOXMC players</p>

        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# ADMIN PANEL
# =========================================================

else:

    # =====================================================
    # LOGIN
    # =====================================================

    if not st.session_state.admin_logged_in:

        st.markdown(
            """
            <div class="hero">

                <h1>🔐 Admin Panel</h1>

                <p>
                    Authorized FOXMC staff members only.
                    Sign in to review applications.
                </p>

            </div>
            """,
            unsafe_allow_html=True
        )


        if not ADMIN_PASSWORD_HASH:

            st.error(
                "ADMIN_PASSWORD_HASH is not configured."
            )

            st.stop()


        with st.form("admin_login"):

            username = st.text_input(
                "Admin Username"
            )

            password = st.text_input(
                "Admin Password",
                type="password"
            )

            login = st.form_submit_button(
                "🔐 SIGN IN",
                use_container_width=True
            )


        if login:

            if (
                username == ADMIN_USERNAME
                and verify_password(password)
            ):

                st.session_state.admin_logged_in = True

                st.rerun()

            else:

                st.error(
                    "❌ Invalid admin username or password."
                )


        st.stop()


    # =====================================================
    # DASHBOARD
    # =====================================================

    st.markdown(
        """
        <div class="hero">

            <h1>FOXMC Admin Dashboard</h1>

            <p>
                Review and manage all staff applications.
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )


    col1, col2 = st.columns(
        [5, 1]
    )


    with col1:

        st.success(
            "🟢 Administrator authenticated"
        )


    with col2:

        if st.button(
            "Log Out",
            use_container_width=True
        ):

            st.session_state.admin_logged_in = False

            st.rerun()


    # =====================================================
    # GET APPLICATIONS
    # =====================================================

    try:

        applications = get_applications()

    except Exception as e:

        st.error(
            "Could not load applications."
        )

        st.caption(str(e))

        st.stop()


    df = pd.DataFrame(applications)


    if df.empty:

        st.info(
            "📭 No applications have been submitted yet."
        )

        st.stop()


    # =====================================================
    # STATISTICS
    # =====================================================

    statuses = (
        df["status"]
        .fillna("Pending")
    )


    c1, c2, c3, c4 = st.columns(4)


    c1.metric(
        "Total Applications",
        len(df)
    )

    c2.metric(
        "Pending",
        int(
            (statuses == "Pending").sum()
        )
    )

    c3.metric(
        "Approved",
        int(
            (statuses == "Approved").sum()
        )
    )

    c4.metric(
        "Rejected",
        int(
            (statuses == "Rejected").sum()
        )
    )


    st.divider()


    # =====================================================
    # FILTERS
    # =====================================================

    f1, f2 = st.columns(
        [2, 3]
    )


    with f1:

        filter_status = st.selectbox(
            "Filter by Status",
            [
                "All",
                "Pending",
                "Under Review",
                "Approved",
                "Rejected"
            ]
        )


    with f2:

        search = st.text_input(
            "Search Applications",
            placeholder=(
                "Name, Discord, Minecraft username or Application ID"
            )
        )


    filtered = df.copy()


    if filter_status != "All":

        filtered = filtered[
            filtered["status"]
            == filter_status
        ]


    if search.strip():

        q = search.strip().lower()

        filtered = filtered[
            filtered.apply(
                lambda row:
                    q in str(
                        row.get(
                            "name",
                            ""
                        )
                    ).lower()
                    or q in str(
                        row.get(
                            "discord",
                            ""
                        )
                    ).lower()
                    or q in str(
                        row.get(
                            "minecraft",
                            ""
                        )
                    ).lower()
                    or q in str(
                        row.get(
                            "application_id",
                            ""
                        )
                    ).lower(),
                axis=1
            )
        ]


    st.markdown(
        f"### Applications ({len(filtered)})"
    )


    # =====================================================
    # APPLICATION CARDS
    # =====================================================

    for _, row in filtered.iterrows():

        app_id = row["id"]

        application_number = row.get(
            "application_id",
            "Unknown"
        )

        applicant_name = row.get(
            "name",
            "Unknown"
        )

        discord_name = row.get(
            "discord",
            ""
        )


        title = (
            f"{application_number}  •  "
            f"{applicant_name}  •  "
            f"{discord_name}"
        )


        with st.expander(title):

            left, right = st.columns(
                [2.2, 1]
            )


            # =============================================
            # APPLICATION DETAILS
            # =============================================

            with left:

                current_status = (
                    row.get(
                        "status",
                        "Pending"
                    )
                )


                st.markdown(
                    f"""
                    **Status:**  
                    {status_badge(current_status)}
                    """,
                    unsafe_allow_html=True
                )


                st.markdown("### Basic Information")

                st.write(
                    f"**Discord:** "
                    f"{row.get('discord', 'N/A')}"
                )

                st.write(
                    f"**Minecraft:** "
                    f"{row.get('minecraft', 'N/A')}"
                )

                st.write(
                    f"**Age:** "
                    f"{row.get('age', 'N/A')}"
                )

                st.write(
                    f"**Country / Timezone:** "
                    f"{row.get('timezone', 'N/A')}"
                )


                st.markdown(
                    "### Staff Experience"
                )

                st.write(
                    f"**Position:** "
                    f"{row.get('position', 'N/A')}"
                )

                st.write(
                    f"**Previous Experience:** "
                    f"{row.get('previous_staff_experience', 'N/A')}"
                )

                st.markdown(
                    "**Experience Description:**"
                )

                st.write(
                    row.get(
                        "experience",
                        "N/A"
                    )
                )


                st.markdown(
                    "### About You"
                )

                st.markdown(
                    "**Why do you want to join FOXMC?**"
                )

                st.write(
                    row.get(
                        "why_us",
                        "N/A"
                    )
                )


                st.markdown(
                    "**Why should we choose you?**"
                )

                st.write(
                    row.get(
                        "strengths",
                        "N/A"
                    )
                )


                st.markdown(
                    "**Activity:**"
                )

                st.write(
                    row.get(
                        "activity",
                        "N/A"
                    )
                )


                st.markdown(
                    "### Situational Questions"
                )

                scenario_text = row.get(
                    "scenario",
                    "N/A"
                )

                st.write(
                    scenario_text
                )


                st.markdown(
                    "### Final"
                )

                st.write(
                    f"**Agreed to FOXMC rules:** "
                    f"{row.get('agreed_to_rules', 'N/A')}"
                )

                st.markdown(
                    "**Additional Information:**"
                )

                st.write(
                    row.get(
                        "anything_else",
                        "N/A"
                    )
                )


            # =============================================
            # ADMIN CONTROLS
            # =============================================

            with right:

                st.markdown(
                    "### Application Management"
                )


                statuses_list = [
                    "Pending",
                    "Under Review",
                    "Approved",
                    "Rejected"
                ]


                current_index = (
                    statuses_list.index(
                        current_status
                    )
                    if current_status
                    in statuses_list
                    else 0
                )


                new_status = st.selectbox(
                    "Application Status",
                    statuses_list,
                    index=current_index,
                    key=f"status_{app_id}"
                )


                notes = st.text_area(
                    "Private Admin Notes",
                    value=row.get(
                        "admin_notes",
                        ""
                    ) or "",
                    height=180,
                    key=f"notes_{app_id}"
                )


                if st.button(
                    "💾 SAVE CHANGES",
                    key=f"save_{app_id}",
                    use_container_width=True
                ):

                    try:

                        update_application(
                            app_id,
                            {
                                "status":
                                    new_status,

                                "admin_notes":
                                    notes
                            }
                        )

                        st.success(
                            "Application updated!"
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(
                            "Could not update application."
                        )

                        st.caption(str(e))


            st.caption(
                "Submitted: "
                + str(
                    row.get(
                        "created_at",
                        "Unknown"
                    )
                )
            )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">
        © FOXMC • Staff Recruitment System
    </div>
    """,
    unsafe_allow_html=True
)
