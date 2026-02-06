"""Input validation and sanitization utilities."""

import html
import re


def sanitize_for_prompt(text: str) -> str:
    """Sanitize user input for use in LLM prompts.
    
    Prevents prompt injection attacks by:
    - Escaping HTML entities
    - Removing control characters
    - Limiting length
    - Removing prompt injection markers
    
    Args:
        text: Raw user input
        
    Returns:
        Sanitized text safe for prompts
    """
    if not text:
        return ""
    
    # Limit length
    max_length = 10000
    text = text[:max_length]
    
    # Escape HTML entities
    text = html.escape(text)
    
    # Remove null bytes and control characters (except common whitespace)
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    
    # Remove potential prompt injection markers
    # These patterns try to override system prompts
    injection_patterns = [
        r'ignore previous instructions',
        r'ignore all previous',
        r'system prompt',
        r'you are now',
        r'you will now',
        r'act as',
        r'pretend to be',
        r'new instructions',
        r'override',
        r'<system>',
        r'</system>',
        r'```system',
        r'```user',
        r'```assistant',
    ]
    
    text_lower = text.lower()
    for pattern in injection_patterns:
        if re.search(pattern, text_lower):
            # Replace with safe alternative
            text = re.sub(pattern, '[REDACTED]', text, flags=re.IGNORECASE)
    
    return text


def validate_code_input(code: str, max_lines: int = 1000) -> tuple[bool, str]:
    """Validate code input for security.
    
    Args:
        code: Code to validate
        max_lines: Maximum allowed lines
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not code:
        return False, "Code cannot be empty"
    
    lines = code.split('\n')
    if len(lines) > max_lines:
        return False, f"Code exceeds maximum of {max_lines} lines"
    
    # Check for dangerous patterns
    dangerous_patterns = [
        (r'eval\s*\(', "Use of eval() is dangerous"),
        (r'exec\s*\(', "Use of exec() is dangerous"),
        (r'__import__\s*\(', "Dynamic imports are dangerous"),
        (r'subprocess\.call\s*\([^)]*shell\s*=\s*True', "Shell=True is dangerous"),
        (r'os\.system\s*\(', "os.system() is dangerous"),
    ]
    
    for pattern, message in dangerous_patterns:
        if re.search(pattern, code):
            return False, message
    
    return True, ""


def validate_api_key(key: str | None) -> bool:
    """Validate API key format.
    
    Args:
        key: API key to validate
        
    Returns:
        True if key appears valid
    """
    if not key:
        return False
    
    # Basic validation - must be non-empty string with reasonable length
    if not isinstance(key, str):
        return False
    
    if len(key) < 10 or len(key) > 500:
        return False
    
    # Should not contain whitespace
    if any(c.isspace() for c in key):
        return False
    
    return True


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename to prevent path traversal.
    
    Args:
        filename: Input filename
        
    Returns:
        Sanitized filename
    """
    if not filename:
        return "unnamed"
    
    # Remove path components
    filename = filename.replace('..', '_')
    filename = filename.replace('/', '_')
    filename = filename.replace('\\', '_')
    
    # Remove null bytes
    filename = filename.replace('\x00', '')
    
    # Limit length
    max_len = 255
    if len(filename) > max_len:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:max_len - len(ext) - 1] + '.' + ext if ext else name[:max_len]
    
    return filename or "unnamed"
