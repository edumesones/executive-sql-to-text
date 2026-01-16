"""
Start the Gradio landing page
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    port = int(os.getenv("GRADIO_PORT", "7860"))

    print(f"Starting Executive Analytics Landing Page on port {port}")
    print(f"Open: http://localhost:{port}")

    import gradio as gr
    from frontend.gradio_app import create_app, CUSTOM_CSS

    app = create_app()
    app.launch(
        server_name="0.0.0.0",
        server_port=port,
        share=False,
        css=CUSTOM_CSS,
        theme=gr.themes.Soft()
    )
