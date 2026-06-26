import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import datetime
import time
import os
import json
from google import genai
from google.genai import types

# Page Configurations
st.set_page_config(
    page_title="Clutch AI Elite - Last-Minute Life Saver",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------- SESSION STATE INITIALIZATION -----------------
if "deadline_time" not in st.session_state:
    st.session_state.deadline_time = datetime.datetime.now() + datetime.timedelta(hours=8)
if "emergency_override" not in st.session_state:
    st.session_state.emergency_override = False
if "unlocked" not in st.session_state:
    st.session_state.unlocked = False
if "task_name" not in st.session_state:
    st.session_state.task_name = "Hackathon App Prototype"
if "selected_template_idx" not in st.session_state:
    st.session_state.selected_template_idx = 0
if "wpm" not in st.session_state:
    st.session_state.wpm = 0.0
if "accuracy" not in st.session_state:
    st.session_state.accuracy = 0.0
if "panic_calculated" not in st.session_state:
    st.session_state.panic_calculated = False
if "calculated_score" not in st.session_state:
    st.session_state.calculated_score = 5.0
if "micro_steps" not in st.session_state:
    st.session_state.micro_steps = []
if "asset_generated" not in st.session_state:
    st.session_state.asset_generated = None

# Typing Game Templates
TYPING_TEMPLATES = [
    {
        "name": "Python Execution Protocol",
        "text": "import sys, time; print('Initialize clutch protocol: ready to execute.')"
    },
    {
        "name": "React Landing Component",
        "text": "export default function Hero() { return <h1 class='glow'>Fast Dev Arena</h1>; }"
    },
    {
        "name": "HTML Emergency Banner",
        "text": "<div class='arena-warning'>⚠️ Time is ticking. Execute code now!</div>"
    },
    {
        "name": "CSS Pulse Accent Glow",
        "text": "@keyframes pulse { 0% { opacity: 0.4; } 100% { opacity: 1.0; } }"
    }
]

# ----------------- DESIGN SYSTEM / CUSTOM CSS -----------------
# Determine if we are in Emergency Arena Mode (< 6 hours remaining or override active)
now = datetime.datetime.now()
time_diff = st.session_state.deadline_time - now
hours_left = time_diff.total_seconds() / 3600.0
is_emergency = (hours_left < 6.0 and hours_left > 0.0) or st.session_state.emergency_override

# Custom CSS variables based on Mode
if is_emergency:
    bg_gradient = "radial-gradient(circle at 50% 10%, #200404 0%, #0d0101 100%)"
    card_bg = "rgba(42, 10, 10, 0.75)"
    border_color = "rgba(239, 68, 68, 0.5)"
    accent_color = "#ef4444"
    accent_glow = "rgba(239, 68, 68, 0.4)"
    header_text = "EMERGENCY EXECUTION ARENA"
    pulse_class = "pulse-emergency"
else:
    bg_gradient = "radial-gradient(circle at 50% 10%, #151829 0%, #0b0c15 100%)"
    card_bg = "rgba(22, 26, 44, 0.75)"
    border_color = "rgba(99, 102, 241, 0.3)"
    accent_color = "#6366f1"
    accent_glow = "rgba(99, 102, 241, 0.2)"
    header_text = "CLUTCH AI ELITE"
    pulse_class = "pulse-standard"

# Injected CSS stylesheet
css_style = f"""
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=JetBrains+Mono&display=swap" rel="stylesheet">
<style>
    /* Main body background overlay */
    .stApp {{
        background: {bg_gradient} !important;
        color: #f1f5f9 !important;
        font-family: 'Outfit', sans-serif !important;
    }}
    
    /* Headers styling */
    h1, h2, h3, h4, h5, h6 {{
        font-family: 'Outfit', sans-serif !important;
        font-weight: 800 !important;
        color: #ffffff !important;
    }}
    
    /* Glowing main title */
    .glowing-title {{
        font-size: 3rem;
        background: linear-gradient(90deg, #ffffff, {accent_color});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 20px {accent_glow};
        text-align: center;
        margin-bottom: 5px;
    }}
    
    /* Modern Glassmorphic Container */
    .clutch-card {{
        background: {card_bg} !important;
        border: 1px solid {border_color} !important;
        border-radius: 16px !important;
        padding: 24px !important;
        box-shadow: 0 10px 30px 0 rgba(0, 0, 0, 0.5) !important;
        backdrop-filter: blur(12px) !important;
        margin-bottom: 24px !important;
        transition: all 0.3s ease !important;
    }}
    .clutch-card:hover {{
        border-color: {accent_color} !important;
        box-shadow: 0 10px 40px 0 {accent_glow} !important;
    }}
    
    /* Custom button aesthetics */
    .stButton>button {{
        background: linear-gradient(135deg, {accent_color} 0%, #4f46e5 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 15px {accent_glow} !important;
        transition: all 0.2s ease-in-out !important;
    }}
    .stButton>button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px {accent_glow} !important;
    }}
    .stButton>button:active {{
        transform: translateY(0px) !important;
    }}
    
    /* Live emergency warning indicator */
    .emergency-banner {{
        background: linear-gradient(90deg, #7f1d1d 0%, #ef4444 50%, #7f1d1d 100%);
        border: 2px solid #f87171;
        border-radius: 8px;
        padding: 12px;
        text-align: center;
        font-weight: bold;
        font-size: 1.2rem;
        margin-bottom: 25px;
        animation: warning-pulse 2s infinite;
        box-shadow: 0 0 15px rgba(239, 68, 68, 0.4);
    }}
    @keyframes warning-pulse {{
        0% {{ opacity: 0.8; box-shadow: 0 0 10px rgba(239, 68, 68, 0.4); }}
        50% {{ opacity: 1.0; box-shadow: 0 0 25px rgba(239, 68, 68, 0.7); }}
        100% {{ opacity: 0.8; box-shadow: 0 0 10px rgba(239, 68, 68, 0.4); }}
    }}
    
    /* Monospace formatting for inputs/code */
    code, pre {{
        font-family: 'JetBrains Mono', monospace !important;
    }}
</style>
"""
st.markdown(css_style, unsafe_allow_html=True)

# ----------------- OFFLINE BOILERPLATE DICTIONARIES -----------------
def generate_offline_asset(task_desc, asset_type):
    task_desc_lower = task_desc.lower()
    
    if asset_type == "Code Boilerplate":
        if "react" in task_desc_lower or "web" in task_desc_lower or "html" in task_desc_lower or "js" in task_desc_lower:
            return """# Modern React Hero Component (Offline Template)
```jsx
import React, { useState, useEffect } from 'react';

// Live Demo Ready Hero Component with Tailwind/CSS styling
export default function HeroSection() {
  const [isActive, setIsActive] = useState(false);
  const [timeLeft, setTimeLeft] = useState(600); // 10 minutes

  useEffect(() => {
    if (timeLeft <= 0) return;
    const interval = setInterval(() => {
      setTimeLeft(prev => prev - 1);
    }, 1000);
    return () => clearInterval(interval);
  }, [timeLeft]);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
  };

  return (
    <div className="relative min-h-screen bg-slate-950 text-white flex flex-col justify-center items-center overflow-hidden">
      {/* Glassmorphic backdrop radial glow */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(79,70,229,0.15)_0,transparent_60%)]" />
      
      <div className="z-10 text-center max-w-2xl px-6">
        <span className="px-3 py-1 text-xs font-semibold bg-indigo-500/20 text-indigo-300 rounded-full border border-indigo-500/30 uppercase tracking-widest">
          Launch Ready
        </span>
        <h1 className="mt-6 text-5xl md:text-6xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-200 to-indigo-400">
          Supercharge Your Workflow
        </h1>
        <p className="mt-4 text-slate-400 text-lg">
          Zero friction boilerplate code designed for instant deployment. Copy, paste, customize, and deliver on time.
        </p>
        
        <div className="mt-8 flex flex-col sm:flex-row gap-4 justify-center">
          <button 
            onClick={() => setIsActive(!isActive)}
            className="px-8 py-3 bg-indigo-600 hover:bg-indigo-500 active:scale-95 transition rounded-lg font-medium shadow-lg shadow-indigo-600/30"
          >
            {isActive ? "✓ Execution Started" : "Activate Engine"}
          </button>
          <div className="px-6 py-3 bg-slate-900 border border-slate-800 rounded-lg flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-emerald-500 animate-ping" />
            <span className="text-sm font-mono text-slate-300">Countdown: {formatTime(timeLeft)}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
```
**Actionable Execution Tip**: Place this React boilerplate directly in a new file `HeroSection.jsx` and import it into your main App. Run `npm run dev` to see it live immediately.
"""
        elif "python" in task_desc_lower or "script" in task_desc_lower or "data" in task_desc_lower or "csv" in task_desc_lower:
            return """# High-Performance Python Data Processor (Offline Template)
```python
import pandas as pd
import numpy as np
import time
import os

class DataProcessor:
    def __init__(self, file_path: str):
        self.file_path = file_path
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Input file {file_path} not found.")
            
    def load_data(self) -> pd.DataFrame:
        print(f"[*] Loading dataset from: {self.file_path}")
        start = time.time()
        try:
            self.df = pd.read_csv(self.file_path)
        except Exception:
            self.df = pd.read_csv(self.file_path, sep=None, engine='python')
        print(f"[✓] Loaded {len(self.df)} rows in {time.time() - start:.2f}s")
        return self.df
        
    def clean_missing_values(self, strategy: str = "median") -> pd.DataFrame:
        print(f"[*] Cleaning missing values using strategy: {strategy}")
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if self.df[col].isnull().any():
                if strategy == "median":
                    fill_val = self.df[col].median()
                elif strategy == "mean":
                    fill_val = self.df[col].mean()
                else:
                    fill_val = 0
                self.df[col] = self.df[col].fillna(fill_val)
        return self.df

    def generate_stats_summary(self, output_path: str) -> None:
        print(f"[*] Generating profiling report...")
        summary = self.df.describe(include='all').transpose()
        summary['missing_percentage'] = (self.df.isnull().sum() / len(self.df)) * 100
        summary.to_csv(output_path)
        print(f"[✓] Report successfully written to {output_path}")

if __name__ == "__main__":
    # Create sample CSV file for demo testing
    sample_path = "sample_data.csv"
    pd.DataFrame({
        'timestamp': pd.date_range(start='2026-01-01', periods=100, freq='H'),
        'metric_a': np.random.randint(10, 100, size=100),
        'metric_b': np.random.choice([np.nan, 2.5, 3.6, 8.1, 4.4], size=100),
        'status': np.random.choice(['Success', 'Failure', 'Pending'], size=100)
    }).to_csv(sample_path, index=False)
    
    # Run processor
    processor = DataProcessor(sample_path)
    df = processor.load_data()
    processor.clean_missing_values(strategy="median")
    processor.generate_stats_summary("data_profile.csv")
    
    print("[✓] Process completed successfully!")
```
**Actionable Execution Tip**: Run this script locally using `python data_processor.py` (after placing this code in a file). It automatically handles missing dataset files by creating a mockup CSV configuration file.
"""
        else:
            return """# General Purpose Streamlit Application Boilerplate (Offline Template)
```python
import streamlit as st
import pandas as pd
import numpy as np
import time

st.set_page_config(page_title="Sprint Prototype", layout="wide")

# Modern Styling injection
st.markdown(\"\"\"
<style>
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px;
        border-radius: 8px;
        text-align: center;
    }
</style>
\"\"\", unsafe_allow_html=True)

st.title("⚡ Sprint Prototype Dashboard")
st.caption("Auto-generated mockup configuration boilerplate.")

# Create columns for metric cards
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown('<div class="metric-card"><h3>📈 Sales</h3><h2>$12,480</h2><span style="color:#00cc66">▲ +12%</span></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="metric-card"><h3>👥 Visitors</h3><h2>3,820</h2><span style="color:#00cc66">▲ +8%</span></div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="metric-card"><h3>⏱ Load Time</h3><h2>180ms</h2><span style="color:#ff3333">▼ -4%</span></div>', unsafe_allow_html=True)

st.subheader("Data Analysis")
data = pd.DataFrame(np.random.randn(50, 3), columns=['Metric A', 'Metric B', 'Metric C'])
st.line_chart(data)
```
**Actionable Execution Tip**: Copy this script into a local python file (e.g., `dashboard.py`) and run `streamlit run dashboard.py` in your terminal to see the live metrics layout.
"""
            
    elif asset_type == "Email Draft":
        if "extension" in task_desc_lower or "deadline" in task_desc_lower or "late" in task_desc_lower or "professor" in task_desc_lower or "manager" in task_desc_lower:
            return """# Deadline Extension Request (Offline Template)

**Subject:** Request for Extension: [Project/Assignment Name] - [Your Full Name]

Dear [Professor Name / Manager Name],

I am writing to request a brief extension for the submission of [Project/Assignment Name], which is currently scheduled for [Original Deadline]. 

Despite my best efforts, [optional: state a professional reason, e.g., I have encountered unexpected challenges with integrating the third-party API / I have had a sudden health setback]. I want to ensure that the work I deliver meets a high standard of quality, and having an extra [number of days, e.g., 24/48 hours] would allow me to finalize and thoroughly debug the final system.

Would it be possible to submit the completed work by [Proposed New Date & Time]? I am happy to share a draft of my current progress if that would help.

Thank you very much for your understanding and consideration.

Best regards,

[Your Name]  
[Your Contact Info / Student ID]  

**Actionable Execution Tip**: Personalize the bracketed areas `[...]` and send this email immediately. Sending requests *before* the actual deadline passes shows transparency and professionalism.
"""
        else:
            return """# Project Status Update (Offline Template)

**Subject:** Project Status Check-in & Blockers Update: [Project Name]

Dear [Stakeholder / Manager Name],

I wanted to provide a quick status update regarding the [Project Name] deliverables. 

We have successfully completed:
- Core module structure and basic page routing
- Setup of the local data pipelines

Current challenges / focus area:
- Finalizing the styling integration and verifying browser compatibility
- Resolving edge-case network issues with the external model endpoint

I am currently on track to finalize the execution. We expect to complete the testing by [Time/Date]. I will reach out if any critical blockers arise that require your review.

Best regards,

[Your Name]  

**Actionable Execution Tip**: Send this email to keep managers or clients updated. Transparency about progress and blockers prevents last-minute surprises.
"""
            
    elif asset_type == "Project / Essay Outline":
        if "essay" in task_desc_lower or "paper" in task_desc_lower or "ethics" in task_desc_lower:
            return """# Structured Essay Outline (Offline Template)

### Title: The Impact of Critical Deadlines on Creative Output

#### I. Introduction
*   **Hook**: The countdown clock as a psychological catalyst.
*   **Context**: Procrastination vs. structured flow in rapid development.
*   **Thesis Statement**: While late-stage work limits drafting cycles, high-arousal time limits can enhance focus and force essential design simplification.

#### II. Section 1: The Psychology of Procrastination and the Clutch Reflex
*   **Key Concept**: Yerkes-Dodson Law (Arousal-performance relationship).
*   **Supporting Point**: How cognitive friction prevents the activation of starting, and how low-stake templates break this barrier.

#### III. Section 2: Methodology & Core Case Studies
*   **Example A**: Hackathon timeframes (24-48h formats).
*   **Example B**: Academic submission deadlines and quality variance.

#### IV. Conclusion
*   **Summary**: Reiteration of the main thesis points.
*   **Final Thought**: The role of automation systems in turning panic into creative execution.

**Actionable Execution Tip**: Use this outline as your header layout. Write 2-3 paragraphs for each section, focusing first on getting words on the page before editing.
"""
        else:
            return """# System Architecture & Development Roadmap (Offline Template)

### Project Roadmap: Clutch AI Elite Platform

#### Phase 1: Interactive Front-End Mockup (Duration: 4 Hours)
*   Draft responsive sidebar structure with parameters.
*   Implement standard/emergency custom CSS modes.
*   Build the Plotly gauge calculator for panic and friction stats.

#### Phase 2: Core Workflows & Logic (Duration: 6 Hours)
*   Integrate Monkeytype-style HTML typing game widget.
*   Establish state validations for typing verification codes.
*   Implement local template repositories for fallback states.

#### Phase 3: Gemini API Integration (Duration: 2 Hours)
*   Configure Google GenAI client instance.
*   Test prompts and response parsing models.

**Actionable Execution Tip**: Create a kanban board or markdown checklist based on this outline. Focus exclusively on finishing Phase 1 first to establish a working prototype.
"""

# ----------------- SIDEBAR INTERFACES -----------------
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>⚙️ CONTROL STATION</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Task input config
    st.session_state.task_name = st.text_input("🎯 Target Task Name", value=st.session_state.task_name)
    
    # Deadline setting
    st.markdown("📅 **Set Task Deadline**")
    d_date = st.date_input("Deadline Date", value=st.session_state.deadline_time.date())
    d_time = st.time_input("Deadline Time", value=st.session_state.deadline_time.time())
    st.session_state.deadline_time = datetime.datetime.combine(d_date, d_time)
    
    # Manual Override for Demo Mode
    st.session_state.emergency_override = st.checkbox(
        "🚨 Force Emergency UI Mode",
        value=st.session_state.emergency_override,
        help="Simulate the Emergency Execution Arena layout styling instantly."
    )
    
    # API key setup
    st.markdown("🔑 **Gemini API Setup**")
    api_key_input = st.text_input(
        "Enter Gemini API Key",
        type="password",
        value=os.environ.get("GEMINI_API_KEY", ""),
        help="Optional: The app will run offline template fallbacks if not supplied."
    )
    
    st.markdown("---")
    
    # Focus Pomodoro Component in Sidebar (Vanilla Client-Side JS)
    pomo_html = """
    <div style="font-family: 'Outfit', sans-serif; color: white; background: rgba(255, 255, 255, 0.05); padding: 15px; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.1); text-align: center; margin-top: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
      <h4 style="margin: 0 0 10px 0; color: #ffeb3b; font-size: 0.95rem; letter-spacing: 0.05em;">⏱ FOCUS POMODORO</h4>
      <div id="pomo-timer" style="font-size: 2rem; font-weight: 800; margin-bottom: 12px; font-family: monospace; color: #ffffff; text-shadow: 0 0 10px rgba(255,255,255,0.2);">25:00</div>
      <button id="pomo-btn" style="background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%); border: none; color: white; padding: 8px 20px; border-radius: 6px; cursor: pointer; font-weight: bold; width: 100%; transition: all 0.2s;">Start Focus Session</button>
    </div>

    <script>
        let pomoTime = 1500; // 25 minutes
        let pomoActive = false;
        let pomoInterval = null;
        const pomoTimerEl = document.getElementById("pomo-timer");
        const pomoBtn = document.getElementById("pomo-btn");

        pomoBtn.addEventListener("click", () => {
            if (pomoActive) {
                clearInterval(pomoInterval);
                pomoActive = false;
                pomoBtn.textContent = "Resume Focus";
                pomoBtn.style.background = "linear-gradient(135deg, #4f46e5 0%, #6366f1 100%)";
            } else {
                pomoActive = true;
                pomoBtn.textContent = "Pause Session";
                pomoBtn.style.background = "linear-gradient(135deg, #ef4444 0%, #b91c1c 100%)";
                pomoInterval = setInterval(() => {
                    pomoTime--;
                    let mins = Math.floor(pomoTime / 60);
                    let secs = pomoTime % 60;
                    pomoTimerEl.textContent = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
                    if (pomoTime <= 0) {
                        clearInterval(pomoInterval);
                        pomoTimerEl.textContent = "TIME OUT!";
                        pomoActive = false;
                        pomoBtn.textContent = "Restart Focus";
                        pomoBtn.style.background = "linear-gradient(135deg, #10b981 0%, #059669 100%)";
                        pomoTime = 1500;
                    }
                }, 1000);
            }
        });
    </script>
    """
    st.components.v1.html(pomo_html, height=160)
    
    # Cheat/Bypass button for test convenience
    st.markdown("🤖 **Testing / Hackathon Grading Tools**")
    if st.button("⚡ Quick Unlock (Bypass Icebreaker)"):
        st.session_state.unlocked = True
        st.success("Developer mode: assets unlocked!")

# ----------------- MAIN APP HEADER -----------------
st.markdown(f"<div class='glowing-title'>{header_text}</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #a5b4fc; font-size: 1.1rem; margin-bottom: 25px;'>⚡ Peak Productivity Engine Designed for Procrastinating Geniuses ⚡</p>", unsafe_allow_html=True)

# Render Emergency Arena active header if criteria met
if is_emergency:
    st.markdown(
        f"""
        <div class="emergency-banner">
            🚨 CRITICAL EMERGENCY MODE ACTIVE ({hours_left:.1f}h REMAINING). NO DISTRACTIONS, ONLY LAUNCH READY EXECUTION.
        </div>
        """,
        unsafe_allow_html=True
    )

# ----------------- TWO COLUMN LAYOUT -----------------
col_left, col_right = st.columns([1, 1])

with col_left:
    # --- 1. COGNITIVE FRICTION CALCULATOR ---
    st.markdown(f"<div class='clutch-card'>", unsafe_allow_html=True)
    st.subheader("📊 Cognitive Friction Calculator")
    st.write("Assess the mental resistance preventing task completion.")
    
    complexity = st.slider("1. Task Complexity / Scope", 1, 10, 5, help="How large or difficult is the work?")
    fatigue = st.slider("2. Physical/Mental Fatigue", 1, 10, 4, help="How tired are you currently?")
    clarity = st.slider("3. Requirements Clarity", 1, 10, 7, help="Do you know exactly what is expected? (10 is very clear)")
    distraction = st.slider("4. Immediate Environment Distractions", 1, 10, 3, help="Are you being pulled away by social/ambient noise?")
    
    if st.button("Calculate Friction Level"):
        # Friction formulation
        score = (complexity * 0.35) + (fatigue * 0.25) + ((11 - clarity) * 0.25) + (distraction * 0.15)
        st.session_state.calculated_score = float(round(score, 1))
        st.session_state.panic_calculated = True
        
        # Build three 15-minute micro-steps based on attributes
        steps = []
        if clarity < 6:
            steps.append("🔍 Step 1 (15m): Set a timer, open a notepad, and write down 3 clear bullet points defining what 'completed' looks like.")
        elif fatigue > 7:
            steps.append("💧 Step 1 (15m): Do a physical reset. Drink a full glass of cold water, step outside, or do 2 minutes of breathing to clear neural fog.")
        else:
            steps.append("📂 Step 1 (15m): Set up the project files, workspace sandbox directories, and write down a single code file structure skeleton.")
            
        if complexity > 6:
            steps.append("✂️ Step 2 (15m): Cut the feature list in half. Define the Absolute Minimum Viable Product (MVP) core component to implement.")
        else:
            steps.append("📝 Step 2 (15m): Write the absolute easiest 15 lines of code, draft introductory headers, or outline the first core script.")
            
        if distraction > 6:
            steps.append("🔇 Step 3 (15m): Put phone in Do Not Disturb in another room, close all web browser tabs except Streamlit & docs, put on binaural beats.")
        else:
            steps.append("🚀 Step 3 (15m): Run the basic mock setup script to confirm local configurations compile properly before adding complex logic.")
            
        st.session_state.micro_steps = steps
        
    if st.session_state.panic_calculated:
        # Plotly custom dark-mode radial progress index gauge
        val = st.session_state.calculated_score
        bar_color = "#ef4444" if val > 7.0 else "#f59e0b" if val > 4.5 else "#10b981"
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = val,
            domain = {'x': [0, 1], 'y': [0, 1]},
            gauge = {
                'axis': {'range': [0, 10], 'tickwidth': 1, 'tickcolor': "#ffffff"},
                'bar': {'color': bar_color},
                'bgcolor': "rgba(255,255,255,0.05)",
                'borderwidth': 1,
                'bordercolor': "rgba(255, 255, 255, 0.2)",
                'steps': [
                    {'range': [0, 4.5], 'color': 'rgba(16, 185, 129, 0.15)'},
                    {'range': [4.5, 7.0], 'color': 'rgba(245, 158, 11, 0.15)'},
                    {'range': [7.0, 10.0], 'color': 'rgba(239, 68, 68, 0.15)'}
                ],
            }
        ))
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'color': "#ffffff", 'family': "Outfit, sans-serif"},
            height=200,
            margin=dict(l=15, r=15, t=30, b=15)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Display customized 15-minute micro steps
        st.markdown("🎯 **Actionable 15-Minute Micro-Steps:**")
        for step in st.session_state.micro_steps:
            st.checkbox(step, key=f"step_{step[:15]}")
            
    st.markdown("</div>", unsafe_allow_html=True)


