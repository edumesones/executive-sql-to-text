"""
Custom Callback Handler for Local Tracing
Saves detailed traces to JSON files for inspection
"""
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult
from langchain_core.messages import BaseMessage


class LocalJSONTracer(BaseCallbackHandler):
    """
    Custom callback handler that saves traces to JSON files
    """
    
    def __init__(self, trace_dir: str = "traces"):
        """Initialize the tracer with a directory for trace files"""
        self.trace_dir = Path(trace_dir)
        self.trace_dir.mkdir(exist_ok=True)
        
        # Current run tracking
        self.current_run = None
        self.runs = {}
        self.session_start = datetime.now()
    
    def _get_run_file(self, run_id: UUID) -> Path:
        """Get the file path for a run"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.trace_dir / f"trace_{timestamp}_{str(run_id)[:8]}.json"
    
    def on_llm_start(
        self,
        serialized: Dict[str, Any],
        prompts: List[str],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Run when LLM starts"""
        run_data = {
            "run_id": str(run_id),
            "parent_run_id": str(parent_run_id) if parent_run_id else None,
            "type": "llm",
            "start_time": datetime.now().isoformat(),
            "tags": tags or [],
            "metadata": metadata or {},
            "model": serialized.get("kwargs", {}).get("model_name", "unknown"),
            "prompts": prompts,
            "prompts_preview": [p[:200] + "..." if len(p) > 200 else p for p in prompts],
        }
        self.runs[run_id] = run_data
    
    def on_llm_end(
        self,
        response: LLMResult,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Run when LLM ends"""
        if run_id not in self.runs:
            return
        
        run_data = self.runs[run_id]
        run_data["end_time"] = datetime.now().isoformat()
        
        # Extract response
        generations = []
        for gen_list in response.generations:
            for gen in gen_list:
                generations.append({
                    "text": gen.text,
                    "text_preview": gen.text[:200] + "..." if len(gen.text) > 200 else gen.text,
                })
        
        run_data["generations"] = generations
        run_data["llm_output"] = response.llm_output
        
        # Calculate duration
        start = datetime.fromisoformat(run_data["start_time"])
        end = datetime.fromisoformat(run_data["end_time"])
        run_data["duration_seconds"] = (end - start).total_seconds()
        
        # Save to file
        self._save_run(run_id)
    
    def on_llm_error(
        self,
        error: Exception,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Run when LLM errors"""
        if run_id not in self.runs:
            return
        
        run_data = self.runs[run_id]
        run_data["end_time"] = datetime.now().isoformat()
        run_data["error"] = str(error)
        run_data["status"] = "error"
        
        # Save to file
        self._save_run(run_id)
    
    def on_chain_start(
        self,
        serialized: Dict[str, Any],
        inputs: Dict[str, Any],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Run when chain starts"""
        # Determine if this is a workflow node (agent)
        node_name = metadata.get("langgraph_node") if metadata else None
        chain_type = serialized.get("id", ["unknown"])[-1]
        
        # Only save traces for workflow nodes (agents) or important chains
        if not node_name and chain_type not in ["RunnableSequence", "RunnableLambda"]:
            return
        
        run_data = {
            "run_id": str(run_id),
            "parent_run_id": str(parent_run_id) if parent_run_id else None,
            "type": "agent_node" if node_name else "chain",
            "node_name": node_name,
            "start_time": datetime.now().isoformat(),
            "tags": tags or [],
            "metadata": metadata or {},
            "chain_type": chain_type,
            "inputs": self._truncate_dict(inputs),
        }
        self.runs[run_id] = run_data
    
    def on_chain_end(
        self,
        outputs: Dict[str, Any],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Run when chain ends"""
        if run_id not in self.runs:
            return
        
        run_data = self.runs[run_id]
        run_data["end_time"] = datetime.now().isoformat()
        run_data["outputs"] = self._truncate_dict(outputs)
        run_data["status"] = "success"
        
        # Calculate duration
        start = datetime.fromisoformat(run_data["start_time"])
        end = datetime.fromisoformat(run_data["end_time"])
        run_data["duration_seconds"] = (end - start).total_seconds()
        
        # Add summary for agent nodes
        if run_data.get("type") == "agent_node":
            run_data["summary"] = self._create_node_summary(run_data)
        
        # Save to file
        self._save_run(run_id)
    
    def on_chain_error(
        self,
        error: Exception,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Run when chain errors"""
        if run_id not in self.runs:
            return
        
        run_data = self.runs[run_id]
        run_data["end_time"] = datetime.now().isoformat()
        run_data["error"] = str(error)
        run_data["status"] = "error"
        
        # Save to file
        self._save_run(run_id)
    
    def _truncate_dict(self, d: Dict[str, Any], max_str_len: int = 500) -> Dict[str, Any]:
        """Truncate long strings in a dictionary"""
        result = {}
        for k, v in d.items():
            if isinstance(v, str):
                result[k] = v[:max_str_len] + "..." if len(v) > max_str_len else v
            elif isinstance(v, dict):
                result[k] = self._truncate_dict(v, max_str_len)
            elif isinstance(v, list):
                result[k] = [
                    item[:max_str_len] + "..." if isinstance(item, str) and len(item) > max_str_len else item
                    for item in v[:10]  # Limit to first 10 items
                ]
            else:
                result[k] = v
        return result
    
    def _create_node_summary(self, run_data: Dict[str, Any]) -> str:
        """Create a human-readable summary for agent nodes"""
        node_name = run_data.get("node_name", "unknown")
        duration = run_data.get("duration_seconds", 0)
        outputs = run_data.get("outputs", {})
        
        if node_name == "sql_agent":
            return f"Generated SQL query in {duration:.2f}s"
        elif node_name == "analyst_agent":
            result_count = len(outputs.get("query_results", []))
            return f"Executed query and retrieved {result_count} rows in {duration:.2f}s"
        elif node_name == "viz_agent":
            chart_type = outputs.get("chart_type", "none")
            return f"Created {chart_type} visualization in {duration:.2f}s"
        elif node_name == "insight_agent":
            insight_count = len(outputs.get("insights", []))
            return f"Generated {insight_count} insights in {duration:.2f}s"
        else:
            return f"Completed in {duration:.2f}s"
    
    def _save_run(self, run_id: UUID) -> None:
        """Save a run to a JSON file"""
        run_data = self.runs[run_id]
        file_path = self._get_run_file(run_id)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(run_data, f, indent=2, ensure_ascii=False)
        
        # Clean up from memory
        del self.runs[run_id]


def get_local_tracer(enabled: bool = True) -> Optional[LocalJSONTracer]:
    """
    Get a local JSON tracer if enabled
    
    Args:
        enabled: Whether to enable tracing
    
    Returns:
        LocalJSONTracer if enabled, None otherwise
    """
    if not enabled:
        return None
    
    return LocalJSONTracer(trace_dir="traces")
