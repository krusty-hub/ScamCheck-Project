import streamlit as st
from detector import check_message

# 1. Page Configuration
st.set_page_config(
    page_title="ScamCheck | Threat Analysis",
    page_icon="🛡️",
    layout="centered"
)

# 2. Custom CSS for Background and UI Styling
st.markdown("""
    <style>
    /* Main App Background */
    .stApp {
        background-color: #0f172a; /* Deep navy/slate background */
        color: #f8fafc;
    }

    /* Target main container width & spacing */
    .block-container {
        padding-top: 3rem;
        padding-bottom: 3rem;
    }

    /* Headings and Body text color override */
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown {
        color: #f8fafc !important;
    }

    /* Text Area Container Styling */
    .stTextArea textarea {
        background-color: #1e293b !important;
        color: #f8fafc !important;
        border: 1px solid #334155 !important;
        border-radius: 8px;
    }
    .stTextArea textarea:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 1px #3b82f6 !important;
    }
        

    /* Custom Primary Button Styling */
    div.stButton > button {
        width: 100%;
        background-color: #2563eb;
        color: #ffffff !important;
        font-weight: 600;
        font-size: 1rem;
        border-radius: 8px;
        border: none;
        padding: 0.6rem 1rem;
        transition: all 0.2s ease-in-out;
    }
    div.stButton > button:hover {
        background-color: #1d4ed8;
        color: #ffffff !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
    }

    /* Style Streamlit Metric Cards */
    [data-testid="stMetric"] {
        background-color: #1e293b;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #334155;
    }
    [data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
    }
    [data-testid="stMetricValue"] {
        color: #f8fafc !important;
    }
    </style>
""", unsafe_allow_html=True)

def show_warning_yellow(message):
    st.markdown(
        f"""
        <div style="
            background-color: #e6e84f;
            color: #543737;
            padding: 1rem;
            border-radius: 8px;
            font-weight: 600;
        ">
            ⚠️ {message}
        </div>
        """,
        unsafe_allow_html=True
    )

def show_warning_red(message):
        st.markdown(
        f"""
        <div style="
            background-color: #b52121;
            color: #debdbd;
            padding: 1rem;
            border-radius: 8px;
            font-weight: 600;
        ">
            💀 {message}
        </div>
        """,
        unsafe_allow_html=True
    )
# 3. App Header
st.title("🛡️ ScamCheck")
st.caption("Enterprise Message Safety & Phishing Detector")
st.markdown("---")

# 4. Main Interface
st.subheader("Analyze Message")
st.write("Paste an unknown text message, email snippet, or link below to run a security risk assessment.")

user_text = st.text_area(
    label="Message Content",
    placeholder="e.g., 'URGENT: Your bank account has been locked. Click here to verify...'",
    height=140,
    label_visibility="collapsed"
)

is_clicked = st.button("🔍 Scan Message for Threats")

# 5. Result Logic & Display
if is_clicked:
    if not user_text.strip():
        st.warning("⚠️ **Input Required:** Please enter a message before running the scan.")
    else:
        with st.spinner("Analyzing message indicators..."):
            result = check_message(user_text)

        st.markdown("---")
        st.subheader("Analysis Summary")
        
        # Display Results in Structured Columns
        col1, col2 = st.columns([1, 1])
        
        level = result.get("level", "GREEN")
        score = result.get("score", 0)

        # Config map for dynamic UI status badges
        status_config = {
            "GREEN": {
                "label": "Low Risk / Safe",
                "banner": st.success,
                "msg": "No significant threat indicators detected."
            },
            "YELLOW": {
                "label": "Medium Risk",
                "banner": show_warning_yellow,
                "msg": "Suspicious elements detected. Proceed with caution."
            },
            "RED": {
                "label": "High Risk / Danger",
                "banner": show_warning_red,
                "msg": "Critical risk indicators detected! Do not click links or share details."
            }
        }

        current_status = status_config.get(level, status_config["GREEN"])

        with col1:
            st.metric(label="Threat Status", value=current_status["label"])
            
        with col2:
            st.metric(label="Risk Score", value=f"{score}/100")

        # Status Alert Banner
        current_status["banner"](current_status["msg"])

        # Reasons Breakdown
        reasons = result.get("reasons", [])
        if reasons:
            st.markdown("### ⚠️ Flagged Indicators")
            for reason in reasons:
                st.markdown(f"- {reason}")
        else:
            st.info("No suspicious patterns or blacklist triggers matched.")

# 6. Footer
st.divider()


st.caption(
    "🔒 **ScamCheck Engine v1.0** — Rule-Based Detection | Built by the SIWES Python Engineering Team"
)

