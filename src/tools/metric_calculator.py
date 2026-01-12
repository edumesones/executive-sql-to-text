"""
Metric Calculator - Calculate business metrics and KPIs
"""
from typing import List, Dict, Any, Optional
import statistics
from decimal import Decimal


class MetricCalculator:
    """Calculate common business metrics from query results"""
    
    @staticmethod
    def calculate_financial_metrics(
        data: List[Dict[str, Any]],
        amount_column: str
    ) -> Dict[str, float]:
        """
        Calculate financial metrics (sum, avg, median, etc.)
        
        Args:
            data: List of result rows
            amount_column: Name of column with monetary values
        
        Returns:
            Dict with financial metrics
        """
        if not data:
            return {}
        
        amounts = [
            float(row[amount_column])
            for row in data
            if row.get(amount_column) is not None
        ]
        
        if not amounts:
            return {}
        
        return {
            "total": sum(amounts),
            "average": statistics.mean(amounts),
            "median": statistics.median(amounts),
            "min": min(amounts),
            "max": max(amounts),
            "std_dev": statistics.stdev(amounts) if len(amounts) > 1 else 0,
            "count": len(amounts)
        }
    
    @staticmethod
    def calculate_rate(
        data: List[Dict[str, Any]],
        condition_column: str,
        condition_values: List[str]
    ) -> float:
        """
        Calculate rate (e.g., default rate, approval rate)
        
        Args:
            data: List of result rows
            condition_column: Column to check condition
            condition_values: Values that meet condition
        
        Returns:
            Rate as percentage (0-100)
        """
        if not data:
            return 0.0
        
        total = len(data)
        matching = sum(
            1 for row in data
            if row.get(condition_column) in condition_values
        )
        
        return round((matching / total) * 100, 2)
    
    @staticmethod
    def calculate_distribution(
        data: List[Dict[str, Any]],
        column: str
    ) -> Dict[str, Any]:
        """
        Calculate distribution statistics
        
        Args:
            data: List of result rows
            column: Column to analyze
        
        Returns:
            Distribution metrics including quartiles
        """
        if not data:
            return {}
        
        values = [
            float(row[column])
            for row in data
            if row.get(column) is not None
        ]
        
        if not values:
            return {}
        
        sorted_values = sorted(values)
        
        return {
            "min": min(values),
            "q1": statistics.quantiles(values, n=4)[0],
            "median": statistics.median(values),
            "q3": statistics.quantiles(values, n=4)[2],
            "max": max(values),
            "iqr": statistics.quantiles(values, n=4)[2] - statistics.quantiles(values, n=4)[0],
            "outliers_count": MetricCalculator._count_outliers(values)
        }
    
    @staticmethod
    def _count_outliers(values: List[float]) -> int:
        """Count outliers using IQR method"""
        if len(values) < 4:
            return 0
        
        q1 = statistics.quantiles(values, n=4)[0]
        q3 = statistics.quantiles(values, n=4)[2]
        iqr = q3 - q1
        
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        return sum(1 for v in values if v < lower_bound or v > upper_bound)
    
    @staticmethod
    def calculate_growth(
        current_value: float,
        previous_value: float
    ) -> Dict[str, float]:
        """
        Calculate growth metrics
        
        Args:
            current_value: Current period value
            previous_value: Previous period value
        
        Returns:
            Growth metrics (absolute, percentage)
        """
        if previous_value == 0:
            return {"absolute_change": current_value, "percent_change": None}
        
        absolute_change = current_value - previous_value
        percent_change = (absolute_change / previous_value) * 100
        
        return {
            "absolute_change": round(absolute_change, 2),
            "percent_change": round(percent_change, 2)
        }
