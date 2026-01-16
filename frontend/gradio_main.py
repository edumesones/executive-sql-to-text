"""
Executive Analytics - Main Query App (Gradio)
Runs on port 7861 with freemium model (1 free query without login)
"""
import os
import uuid
import tempfile
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple

import gradio as gr
import httpx
import pandas as pd
import plotly.graph_objects as go

# =============================================================================
# CONFIGURATION
# =============================================================================

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
LANDING_URL = os.getenv("LANDING_URL", "http://localhost:7860")
FREE_QUERY_LIMIT = 1

# =============================================================================
# DARK THEME CSS
# =============================================================================

DARK_CSS = """
/* =====================================================
   EXECUTIVE ANALYTICS - DARK THEME
   ===================================================== */

/* Base Colors */
:root {
    --bg-primary: #0f0f1a !important;
    --bg-secondary: #1a1a2e !important;
    --bg-card: #252542 !important;
    --bg-elevated: #2d2d4a !important;
    --accent-primary: #667eea;
    --accent-secondary: #764ba2;
    --accent-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    --text-primary: #ffffff !important;
    --text-secondary: #b8b8d0 !important;
    --text-muted: #8888a0 !important;
    --border-color: #3d3d5c !important;
    --success: #10b981;
    --warning: #f59e0b;
    --error: #ef4444;

    --background-fill-primary: var(--bg-primary) !important;
    --background-fill-secondary: var(--bg-secondary) !important;
    --block-background-fill: var(--bg-card) !important;
    --color-text-body: var(--text-primary) !important;
    --color-text-subdued: var(--text-secondary) !important;
    --border-color-primary: var(--border-color) !important;
}

/* Global Background */
body, .gradio-container {
    background: var(--bg-primary) !important;
    min-height: 100vh;
}

.gradio-container {
    background: radial-gradient(ellipse at top, #1a1a2e 0%, #0f0f1a 70%) !important;
}

/* All text white by default */
.gradio-container * {
    color: var(--text-primary);
}

/* =====================================================
   HEADER SECTION
   ===================================================== */
.header-section {
    background: var(--accent-gradient);
    padding: 35px 40px;
    border-radius: 16px;
    margin-bottom: 25px;
    box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
}

.header-title {
    font-size: 2.2rem;
    font-weight: 700;
    margin: 0;
    color: #fff !important;
    text-shadow: 0 2px 10px rgba(0,0,0,0.2);
}

.header-subtitle {
    color: rgba(255,255,255,0.9) !important;
    margin-top: 10px;
    font-size: 1.1rem;
}

/* =====================================================
   DEMO INFO PANEL - HIGH VISIBILITY
   ===================================================== */
.demo-info-panel {
    background: linear-gradient(135deg, #252542 0%, #1f1f3a 100%);
    border: 2px solid #667eea;
    border-radius: 16px;
    padding: 25px 30px;
    margin: 20px 0;
    box-shadow: 0 8px 32px rgba(102, 126, 234, 0.15), inset 0 1px 0 rgba(255,255,255,0.05);
}

.demo-info-panel .demo-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 20px;
    padding-bottom: 15px;
    border-bottom: 1px solid rgba(102, 126, 234, 0.3);
}

.demo-info-panel .demo-icon {
    font-size: 2rem;
}

.demo-info-panel .demo-title {
    color: #a5b4fc !important;
    font-size: 1.4rem;
    font-weight: 700;
    margin: 0;
}

.demo-info-panel .demo-subtitle {
    color: #b8b8d0 !important;
    font-size: 0.95rem;
    margin-top: 5px;
}

.demo-info-panel .columns-section {
    background: rgba(102, 126, 234, 0.1);
    border-radius: 12px;
    padding: 18px;
    margin: 15px 0;
}

.demo-info-panel .columns-title {
    color: #c4b5fd !important;
    font-weight: 600;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 12px;
}

.demo-info-panel .column-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
}

.demo-info-panel .column-item {
    background: rgba(255,255,255,0.05);
    padding: 8px 12px;
    border-radius: 8px;
    border-left: 3px solid #667eea;
}

.demo-info-panel .column-name {
    color: #f0abfc !important;
    font-family: monospace;
    font-weight: 600;
    font-size: 0.9rem;
}

.demo-info-panel .column-desc {
    color: #9ca3af !important;
    font-size: 0.8rem;
    margin-top: 2px;
}

.demo-info-panel .examples-section {
    margin-top: 20px;
}

.demo-info-panel .examples-title {
    color: #34d399 !important;
    font-weight: 600;
    font-size: 0.95rem;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.demo-info-panel .example-queries {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}

.demo-info-panel .example-query {
    background: linear-gradient(135deg, rgba(52, 211, 153, 0.15) 0%, rgba(16, 185, 129, 0.1) 100%);
    border: 1px solid rgba(52, 211, 153, 0.4);
    color: #6ee7b7 !important;
    padding: 10px 16px;
    border-radius: 25px;
    font-size: 0.9rem;
    transition: all 0.2s;
}

.demo-info-panel .example-query:hover {
    background: linear-gradient(135deg, rgba(52, 211, 153, 0.25) 0%, rgba(16, 185, 129, 0.2) 100%);
    transform: translateY(-1px);
}

/* =====================================================
   STATUS BAR
   ===================================================== */
.status-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: var(--bg-card);
    padding: 12px 20px;
    border-radius: 12px;
    border: 1px solid var(--border-color);
    margin-bottom: 20px;
}

.api-status {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 16px;
    border-radius: 25px;
    font-size: 0.9rem;
    font-weight: 600;
}

.api-status.connected {
    background: rgba(16, 185, 129, 0.15);
    color: #34d399 !important;
    border: 1px solid rgba(16, 185, 129, 0.3);
}

.api-status.disconnected {
    background: rgba(239, 68, 68, 0.15);
    color: #f87171 !important;
    border: 1px solid rgba(239, 68, 68, 0.3);
}

/* =====================================================
   QUERY COUNTER
   ===================================================== */
.query-counter {
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.15) 0%, rgba(217, 119, 6, 0.1) 100%);
    border: 1px solid rgba(245, 158, 11, 0.4);
    border-radius: 25px;
    padding: 10px 20px;
    color: #fbbf24 !important;
    font-weight: 600;
    font-size: 0.9rem;
    text-align: center;
}

.query-counter.unlimited {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(5, 150, 105, 0.1) 100%);
    border-color: rgba(16, 185, 129, 0.4);
    color: #34d399 !important;
}

/* =====================================================
   VOICE INPUT SECTION
   ===================================================== */
.voice-accordion {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 12px !important;
    margin: 15px 0 !important;
    overflow: hidden;
}

.voice-accordion > .label-wrap {
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.15) 0%, rgba(124, 58, 237, 0.1) 100%) !important;
    padding: 12px 18px !important;
}

.voice-accordion .label-wrap span {
    color: #c4b5fd !important;
    font-weight: 600;
}

/* Audio component styling */
.voice-accordion .wrap {
    background: var(--bg-elevated) !important;
    padding: 20px !important;
}

/* =====================================================
   INPUT FIELDS & BUTTONS
   ===================================================== */
textarea, input[type="text"] {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border-color) !important;
    color: var(--text-primary) !important;
    border-radius: 12px !important;
}

textarea:focus, input[type="text"]:focus {
    border-color: #667eea !important;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2) !important;
}

/* Primary Button */
.primary-btn, button.primary {
    background: var(--accent-gradient) !important;
    border: none !important;
    color: white !important;
    font-weight: 600 !important;
    padding: 12px 28px !important;
    border-radius: 10px !important;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
    transition: all 0.3s !important;
}

.primary-btn:hover, button.primary:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4) !important;
}

/* Secondary Button */
button.secondary {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border-color) !important;
    color: var(--text-secondary) !important;
}

/* =====================================================
   SQL CODE BLOCK
   ===================================================== */
.code-block, pre, code {
    background: #1e1e3f !important;
    border: 1px solid #3d3d5c !important;
    border-radius: 12px !important;
    color: #e2e8f0 !important;
}

/* =====================================================
   RESULTS SECTION
   ===================================================== */
.results-header {
    color: var(--text-primary) !important;
    font-size: 1.3rem;
    font-weight: 700;
    margin-bottom: 15px;
    padding-bottom: 10px;
    border-bottom: 2px solid var(--accent-primary);
}

/* Tabs */
.tabs {
    background: var(--bg-card) !important;
    border-radius: 12px !important;
    border: 1px solid var(--border-color) !important;
    overflow: hidden;
}

.tab-nav {
    background: var(--bg-secondary) !important;
    border-bottom: 1px solid var(--border-color) !important;
}

.tab-nav button {
    color: var(--text-muted) !important;
    font-weight: 500;
    padding: 12px 24px !important;
}

.tab-nav button.selected {
    color: var(--text-primary) !important;
    background: var(--bg-card) !important;
    border-bottom: 2px solid var(--accent-primary) !important;
}

/* Data Table */
.dataframe, table {
    background: var(--bg-card) !important;
    border-radius: 8px !important;
}

.dataframe th {
    background: var(--bg-elevated) !important;
    color: #a5b4fc !important;
    font-weight: 600;
    padding: 12px !important;
}

.dataframe td {
    color: var(--text-secondary) !important;
    padding: 10px 12px !important;
    border-bottom: 1px solid var(--border-color) !important;
}

/* =====================================================
   LOGIN PROMPT
   ===================================================== */
.login-prompt {
    background: var(--accent-gradient);
    border-radius: 20px;
    padding: 45px;
    text-align: center;
    color: white !important;
    margin: 25px 0;
    box-shadow: 0 15px 50px rgba(102, 126, 234, 0.3);
}

.login-prompt h2 {
    margin-top: 0;
    font-size: 1.8rem;
    color: white !important;
}

.login-prompt p {
    color: rgba(255,255,255,0.9) !important;
    font-size: 1.1rem;
}

.login-prompt a.signup-btn {
    display: inline-block;
    background: white;
    color: #667eea !important;
    padding: 14px 35px;
    border-radius: 30px;
    text-decoration: none;
    font-weight: 700;
    font-size: 1rem;
    margin-top: 20px;
    transition: all 0.3s;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.login-prompt a.signup-btn:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.3);
}

.login-prompt .login-link {
    color: rgba(255,255,255,0.8) !important;
    margin-top: 15px;
}

.login-prompt .login-link a {
    color: white !important;
    text-decoration: underline;
}

/* =====================================================
   INSIGHTS BOX
   ===================================================== */
.insights-box {
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(37, 99, 235, 0.05) 100%);
    border-left: 4px solid #3b82f6;
    padding: 20px;
    margin: 15px 0;
    border-radius: 0 12px 12px 0;
}

.insights-box h3 {
    color: #93c5fd !important;
    margin-top: 0;
}

/* =====================================================
   FOOTER
   ===================================================== */
.footer {
    text-align: center;
    padding: 30px;
    color: var(--text-muted) !important;
    border-top: 1px solid var(--border-color);
    margin-top: 50px;
    font-size: 0.9rem;
}

/* =====================================================
   GRADIO OVERRIDES
   ===================================================== */
.block {
    background: transparent !important;
    border: none !important;
}

.wrap {
    background: var(--bg-card) !important;
}

label, .label {
    color: var(--text-secondary) !important;
    font-weight: 500 !important;
}

/* Accordion */
.accordion {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 12px !important;
}

.accordion .label-wrap {
    background: var(--bg-elevated) !important;
}
"""

