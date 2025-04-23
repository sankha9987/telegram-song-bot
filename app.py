from flask import Flask

# Create a Flask application
app = Flask(_name_)

# Define a route for the homepage
@app.route('/')
def hello_world():
    return 'This bot is made by @SrijanMajumdar and currently it hosted and live for everyone'

# Run the application
if _name_ == '_main_':
    app.run()
