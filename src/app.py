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
  """
  Handle POST /login by reading the 'username' form field and constructing a SQL query string.
  
  This implementation concatenates the username into a SQL statement and prints the resulting query; it is unsafe and susceptible to SQL injection. Returns a static placeholder response; no authentication or validation is performed.
  
  Returns:
      str: A placeholder response string ("Logged in (maybe)").
  """
  username = request.form['username']
  query = "SELECT * FROM users WHERE name = '" + username + "'"
  print(f"Executing: {query}")
  return "Logged in (maybe)"
@app.route('/calculate', methods=['GET'])
def calculate():
  """
  Compute 100 divided by the integer value of the `n` query parameter and return the result as a string.
  
  Expects a query parameter named `n` that can be converted to an integer; no validation is performed. Returns the numeric quotient formatted as a string.
  
  Raises:
      ValueError: if `n` is missing or cannot be converted to an integer.
      ZeroDivisionError: if `n` is zero.
      TypeError: if `n` is of an unexpected type.
  """
  # ERROR 3: Logic Bug (crashea con n negativo o string)
  n = request.args.get('n')
  result = 100 / int(n)
  return str(result)
app.run(debug=True)
 