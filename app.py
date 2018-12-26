from flask import Flask
app = Flask(__name__)


@app.route('/')
def home():
    return "Fantasy Dashboard"

@app.route('/<name>')
def home_name(name):
    return "Welcome back {}!".format(name)

if __name__ == "__main__":
    app.run()