# =============================================================================
# HTML TEMPLATES
# =============================================================================

HEADER_HTML = """
<div class="header-section">
    <h1 class="header-title">Executive Analytics Assistant</h1>
    <p class="header-subtitle">Ask questions about data in natural language</p>
</div>
"""

DEMO_INFO_HTML = """
<div class="demo-info-panel">
    <div class="demo-header">
        <span class="demo-icon">📊</span>
        <div>
            <h3 class="demo-title">Demo Database: Lending Club Loans</h3>
            <p class="demo-subtitle">Query a sample dataset with 100K+ loan records</p>
        </div>
    </div>

    <div class="columns-section">
        <div class="columns-title">📋 Available Columns</div>
        <div class="column-grid">
            <div class="column-item">
                <div class="column-name">loan_amnt</div>
                <div class="column-desc">Loan amount ($)</div>
            </div>
            <div class="column-item">
                <div class="column-name">int_rate</div>
                <div class="column-desc">Interest rate (%)</div>
            </div>
            <div class="column-item">
                <div class="column-name">grade</div>
                <div class="column-desc">Grade A-G</div>
            </div>
            <div class="column-item">
                <div class="column-name">loan_status</div>
                <div class="column-desc">Current status</div>
            </div>
            <div class="column-item">
                <div class="column-name">purpose</div>
                <div class="column-desc">Loan purpose</div>
            </div>
            <div class="column-item">
                <div class="column-name">addr_state</div>
                <div class="column-desc">Borrower state</div>
            </div>
        </div>
    </div>

    <div class="examples-section">
        <div class="examples-title">💡 Try these queries</div>
        <div class="example-queries">
            <span class="example-query">"Show top 10 loans by amount"</span>
            <span class="example-query">"Default rate by grade?"</span>
            <span class="example-query">"Average interest rate by state"</span>
        </div>
    </div>
</div>
"""

