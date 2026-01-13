"""
Viewer for Local JSON Traces
"""
import json
from pathlib import Path
from datetime import datetime
import sys


def format_trace(trace_file: Path) -> str:
    """Format a trace file for display"""
    with open(trace_file, 'r', encoding='utf-8') as f:
        trace = json.load(f)
    
    output = []
    output.append("=" * 80)
    output.append(f"TRACE: {trace_file.name}")
    output.append("=" * 80)
    
    # Basic info
    output.append(f"\nType: {trace.get('type', 'unknown').upper()}")
    output.append(f"Run ID: {trace.get('run_id', 'unknown')[:16]}...")
    output.append(f"Parent: {trace.get('parent_run_id', 'None')}")
    output.append(f"Start: {trace.get('start_time', 'unknown')}")
    output.append(f"End: {trace.get('end_time', 'unknown')}")
    
    if 'duration_seconds' in trace:
        output.append(f"Duration: {trace['duration_seconds']:.3f}s")
    
    # Tags and metadata
    if trace.get('tags'):
        output.append(f"\nTags: {', '.join(trace['tags'])}")
    
    if trace.get('metadata'):
        output.append(f"Metadata: {json.dumps(trace['metadata'], indent=2)}")
    
    # Type-specific info
    if trace['type'] == 'llm':
        output.append(f"\n--- LLM CALL ---")
        output.append(f"Model: {trace.get('model', 'unknown')}")
        output.append(f"\nPrompts ({len(trace.get('prompts', []))}):")
        for i, prompt in enumerate(trace.get('prompts_preview', []), 1):
            output.append(f"  {i}. {prompt}")
        
        if 'generations' in trace:
            output.append(f"\nGenerations ({len(trace['generations'])}):")
            for i, gen in enumerate(trace['generations'], 1):
                output.append(f"  {i}. {gen.get('text_preview', gen.get('text', ''))}")
    
    elif trace['type'] == 'agent_node':
        output.append(f"\n--- AGENT NODE EXECUTION ---")
        output.append(f"Node: {trace.get('node_name', 'unknown').upper()}")
        
        if 'summary' in trace:
            output.append(f"Summary: {trace['summary']}")
        
        if 'inputs' in trace:
            output.append(f"\nInputs (truncated):")
            inputs = trace['inputs']
            if isinstance(inputs, dict):
                for key in list(inputs.keys())[:5]:  # Show first 5 keys
                    value = str(inputs[key])[:100]
                    output.append(f"  {key}: {value}...")
        
        if 'outputs' in trace:
            output.append(f"\nOutputs (truncated):")
            outputs = trace['outputs']
            if isinstance(outputs, dict):
                for key in list(outputs.keys())[:5]:  # Show first 5 keys
                    value = str(outputs[key])[:100]
                    output.append(f"  {key}: {value}...")
    
    elif trace['type'] == 'chain':
        output.append(f"\n--- CHAIN EXECUTION ---")
        output.append(f"Chain Type: {trace.get('chain_type', 'unknown')}")
        
        if 'inputs' in trace:
            output.append(f"\nInputs:")
            output.append(f"  {json.dumps(trace['inputs'], indent=4)}")
        
        if 'outputs' in trace:
            output.append(f"\nOutputs:")
            output.append(f"  {json.dumps(trace['outputs'], indent=4)}")
    
    # Errors
    if 'error' in trace:
        output.append(f"\n!!! ERROR !!!")
        output.append(f"  {trace['error']}")
    
    output.append("\n" + "=" * 80)
    output.append("")
    
    return "\n".join(output)


def view_latest_traces(n: int = 5):
    """View the latest n traces"""
    traces_dir = Path("traces")
    
    if not traces_dir.exists():
        print("No traces directory found. Run some queries first!")
        return
    
    trace_files = sorted(traces_dir.glob("trace_*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
    
    if not trace_files:
        print("No trace files found. Run some queries first!")
        return
    
    print(f"\n{'='*80}")
    print(f"SHOWING LATEST {min(n, len(trace_files))} TRACES (out of {len(trace_files)} total)")
    print(f"{'='*80}\n")
    
    for trace_file in trace_files[:n]:
        print(format_trace(trace_file))


def view_all_traces():
    """View all traces"""
    traces_dir = Path("traces")
    
    if not traces_dir.exists():
        print("No traces directory found. Run some queries first!")
        return
    
    trace_files = sorted(traces_dir.glob("trace_*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
    
    if not trace_files:
        print("No trace files found. Run some queries first!")
        return
    
    print(f"\n{'='*80}")
    print(f"SHOWING ALL {len(trace_files)} TRACES")
    print(f"{'='*80}\n")
    
    for trace_file in trace_files:
        print(format_trace(trace_file))


def list_traces():
    """List all trace files"""
    traces_dir = Path("traces")
    
    if not traces_dir.exists():
        print("No traces directory found. Run some queries first!")
        return
    
    trace_files = sorted(traces_dir.glob("trace_*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
    
    if not trace_files:
        print("No trace files found. Run some queries first!")
        return
    
    print(f"\nFound {len(trace_files)} trace files:\n")
    
    for i, trace_file in enumerate(trace_files, 1):
        mtime = datetime.fromtimestamp(trace_file.stat().st_mtime)
        size = trace_file.stat().st_size / 1024  # KB
        print(f"{i:3d}. {trace_file.name:50s} | {mtime.strftime('%Y-%m-%d %H:%M:%S')} | {size:6.1f} KB")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "list":
            list_traces()
        elif command == "all":
            view_all_traces()
        elif command.isdigit():
            view_latest_traces(int(command))
        else:
            print("Usage:")
            print("  python view_traces.py        - View latest 5 traces")
            print("  python view_traces.py list   - List all trace files")
            print("  python view_traces.py all    - View all traces")
            print("  python view_traces.py N      - View latest N traces")
    else:
        view_latest_traces(5)
