#!/usr/bin/env python3
"""
Logging module for TutorAI
Handles all logging-related functionality including access logs and application logs.
"""

import os
import logging
import httpx


# Cache for user-specific loggers
_user_loggers = {}


def setup_logging():
    """Setup logging for access and application logs."""
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Setup access logger
    access_logger = logging.getLogger('access')
    access_logger.setLevel(logging.INFO)
    access_handler = logging.FileHandler('logs/access.log')
    access_formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    access_handler.setFormatter(access_formatter)
    access_logger.addHandler(access_handler)
    
    # Setup default application logger (for cases without username)
    app_logger = logging.getLogger('app')
    app_logger.setLevel(logging.INFO)
    app_handler = logging.FileHandler('logs/app.log')
    app_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    app_handler.setFormatter(app_formatter)
    app_logger.addHandler(app_handler)
    
    return access_logger, app_logger




def get_user_logger(username=None):
    """Get or create a logger for a specific user.
    
    Args:
        username: Username to get logger for (None for default app logger)
        
    Returns:
        logging.Logger: Logger instance for the user
    """
    if username is None or username == '':
        # Return default app logger
        return logging.getLogger('app')
    
    # Sanitize username for filename (remove invalid characters)
    safe_username = "".join(c for c in username if c.isalnum() or c in ('_', '-')).strip()
    if not safe_username:
        return logging.getLogger('app')
    
    # Check if logger already exists in cache
    if safe_username in _user_loggers:
        return _user_loggers[safe_username]
    
    # Create new logger for this user
    logger_name = f'app_{safe_username}'
    user_logger = logging.getLogger(logger_name)
    user_logger.setLevel(logging.INFO)
    
    # Create file handler for user-specific log file
    log_file = f'logs/app_{safe_username}.log'
    user_handler = logging.FileHandler(log_file)
    user_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    user_handler.setFormatter(user_formatter)
    user_logger.addHandler(user_handler)
    
    # Prevent duplicate handlers if logger already exists
    user_logger.propagate = False
    
    # Cache the logger
    _user_loggers[safe_username] = user_logger
    
    return user_logger


