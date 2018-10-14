from flask import Flask
app = Flask(__name__)

@app.route('/')
def home_route():
  return 'Home Route'

@app.route('/hello')
def hello_world():
  return 'Hello, from the hello route'