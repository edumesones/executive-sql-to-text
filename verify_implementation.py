"""
Quick test script to verify the implementation

Tests:
1. Logging setup
2. Metrics tracking
3. API imports
4. Frontend file exists
"""
import sys
from pathlib import Path

# Colors for terminal
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def test_logging():
    """Test logging module"""
    try:
        from src.utils.logging import setup_logging, get_logger
        logger = setup_logging(log_level="INFO", console_output=False)
        logger.info("test_event", test_key="test_value")
        print(f"{GREEN}OK{RESET} Logging module works")
        return True
    except Exception as e:
        print(f"{RED}FAIL{RESET} Logging module failed: {e}")
        return False


def test_metrics():
    """Test metrics module"""
    try:
        from src.utils.metrics import WorkflowMetrics, TimerContext
        metrics = WorkflowMetrics(session_id="test-123")
        metrics.start()
        metrics.complete()
        with TimerContext() as timer:
            pass
        assert timer.duration_ms >= 0
        print(f"{GREEN}OK{RESET} Metrics module works")
        return True
    except Exception as e:
        print(f"{RED}FAIL{RESET} Metrics module failed: {e}")
        return False


def test_api():
    """Test API modules"""
    try:
        from src.api import app, router
        from src.api.schemas import QueryRequest, QueryResponse, HealthResponse
        assert app is not None
        assert router is not None
        print(f"{GREEN}OK{RESET} API modules work")
        return True
    except Exception as e:
        print(f"{RED}FAIL{RESET} API modules failed: {e}")
        return False


def test_frontend():
    """Test frontend file exists"""
    try:
        frontend_file = Path("frontend/streamlit_app.py")
        assert frontend_file.exists()
        print(f"{GREEN}OK{RESET} Frontend file exists")
        return True
    except Exception as e:
        print(f"{RED}FAIL{RESET} Frontend file check failed: {e}")
        return False


def test_nodes_instrumentation():
    """Test that nodes are instrumented with logging"""
    try:
        from src.graph.nodes import sql_agent_node
        import inspect
        source = inspect.getsource(sql_agent_node)
        assert "logger.info" in source
        print(f"{GREEN}OK{RESET} Workflow nodes are instrumented")
        return True
    except Exception as e:
        print(f"{RED}FAIL{RESET} Nodes instrumentation check failed: {e}")
        return False


def test_requirements():
    """Test that structlog is in requirements"""
    try:
        with open("requirements.txt", "r") as f:
            content = f.read()
        assert "structlog" in content
        print(f"{GREEN}OK{RESET} Requirements updated with structlog")
        return True
    except Exception as e:
        print(f"{RED}FAIL{RESET} Requirements check failed: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("Testing Implementation")
    print("="*60 + "\n")
    
    tests = [
        ("Logging Module", test_logging),
        ("Metrics Module", test_metrics),
        ("API Modules", test_api),
        ("Frontend File", test_frontend),
        ("Nodes Instrumentation", test_nodes_instrumentation),
        ("Requirements", test_requirements)
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\nTesting {name}...")
        results.append(test_func())
    
    # Summary
    print("\n" + "="*60)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"{GREEN}SUCCESS: All tests passed ({passed}/{total}){RESET}")
        print("\nImplementation verified successfully!")
        print("\nNext steps:")
        print("  1. pip install -r requirements.txt")
        print("  2. python run_api.py")
        print("  3. python run_frontend.py")
    else:
        print(f"{YELLOW}WARNING: Some tests failed ({passed}/{total}){RESET}")
        print("\nPlease fix the issues above before proceeding.")
    
    print("="*60 + "\n")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
