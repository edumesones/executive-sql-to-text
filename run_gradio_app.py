"""
Start the Gradio Main App (query interface)
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    port = int(os.getenv("GRADIO_APP_PORT", "7861"))

    print(f"Starting Executive Analytics Main App on port {port}")
    print(f"Open: http://localhost:{port}")

    import gradio as gr
    from frontend.gradio_main import create_main_app, DARK_CSS

    app = create_main_app()
    app.launch(
        server_name="0.0.0.0",
        server_port=port,
        share=False,
        css=DARK_CSS
    )
