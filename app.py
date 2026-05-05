import streamlit as st
import pandas as pd
import joblib
import plotly.express as px
import plotly.graph_objects as go
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import random
import string
import base64
import io
import time
import streamlit.components.v1 as components
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

try:
    from st_keyup import st_keyup
    KEYUP_AVAILABLE = True
except ImportError:
    KEYUP_AVAILABLE = False

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# ==========================================
# PAGE SETUP & BRANDING THEME
# ==========================================
st.set_page_config(page_title="Bank Churn Sentinel", page_icon="🏦", layout="wide", initial_sidebar_state="collapsed")

def apply_enterprise_theme():
    theme_css = """
    <style>
        /* Base Animations */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes slideUp {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* 🚀 SCI-FI ANIMATIONS 🚀 */
        @keyframes float {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-8px); }
            100% { transform: translateY(0px); }
        }
        @keyframes pulseGlow {
            0% { box-shadow: 0 0 5px rgba(0, 230, 118, 0.4); }
            50% { box-shadow: 0 0 20px rgba(0, 230, 118, 0.8), 0 0 30px rgba(30, 58, 138, 0.6); }
            100% { box-shadow: 0 0 5px rgba(0, 230, 118, 0.4); }
        }
        @keyframes borderFlow {
            0% { background-position: 0% 0%; }
            50% { background-position: 0% 100%; }
            100% { background-position: 0% 0%; }
        }
        
        /* 🌟 DYNAMIC SUBTITLE & AUTH TEXT ANIMATION 🌟 */
        @keyframes textReveal {
            0% { opacity: 0; transform: translateY(15px); filter: blur(5px); }
            100% { opacity: 1; transform: translateY(0); filter: blur(0); }
        }
        @keyframes textGlowPulse {
            0% { text-shadow: 0 0 10px rgba(0, 230, 118, 0.2); }
            50% { text-shadow: 0 0 25px rgba(0, 230, 118, 0.8), 0 0 15px rgba(255, 255, 255, 0.5); }
            100% { text-shadow: 0 0 10px rgba(0, 230, 118, 0.2); }
        }
        
        /* 🌟 EXTERNAL GLOW EFFECT FOR CARDS 🌟 */
        @keyframes activeCardGlow {
            0% { box-shadow: 0 0 10px rgba(0, 230, 118, 0.3); }
            50% { box-shadow: 0 0 20px rgba(0, 230, 118, 0.7), 0 0 10px rgba(255, 255, 255, 0.2); }
            100% { box-shadow: 0 0 10px rgba(0, 230, 118, 0.3); }
        }

        .stApp { animation: fadeIn 0.8s ease-out; }

        /* 🌟 GLOBAL TEXT ENHANCEMENTS (Making everything bigger) 🌟 */
        [data-testid="stMarkdownContainer"] p {
            font-size: 1.15rem !important;
            line-height: 1.6 !important;
        }
        [data-testid="stMarkdownContainer"] h3 {
            font-size: 1.75rem !important;
        }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
            font-size: 1.1rem !important;
        }

        /* General Container Cards */
        .sentinel-card {
            background: linear-gradient(145deg, #161A23 0%, #0D1017 100%);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 20px;
            border: 1px solid #2A303C;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
            animation: slideUp 0.6s ease-out forwards;
            transition: all 0.3s ease;
        }
        .sentinel-card:hover { transform: translateY(-3px); border-color: #00E676; box-shadow: 0 8px 25px rgba(0, 230, 118, 0.1); }
        
        .card-title { color: #00E676; font-size: 1.45rem; font-weight: 600; margin-bottom: 12px; display: flex; align-items: center; gap: 10px; }
        .card-text { color: #A5B1C2; font-size: 1.15rem; line-height: 1.6; }

        /* Dashboard KPI Cards (Tab 2) */
        .dashboard-kpi {
            background: rgba(22, 26, 35, 0.5);
            backdrop-filter: blur(5px);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            padding: 15px;
            text-align: center;
        }
        .dashboard-kpi-val { color: #FFFFFF; font-size: 2.1rem; font-weight: bold; margin-bottom: 5px; }
        .dashboard-kpi-lab { color: #8b949e; font-size: 0.95rem; text-transform: uppercase; letter-spacing: 1px; }

        /* --------------------------------------------------- */
        /* 🚀 3D SCI-FI HOME PAGE STYLES 🚀                    */
        /* --------------------------------------------------- */
        
        .hero-badge {
            display: inline-block;
            background-color: rgba(34, 197, 94, 0.1);
            color: #22c55e;
            padding: 8px 18px;
            border-radius: 20px;
            font-size: 0.95rem;
            font-weight: 600;
            border: 1px solid rgba(34, 197, 94, 0.5);
            margin-bottom: 20px;
            letter-spacing: 1px;
            animation: pulseGlow 2.5s infinite; 
        }
        
        .hero-title { 
            color: #FFFFFF; 
            font-size: 4.8rem; 
            font-weight: 800; 
            line-height: 1.1; 
            margin-bottom: 20px;
            text-shadow: 0 0 25px rgba(0, 230, 118, 0.2); 
        }
        
        .dynamic-subtitle { 
            color: #A5B1C2; 
            font-size: 1.3rem; 
            line-height: 1.6; 
            margin-bottom: 40px; 
            max-width: 90%; 
            opacity: 0;
            animation: textReveal 1.2s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
            animation-delay: 0.4s;
        }
        
        /* 3D Floating Stat Boxes */
        .stat-box {
            background: rgba(22, 26, 35, 0.5);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(0, 230, 118, 0.1);
            border-radius: 16px;
            padding: 25px;
            text-align: center;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); 
            position: relative;
            overflow: hidden;
            animation: float 6s ease-in-out infinite;
        }
        .stat-box:nth-child(1) { animation-delay: 0s; }
        .stat-box:nth-child(2) { animation-delay: 1.5s; }
        .stat-box:nth-child(3) { animation-delay: 0.7s; }
        .stat-box:nth-child(4) { animation-delay: 2.2s; }

        .stat-box:hover { 
            transform: translateY(-12px) scale(1.05) !important; 
            background: rgba(22, 26, 35, 0.8); 
            border: 1px solid rgba(0, 230, 118, 0.8); 
            box-shadow: 0 15px 35px rgba(0, 230, 118, 0.25), inset 0 0 20px rgba(0, 230, 118, 0.15); 
            z-index: 10;
        }
        .stat-icon { font-size: 2.8rem; margin-bottom: 10px; text-shadow: 0 0 15px rgba(255,255,255,0.5); }
        .stat-value { color: #FFFFFF; font-size: 1.7rem; font-weight: bold; margin-bottom: 5px; }
        .stat-label { color: #00E676; font-size: 1rem; text-transform: uppercase; letter-spacing: 1px; }
        
        /* Sci-Fi Feature Cards */
        .feature-card {
            background: rgba(13, 16, 23, 0.7);
            padding: 25px;
            border-radius: 0 12px 12px 0;
            height: 100%;
            position: relative;
            transition: all 0.3s ease;
            box-shadow: inset 1px 0 0px rgba(0, 230, 118, 0.1);
        }
        .feature-card::before {
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 4px;
            background: linear-gradient(180deg, #00E676, #1e3a8a, #00E676);
            background-size: 200% 200%;
            animation: borderFlow 3s ease infinite;
            box-shadow: 0 0 8px rgba(0, 230, 118, 0.4);
            transition: all 0.3s ease;
        }
        .feature-card:hover {
            transform: translateX(10px); 
            background: rgba(20, 26, 38, 0.9);
            box-shadow: -5px 0 25px rgba(0, 230, 118, 0.15);
        }
        .feature-card:hover::before {
            width: 6px; 
            box-shadow: 0 0 20px #00E676, 0 0 40px #1e3a8a; 
            background: #00E676;
        }
        .feature-title { color: #FFFFFF; font-size: 1.45rem; font-weight: bold; margin-bottom: 15px; display:flex; align-items: center; gap:8px;}
        .feature-text { color: #8b949e; font-size: 1.1rem; line-height: 1.5; }

        /* 🌟 ENHANCED TYPOGRAPHY FOR INPUTS, TABS AND BUTTONS 🌟 */
        [data-testid="stTabs"] button div[data-testid="stMarkdownContainer"] p {
            font-size: 1.25rem !important;
            font-weight: bold !important;
        }
        [data-testid="stTextInput"] label p, [data-testid="stSelectbox"] label p, [data-testid="stNumberInput"] label p, [data-testid="stRadio"] label p, .stSlider label p {
            font-size: 1.15rem !important;
            font-weight: 600 !important;
            color: #E2E8F0 !important;
        }
        [data-testid="stButton"] button p {
            font-size: 1.2rem !important;
            font-weight: 600 !important;
        }
        .stButton>button { transition: all 0.2s ease; border-radius: 8px; padding: 10px 0;}
        .stButton>button:hover { box-shadow: 0 0 15px rgba(0, 230, 118, 0.4); }
        .stButton>button:active { transform: scale(0.96); }
        
        /* 🌟 AUTH PAGE DYNAMIC STYLING 🌟 */
        .auth-dynamic-title {
            text-align: center;
            font-size: 2.8rem;
            font-weight: 800;
            color: #FFFFFF;
            margin-bottom: 10px;
            animation: textGlowPulse 3s infinite ease-in-out;
        }
        .auth-dynamic-subtitle {
            text-align: center;
            color: #A5B1C2;
            font-size: 1.2rem;
            line-height: 1.6;
            margin-bottom: 30px;
            opacity: 0;
            animation: textReveal 1s ease-out forwards;
            animation-delay: 0.2s;
        }
        .auth-container {
            background: rgba(22, 26, 35, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 40px;
            margin-top: 20px;
            max-width: 600px;
            margin-left: auto;
            margin-right: auto;
        }
        
        /* 🌟 APPLYING THE NEW GLOW TO ACTIVE CARDS/COMPONENTS 🌟 */
        .active-analytical-area {
            animation: activeCardGlow 3s infinite;
            border: 1px solid rgba(0, 230, 118, 0.6) !important;
        }

        /* 🌟 APPLY GLOW DIRECTLY TO PLOTLY CHARTS (FIXED SCROLLBAR) 🌟 */
        div[data-testid="stPlotlyChart"] {
            background: linear-gradient(145deg, #161A23 0%, #0D1017 100%);
            border-radius: 12px;
            padding: 15px;
            border: 1px solid rgba(0, 230, 118, 0.3);
            animation: activeCardGlow 3s infinite;
            margin-bottom: 20px;
            overflow: hidden !important; /* Removes the ugly scrollbar */
        }

        /* 🌟 TAB 2 CARD VISUALIZATIONS 🌟 */
        .comp-card {
            background: rgba(22, 26, 35, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            padding: 15px;
            text-align: center;
            transition: transform 0.2s ease;
        }
        .comp-card:hover { transform: translateY(-3px); border-color: #00E676; }
        .comp-title { color: #A5B1C2; font-size: 1.05rem; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 8px; margin-bottom: 10px; font-weight: bold;}
        .comp-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
        .comp-val-cust { color: #00E676; font-size: 1.6rem; font-weight: bold; }
        .comp-val-bank { color: #8b949e; font-size: 1.6rem; font-weight: bold; }
        .comp-label { font-size: 0.85rem; color: #6e7681; text-transform: uppercase; letter-spacing: 0.5px;}
        
        .demo-card {
            background: rgba(22, 26, 35, 0.6);
            border-left: 4px solid #00E676;
            border-radius: 8px;
            padding: 15px 20px;
            transition: transform 0.2s ease;
        }
        .demo-card:hover { transform: translateX(5px); background: rgba(20, 26, 38, 0.8); }
        .demo-title { display: flex; align-items: center; gap: 10px; color: #FFFFFF; font-size: 1.25rem; font-weight: 600; margin-bottom: 10px;}
        .demo-val { color: #00E676; font-size: 2.0rem; font-weight: bold; margin-bottom: 5px; }
        .demo-pct { color: #A5B1C2; font-size: 1.05rem; }

    </style>
    """
    st.markdown(theme_css, unsafe_allow_html=True)

