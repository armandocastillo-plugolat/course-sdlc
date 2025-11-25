"""Integration tests for the Flask application.

These tests verify the application behavior when multiple components
interact together, testing realistic user scenarios.
"""
import pytest
import sys
import os
from concurrent.futures import ThreadPoolExecutor
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from app import app


@pytest.fixture
def client():
    """Create a test client."""
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


class TestUserWorkflows:
    """Test complete user workflows."""
    
    def test_user_login_and_calculate_workflow(self, client, captured_print):
        """Test a typical user workflow: login then perform calculation."""
        # Step 1: User logs in
        login_response = client.post('/login', data={'username': 'john_doe'})
        assert login_response.status_code == 200
        assert b"Logged in (maybe)" in login_response.data
        
        # Verify SQL query was constructed
        assert any("john_doe" in p for p in captured_print)
        
        # Step 2: User performs a calculation
        calc_response = client.get('/calculate?n=25')
        assert calc_response.status_code == 200
        assert b"4.0" in calc_response.data
    
    def test_multiple_users_concurrent_logins(self, client, captured_print):
        """Test multiple users logging in with different usernames."""
        users = ['alice', 'bob', 'charlie', 'david', 'eve']
        
        for user in users:
            response = client.post('/login', data={'username': user})
            assert response.status_code == 200
            assert b"Logged in (maybe)" in response.data
        
        # Verify all usernames were processed
        for user in users:
            assert any(user in p for p in captured_print)
    
    def test_user_performs_multiple_calculations(self, client):
        """Test a user performing multiple calculations in sequence."""
        calculations = [
            ('1', '100.0'),
            ('2', '50.0'),
            ('5', '20.0'),
            ('10', '10.0'),
            ('100', '1.0'),
        ]
        
        for n, expected in calculations:
            response = client.get(f'/calculate?n={n}')
            assert response.status_code == 200
            assert expected in response.data.decode()
    
    def test_user_with_sql_injection_then_calculate(self, client, captured_print):
        """Test malicious user attempting SQL injection then calculating."""
        # Malicious login attempt
        malicious_username = "admin' OR '1'='1"
        login_response = client.post('/login', data={'username': malicious_username})
        assert login_response.status_code == 200
        
        # User can still use calculate endpoint
        calc_response = client.get('/calculate?n=10')
        assert calc_response.status_code == 200
        assert b"10.0" in calc_response.data


class TestErrorRecovery:
    """Test error handling and recovery scenarios."""
    
    def test_recovery_after_division_by_zero(self, client):
        """Test that app continues working after division by zero error."""
        # First, cause a division by zero error
        with pytest.raises(ZeroDivisionError):
            client.get('/calculate?n=0')
        
        # App should still work for subsequent requests
        response = client.get('/calculate?n=10')
        assert response.status_code == 200
        assert b"10.0" in response.data
    
    def test_recovery_after_invalid_input(self, client):
        """Test recovery after invalid input errors."""
        # Cause a ValueError
        with pytest.raises(ValueError):
            client.get('/calculate?n=invalid')
        
        # App should still work
        response = client.get('/calculate?n=5')
        assert response.status_code == 200
    
    def test_recovery_after_missing_form_field(self, client):
        """Test recovery after missing form field error."""
        # Cause a KeyError
        with pytest.raises(Exception):
            client.post('/login', data={})
        
        # App should still work
        response = client.post('/login', data={'username': 'test'})
        assert response.status_code == 200


class TestEndpointInteraction:
    """Test interactions between different endpoints."""
    
    def test_login_does_not_affect_calculate(self, client):
        """Test that login state doesn't affect calculate endpoint."""
        # Login first
        client.post('/login', data={'username': 'test'})
        
        # Calculate should work the same
        response = client.get('/calculate?n=10')
        assert response.status_code == 200
        assert b"10.0" in response.data
    
    def test_calculate_does_not_affect_login(self, client, captured_print):
        """Test that calculate state doesn't affect login endpoint."""
        # Calculate first
        client.get('/calculate?n=10')
        
        # Login should work the same
        response = client.post('/login', data={'username': 'test'})
        assert response.status_code == 200
        assert any("test" in p for p in captured_print)
    
    def test_alternating_endpoints(self, client, captured_print):
        """Test alternating between login and calculate endpoints."""
        # Login
        client.post('/login', data={'username': 'user1'})
        
        # Calculate
        response = client.get('/calculate?n=5')
        assert b"20.0" in response.data
        
        # Login again
        client.post('/login', data={'username': 'user2'})
        
        # Calculate again
        response = client.get('/calculate?n=10')
        assert b"10.0" in response.data


