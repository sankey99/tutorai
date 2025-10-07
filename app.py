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

def get_browser_location_from_ip(ip):
    """Get browser location from IP address (client-side location)."""
    try:
        if ip == 'unknown' or ip.startswith('127.') or ip.startswith('192.168.') or ip.startswith('10.'):
            return 'Local Network'
        
        # Use a geolocation service to get browser location
        response = requests.get(f'http://ip-api.com/json/{ip}', timeout=5)
        data = response.json()
        if data['status'] == 'success':
            return f"{data['city']}, {data['regionName']}, {data['country']}"
        else:
            return 'Unknown Browser Location'
    except:
        return 'Unknown Browser Location'

def log_access(access_logger, event_type, details, ip=None, location=None):
    """Log access events with browser location."""
    if ip is None:
        ip = get_client_ip()
    if location is None:
        # Get browser location instead of server location
        location = get_browser_location_from_ip(ip)
    
    log_entry = f"IP: {ip} | Browser Location: {location} | Event: {event_type} | Details: {details}"
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

# Load questions from file
def load_questions():
    """Load questions from questions.txt file."""
    try:
        with open('questions.txt', 'r', encoding='utf-8') as f:
            content = f.read().strip()
            # Split by double newlines to get individual questions
            questions = [q.strip() for q in content.split('\n\n') if q.strip()]
            return questions
    except FileNotFoundError:
        print("❌ questions.txt not found. Using default questions.")
        # Fallback to default questions
        return [
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
    except Exception as e:
        print(f"❌ Error loading questions: {e}")
        return ["1. Hello, Python! Write a Python program that prints:\nHello, World!"]

# Load questions from file
questions = load_questions()

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
        return None
    
    return openai_api_key

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
        '--auth', 
        action='store_true', 
        help='Enable access key authentication'
    )
    
    return parser.parse_args()

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

def evaluate_gpt(q, code):
    """Stream evaluation from GPT for student's code solution."""
    log_app_event(app_logger, 'INFO', 'evaluate_gpt called', f"Question: {q[:50]}... | Code: {code[:50]}...")
    messages = [
        {"role": "system", "content": "you are an expert python tutor and help kids 10 year old to learn python, evaluate solution of q as provided on code, if its about expected output, Say Good Job, otherwise provide hint on what is expected without providing actual solution "},
        {"role": "user", "content": "question: "+q + " code: "+ code }
    ]
    try:
        stream =OpenAI().chat.completions.create(
            model='gpt-4o-mini',
            messages=messages,
            stream=True
        )
        result = ""
        for chunk in stream:
            content = chunk.choices[0].delta.content or ""
            result += content
            log_app_event(app_logger, 'DEBUG', f'evaluate_gpt chunk: {len(content)} chars')
            yield result
        log_app_event(app_logger, 'INFO', 'evaluate_gpt completed', f"Final result length: {len(result)}")
    except Exception as e:
        log_app_event(app_logger, 'ERROR', 'evaluate_gpt failed', f"Error: {str(e)}")
        yield f"AI Evaluation Error: {str(e)}"

def evaluate_gpt_sync(q, code):
    """Non-streaming evaluation from GPT for Docker environments."""
    log_app_event(app_logger, 'INFO', 'evaluate_gpt_sync called', f"Question: {q[:50]}... | Code: {code[:50]}...")
    messages = [
        {"role": "system", "content": "you are an expert python tutor and help kids 10 year old to learn python, evaluate solution of q as provided on code, if its about expected output, Say Good Job, otherwise provide hint on what is expected without providing actual solution "},
        {"role": "user", "content": "question: "+q + " code: "+ code }
    ]
    try:
        completion = OpenAI().chat.completions.create(
            model='gpt-4o-mini',
            messages=messages
        )
        result = completion.choices[0].message.content
        log_app_event(app_logger, 'INFO', 'evaluate_gpt_sync completed', f"Result length: {len(result)}")
        return result
    except Exception as e:
        log_app_event(app_logger, 'ERROR', 'evaluate_gpt_sync failed', f"Error: {str(e)}")
        return f"AI Evaluation Error: {str(e)}"

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
        code_output = f.getvalue()
        
        if not code_output.strip():
            code_output = "_(No output)_"
        
        # Log successful execution
        log_app_event(app_logger, 'INFO', 'Code execution successful', 
                     f"Question: {question[:50]}... | Output: {code_output[:100]}...")
        
        return f"### Output\n```\n{code_output}\n```"
    except Exception as e:
        # Log execution error
        log_app_event(app_logger, 'ERROR', 'Code execution failed', 
                     f"Question: {question[:50]}... | Error: {str(e)} | Code: {code[:100]}...")
        
        return f"**Error:** {str(e)}"

