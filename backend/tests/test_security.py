import pytest
from app.security.sanitizer import sanitize_html, CSP_META_TAG


def test_html_sanitizer_removes_dangerous_scripts():
    # 1. External script injection attempt
    malicious_external = '<div class="card"><h1>Tool</h1><script src="https://evil.com/steal.js"></script></div>'
    sanitized = sanitize_html(malicious_external)
    assert 'https://evil.com/steal.js' not in sanitized
    assert '<!-- external script blocked -->' in sanitized
    assert CSP_META_TAG in sanitized

    # 2. Event handler injection (onerror, onload, onclick)
    malicious_event = '<img src="invalid.jpg" onerror="alert(document.cookie)" onclick="window.parent.postMessage(\'leak\')">'
    sanitized_event = sanitize_html(malicious_event)
    assert 'onerror' not in sanitized_event
    assert 'onclick' not in sanitized_event
    assert 'document.cookie' not in sanitized_event
    assert 'window.parent' not in sanitized_event

    # 3. Javascript: URI in links
    malicious_link = '<a href="javascript:alert(1)">Click for bonus</a>'
    sanitized_link = sanitize_html(malicious_link)
    assert 'javascript:' not in sanitized_link
    assert 'href="#"' in sanitized_link


def test_html_sanitizer_preserves_safe_interactivity():
    # Safe interactive HTML with local calculations and canvas
    safe_markup = """
    <div class="calculator">
      <h3>SaaS LTV Calculator</h3>
      <input type="number" id="arpu" value="100" />
      <input type="number" id="churn" value="0.05" />
      <button id="calc-btn">Calculate</button>
      <div id="result">LTV: $2,000</div>
      <canvas id="growth-chart" width="400" height="200"></canvas>
    </div>
    """
    sanitized = sanitize_html(safe_markup)
    assert '<input' in sanitized
    assert '<button' in sanitized
    assert '<canvas' in sanitized
    assert 'id="growth-chart"' in sanitized
    assert CSP_META_TAG in sanitized


def test_csp_meta_tag_injected_properly():
    html_with_head = "<html><head><title>Test</title></head><body><h1>Hello</h1></body></html>"
    sanitized = sanitize_html(html_with_head)
    assert "<head>\n  <meta http-equiv=\"Content-Security-Policy\"" in sanitized
    assert "default-src 'none'" in sanitized
    assert "connect-src 'none'" in sanitized
