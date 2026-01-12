"""
Insight Agent - Generates business insights
"""
from typing import Dict, Any, List

from .base_agent import BaseAgent


class InsightAgent(BaseAgent):
    """
    Generates executive-level insights and recommendations
    from analyzed data and metrics.
    """
    
    def __init__(self):
        super().__init__(agent_name='insight_agent')
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate business insights from results
        
        Args:
            state: Current workflow state with query_results and derived_metrics
            
        Returns:
            State updates with insights and recommendations
        """
        results = state.get('query_results', [])
        metrics = state.get('derived_metrics', {})
        user_query = state.get('user_query', '')
        
        if not results:
            return {
                "insights": [],
                "recommendations": [],
                "current_step": "insight_skipped"
            }
        
        try:
            # Build context for LLM
            context = self._build_insight_context(results, metrics, user_query)
            
            # Get insights from LLM
            insights_response = self.invoke_llm(context)
            
            # Parse insights and recommendations
            insights, recommendations = self._parse_insights(insights_response)
            
            return {
                "insights": insights,
                "recommendations": recommendations,
                "current_step": "insight_complete"
            }
            
        except Exception as e:
            return {
                "errors": [f"Insight generation failed: {str(e)}"],
                "current_step": "insight_error"
            }
    
    def _build_insight_context(
        self,
        results: List[Dict[str, Any]],
        metrics: Dict[str, Any],
        query: str
    ) -> str:
        """Build context prompt for insight generation"""
        
        # Summarize results
        result_summary = f"Query returned {len(results)} rows."
        
        # Format metrics
        metrics_text = ""
        if metrics:
            metrics_text = "\n\nKey Metrics:\n"
            for key, value in metrics.items():
                if isinstance(value, dict):
                    metrics_text += f"\n{key}:\n"
                    for k, v in value.items():
                        metrics_text += f"  - {k}: {v:,.2f}\n"
                else:
                    metrics_text += f"- {key}: {value}\n"
        
        # Sample data
        sample_size = min(5, len(results))
        sample_data = results[:sample_size]
        
        return f"""
        You are a senior business analyst presenting insights to executives.
        
        User Question: {query}
        
        Data Summary:
        {result_summary}
        {metrics_text}
        
        Sample Data (first {sample_size} rows):
        {self._format_sample_data(sample_data)}
        
        Generate 3-5 concise business insights in bullet points.
        Then provide 2-3 actionable recommendations.
        
        Format your response as:
        
        INSIGHTS:
        - [insight 1]
        - [insight 2]
        - [insight 3]
        
        RECOMMENDATIONS:
        - [recommendation 1]
        - [recommendation 2]
        
        Use clear, executive-friendly language with quantified findings.
        """
    
    def _format_sample_data(self, sample: List[Dict[str, Any]]) -> str:
        """Format sample data for display"""
        if not sample:
            return "No data available"
        
        lines = []
        for i, row in enumerate(sample, 1):
            row_str = ", ".join(f"{k}: {v}" for k, v in row.items())
            lines.append(f"{i}. {row_str}")
        
        return "\n".join(lines)
    
    def _parse_insights(self, response: str) -> tuple[List[str], List[str]]:
        """Parse insights and recommendations from LLM response"""
        insights = []
        recommendations = []
        
        lines = response.strip().split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            if 'INSIGHTS:' in line.upper():
                current_section = 'insights'
                continue
            elif 'RECOMMENDATIONS:' in line.upper():
                current_section = 'recommendations'
                continue
            
            if line and line.startswith('-'):
                content = line[1:].strip()
                if current_section == 'insights':
                    insights.append(content)
                elif current_section == 'recommendations':
                    recommendations.append(content)
        
        return insights, recommendations