def get_client_ip_from_request(request=None):
    """Get client IP address from request headers.
    
    Args:
        request: Gradio/FastAPI Request object
        
    Returns:
        str: Client IP address or 'unknown' if not available
    """
    if request is None:
        return 'unknown'
    
    try:
        # Method 1: Check request.scope (FastAPI internal - most reliable)
        # FastAPI stores client info in request.scope['client'] as (host, port) tuple
        if hasattr(request, 'scope'):
            scope = request.scope
            if isinstance(scope, dict):
                # Get client from scope
                if 'client' in scope and scope['client']:
                    client_info = scope['client']
                    if isinstance(client_info, (list, tuple)) and len(client_info) > 0:
                        ip = str(client_info[0])
                        # Only return if it's not localhost
                        if ip and ip not in ('127.0.0.1', 'localhost', '::1', '0.0.0.0', 'unknown'):
                            return ip
                
                # Check headers in scope (raw headers are list of (b'key', b'value') tuples)
                if 'headers' in scope:
                    scope_headers = scope['headers']
                    if isinstance(scope_headers, list):
                        for header_tuple in scope_headers:
                            if len(header_tuple) == 2:
                                key = header_tuple[0]
                                value = header_tuple[1]
                                # Decode bytes if needed
                                if isinstance(key, bytes):
                                    key = key.decode('utf-8', errors='ignore').lower()
                                if isinstance(value, bytes):
                                    value = value.decode('utf-8', errors='ignore')
                                
                                if key in ('x-forwarded-for', 'x-real-ip', 'x-client-ip', 'cf-connecting-ip'):
                                    ip = str(value).split(',')[0].strip()
                                    if ip and ip not in ('unknown', '127.0.0.1', 'localhost', '::1', '0.0.0.0'):
                                        return ip
        
        # Method 2: Check request.header (Gradio uses singular 'header')
        if hasattr(request, 'header'):
            headers = request.header
            
            # Try as dict
            if isinstance(headers, dict):
                for header_name in ['X-Forwarded-For', 'x-forwarded-for', 'X-Real-IP', 'x-real-ip', 'X-Client-IP', 'x-client-ip', 'CF-Connecting-IP', 'cf-connecting-ip']:
                    if header_name in headers:
                        value = headers[header_name]
                        if value:
                            ip = str(value).split(',')[0].strip()
                            if ip and ip not in ('unknown', '127.0.0.1', 'localhost', '::1', '0.0.0.0'):
                                return ip
            
            # Try get method
            if hasattr(headers, 'get'):
                for header_name in ['X-Forwarded-For', 'x-forwarded-for', 'X-Real-IP', 'x-real-ip', 'X-Client-IP', 'x-client-ip', 'CF-Connecting-IP', 'cf-connecting-ip']:
                    value = headers.get(header_name)
                    if value:
                        ip = str(value).split(',')[0].strip()
                        if ip and ip not in ('unknown', '127.0.0.1', 'localhost', '::1', '0.0.0.0'):
                            return ip
            
            # Try items() method
            if hasattr(headers, 'items'):
                for key, value in headers.items():
                    if isinstance(key, str) and key.lower() in ('x-forwarded-for', 'x-real-ip', 'x-client-ip', 'cf-connecting-ip'):
                        ip = str(value).split(',')[0].strip()
                        if ip and ip not in ('unknown', '127.0.0.1', 'localhost', '::1', '0.0.0.0'):
                            return ip
        
        # Method 3: Check request.headers (standard FastAPI - plural)
        if hasattr(request, 'headers'):
            headers = request.headers
            
            # Try as dict
            if isinstance(headers, dict):
                for header_name in ['X-Forwarded-For', 'x-forwarded-for', 'X-Real-IP', 'x-real-ip', 'X-Client-IP', 'x-client-ip', 'CF-Connecting-IP', 'cf-connecting-ip']:
                    if header_name in headers:
                        value = headers[header_name]
                        if value:
                            ip = str(value).split(',')[0].strip()
                            if ip and ip not in ('unknown', '127.0.0.1', 'localhost', '::1', '0.0.0.0'):
                                return ip
            
            # Try get method
            if hasattr(headers, 'get'):
                for header_name in ['X-Forwarded-For', 'x-forwarded-for', 'X-Real-IP', 'x-real-ip', 'X-Client-IP', 'x-client-ip', 'CF-Connecting-IP', 'cf-connecting-ip']:
                    value = headers.get(header_name)
                    if value:
                        ip = str(value).split(',')[0].strip()
                        if ip and ip not in ('unknown', '127.0.0.1', 'localhost', '::1', '0.0.0.0'):
                            return ip
            
            # Try items() method
            if hasattr(headers, 'items'):
                for key, value in headers.items():
                    if isinstance(key, str) and key.lower() in ('x-forwarded-for', 'x-real-ip', 'x-client-ip', 'cf-connecting-ip'):
                        ip = str(value).split(',')[0].strip()
                        if ip and ip not in ('unknown', '127.0.0.1', 'localhost', '::1', '0.0.0.0'):
                            return ip
        
        # Method 3: Check request.client.host (FastAPI/Gradio standard)
        if hasattr(request, 'client') and request.client:
            if hasattr(request.client, 'host'):
                client_host = request.client.host
                if client_host:
                    ip = str(client_host).strip()
                    # Only return if it's not localhost
                    if ip and ip not in ('127.0.0.1', 'localhost', '::1', '0.0.0.0', 'unknown'):
                        return ip
        
        # Method 4: Try to get from request.url if available (for some Gradio contexts)
        if hasattr(request, 'url'):
            # This won't give us the client IP, but worth checking
            pass
        
        # Method 5: Check if request has a _get_client_ip method or similar
        if hasattr(request, '_get_client_ip'):
            try:
                ip = request._get_client_ip()
                if ip and ip not in ('unknown', '127.0.0.1', 'localhost', '::1', '0.0.0.0'):
                    return ip
            except:
                pass
        
        # Method 6: Try accessing request.state if it exists (some frameworks store IP here)
        if hasattr(request, 'state'):
            state = request.state
            if hasattr(state, 'client_ip'):
                ip = str(state.client_ip)
                if ip and ip not in ('unknown', '127.0.0.1', 'localhost', '::1', '0.0.0.0'):
                    return ip
        
        # Method 7: For Gradio, try to access the underlying FastAPI request
        # Gradio wraps FastAPI, so we might need to access it differently
        if hasattr(request, '_fastapi_request'):
            fastapi_request = request._fastapi_request
            if fastapi_request:
                # Recursively try to get IP from the underlying request
                ip = get_client_ip_from_request(fastapi_request)
                if ip != 'unknown':
                    return ip
        
        # Method 8: Try accessing request.base_url or request.url for host info
        # (This won't give client IP but might help in some edge cases)
        if hasattr(request, 'base_url'):
            base_url = str(request.base_url)
            # Extract host from URL if it's not localhost
            if '://' in base_url:
                host = base_url.split('://')[1].split('/')[0].split(':')[0]
                if host and host not in ('127.0.0.1', 'localhost', '::1', '0.0.0.0', 'unknown'):
                    # This is the server host, not client IP, so skip it
                    pass
    except Exception as e:
        # Silently fail and return unknown
        pass
    
    return 'unknown'


