# FEAT-004: Gradio Migration - Technical Design

## Architecture

### Component Mapping

| Streamlit | Gradio Equivalent |
|-----------|-------------------|
| `st.text_input` | `gr.Textbox` |
| `st.button` | `gr.Button` |
| `st.dataframe` | `gr.Dataframe` |
| `st.plotly_chart` | `gr.Plot` |
| `st.markdown` | `gr.Markdown` |
| `st.audio` | `gr.Audio` |
| `st.sidebar` | `gr.Column` / `gr.Tab` |
| `st.spinner` | `gr.Progress` |

### Layout Structure

```python
import gradio as gr

with gr.Blocks(theme=gr.themes.Soft()) as app:
    # Header
    gr.Markdown("# Executive Analytics Assistant")

    with gr.Tabs():
        with gr.Tab("Query"):
            with gr.Row():
                with gr.Column(scale=3):
                    query_input = gr.Textbox(
                        label="Ask your data",
                        placeholder="What's our default rate?"
                    )
                    audio_input = gr.Audio(
                        sources=["microphone"],
                        type="filepath"
                    )
                    submit_btn = gr.Button("Analyze", variant="primary")

                with gr.Column(scale=2):
                    sql_output = gr.Code(language="sql")

            with gr.Row():
                results_table = gr.Dataframe()
                chart_output = gr.Plot()

            insights_output = gr.Markdown()

        with gr.Tab("History"):
            history_table = gr.Dataframe()

        with gr.Tab("Settings"):
            connection_dropdown = gr.Dropdown()
```

### Voice Integration

```python
import speech_recognition as sr

def transcribe_audio(audio_path):
    """Convert audio to text."""
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return "Could not understand audio"

audio_input.change(
    fn=transcribe_audio,
    inputs=[audio_input],
    outputs=[query_input]
)
```

### Theming

```python
custom_theme = gr.themes.Soft(
    primary_hue="blue",
    secondary_hue="slate",
).set(
    body_background_fill="*neutral_50",
    block_background_fill="white",
    block_border_width="1px",
)
```

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `frontend/gradio_app.py` | Create | Main Gradio application |
| `frontend/components/` | Create | Reusable UI components |
| `frontend/auth.py` | Create | Auth state management |
| `run_frontend.py` | Modify | Switch to Gradio |

## Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| `gradio` | >=4.0.0 | UI framework |
| `httpx` | >=0.25.0 | Async HTTP client |
| `SpeechRecognition` | >=3.10.0 | Voice transcription |

## Migration Strategy

1. **Phase 1**: Create Gradio app parallel to Streamlit
2. **Phase 2**: Migrate core query functionality
3. **Phase 3**: Add voice input support
4. **Phase 4**: Implement auth integration
5. **Phase 5**: Switch default, keep Streamlit as fallback
6. **Phase 6**: Deprecate Streamlit

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Learning curve | Medium | Low | Good docs, similar to Streamlit |
| Voice compatibility | Medium | Medium | Test multiple browsers |
| Auth complexity | Low | Medium | Simple session state first |

---

*Created: 2026-01-15*
