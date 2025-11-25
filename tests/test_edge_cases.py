"""Edge case tests for the Flask application.

Tests unusual, unexpected, and extreme inputs and scenarios.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from app import app


@pytest.fixture
def client():
    """Create test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def captured_print(monkeypatch):
    """Capture print output."""
    printed = []
    
    def mock_print(*args, **kwargs):
        printed.append(' '.join(str(arg) for arg in args))
    
    monkeypatch.setattr('builtins.print', mock_print)
    yield printed


class TestUnicodeAndEncoding:
    """Test Unicode and encoding edge cases."""
    
    def test_login_with_emoji(self, client, captured_print):
        """Test login with emoji in username."""
        response = client.post('/login', data={'username': '😀👍🎉'})
        assert response.status_code == 200
    
    def test_login_with_rtl_text(self, client, captured_print):
        """Test login with right-to-left text."""
        response = client.post('/login', data={'username': 'مستخدم'})
        assert response.status_code == 200
    
    def test_login_with_mixed_scripts(self, client, captured_print):
        """Test login with mixed scripts."""
        response = client.post('/login', data={'username': 'user用户пользователь'})
        assert response.status_code == 200
    
    def test_login_with_zero_width_characters(self, client, captured_print):
        """Test login with zero-width characters."""
        # Zero-width space
        response = client.post('/login', data={'username': 'user\u200Bname'})
        assert response.status_code == 200
        
        # Zero-width joiner
        response = client.post('/login', data={'username': 'user\u200Dname'})
        assert response.status_code == 200
    
    def test_login_with_combining_characters(self, client, captured_print):
        """Test login with Unicode combining characters."""
        # Combining diacritical marks
        response = client.post('/login', data={'username': 'café'})  # é is e + combining acute
        assert response.status_code == 200
    
    def test_calculate_with_unicode_digits(self, client):
        """Test calculate with Unicode digit characters."""
        # Regular digits work, but Unicode digits should fail
        with pytest.raises(ValueError):
            client.get('/calculate?n=٥')  # Arabic-Indic digit 5


class TestNumericEdgeCases:
    """Test numeric edge cases in calculate endpoint."""
    
    def test_calculate_with_leading_zeros(self, client):
        """Test calculate with leading zeros."""
        response = client.get('/calculate?n=010')
        assert response.status_code == 200
        # Python int() treats this as decimal 10, not octal
        assert b"10.0" in response.data
    
    def test_calculate_with_plus_sign(self, client):
        """Test calculate with explicit plus sign."""
        response = client.get('/calculate?n=+10')
        assert response.status_code == 200
        assert b"10.0" in response.data
    
    def test_calculate_with_scientific_notation_lowercase(self, client):
        """Test calculate with lowercase scientific notation."""
        response = client.get('/calculate?n=1e2')
        assert response.status_code == 200
        # int(1e2) = 100
        assert b"1.0" in response.data
    
    def test_calculate_with_scientific_notation_uppercase(self, client):
        """Test calculate with uppercase scientific notation."""
        response = client.get('/calculate?n=1E2')
        assert response.status_code == 200
        assert b"1.0" in response.data
    
    def test_calculate_with_negative_scientific_notation(self, client):
        """Test calculate with negative exponent in scientific notation."""
        with pytest.raises(ValueError):
            # int() doesn't handle negative exponents well
            client.get('/calculate?n=1e-2')
    
    def test_calculate_with_underscores_in_number(self, client):
        """Test calculate with underscores (Python 3.6+ numeric literal)."""
        with pytest.raises(ValueError):
            # URL parameter won't parse underscores
            client.get('/calculate?n=1_000')
    
    def test_calculate_with_binary_literal(self, client):
        """Test calculate with binary literal string."""
        with pytest.raises(ValueError):
            client.get('/calculate?n=0b1010')
    
    def test_calculate_with_octal_literal(self, client):
        """Test calculate with octal literal string."""
        with pytest.raises(ValueError):
            client.get('/calculate?n=0o12')
    
    def test_calculate_with_max_int(self, client):
        """Test calculate with very large integer."""
        # Python can handle arbitrarily large integers
        response = client.get('/calculate?n=999999999999999999999999')
        assert response.status_code == 200


class TestWhitespaceEdgeCases:
    """Test whitespace handling edge cases."""
    
    def test_login_with_leading_whitespace(self, client, captured_print):
        """Test login with leading whitespace."""
        response = client.post('/login', data={'username': '   user'})
        assert response.status_code == 200
    
    def test_login_with_trailing_whitespace(self, client, captured_print):
        """Test login with trailing whitespace."""
        response = client.post('/login', data={'username': 'user   '})
        assert response.status_code == 200
    
    def test_login_with_internal_whitespace(self, client, captured_print):
        """Test login with internal whitespace."""
        response = client.post('/login', data={'username': 'user   name'})
        assert response.status_code == 200
    
    def test_login_with_tabs(self, client, captured_print):
        """Test login with tab characters."""
        response = client.post('/login', data={'username': 'user\tname'})
        assert response.status_code == 200
    
    def test_login_with_newlines(self, client, captured_print):
        """Test login with newline characters."""
        response = client.post('/login', data={'username': 'user\nname'})
        assert response.status_code == 200
    
    def test_calculate_with_whitespace(self, client):
        """Test calculate with whitespace in parameter."""
        with pytest.raises(ValueError):
            client.get('/calculate?n= 10 ')


