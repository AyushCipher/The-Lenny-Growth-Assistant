import re
import bleach

# Allowed HTML tags for rendered artifacts
ALLOWED_TAGS = [
    "html", "head", "body", "meta", "title", "style",
    "div", "span", "p", "h1", "h2", "h3", "h4", "h5", "h6",
    "ul", "ol", "li", "table", "thead", "tbody", "tr", "th", "td",
    "button", "input", "label", "select", "option", "textarea", "form",
    "canvas", "svg", "path", "circle", "rect", "line", "polyline", "polygon", "text", "g",
    "b", "strong", "i", "em", "u", "s", "blockquote", "code", "pre", "hr", "br",
    "header", "footer", "nav", "section", "article", "aside", "main",
    "script"  # Allowed for local calculations/canvas, but stripped of dangerous src and sandboxed
]

ALLOWED_ATTRIBUTES = {
    "*": ["class", "id", "style", "title", "aria-*", "role", "data-*"],
    "meta": ["charset", "name", "content", "http-equiv"],
    "input": ["type", "value", "placeholder", "min", "max", "step", "id", "name", "checked", "disabled"],
    "button": ["type", "id", "name", "disabled"],
    "select": ["id", "name", "multiple", "disabled"],
    "option": ["value", "selected"],
    "textarea": ["rows", "cols", "placeholder", "id", "name"],
    "canvas": ["width", "height", "id"],
    "svg": ["width", "height", "viewBox", "xmlns", "fill", "stroke"],
    "path": ["d", "fill", "stroke", "stroke-width"],
    "circle": ["cx", "cy", "r", "fill", "stroke"],
    "rect": ["x", "y", "width", "height", "rx", "ry", "fill", "stroke"],
    "line": ["x1", "y1", "x2", "y2", "stroke", "stroke-width"],
    "text": ["x", "y", "font-size", "fill", "text-anchor"],
    "a": ["href", "title", "target"],
}

ALLOWED_PROTOCOLS = ["http", "https", "mailto", "data"]

# Strict Content Security Policy injected into untrusted HTML
CSP_META_TAG = (
    '<meta http-equiv="Content-Security-Policy" content="'
    "default-src 'none'; "
    "style-src 'unsafe-inline'; "
    "script-src 'unsafe-inline'; "
    "img-src 'self' data:; "
    "connect-src 'none'; "
    "frame-src 'none'; "
    "font-src 'none'; "
    '">'
)


def sanitize_html(raw_html: str) -> str:
    if not raw_html:
        return ""

    # 1. Clean script tags with dangerous external src or attributes
    cleaned_html = re.sub(
        r'<script\b[^>]*\bsrc\s*=\s*["\'][^"\']*["\'][^>]*>.*?</script>',
        '<!-- external script blocked -->',
        raw_html,
        flags=re.IGNORECASE | re.DOTALL
    )

    # 2. Strip inline event handlers (onerror, onload, onclick, onmouseover, etc.)
    cleaned_html = re.sub(
        r'\son[a-zA-Z]+\s*=\s*["\'][^"\']*["\']',
        '',
        cleaned_html,
        flags=re.IGNORECASE
    )

    # 3. Strip javascript: URIs in href or src
    cleaned_html = re.sub(
        r'(href|src)\s*=\s*["\']javascript:[^"\']*["\']',
        r'\1="#"',
        cleaned_html,
        flags=re.IGNORECASE
    )

    # 4. Strip dangerous window.parent, window.top, localStorage, document.cookie references in script bodies
    cleaned_html = re.sub(r'\b(window\.(parent|top)|document\.cookie|localStorage|sessionStorage)\b', '/* blocked */', cleaned_html)

    # 5. Inject CSP meta tag if html/head is present, or prepend it
    if "<head>" in cleaned_html:
        cleaned_html = cleaned_html.replace("<head>", f"<head>\n  {CSP_META_TAG}", 1)
    elif "<html>" in cleaned_html:
        cleaned_html = cleaned_html.replace("<html>", f"<html>\n<head>\n  {CSP_META_TAG}\n</head>", 1)
    else:
        cleaned_html = f"{CSP_META_TAG}\n{cleaned_html}"

    return cleaned_html
