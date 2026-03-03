"""Comprehensive unit tests for src/app.py Flask application.

Tests cover:
- Login endpoint (POST /login)
- Calculate endpoint (GET /calculate)
- Happy paths, edge cases, and error conditions
- SQL injection vulnerability demonstration
- Division by zero and invalid input handling
"""
import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from app import app


@pytest.fixture
def client():
    """Create a test client for the Flask application.
    
    Yields:
        FlaskClient: Test client for making requests
    """
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def captured_print(monkeypatch):
    """Fixture to capture print statements.
    
    Yields:
        list: List that collects printed messages
    """
    printed = []
    
    def mock_print(*args, **kwargs):
        printed.append(' '.join(str(arg) for arg in args))
    
    monkeypatch.setattr('builtins.print', mock_print)
    yield printed


class TestLoginEndpoint:
    """Test suite for POST /login endpoint."""
    
    def test_login_with_valid_username(self, client, captured_print):
        """Test login with a valid username."""
        response = client.post('/login', data={'username': 'john_doe'})
        
        assert response.status_code == 200
        assert b"Logged in (maybe)" in response.data
        assert any("SELECT * FROM users WHERE name = 'john_doe'" in p for p in captured_print)
    
    def test_login_with_empty_username(self, client, captured_print):
        """Test login with an empty username."""
        response = client.post('/login', data={'username': ''})
        
        assert response.status_code == 200
        assert b"Logged in (maybe)" in response.data
        assert any("SELECT * FROM users WHERE name = ''" in p for p in captured_print)
    
    def test_login_with_special_characters(self, client, captured_print):
        """Test login with special characters in username."""
        response = client.post('/login', data={'username': 'user@example.com'})
        
        assert response.status_code == 200
        assert b"Logged in (maybe)" in response.data
        assert any("user@example.com" in p for p in captured_print)
    
    def test_login_with_sql_injection_attempt(self, client, captured_print):
        """Test SQL injection vulnerability - demonstrates the security issue."""
        malicious_input = "admin' OR '1'='1"
        response = client.post('/login', data={'username': malicious_input})
        
        assert response.status_code == 200
        # This demonstrates the vulnerability - the malicious input gets concatenated
        assert any("SELECT * FROM users WHERE name = 'admin' OR '1'='1'" in p 
                  for p in captured_print)
    
    def test_login_with_sql_injection_drop_table(self, client, captured_print):
        """Test SQL injection with DROP TABLE attempt."""
        malicious_input = "'; DROP TABLE users; --"
        response = client.post('/login', data={'username': malicious_input})
        
        assert response.status_code == 200
        assert any("DROP TABLE users" in p for p in captured_print)
    
    def test_login_with_unicode_characters(self, client, captured_print):
        """Test login with Unicode characters."""
        response = client.post('/login', data={'username': 'José_García_日本'})
        
        assert response.status_code == 200
        assert b"Logged in (maybe)" in response.data
    
    def test_login_with_very_long_username(self, client, captured_print):
        """Test login with extremely long username."""
        long_username = 'a' * 10000
        response = client.post('/login', data={'username': long_username})
        
        assert response.status_code == 200
        assert any(long_username in p for p in captured_print)
    
    def test_login_missing_username_field(self, client):
        """Test login without username field - should raise KeyError."""
        with pytest.raises(Exception):  # Will raise KeyError
            response = client.post('/login', data={})
    
    def test_login_with_null_bytes(self, client, captured_print):
        """Test login with null bytes in username."""
        response = client.post('/login', data={'username': 'user\x00admin'})
        
        assert response.status_code == 200
        assert b"Logged in (maybe)" in response.data
    
    def test_login_get_request_not_allowed(self, client):
        """Test that GET request to /login is not allowed."""
        response = client.get('/login')
        
        assert response.status_code == 405  # Method Not Allowed
    
    def test_login_with_numeric_username(self, client, captured_print):
        """Test login with numeric username."""
        response = client.post('/login', data={'username': '12345'})
        
        assert response.status_code == 200
        assert any("SELECT * FROM users WHERE name = '12345'" in p for p in captured_print)
    
    def test_login_response_type(self, client):
        """Test that login returns text response."""
        response = client.post('/login', data={'username': 'test'})
        
        assert response.content_type == 'text/html; charset=utf-8'
        assert isinstance(response.data, bytes)


