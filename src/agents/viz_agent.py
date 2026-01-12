"""
Viz Agent - Selects optimal visualizations
"""
from typing import Dict, Any, List

from .base_agent import BaseAgent
from ..tools.chart_generator import ChartGenerator


class VizAgent(BaseAgent):
    """
    Selects appropriate chart type and generates Plotly configurations
    based on data structure and user query context.
    """
    
    def __init__(self):
        super().__init__(agent_name='viz_agent')
        self.chart_generator = ChartGenerator()
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze data and create visualization
        
        Args:
            state: Current workflow state with query_results
            
        Returns:
            State updates with chart_type and chart_config
        """
        results = state.get('query_results', [])
        user_query = state.get('user_query', '')
        
        if not results:
            return {
                "chart_type": None,
                "chart_config": None,
                "warnings": ["No data available for visualization"],
                "current_step": "viz_skipped"
            }
        
        try:
            # Select appropriate chart type
            chart_type = self._select_chart_type(results, user_query)
            
            # Generate chart configuration
            chart_config = self._generate_chart(results, chart_type, user_query)
            
            return {
                "chart_type": chart_type,
                "chart_config": chart_config,
                "current_step": "viz_complete"
            }
            
        except Exception as e:
            return {
                "errors": [f"Visualization generation failed: {str(e)}"],
                "current_step": "viz_error"
            }
    
    def _select_chart_type(
        self,
        results: List[Dict[str, Any]],
        query: str
    ) -> str:
        """Select appropriate chart type"""
        return self.chart_generator.select_chart_type(results, query)
    
    def _generate_chart(
        self,
        results: List[Dict[str, Any]],
        chart_type: str,
        query: str
    ) -> Dict[str, Any]:
        """Generate chart configuration"""
        if not results:
            return {}
        
        # Get columns and their types
        first_row = results[0]
        columns = list(first_row.keys())
        
        # Identify categorical and numeric columns
        categorical_cols = [
            col for col in columns
            if isinstance(first_row[col], (str, type(None)))
        ]
        numeric_cols = [
            col for col in columns
            if isinstance(first_row[col], (int, float))
        ]
        
        # Generate title from query
        title = self._generate_title(query, chart_type)
        
        # Generate appropriate chart
        if chart_type == 'bar':
            return self._generate_bar_chart(results, categorical_cols, numeric_cols, title)
        elif chart_type == 'line':
            return self._generate_line_chart(results, columns, numeric_cols, title)
        elif chart_type == 'pie':
            return self._generate_pie_chart(results, categorical_cols, numeric_cols, title)
        elif chart_type == 'scatter':
            return self._generate_scatter_chart(results, numeric_cols, title)
        else:
            return self._generate_bar_chart(results, categorical_cols, numeric_cols, title)
    
    def _generate_bar_chart(
        self,
        results: List[Dict[str, Any]],
        categorical_cols: List[str],
        numeric_cols: List[str],
        title: str
    ) -> Dict[str, Any]:
        """Generate bar chart configuration"""
        if not categorical_cols or not numeric_cols:
            return {}
        
        x_col = categorical_cols[0]
        y_col = numeric_cols[0]
        
        # Use horizontal if many categories or long labels
        orientation = 'h' if len(results) > 10 else 'v'
        
        return self.chart_generator.generate_bar_chart(
            results, x_col, y_col, title, orientation
        )
    
    def _generate_line_chart(
        self,
        results: List[Dict[str, Any]],
        columns: List[str],
        numeric_cols: List[str],
        title: str
    ) -> Dict[str, Any]:
        """Generate line chart configuration"""
        if not numeric_cols:
            return {}
        
        # Look for date/time column
        date_col = next(
            (col for col in columns if any(
                kw in col.lower() for kw in ['date', 'time', 'month', 'year']
            )),
            columns[0]
        )
        y_col = numeric_cols[0]
        
        return self.chart_generator.generate_line_chart(
            results, date_col, y_col, title
        )
    
    def _generate_pie_chart(
        self,
        results: List[Dict[str, Any]],
        categorical_cols: List[str],
        numeric_cols: List[str],
        title: str
    ) -> Dict[str, Any]:
        """Generate pie chart configuration"""
        if not categorical_cols or not numeric_cols:
            return {}
        
        labels_col = categorical_cols[0]
        values_col = numeric_cols[0]
        
        return self.chart_generator.generate_pie_chart(
            results, labels_col, values_col, title
        )
    
    def _generate_scatter_chart(
        self,
        results: List[Dict[str, Any]],
        numeric_cols: List[str],
        title: str
    ) -> Dict[str, Any]:
        """Generate scatter chart configuration"""
        if len(numeric_cols) < 2:
            return {}
        
        x_col = numeric_cols[0]
        y_col = numeric_cols[1]
        color_col = numeric_cols[2] if len(numeric_cols) > 2 else None
        
        return self.chart_generator.generate_scatter_chart(
            results, x_col, y_col, title, color_col
        )
    
    def _generate_title(self, query: str, chart_type: str) -> str:
        """Generate chart title from query"""
        # Capitalize first letter
        title = query[0].upper() + query[1:] if query else "Data Analysis"
        
        # Trim if too long
        if len(title) > 60:
            title = title[:57] + "..."
        
        return title
