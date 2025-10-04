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
        default=7860, 
        help='Port to run the app on (default: 7860)'
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
    
    return parser.parse_args()

def help_gpt_msg(prompt):
    """Get help message from GPT."""
    messages = [
        {"role": "system", "content": "you are an expert python tutor and help kids 10 year old to learn python, and suggest solution based on code and error of code execution"},
        {"role": "user", "content": prompt}
    ]
    completion = openai.chat.completions.create(
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
    stream = openai.chat.completions.create(
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
    try:
        with contextlib.redirect_stdout(f):
            exec(code, {})  # run code in an empty namespace
        output = f.getvalue()
        if not output.strip():
            output = "_(No output)_"
        return f"### Output\n```\n{output}\n```"
    except Exception as e:
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
    # call your existing streaming LLM function
    for chunk in help_gpt(q, code, output):
        yield chunk  # stream chunks as they arrive

def create_gradio_app(openai_client, args):
    """Create and launch the Gradio interface."""
    # Create the Gradio interface
    with gr.Blocks(title="TutorAI - Python Learning Assistant") as demo:
        gr.Markdown("# 🐍 TutorAI - Python Learning Assistant for Kids")
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

        # Help button → streams from your LLM
        help_btn.click(
            fn=help_wrapper,
            inputs=[hidden_idx, code_box, result],
            outputs=result,
        )

    # Launch the app
    print(f"🌐 Starting web interface on http://{args.host}:{args.port}")
    if args.share:
        print("🔗 Public sharing enabled - creating public URL...")
    
    try:
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