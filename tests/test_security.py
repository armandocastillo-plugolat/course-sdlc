"""Security-focused tests for src/app.py.

This module contains tests specifically targeting security vulnerabilities
and potential attack vectors in the application.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from app import app


@pytest.fixture
def client():
    """Create a test client for security testing."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def captured_print(monkeypatch):
    """Fixture to capture print output."""
    printed = []
    
    def mock_print(*args, **kwargs):
        printed.append(' '.join(str(arg) for arg in args))
    
    monkeypatch.setattr('builtins.print', mock_print)
    yield printed


class TestSQLInjectionVulnerabilities:
    """Comprehensive SQL injection vulnerability tests."""
    
    def test_classic_sql_injection_bypass_authentication(self, client, captured_print):
        """Test classic SQL injection to bypass authentication."""
        payloads = [
            "admin' OR '1'='1",
            "admin' OR '1'='1' --",
            "admin' OR '1'='1' #",
            "admin' OR '1'='1'/*",
            "' OR '1'='1",
            "' OR 1=1 --",
            "admin'--",
            "admin' #",
        ]
        
        for payload in payloads:
            response = client.post('/login', data={'username': payload})
            assert response.status_code == 200
            # Verify the malicious SQL gets constructed
            assert any("OR" in p and "1" in p for p in captured_print)
    
    def test_sql_injection_stacked_queries(self, client, captured_print):
        """Test stacked query SQL injection attempts."""
        payloads = [
            "'; DROP TABLE users; --",
            "'; DELETE FROM users; --",
            "'; UPDATE users SET password='hacked'; --",
            "'; INSERT INTO users VALUES('hacker','pass'); --",
        ]
        
        for payload in payloads:
            response = client.post('/login', data={'username': payload})
            assert response.status_code == 200
    
    def test_sql_injection_union_based(self, client, captured_print):
        """Test UNION-based SQL injection."""
        payloads = [
            "' UNION SELECT NULL--",
            "' UNION SELECT NULL,NULL--",
            "' UNION SELECT username,password FROM users--",
            "' UNION ALL SELECT NULL--",
        ]
        
        for payload in payloads:
            response = client.post('/login', data={'username': payload})
            assert response.status_code == 200
            assert any("UNION" in p for p in captured_print)
    
    def test_sql_injection_time_based_blind(self, client, captured_print):
        """Test time-based blind SQL injection attempts."""
        payloads = [
            "' OR SLEEP(5)--",
            "' OR WAITFOR DELAY '0:0:5'--",
            "'; WAITFOR DELAY '0:0:5'--",
        ]
        
        for payload in payloads:
            response = client.post('/login', data={'username': payload})
            assert response.status_code == 200
    
    def test_sql_injection_boolean_based_blind(self, client, captured_print):
        """Test boolean-based blind SQL injection."""
        payloads = [
            "admin' AND '1'='1",
            "admin' AND '1'='2",
            "' AND 1=1 AND 'x'='x",
            "' AND 1=2 AND 'x'='x",
        ]
        
        for payload in payloads:
            response = client.post('/login', data={'username': payload})
            assert response.status_code == 200
    
    def test_sql_injection_with_encoding(self, client, captured_print):
        """Test SQL injection with various encoding techniques."""
        # URL encoded single quote
        response = client.post('/login', data={'username': "admin%27--"})
        assert response.status_code == 200
        
        # Double URL encoding
        response = client.post('/login', data={'username': "admin%2527--"})
        assert response.status_code == 200


class TestAPIKeyExposure:
    """Tests related to hardcoded API key security issue."""
    
    def test_api_key_is_hardcoded(self):
        """Test that API key is exposed in code (security issue)."""
        import src.app as app_module
        assert hasattr(app_module, 'API_KEY')
    
    def test_api_key_value_is_sensitive(self):
        """Test that the API key contains sensitive-looking data."""
        import src.app as app_module
        api_key = app_module.API_KEY
        assert len(api_key) > 10
        assert 'secret' in api_key.lower() or 'key' in api_key.lower()
    
    def test_api_key_not_from_environment(self):
        """Test that API key is not loaded from environment variables."""
        import src.app as app_module
        # This is a negative test - the key SHOULD be from environment
        # but it's not, which is a security issue
        assert app_module.API_KEY == "12345-abcde-secret-key-do-not-share"


