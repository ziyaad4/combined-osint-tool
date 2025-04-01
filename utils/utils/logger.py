import datetime
import json
import os
from typing import Dict, Any, Optional

def log_activity(tool: str, query: str, st_session=None) -> Dict[str, Any]:
    """
    Log OSINT tool usage activity.
    
    Args:
        tool: Name of the tool being used
        query: The search query or input value
        st_session: Streamlit session state object
        
    Returns:
        Dictionary containing log entry information
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    log_entry = {
        "timestamp": timestamp,
        "tool": tool,
        "query": query
    }
    
    # Add to session history if available
    if st_session and hasattr(st_session, "history"):
        st_session.history.append(log_entry)
    
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    if not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir)
        except:
            # If we can't create a log directory, we'll skip file logging
            pass
    
    # Log to file (with date-based rotation)
    try:
        log_date = datetime.datetime.now().strftime("%Y-%m-%d")
        log_file = os.path.join(log_dir, f"osint_activity_{log_date}.log")
        
        with open(log_file, "a") as f:
            f.write(f"{timestamp} | {tool} | {query}\n")
    except:
        # If file logging fails, we'll still return the log entry
        pass
    
    return log_entry

def get_activity_logs(days: int = 7) -> list:
    """
    Retrieve activity logs for the specified number of days.
    
    Args:
        days: Number of days of logs to retrieve
        
    Returns:
        List of log entries
    """
    logs = []
    log_dir = "logs"
    
    if not os.path.exists(log_dir):
        return logs
    
    # Calculate date range
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=days)
    
    # Iterate through date range
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        log_file = os.path.join(log_dir, f"osint_activity_{date_str}.log")
        
        if os.path.exists(log_file):
            try:
                with open(log_file, "r") as f:
                    for line in f:
                        parts = line.strip().split(" | ", 2)
                        if len(parts) == 3:
                            timestamp, tool, query = parts
                            logs.append({
                                "timestamp": timestamp,
                                "tool": tool,
                                "query": query
                            })
            except:
                # If we can't read a log file, skip it
                pass
        
        current_date += datetime.timedelta(days=1)
    
    # Sort logs by timestamp (newest first)
    logs.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return logs

def clear_logs(older_than_days: int = 30) -> Dict[str, Any]:
    """
    Clear log files older than the specified number of days.
    
    Args:
        older_than_days: Clear logs older than this many days
        
    Returns:
        Dictionary with result information
    """
    log_dir = "logs"
    
    if not os.path.exists(log_dir):
        return {"status": "No logs directory found"}
    
    # Calculate cutoff date
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=older_than_days)
    deleted_count = 0
    
    # Check all log files
    for filename in os.listdir(log_dir):
        if filename.startswith("osint_activity_") and filename.endswith(".log"):
            try:
                # Extract date from filename
                date_str = filename.replace("osint_activity_", "").replace(".log", "")
                file_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                
                # Delete if older than cutoff
                if file_date < cutoff_date:
                    os.remove(os.path.join(log_dir, filename))
                    deleted_count += 1
            except:
                # Skip files that don't match our expected format
                pass
    
    return {
        "status": "success",
        "deleted_files": deleted_count,
        "cutoff_date": cutoff_date.strftime("%Y-%m-%d")
    }
