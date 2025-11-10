#!/usr/bin/env python3
"""
TutorAI - A Python Learning Assistant for Kids
A self-contained app for teaching Python programming to children.
"""

import argparse
import sys
import os

from typing import List
from dotenv import load_dotenv
from openai import OpenAI
import io
import gradio as gr
import contextlib
from contextvars import ContextVar

# Import logging functions from logger module
from logger import setup_logging, log_access, log_app_event

# Import AI functions from ai module
from ai import help_gpt, evaluate_gpt, evaluate_gpt_sync

# Import authentication functions from auth module
from auth import access_key_auth

# Context variable to store the current request
_current_request: ContextVar = ContextVar('current_request', default=None)

# Initialize logging
access_logger, app_logger = setup_logging()

# Load questions from file
def load_questions():
    """Load questions from data/questions.txt file."""
    try:
        with open('data/questions.txt', 'r', encoding='utf-8') as f:
            content = f.read().strip()
            # Split by double newlines to get individual questions
            questions = [q.strip() for q in content.split('\n\n') if q.strip()]
            return questions
    except FileNotFoundError:
        print("❌ data/questions.txt not found. Using default questions.")
        # Fallback to default questions
        return [
            "1. Hello, Python! Write a Python program that prints:\nHello, World!",
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
        print("3. Pass it as argument: python src/app.py --api-key your_key_here")
        return None
    
    return openai_api_key

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="TutorAI - A Python Learning Assistant for Kids",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python src/app.py                    # Launch with default settings
  python src/app.py --port 7860       # Launch on specific port
  python src/app.py --api-key sk-...  # Launch with API key
  python src/app.py --share           # Launch with public sharing
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
    
    parser.add_argument(
        '--debug', 
        action='store_true', 
        help='Enable debug mode (verbose logging and error details)'
    )
    
    parser.add_argument(
        '--debugger', 
        choices=['pdb', 'ipdb', 'breakpoint'],
        help='Enable Python debugger (pdb, ipdb, or breakpoint) for interactive debugging'
    )
    
    return parser.parse_args()
 # Function to update username_state from authenticated session
            # This will be called on page load to get the authenticated username

# def run_code(idx, code):
#     """Safely run learner's code."""
#     f = io.StringIO()
#     question = questions[idx % len(questions)]
    
#     # Log code execution attempt
#     log_app_event(app_logger, 'INFO', 'Code execution started', 
#                  f"Question: {question[:50]}... | Code: {code[:100]}...")
    
#     try:
#         with contextlib.redirect_stdout(f):
#             exec(code, {})  # run code in an empty namespace
#         code_output = f.getvalue()
        
#         if not code_output.strip():
#             code_output = "_(No output)_"
        
#         # Log successful execution
#         log_app_event(app_logger, 'INFO', 'Code execution successful', 
#                      f"Question: {question[:50]}... | Output: {code_output[:100]}...")
        
#         return f"### Output\n```\n{code_output}\n```"
#     except Exception as e:
#         # Log execution error
#         log_app_event(app_logger, 'ERROR', 'Code execution failed', 
#                      f"Question: {question[:50]}... | Error: {str(e)} | Code: {code[:100]}...")
        
#         return f"**Error:** {str(e)}"

def run_code_with_evaluation(idx, code, username_state, request: gr.Request | None = None):
    """Run code and stream evaluation like help_wrapper."""
    f = io.StringIO()
    question = questions[idx % len(questions)]
    
    # Get username from gr.State
    username = username_state if username_state else None
    
    # Return username_state (will be updated by demo.load() if needed)
    updated_username_state = username_state
    
    # Log code execution attempt
    log_app_event(app_logger, 'INFO', 'Code execution started', 
                 f"Question: {question[:50]}... | Code: {code[:100]}...", request=None, username=username)
    
    try:
        with contextlib.redirect_stdout(f):
            exec(code, {})  # run code in an empty namespace
        code_output = f.getvalue()
        
        if not code_output.strip():
            code_output = "_(No output)_"
        
        # Log successful execution
        log_app_event(app_logger, 'INFO', 'Code execution successful', 
                     f"Question: {question[:50]}... | Output: {code_output[:100]}...", request=None, username=username)
        
        # Build the output progressively
        base_output = f"### Code Output\n```\n{code_output}\n```\n\n### AI Evaluation\n"
        # Yield result with updated username_state (Gradio will handle state update)
        yield base_output, updated_username_state
        
        # Stream the evaluation with Docker fallback
        log_app_event(app_logger, 'INFO', 'Starting AI evaluation streaming', request=None, username=username)
        try:
            # Try streaming first
            for chunk in evaluate_gpt(question, code, app_logger):
                log_app_event(app_logger, 'DEBUG', f'Evaluation chunk received: {len(chunk)} chars', request=None, username=username)
                yield base_output + chunk, updated_username_state
            log_app_event(app_logger, 'INFO', 'AI evaluation streaming completed', request=None, username=username)
        except Exception as stream_error:
            # Fallback to non-streaming for Docker
            log_app_event(app_logger, 'WARNING', 'Streaming failed, using sync evaluation', 
                         f"Error: {str(stream_error)}", request=None, username=username)
            try:
                # Use non-streaming evaluation
                evaluation_result = evaluate_gpt_sync(question, code, app_logger)
                yield base_output + str(evaluation_result), updated_username_state
                log_app_event(app_logger, 'INFO', 'AI evaluation sync completed', request=None, username=username)
            except Exception as sync_error:
                log_app_event(app_logger, 'ERROR', 'Both streaming and sync evaluation failed', 
                             f"Sync error: {str(sync_error)}", request=None, username=username)
                yield base_output + "AI Evaluation unavailable (Docker environment)", updated_username_state
            
    except Exception as e:
        # Log execution error
        log_app_event(app_logger, 'ERROR', 'Code execution failed', 
                     f"Question: {question[:50]}... | Error: {str(e)} | Code: {code[:100]}...", request=None, username=username)
        
        yield f"**Error:** {str(e)}", updated_username_state

def format_question_for_display(question):
    """Format question text to preserve newlines in Markdown display."""
    # Replace single newlines with HTML line breaks for Gradio Markdown
    # Gradio Markdown supports HTML, so <br> tags will create line breaks
    return question.replace('\n', '<br>')

def next_question(idx):
    """Navigate to next question."""
    idx = (idx + 1) % len(questions)
    return idx, format_question_for_display(questions[idx])

def prev_question(idx):
    """Navigate to previous question."""
    idx = (idx - 1) % len(questions)
    return idx, format_question_for_display(questions[idx])

def help_wrapper(idx, code, username_state):
    """Wrapper around help_gpt to adapt to Gradio."""
    q = questions[idx % len(questions)]
    
    # Get username from gr.State
    username = username_state if username_state else None
    
    # Return username_state (will be updated by demo.load() if needed)
    updated_username_state = username_state
    
    # Log help request
    log_app_event(app_logger, 'INFO', 'Help request received', 
                 f"Question: {q[:50]}... | Code: {code[:100]}...", request=None, username=username)
    
    # call your existing streaming LLM function
    # result = ""
    log_app_event(app_logger, 'INFO', 'Help response streaming completed', request=None, username=username)

    for chunk in help_gpt(q, code, ""):
        yield chunk, updated_username_state


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
            question_label = gr.Markdown(format_question_for_display(questions[0]))
        with gr.Row():
            next_btn = gr.Button("Next Question ➡️")
            prev_btn = gr.Button("⬅️ Previous Question")
            hidden_idx = gr.State(0)  # keep track of current question index
            username_state = gr.State("")  # keep track of current username

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

        # Set username_state from authenticated session (only if auth is enabled)
        def update_username_from_auth(request: gr.Request | None = None):
            """Update username_state from Gradio's authenticated session."""
            # We can't access request here directly, so we'll update it in the button handlers
            # For now, return empty string - it will be updated when buttons are clicked
            return ""
            
        if args.auth:
           
            # Update username_state on page load
            demo.load(
                update_username_from_auth,
                inputs=None,
                outputs=username_state
            )
            
            # Create wrapper functions that update username_state from request
            def run_code_with_auth(idx, code, username_state, request: gr.Request = None):
                """Wrapper that updates username_state from request before calling run_code_with_evaluation."""
                # Update username_state from request if available
                updated_state = username_state
                if request is not None and hasattr(request, 'username') and request.username:
                    updated_state = request.username
                # Call the actual function and return both result and updated state
                for result_chunk, state in run_code_with_evaluation(idx, code, updated_state):
                    yield result_chunk, updated_state
            
            def help_with_auth(idx, code, username_state, request: gr.Request = None):
                """Wrapper that updates username_state from request before calling help_wrapper."""
                # Update username_state from request if available
                updated_state = username_state
                if request is not None and hasattr(request, 'username') and request.username:
                    updated_state = request.username
                # Call the actual function and return both result and updated state
                for result_chunk, state in help_wrapper(idx, code, updated_state):
                    yield result_chunk, updated_state
            
            # Update button handlers to use auth wrappers
            run_btn.click(
                fn=run_code_with_auth,
                inputs=[hidden_idx, code_box, username_state],
                outputs=[result, username_state]
            )
            
            help_btn.click(
                fn=help_with_auth,
                inputs=[hidden_idx, code_box, username_state],
                outputs=[result, username_state]
            )
        else:
            # No auth - use functions directly
            run_btn.click(
                fn=run_code_with_evaluation, 
                inputs=[hidden_idx, code_box, username_state], 
                outputs=[result, username_state]
            )

            help_btn.click(
                fn=help_wrapper,
                inputs=[hidden_idx, code_box, username_state],
                outputs=[result, username_state]
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
            
            # Add middleware to capture requests
            @demo.app.middleware("http")
            async def capture_request(request, call_next):
                """Middleware to capture the current request in context."""
                _current_request.set(request)
                response = await call_next(request)
                return response
            
            # Create authentication function for Gradio
            # Returns username if auth succeeds, which Gradio will use to set request.username
            # We also need to update username_state, but we can't do it directly here
            # Instead, we'll update it via demo.load() and button click handlers
            def gradio_auth(username, password):
                if access_key_auth(username, password, access_logger, enable_debugger=bool(args.debugger)):
                    # Return username - Gradio will store it in request.username
                    # username_state will be updated via demo.load() and button click handlers
                    return username
                return None
            
            print("🚀 Launching with authentication...")
            demo.launch(
                server_name=args.host,
                server_port=args.port,
                share=args.share,
                show_error=True,
                debug=args.debug,
                auth=gradio_auth,
                auth_message="🔐 Please enter your username and access key to access TutorAI"
            )
        else:
            # Launch Gradio directly
            demo.launch(
                server_name=args.host,
                server_port=args.port,
                share=args.share,
                show_error=True,
                debug=args.debug
            )
    except KeyboardInterrupt:
        print("\n👋 TutorAI stopped by user")
    except Exception as e:
        print(f"❌ Error launching app: {e}")
        sys.exit(1)

def main():
    """Main function to run the TutorAI app."""
    print("🚀 Starting TutorAI - Python Learning Assistant...")
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Enable debug logging if debug mode is on
    if args.debug:
        import logging
        logging.getLogger().setLevel(logging.DEBUG)
        access_logger.setLevel(logging.DEBUG)
        app_logger.setLevel(logging.DEBUG)
        print("🐛 Debug mode enabled - verbose logging activated")
    
    # Setup debugger if requested
    if args.debugger:
        if args.debugger == 'pdb':
            import pdb
            pdb.set_trace()
            print("🐛 PDB debugger enabled - breakpoint set at startup")
        elif args.debugger == 'ipdb':
            try:
                import ipdb
                ipdb.set_trace()
                print("🐛 IPDB debugger enabled - breakpoint set at startup")
            except ImportError:
                print("⚠️  ipdb not installed. Install with: pip install ipdb")
                print("🐛 Falling back to pdb...")
                import pdb
                pdb.set_trace()
        elif args.debugger == 'breakpoint':
            # Python 3.7+ built-in breakpoint
            breakpoint()
            print("🐛 Built-in breakpoint() enabled - breakpoint set at startup")
    
    # Log application startup
    log_app_event(app_logger, 'INFO', 'TutorAI application starting')
    log_access(access_logger, 'APP_START', 'Application started')
    
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