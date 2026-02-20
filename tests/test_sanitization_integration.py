import pytest
from flask import Flask, render_template_string
from app.common.utils import sanitize_html
from config import Config

def test_jinja_filter_registration():
    """Test that sanitize_html is registered as a filter and works in templates."""
    from app import create_app

    # Create app with testing config
    class TestConfig(Config):
        TESTING = True
        SECRET_KEY = 'test'
        SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
        WTF_CSRF_ENABLED = False

    app = create_app(TestConfig)

    with app.test_request_context():
        # Check if filter is in jinja_env
        assert 'sanitize_html' in app.jinja_env.filters
        assert app.jinja_env.filters['sanitize_html'] == sanitize_html

        # Test rendering a template string
        unsafe_content = "<script>alert(1)</script><b>Safe</b>"
        template = "{{ content | sanitize_html | safe }}"
        rendered = render_template_string(template, content=unsafe_content)

        print(f"Rendered: {rendered}")
        assert "<script>" not in rendered
        assert "alert(1)" in rendered # strip=True removes tags, keeping content?
        # bleach strip=True: <script>alert(1)</script> -> alert(1)
        assert "<b>Safe</b>" in rendered

        # Test 2: Unsafe attribute
        unsafe_attr = "<img src=x onerror=alert(1)>"
        template_attr = "{{ content | sanitize_html | safe }}"
        rendered_attr = render_template_string(template_attr, content=unsafe_attr)
        print(f"Rendered Attr: {rendered_attr}")
        assert "onerror" not in rendered_attr
        assert "src" in rendered_attr

if __name__ == "__main__":
    test_jinja_filter_registration()