def run_code_with_evaluation(idx, code, resultop, evaluationop):
    """Run code and stream evaluation like help_wrapper."""
    f = io.StringIO()
    question = questions[idx % len(questions)]
    
    # Log code execution attempt
    log_app_event(app_logger, 'INFO', 'Code execution started', 
                 f"Question: {question[:50]}... | Code: {code[:100]}...")
    
    try:
        with contextlib.redirect_stdout(f):
            exec(code, {})  # run code in an empty namespace
        code_output = f.getvalue()
        
        if not code_output.strip():
            code_output = "_(No output)_"
        
        # Log successful execution
        log_app_event(app_logger, 'INFO', 'Code execution successful', 
                     f"Question: {question[:50]}... | Output: {code_output[:100]}...")
        
        # Build the output progressively
        base_output = f"### Code Output\n```\n{code_output}\n```\n\n### AI Evaluation\n"
        yield base_output
        
        # Stream the evaluation with Docker fallback
        log_app_event(app_logger, 'INFO', 'Starting AI evaluation streaming')
        try:
            # Try streaming first
            for chunk in evaluate_gpt(question, code):
                log_app_event(app_logger, 'DEBUG', f'Evaluation chunk received: {len(chunk)} chars')
                yield base_output + chunk
            log_app_event(app_logger, 'INFO', 'AI evaluation streaming completed')
        except Exception as stream_error:
            # Fallback to non-streaming for Docker
            log_app_event(app_logger, 'WARNING', 'Streaming failed, using sync evaluation', 
                         f"Error: {str(stream_error)}")
            try:
                # Use non-streaming evaluation
                evaluation_result = evaluate_gpt_sync(question, code)
                yield base_output + evaluation_result
                log_app_event(app_logger, 'INFO', 'AI evaluation sync completed')
            except Exception as sync_error:
                log_app_event(app_logger, 'ERROR', 'Both streaming and sync evaluation failed', 
                             f"Sync error: {str(sync_error)}")
                yield base_output + "AI Evaluation unavailable (Docker environment)"
            
    except Exception as e:
        # Log execution error
        log_app_event(app_logger, 'ERROR', 'Code execution failed', 
                     f"Question: {question[:50]}... | Error: {str(e)} | Code: {code[:100]}...")
        
        yield f"**Error:** {str(e)}"

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


def access_key_auth(username: str, access_key: str) -> bool:
    """Check if user exists in USERS env variable and access key matches ACCESS_KEYS.
    The access key is hashed with SHA256 before comparison."""
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
            stored_key = access_keys[user_index]
            
            # Hash the access key with SHA256 before comparing
            hashed_access_key = hashlib.sha256(access_key.encode()).hexdigest()
            if hashed_access_key.lower() == stored_key.lower():
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

def create_gradio_app(openai, args):
    """Create and launch the Gradio interface."""
    # Create the Gradio interface
    with gr.Blocks(title="TutorAI - Python Learning Assistant", css="""
        .gradio-container {
            font-family: Arial, sans-serif;
        }
        .login-form {
            max-width: 400px;
            margin: 50px auto;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 8px;
            background: white;
        }
    """) as demo:
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

        with gr.Row():
            evaluation = gr.Markdown()

        # Navigation
        next_btn.click(fn=next_question, inputs=hidden_idx, outputs=[hidden_idx, question_label])
        prev_btn.click(fn=prev_question, inputs=hidden_idx, outputs=[hidden_idx, question_label])

        # Run code
        run_btn.click(
            fn=run_code_with_evaluation, 
            inputs=[hidden_idx, code_box], 
            outputs=result
        )

        # Help button → streams help from your LLM
        help_btn.click(
            fn=help_wrapper,
            inputs=[hidden_idx, code_box, result],
            outputs=result
        )

    # Launch the app
    print(f"🌐 Starting web interface on http://{args.host}:{args.port}")
    if args.share:
        print("🔗 Public sharing enabled - creating public URL...")
        log_app_event(app_logger, 'INFO', 'Public sharing enabled')
    
    # Log launch configuration
    log_app_event(app_logger, 'INFO', f'Launching on {args.host}:{args.port}', 
                 f'Share: {args.share}, Auth: {args.auth}')
    
    try:
        if args.auth:
            # Use Gradio's built-in authentication
            print("🔑 Access key authentication enabled")
            print("📝 Make sure to configure USERS and ACCESS_KEYS in .env file")
            print("🔒 Using Gradio's built-in authentication system")
            
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
    else:
        openai_api_key = setup_environment()
        if not openai_api_key:
            sys.exit(1)
     # Initialize OpenAI client
    try:
        openai = OpenAI()
        print("✅ OpenAI client initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing OpenAI client: {e}")
        sys.exit(1)

   
    # Create the Gradio interface
    create_gradio_app(openai, args)

if __name__ == "__main__":
    main()