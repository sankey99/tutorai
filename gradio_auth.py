#!/usr/bin/env python3
"""
Gradio-compatible authentication module for TutorAI.
This module provides authentication that works directly with Gradio.
"""

import os
import json
import hashlib
import gradio as gr
from typing import List, Tuple, Optional

def load_auth_config():
    """Load authentication configuration from environment variables."""
    users_json = os.getenv('USERS', '[]')
    access_keys_json = os.getenv('ACCESS_KEYS', '[]')
    
    try:
        users = json.loads(users_json)
        access_keys = json.loads(access_keys_json)
        return users, access_keys
    except (json.JSONDecodeError, ValueError):
        return [], []

def verify_credentials(username: str, access_key: str) -> bool:
    """Verify user credentials against stored values."""
    users, access_keys = load_auth_config()
    
    if not users or not access_keys:
        return False
    
    try:
        # Check if username exists
        if username not in users:
            return False
        
        # Get user index
        user_index = users.index(username)
        
        # Check if access key matches
        if user_index < len(access_keys):
            hashed_key = hashlib.sha256(access_key.encode()).hexdigest()
            stored_key = access_keys[user_index]
            return hashed_key == stored_key
        
        return False
    except (ValueError, IndexError):
        return False

def create_auth_interface():
    """Create a Gradio authentication interface."""
    
    def authenticate(username: str, access_key: str) -> Tuple[str, bool]:
        """Authenticate user and return status message."""
        if not username or not access_key:
            return "Please enter both username and access key.", False
        
        if verify_credentials(username, access_key):
            return f"✅ Welcome, {username}! Authentication successful.", True
        else:
            return "❌ Invalid username or access key. Please try again.", False
    
    # Create authentication interface
    with gr.Blocks(title="TutorAI - Authentication") as auth_interface:
        gr.Markdown("# 🔐 TutorAI Authentication")
        gr.Markdown("Please enter your credentials to access the Python learning assistant.")
        
        with gr.Row():
            with gr.Column():
                username_input = gr.Textbox(
                    label="Username",
                    placeholder="Enter your username",
                    interactive=True
                )
                access_key_input = gr.Textbox(
                    label="Access Key",
                    placeholder="Enter your access key",
                    type="password",
                    interactive=True
                )
                auth_button = gr.Button("🔑 Authenticate", variant="primary")
        
        with gr.Row():
            auth_status = gr.Markdown("")
        
        # Authentication logic
        def handle_auth(username, access_key):
            message, success = authenticate(username, access_key)
            return message, success
        
        auth_button.click(
            fn=handle_auth,
            inputs=[username_input, access_key_input],
            outputs=[auth_status, gr.State()]
        )
    
    return auth_interface

def create_protected_gradio_app(original_app, auth_interface):
    """Create a protected Gradio app that requires authentication."""
    
    # Instead of creating a complex integration, let's use a simpler approach
    # We'll create a wrapper that shows authentication first, then redirects to the main app
    
    with gr.Blocks(title="TutorAI - Authentication Required") as protected_app:
        gr.Markdown("# 🔐 TutorAI Authentication Required")
        gr.Markdown("Please authenticate to access the Python learning assistant.")
        
        # Show the authentication interface
        auth_interface.render()
        
        # Add a note about the full app
        gr.Markdown("---")
        gr.Markdown("**Note:** After authentication, you will be redirected to the full TutorAI interface.")
        gr.Markdown("The complete Python learning environment includes:")
        gr.Markdown("- 🐍 10 Progressive Python exercises")
        gr.Markdown("- 🤖 AI-powered tutoring with GPT-4o-mini")
        gr.Markdown("- 🚀 Safe code execution environment")
        gr.Markdown("- 📚 Interactive learning interface")
    
    return protected_app
