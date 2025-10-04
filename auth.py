#!/usr/bin/env python3
"""
Authentication module for TutorAI using Google OAuth.
"""

import os
import secrets
import base64
from urllib.parse import urlencode, parse_qs, urlparse
from typing import Optional, Dict, Any
import requests
from authlib.integrations.flask_client import OAuth
from flask import Flask, request, redirect, session, jsonify, render_template_string
import gradio as gr

class GoogleOAuth:
    """Google OAuth authentication handler for Gradio apps."""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.authorization_base_url = 'https://accounts.google.com/o/oauth2/v2/auth'
        self.token_url = 'https://oauth2.googleapis.com/token'
        self.userinfo_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
        
    def get_authorization_url(self, state: str = None) -> str:
        """Generate authorization URL."""
        if not state:
            state = secrets.token_urlsafe(32)
            
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'openid email profile',
            'response_type': 'code',
            'state': state,
            'access_type': 'offline',
            'prompt': 'consent'
        }
        
        return f"{self.authorization_base_url}?{urlencode(params)}"
    
    def exchange_code_for_token(self, code: str, state: str = None) -> Dict[str, Any]:
        """Exchange authorization code for access token."""
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri
        }
        
        response = requests.post(self.token_url, data=data)
        response.raise_for_status()
        return response.json()
    
    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from Google."""
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(self.userinfo_url, headers=headers)
        response.raise_for_status()
        return response.json()

class GradioOAuth:
    """OAuth integration for Gradio applications."""
    
    def __init__(self, oauth: GoogleOAuth):
        self.oauth = oauth
        self.app = Flask(__name__)
        self.app.secret_key = secrets.token_hex(32)
        self.authenticated_users = {}  # In production, use a proper session store
        self.gradio_app = None
        
    def create_auth_interface(self, gradio_app, share=False):
        """Create authentication interface for Gradio app."""
        
        def check_auth():
            """Check if user is authenticated."""
            user_id = session.get('user_id')
            if user_id and user_id in self.authenticated_users:
                return True, self.authenticated_users[user_id]
            return False, None
        
        def login_redirect():
            """Redirect to Google OAuth."""
            auth_url = self.oauth.get_authorization_url()
            return redirect(auth_url)
        
        def oauth_callback():
            """Handle OAuth callback."""
            code = request.args.get('code')
            state = request.args.get('state')
            
            if not code:
                return "Authentication failed. No authorization code received.", 400
            
            try:
                # Exchange code for token
                token_data = self.oauth.exchange_code_for_token(code, state)
                access_token = token_data['access_token']
                
                # Get user info
                user_info = self.oauth.get_user_info(access_token)
                
                # Store user session
                user_id = user_info['id']
                session['user_id'] = user_id
                self.authenticated_users[user_id] = {
                    'name': user_info.get('name', 'User'),
                    'email': user_info.get('email', ''),
                    'picture': user_info.get('picture', ''),
                    'access_token': access_token
                }
                
                # Redirect back to Gradio app
                return redirect('/')
                
            except Exception as e:
                return f"Authentication failed: {str(e)}", 400
        
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
        self.app.route('/auth/login')(login_redirect)
        self.app.route('/auth/callback')(oauth_callback)
        self.app.route('/auth/logout')(logout)
        self.app.route('/auth/status')(auth_status)
        
        # Create login page
        login_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>TutorAI - Login</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                .login-container { max-width: 400px; margin: 0 auto; }
                .google-btn { 
                    background: #4285f4; color: white; padding: 12px 24px; 
                    border: none; border-radius: 4px; cursor: pointer; 
                    text-decoration: none; display: inline-block;
                }
                .google-btn:hover { background: #3367d6; }
            </style>
        </head>
        <body>
            <div class="login-container">
                <h1>🐍 TutorAI</h1>
                <p>Please sign in with your Google account to access the Python learning assistant.</p>
                <a href="/auth/login" class="google-btn">Sign in with Google</a>
            </div>
        </body>
        </html>
        """
        
        @self.app.route('/')
        def index():
            is_auth, user_info = check_auth()
            if is_auth:
                # User is authenticated, show Gradio app
                return gradio_app
            else:
                # Show login page
                return login_html
        
        # If share is enabled, we need to handle Gradio sharing differently
        if share:
            print("🔗 Public sharing enabled - but authentication prevents direct Gradio sharing")
            print("📝 Consider using a reverse proxy or deploying to a platform that supports both")
        
        return self.app

def create_oauth_app(gradio_app, client_id: str, client_secret: str, redirect_uri: str, share=False):
    """Create OAuth-enabled Flask app wrapping Gradio."""
    oauth = GoogleOAuth(client_id, client_secret, redirect_uri)
    gradio_oauth = GradioOAuth(oauth)
    return gradio_oauth.create_auth_interface(gradio_app, share)
