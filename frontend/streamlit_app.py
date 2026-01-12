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
        return response.status_code == 200
    except:
        return False


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
    
    # Query input
    default_query = st.session_state.get('example_query', '')
    query = st.text_input(
        "Your question:",
        value=default_query,
        placeholder="e.g., Show me the top 10 loans by amount",
        key="query_input"
    )
    
    # Clear example query after use
    if 'example_query' in st.session_state:
        del st.session_state.example_query
    
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
        if not query:
            st.warning("Please enter a question")
        else:
            with st.spinner("🤔 Analyzing your question..."):
                result = call_api(query)
                
                if result:
                    st.session_state.query_history.append(query)
                    st.session_state.current_result = result
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
