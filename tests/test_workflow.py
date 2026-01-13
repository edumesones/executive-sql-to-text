"""
Test script for complete workflow with observability
"""
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.graph import create_initial_state, get_workflow
from src.utils.logging import setup_logging

# Setup logging
logger = setup_logging(log_level="INFO", console_output=True)


async def test_workflow():
    """Test the complete multi-agent workflow"""
    
    logger.info("test_workflow_started", query="Show me the top 10 loans by amount")
    
    # Create initial state
    state = create_initial_state(
        user_query="Show me the top 10 loans by amount",
        session_id="test-123"
    )
    
    print("🚀 Starting workflow...")
    print(f"Query: {state['user_query']}")
    print("-" * 80)
    
    # Get workflow
    workflow = get_workflow()
    
    # Execute workflow
    try:
        result = await workflow.ainvoke(state)
        
        print("\n✅ Workflow completed!")
        print("-" * 80)
        
        # Display results
        print("\n📊 SQL Query:")
        print(result.get('sql_query', 'N/A'))
        
        print("\n📈 Results:")
        print(f"Rows returned: {result.get('result_count', 0)}")
        
        print("\n📊 Derived Metrics:")
        metrics = result.get('derived_metrics', {})
        for key, value in metrics.items():
            print(f"  {key}: {value}")
        
        print("\n📉 Chart Type:")
        print(result.get('chart_type', 'N/A'))
        
        print("\n💡 Insights:")
        for insight in result.get('insights', []):
            print(f"  • {insight}")
        
        print("\n🎯 Recommendations:")
        for rec in result.get('recommendations', []):
            print(f"  • {rec}")
        
        # Display performance metrics
        if result.get('metrics'):
            print("\n⏱️ Performance Metrics:")
            perf = result['metrics']
            print(f"  Total Duration: {perf.get('total_duration_ms', 0)}ms")
            print(f"  SQL Agent: {perf.get('sql_agent_duration_ms', 0)}ms")
            print(f"  Analyst Agent: {perf.get('analyst_agent_duration_ms', 0)}ms")
            print(f"  Viz Agent: {perf.get('viz_agent_duration_ms', 0)}ms")
            print(f"  Insight Agent: {perf.get('insight_agent_duration_ms', 0)}ms")
        
        if result.get('errors'):
            print("\n❌ Errors:")
            for error in result['errors']:
                print(f"  • {error}")
        
        if result.get('warnings'):
            print("\n⚠️ Warnings:")
            for warning in result['warnings']:
                print(f"  • {warning}")
        
        logger.info("test_workflow_completed", 
                   success=not result.get('errors'),
                   total_duration_ms=result.get('metrics', {}).get('total_duration_ms', 0))
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        logger.error("test_workflow_failed", error=str(e), exc_info=True)
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_workflow())
