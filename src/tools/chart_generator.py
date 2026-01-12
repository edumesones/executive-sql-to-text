"""
Chart Generator - Generate Plotly charts from data
"""
from typing import List, Dict, Any, Optional
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class ChartGenerator:
    """Generate interactive Plotly charts"""
    
    DEFAULT_TEMPLATE = "plotly_white"
    DEFAULT_HEIGHT = 500
    DEFAULT_WIDTH = 800
    
    @staticmethod
    def generate_bar_chart(
        data: List[Dict[str, Any]],
        x_column: str,
        y_column: str,
        title: str,
        orientation: str = "v"
    ) -> Dict[str, Any]:
        """
        Generate bar chart
        
        Args:
            data: List of data rows
            x_column: Column for x-axis
            y_column: Column for y-axis (numeric)
            title: Chart title
            orientation: 'v' for vertical, 'h' for horizontal
        
        Returns:
            Plotly figure as dict
        """
        x_values = [row[x_column] for row in data]
        y_values = [row[y_column] for row in data]
        
        fig = go.Figure(data=[
            go.Bar(
                x=x_values if orientation == "v" else y_values,
                y=y_values if orientation == "v" else x_values,
                orientation=orientation,
                marker=dict(
                    color='rgba(55, 128, 191, 0.7)',
                    line=dict(color='rgba(55, 128, 191, 1.0)', width=1.5)
                ),
                hovertemplate=(
                    f"{x_column}: %{{x}}<br>"
                    f"{y_column}: %{{y:,.2f}}<br>"
                    "<extra></extra>"
                ) if orientation == "v" else (
                    f"{x_column}: %{{y}}<br>"
                    f"{y_column}: %{{x:,.2f}}<br>"
                    "<extra></extra>"
                )
            )
        ])
        
        fig.update_layout(
            title=title,
            xaxis_title=x_column if orientation == "v" else y_column,
            yaxis_title=y_column if orientation == "v" else x_column,
            template=ChartGenerator.DEFAULT_TEMPLATE,
            height=ChartGenerator.DEFAULT_HEIGHT,
            width=ChartGenerator.DEFAULT_WIDTH,
            showlegend=False
        )
        
        return fig.to_dict()
    
    @staticmethod
    def generate_line_chart(
        data: List[Dict[str, Any]],
        x_column: str,
        y_column: str,
        title: str,
        group_column: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate line chart (supports multiple series if group_column provided)
        
        Args:
            data: List of data rows
            x_column: Column for x-axis (usually dates)
            y_column: Column for y-axis (numeric)
            title: Chart title
            group_column: Optional column to group by (creates multiple lines)
        
        Returns:
            Plotly figure as dict
        """
        fig = go.Figure()
        
        if group_column:
            # Multiple series
            groups = {}
            for row in data:
                group = row[group_column]
                if group not in groups:
                    groups[group] = {'x': [], 'y': []}
                groups[group]['x'].append(row[x_column])
                groups[group]['y'].append(row[y_column])
            
            for group_name, values in groups.items():
                fig.add_trace(go.Scatter(
                    x=values['x'],
                    y=values['y'],
                    mode='lines+markers',
                    name=str(group_name),
                    hovertemplate=(
                        f"{x_column}: %{{x}}<br>"
                        f"{y_column}: %{{y:,.2f}}<br>"
                        "<extra></extra>"
                    )
                ))
        else:
            # Single series
            x_values = [row[x_column] for row in data]
            y_values = [row[y_column] for row in data]
            
            fig.add_trace(go.Scatter(
                x=x_values,
                y=y_values,
                mode='lines+markers',
                line=dict(color='rgba(55, 128, 191, 0.7)', width=2),
                marker=dict(size=6),
                hovertemplate=(
                    f"{x_column}: %{{x}}<br>"
                    f"{y_column}: %{{y:,.2f}}<br>"
                    "<extra></extra>"
                )
            ))
        
        fig.update_layout(
            title=title,
            xaxis_title=x_column,
            yaxis_title=y_column,
            template=ChartGenerator.DEFAULT_TEMPLATE,
            height=ChartGenerator.DEFAULT_HEIGHT,
            width=ChartGenerator.DEFAULT_WIDTH
        )
        
        return fig.to_dict()
    
    @staticmethod
    def generate_pie_chart(
        data: List[Dict[str, Any]],
        labels_column: str,
        values_column: str,
        title: str
    ) -> Dict[str, Any]:
        """
        Generate pie chart
        
        Args:
            data: List of data rows
            labels_column: Column for labels
            values_column: Column for values (numeric)
            title: Chart title
        
        Returns:
            Plotly figure as dict
        """
        labels = [row[labels_column] for row in data]
        values = [row[values_column] for row in data]
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.3,  # Donut style
            hovertemplate=(
                "<b>%{label}</b><br>"
                "Value: %{value:,.2f}<br>"
                "Percent: %{percent}<br>"
                "<extra></extra>"
            )
        )])
        
        fig.update_layout(
            title=title,
            template=ChartGenerator.DEFAULT_TEMPLATE,
            height=ChartGenerator.DEFAULT_HEIGHT,
            width=ChartGenerator.DEFAULT_WIDTH
        )
        
        return fig.to_dict()
    
    @staticmethod
    def generate_scatter_chart(
        data: List[Dict[str, Any]],
        x_column: str,
        y_column: str,
        title: str,
        color_column: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate scatter plot
        
        Args:
            data: List of data rows
            x_column: Column for x-axis
            y_column: Column for y-axis
            title: Chart title
            color_column: Optional column for color encoding
        
        Returns:
            Plotly figure as dict
        """
        x_values = [row[x_column] for row in data]
        y_values = [row[y_column] for row in data]
        
        scatter_params = {
            'x': x_values,
            'y': y_values,
            'mode': 'markers',
            'marker': dict(size=8),
            'hovertemplate': (
                f"{x_column}: %{{x:,.2f}}<br>"
                f"{y_column}: %{{y:,.2f}}<br>"
                "<extra></extra>"
            )
        }
        
        if color_column:
            scatter_params['marker']['color'] = [row[color_column] for row in data]
            scatter_params['marker']['colorscale'] = 'Viridis'
            scatter_params['marker']['showscale'] = True
        
        fig = go.Figure(data=[go.Scatter(**scatter_params)])
        
        fig.update_layout(
            title=title,
            xaxis_title=x_column,
            yaxis_title=y_column,
            template=ChartGenerator.DEFAULT_TEMPLATE,
            height=ChartGenerator.DEFAULT_HEIGHT,
            width=ChartGenerator.DEFAULT_WIDTH
        )
        
        return fig.to_dict()
    
    @staticmethod
    def select_chart_type(
        data: List[Dict[str, Any]],
        query: str
    ) -> str:
        """
        Automatically select appropriate chart type based on data structure
        
        Args:
            data: Query results
            query: Original user query (for context)
        
        Returns:
            Chart type: 'bar', 'line', 'pie', 'scatter'
        """
        if not data:
            return 'bar'  # default
        
        query_lower = query.lower()
        columns = list(data[0].keys())
        
        # Check for temporal data
        temporal_keywords = ['trend', 'over time', 'monthly', 'daily', 'quarterly', 'yearly']
        has_temporal = any(kw in query_lower for kw in temporal_keywords)
        
        # Check for comparison keywords
        comparison_keywords = ['top', 'bottom', 'highest', 'lowest', 'compare']
        has_comparison = any(kw in query_lower for kw in comparison_keywords)
        
        # Check for composition keywords
        composition_keywords = ['percentage', 'proportion', 'distribution', 'breakdown']
        has_composition = any(kw in query_lower for kw in composition_keywords)
        
        # Decision logic
        if has_temporal:
            return 'line'
        elif has_composition and len(data) <= 7:
            return 'pie'
        elif has_comparison or len(data) <= 20:
            return 'bar'
        elif len(columns) >= 3:  # Multiple numeric columns
            return 'scatter'
        else:
            return 'bar'  # default fallback
