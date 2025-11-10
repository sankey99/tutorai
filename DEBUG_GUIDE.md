# Debugging Guide for TutorAI

## Quick Start

### Command Line Debugging

1. **Start the app with debugger:**
   ```bash
   source venv/bin/activate
   python src/app.py --debugger breakpoint --auth
   ```

2. **Try to authenticate** - the debugger will pause at the breakpoint

3. **Inspect the request object:**
   ```python
   (Pdb) request
   (Pdb) type(request)
   (Pdb) dir(request)
   (Pdb) request.headers  # Check if headers exist
   (Pdb) request.scope     # Check FastAPI scope
   (Pdb) hasattr(request, 'headers')
   ```

4. **Continue execution:**
   ```python
   (Pdb) c  # or 'continue'
   ```

### VS Code Debugging

1. **Set breakpoints** by clicking to the left of line numbers
2. **Press F5** or go to Run > Start Debugging
3. **Select "Python: TutorAI (with auth)"**
4. **Try to authenticate** - execution will pause at breakpoints
5. **Inspect variables** in the Debug panel

## Breakpoint Locations

### 1. Authentication Function (`src/app.py` line ~432)
- Triggers when user tries to authenticate
- Inspect: `request`, `username`, `password`

### 2. Header Extraction (`src/logger.py` line ~295)
- Triggers when extracting headers from request
- Inspect: `request`, `request.headers`, `request.scope`

## Common Debugger Commands

| Command | Description |
|---------|-------------|
| `c` or `continue` | Continue execution |
| `n` or `next` | Execute next line |
| `s` or `step` | Step into function |
| `l` or `list` | Show current code |
| `p variable` | Print variable |
| `pp variable` | Pretty print variable |
| `q` or `quit` | Quit debugger |
| `h` or `help` | Show help |

## What to Inspect

When debugging the request object, check:

1. **Request Type:**
   ```python
   type(request)
   ```

2. **Available Attributes:**
   ```python
   dir(request)
   ```

3. **Headers:**
   ```python
   request.headers
   hasattr(request, 'headers')
   ```

4. **FastAPI Scope:**
   ```python
   request.scope
   request.scope.get('headers') if hasattr(request, 'scope') else None
   ```

5. **Client Info:**
   ```python
   request.client if hasattr(request, 'client') else None
   ```

## Example Debug Session

```
🔍 DEBUG: gradio_auth called with username=boss
🔍 DEBUG: request type: <class 'gradio.Request'>
> src/app.py(432)gradio_auth()
-> breakpoint()
(Pdb) request
<gradio.Request object at 0x...>
(Pdb) type(request)
<class 'gradio.Request'>
(Pdb) dir(request)
['client', 'headers', 'scope', ...]
(Pdb) request.headers
<Headers object>
(Pdb) list(request.headers.items())
[('host', 'localhost:7777'), ('user-agent', '...'), ...]
(Pdb) c
```

## Troubleshooting

- **If breakpoint doesn't trigger:** Make sure you're using `--debugger breakpoint` flag
- **If request is None:** Check if Gradio is passing the request parameter
- **If headers are empty:** Inspect `request.scope` for FastAPI internal headers

