"""
SoulSync — Streamlit Dashboard
app.py
 
Run with:
    streamlit run 3.core_app/app.py
"""

import streamlit as st
import subprocess
import os


st.set_page_config(
                page_title="SoulSync — Workspace Ergonomics Hub",
                page_icon="🧘",
                layout="wide")

            
st.markdown("""
    <style>  
    .main { background-color: #0F1115; }
    h1, h2, h3 { color: #E2E8F0 !important; font-family: 'Helvetica Neue', sans-serif; }
    .card { background-color: #161920; padding: 25px; border-radius: 12px; border-left: 5px solid #8EC472; margin-bottom: 20px; }
    .status-box { background-color: #1A1F2C; padding: 15px; border-radius: 8px; border: 1px solid #333; }
    </style>""", unsafe_allow_html=True)


st.title("🧘 SoulSync Workspace Intelligence")
st.caption("AI-Driven Real-time Postural Diagnostics & Kinetic Coaching")
st.markdown("---")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    <div class="card">
        <h3>🚀 System Diagnostic Overview</h3>
        <p style="color: #A0AEC0;">SoulSync uses an integrated deep learning LSTM network to track structural skeletal alignment via your webcam. The system runs locally to analyze positional fatigue, dynamically providing live, non-blocking verbal corrections.</p>
        <ul style="color: #CBD5E0;">
            <li><b>Posture Framework:</b> MediaPipe Pose Tracking (Muted Executive Specs)</li>
            <li><b>Classification Engine:</b> 30-Frame Rolling Window Temporal LSTM Network</li>
            <li><b>Audio Synthesis:</b> Windows Native SAPI Engine</li>
        </ul>
    </div>""", unsafe_allow_html=True)
    
    st.subheader("🎮 Core Engine Controller")
    st.write("Click below to initialize the camera capturing pipeline and engagement drivers.")

    
    if st.button("▶️ LAUNCH SOULSYNC CORE ENGINE", use_container_width=True):
        st.success("🤖 Core Engine Booting up... Watch your Windows taskbar for the Live Camera window!")
        
        # Point directly to your active virtual environment's execution path
        python_exe = r"H:\SoulSync\soul_venv\Scripts\python.exe"
        engine_script = os.path.join(os.path.dirname(__file__), "main_engine.py")
        
        try:
            # Spawns your original working script as its own pure process
            subprocess.Popen([python_exe, engine_script], shell=True)
        except Exception as e:
            st.error(f"Error launching core script: {e}")

    if st.button("⏹️ STOP ENGINE", use_container_width=True):
        os.system("taskkill /f /im python.exe")
        st.warning("⚠️ Engine stopped.")
 
    st.markdown("---")
    

    st.subheader("📖 How It Works")
    st.markdown("""
    <div class="card">
        <ol style="color: #CBD5E0; line-height: 2;">
            <li>Click <b>Launch</b> — the webcam window opens separately on your screen.</li>
            <li>SoulSync watches your posture every second using MediaPipe Pose.</li>
            <li>The LSTM model classifies your state as <b>Balanced</b>, <b>Slumped</b>, or <b>Restless</b>.</li>
            <li>When a state is detected with high confidence, a voice recommendation plays.</li>
            <li>Press <b>Q</b> inside the camera window or click <b>Stop Engine</b> to quit.</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)


with col2:
    st.subheader("📋 System Status")
    st.markdown("""
    <div class="status-box">
        <span style="color: #8EC472;">●</span> <b style="color: white;">Web Server:</b> Online<br>
        <span style="color: #8EC472;">●</span> <b style="color: white;">Virtual Env:</b> soul_venv<br>
        <span style="color: #8EC472;">●</span> <b style="color: white;">LSTM Layout:</b> Loaded
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("💡 Controls Reminder")
    st.info("Once the live camera stream opens up, press the **[ Q ]** key on your keyboard while clicking inside the video display frame to terminate the engine cleanly.")


    st.markdown("---")
 
    
    st.subheader("🌿 Quick Wellness Tips")
    st.markdown("""
    - Sit with feet flat on the floor
    - Keep your screen at eye level
    - Take a 5-minute break every hour
    - Roll your shoulders every 30 minutes
    - Stay hydrated throughout the day
    """)