def get_browser_location_from_ip(ip):
    """Get browser location from IP address (client-side location)."""
    if ip == 'unknown':
        return 'Unknown Location'
    
    # Check for localhost/loopback addresses
    if ip.startswith('127.') or ip == 'localhost' or ip == '::1':
        return 'Local Network'
    
    # Check for private network ranges (but still try to look them up if they're the only IP we have)
    is_private = (ip.startswith('192.168.') or 
                  ip.startswith('10.') or 
                  ip.startswith('172.16.') or
                  ip.startswith('172.17.') or
                  ip.startswith('172.18.') or
                  ip.startswith('172.19.') or
                  ip.startswith('172.20.') or
                  ip.startswith('172.21.') or
                  ip.startswith('172.22.') or
                  ip.startswith('172.23.') or
                  ip.startswith('172.24.') or
                  ip.startswith('172.25.') or
                  ip.startswith('172.26.') or
                  ip.startswith('172.27.') or
                  ip.startswith('172.28.') or
                  ip.startswith('172.29.') or
                  ip.startswith('172.30.') or
                  ip.startswith('172.31.'))
    
    # Try to look up location even for private IPs (in case it's actually a public IP)
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(f'http://ip-api.com/json/{ip}')
            data = response.json()
            if data.get('status') == 'success':
                location = f"{data.get('city', '')}, {data.get('regionName', '')}, {data.get('country', '')}".strip(', ')
                if location:
                    return location
        
        # If lookup failed and it's a private IP, return Local Network
        if is_private:
            return 'Local Network'
        
        # If lookup failed and it's not private, return Unknown
        return 'Unknown Location'
    except Exception as e:
        # If lookup fails, check if it's a private IP
        if is_private:
            return 'Local Network'
        return 'Unknown Location'


def _extract_all_headers(request, enable_debugger=False):
    """Extract all headers from a request object.
    
    Args:
        request: Request object (Gradio/FastAPI)
        enable_debugger: If True, set breakpoint for debugging
        
    Returns:
        dict: Dictionary of all headers, or empty dict if not available
    """
    headers_dict = {}
    
    if request is None:
        return headers_dict
    
    # DEBUG: Breakpoint to inspect request object
    if enable_debugger:
        print(f"🔍 DEBUG: _extract_all_headers called")
        print(f"🔍 DEBUG: request type: {type(request)}")
        if hasattr(request, 'header'):
            print(f"🔍 DEBUG: request.header: {request.header}")
        if hasattr(request, 'headers'):
            print(f"🔍 DEBUG: request.headers: {request.headers}")
        if hasattr(request, 'scope'):
            print(f"🔍 DEBUG: request.scope: {request.scope}")
        breakpoint()  # Python 3.7+ built-in breakpoint
    
    try:
        # Debug: Log request type and attributes
        request_type = type(request).__name__
        request_attrs = [attr for attr in dir(request) if not attr.startswith('_')]
        
        # Method 1: Check request.scope for headers (FastAPI internal)
        if hasattr(request, 'scope'):
            scope = request.scope
            if isinstance(scope, dict) and 'headers' in scope:
                scope_headers = scope['headers']
                if isinstance(scope_headers, list):
                    for header_tuple in scope_headers:
                        if len(header_tuple) == 2:
                            key = header_tuple[0]
                            value = header_tuple[1]
                            # Decode bytes if needed
                            if isinstance(key, bytes):
                                key = key.decode('utf-8', errors='ignore')
                            if isinstance(value, bytes):
                                value = value.decode('utf-8', errors='ignore')
                            headers_dict[key] = value
        
        # Method 2: Check request.header (Gradio uses singular 'header')
        if hasattr(request, 'header'):
            headers = request.header
            
            # Try as dict
            if isinstance(headers, dict):
                headers_dict.update(headers)
            
            # Try get method
            elif hasattr(headers, 'get'):
                # Try to get all headers by iterating
                if hasattr(headers, 'items'):
                    for key, value in headers.items():
                        headers_dict[str(key)] = str(value)
                elif hasattr(headers, 'keys'):
                    for key in headers.keys():
                        value = headers.get(key)
                        if value:
                            headers_dict[str(key)] = str(value)
            
            # Try items() method
            elif hasattr(headers, 'items'):
                for key, value in headers.items():
                    headers_dict[str(key)] = str(value)
        
        # Method 3: Check request.headers (standard FastAPI - plural)
        if hasattr(request, 'headers'):
            headers = request.headers
            
            # Try as dict
            if isinstance(headers, dict):
                headers_dict.update(headers)
            
            # Try get method
            elif hasattr(headers, 'get'):
                # Try to get all headers by iterating
                if hasattr(headers, 'items'):
                    for key, value in headers.items():
                        headers_dict[str(key)] = str(value)
                elif hasattr(headers, 'keys'):
                    for key in headers.keys():
                        value = headers.get(key)
                        if value:
                            headers_dict[str(key)] = str(value)
            
            # Try items() method
            elif hasattr(headers, 'items'):
                for key, value in headers.items():
                    headers_dict[str(key)] = str(value)
        
        # Method 4: Try accessing headers via getattr (some wrappers)
        if not headers_dict:
            # Try common header access patterns
            for attr_name in ['header', 'headers', 'request_headers', 'http_headers']:
                if hasattr(request, attr_name):
                    try:
                        attr_value = getattr(request, attr_name)
                        if attr_value and isinstance(attr_value, (dict, list)):
                            if isinstance(attr_value, dict):
                                headers_dict.update(attr_value)
                            break
                    except:
                        pass
        
        # Debug: If still no headers, log what we found
        if not headers_dict:
            # Log debug info to help diagnose
            debug_info = f"Request type: {request_type}, Has scope: {hasattr(request, 'scope')}, Has header: {hasattr(request, 'header')}, Has headers: {hasattr(request, 'headers')}"
            if hasattr(request, 'header'):
                debug_info += f", Header type: {type(request.header).__name__}"
            if hasattr(request, 'headers'):
                debug_info += f", Headers type: {type(request.headers).__name__}"
            # Store debug info in headers_dict as a special key
            headers_dict['_debug'] = debug_info
    except Exception as e:
        # If extraction fails, log the error
        headers_dict['_error'] = f"Exception extracting headers: {str(e)}"
    
    return headers_dict


