#!/usr/bin/env python3
"""
TutorAI - A Python Learning Assistant for Kids
A self-contained app for teaching Python programming to children.
"""

import argparse
import sys
import os
import requests
from bs4 import BeautifulSoup
from typing import List
from dotenv import load_dotenv
from openai import OpenAI
import io
import gradio as gr
import contextlib
import json
import hashlib
import logging
import datetime
import socket
import requests
from auth import create_oauth_app
from auth_access import create_access_key_app
from gradio_auth import create_auth_interface, create_protected_gradio_app

# Setup logging
def setup_logging():
    """Setup logging for access and application logs."""
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Setup access logger
    access_logger = logging.getLogger('access')
    access_logger.setLevel(logging.INFO)
    access_handler = logging.FileHandler('logs/access.log')
    access_formatter = logging.Formatter('%(asctime)s - %(message)s')
    access_handler.setFormatter(access_formatter)
    access_logger.addHandler(access_handler)
    
    # Setup application logger
    app_logger = logging.getLogger('app')
    app_logger.setLevel(logging.INFO)
    app_handler = logging.FileHandler('logs/app.log')
    app_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    app_handler.setFormatter(app_formatter)
    app_logger.addHandler(app_handler)
    
    return access_logger, app_logger

def get_client_ip():
    """Get client IP address."""
    try:
        # Try to get external IP
        response = requests.get('https://api.ipify.org', timeout=5)
        return response.text.strip()
    except:
        try:
            # Fallback to local IP
            hostname = socket.gethostname()
            return socket.gethostbyname(hostname)
        except:
            return 'unknown'

def get_location_from_ip(ip):
    """Get location from IP address."""
    try:
        if ip == 'unknown' or ip.startswith('127.') or ip.startswith('192.168.') or ip.startswith('10.'):
            return 'Local Network'
        
        response = requests.get(f'http://ip-api.com/json/{ip}', timeout=5)
        data = response.json()
        if data['status'] == 'success':
            return f"{data['city']}, {data['regionName']}, {data['country']}"
        else:
            return 'Unknown Location'
    except:
        return 'Unknown Location'

def log_access(access_logger, event_type, details, ip=None, location=None):
    """Log access events."""
    if ip is None:
        ip = get_client_ip()
    if location is None:
        location = get_location_from_ip(ip)
    
    log_entry = f"IP: {ip} | Location: {location} | Event: {event_type} | Details: {details}"
    access_logger.info(log_entry)

def log_app_event(app_logger, level, message, details=None):
    """Log application events."""
    if details:
        full_message = f"{message} | Details: {details}"
    else:
        full_message = message
    
    if level == 'INFO':
        app_logger.info(full_message)
    elif level == 'WARNING':
        app_logger.warning(full_message)
    elif level == 'ERROR':
        app_logger.error(full_message)
    elif level == 'DEBUG':
        app_logger.debug(full_message)

# Initialize logging
access_logger, app_logger = setup_logging()

# Questions for the tutoring session
questions = [
    "1. Hello, Python! Write a Python program that prints:\nHello, World!",
    "2. Introduce Yourself. Create a variable 'name' with your name and print:\nMy name is <your name>",
    "3. Your Age. Store your age in a variable called 'age' and print:\nI am <age> years old",
    "4. Adding Numbers. Make two variables, a = 5 and b = 3. Print their sum like this:\nThe sum of 5 and 3 is 8",
    "5. Counting Fruits. Make a variable 'apples = 4'. Print:\nI have 4 apples",
    "6. Check Data Types. Create these variables: x = 10, y = 3.14, z = 'Python'. Print the type of each variable using type()",
    "7. Swap Values. Create two variables: red = 'apple', yellow = 'banana'. Swap their values and print them",
    "8. Repeat Printing. Print your name 5 times using Python code",
    "9. First Letter. Make a variable word = 'Python'. Print only the first letter of the word",
    "10. Combine Strings. Make two variables: first = 'Good', second = 'Morning'. Print them together as:\nGood Morning"
]

