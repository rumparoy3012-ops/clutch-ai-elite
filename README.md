# ⚡ Clutch AI Elite: The Last-Minute Life Saver

**Clutch AI Elite** is an advanced Python + Streamlit application designed for the "Vibe2Ship" Hackathon. It targets the "Last-Minute Life Saver" challenge by using gamified focus triggers, cognitive friction assessments, and autonomous asset generation to break deadline paralysis and turn procrastination into rapid execution.

---

## 🚀 Core Features

### 1. 📊 Cognitive Friction Calculator & Micro-Steps
* **Friction Analytics**: Sliders diagnostic questions (Complexity, Fatigue, Clarity of Requirements, and Distractions) are converted into a unified **Cognitive Friction Index** (1-10) using weight-based reasoning formulas.
* **Modern Gauge Rendering**: Renders a dynamic, dark-themed radial gauge chart built using Plotly with threshold warning states (Green/Amber/Red).
* **De-Paralysis Micro-Steps**: Instantly drafts three customized, sequential **15-minute action items** mapping directly to the user's specific high-friction scores to make starting feel achievable.

### 2. ⌨️ Kinetic Flow Icebreaker (Gamified Typing Game)
* **Neural Activation**: Overcomes the physical inertia of procrastination by forcing a 120-second speed-typing challenge before unlocking project resources.
* **Interactive Monospace Editor**: Features a custom Javascript-based interface styled like Monkeytype, computing **WPM** (Words Per Minute) and **Accuracy** on the fly.
* **Success Lock**: Characters are color-coded in real-time (green/red). Typing the starter code block successfully with $\geq 80\%$ accuracy unlocks a cryptographic verification code (`CLUTCH-FLOW-2026`) that is submitted to gain access to the main generator workspace.

### 3. 🎁 Autonomous Asset Delivery
* **Zero-Friction Templates**: Provides fully functional starter boilerplate code (React modules, python scripts, HTML layouts), professional communications (extension requests, status updates), or essay outlines based on the task description.
* **Gemini 2.5 Integration**: Uses the new official `google-genai` SDK to dynamically query `gemini-2.5-flash` for tailored, high-performance assets.
* **Intelligent Offline Fallback**: Features a built-in semantic keyword processor that serves pre-constructed, high-quality boilerplates if no Gemini API key is configured.

### 4. 🚨 Dynamic UI States
* **Standard Mode**: Calm, structured deep slate/indigo dashboard styling focusing on task definition and planning.
* **Emergency Execution Arena**: Automatically triggers if the deadline is under 6 hours away (or simulated manually). Swaps page layouts to an intense, distraction-free charcoal/crimson layout with animated pulse shadows, blinking headers, and a client-side Pomodoro timer focused entirely on execution.

---

## 🛠 Setup & Installation

### Prerequisites
* Python 3.10+
* Git

### Local Deployment
1. Clone the repository:
   ```bash
   git clone https://github.com/[Your-Username]/clutch-ai-elite.git
   cd clutch-ai-elite
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   streamlit run app.py
   ```
   *The application will open on `http://localhost:8501`.*

---

## ⚙️ Project Structure
```
clutch-ai-elite/
│
├── app.py                # Main application code (Aesthetics, CSS, Calculations, HTML typing component)
├── requirements.txt      # Dependency specification (streamlit, google-genai, plotly, pandas)
├── .gitignore            # Git exclusion patterns
└── README.md             # Project documentation and submission template
```

---

## ⚡ Hackathon Submission Info
* **Project Name**: Clutch AI Elite
* **Tagline**: Breaking Procrastination with Cognitive Analytics & Kinetic Gamification
* **Challenge**: The Last-Minute Life Saver (Vibe2Ship)
