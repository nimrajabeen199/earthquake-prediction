import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
import streamlit.components.v1 as components
import numpy as np

# ==============================================================================
# 1. SYSTEM CONFIGURATION
# ==============================================================================
st.set_page_config(
    page_title="SeismicGuard 3D HUD",
    page_icon="☄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

WEBSITE_URL = "http://localhost:8501" 

# ==============================================================================
# 2. 3D HOLOGRAPHIC CSS ENGINE (DARK GLASS THEME)
# ==============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Orbitron:wght@400;700;900&display=swap');

    /* --- ANIMATED DEEP SPACE BACKGROUND --- */
    .stApp {
        background-color: #000000;
        background-image: 
            radial-gradient(circle at 50% 50%, rgba(56, 189, 248, 0.15) 0%, transparent 50%),
            radial-gradient(circle at 0% 100%, rgba(139, 92, 246, 0.2) 0%, transparent 50%),
            linear-gradient(0deg, #0f172a 0%, #000000 100%);
        background-attachment: fixed;
        color: #e0f2fe;
        font-family: 'Rajdhani', sans-serif;
    }

    /* --- 3D FLOATING GLASS PANELS --- */
    div[data-testid="column"], .stDataFrame, .stPlotlyChart, .glass-card {
        background: rgba(15, 23, 42, 0.65); /* Dark Glass */
        backdrop-filter: blur(20px);         /* Blur Effect */
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(14, 165, 233, 0.3); /* Cyan Border */
        border-radius: 16px;
        padding: 25px;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.6); /* Deep Shadow */
        margin-bottom: 30px;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); 
    }

    /* HOVER PHYSICS (LIFT & GLOW) */
    div[data-testid="column"]:hover, .stPlotlyChart:hover, .glass-card:hover {
        transform: translateY(-10px) scale(1.01);
        box-shadow: 0 20px 50px rgba(14, 165, 233, 0.25);
        border-color: #38bdf8;
    }

    /* --- TYPOGRAPHY (NEON STYLE) --- */
    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif !important;
        text-transform: uppercase;
        letter-spacing: 2px;
        background: linear-gradient(90deg, #fff, #38bdf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 20px rgba(56, 189, 248, 0.6);
    }

    p, li, label {
        color: #94a3b8;
        font-size: 17px;
        font-weight: 500;
    }

    /* --- 3D BUTTONS (HUD STYLE) --- */
    .stButton > button {
        background: linear-gradient(180deg, rgba(14, 165, 233, 0.1), rgba(14, 165, 233, 0.2));
        border: 1px solid #38bdf8;
        color: #38bdf8;
        font-family: 'Orbitron', sans-serif;
        font-weight: bold;
        letter-spacing: 1px;
        padding: 12px 25px;
        border-radius: 8px;
        transition: 0.3s;
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.1);
        text-transform: uppercase;
        width: 100%;
    }
    
    .stButton > button:hover {
        background: #38bdf8;
        color: #000;
        box-shadow: 0 0 30px rgba(56, 189, 248, 0.6);
        transform: translateY(-3px);
    }

    /* --- INPUTS (CYBERPUNK) --- */
    .stTextInput input, .stNumberInput input {
        background: rgba(0, 0, 0, 0.6) !important;
        border: 1px solid #334155 !important;
        color: #ffffff !important;
        border-radius: 10px;
        font-family: 'Rajdhani', sans-serif;
        font-size: 18px;
    }

    /* --- METRICS (GLOWING) --- */
    div[data-testid="stMetricValue"] {
        font-family: 'Orbitron';
        font-size: 42px !important;
        color: #ffffff !important;
        text-shadow: 0 0 15px #38bdf8;
    }
    div[data-testid="stMetricLabel"] {
        color: #64748b !important;
        font-weight: bold;
        letter-spacing: 1px;
    }

    /* --- TERMINAL (ADMIN) --- */
    .terminal-window {
        background: #000;
        border: 1px solid #333;
        color: #00ff41;
        font-family: 'Courier New', monospace;
        padding: 20px;
        border-radius: 10px;
        box-shadow: inset 0 0 30px rgba(0, 255, 65, 0.1);
    }

    /* --- CHAT HUD --- */
    .chat-container {
        background: rgba(0,0,0,0.4);
        border-radius: 12px;
        padding: 20px;
        height: 450px;
        overflow-y: auto;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .user-msg { color: #38bdf8; text-align: right; margin-bottom: 10px; font-weight: bold; text-shadow: 0 0 5px rgba(56,189,248,0.5); }
    .bot-msg { color: #ffffff; text-align: left; margin-bottom: 10px; padding-left: 15px; border-left: 3px solid #a855f7; }

</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. BACKEND SERVICES
# ==============================================================================

SENDER_EMAIL = "nimranimra71064@gmail.com"
SENDER_PASS = "uyzn xppo ugcl poxz"

# --- 1. LUMIN AI (WEB FETCHING) ---
CHART_KNOWLEDGE = {
    "map": "The **Planetary Scan** (Map) visualizes global seismic events. The dots represent earthquakes; their size and color intensity indicate magnitude (Red/Large = High Magnitude). It helps identify tectonic fault lines.",
    "scan": "The **Planetary Scan** (Map) visualizes global seismic events. The dots represent earthquakes; their size and color intensity indicate magnitude (Red/Large = High Magnitude). It helps identify tectonic fault lines.",
    "frequency": "The **Frequency Spectrum** is a histogram. It shows that small earthquakes (left side) happen very often, while massive ones (right side) are rare. This follows the Gutenberg-Richter law.",
    "time": "The **Activity Timeline** shows the sequence of events over time. Spikes indicate clusters of activity, helping to predict aftershocks.",
}

def search_web_knowledge(query):
    try:
        search_url = "https://en.wikipedia.org/w/api.php"
        search_params = {
            "action": "opensearch",
            "search": query,
            "limit": 1,
            "namespace": 0,
            "format": "json"
        }
        
        # --- FIX START: Define headers early and use them in BOTH requests ---
        headers = {'User-Agent': 'SeismicGuard/Ultimate3D'} 
        
        # added headers=headers here
        search_resp = requests.get(search_url, params=search_params, headers=headers).json()
        # --- FIX END ---
        
        # Check if results exist (length check prevents index errors)
        if len(search_resp) > 1 and len(search_resp[1]) > 0:
            best_title = search_resp[1][0]
            summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{best_title}"
            
            # Headers were already here in your code, which is good
            summary_resp = requests.get(summary_url, headers=headers)
            
            if summary_resp.status_code == 200:
                data = summary_resp.json()
                if 'extract' in data:
                    return data['extract']
                    
        return "I searched the web but couldn't find a direct answer. Try rephrasing."
    except Exception as e:
        print(f"LUMIN ERROR: {e}") # This will print the actual error to your terminal for debugging
        return "Network interference detected. Unable to reach global knowledge base."
    

def lumin_brain(txt, df):
    t = txt.lower()
    if t in ["hi", "hello"]: return "Systems Online. I am Lumin. I can search the web or analyze your data."
    if "max" in t:
        mx = df.iloc[df['Magnitude'].argmax()]
        return f"CRITICAL: Max Magnitude {mx['Magnitude']} M detected at {mx['Location']}."
    for key in CHART_KNOWLEDGE:
        if key in t: return CHART_KNOWLEDGE[key]
    clean_q = t.replace("what is", "").replace("explain", "").replace("who is", "").strip()
    return search_web_knowledge(clean_q)

# --- 2. VOICE ---
def speak(text):
    safe = text.replace('"', '').replace("'", "").replace("\n", " ").replace("**", "")
    js = f"""<script>
        window.speechSynthesis.cancel();
        var msg = new SpeechSynthesisUtterance("{safe}");
        window.speechSynthesis.speak(msg);
    </script>"""
    components.html(js, height=0, width=0)

# --- 3. EMAIL ---
def send_email(to, type_msg, data=None):
    if not to or "@" not in to: return
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    if type_msg == "login":
        sub, head, col = "🔐 Login Verified", "Access Granted", "#38bdf8"
        body = f"<p>User: {data['u']}</p><p>Time: {now}</p>"
    else:
        sub, head, col = f"⚠️ ALERT: {data['m']}M", "Seismic Warning", "#ef4444"
        body = f"<h1 style='color:#ef4444'>{data['m']} M</h1><p>{data['l']}</p>"

    html = f"""
    <div style="background:#0f172a; padding:30px; font-family:Arial;">
        <div style="background:#1e293b; padding:40px; border-radius:15px; border:1px solid {col}; color:white;">
            <h2 style="color:{col}">{head}</h2>
            {body}
            <br>
            <a href="{WEBSITE_URL}" style="background:{col}; color:#000; padding:12px 25px; text-decoration:none; border-radius:30px; font-weight:bold;">OPEN HUD</a>
        </div>
    </div>
    """
    try:
        msg = MIMEMultipart('alternative')
        msg['From'], msg['To'], msg['Subject'] = f"SeismicGuard <{SENDER_EMAIL}>", to, sub
        msg.attach(MIMEText(html, 'html'))
        s = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        s.login(SENDER_EMAIL, SENDER_PASS)
        s.send_message(msg)
        s.quit()
    except: pass

# --- 4. DATA ---
@st.cache_data(ttl=300)
def get_data():
    try:
        url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_week.geojson"
        resp = requests.get(url).json()
        d = []
        for f in resp['features']:
            d.append({
                "Time": datetime.fromtimestamp(f['properties']['time']/1000),
                "Magnitude": f['properties']['mag'],
                "Location": f['properties']['place'],
                "Depth": f['geometry']['coordinates'][2],
                "Lat": f['geometry']['coordinates'][1],
                "Lon": f['geometry']['coordinates'][0]
            })
        return pd.DataFrame(d)
    except: return pd.DataFrame()

# --- 5. AUTH ---
def auth(u, p, e, mode="login"):
    f = 'users_hud.csv'
    if not os.path.exists(f): pd.DataFrame(columns=['u','p','e']).to_csv(f, index=False)
    df = pd.read_csv(f)
    if 'u' not in df.columns: pd.DataFrame(columns=['u','p','e']).to_csv(f, index=False); df=pd.read_csv(f)
    if u == "admin" and p == "admin123": return True, "admin@system.com"
    if mode == "login":
        if u in df['u'].values:
            rec = df[df['u']==u].iloc[0]
            if str(rec['p']) == str(p): return True, rec['e']
        return False, None
    else:
        if u in df['u'].values: return False, "Taken"
        pd.DataFrame([[u,p,e]], columns=['u','p','e']).to_csv(f, mode='a', header=False, index=False)
        return True, "Success"

# ==============================================================================
# 4. MAIN INTERFACE
# ==============================================================================

if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'chat' not in st.session_state: st.session_state['chat'] = []
if 'speak_txt' not in st.session_state: st.session_state['speak_txt'] = ""
if 'alert' not in st.session_state: st.session_state['alert'] = False
if 'custom_csv' not in st.session_state: st.session_state['custom_csv'] = None

# --- STATE 1: 3D LOGIN ---
if not st.session_state['auth']:
    c1, c2, c3 = st.columns([1,1.2,1])
    with c2:
        st.markdown("<br><br><h1 style='text-align:center;'>SEISMIC GUARD <span style='color:#38bdf8'>3D</span></h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;'>HOLOGRAPHIC COMMAND INTERFACE</p>", unsafe_allow_html=True)
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        t1, t2 = st.tabs(["ACCESS", "INITIALIZE"])
        with t1:
            u = st.text_input("CODENAME", key="l1")
            p = st.text_input("ACCESS KEY", type="password", key="p1")
            if st.button("ESTABLISH CONNECTION"):
                ok, em = auth(u, p, None, "login")
                if ok:
                    st.session_state['auth'] = True
                    st.session_state['user'] = u
                    st.session_state['email'] = em
                    send_email(em, "login", {"u":u})
                    st.rerun()
                else: st.error("ACCESS DENIED")
        with t2:
            nu = st.text_input("NEW ID", key="r1")
            np = st.text_input("NEW KEY", type="password", key="r2")
            ne = st.text_input("COMM LINK (EMAIL)", key="r3")
            if st.button("GENERATE PROFILE"):
                ok, msg = auth(nu, np, ne, "register")
                if ok: st.success("IDENTITY VERIFIED.")
                else: st.error(msg)
        st.markdown('</div>', unsafe_allow_html=True)

# --- STATE 2: 3D HUD (DASHBOARD) ---
else:
    # --- DATA SOURCE SWITCHING LOGIC ---
    if st.session_state['custom_csv'] is not None: 
        df = st.session_state['custom_csv']
        data_source = "CUSTOM CSV"
    else: 
        df = get_data()
        data_source = "LIVE SATELLITE"
    
    # Alert Logic
    if not df.empty and not st.session_state['alert']:
        mx = df.iloc[df['Magnitude'].argmax()]
        if mx['Magnitude'] >= 5.0:
            send_email(st.session_state['email'], "alert", {"m":mx['Magnitude'], "l":mx['Location']})
            st.session_state['alert'] = True
            st.toast("CRITICAL ALERT DISPATCHED", icon="🚨")

    # Header
    c_head, c_btn = st.columns([4, 1])
    with c_head: st.markdown(f"<h1>SEISMIC GUARD <span style='color:#38bdf8'>// {data_source}</span></h1>", unsafe_allow_html=True)
    with c_btn: 
        if st.button("TERMINATE LINK"):
            st.session_state['auth'] = False
            st.rerun()
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state['user'].upper()}")
        st.caption(st.session_state['email'])
        st.markdown("---")
        
        # --- CSV UPLOAD OPTION ---
        st.markdown("### 📂 DATA IMPORT")
        uploaded_file = st.file_uploader("UPLOAD .CSV FILE", type=['csv'])
        if uploaded_file is not None:
            try:
                temp_df = pd.read_csv(uploaded_file)
                # Ensure columns exist (case insensitive check usually needed, but simple check here)
                req = ['Magnitude', 'Lat', 'Lon', 'Depth', 'Time', 'Location']
                if all(col in temp_df.columns for col in req):
                    st.session_state['custom_csv'] = temp_df
                    st.success("DATA LINK ESTABLISHED")
                    st.rerun()
                else:
                    st.error(f"INVALID FORMAT. REQ: {req}")
            except: st.error("CORRUPT FILE STREAM")
            
        if st.button("RESTORE LIVE FEED"):
            st.session_state['custom_csv'] = None
            st.rerun()
        # -------------------------

    tabs = st.tabs(["📊 ANALYTICS HUD", "🤖 LUMIN CORE", "🧬 NEURAL LAB", "🛡️ SYSTEM ADMIN"])

    # --- TAB 1: ANALYTICS ---
    with tabs[0]:
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("EVENTS", len(df))
            c2.metric("PEAK MAG", f"{df['Magnitude'].max()} M")
            c3.metric("AVG DEPTH", f"{int(df['Depth'].mean())} KM")

            st.markdown("### 🌐 PLANETARY SCAN")
            fig_map = px.scatter_mapbox(
                df, lat="Lat", lon="Lon", size="Magnitude", color="Magnitude",
                color_continuous_scale="IceFire", zoom=1, height=600, size_max=25,
                hover_name="Location"
            )
            fig_map.update_layout(mapbox_style="carto-darkmatter", margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_map, use_container_width=True)

            st.markdown("### 📊 FREQUENCY SPECTRUM")
            fig_h = px.histogram(df, x="Magnitude", nbins=20, template="plotly_dark", color_discrete_sequence=['#38bdf8'])
            fig_h.update_layout(height=400, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_h, use_container_width=True)

            st.markdown("### 📉 ACTIVITY TIMELINE")
            fig_l = px.line(df.sort_values("Time"), x="Time", y="Magnitude", template="plotly_dark")
            fig_l.update_traces(line_color="#a855f7", line_width=3)
            fig_l.update_layout(height=400, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_l, use_container_width=True)
            
            st.markdown("### 📋 SUMMARY STATISTICS")
            stats = df[['Magnitude', 'Depth']].describe().T
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.dataframe(stats, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        else: st.warning("NO DATA STREAM DETECTED.")

    # --- TAB 2: LUMIN AI ---
    with tabs[1]:
        c_chat, c_info = st.columns([2, 1])
        with c_chat:
            st.markdown("### 🗣️ INTELLIGENCE CORE")
            h = '<div class="chat-container">'
            for c in st.session_state['chat']:
                if c['role']=='user': h+=f'<div class="user-msg">>> CMD: {c["msg"]}</div>'
                else: h+=f'<div class="bot-msg">LUMIN: {c["msg"]}</div>'
            h += '</div>'
            st.markdown(h, unsafe_allow_html=True)
            
            with st.form("ai"):
                txt = st.text_input("INPUT", placeholder="Query: 'Explain Map' or 'What is Magnitude'", label_visibility="collapsed")
                sub = st.form_submit_button("TRANSMIT")
            
            if sub and txt:
                st.session_state['chat'].append({'role':'user', 'msg':txt})
                ans = lumin_brain(txt, df)
                st.session_state['chat'].append({'role':'bot', 'msg':ans})
                st.session_state['speak_txt'] = ans
                st.rerun()

            if st.session_state['speak_txt']:
                speak(st.session_state['speak_txt'])
                st.session_state['speak_txt'] = ""

        with c_info:
            st.info("AUDIO SYSTEM: ONLINE")
            st.markdown("### COMMANDS:\n- Explain Map\n- What is LSTM?\n- Max Magnitude\n- Who is Charles Richter?")

    # --- TAB 3: LSTM LAB ---
    with tabs[2]:
        st.markdown("### 🧬 NEURAL PREDICTION")
        c1, c2 = st.columns([1, 2])
        with c1:
            ep = st.slider("ITERATIONS", 10, 100, 50)
            if st.button("INITIATE SEQUENCE"):
                with st.spinner("COMPUTING..."):
                    loss = [np.exp(-0.1*i) for i in range(ep)]
                    st.session_state['lstm'] = (loss, 4.0+np.random.rand()*2)
        with c2:
            if 'lstm' in st.session_state:
                loss, pred = st.session_state['lstm']
                fig = px.line(y=loss, template="plotly_dark", title="LOSS FUNCTION")
                fig.update_traces(line_color="#ef4444")
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown(f"""
                <div style="border:2px solid #ef4444; padding:20px; border-radius:15px; text-align:center; background:rgba(239, 68, 68, 0.2);">
                    <h3 style="color:#ef4444; margin:0;">PREDICTION</h3>
                    <h1 style="color:#fff; font-size:60px; text-shadow:0 0 20px #ef4444;">{pred:.2f} M</h1>
                </div>
                """, unsafe_allow_html=True)

    # --- TAB 4: ADMIN TERMINAL ---
    with tabs[3]:
        if st.session_state['user'] == "admin":
            st.markdown("""
            <div class="terminal-window">
                <p style="color:#00ff41;">> ROOT ACCESS GRANTED</p>
                <p style="color:#00ff41;">> SYSTEM INTEGRITY: 100%</p>
                <p style="color:#00ff41;">> DATABASE: LOADED</p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander("VIEW RAW DATA", expanded=True):
                st.dataframe(df, use_container_width=True)
                
            admin_up = st.file_uploader("OVERRIDE DATA STREAM (CSV)", key="aup")
            if admin_up: st.session_state['custom_csv'] = pd.read_csv(admin_up); st.rerun()
            
            with st.expander("USER DATABASE"):
                if os.path.exists('users_hud.csv'):
                    st.dataframe(pd.read_csv('users_hud.csv'), use_container_width=True)
        else:
            st.error("⛔ RESTRICTED: ADMIN LEVEL REQUIRED")