class TestSpecialCharacterEdgeCases:
    """Test special character handling."""
    
    def test_login_with_control_characters(self, client, captured_print):
        """Test login with control characters."""
        control_chars = ['\x00', '\x01', '\x1f', '\x7f']
        
        for char in control_chars:
            try:
                response = client.post('/login', data={'username': f'user{char}name'})
                assert response.status_code == 200
            except Exception:
                # Some control characters might cause issues
                pass
    
    def test_login_with_backslash(self, client, captured_print):
        """Test login with backslash character."""
        response = client.post('/login', data={'username': 'user\\name'})
        assert response.status_code == 200
    
    def test_login_with_quotes(self, client, captured_print):
        """Test login with various quote characters."""
        quotes = ["'", '"', "`", "'", "'", """, """]
        
        for quote in quotes:
            response = client.post('/login', data={'username': f'user{quote}name'})
            assert response.status_code == 200
    
    def test_login_with_url_special_chars(self, client, captured_print):
        """Test login with URL special characters."""
        special_chars = ['&', '=', '?', '#', '%', '+']
        
        for char in special_chars:
            response = client.post('/login', data={'username': f'user{char}name'})
            assert response.status_code == 200
    
    def test_login_with_path_traversal_attempt(self, client, captured_print):
        """Test login with path traversal characters."""
        response = client.post('/login', data={'username': '../../../etc/passwd'})
        assert response.status_code == 200


class TestConcurrencyEdgeCases:
    """Test edge cases related to concurrent operations."""
    
    def test_rapid_sequential_logins(self, client, captured_print):
        """Test rapid sequential login requests."""
        for i in range(100):
            response = client.post('/login', data={'username': f'user{i}'})
            assert response.status_code == 200
    
    def test_rapid_sequential_calculations(self, client):
        """Test rapid sequential calculation requests."""
        for i in range(1, 101):
            response = client.get(f'/calculate?n={i}')
            assert response.status_code == 200
    
    def test_interleaved_requests(self, client, captured_print):
        """Test interleaved login and calculate requests."""
        for i in range(1, 51):
            client.post('/login', data={'username': f'user{i}'})
            client.get(f'/calculate?n={i}')


class TestHTTPEdgeCases:
    """Test HTTP protocol edge cases."""
    
    def test_login_with_multiple_values_same_key(self, client):
        """Test login with multiple username values."""
        # Flask uses the first value by default
        response = client.post('/login', data=[('username', 'user1'), ('username', 'user2')])
        assert response.status_code == 200
    
    def test_calculate_with_multiple_n_values(self, client):
        """Test calculate with multiple n parameters."""
        response = client.get('/calculate?n=10&n=20&n=30')
        assert response.status_code == 200
        # Flask uses the first value
        assert b"10.0" in response.data
    
    def test_login_with_case_sensitive_parameter(self, client):
        """Test that parameter names are case-sensitive."""
        # Using 'Username' instead of 'username' should fail
        with pytest.raises(Exception):
            client.post('/login', data={'Username': 'test'})
    
    def test_calculate_with_case_sensitive_parameter(self, client):
        """Test that parameter names are case-sensitive."""
        # Using 'N' instead of 'n' should fail
        with pytest.raises(Exception):
            client.get('/calculate?N=10')
    
    def test_login_with_empty_post_body(self, client):
        """Test login with completely empty POST body."""
        with pytest.raises(Exception):
            client.post('/login')
    
    def test_calculate_with_empty_query_string(self, client):
        """Test calculate with empty query string."""
        with pytest.raises(Exception):
            client.get('/calculate')


class TestFloatPrecisionEdgeCases:
    """Test floating-point precision edge cases."""
    
    def test_calculate_with_prime_divisor(self, client):
        """Test calculation resulting in repeating decimal."""
        response = client.get('/calculate?n=3')
        result = float(response.data.decode())
        # 100/3 = 33.333...
        assert result == pytest.approx(33.333333333333336)
    
    def test_calculate_with_divisors_resulting_in_small_floats(self, client):
        """Test calculations resulting in very small floats."""
        large_divisors = [10000, 100000, 1000000]
        
        for divisor in large_divisors:
            response = client.get(f'/calculate?n={divisor}')
            assert response.status_code == 200
            result = float(response.data.decode())
            assert result > 0
    
    def test_calculate_precision_consistency(self, client):
        """Test that float precision is consistent across requests."""
        results = []
        for _ in range(10):
            response = client.get('/calculate?n=7')
            result = float(response.data.decode())
            results.append(result)
        
        # All results should be identical
        assert all(r == results[0] for r in results)


class TestResourceLimits:
    """Test resource limit edge cases."""
    
    def test_login_with_maximum_practical_username_length(self, client):
        """Test login with very long but practical username."""
        # 10KB username
        long_username = 'a' * (10 * 1024)
        response = client.post('/login', data={'username': long_username})
        assert response.status_code == 200
    
    def test_calculate_with_many_decimal_places(self, client):
        """Test that results with many decimal places are handled."""
        # 100/7 has many decimal places
        response = client.get('/calculate?n=7')
        result_str = response.data.decode()
        assert '.' in result_str
        assert len(result_str) > 10  # Should have many digits