def setup_environment():
    """Load environment variables and validate API keys."""
    load_dotenv(override=True)
    openai_api_key = os.getenv('OPENAI_API_KEY')
    
    if not openai_api_key:
        print("❌ Error: OPENAI_API_KEY not found!")
        print("Please set your OpenAI API key in one of these ways:")
        print("1. Create a .env file with: OPENAI_API_KEY=your_key_here")
        print("2. Set environment variable: export OPENAI_API_KEY=your_key_here")
        print("3. Pass it as argument: python app.py --api-key your_key_here")
        return None, None, None
    
    # OAuth credentials (optional)
    google_client_id = os.getenv('GOOGLE_CLIENT_ID')
    google_client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    redirect_uri = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:7777/auth/callback')
    
    # Only return OAuth credentials if they exist
    if google_client_id and google_client_secret:
        return openai_api_key, google_client_id, google_client_secret, redirect_uri
    else:
        return openai_api_key, None, None, None

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="TutorAI - A Python Learning Assistant for Kids",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python app.py                    # Launch with default settings
  python app.py --port 7860       # Launch on specific port
  python app.py --api-key sk-...  # Launch with API key
  python app.py --share           # Launch with public sharing
        """
    )
    
    parser.add_argument(
        '--port', 
        type=int, 
        default=7777, 
        help='Port to run the app on (default: 7777)'
    )
    
    parser.add_argument(
        '--api-key', 
        type=str, 
        help='OpenAI API key (overrides environment variable)'
    )
    
    parser.add_argument(
        '--share', 
        action='store_true', 
        help='Enable public sharing (creates public URL)'
    )
    
    parser.add_argument(
        '--host', 
        type=str, 
        default='127.0.0.1', 
        help='Host to bind to (default: 127.0.0.1)'
    )
    
    parser.add_argument(
        '--oauth', 
        action='store_true', 
        help='Enable Google OAuth authentication'
    )
    
    parser.add_argument(
        '--auth', 
        action='store_true', 
        help='Enable access key authentication'
    )
    
    return parser.parse_args()

def help_gpt_msg(prompt, openai_client):
    """Get help message from GPT."""
    messages = [
        {"role": "system", "content": "you are an expert python tutor and help kids 10 year old to learn python, and suggest solution based on code and error of code execution"},
        {"role": "user", "content": prompt}
    ]
    completion = openai_client.chat.completions.create(
        model='gpt-4o-mini',
        messages=messages,
    )
    return completion.choices[0].message.content

def help_gpt(q, code, error):
    """Stream help from GPT."""
    messages = [
        {"role": "system", "content": "you are an expert python tutor and help kids 10 year old to learn python, and suggest solution for question q based on code and error of code execution, provide easy to understand explaination for kid in not more than 5 lines, you must guide to get to right solution without providing actual solution"},
        {"role": "user", "content": "question: "+q + " code: "+ code + " output: "+error}
    ]
    stream =OpenAI().chat.completions.create(
        model='gpt-4o-mini',
        messages=messages,
        stream=True
    )
    result = ""
    for chunk in stream:
        result += chunk.choices[0].delta.content or ""
        yield result

def run_code(idx, code):
    """Safely run learner's code."""
    f = io.StringIO()
    question = questions[idx % len(questions)]
    
    # Log code execution attempt
    log_app_event(app_logger, 'INFO', 'Code execution started', 
                 f"Question: {question[:50]}... | Code: {code[:100]}...")
    
    try:
        with contextlib.redirect_stdout(f):
            exec(code, {})  # run code in an empty namespace
        output = f.getvalue()
        if not output.strip():
            output = "_(No output)_"
        
        # Log successful execution
        log_app_event(app_logger, 'INFO', 'Code execution successful', 
                     f"Question: {question[:50]}... | Output: {output[:100]}...")
        
        return f"### Output\n```\n{output}\n```"
    except Exception as e:
        # Log execution error
        log_app_event(app_logger, 'ERROR', 'Code execution failed', 
                     f"Question: {question[:50]}... | Error: {str(e)} | Code: {code[:100]}...")
        
        return f"**Error:** {str(e)}"

def next_question(idx):
    """Navigate to next question."""
    idx = (idx + 1) % len(questions)
    return idx, questions[idx]

def prev_question(idx):
    """Navigate to previous question."""
    idx = (idx - 1) % len(questions)
    return idx, questions[idx]

def help_wrapper(idx, code, output):
    """Wrapper around help_gpt to adapt to Gradio."""
    q = questions[idx % len(questions)]
    
    # Log help request
    log_app_event(app_logger, 'INFO', 'Help request received', 
                 f"Question: {q[:50]}... | Code: {code[:100]}... | Output: {output[:100]}...")
    
    # call your existing streaming LLM function
    # result = ""
    log_app_event(app_logger, 'INFO', 'Help response streaming completed')

    for chunk in help_gpt(q, code, output):
        yield chunk
    
    # Log help response completion
    
    # return result

def help_wrapper_streaming(idx, code, output):
    """Streaming version of help_wrapper for Gradio."""
    q = questions[idx % len(questions)]
    # This is a generator that yields chunks
    for chunk in help_gpt(q, code, output):
        yield chunk

def access_key_auth(username: str, access_key: str) -> bool:
    """Check if user exists in USERS env variable and access key matches ACCESS_KEYS."""
    try:
        # Get users and access keys from environment variables
        users_json = os.getenv('USERS', '[]')
        access_keys_json = os.getenv('ACCESS_KEYS', '[]')
        
        # Parse JSON lists
        users = json.loads(users_json)
        access_keys = json.loads(access_keys_json)
        
        # Check if username exists in users list
        if username not in users:
            log_access(access_logger, 'AUTH_FAILED', f'Username not found: {username}')
            return False
        
        # Get user index to match with access key
        user_index = users.index(username)
        
        # Check if access key matches (with same index)
        if user_index < len(access_keys):
            # Hash the provided access key for comparison
            hashed_key = hashlib.sha256(access_key.encode()).hexdigest()
            stored_key = access_keys[user_index]
            
            # Compare hashed keys
            if hashed_key == stored_key:
                log_access(access_logger, 'AUTH_SUCCESS', f'User authenticated: {username}')
                return True
            else:
                log_access(access_logger, 'AUTH_FAILED', f'Invalid access key for user: {username}')
                return False
        
        log_access(access_logger, 'AUTH_FAILED', f'No access key found for user: {username}')
        return False
        
    except (json.JSONDecodeError, ValueError, IndexError) as e:
        log_access(access_logger, 'AUTH_ERROR', f'Authentication error: {str(e)}')
        return False