class TestInputValidationBypass:
    """Tests for input validation bypass attempts."""
    
    def test_login_with_null_byte_injection(self, client, captured_print):
        """Test null byte injection in username."""
        payloads = [
            "admin\x00",
            "admin\x00.jpg",
            "\x00admin",
        ]
        
        for payload in payloads:
            response = client.post('/login', data={'username': payload})
            assert response.status_code == 200
    
    def test_login_with_unicode_bypass(self, client, captured_print):
        """Test Unicode normalization bypass attempts."""
        payloads = [
            "admin\u0000",
            "\uFEFFadmin",  # Zero-width no-break space
            "ad\u200Bmin",  # Zero-width space
        ]
        
        for payload in payloads:
            response = client.post('/login', data={'username': payload})
            assert response.status_code == 200
    
    def test_calculate_with_type_confusion(self, client):
        """Test type confusion in calculate endpoint."""
        # These should fail but test the error handling
        with pytest.raises((ValueError, TypeError)):
            client.get('/calculate?n=[]')
        
        with pytest.raises((ValueError, TypeError)):
            client.get('/calculate?n={}')


class TestXSSVulnerabilities:
    """Tests for Cross-Site Scripting vulnerabilities."""
    
    def test_xss_script_tag(self, client, captured_print):
        """Test XSS with script tags."""
        payloads = [
            "<script>alert('XSS')</script>",
            "<script>alert(1)</script>",
            "<SCRIPT>alert('XSS')</SCRIPT>",
        ]
        
        for payload in payloads:
            response = client.post('/login', data={'username': payload})
            assert response.status_code == 200
            # The response doesn't render it, but it's in the print output
            assert any("<script>" in p.lower() for p in captured_print)
    
    def test_xss_event_handlers(self, client, captured_print):
        """Test XSS with HTML event handlers."""
        payloads = [
            "<img src=x onerror=alert(1)>",
            "<body onload=alert(1)>",
            "<svg onload=alert(1)>",
        ]
        
        for payload in payloads:
            response = client.post('/login', data={'username': payload})
            assert response.status_code == 200
    
    def test_xss_javascript_protocol(self, client, captured_print):
        """Test XSS with javascript: protocol."""
        payloads = [
            "javascript:alert(1)",
            "<a href='javascript:alert(1)'>click</a>",
        ]
        
        for payload in payloads:
            response = client.post('/login', data={'username': payload})
            assert response.status_code == 200


class TestDenialOfServiceVulnerabilities:
    """Tests for potential DoS vulnerabilities."""
    
    def test_calculate_with_division_by_zero(self, client):
        """Test DoS via division by zero."""
        with pytest.raises(ZeroDivisionError):
            client.get('/calculate?n=0')
    
    def test_login_with_extremely_long_input(self, client):
        """Test resource exhaustion with very long input."""
        # 1MB of data
        huge_username = 'A' * (1024 * 1024)
        response = client.post('/login', data={'username': huge_username})
        assert response.status_code == 200
    
    def test_calculate_with_huge_number(self, client):
        """Test calculation with extremely large numbers."""
        # This should work but results in very small output
        response = client.get('/calculate?n=999999999999')
        assert response.status_code == 200


class TestAuthenticationBypass:
    """Tests for authentication bypass vulnerabilities."""
    
    def test_no_authentication_required_for_calculate(self, client):
        """Test that calculate endpoint has no authentication."""
        # This demonstrates a potential security issue
        response = client.get('/calculate?n=10')
        assert response.status_code == 200
        # No authentication needed - this might be a security issue
    
    def test_no_session_management(self, client):
        """Test that there's no session management."""
        # Login doesn't create a session
        client.post('/login', data={'username': 'test'})
        
        # No session cookie should be set
        assert 'session' not in [cookie.name for cookie in client.cookie_jar]


class TestInformationDisclosure:
    """Tests for information disclosure vulnerabilities."""
    
    def test_debug_mode_enabled_risk(self):
        """Test that debug mode configuration could expose information."""
        # Debug mode is enabled in the code (app.run(debug=True))
        # This is a security risk in production
        pass
    
    def test_error_messages_disclosure(self, client):
        """Test that error messages might disclose information."""
        # When debug=True, detailed error messages are shown
        # We can't easily test this without actually running the app
        pass
    
    def test_sql_query_disclosure_in_logs(self, client, captured_print):
        """Test that SQL queries are printed (information disclosure)."""
        client.post('/login', data={'username': 'test'})
        
        # The application prints the SQL query - this is an info disclosure
        assert any("SELECT * FROM users" in p for p in captured_print)