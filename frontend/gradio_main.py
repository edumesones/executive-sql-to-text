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
/* Dark Theme */
:root {
    --background-fill-primary: #1a1a2e !important;
    --background-fill-secondary: #16213e !important;
    --block-background-fill: #1f2937 !important;
    --color-text-body: #e5e7eb !important;
    --color-text-subdued: #9ca3af !important;
    --border-color-primary: #374151 !important;
}

.gradio-container {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%) !important;
    min-height: 100vh;
}

body {
    background: #1a1a2e !important;
}

/* Header */
.header-section {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 30px;
    border-radius: 12px;
    margin-bottom: 20px;
    color: white;
}

.header-title {
    font-size: 2rem;
    font-weight: 700;
    margin: 0;
}

.header-subtitle {
    opacity: 0.9;
    margin-top: 8px;
}

/* Demo Info Panel */
.demo-info-panel {
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
    border: 1px solid rgba(102, 126, 234, 0.4);
    border-radius: 12px;
    padding: 20px;
    margin: 15px 0;
    color: #e5e7eb;
}

.demo-info-panel h3 {
    color: #a5b4fc;
    margin-top: 0;
}

.demo-info-panel ul {
    margin: 10px 0;
    padding-left: 20px;
}

.demo-info-panel li {
    margin: 5px 0;
}

/* Query Counter */
.query-counter {
    background: rgba(245, 158, 11, 0.2);
    border: 1px solid rgba(245, 158, 11, 0.5);
    border-radius: 8px;
    padding: 10px 15px;
    color: #fbbf24;
    font-weight: 600;
    text-align: center;
}

.query-counter.unlimited {
    background: rgba(34, 197, 94, 0.2);
    border-color: rgba(34, 197, 94, 0.5);
    color: #4ade80;
}

/* Login Prompt */
.login-prompt {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 16px;
    padding: 40px;
    text-align: center;
    color: white;
    margin: 20px 0;
}

.login-prompt h2 {
    margin-top: 0;
}

.login-prompt a {
    display: inline-block;
    background: white;
    color: #667eea;
    padding: 12px 30px;
    border-radius: 25px;
    text-decoration: none;
    font-weight: 600;
    margin-top: 15px;
    transition: transform 0.3s, box-shadow 0.3s;
}

.login-prompt a:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(0,0,0,0.3);
}

/* Results Section */
.results-container {
    background: #1f2937;
    border-radius: 12px;
    padding: 20px;
    margin-top: 20px;
    border: 1px solid #374151;
}

/* Insights */
.insights-box {
    background: rgba(59, 130, 246, 0.1);
    border-left: 4px solid #3b82f6;
    padding: 15px;
    margin: 10px 0;
    border-radius: 0 8px 8px 0;
}

/* API Status */
.api-status {
    display: inline-block;
    padding: 5px 12px;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 500;
}

.api-status.connected {
    background: rgba(34, 197, 94, 0.2);
    color: #4ade80;
}

.api-status.disconnected {
    background: rgba(239, 68, 68, 0.2);
    color: #f87171;
}

/* Primary Button Override */
.primary-btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    border: none !important;
}

.primary-btn:hover {
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4) !important;
}

/* Footer */
.footer {
    text-align: center;
    padding: 30px;
    color: #6b7280;
    border-top: 1px solid #374151;
    margin-top: 40px;
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
    <h3>Demo Database: Lending Club Loans</h3>
    <p>You're querying a sample dataset with loan information:</p>
    <ul>
        <li><strong>loan_amnt</strong> - Loan amount</li>
        <li><strong>int_rate</strong> - Interest rate</li>
        <li><strong>grade</strong> - Loan grade (A-G)</li>
        <li><strong>loan_status</strong> - Current status</li>
        <li><strong>purpose</strong> - Loan purpose</li>
        <li><strong>addr_state</strong> - Borrower's state</li>
    </ul>
    <p><strong>Try asking:</strong></p>
    <ul>
        <li>"Show me top 10 loans by amount"</li>
        <li>"What is the default rate by grade?"</li>
        <li>"Average interest rate by state"</li>
    </ul>
</div>
"""

LOGIN_PROMPT_HTML = f"""
<div class="login-prompt">
    <h2>Free Query Used!</h2>
    <p>You've used your free query. Sign up to continue with unlimited queries.</p>
    <a href="{LANDING_URL}#auth-section">Sign Up Free</a>
    <p style="margin-top: 15px; opacity: 0.8;">
        Already have an account? <a href="{LANDING_URL}#auth-section" style="color: white;">Log in</a>
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
                    label="Ask your question",
                    placeholder="e.g., Show me top 10 loans by amount",
                    lines=2
                )

                # Voice Input
                with gr.Accordion("Voice Input", open=False):
                    voice_input = gr.Audio(
                        sources=["microphone"],
                        type="filepath",
                        label="Record your question"
                    )
                    transcribe_btn = gr.Button("Transcribe", size="sm")

                # Action Buttons
                with gr.Row():
                    submit_btn = gr.Button(
                        "Analyze",
                        variant="primary",
                        elem_classes=["primary-btn"]
                    )
                    clear_btn = gr.Button("Clear", variant="secondary")

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
