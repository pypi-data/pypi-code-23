from flask import Flask


app = Flask(__name__)


@app.route("/")
def hello():
	return "Hello, World!"


def hello():
	print("Hello, world")
	

def get_hello():
	return "Hello, World"
	
	
def run_server():
	app.run()