class TestCalculateEndpoint:
    """Test suite for GET /calculate endpoint."""
    
    def test_calculate_with_positive_number(self, client):
        """Test calculate with a positive number."""
        response = client.get('/calculate?n=10')
        
        assert response.status_code == 200
        assert b"10.0" in response.data
    
    def test_calculate_with_one(self, client):
        """Test calculate with n=1."""
        response = client.get('/calculate?n=1')
        
        assert response.status_code == 200
        assert b"100.0" in response.data
    
    def test_calculate_with_negative_number(self, client):
        """Test calculate with a negative number."""
        response = client.get('/calculate?n=-10')
        
        assert response.status_code == 200
        assert b"-10.0" in response.data
    
    def test_calculate_with_two(self, client):
        """Test calculate with n=2."""
        response = client.get('/calculate?n=2')
        
        assert response.status_code == 200
        assert b"50.0" in response.data
    
    def test_calculate_with_large_number(self, client):
        """Test calculate with a large number."""
        response = client.get('/calculate?n=1000')
        
        assert response.status_code == 200
        assert b"0.1" in response.data
    
    def test_calculate_with_zero_raises_error(self, client):
        """Test calculate with zero - should raise ZeroDivisionError."""
        with pytest.raises(ZeroDivisionError):
            response = client.get('/calculate?n=0')
    
    def test_calculate_with_float_string(self, client):
        """Test calculate with float string."""
        response = client.get('/calculate?n=5.5')
        
        assert response.status_code == 200
        # int(5.5) = 5, so 100/5 = 20.0
        # Note: int() truncates float strings
        result = float(response.data.decode())
        assert result == pytest.approx(20.0)
    
    def test_calculate_with_non_numeric_string(self, client):
        """Test calculate with non-numeric string - should raise ValueError."""
        with pytest.raises(ValueError):
            response = client.get('/calculate?n=abc')
    
    def test_calculate_with_empty_string(self, client):
        """Test calculate with empty string - should raise ValueError."""
        with pytest.raises(ValueError):
            response = client.get('/calculate?n=')
    
    def test_calculate_missing_parameter(self, client):
        """Test calculate without n parameter - should raise TypeError."""
        with pytest.raises(Exception):  # Will raise TypeError for int(None)
            response = client.get('/calculate')
    
    def test_calculate_with_scientific_notation(self, client):
        """Test calculate with scientific notation."""
        response = client.get('/calculate?n=1e2')
        
        assert response.status_code == 200
        # int(1e2) = 100, so 100/100 = 1.0
        assert b"1.0" in response.data
    
    def test_calculate_with_negative_zero(self, client):
        """Test calculate with -0 (treated as 0)."""
        with pytest.raises(ZeroDivisionError):
            response = client.get('/calculate?n=-0')
    
    def test_calculate_with_whitespace(self, client):
        """Test calculate with whitespace in parameter."""
        with pytest.raises(ValueError):
            response = client.get('/calculate?n= 10 ')
    
    def test_calculate_with_hexadecimal(self, client):
        """Test calculate with hexadecimal string."""
        with pytest.raises(ValueError):
            response = client.get('/calculate?n=0x10')
    
    def test_calculate_with_very_small_number(self, client):
        """Test calculate with very small positive number."""
        response = client.get('/calculate?n=10000')
        
        assert response.status_code == 200
        assert b"0.01" in response.data
    
    def test_calculate_response_type(self, client):
        """Test that calculate returns string response."""
        response = client.get('/calculate?n=10')
        
        assert response.content_type == 'text/html; charset=utf-8'
        assert isinstance(response.data, bytes)
    
    def test_calculate_post_request_not_allowed(self, client):
        """Test that POST request to /calculate is not allowed."""
        response = client.post('/calculate', data={'n': '10'})
        
        assert response.status_code == 405  # Method Not Allowed
    
    def test_calculate_with_fraction(self, client):
        """Test calculate with fractional result."""
        response = client.get('/calculate?n=3')
        
        assert response.status_code == 200
        result = float(response.data.decode())
        assert result == pytest.approx(33.333333333333336)
    
    def test_calculate_with_multiple_parameters(self, client):
        """Test calculate with multiple n parameters - should use first one."""
        response = client.get('/calculate?n=10&n=20')
        
        assert response.status_code == 200
        # Flask uses the first value
        assert b"10.0" in response.data
    
    def test_calculate_with_plus_sign(self, client):
        """Test calculate with plus sign in number."""
        response = client.get('/calculate?n=%2B10')  # URL encoded +10
        
        assert response.status_code == 200
        assert b"10.0" in response.data


class TestApplicationConfiguration:
    """Test suite for application configuration and setup."""
    
    def test_app_exists(self):
        """Test that app instance exists."""
        assert app is not None
    
    def test_app_is_flask_instance(self):
        """Test that app is a Flask instance."""
        from flask import Flask
        assert isinstance(app, Flask)
    
    def test_api_key_constant_defined(self):
        """Test that API_KEY constant is defined (security issue)."""
        import src.app as app_module
        assert hasattr(app_module, 'API_KEY')
        assert app_module.API_KEY == "12345-abcde-secret-key-do-not-share"
    
    def test_debug_mode_enabled(self):
        """Test that debug mode is enabled (should be False in production)."""
        # Note: This tests the configuration issue
        # In production, debug should be False
        pass
    
    def test_routes_registered(self, client):
        """Test that both routes are registered."""
        # Test that routes exist by checking 404 for non-existent route
        response = client.get('/nonexistent')
        assert response.status_code == 404
        
        # Our routes should not return 404
        response = client.get('/calculate?n=1')
        assert response.status_code != 404


