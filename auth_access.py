#!/usr/bin/env python3
"""
Access Key Authentication module for TutorAI.
"""

import os
import secrets
import hashlib
import json
import time
import threading
from typing import Optional, Dict, Any
from flask import Flask, request, redirect, session, jsonify, render_template_string
import gradio as gr

class AccessKeyAuth:
    """Access Key authentication handler for Gradio apps."""
    
    def __init__(self):
        self.app = Flask(__name__)
        self.app.secret_key = secrets.token_hex(32)
        self.authenticated_users = {}  # In production, use a proper session store
        
    def create_auth_interface(self, gradio_app, auth_function, share=False):
        """Create authentication interface for Gradio app."""
        
        def check_auth():
            """Check if user is authenticated."""
            user_id = session.get('user_id')
            if user_id and user_id in self.authenticated_users:
                return True, self.authenticated_users[user_id]
            return False, None
        
        def login_redirect():
            """Show login page."""
            return redirect('/')
        
        def login_submit():
            """Handle login form submission."""
            username = request.form.get('username', '').strip()
            access_key = request.form.get('access_key', '').strip()
            
            if not username or not access_key:
                return "Please provide both username and access key.", 400
            
            # Use the provided authentication function
            if auth_function(username, access_key):
                # Store user session
                session['user_id'] = username
                self.authenticated_users[username] = {
                    'username': username,
                    'login_time': session.get('login_time', '')
                }
                session['login_time'] = str(time.time())
                
                # Redirect back to the main app
                return redirect('/')
            else:
                return "Invalid username or access key.", 401
        
        def logout():
            """Logout user."""
            user_id = session.get('user_id')
            if user_id:
                session.pop('user_id', None)
                self.authenticated_users.pop(user_id, None)
            return redirect('/')
        
        def auth_status():
            """Get authentication status."""
            is_auth, user_info = check_auth()
            if is_auth:
                return jsonify({
                    'authenticated': True,
                    'user': user_info
                })
            return jsonify({'authenticated': False})
        
        # Flask routes
        self.app.route('/auth/login', methods=['GET', 'POST'])(login_submit)
        self.app.route('/auth/logout')(logout)
        self.app.route('/auth/status')(auth_status)
        
        # Create login page
        login_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>TutorAI - Login</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    text-align: center; 
                    padding: 50px; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    min-height: 100vh;
                    margin: 0;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                .login-container { 
                    max-width: 400px; 
                    margin: 0 auto; 
                    background: rgba(255, 255, 255, 0.1);
                    padding: 40px;
                    border-radius: 20px;
                    backdrop-filter: blur(10px);
                    box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
                }
                .form-group {
                    margin-bottom: 20px;
                    text-align: left;
                }
                label {
                    display: block;
                    margin-bottom: 5px;
                    font-weight: bold;
                }
                input[type="text"], input[type="password"] {
                    width: 100%;
                    padding: 12px;
                    border: none;
                    border-radius: 8px;
                    background: rgba(255, 255, 255, 0.2);
                    color: white;
                    font-size: 16px;
                    box-sizing: border-box;
                }
                input[type="text"]::placeholder, input[type="password"]::placeholder {
                    color: rgba(255, 255, 255, 0.7);
                }
                .login-btn { 
                    background: #4285f4; 
                    color: white; 
                    padding: 15px 30px; 
                    border: none; 
                    border-radius: 8px; 
                    cursor: pointer; 
                    font-size: 16px;
                    font-weight: bold;
                    transition: all 0.3s ease;
                    box-shadow: 0 4px 15px rgba(66, 133, 244, 0.3);
                    width: 100%;
                }
                .login-btn:hover { 
                    background: #3367d6; 
                    transform: translateY(-2px);
                    box-shadow: 0 6px 20px rgba(66, 133, 244, 0.4);
                }
                h1 { margin-bottom: 20px; font-size: 2.5em; }
                p { margin-bottom: 30px; font-size: 1.1em; opacity: 0.9; }
                .error {
                    color: #ff6b6b;
                    background: rgba(255, 107, 107, 0.2);
                    padding: 10px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                }
            </style>
        </head>
        <body>
            <div class="login-container">
                <h1>🐍 TutorAI</h1>
                <p>Please enter your access credentials to continue.</p>
                
                <form method="POST" action="/auth/login">
                    <div class="form-group">
                        <label for="username">Username:</label>
                        <input type="text" id="username" name="username" placeholder="Enter your username" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="access_key">Access Key:</label>
                        <input type="password" id="access_key" name="access_key" placeholder="Enter your access key" required>
                    </div>
                    
                    <button type="submit" class="login-btn">Sign In</button>
                </form>
                
                <p style="margin-top: 20px; font-size: 0.9em; opacity: 0.7;">
                    Contact your administrator for access credentials.
                </p>
            </div>
        </body>
        </html>
        """
        
        @self.app.route('/')
        def index():
            is_auth, user_info = check_auth()
            if is_auth:
                # User is authenticated, show success page with link to Gradio
                success_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>TutorAI - Authenticated</title>
                    <style>
                        body {{ 
                            font-family: Arial, sans-serif; 
                            text-align: center; 
                            padding: 50px; 
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            color: white;
                            min-height: 100vh;
                            margin: 0;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                        }}
                        .success-container {{ 
                            max-width: 500px; 
                            margin: 0 auto; 
                            background: rgba(255, 255, 255, 0.1);
                            padding: 40px;
                            border-radius: 20px;
                            backdrop-filter: blur(10px);
                            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
                        }}
                        .gradio-btn {{ 
                            background: #4285f4; 
                            color: white; 
                            padding: 15px 30px; 
                            border: none; 
                            border-radius: 8px; 
                            cursor: pointer; 
                            text-decoration: none;
                            display: inline-block;
                            font-size: 16px;
                            font-weight: bold;
                            transition: all 0.3s ease;
                            box-shadow: 0 4px 15px rgba(66, 133, 244, 0.3);
                            margin: 10px;
                        }}
                        .gradio-btn:hover {{ 
                            background: #3367d6; 
                            transform: translateY(-2px);
                            box-shadow: 0 6px 20px rgba(66, 133, 244, 0.4);
                        }}
                        h1 {{ margin-bottom: 20px; font-size: 2.5em; }}
                        p {{ margin-bottom: 30px; font-size: 1.1em; opacity: 0.9; }}
                    </style>
                </head>
                <body>
                    <div class="success-container">
                        <h1>🐍 TutorAI</h1>
                        <p>Welcome, {user_info.get('username', 'User')}! You are now authenticated.</p>
                        <p>Click the button below to access the Python learning interface:</p>
                        <a href="/gradio" class="gradio-btn">🚀 Launch TutorAI</a>
                        <br><br>
                        <a href="/auth/logout" class="gradio-btn" style="background: #dc3545;">🚪 Logout</a>
                    </div>
                </body>
                </html>
                """
                return success_html
            else:
                # Show login page
                return login_html
        
        @self.app.route('/gradio')
        def gradio_interface():
            is_auth, user_info = check_auth()
            if is_auth:
                # User is authenticated, show Gradio app
                return gradio_app
            else:
                # Not authenticated, redirect to login
                return redirect('/')
        
        # If share is enabled, we need to handle Gradio sharing differently
        if share:
            print("🔗 Public sharing enabled - but authentication prevents direct Gradio sharing")
            print("📝 Consider using a reverse proxy or deploying to a platform that supports both")
        
        return self.app

def create_access_key_app(gradio_app, auth_function, share=False):
    """Create access key authentication Flask app wrapping Gradio."""
    access_auth = AccessKeyAuth()
    return access_auth.create_auth_interface(gradio_app, auth_function, share)
