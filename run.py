from flask import Flask, render_template, request, redirect, url_for, send_from_directory, make_response, session, flash
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# In-memory storage for simplicity (replace with a database in production)

# Load users from a JSON file
with open('users.json', 'r') as f:
    users = json.load(f)

sessions = {}

@app.route('/')
def home():
    return redirect("/gallery")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            # Generate a session ID
            session_id = os.urandom(16).hex()
            sessions[session_id] = username

            # Set the session cookie
            response = make_response(redirect(url_for('gallery')))
            response.set_cookie('session_id', session_id)
            return response
        else:
            flash('Invalid credentials', 'error')
    else:
        flash('Please log in to continue', 'info')
    return render_template('login.html')

@app.route('/gallery')
def gallery():
    # Check if the user is logged in by verifying the session cookie
    session_id = request.cookies.get('session_id')
    if session_id not in sessions:
        return redirect(url_for('login'))

    # Get a list of all image files in the new img directory
    images = os.listdir('img')
    # Filter out non-image files if necessary (e.g., .DS_Store on macOS)
    images = [img for img in images if os.path.splitext(img)[1].lower() in ['.jpg', '.jpeg', '.png', '.gif']]
    return render_template('gallery.html', images=images)

@app.route('/logout')
def logout():
    # Clear the session cookie
    response = make_response(redirect(url_for('login')))
    response.set_cookie('session_id', '', expires=0)
    return response

@app.route('/img/<path:filename>')
def custom_static(filename):
    session_id = request.cookies.get('session_id')
    if session_id not in sessions:
        return redirect(url_for('login'))
    # Serve static files from the default static directory or img directory

    return send_from_directory('img', filename)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')