class TestDataConsistency:
    """Test data consistency across operations."""
    
    def test_calculate_results_are_consistent(self, client):
        """Test that same input gives same output consistently."""
        for _ in range(10):
            response = client.get('/calculate?n=7')
            assert response.status_code == 200
            result = float(response.data.decode())
            expected = 100.0 / 7.0
            assert result == pytest.approx(expected)
    
    def test_login_query_construction_is_consistent(self, client, captured_print):
        """Test that SQL query construction is consistent."""
        username = "testuser"
        expected_query = f"SELECT * FROM users WHERE name = '{username}'"
        
        # Try multiple times
        for _ in range(5):
            client.post('/login', data={'username': username})
        
        # All should have the same query format
        matching_queries = [p for p in captured_print if expected_query in p]
        assert len(matching_queries) >= 5


class TestBoundaryConditions:
    """Test boundary conditions across the application."""
    
    def test_minimum_and_maximum_calculations(self, client):
        """Test calculations at boundary values."""
        # Minimum positive value
        response = client.get('/calculate?n=1')
        assert response.status_code == 200
        assert b"100.0" in response.data
        
        # Large value
        response = client.get('/calculate?n=1000000')
        assert response.status_code == 200
        result = float(response.data.decode())
        assert result == pytest.approx(0.0001)
        
        # Negative boundary
        response = client.get('/calculate?n=-1')
        assert response.status_code == 200
        assert b"-100.0" in response.data
    
    def test_username_length_boundaries(self, client, captured_print):
        """Test username at various length boundaries."""
        # Empty username
        client.post('/login', data={'username': ''})
        
        # Single character
        client.post('/login', data={'username': 'a'})
        
        # Very long username
        long_name = 'a' * 1000
        client.post('/login', data={'username': long_name})
        
        # All should succeed
        assert len([p for p in captured_print if "SELECT" in p]) >= 3


class TestPerformanceCharacteristics:
    """Test performance-related characteristics."""
    
    def test_sequential_requests_performance(self, client):
        """Test performance of sequential requests."""
        start_time = time.time()
        
        for i in range(100):
            response = client.get(f'/calculate?n={i+1}')
            assert response.status_code == 200
        
        elapsed = time.time() - start_time
        # Should complete 100 requests reasonably quickly (< 5 seconds)
        assert elapsed < 5.0
    
    def test_alternating_endpoint_performance(self, client, captured_print):
        """Test performance when alternating between endpoints."""
        start_time = time.time()
        
        for i in range(50):
            client.post('/login', data={'username': f'user{i}'})
            client.get(f'/calculate?n={i+1}')
        
        elapsed = time.time() - start_time
        # Should complete 100 total requests (50 of each) reasonably quickly
        assert elapsed < 5.0


class TestStatelessness:
    """Test that the application is stateless."""
    
    def test_no_session_persistence(self, client):
        """Test that no session state is maintained."""
        # Login
        response1 = client.post('/login', data={'username': 'user1'})
        
        # Second login with different user
        response2 = client.post('/login', data={'username': 'user2'})
        
        # Both should succeed independently
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # No session cookie should exist
        cookies = [cookie.name for cookie in client.cookie_jar]
        assert 'session' not in cookies
    
    def test_calculation_statelessness(self, client):
        """Test that calculations don't maintain state."""
        # First calculation
        response1 = client.get('/calculate?n=10')
        result1 = float(response1.data.decode())
        
        # Second calculation with same input
        response2 = client.get('/calculate?n=10')
        result2 = float(response2.data.decode())
        
        # Results should be identical (stateless)
        assert result1 == result2 == 10.0