LOGIN_PROMPT_HTML = f"""
<div class="login-prompt">
    <h2>🔒 Free Query Used!</h2>
    <p>You've used your free query. Sign up to continue with unlimited access.</p>
    <a href="{LANDING_URL}#auth-section" class="signup-btn">Sign Up Free</a>
    <p class="login-link">
        Already have an account? <a href="{LANDING_URL}#auth-section">Log in</a>
    </p>
</div>
"""

FOOTER_HTML = """
<div class="footer">
    Executive Analytics v0.2.0 | Powered by LangGraph & OpenAI
</div>
"""

# =============================================================================
# API CLIENT FUNCTIONS
# =============================================================================

def check_api_health() -> Tuple[bool, str]:
    """Check if API is available"""
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(f"{API_BASE_URL}/api/health")
            if response.status_code == 200:
                data = response.json()
                return True, data.get("status", "healthy")
            return False, "error"
    except httpx.ConnectError:
        return False, "disconnected"
    except Exception as e:
        return False, str(e)


def execute_query(query: str, session_id: str) -> Dict[str, Any]:
    """Execute query via demo endpoint"""
    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                f"{API_BASE_URL}/api/demo-query",
                json={"query": query, "session_id": session_id}
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        return {"errors": [f"API Error: {e.response.status_code}"]}
    except httpx.ConnectError:
        return {"errors": ["Cannot connect to API. Is the server running?"]}
    except httpx.ReadTimeout:
        return {"errors": ["Query timed out. Try a simpler question."]}
    except Exception as e:
        return {"errors": [f"Error: {str(e)}"]}


