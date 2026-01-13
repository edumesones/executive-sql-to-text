"""
Analyst Agent - Executes queries and analyzes results
"""
from typing import Dict, Any, List
import asyncio
from datetime import datetime

from .base_agent import BaseAgent
from ..tools.sql_executor import get_sql_executor
from ..tools.metric_calculator import MetricCalculator


class AnalystAgent(BaseAgent):
    """
    Executes SQL queries and performs data analysis.
    Validates results, calculates metrics, and detects issues.
    """
    
    def __init__(self):
        super().__init__(agent_name='analyst_agent')
        self.sql_executor = get_sql_executor()
        self.metric_calculator = MetricCalculator()
    
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute SQL query and analyze results
        
        Args:
            state: Current workflow state with sql_query
            
        Returns:
            State updates with query_results, metrics, and quality checks
        """
        sql_query = state.get('sql_query')
        
        if not sql_query:
            return {
                "errors": ["No SQL query provided"],
                "current_step": "analyst_error"
            }
        
        try:
            # Execute query (async)
            results, metadata = await self.sql_executor.execute_query(sql_query)
            
            # Validate results
            quality_issues = self._validate_data_quality(results)
            
            # Calculate derived metrics
            derived_metrics = self._calculate_derived_metrics(results, state)
            
            # Prepare response
            return {
                "query_results": results,
                "result_count": metadata['row_count'],
                "derived_metrics": derived_metrics,
                "data_quality_issues": quality_issues,
                "execution_time_ms": metadata['execution_time_ms'],
                "warnings": self._generate_warnings(metadata, results),
                "current_step": "analysis_complete"
            }
            
        except Exception as e:
            return {
                "errors": [f"Query execution failed: {str(e)}"],
                "current_step": "analyst_error"
            }
    
    def _validate_data_quality(self, results: List[Dict[str, Any]]) -> List[str]:
        """Check for data quality issues"""
        issues = []
        
        if not results:
            issues.append("Query returned no results")
            return issues
        
        # Check for null values in each column
        first_row = results[0]
        for column in first_row.keys():
            null_count = sum(1 for row in results if row.get(column) is None)
            if null_count > 0:
                pct = (null_count / len(results)) * 100
                issues.append(f"{column}: {null_count} null values ({pct:.1f}%)")
        
        # Check for duplicate rows
        unique_rows = len(set(tuple(row.items()) for row in results))
        if unique_rows < len(results):
            issues.append(f"{len(results) - unique_rows} duplicate rows detected")
        
        return issues
    
    def _calculate_derived_metrics(
        self, 
        results: List[Dict[str, Any]],
        state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate relevant metrics based on query results"""
        if not results:
            return {}
        
        metrics = {}
        first_row = results[0]
        
        # Identify numeric columns
        numeric_columns = [
            col for col in first_row.keys()
            if isinstance(first_row[col], (int, float))
        ]
        
        # Calculate financial metrics for amount-like columns
        amount_columns = [
            col for col in numeric_columns
            if any(keyword in col.lower() for keyword in ['amount', 'amnt', 'balance', 'income', 'rate'])
        ]
        
        for col in amount_columns:
            col_metrics = self.metric_calculator.calculate_financial_metrics(results, col)
            if col_metrics:
                metrics[f"{col}_metrics"] = col_metrics
        
        # Calculate default rate if loan_status column exists
        if 'loan_status' in first_row:
            default_rate = self.metric_calculator.calculate_rate(
                results,
                'loan_status',
                ['Charged Off', 'Default']
            )
            metrics['default_rate'] = default_rate
        
        return metrics
    
    def _generate_warnings(
        self,
        metadata: Dict[str, Any],
        results: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate warnings based on query execution"""
        warnings = []
        
        if metadata.get('truncated'):
            warnings.append(
                f"Results truncated to {len(results)} rows. "
                "Consider adding filters for more specific results."
            )
        
        if metadata.get('execution_time_ms', 0) > 5000:
            warnings.append(
                f"Query took {metadata['execution_time_ms']/1000:.1f}s. "
                "Consider optimizing with indexes or filters."
            )
        
        return warnings