apply_enterprise_theme()

# ==========================================
# 🌟 VISIBLE BACKGROUND 🌟
# ==========================================
def apply_bg_img(img_file):
    try:
        with open(img_file, 'rb') as f:
            data = f.read()
        bin_str = base64.b64encode(data).decode()
        page_bg_img = f'''
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(10, 14, 23, 0.3), rgba(10, 14, 23, 0.5)), url("data:image/png;base64,{bin_str}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        [data-testid="stSidebar"], [data-testid="stSidebar"] > div:first-child {{
            background-color: transparent !important;
            border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
        }}
        [data-testid="stHeader"] {{ background-color: transparent !important; }}
        </style>
        '''
        st.markdown(page_bg_img, unsafe_allow_html=True)
    except FileNotFoundError:
        pass 

apply_bg_img('background.png')

# ==========================================
# SESSION SECURITY & AUTO-LOGOUT
# ==========================================
INACTIVITY_TIMEOUT = 600 

if 'show_login' not in st.session_state:
    st.session_state['show_login'] = False  
if 'last_active' not in st.session_state:
    st.session_state['last_active'] = time.time()
if 'officer_logged_in' not in st.session_state:
    st.session_state['officer_logged_in'] = False
if 'customer_ready' not in st.session_state:
    st.session_state['customer_ready'] = False
if 'cust_data' not in st.session_state:
    st.session_state['cust_data'] = {}
if 'auto_fill_acc' not in st.session_state:
    st.session_state['auto_fill_acc'] = ""
if 'user' not in st.session_state:
    st.session_state['user'] = "Authorized Officer"
if 'prob_calculated' not in st.session_state:
    st.session_state['prob_calculated'] = False
if 'current_prob' not in st.session_state:
    st.session_state['current_prob'] = 0.0

