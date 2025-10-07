#!/usr/bin/env python3
"""
Log viewer utility for TutorAI.
View access logs and application logs.
"""

import os
import sys
from datetime import datetime

def view_access_logs(lines=50):
    """View access logs."""
    log_file = 'logs/access.log'
    if not os.path.exists(log_file):
        print("❌ No access logs found.")
        return
    
    print("📊 Access Logs (last {} lines):".format(lines))
    print("=" * 80)
    
    with open(log_file, 'r') as f:
        all_lines = f.readlines()
        recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
        
        for line in recent_lines:
            print(line.strip())

def view_app_logs(lines=50):
    """View application logs."""
    log_file = 'logs/app.log'
    if not os.path.exists(log_file):
        print("❌ No application logs found.")
        return
    
    print("📊 Application Logs (last {} lines):".format(lines))
    print("=" * 80)
    
    with open(log_file, 'r') as f:
        all_lines = f.readlines()
        recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
        
        for line in recent_lines:
            print(line.strip())

def view_code_executions():
    """View code execution logs specifically."""
    log_file = 'logs/app.log'
    if not os.path.exists(log_file):
        print("❌ No application logs found.")
        return
    
    print("🐍 Code Execution Logs:")
    print("=" * 80)
    
    with open(log_file, 'r') as f:
        for line in f:
            if 'Code execution' in line:
                print(line.strip())

def view_auth_attempts():
    """View authentication attempts."""
    log_file = 'logs/access.log'
    if not os.path.exists(log_file):
        print("❌ No access logs found.")
        return
    
    print("🔐 Authentication Attempts:")
    print("=" * 80)
    
    with open(log_file, 'r') as f:
        for line in f:
            if 'AUTH_' in line:
                print(line.strip())

def get_log_stats():
    """Get log statistics."""
    access_log = 'logs/access.log'
    app_log = 'logs/app.log'
    
    print("📈 Log Statistics:")
    print("=" * 80)
    
    if os.path.exists(access_log):
        with open(access_log, 'r') as f:
            access_lines = len(f.readlines())
        print(f"Access logs: {access_lines} entries")
    else:
        print("Access logs: No file found")
    
    if os.path.exists(app_log):
        with open(app_log, 'r') as f:
            app_lines = len(f.readlines())
        print(f"Application logs: {app_lines} entries")
    else:
        print("Application logs: No file found")

def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("📊 TutorAI Log Viewer")
        print("=" * 50)
        print("Usage:")
        print("  python view_logs.py access [lines]     - View access logs")
        print("  python view_logs.py app [lines]        - View application logs")
        print("  python view_logs.py code               - View code executions")
        print("  python view_logs.py auth               - View auth attempts")
        print("  python view_logs.py stats              - View log statistics")
        print("  python view_logs.py all [lines]        - View all logs")
        return
    
    command = sys.argv[1]
    
    if command == 'access':
        lines = int(sys.argv[2]) if len(sys.argv) > 2 else 50
        view_access_logs(lines)
    elif command == 'app':
        lines = int(sys.argv[2]) if len(sys.argv) > 2 else 50
        view_app_logs(lines)
    elif command == 'code':
        view_code_executions()
    elif command == 'auth':
        view_auth_attempts()
    elif command == 'stats':
        get_log_stats()
    elif command == 'all':
        lines = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        print("📊 All Logs (last {} lines each):".format(lines))
        print("=" * 80)
        view_access_logs(lines)
        print("\n")
        view_app_logs(lines)
    else:
        print("❌ Unknown command. Use 'python view_logs.py' for help.")

if __name__ == "__main__":
    main()