with col_right:
    # --- 2. KINETIC FLOW ICEBREAKER ---
    st.markdown(f"<div class='clutch-card'>", unsafe_allow_html=True)
    st.subheader("⌨️ Kinetic Flow Icebreaker")
    st.write("Break deadline paralysis. Type out the snippet below in our gamified speed-typing sandbox to unlock the asset arena.")
    
    # Template Selection
    template_names = [t["name"] for t in TYPING_TEMPLATES]
    sel_idx = st.selectbox("Select Starter Code Snippet", range(len(template_names)), format_func=lambda i: template_names[i])
    st.session_state.selected_template_idx = sel_idx
    target_snippet = TYPING_TEMPLATES[sel_idx]["text"]
    
    st.markdown(f"**Target Snippet:**")
    st.code(target_snippet, language="python" if "Python" in template_names[sel_idx] else "html" if "HTML" in template_names[sel_idx] else "javascript" if "React" in template_names[sel_idx] else "css")
    
    # HTML Monkeytype-style typing challenger (custom JavaScript sandbox)
    challenge_payload = json.dumps(target_snippet)
    
    typing_game_html = f"""
    <div style="font-family: monospace; color: #a1a1aa; background: #0f1016; padding: 18px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.08); box-shadow: inset 0 2px 10px rgba(0,0,0,0.8);">
        <div id="text-display" style="font-size: 1.1rem; line-height: 1.6em; margin-bottom: 12px; user-select: none; pointer-events: none; white-space: pre-wrap; font-family: 'JetBrains Mono', monospace; word-break: break-all;"></div>
        <textarea id="text-input" placeholder="Start typing exactly what is shown above..." style="width: 95%; height: 60px; background: #161822; color: #ffffff; border: 1px solid rgba(255,255,255,0.15); padding: 10px; border-radius: 6px; font-family: 'JetBrains Mono', monospace; font-size: 1.05rem; resize: none; outline: none; transition: border 0.2s;"></textarea>
        <div style="display: flex; justify-content: space-between; margin-top: 12px; font-size: 0.95rem; font-family: 'Outfit', sans-serif;">
            <div style="color: #ef4444;">⏱ Timer: <span id="timer" style="font-weight: bold; font-size:1.1rem;">120</span>s</div>
            <div style="color: #fbbf24;">⚡ WPM: <span id="wpm" style="font-weight: bold; font-size:1.1rem;">0</span></div>
            <div style="color: #34d399;">🎯 Accuracy: <span id="accuracy" style="font-weight: bold; font-size:1.1rem;">100</span>%</div>
        </div>
        <div id="result-message" style="margin-top: 12px; padding: 10px; border-radius: 6px; font-family: 'Outfit', sans-serif; font-weight: bold; text-align: center; display: none;"></div>
    </div>

    <script>
        const targetText = {challenge_payload};
        const textDisplay = document.getElementById("text-display");
        const textInput = document.getElementById("text-input");
        const timerEl = document.getElementById("timer");
        const wpmEl = document.getElementById("wpm");
        const accuracyEl = document.getElementById("accuracy");
        const resultEl = document.getElementById("result-message");

        // Populate the container with target span nodes
        for (let char of targetText) {{
            let span = document.createElement("span");
            span.textContent = char;
            span.style.color = "#52525b"; // Muted gray
            textDisplay.appendChild(span);
        }}

        let startTime = null;
        let timerInterval = null;
        let timeLeft = 120;
        let challengeActive = false;
        let finished = false;

        textInput.addEventListener("input", () => {{
            if (!challengeActive && !finished) {{
                challengeActive = true;
                startTime = new Date().getTime();
                timerInterval = setInterval(updateTimer, 1000);
                textInput.style.borderColor = "#6366f1";
            }}
            
            if (finished) return;
            
            const typedVal = textInput.value;
            const spans = textDisplay.querySelectorAll("span");
            let correctChars = 0;
            
            for (let i = 0; i < spans.length; i++) {{
                const span = spans[i];
                if (i < typedVal.length) {{
                    if (typedVal[i] === targetText[i]) {{
                        span.style.color = "#34d399"; // Success green
                        span.style.backgroundColor = "transparent";
                        correctChars++;
                    }} else {{
                        span.style.color = "#f87171"; // Error red
                        span.style.backgroundColor = "rgba(239, 68, 68, 0.15)";
                    }}
                }} else {{
                    span.style.color = "#52525b";
                    span.style.backgroundColor = "transparent";
                }}
            }}
            
            let accuracy = typedVal.length > 0 ? Math.round((correctChars / typedVal.length) * 100) : 100;
            accuracyEl.textContent = accuracy;
            
            let elapsedMinutes = (new Date().getTime() - startTime) / 60000;
            let wpm = elapsedMinutes > 0 ? Math.round((typedVal.length / 5) / elapsedMinutes) : 0;
            wpmEl.textContent = wpm;
            
            if (typedVal.length >= targetText.length && accuracy >= 80) {{
                completeChallenge(true, accuracy, wpm);
            }}
        }});

        function updateTimer() {{
            timeLeft--;
            timerEl.textContent = timeLeft;
            
            let elapsedMinutes = (new Date().getTime() - startTime) / 60000;
            let wpm = elapsedMinutes > 0 ? Math.round((textInput.value.length / 5) / elapsedMinutes) : 0;
            wpmEl.textContent = wpm;
            
            if (timeLeft <= 0) {{
                clearInterval(timerInterval);
                const typedVal = textInput.value;
                let correct = 0;
                for(let i=0; i<typedVal.length; i++) {{
                    if(typedVal[i] === targetText[i]) correct++;
                }}
                let acc = typedVal.length > 0 ? Math.round((correct / typedVal.length) * 100) : 100;
                completeChallenge(acc >= 80, acc, wpm);
            }}
        }}

        function completeChallenge(success, accuracy, wpm) {{
            finished = true;
            challengeActive = false;
            clearInterval(timerInterval);
            textInput.disabled = true;
            
            if (success) {{
                resultEl.style.backgroundColor = "rgba(16, 185, 129, 0.15)";
                resultEl.style.color = "#34d399";
                resultEl.style.border = "1px solid rgba(16, 185, 129, 0.3)";
                resultEl.innerHTML = `🎉 Flow Activated! Verification Code: <span style='font-size:1.15rem; color:#facc15; font-family:monospace;'>CLUTCH-FLOW-2026</span>`;
                resultEl.style.display = "block";
            }} else {{
                resultEl.style.backgroundColor = "rgba(239, 68, 68, 0.15)";
                resultEl.style.color = "#f87171";
                resultEl.style.border = "1px solid rgba(239, 68, 68, 0.3)";
                resultEl.innerHTML = `❌ Accuracy too low (${{accuracy}}%). Try again.`;
                resultEl.style.display = "block";
            }}
        }}
    </script>
    """
    st.components.v1.html(typing_game_html, height=220)
    
    # Text input inside Streamlit to input verification code
    verification_code = st.text_input("🔑 Enter Verification Code to Unlock:", value="")
    if verification_code.strip() == "CLUTCH-FLOW-2026":
        st.session_state.unlocked = True
        st.success("Verification successful! Autonomous Asset Arena Unlocked!")
        
    st.markdown("</div>", unsafe_allow_html=True)


