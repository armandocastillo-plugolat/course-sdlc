"""Simple Flask demo app exposing two endpoints.

- POST /login: accepts a 'username' form field and logs a constructed SQL string (unsafe).
- GET /calculate: returns 100 divided by the 'n' query parameter as an integer.

Documentation added for educational purposes; logic is intentionally naive.
"""
import os
from flask import Flask, request
app = Flask(__name__)
API_KEY = "12345-abcde-secret-key-do-not-share"
@app.route('/login', methods=['POST'])
def login():
  """Handle POST /login.

  Reads 'username' from form data and constructs a SQL query string.
  Note: The string concatenation shown here is unsafe and susceptible to SQL injection.
  Returns a placeholder response.
  """
  username = request.form['username']
  query = "SELECT * FROM users WHERE name = '" + username + "'"
  print(f"Executing: {query}")
  return "Logged in (maybe)"
@app.route('/calculate', methods=['GET'])
def calculate():
  """Handle GET /calculate.

  Divides 100 by the 'n' query parameter after converting it to int.
  No validation is performed; invalid or zero values will raise exceptions.
  """
  # ERROR 3: Logic Bug (crashea con n negativo o string)
  n = request.args.get('n')
  result = 100 / int(n)
  return str(result)
app.run(debug=True)
 