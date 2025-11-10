#!/usr/bin/env python3
"""
Authentication module for TutorAI
Handles user authentication and access key validation.
"""

import os
import json
import hashlib
from logger import log_access




def access_key_auth(username: str, access_key: str, access_logger, request=None, enable_debugger=False) -> bool:
    """Check if user exists in USERS env variable and access key matches ACCESS_KEYS.
    The access key is hashed with SHA256 before comparison.
    
    Args:
        username: Username to authenticate
        access_key: Access key to verify
        access_logger: Logger instance for access logging
        request: Gradio Request object (optional) to get client IP and store username
    
    Returns:
        bool: True if authentication succeeds, False otherwise
    """
    try:
        # Get users and access keys from environment variables
        users_json = os.getenv('USERS', '[]')
        access_keys_json = os.getenv('ACCESS_KEYS', '[]')
        
        # Parse JSON lists
        users = json.loads(users_json)
        access_keys = json.loads(access_keys_json)
        
        # Check if username exists in users list
        if username not in users:
            log_access(access_logger, 'AUTH_FAILED', f'Username not found: {username}', request=request, username=username, enable_debugger=enable_debugger)
            return False
        
        # Get user index to match with access key
        user_index = users.index(username)
        
        # Check if access key matches (with same index)
        if user_index < len(access_keys):
            stored_key = access_keys[user_index]
            
            # Hash the access key with SHA256 before comparing
            hashed_access_key = hashlib.sha256(access_key.encode()).hexdigest()
            if hashed_access_key.lower() == stored_key.lower():
                log_access(access_logger, 'AUTH_SUCCESS', f'User authenticated: {username}', request=request, username=username, enable_debugger=enable_debugger)
                return True
            else:
                log_access(access_logger, 'AUTH_FAILED', f'Invalid access key for user: {username}', request=request, username=username, enable_debugger=enable_debugger)
                return False
        
        log_access(access_logger, 'AUTH_FAILED', f'No access key found for user: {username}', request=request, username=username, enable_debugger=enable_debugger)
        return False
        
    except (json.JSONDecodeError, ValueError, IndexError) as e:
        log_access(access_logger, 'AUTH_ERROR', f'Authentication error: {str(e)}', request=request, username=username if 'username' in locals() else None, enable_debugger=enable_debugger)
        return False