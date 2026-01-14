"""
Executive Analytics Assistant - Streamlit Frontend

Interactive UI for conversational SQL analytics
"""
import streamlit as st
import requests
import uuid
import plotly.graph_objects as go
from datetime import datetime
from typing import Optional, Dict, Any
import pandas as pd
import os
import tempfile
import io

# Audio recording and speech recognition imports
try:
    from audio_recorder_streamlit import audio_recorder
    AUDIO_RECORDER_AVAILABLE = True
except ImportError:
    AUDIO_RECORDER_AVAILABLE = False

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="Executive Analytics Assistant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_URL = "http://localhost:8000"


def initialize_session_state():
    """Initialize session state variables"""
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if 'query_history' not in st.session_state:
        st.session_state.query_history = []
    if 'current_result' not in st.session_state:
        st.session_state.current_result = None
    if 'audio_transcribed' not in st.session_state:
        st.session_state.audio_transcribed = None


def call_api(query: str) -> Optional[Dict[str, Any]]:
    """
    Call the analytics API
    
    Args:
        query: Natural language query
        
    Returns:
        API response or None if error
    """
    try:
        response = requests.post(
            f"{API_URL}/api/query",
            json={
                "query": query,
                "session_id": st.session_state.session_id
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return None


def check_api_health() -> bool:
    """Check if API is available"""
    try:
        response = requests.get(f"{API_URL}/api/health", timeout=5)
        if response.status_code == 200:
            return True
        else:
            st.error(f"API returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError as e:
        st.error(f"❌ Cannot connect to API at {API_URL}. Is the server running?")
        return False
    except requests.exceptions.Timeout:
        st.error(f"⏱️ API request timed out. Server may be slow or unresponsive.")
        return False
    except Exception as e:
        st.error(f"❌ Error checking API health: {str(e)}")
        return False


def transcribe_audio(audio_bytes: bytes, language: str = "en-US") -> Optional[str]:
    """
    Transcribe audio bytes to text using speech recognition
    
    Args:
        audio_bytes: Audio data in bytes (WAV format)
        language: Language code for recognition (default: en-US)
        
    Returns:
        Transcribed text or None if error
    """
    if not SPEECH_RECOGNITION_AVAILABLE:
        st.error("❌ Speech recognition no está disponible")
        return None
    
    # Log inicial
    st.write("🔍 **Logs de transcripción:**")
    st.write(f"📊 Tamaño del audio: {len(audio_bytes)} bytes")
    
    try:
        # Create a temporary file to save audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_file_path = tmp_file.name
        
        st.write(f"💾 Audio guardado temporalmente en: {tmp_file_path}")
        
        # Initialize recognizer
        recognizer = sr.Recognizer()
        st.write("✅ Reconocedor inicializado")
        
        # Load audio file
        with sr.AudioFile(tmp_file_path) as source:
            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio_data = recognizer.record(source)
        
        st.write(f"🎵 Audio cargado. Duración estimada: {len(audio_data.frame_data) / audio_data.sample_rate:.2f} segundos")
        
        # Try different recognition engines
        transcribed_text = None
        
        # Try Google Speech Recognition first (requires API key)
        google_api_key = os.getenv("GOOGLE_SPEECH_API_KEY")
        if google_api_key:
            st.write("🌐 Intentando transcripción con Google Speech Recognition...")
            try:
                transcribed_text = recognizer.recognize_google(
                    audio_data, 
                    language=language,
                    key=google_api_key
                )
                st.write(f"✅ **Google Speech Recognition:** Texto transcrito = '{transcribed_text}'")
                st.success("✅ Audio transcribed using Google Speech Recognition")
            except sr.UnknownValueError:
                st.write("⚠️ Google Speech Recognition no pudo entender el audio (audio muy bajo o incomprensible)")
                st.warning("⚠️ Google Speech Recognition could not understand the audio")
            except sr.RequestError as e:
                st.write(f"❌ Error de Google Speech Recognition: {str(e)}")
                st.warning(f"⚠️ Google Speech Recognition error: {str(e)}")
        else:
            st.write("ℹ️ Google Speech Recognition no configurado (falta GOOGLE_SPEECH_API_KEY)")
        
        # Fallback to Whisper (offline, no API key needed)
        if not transcribed_text:
            st.write("🤖 Intentando transcripción con Whisper (offline)...")
            try:
                # Check if whisper is available
                try:
                    import whisper
                    st.write("✅ Módulo Whisper disponible")
                except ImportError:
                    st.write("❌ Whisper no está instalado")
                    st.warning("⚠️ Whisper no está instalado. Instalando dependencias necesarias...")
                    st.info("💡 Para usar Whisper offline, instala: `uv pip install openai-whisper`")
                    st.info("💡 O usa Google Speech Recognition configurando GOOGLE_SPEECH_API_KEY en .env")
                    return None
                
                st.write("🔄 Procesando audio con Whisper (esto puede tardar unos segundos)...")
                transcribed_text = recognizer.recognize_whisper(
                    audio_data,
                    language=language.split("-")[0] if "-" in language else language
                )
                st.write(f"✅ **Whisper:** Texto transcrito = '{transcribed_text}'")
                st.success("✅ Audio transcribed using Whisper (offline)")
            except ImportError as e:
                st.write(f"❌ Error de importación: {str(e)}")
                st.error(f"❌ Módulo faltante: {str(e)}")
                st.info("💡 Instala las dependencias: `uv pip install soundfile pydub openai-whisper`")
                return None
            except Exception as e:
                error_msg = str(e)
                st.write(f"❌ Error durante transcripción Whisper: {error_msg}")
                if "soundfile" in error_msg.lower():
                    st.error("❌ Error: Falta el módulo 'soundfile'")
                    st.info("💡 Instala con: `cd D:\\gestoria_agentes && uv pip install soundfile`")
                else:
                    st.error(f"❌ Speech recognition error: {error_msg}")
                return None
        
        # Verificar resultado
        if transcribed_text:
            st.write(f"✅ **Transcripción exitosa:** '{transcribed_text}'")
            st.write(f"📏 Longitud del texto: {len(transcribed_text)} caracteres")
        else:
            st.write("❌ **No se pudo transcribir el audio**")
            st.write("💡 Posibles causas:")
            st.write("   - Audio demasiado corto o silencioso")
            st.write("   - Calidad de audio baja")
            st.write("   - Ruido de fondo excesivo")
            st.write("   - Idioma no reconocido")
        
        # Clean up temporary file
        try:
            os.unlink(tmp_file_path)
            st.write(f"🗑️ Archivo temporal eliminado: {tmp_file_path}")
        except Exception as e:
            st.write(f"⚠️ No se pudo eliminar archivo temporal: {str(e)}")
        
        return transcribed_text
        
    except Exception as e:
        st.write(f"❌ **Error general procesando audio:** {str(e)}")
        st.error(f"❌ Error processing audio: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        return None


def display_metrics_summary(metrics: Dict[str, Any]):
    """Display performance metrics in columns"""
    if not metrics:
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Time", f"{metrics.get('total_duration_ms', 0)}ms")
    with col2:
        st.metric("SQL Gen", f"{metrics.get('sql_agent_duration_ms', 0)}ms")
    with col3:
        st.metric("Analysis", f"{metrics.get('analyst_agent_duration_ms', 0)}ms")
    with col4:
        st.metric("Viz + Insights", 
                 f"{metrics.get('viz_agent_duration_ms', 0) + metrics.get('insight_agent_duration_ms', 0)}ms")


def display_results(result: Dict[str, Any]):
    """Display query results"""
    
    # SQL Query (expandable)
    with st.expander("🔍 SQL Query Generated", expanded=False):
        if result.get("sql_query"):
            st.code(result["sql_query"], language="sql")
        else:
            st.warning("No SQL query generated")
    
    # Errors
    if result.get("errors"):
        st.error("❌ Errors occurred:")
        for error in result["errors"]:
            st.error(error)
        return
    
    # Warnings
    if result.get("warnings"):
        for warning in result["warnings"]:
            st.warning(warning)
    
    # Performance Metrics
    if result.get("metrics"):
        st.subheader("⏱️ Performance Metrics")
        display_metrics_summary(result["metrics"])
        st.divider()
    
    # Chart Visualization
    if result.get("chart_config"):
        st.subheader("📊 Visualization")
        try:
            fig = go.Figure(result["chart_config"])
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error rendering chart: {str(e)}")
            st.json(result["chart_config"])
    
    # Data Table
    if result.get("query_results"):
        st.subheader("📋 Data")
        df = pd.DataFrame(result["query_results"])
        st.dataframe(df, use_container_width=True, height=300)
        
        # Download button
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"query_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    # Derived Metrics
    if result.get("derived_metrics"):
        st.subheader("📈 Key Metrics")
        metrics_df = pd.DataFrame([result["derived_metrics"]])
        st.dataframe(metrics_df, use_container_width=True)
    
    # Insights
    if result.get("insights"):
        st.subheader("💡 Key Insights")
        for insight in result["insights"]:
            st.info(insight)
    
    # Recommendations
    if result.get("recommendations"):
        st.subheader("🎯 Recommendations")
        for rec in result["recommendations"]:
            st.success(rec)


def main():
    """Main application"""
    initialize_session_state()
    
    # Header
    st.title("📊 Executive Analytics Assistant")
    st.markdown("*Ask questions about loan data in natural language*")
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 Settings")
        
        # API Status
        api_healthy = check_api_health()
        status_color = "🟢" if api_healthy else "🔴"
        st.markdown(f"{status_color} API Status: {'Connected' if api_healthy else 'Disconnected'}")
        
        if not api_healthy:
            st.error("⚠️ API is not available. Make sure to start the backend server:")
            st.code("python run_api.py", language="bash")
        
        st.divider()
        
        # Session Info
        st.subheader("📋 Session Info")
        st.text(f"ID: {st.session_state.session_id[:8]}...")
        st.text(f"Queries: {len(st.session_state.query_history)}")
        
        if st.button("🔄 New Session"):
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.query_history = []
            st.session_state.current_result = None
            st.rerun()
        
        st.divider()
        
        # Query History
        if st.session_state.query_history:
            st.subheader("📜 Recent Queries")
            for i, hist_query in enumerate(reversed(st.session_state.query_history[-5:])):
                with st.expander(f"Query {len(st.session_state.query_history) - i}"):
                    st.text(hist_query[:100] + "..." if len(hist_query) > 100 else hist_query)
        
        st.divider()
        
        # Example Queries
        st.subheader("💭 Example Queries")
        examples = [
            "Show me the top 10 loans by amount",
            "What is the default rate by loan grade?",
            "Average interest rate by state",
            "Monthly loan origination trend",
            "Distribution of loan purposes"
        ]
        for example in examples:
            if st.button(example, key=f"example_{examples.index(example)}"):
                st.session_state.example_query = example
    
    # Main content
    if not api_healthy:
        st.warning("⚠️ Cannot proceed without API connection. Please start the backend server.")
        st.info("Run: `python run_api.py` in your terminal")
        return
    
    # Query input section
    st.subheader("💬 Ask Your Question")
    
    # Tabs for text and voice input
    input_tab1, input_tab2 = st.tabs(["✍️ Text Input", "🎤 Voice Input"])
    
    query = ""
    
    with input_tab1:
        # Text input
        default_query = st.session_state.get('example_query', '')
        
        # Priorizar texto transcrito de audio (NO eliminar hasta que se use para analizar)
        if st.session_state.get('audio_transcribed'):
            default_query = st.session_state.audio_transcribed
            st.success(f"🎤 **Texto transcrito desde audio:** '{default_query}'")
            st.info("💡 Este texto está listo para analizar. Presiona el botón 'Analyze' abajo.")
        
        query = st.text_input(
            "Type your question:",
            value=default_query,
            placeholder="e.g., Show me the top 10 loans by amount",
            key="query_input"
        )
        
        # Mostrar el valor actual del campo
        if query:
            st.write(f"📝 **Texto actual en el campo:** '{query}'")
        elif st.session_state.get('audio_transcribed'):
            # Si el campo está vacío pero hay texto transcrito, mostrarlo
            st.warning(f"⚠️ El campo está vacío, pero hay texto transcrito: '{st.session_state.audio_transcribed}'")
            st.info("💡 El texto transcrito se usará automáticamente al presionar 'Analyze'.")
        
        # Clear example query after use
        if 'example_query' in st.session_state:
            del st.session_state.example_query
    
    with input_tab2:
        # Voice input
        if not AUDIO_RECORDER_AVAILABLE:
            st.warning("⚠️ Audio recording not available. Please install: `pip install audio-recorder-streamlit`")
        elif not SPEECH_RECOGNITION_AVAILABLE:
            st.warning("⚠️ Speech recognition not available. Please install: `pip install SpeechRecognition`")
        else:
            st.markdown("**Record your question:**")
            st.info("💡 Click the microphone button below to start recording. Click again to stop.")
            
            # Audio recorder
            audio_bytes = audio_recorder(
                text="Click to record",
                recording_color="#e74c3c",
                neutral_color="#6c757d",
                icon_name="microphone",
                icon_size="2x",
                pause_threshold=2.0
            )
            
            if audio_bytes:
                st.audio(audio_bytes, format="audio/wav")
                st.write(f"📊 Audio recibido: {len(audio_bytes)} bytes")
                
                # Transcribe button
                if st.button("🎯 Transcribe Audio", type="primary"):
                    with st.spinner("🎤 Transcribing audio..."):
                        transcribed = transcribe_audio(audio_bytes)
                        if transcribed and transcribed.strip():
                            # Guardar texto transcrito (NO modificar query_input directamente)
                            st.session_state.audio_transcribed = transcribed.strip()
                            st.success(f"📝 **Texto transcrito:** '{transcribed.strip()}'")
                            st.info("💡 El texto ha sido copiado al campo de entrada. Cambia a la pestaña 'Text Input' para verlo y analizarlo.")
                            st.rerun()
                        else:
                            st.error("❌ Could not transcribe audio. Please try again.")
                            if transcribed is None:
                                st.warning("⚠️ La transcripción devolvió None. Revisa los logs arriba para más detalles.")
                            elif transcribed.strip() == "":
                                st.warning("⚠️ La transcripción está vacía. El audio puede ser demasiado corto o silencioso.")
    
    # Analyze button
    col1, col2 = st.columns([1, 5])
    with col1:
        analyze_button = st.button("🔍 Analyze", type="primary", use_container_width=True)
    with col2:
        if st.button("🗑️ Clear Results"):
            st.session_state.current_result = None
            st.rerun()
    
    # Process query
    if analyze_button:
        # Usar texto transcrito si el campo está vacío
        query_to_analyze = query
        if not query_to_analyze and st.session_state.get('audio_transcribed'):
            query_to_analyze = st.session_state.audio_transcribed
            st.info(f"🎤 Usando texto transcrito: '{query_to_analyze}'")
            # Limpiar después de usar
            del st.session_state.audio_transcribed
        
        if not query_to_analyze:
            st.warning("⚠️ Please enter a question or transcribe audio first")
        else:
            with st.spinner(f"🤔 Analyzing: '{query_to_analyze}'..."):
                result = call_api(query_to_analyze)
                
                if result:
                    st.session_state.query_history.append(query_to_analyze)
                    st.session_state.current_result = result
                    # Limpiar audio_transcribed después de analizar exitosamente
                    if 'audio_transcribed' in st.session_state:
                        del st.session_state.audio_transcribed
                    st.rerun()
    
    # Display results
    if st.session_state.current_result:
        st.divider()
        st.header("📊 Results")
        display_results(st.session_state.current_result)
    
    # Footer
    st.divider()
    st.markdown(
        """
        <div style='text-align: center; color: gray; font-size: 0.8em;'>
        Executive Analytics Assistant v0.1.0 | Powered by LangGraph & OpenAI
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