# ----------------- 3. AUTONOMOUS ASSET DELIVERY AREA -----------------
st.markdown("---")
st.markdown("## 🎁 Autonomous Asset Delivery")

if not st.session_state.unlocked:
    st.info("🔒 Complete the Kinetic Flow Icebreaker typing challenge above to unlock immediate assets.")
else:
    st.markdown(f"<div class='clutch-card'>", unsafe_allow_html=True)
    st.subheader(f"⚡ Work Area: {st.session_state.task_name}")
    st.write("Generate clean code configurations, email communications, or structure outlines with a click.")
    
    sub_col1, sub_col2 = st.columns([1, 2])
    with sub_col1:
        asset_type = st.selectbox("Asset Category", ["Code Boilerplate", "Email Draft", "Project / Essay Outline"])
        task_prompt_spec = st.text_area("Specific Instructions (Optional)", placeholder="e.g. Include React state counters / Ask for 48h to submit grading...")
        
        generate_btn = st.button("Generate Asset")
        
    with sub_col2:
        if generate_btn:
            with st.spinner("Executing clutch reasoning system..."):
                final_prompt = f"Create a {asset_type} for task '{st.session_state.task_name}'."
                if task_prompt_spec:
                    final_prompt += f" Special requirements: {task_prompt_spec}"
                
                # Check for Gemini key config
                if api_key_input.strip() != "":
                    try:
                        # Initialize new SDK client structure
                        client = genai.Client(api_key=api_key_input.strip())
                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=final_prompt
                        )
                        st.session_state.asset_generated = response.text
                        st.success("✓ Freshly generated by Gemini 2.5!")
                    except Exception as e:
                        st.error(f"Error calling API ({e}). Falling back to offline local library.")
                        st.session_state.asset_generated = generate_offline_asset(st.session_state.task_name, asset_type)
                else:
                    # Offline generation
                    st.info("Offline mode active. Delivering optimized boilerplate template.")
                    st.session_state.asset_generated = generate_offline_asset(st.session_state.task_name, asset_type)
        
        if st.session_state.asset_generated:
            st.markdown(st.session_state.asset_generated)
            
    st.markdown("</div>", unsafe_allow_html=True)