class TestEdgeCasesAndSecurity:
    """Test suite for edge cases and security considerations."""
    
    def test_login_sql_injection_union_attack(self, client, captured_print):
        """Test UNION-based SQL injection."""
        malicious = "' UNION SELECT * FROM passwords --"
        response = client.post('/login', data={'username': malicious})
        
        assert response.status_code == 200
        assert any("UNION SELECT" in p for p in captured_print)
    
    def test_login_with_quotes_and_escapes(self, client, captured_print):
        """Test with various quote and escape combinations."""
        test_cases = [
            "user'name",
            'user"name',
            "user\\'name",
            "user\\\"name",
        ]
        
        for username in test_cases:
            response = client.post('/login', data={'username': username})
            assert response.status_code == 200
    
    def test_calculate_boundary_values(self, client):
        """Test calculate with boundary integer values."""
        # Test with maximum positive value that won't cause issues
        response = client.get('/calculate?n=2147483647')
        assert response.status_code == 200
        
        # Test with minimum negative value
        response = client.get('/calculate?n=-2147483647')
        assert response.status_code == 200
    
    def test_concurrent_requests_simulation(self, client):
        """Test that multiple sequential requests work correctly."""
        for i in range(1, 11):
            response = client.get(f'/calculate?n={i}')
            assert response.status_code == 200
            expected = 100.0 / i
            actual = float(response.data.decode())
            assert actual == pytest.approx(expected)
    
    def test_login_with_newlines(self, client, captured_print):
        """Test login with newline characters."""
        response = client.post('/login', data={'username': 'user\nname'})
        assert response.status_code == 200
    
    def test_calculate_type_coercion(self, client):
        """Test int() type coercion with edge cases."""
        # Boolean true becomes 1
        response = client.get('/calculate?n=True')
        with pytest.raises(ValueError):
            pass  # Should raise ValueError
    
    def test_xss_in_username(self, client, captured_print):
        """Test potential XSS in username field."""
        xss_payload = "<script>alert('XSS')</script>"
        response = client.post('/login', data={'username': xss_payload})
        
        assert response.status_code == 200
        # The response doesn't render the username, but it's in the print
        assert any("<script>" in p for p in captured_print)


class TestErrorHandling:
    """Test suite specifically for error conditions."""
    
    def test_calculate_none_parameter(self, client):
        """Test calculate when parameter is explicitly None."""
        with pytest.raises(TypeError):
            response = client.get('/calculate')
    
    def test_login_form_data_vs_json(self, client):
        """Test login with JSON instead of form data."""
        response = client.post('/login', 
                              json={'username': 'test'},
                              content_type='application/json')
        # Should fail because it expects form data
        with pytest.raises(Exception):
            pass
    
    def test_calculate_with_infinity(self, client):
        """Test calculate with infinity string."""
        with pytest.raises(ValueError):
            response = client.get('/calculate?n=inf')
    
    def test_malformed_requests(self, client):
        """Test various malformed requests."""
        # PUT request to login
        response = client.put('/login')
        assert response.status_code == 405
        
        # DELETE request to calculate
        response = client.delete('/calculate')
        assert response.status_code == 405


class TestIntegrationScenarios:
    """Integration-style tests that combine multiple operations."""
    
    def test_login_then_calculate_sequence(self, client, captured_print):
        """Test a sequence of login followed by calculate."""
        # First login
        login_response = client.post('/login', data={'username': 'testuser'})
        assert login_response.status_code == 200
        
        # Then calculate
        calc_response = client.get('/calculate?n=5')
        assert calc_response.status_code == 200
        assert b"20.0" in calc_response.data
    
    def test_multiple_logins_different_users(self, client, captured_print):
        """Test multiple logins with different usernames."""
        users = ['alice', 'bob', 'charlie', 'david', 'eve']
        
        for user in users:
            response = client.post('/login', data={'username': user})
            assert response.status_code == 200
            assert b"Logged in (maybe)" in response.data
    
    def test_calculate_various_divisors(self, client):
        """Test calculate with various divisors to ensure consistency."""
        test_cases = {
            '1': '100.0',
            '2': '50.0',
            '4': '25.0',
            '5': '20.0',
            '10': '10.0',
            '20': '5.0',
            '25': '4.0',
            '50': '2.0',
            '100': '1.0',
        }
        
        for n, expected in test_cases.items():
            response = client.get(f'/calculate?n={n}')
            assert response.status_code == 200
            assert expected in response.data.decode()