if st.query_params.get("session") == "active":
    st.session_state['officer_logged_in'] = True

if st.session_state['officer_logged_in']:
    if time.time() - st.session_state['last_active'] > INACTIVITY_TIMEOUT:
        st.session_state.clear()
        st.query_params.clear()
        st.warning("🔒 Session expired due to 10 minutes of inactivity. Please log in again to secure data.")
        st.stop()
    else:
        st.session_state['last_active'] = time.time()

# ==========================================
# CORE HIGH-PERFORMANCE CACHING
# ==========================================
@st.cache_resource
def load_assets():
    model = joblib.load('model.pkl')
    scaler = joblib.load('scaler.pkl')
    return model, scaler

@st.cache_data(ttl=600)
def load_google_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    workbook = client.open("Bank_Churn_Database")
    sheet_list = workbook.worksheet("Customer_List")
    sheet_data = workbook.worksheet("Customer_Data")
    
    try:
        sheet_officers = workbook.worksheet("Officer_DB")
        df_officers = pd.DataFrame(sheet_officers.get_all_records())
    except Exception:
        df_officers = pd.DataFrame(columns=['Officer ID', 'Security Key', 'Name', 'Designation', 'Branch'])
    
    df_list = pd.DataFrame(sheet_list.get_all_records())
    df_data = pd.DataFrame(sheet_data.get_all_records())
    return df_list, df_data, df_officers

try:
    df_cust_list, df_cust_data, df_officers = load_google_sheet()
    db_connected = True
except Exception as e:
    st.error(f"Database Connection Error: Ensure 'credentials.json' is present. {e}")
    db_connected = False

# ==========================================
# PDF GENERATOR UTIL
# ==========================================
def create_pdf_report(officer, cust_name, acc_num, branch, prob, rec_list):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    c.setStrokeColor(colors.HexColor("#1e3a8a"))
    c.setLineWidth(3)
    c.rect(20, 20, width - 40, height - 40)
    c.saveState()
    c.setFont("Helvetica-Bold", 50)
    c.setFillColorRGB(0.8, 0.8, 0.8, alpha=0.15)
    c.translate(width/2, height/2)
    c.rotate(45)
    c.drawCentredString(0, 0, "BANK CHURN SENTINEL")
    c.restoreState()
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(colors.HexColor("#1e3a8a"))
    c.drawCentredString(width/2, height - 60, "OFFICIAL RISK ASSESSMENT REPORT")
    c.setLineWidth(1)
    c.line(50, height - 70, width - 50, height - 70)
    c.setFont("Helvetica", 12)
    c.setFillColor(colors.black)
    y_pos = height - 110
    c.drawString(50, y_pos, f"Authorized Officer: {officer}")
    y_pos -= 25
    c.drawString(50, y_pos, f"Customer Name: {cust_name}")
    y_pos -= 25
    c.drawString(50, y_pos, f"Account Number: {acc_num}")
    y_pos -= 25
    c.drawString(50, y_pos, f"Branch Name: {branch}")
    y_pos -= 40
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y_pos, "ANALYSIS RESULT:")
    y_pos -= 25
    c.setFont("Helvetica", 12)
    risk_category = "High Risk" if prob > 70 else "Moderate Risk" if prob > 30 else "Low Risk"
    risk_color = colors.red if prob > 70 else colors.orange if prob > 30 else colors.green
    c.drawString(50, y_pos, f"Churn Probability: {prob:.2f}%")
    y_pos -= 25
    c.drawString(50, y_pos, "Risk Category: ")
    c.setFillColor(risk_color)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(140, y_pos, risk_category)
    c.setFillColor(colors.black)
    y_pos -= 40
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y_pos, "RECOMMENDED RETENTION ACTIONS:")
    y_pos -= 25
    c.setFont("Helvetica", 11)
    for line in rec_list:
        c.drawString(60, y_pos, line)
        y_pos -= 20
    c.setFont("Helvetica-Oblique", 9)
    c.setFillColor(colors.gray)
    c.drawCentredString(width/2, 40, "System Generated Report - Confidential & Proprietary")
    c.save()
    buffer.seek(0)
    return buffer