# =============================================================================
# VOICE TRANSCRIPTION
# =============================================================================

def transcribe_audio(audio_path: Optional[str]) -> str:
    """Transcribe audio using speech recognition"""
    if not audio_path:
        return ""

    try:
        import speech_recognition as sr

        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio_data = recognizer.record(source)

        # Try Whisper first (offline)
        try:
            text = recognizer.recognize_whisper(audio_data, language="en")
            return text.strip()
        except Exception:
            pass

        # Fallback to Google (requires internet)
        try:
            text = recognizer.recognize_google(audio_data)
            return text.strip()
        except Exception:
            pass

        return "[Could not transcribe audio]"
    except ImportError:
        return "[Speech recognition not installed]"
    except Exception as e:
        return f"[Transcription error: {str(e)}]"


# =============================================================================
# RESULT FORMATTING
# =============================================================================

def format_chart(chart_config: Optional[Dict]) -> Optional[go.Figure]:
    """Convert API chart config to Plotly figure"""
    if not chart_config:
        return None
    try:
        fig = go.Figure(chart_config)
        # Apply dark theme
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        return fig
    except Exception:
        return None


def format_dataframe(data: Optional[List[Dict]]) -> pd.DataFrame:
    """Convert query results to DataFrame"""
    if not data:
        return pd.DataFrame()
    return pd.DataFrame(data)