def _get_username_from_request(request):
    """Extract username from request object.
    
    Args:
        request: Request object (Gradio/FastAPI)
        
    Returns:
        str: Username if available, 'unknown' otherwise
    """
    if request is None:
        return 'unknown'
    
    try:
        # Gradio sets request.username after authentication
        if hasattr(request, 'username') and request.username:
            return str(request.username)
    except Exception:
        pass
    
    return 'unknown'


def log_access(access_logger, event_type, details, ip=None, location=None, request=None, username=None, enable_debugger=False):
    """Log access events with browser location and all request headers.
    
    Args:
        access_logger: Logger instance
        event_type: Type of event (e.g., 'AUTH_SUCCESS', 'AUTH_FAILED')
        details: Event details
        ip: Client IP address (optional, will try to get from request if not provided)
        location: Client location (optional, will be determined from IP if not provided)
        request: Request object to extract client IP from headers (optional)
        username: Username (optional, will try to get from request if not provided)
        enable_debugger: If True, enable debugger breakpoints
    """
    if ip is None:
        # Try to get IP from request only - do not fallback to server IP
        ip = get_client_ip_from_request(request)
    
    if location is None:
        # Get browser location from the IP
        location = get_browser_location_from_ip(ip)
    
    # Get username from request if not provided
    if username is None:
        username = _get_username_from_request(request)
    
    # Extract all headers from request
    headers_dict = _extract_all_headers(request, enable_debugger=enable_debugger)
    
    # Format headers as a string
    if headers_dict:
        # Filter out debug/error keys for cleaner output, but include them if no real headers
        real_headers = {k: v for k, v in headers_dict.items() if not k.startswith('_')}
        if real_headers:
            headers_str = " | ".join([f"{k}: {v}" for k, v in real_headers.items()])
            log_entry = f"Username: {username} | IP: {ip} | Browser Location: {location} | Event: {event_type} | Details: {details} | Headers: {headers_str}"
        else:
            # Only debug/error info available
            debug_info = headers_dict.get('_debug', headers_dict.get('_error', 'No headers found'))
            log_entry = f"Username: {username} | IP: {ip} | Browser Location: {location} | Event: {event_type} | Details: {details} | Headers: {debug_info}"
    else:
        log_entry = f"Username: {username} | IP: {ip} | Browser Location: {location} | Event: {event_type} | Details: {details} | Headers: (none)"
    
    access_logger.info(log_entry)


def log_app_event(app_logger, level, message, details=None, request=None, username=None):
    """Log application events to user-specific log file if username is available.
    
    Args:
        app_logger: Default logger instance (used as fallback)
        level: Log level ('INFO', 'WARNING', 'ERROR', 'DEBUG')
        message: Log message
        details: Optional details to append
        request: Request object (kept for compatibility, not used for username)
        username: Username to use for log file (should be passed from gr.State)
    """
    # Get appropriate logger (user-specific or default)
    logger = get_user_logger(username) if username else app_logger
    
    if details:
        full_message = f"{message} | Details: {details}"
    else:
        full_message = message
    
    if level == 'INFO':
        logger.info(full_message)
    elif level == 'WARNING':
        logger.warning(full_message)
    elif level == 'ERROR':
        logger.error(full_message)
    elif level == 'DEBUG':
        logger.debug(full_message)