# ==========================================
# HTML ANIMATED GAUGE COMPONENT
# ==========================================
def animated_gauge_html(prob):
    color = "#ef4444" if prob > 70 else "#f97316" if prob > 30 else "#22c55e" 
    shadow = f"drop-shadow(0 0 10px {color})"
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        .flex-wrapper {{ display: flex; justify-content: center; align-items: center; font-family: 'Segoe UI', sans-serif; margin-top: 20px; }}
        .single-chart {{ width: 70%; justify-content: space-around; }}
        .circular-chart {{ display: block; margin: 10px auto; max-width: 80%; max-height: 250px; filter: {shadow}; }}
        .circle-bg {{ fill: none; stroke: #2c3e50; stroke-width: 3.8; }}
        .circle {{ fill: none; stroke-width: 2.8; stroke-linecap: round; transition: stroke-dasharray 2.5s cubic-bezier(0.1, 0.8, 0.2, 1); }}
        .percentage {{ fill: #ffffff; font-size: 0.5em; text-anchor: middle; font-weight: bold; }}
        .label {{ fill: #aaaaaa; font-size: 0.12em; text-anchor: middle; text-transform: uppercase; letter-spacing: 1px; }}
    </style>
    </head>
    <body>
        <div class="flex-wrapper">
            <div class="single-chart">
                <svg viewBox="0 0 36 36" class="circular-chart {color}">
                    <path class="circle-bg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                    <path class="circle" id="dynamic-circle" stroke="{color}" stroke-dasharray="0, 100" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                    <text x="18" y="20.35" class="percentage" id="counter">0%</text>
                    <text x="18" y="25" class="label">Live Risk Score</text>
                </svg>
            </div>
        </div>
        <script>
            setTimeout(() => {{
                document.getElementById('dynamic-circle').setAttribute('stroke-dasharray', '{prob}, 100');
                let count = 0; let target = {prob}; let step = target / 60; if(step === 0) step = 1;
                let interval = setInterval(() => {{
                    count += step;
                    if(count >= target) {{ clearInterval(interval); document.getElementById('counter').innerHTML = target.toFixed(1) + '%'; }} 
                    else {{ document.getElementById('counter').innerHTML = Math.floor(count) + '%'; }}
                }}, 35);
            }}, 200);
        </script>
    </body>
    </html>
    """
    return html_code


# ==========================================
# MAIN APPLICATION ROUTING LOGIC
# ==========================================

if not st.session_state['officer_logged_in']:
    if not st.session_state['show_login']:
        # ------------------------------------
        # 🌟 ORIGINAL HERO HOME PAGE 
        # ------------------------------------
        st.write("<br><br>", unsafe_allow_html=True)
        col_hero_left, col_hero_right = st.columns([1.3, 1], gap="large")
        
        with col_hero_left:
            st.markdown('<div class="hero-badge">🟢 SENTINEL SYSTEM ONLINE</div>', unsafe_allow_html=True)
            st.markdown('<div class="hero-title">Predict. Prevent.<br><span style="color:#00E676;">Retain.</span></div>', unsafe_allow_html=True)
            st.markdown('<div class="dynamic-subtitle">Transform your banking database into actionable foresight. Our machine learning architecture identifies high-risk customers before they churn, allowing you to proactively secure financial relationships.</div>', unsafe_allow_html=True)
            st.write("<br>", unsafe_allow_html=True)
            c_btn1, c_btn2 = st.columns([1, 2])
            with c_btn1:
                if st.button("Launch Portal ➔", use_container_width=True, type="primary"):
                    st.session_state['show_login'] = True
                    st.rerun()
        
        with col_hero_right:
            st.write("<br>", unsafe_allow_html=True)
            st.markdown("""
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <div class="stat-box">
                    <div class="stat-icon">🧠</div>
                    <div class="stat-value">Random Forest</div>
                    <div class="stat-label">Core Engine</div>
                </div>
                <div class="stat-box">
                    <div class="stat-icon">⚡</div>
                    <div class="stat-value">< 1.2s</div>
                    <div class="stat-label">Inference Time</div>
                </div>
                <div class="stat-box">
                    <div class="stat-icon">🛡️</div>
                    <div class="stat-value">AES-256</div>
                    <div class="stat-label">Data Protocol</div>
                </div>
                <div class="stat-box">
                    <div class="stat-icon">📊</div>
                    <div class="stat-value">Real-Time</div>
                    <div class="stat-label">API Sync</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        st.write("<br><br><hr style='border-color: rgba(255,255,255,0.05);'><br>", unsafe_allow_html=True)
        st.markdown('<h3 style="color: #FFFFFF; margin-bottom: 30px;">Core Enterprise Capabilities</h3>', unsafe_allow_html=True)
        
        f1, f2, f3 = st.columns(3)
        with f1:
            st.markdown("""
            <div class="feature-card">
                <div class="feature-title"><span>🎯</span> Dynamic Risk Profiling</div>
                <div class="feature-text">Instantly scan thousands of customer records from Google Workspace. The model evaluates critical variables like age, balance, and product density to generate an accurate churn probability score.</div>
            </div>
            """, unsafe_allow_html=True)
        with f2:
            st.markdown("""
            <div class="feature-card">
                <div class="feature-title"><span>🧪</span> Interactive Sandbox</div>
                <div class="feature-text">Don't just predict; prescribe. Relationship managers can use the 'What-If' simulation tool to toggle financial incentives (like fee waivers) and instantly measure the risk reduction before contacting the client.</div>
            </div>
            """, unsafe_allow_html=True)
        with f3:
            st.markdown("""
            <div class="feature-card">
                <div class="feature-title"><span>📑</span> Automated Reporting</div>
                <div class="feature-text">Generate official, watermarked PDF risk assessments with a single click. Every report includes the predictive score and AI-recommended strategic directives for standardized branch communication.</div>
            </div>
            """, unsafe_allow_html=True)

    else:
        # ------------------------------------
        # 🔐 OFFICER AUTHENTICATION PAGE (CENTERED)
        # ------------------------------------
        col_back, _ = st.columns([1, 8])
        with col_back:
            if st.button("⬅️ Back"): 
                st.session_state['show_login'] = False
                st.rerun()
        
        col_space1, col_auth, col_space2 = st.columns([1, 2.5, 1])
        
        with col_auth:
            st.markdown('<div class="auth-dynamic-title">🏦 Secure Access Portal</div>', unsafe_allow_html=True)
            st.markdown('<div class="auth-dynamic-subtitle">System authentication required. Please verify your officer credentials to establish a secure database connection.</div>', unsafe_allow_html=True)
            
            tab_login, tab_register = st.tabs(["🔐 Officer Login", "📝 Register New Officer"])
            
            with tab_login:
                st.write("<br>", unsafe_allow_html=True)
                # 🌟 BIGGER OFFICER ID LABEL 🌟
                st.markdown("<div style='font-size:1.15rem; font-weight:600; color:#E2E8F0; margin-bottom:5px;'>Officer ID:</div>", unsafe_allow_html=True)
                col_prefix, col_input = st.columns([1, 4])
                # 🌟 BIGGER "OFF -" PREFIX 🌟
                col_prefix.markdown("<div style='margin-top:4px; font-size:24px; font-weight:bold; color:#00E676;'>OFF -</div>", unsafe_allow_html=True)
                id_digits = col_input.text_input("Enter digits", placeholder="1234", max_chars=4, label_visibility="collapsed")
                
                security_key_input = st.text_input("Security Key", type="password")
                st.write("<br>", unsafe_allow_html=True)
                
                if st.button("Secure Login", use_container_width=True, type="primary"):
                    full_id = f"OFF-{id_digits.strip()}"
                    if not df_officers.empty:
                        df_officers['Officer ID'] = df_officers['Officer ID'].astype(str)
                        df_officers['Security Key'] = df_officers['Security Key'].astype(str)
                        match = df_officers[(df_officers['Officer ID'] == full_id) & (df_officers['Security Key'] == security_key_input)]
                        if not match.empty:
                            st.session_state['officer_logged_in'] = True
                            st.session_state['user'] = match.iloc[0]['Name']
                            st.session_state['last_active'] = time.time()
                            st.query_params.session = "active" 
                            st.rerun()
                        else:
                            st.error(f"Invalid credentials for ID: {full_id}. Please try again.")
                    else:
                        st.warning("No officers found in the database. Please register first.")
            
            with tab_register:
                st.write("<br>", unsafe_allow_html=True)
                reg_name = st.text_input("Full Name", placeholder="Enter your official name")
                reg_designation = st.selectbox("Designation", ["Relationship Manager", "Branch Manager", "Credit Analyst", "Risk Officer"])
                reg_branch = st.text_input("Branch Name", placeholder="e.g. Kolkata Main")
                st.write("<br>", unsafe_allow_html=True)
                
                if st.button("Generate Credentials & Register", use_container_width=True, type="primary"):
                    if reg_name != "" and reg_branch != "":
                        new_id = f"OFF-{random.randint(1000, 9999)}"
                        new_key = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
                        try:
                            scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
                            creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
                            client = gspread.authorize(creds)
                            sheet_officers = client.open("Bank_Churn_Database").worksheet("Officer_DB")
                            sheet_officers.append_row([new_id, new_key, reg_name, reg_designation, reg_branch])
                            st.success(f"✅ Registration Successful for {reg_name}!")
                            st.info(f"**IMPORTANT:** Please save your credentials below to log in.\n\n**Officer ID:** `{new_id}`\n**Security Key:** `{new_key}`")
                            load_google_sheet.clear()
                        except Exception as e:
                            st.error(f"Failed to save to database. Error: {e}")
                    else:
                        st.warning("Please fill out your Name and Branch to register.")

else:
    # ------------------------------------
    # 📊 MAIN DASHBOARD AREA
    # ------------------------------------
    st.set_page_config(initial_sidebar_state="expanded") 
    model, scaler = load_assets()
    
    st.sidebar.title(f"👤 Officer: {st.session_state['user']}")
    if st.sidebar.button("🔍 Fetch Another Customer"):
        st.session_state['customer_ready'] = False
        st.session_state['auto_fill_acc'] = ""
        st.rerun()
        
    if st.sidebar.button("🚪 Logout completely"):
        st.session_state.clear()
        st.query_params.clear()
        st.rerun()
        
    st.sidebar.divider()
    
    if st.session_state.get('customer_ready', False):
        clean_data = {str(k).lower().replace(" ", "").replace("_", ""): v for k, v in st.session_state['cust_data'].items()}
        st.sidebar.header("📑 Live Financial Parameters")
        st.sidebar.markdown("### 🧪 What-If Simulator")
        what_if_mode = st.sidebar.toggle("Enable Sandbox Mode", value=False)

        c_score = int(clean_data.get('creditscore', 600))
        c_age = int(clean_data.get('age', 35))
        c_tenure = int(clean_data.get('tenure', 5))
        c_balance = float(clean_data.get('balance', 50000.0))
        c_salary = float(clean_data.get('estimatedsalary', 75000.0))
        gen_str = str(clean_data.get('gender', 'Male')).strip().title()
        gender_index = 0 if gen_str == 'Male' else 1
        prod_val = int(clean_data.get('numofproducts', clean_data.get('numberofproducts', 1)))
        prod_index = max(0, min(3, prod_val - 1)) 
        has_card_val = int(clean_data.get('hascrcard', clean_data.get('hascreditcard', 1)))
        has_card_index = 0 if has_card_val == 1 else 1
        is_active_val = int(clean_data.get('isactivemember', clean_data.get('isactive', 1)))
        is_active_index = 0 if is_active_val == 1 else 1
        geo_str = str(clean_data.get('geography', clean_data.get('country', 'France'))).strip().title()
        geo_options = ["France", "Germany", "Spain"]
        geo_index = geo_options.index(geo_str) if geo_str in geo_options else 0

        geography = st.sidebar.selectbox("Country (Geography)", geo_options, index=geo_index, disabled=not what_if_mode)
        credit_score = st.sidebar.slider("Credit Score", 300, 850, c_score, disabled=not what_if_mode)
        gender = st.sidebar.selectbox("Gender", ["Male", "Female"], index=gender_index, disabled=not what_if_mode)
        age = st.sidebar.slider("Age", 18, 92, c_age, disabled=not what_if_mode)
        tenure = st.sidebar.slider("Tenure (Years)", 0, 10, c_tenure, disabled=not what_if_mode)
        balance = st.sidebar.number_input("Account Balance (₹)", 0.0, 250000.0, c_balance, disabled=not what_if_mode)
        num_products = st.sidebar.selectbox("Number of Products", [1, 2, 3, 4], index=prod_index, disabled=not what_if_mode)
        has_card = st.sidebar.radio("Has Credit Card?", ["Yes", "No"], index=has_card_index, horizontal=True, disabled=not what_if_mode)
        is_active = st.sidebar.radio("Is Active Member?", ["Yes", "No"], index=is_active_index, horizontal=True, disabled=not what_if_mode)
        salary = st.sidebar.number_input("Estimated Salary (₹)", 0.0, 200000.0, c_salary, disabled=not what_if_mode)

        geo_germany = 1 if geography == "Germany" else 0
        geo_spain = 1 if geography == "Spain" else 0
        
        input_df = pd.DataFrame([{'CreditScore': credit_score, 'Gender': 1 if gender == "Male" else 0, 'Age': age, 'Tenure': tenure, 'Balance': balance, 'NumOfProducts': num_products, 'HasCrCard': 1 if has_card == "Yes" else 0, 'IsActiveMember': 1 if is_active == "Yes" else 0, 'EstimatedSalary': salary, 'Geography_Germany': geo_germany, 'Geography_Spain': geo_spain}])
    else: 
        clean_data = {}
        input_df = pd.DataFrame()

    if not st.session_state.get('customer_ready', False):
        st.success(f"👋 Welcome, {st.session_state['user']}! Authentication successful.")
        st.divider()
        st.subheader("🗄️ Smart Customer Directory")
        st.caption("Search for a specific customer or browse the entire list below. **Click on a row** below to auto-fill the analysis tab.")
        
        col_search_type, col_search_box = st.columns([1, 3])
        with col_search_type:
            search_by = st.selectbox("Search By", ["Customer Name", "Account Number", "Branch"])
        with col_search_box:
            if KEYUP_AVAILABLE:
                search_query = st_keyup(f"Enter {search_by}:", placeholder=f"e.g. Type the {search_by.lower()} here...", key="live_search")
            else:
                search_query = st.text_input(f"Enter {search_by} (Press Enter):", placeholder=f"e.g. Type the {search_by.lower()} here...")
        
        if search_query:
            if search_by == "Customer Name":
                df_filtered = df_cust_list[df_cust_list['Customer Name'].str.contains(search_query, case=False, na=False)]
            elif search_by == "Account Number":
                df_filtered = df_cust_list[df_cust_list['Account Number'].astype(str).str.contains(search_query, na=False)]
            elif search_by == "Branch":
                df_filtered = df_cust_list[df_cust_list['Branch'].str.contains(search_query, case=False, na=False)]
        else:
            df_filtered = df_cust_list

        gb = GridOptionsBuilder.from_dataframe(df_filtered)
        gb.configure_pagination(paginationAutoPageSize=True)
        gb.configure_side_bar()
        gb.configure_default_column(filter=False, resizable=True) 
        gb.configure_selection('single', use_checkbox=True) 
        gridOptions = gb.build()
        dark_theme_css = {
            ".ag-root-wrapper": {"background-color": "#161A23", "border": "1px solid #2A303C"},
            ".ag-header": {"background-color": "#0D1017", "color": "#00E676", "border-bottom": "1px solid #2A303C"},
            ".ag-row": {"background-color": "#161A23", "color": "#A5B1C2", "border-bottom": "1px solid #2A303C"},
            ".ag-row-hover": {"background-color": "#23272e !important"},
            ".ag-row-selected": {"background-color": "#1e3a8a !important", "color": "#ffffff"},
            ".ag-paging-panel": {"background-color": "#0D1017", "color": "#A5B1C2", "border-top": "1px solid #2A303C"},
            ".ag-icon": {"color": "#00E676"}
        }
        grid_response = AgGrid(
            df_filtered, gridOptions=gridOptions, data_return_mode='AS_INPUT', 
            update_mode=GridUpdateMode.SELECTION_CHANGED, theme='streamlit', 
            custom_css=dark_theme_css, height=350
        )

        selected_rows = grid_response['selected_rows']
        if selected_rows is not None and len(selected_rows) > 0:
            if isinstance(selected_rows, pd.DataFrame):
                if not selected_rows.empty:
                    st.session_state['auto_fill_acc'] = str(selected_rows.iloc[0]['Account Number'])
            else:
                st.session_state['auto_fill_acc'] = str(selected_rows[0]['Account Number'])
        
        st.divider()
        st.subheader("🔍 Fetch Customer Profile")
        acc_num = st.text_input("Account Number (Required)", value=st.session_state.get('auto_fill_acc', ''))
        
        if st.button("Fetch & Analyze Profile", type="primary"):
            if acc_num != "":
                try:
                    acc_num_int = int(acc_num)
                    customer_row = df_cust_data[df_cust_data['Account Number'] == acc_num_int]
                    customer_info = df_cust_list[df_cust_list['Account Number'] == acc_num_int]
                    if not customer_row.empty and not customer_info.empty:
                        st.session_state['customer_ready'] = True
                        st.session_state['cust_name'] = customer_info.iloc[0]['Customer Name']
                        st.session_state['branch'] = customer_info.iloc[0]['Branch']
                        st.session_state['acc_num'] = acc_num
                        st.session_state['cust_data'] = customer_row.iloc[0].to_dict()
                        if 'prob_calculated' in st.session_state:
                            st.session_state['prob_calculated'] = False 
                        st.rerun()
                    else:
                        st.error(f"Error: Account Number {acc_num} not found in the database!")
                except ValueError:
                    st.error("Account Number must be a valid number.")
            else:
                st.warning("Account Number is required to fetch data.")

    else:
        st.title(f"📊 Live Analysis: {st.session_state['cust_name']}")
        st.markdown(f"**A/C:** `{st.session_state['acc_num']}` | **Branch:** {st.session_state['branch']}")

        tab1, tab2, tab3 = st.tabs(["🚀 Risk Prediction", "📊 Dataset Insights", "👤 About & Docs"])

        with tab1:
            c1, c2 = st.columns([1, 1.2])
            with c1:
                if what_if_mode:
                    st.subheader("🧪 Simulated Profile (Sandbox)")
                else:
                    st.subheader("Auto-Fetched Profile")
                st.dataframe(input_df.T.rename(columns={0: 'Value'}), height=450)
            with c2:
                st.subheader("Prediction Result")
                if st.button("Calculate Probability", type="primary"):
                    input_scaled = scaler.transform(input_df)
                    st.session_state['current_prob'] = model.predict_proba(input_scaled)[0][1] * 100
                    st.session_state['prob_calculated'] = True
                if st.session_state.get('prob_calculated', False):
                    prob = st.session_state['current_prob']
                    components.html(animated_gauge_html(prob), height=300)
                    st.divider()
                    st.subheader("💡 Suggested Retention Strategy")
                    if prob > 70:
                        st.error("🚨 **High Risk Alert!** Urgent actions required to retain this customer:")
                        rec_list = ["- Immediate Contact: Assign a RM to call within 24 hours.", "- Financial Incentive: Offer a 0.5% interest rate bonus.", "- Fee Waiver: Waive the annual maintenance or credit card fees."]
                    elif prob > 30:
                        st.warning("⚠️ **Moderate Risk.** Strategic engagement recommended:")
                        rec_list = ["- Product Bundling: Offer a 'Lifetime Free' Credit Card.", "- Loyalty Benefits: Credit bonus reward points to their account.", "- Priority Status: Upgrade their account to priority banking."]
                    else:
                        st.success("✅ **Low Risk.** Standard relationship maintenance:")
                        rec_list = ["- Feedback Loop: Send a quick customer satisfaction survey.", "- General Outreach: Keep them updated with monthly newsletters."]
                    for line in rec_list:
                        st.write(line)
                    st.divider()
                    pdf_buffer = create_pdf_report(officer=st.session_state['user'], cust_name=st.session_state['cust_name'] + (" (Simulated)" if what_if_mode else ""), acc_num=st.session_state['acc_num'], branch=st.session_state['branch'], prob=prob, rec_list=rec_list)
                    st.download_button("📥 Download Official PDF Report", data=pdf_buffer, file_name=f"Risk_Report_{st.session_state['acc_num']}.pdf", mime="application/pdf")

        with tab2:
            st.subheader("📊 Analytics & Comparative Insights")
            st.caption("AI-driven macro analysis and comparative cohort metrics replacing standard visualizations.")
            
            try:
                df_clean = df_cust_data.copy()
                df_clean.columns = df_clean.columns.str.lower().str.replace(' ', '').str.replace('_', '')
                
                if not df_clean.empty:
                    pred_df = pd.DataFrame()
                    pred_df['CreditScore'] = pd.to_numeric(df_clean.get('creditscore', 600))
                    gen_series = df_clean.get('gender', pd.Series(['Male']*len(df_clean))).astype(str).str.strip().str.title()
                    pred_df['Gender'] = gen_series.apply(lambda x: 1 if x == 'Male' else 0)
                    pred_df['Age'] = pd.to_numeric(df_clean.get('age', 35))
                    pred_df['Tenure'] = pd.to_numeric(df_clean.get('tenure', 5))
                    pred_df['Balance'] = pd.to_numeric(df_clean.get('balance', 0.0))
                    prod_col_name = 'numofproducts' if 'numofproducts' in df_clean else ('numberofproducts' if 'numberofproducts' in df_clean else None)
                    pred_df['NumOfProducts'] = pd.to_numeric(df_clean[prod_col_name]) if prod_col_name else 1
                    card_col_name = 'hascrcard' if 'hascrcard' in df_clean else ('hascreditcard' if 'hascreditcard' in df_clean else None)
                    pred_df['HasCrCard'] = pd.to_numeric(df_clean[card_col_name]) if card_col_name else 1
                    act_col_name = 'isactivemember' if 'isactivemember' in df_clean else ('isactive' if 'isactive' in df_clean else None)
                    pred_df['IsActiveMember'] = pd.to_numeric(df_clean[act_col_name]) if act_col_name else 1
                    pred_df['EstimatedSalary'] = pd.to_numeric(df_clean.get('estimatedsalary', 0.0))
                    geo_col_name = 'geography' if 'geography' in df_clean else ('country' if 'country' in df_clean else None)
                    geo_series = df_clean[geo_col_name].astype(str).str.strip().str.title() if geo_col_name else pd.Series(['France']*len(df_clean))
                    pred_df['Geography_Germany'] = (geo_series == 'Germany').astype(int)
                    pred_df['Geography_Spain'] = (geo_series == 'Spain').astype(int)

                    bank_scaled = scaler.transform(pred_df)
                    bank_probs = model.predict_proba(bank_scaled)[:, 1] * 100

                    total_cust = len(pred_df)
                    avg_score = pred_df['CreditScore'].mean()
                    avg_balance = pred_df['Balance'].mean()
                    active_pct = (pred_df['IsActiveMember'].sum() / total_cust) * 100 if total_cust > 0 else 0.0
                    
                    health_status = "stable" if avg_score > 600 else "vulnerable"
                    engagement_status = "requires immediate attention" if active_pct < 50 else "shows healthy engagement"
                    
                    st.markdown(f"""
                    <div class="active-analytical-area" style="background: rgba(30, 58, 138, 0.1); border-left: 4px solid #ef4444; border-radius: 8px; padding: 20px; margin-bottom: 20px;">
                        <div style="color: #FFFFFF; font-size: 1.35rem; font-weight: bold; margin-bottom: 10px; display:flex; align-items:center; gap:8px;">
                            🤖 <span>Automated AI Diagnostic Report</span>
                        </div>
                        <div class="card-text">
                            Analyzing the current centralized database of <b>{total_cust} active profiles</b>, the overall cohort credit health is <b>{health_status}</b> with a mean score of {int(avg_score)}. 
                            The average liquidity maintained per account is <b>₹{avg_balance:,.2f}</b>. Currently, <b>{active_pct:.1f}%</b> of the user base is actively transacting, which {engagement_status}. 
                            <br><br><i>AI Recommendation:</i> Prioritize retention efforts on the inactive segment holding above-average balances.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.write("<br>", unsafe_allow_html=True)
                    
                    k1, k2, k3, k4 = st.columns(4)
                    with k1: st.markdown(f'<div class="dashboard-kpi active-analytical-area"><div class="dashboard-kpi-val">{total_cust}</div><div class="dashboard-kpi-lab">Total Database</div></div>', unsafe_allow_html=True)
                    with k2: st.markdown(f'<div class="dashboard-kpi active-analytical-area"><div class="dashboard-kpi-val">{int(avg_score)}</div><div class="dashboard-kpi-lab">Avg Credit Score</div></div>', unsafe_allow_html=True)
                    with k3: st.markdown(f'<div class="dashboard-kpi active-analytical-area"><div class="dashboard-kpi-val">₹{avg_balance:,.0f}</div><div class="dashboard-kpi-lab">Mean Liquidity</div></div>', unsafe_allow_html=True)
                    with k4: st.markdown(f'<div class="dashboard-kpi active-analytical-area"><div class="dashboard-kpi-val">{active_pct:.1f}%</div><div class="dashboard-kpi-lab">Active Engagement</div></div>', unsafe_allow_html=True)
                    
                    st.divider()

                    st.markdown("### 📈 Customer vs. Cohort Benchmarks")
                    bench_col1, bench_col2, bench_col3, bench_col4 = st.columns(4)
                    with bench_col1:
                        st.markdown(f'''
                        <div class="comp-card">
                            <div class="comp-title">⚖️ Comparison: Age</div>
                            <div class="comp-grid">
                                <div><div class="comp-label">Customer</div><div class="comp-val-cust">{c_age}</div></div>
                                <div><div class="comp-label">Bank Avg</div><div class="comp-val-bank">{int(pred_df['Age'].mean())}</div></div>
                            </div>
                        </div>
                        ''', unsafe_allow_html=True)
                    with bench_col2:
                         st.markdown(f'''
                        <div class="comp-card">
                            <div class="comp-title">⚖️ Comparison: Credit Score</div>
                            <div class="comp-grid">
                                <div><div class="comp-label">Customer</div><div class="comp-val-cust">{c_score}</div></div>
                                <div><div class="comp-label">Bank Avg</div><div class="comp-val-bank">{int(avg_score)}</div></div>
                            </div>
                        </div>
                        ''', unsafe_allow_html=True)
                    with bench_col3:
                         st.markdown(f'''
                        <div class="comp-card">
                            <div class="comp-title">⚖️ Comparison: Balance</div>
                            <div class="comp-grid">
                                <div><div class="comp-label">Customer</div><div class="comp-val-cust">₹{c_balance:,.0f}</div></div>
                                <div><div class="comp-label">Bank Avg</div><div class="comp-val-bank">₹{avg_balance:,.0f}</div></div>
                            </div>
                        </div>
                        ''', unsafe_allow_html=True)
                    with bench_col4:
                         st.markdown(f'''
                        <div class="comp-card">
                            <div class="comp-title">⚖️ Comparison: Products</div>
                            <div class="comp-grid">
                                <div><div class="comp-label">Customer</div><div class="comp-val-cust">{prod_val}</div></div>
                                <div><div class="comp-label">Bank Avg</div><div class="comp-val-bank">{pred_df['NumOfProducts'].mean():.1f}</div></div>
                            </div>
                        </div>
                        ''', unsafe_allow_html=True)

                    st.write("<br>", unsafe_allow_html=True)
                    
                    st.markdown("### 🌍 Demographics")
                    demo_col1, demo_col2, demo_col3 = st.columns(3)
                    df_map = pred_df.copy()
                    df_map['Country'] = 'France'
                    df_map.loc[df_map['Geography_Germany'] == 1, 'Country'] = 'Germany'
                    df_map.loc[df_map['Geography_Spain'] == 1, 'Country'] = 'Spain'
                    counts = df_map['Country'].value_counts()
                    fra_count = counts.get('France', 0)
                    ger_count = counts.get('Germany', 0)
                    spa_count = counts.get('Spain', 0)
                    with demo_col1:
                        st.markdown(f'''
                        <div class="demo-card">
                            <div class="demo-title">🇫🇷 Country: France</div>
                            <div class="comp-label">Customer Count</div>
                            <div class="demo-val">{fra_count}</div>
                            <div class="demo-pct">({(fra_count/total_cust)*100:.1f}% of Base)</div>
                        </div>
                        ''', unsafe_allow_html=True)
                    with demo_col2:
                        st.markdown(f'''
                        <div class="demo-card" style="border-left-color: #ef4444;">
                            <div class="demo-title">🇩🇪 Country: Germany</div>
                            <div class="comp-label">Customer Count</div>
                            <div class="demo-val" style="color: #ef4444;">{ger_count}</div>
                            <div class="demo-pct">({(ger_count/total_cust)*100:.1f}% of Base)</div>
                        </div>
                        ''', unsafe_allow_html=True)
                    with demo_col3:
                        st.markdown(f'''
                        <div class="demo-card" style="border-left-color: #f97316;">
                            <div class="demo-title">🇪🇸 Country: Spain</div>
                            <div class="comp-label">Customer Count</div>
                            <div class="demo-val" style="color: #f97316;">{spa_count}</div>
                            <div class="demo-pct">({(spa_count/total_cust)*100:.1f}% of Base)</div>
                        </div>
                        ''', unsafe_allow_html=True)

                    st.write("<br>", unsafe_allow_html=True)

                    st.markdown("### 📊 Advanced Visual Analytics")
                    viz_col1, viz_col2 = st.columns([1, 1.2])

                    with viz_col1:
                        st.markdown('<div class="card-title" style="margin-bottom: 12px;">🕸️ Cohort Radar Analysis</div>', unsafe_allow_html=True)
                        
                        categories = ['Credit Score', 'Age', 'Tenure', 'Balance', 'Products']
                        max_score = pred_df['CreditScore'].max() if pred_df['CreditScore'].max() > 0 else 1
                        max_age = pred_df['Age'].max() if pred_df['Age'].max() > 0 else 1
                        max_tenure = pred_df['Tenure'].max() if pred_df['Tenure'].max() > 0 else 1
                        max_balance = pred_df['Balance'].max() if pred_df['Balance'].max() > 0 else 1
                        max_products = pred_df['NumOfProducts'].max() if pred_df['NumOfProducts'].max() > 0 else 1
                        
                        cust_vals = [c_score/max_score, c_age/max_age, c_tenure/max_tenure, c_balance/max_balance, prod_val/max_products]
                        bank_vals = [avg_score/max_score, pred_df['Age'].mean()/max_age, pred_df['Tenure'].mean()/max_tenure, avg_balance/max_balance, pred_df['NumOfProducts'].mean()/max_products]

                        fig_radar = go.Figure()
                        fig_radar.add_trace(go.Scatterpolar(r=cust_vals, theta=categories, fill='toself', name='Customer', line_color='#00E676'))
                        fig_radar.add_trace(go.Scatterpolar(r=bank_vals, theta=categories, fill='toself', name='Bank Avg', line_color='#ef4444', opacity=0.6))
                        fig_radar.update_layout(
                            height=380,
                            polar=dict(radialaxis=dict(visible=False, range=[0, 1]), bgcolor='rgba(0,0,0,0)'),
                            showlegend=True, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                            margin=dict(t=40, b=40, l=40, r=40),
                            font=dict(color='#A5B1C2', size=13),
                            legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1, font=dict(size=14))
                        )
                        st.plotly_chart(fig_radar, use_container_width=True)

                    with viz_col2:
                        st.markdown('<div class="card-title" style="margin-bottom: 12px;">🧠 AI Feature Weights</div>', unsafe_allow_html=True)
                        if not input_df.empty:
                            try:
                                feat_imp = pd.Series(model.feature_importances_, index=input_df.columns).sort_values(ascending=True).tail(5)
                                fig_feat = px.bar(feat_imp, orientation='h')
                                fig_feat.update_traces(marker_color='#00E676', marker_line_color='#FFFFFF', marker_line_width=1, opacity=0.8)
                                fig_feat.update_layout(
                                    height=380,
                                    showlegend=False,
                                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                    xaxis_title="Impact Weight", yaxis_title="",
                                    margin=dict(l=10, r=20, t=20, b=40),
                                    font=dict(color='#A5B1C2', size=13),
                                    xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
                                    yaxis=dict(showgrid=False)
                                )
                                st.plotly_chart(fig_feat, use_container_width=True)
                            except: st.error("Feature importance calculation unavailable.")

                    st.write("<br>", unsafe_allow_html=True)
                    
                    st.markdown("### 🛑 Main Churn Risk Drivers (Central Cohort)")
                    driver_col1, driver_col2, driver_col3 = st.columns(3)
                    
                    if not input_df.empty:
                        try:
                            feat_imp = pd.Series(model.feature_importances_, index=input_df.columns).sort_values(ascending=False)
                            top_features = feat_imp.head(3)
                            
                            driver_titles = ["#1 Driver: Age Factor", "#2 Driver: Financial Status (Salary)", "#3 Driver: Credit History"]
                            driver_colors = ["#ef4444", "#f97316", "#eab308"] 
                            
                            for col, title, color, (feat, weight) in zip([driver_col1, driver_col2, driver_col3], driver_titles, driver_colors, top_features.items()):
                                with col:
                                    st.markdown(f'''
                                    <div class="dashboard-kpi active-analytical-area" style="text-align: left; padding: 20px;">
                                        <div style="color: {color}; font-size: 1.25rem; font-weight: bold; margin-bottom: 10px; text-transform:uppercase; letter-spacing:1px;">{title}</div>
                                        <div style="color: #8b949e; font-size: 1rem; margin-bottom: 5px;">This cohort's risk is primarily driven by how {feat.lower()} interacts with other parameters, contributing:</div>
                                        <div style="color: #FFFFFF; font-size: 2.1rem; font-weight: bold;">{weight*100:.1f}%</div>
                                        <div style="color: #8b949e; font-size: 1rem;">to the overall predictive model weight.</div>
                                    </div>
                                    ''', unsafe_allow_html=True)
                        except: st.error("ML Drivers unavailable.")

                else: st.warning("Database empty. Cannot calculate overall metrics.")
        
            except Exception as e: st.warning(f"⚠️ Could not load extra insights. Error details: {e}")

        with tab3:
            st.header("📚 Documentation & About")
            col_doc1, col_doc2 = st.columns(2)
            with col_doc1:
                st.markdown("""
                <div class="sentinel-card">
                    <div class="card-title">⚙️ System Specifications</div>
                    <div class="card-text">
                        <strong>Project Domain:</strong> Data Science & Machine Learning<br>
                        <strong>Core Model:</strong> Random Forest Classifier<br>
                        <strong>Framework:</strong> Streamlit x React<br>
                        <strong>Active Officer:</strong> """ + st.session_state.get('user', 'Officer') + """
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.markdown("""
                <div class="sentinel-card">
                    <div class="card-title">🏗️ Project Architecture</div>
                    <div class="card-text">
                        This platform integrates live Google Sheets tracking with an isolated ML environment. The interactive UI provides an immediate feedback loop using Plotly and AgGrid for real-time customer data management.
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("""
                <div class="sentinel-card">
                    <div class="card-title">📊 Model Performance Metrics</div>
                    <div class="card-text">
                        <strong>Accuracy:</strong> 91.0%<br>
                        <strong>F1-Score:</strong> 0.86<br>
                        <strong>Model Update Cycle:</strong> Automated Weekly<br>
                        <strong>Central Sync:</strong> 1-Minute Intervals
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            with col_doc2:
                st.markdown("""
                <div class="sentinel-card">
                    <div class="card-title">🔒 Security Protocol</div>
                    <div class="card-text">
                        <strong>Auth:</strong> 2-Factor Officer Prefix Verification<br>
                        <strong>Session:</strong> 10-Minute Auto-Timeout<br>
                        <strong>Persistence:</strong> Automatic Rollback on F5 refresh<br>
                        <strong>Database:</strong> Google OAuth 2.0 API Link
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.markdown("""
                <div class="sentinel-card" style="border-color: #00E676;">
                    <div class="card-title">🎓 Academic Project Details</div>
                    <div class="card-text">
                        Developed as an advanced predictive analytics model for the <strong>AIPA Course</strong> at <strong>NSTI Howrah</strong>.<br><br>
                        Designed to demonstrate the practical application of machine learning in solving real-world financial retention challenges (Bank Customer Churn).
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("""
                <div class="sentinel-card">
                    <div class="card-title">🛡️ Data Governance & Privacy</div>
                    <div class="card-text">
                        <strong>Compliance:</strong> ISO 27001 Certified Environment<br>
                        <strong>Access:</strong> Role-Based Access Control (RBAC)<br>
                        <strong>Encryption:</strong> AES-256 for PII<br>
                        <strong>Audit Trail:</strong> Complete Logging of Fetch requests
                    </div>
                </div>
                """, unsafe_allow_html=True)