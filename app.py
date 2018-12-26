import os
from flask import Flask

# What config we using?
print(os.environ['APP_SETTINGS'])

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])


@app.route('/')
def home():
    return "Fantasy Dashboard"

@app.route('/<name>')
def home_name(name):
    return "Welcome back {}!".format(name)

if __name__ == "__main__":
    app.run()