def format_insights(insights: List[str], recommendations: List[str]) -> str:
    """Format insights and recommendations as markdown"""
    output = ""

    if insights:
        output += "### Key Insights\n\n"
        for i, insight in enumerate(insights, 1):
            output += f"**{i}.** {insight}\n\n"

    if recommendations:
        output += "### Recommendations\n\n"
        for i, rec in enumerate(recommendations, 1):
            output += f"**{i}.** {rec}\n\n"

    return output if output else "*No insights generated for this query.*"


def create_csv_file(df: pd.DataFrame) -> Optional[str]:
    """Create a temporary CSV file for download"""
    if df is None or df.empty:
        return None

    try:
        filename = f"query_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join(tempfile.gettempdir(), filename)
        df.to_csv(filepath, index=False)
        return filepath
    except Exception:
        return None


# =============================================================================
# MAIN APP
# =============================================================================

def create_main_app() -> gr.Blocks:
    """Create the main query application"""

    with gr.Blocks(title="Executive Analytics") as app:
        # State
        session_id = gr.State(value=str(uuid.uuid4()))
        query_count = gr.State(value=0)

        # Header
        gr.HTML(HEADER_HTML)

        # Status Row
        with gr.Row():
            with gr.Column(scale=3):
                api_status_html = gr.HTML(value="<span class='api-status'>Checking...</span>")
            with gr.Column(scale=1):
                query_counter_html = gr.HTML(
                    value=f"<div class='query-counter'>Free queries: {FREE_QUERY_LIMIT}/{FREE_QUERY_LIMIT}</div>"
                )

        # Demo Info Panel
        demo_panel = gr.HTML(value=DEMO_INFO_HTML)

        # Login Prompt (hidden initially)
        login_prompt = gr.HTML(value=LOGIN_PROMPT_HTML, visible=False)

        # Main Query Interface
        with gr.Row():
            with gr.Column(scale=2):
                # Query Input
                query_input = gr.Textbox(
                    label="💬 Ask your question",
                    placeholder="e.g., Show me top 10 loans by amount...",
                    lines=3
                )

                # Voice Input
                with gr.Accordion("🎤 Voice Input", open=False, elem_classes=["voice-accordion"]):
                    gr.Markdown("*Click the microphone to record your question, then click Transcribe*")
                    voice_input = gr.Audio(
                        sources=["microphone"],
                        type="filepath",
                        label="Record your question"
                    )
                    transcribe_btn = gr.Button("🎯 Transcribe to Text", size="sm", variant="secondary")

                # Action Buttons
                with gr.Row():
                    submit_btn = gr.Button(
                        "🔍 Analyze",
                        variant="primary",
                        elem_classes=["primary-btn"]
                    )
                    clear_btn = gr.Button("🗑️ Clear", variant="secondary")

            with gr.Column(scale=1):
                # SQL Output
                sql_output = gr.Code(
                    label="Generated SQL",
                    language="sql",
                    interactive=False,
                    lines=8
                )

        # Results Section (hidden initially)
        results_section = gr.Column(visible=False)
        with results_section:
            gr.Markdown("## Results")

            with gr.Tabs():
                with gr.TabItem("Data Table"):
                    results_table = gr.Dataframe(
                        label="Query Results",
                        interactive=False,
                        wrap=True
                    )
                    download_btn = gr.Button("Download CSV", size="sm")
                    download_file = gr.File(label="Download", visible=False)

                with gr.TabItem("Visualization"):
                    chart_output = gr.Plot(label="Chart")

            # Insights
            insights_output = gr.Markdown(label="Insights")

        # Error Display
        error_output = gr.Markdown(visible=False)

        # Footer
        gr.HTML(FOOTER_HTML)

        # =================================================================
        # EVENT HANDLERS
        # =================================================================

        def on_load():
            """Check API status on load"""
            connected, status = check_api_health()
            if connected:
                return f"<span class='api-status connected'>API: {status}</span>"
            return f"<span class='api-status disconnected'>API: {status}</span>"

        # Check API on load
        app.load(fn=on_load, outputs=[api_status_html])

        def on_transcribe(audio_path):
            """Transcribe audio to text"""
            if audio_path:
                return transcribe_audio(audio_path)
            return ""

        transcribe_btn.click(
            fn=on_transcribe,
            inputs=[voice_input],
            outputs=[query_input]
        )

        # Auto-transcribe on voice change
        voice_input.change(
            fn=on_transcribe,
            inputs=[voice_input],
            outputs=[query_input]
        )

        def on_submit(query: str, sess_id: str, count: int):
            """Handle query submission"""
            # Validate input
            if not query or not query.strip():
                return (
                    "",  # sql
                    pd.DataFrame(),  # table
                    None,  # chart
                    "",  # insights
                    gr.update(visible=True, value="**Please enter a question.**"),  # error
                    gr.update(visible=False),  # results
                    gr.update(visible=False),  # login prompt
                    count,  # query count
                    f"<div class='query-counter'>Free queries: {FREE_QUERY_LIMIT - count}/{FREE_QUERY_LIMIT}</div>"
                )

            # Check freemium limit
            if count >= FREE_QUERY_LIMIT:
                return (
                    "",
                    pd.DataFrame(),
                    None,
                    "",
                    gr.update(visible=False),
                    gr.update(visible=False),
                    gr.update(visible=True),  # Show login prompt
                    count,
                    "<div class='query-counter'>No free queries remaining</div>"
                )

            # Execute query
            result = execute_query(query.strip(), sess_id)

            # Handle errors
            if result.get("errors"):
                error_msg = "\n\n".join([f"- {e}" for e in result["errors"]])
                return (
                    "",
                    pd.DataFrame(),
                    None,
                    "",
                    gr.update(visible=True, value=f"**Error:**\n{error_msg}"),
                    gr.update(visible=False),
                    gr.update(visible=False),
                    count,
                    f"<div class='query-counter'>Free queries: {FREE_QUERY_LIMIT - count}/{FREE_QUERY_LIMIT}</div>"
                )

            # Increment counter
            new_count = count + 1

            # Prepare outputs
            sql = result.get("sql_query", "")
            df = format_dataframe(result.get("query_results"))
            chart = format_chart(result.get("chart_config"))
            insights = format_insights(
                result.get("insights", []),
                result.get("recommendations", [])
            )

            # Check if this was the last free query
            remaining = FREE_QUERY_LIMIT - new_count
            show_login = remaining <= 0

            if remaining > 0:
                counter_html = f"<div class='query-counter'>Free queries: {remaining}/{FREE_QUERY_LIMIT}</div>"
            else:
                counter_html = "<div class='query-counter'>No free queries remaining</div>"

            return (
                sql,
                df,
                chart,
                insights,
                gr.update(visible=False),  # Hide error
                gr.update(visible=True),   # Show results
                gr.update(visible=show_login),  # Maybe show login
                new_count,
                counter_html
            )

        submit_btn.click(
            fn=on_submit,
            inputs=[query_input, session_id, query_count],
            outputs=[
                sql_output,
                results_table,
                chart_output,
                insights_output,
                error_output,
                results_section,
                login_prompt,
                query_count,
                query_counter_html
            ]
        )

        def on_clear():
            """Clear all outputs"""
            return (
                "",  # query input
                None,  # voice input
                "",  # sql
                pd.DataFrame(),  # table
                None,  # chart
                "",  # insights
                gr.update(visible=False),  # error
                gr.update(visible=False)   # results
            )

        clear_btn.click(
            fn=on_clear,
            inputs=[],
            outputs=[
                query_input,
                voice_input,
                sql_output,
                results_table,
                chart_output,
                insights_output,
                error_output,
                results_section
            ]
        )

        def on_download(df):
            """Generate CSV file for download"""
            filepath = create_csv_file(df)
            if filepath:
                return gr.update(value=filepath, visible=True)
            return gr.update(visible=False)

        download_btn.click(
            fn=on_download,
            inputs=[results_table],
            outputs=[download_file]
        )

    return app


# =============================================================================
# STANDALONE EXECUTION
# =============================================================================

if __name__ == "__main__":
    app = create_main_app()
    app.launch(
        server_name="0.0.0.0",
        server_port=7861,
        css=DARK_CSS
    )