def create_gradio_app(openai, args, oauth_credentials=None):
    """Create and launch the Gradio interface."""
    # Create the Gradio interface
    with gr.Blocks(title="TutorAI - Python Learning Assistant") as demo:
        gr.Markdown("# 🐍 TutorAI - Your Learning buddy")
        gr.Markdown("Learn Python programming step by step with interactive exercises!")
        
        with gr.Row():
            question_label = gr.Markdown(questions[0])
        with gr.Row():
            next_btn = gr.Button("Next Question ➡️")
            prev_btn = gr.Button("⬅️ Previous Question")
            hidden_idx = gr.State(0)  # keep track of current question index

        with gr.Row():
            code_box = gr.Code(label="Write your Python code here", language="python", lines=10)

        with gr.Row():
            run_btn = gr.Button("🚀 Run Code")
            help_btn = gr.Button("💡 Get Help")

        with gr.Row():
            result = gr.Markdown()

        # Navigation
        next_btn.click(fn=next_question, inputs=hidden_idx, outputs=[hidden_idx, question_label])
        prev_btn.click(fn=prev_question, inputs=hidden_idx, outputs=[hidden_idx, question_label])

        # Run code
        run_btn.click(fn=run_code, inputs=[hidden_idx, code_box], outputs=result)

        # Help button → streams help from your LLM
        help_btn.click(
            fn=help_wrapper,
            inputs=[hidden_idx, code_box, result],
            outputs=result,
        )

    # Launch the app
    print(f"🌐 Starting web interface on http://{args.host}:{args.port}")
    if args.share:
        print("🔗 Public sharing enabled - creating public URL...")
        log_app_event(app_logger, 'INFO', 'Public sharing enabled')
    
    # Log launch configuration
    log_app_event(app_logger, 'INFO', f'Launching on {args.host}:{args.port}', 
                 f'Share: {args.share}, Auth: {args.auth}, OAuth: {args.oauth}')
    
    try:
        if args.oauth and oauth_credentials:
            # For OAuth, we'll use a simple username/password approach
            # since Gradio doesn't support OAuth directly
            print("🔐 OAuth authentication requested")
            print("📝 Make sure to configure your Google OAuth credentials in .env file")
            print("💡 Note: Using access key authentication instead of OAuth")
            print("   (OAuth requires custom implementation with Flask)")
            
            # Create authentication function for Gradio
            def gradio_auth(username, password):
                return access_key_auth(username, password)
            
            print("🚀 Launching with authentication...")
            demo.launch(
                server_name=args.host,
                server_port=args.port,
                share=args.share,
                show_error=True,
                auth=gradio_auth,
                auth_message="🔐 Please enter your username and access key to access TutorAI"
            )
        elif args.auth:
            # Use Gradio's built-in authentication
            print("🔑 Access key authentication enabled")
            print("📝 Make sure to configure USERS and ACCESS_KEYS in .env file")
            
            # Create authentication function for Gradio
            def gradio_auth(username, password):
                return access_key_auth(username, password)
            
            print("🚀 Launching with Gradio authentication...")
            demo.launch(
                server_name=args.host,
                server_port=args.port,
                share=args.share,
                show_error=True,
                auth=gradio_auth,
                auth_message="🔐 Please enter your username and access key to access TutorAI"
            )
        else:
            # Launch Gradio directly
            demo.launch(
                server_name=args.host,
                server_port=args.port,
                share=args.share,
                show_error=True
            )
    except KeyboardInterrupt:
        print("\n👋 TutorAI stopped by user")
    except Exception as e:
        print(f"❌ Error launching app: {e}")
        sys.exit(1)

def main():
    """Main function to run the TutorAI app."""
    print("🚀 Starting TutorAI - Python Learning Assistant...")
    
    # Log application startup
    log_app_event(app_logger, 'INFO', 'TutorAI application starting')
    log_access(access_logger, 'APP_START', 'Application started')
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Setup environment and validate API key
    if args.api_key:
        os.environ['OPENAI_API_KEY'] = args.api_key
        openai_api_key = args.api_key
        oauth_credentials = None
    else:
        env_result = setup_environment()
        if not env_result or len(env_result) < 1:
            sys.exit(1)
        openai_api_key, google_client_id, google_client_secret, redirect_uri = env_result
        if google_client_id and google_client_secret:
            oauth_credentials = (google_client_id, google_client_secret, redirect_uri)
        else:
            oauth_credentials = None
     # Initialize OpenAI client
    try:
        openai = OpenAI()
        print("✅ OpenAI client initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing OpenAI client: {e}")
        sys.exit(1)

   
    # Create the Gradio interface
    create_gradio_app(openai, args, oauth_credentials)

if __name__ == "__main__":
    main()