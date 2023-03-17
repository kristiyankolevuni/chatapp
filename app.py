import time
import redis
from flask import Flask, request

app = Flask(__name__)
cache = redis.Redis(host='redis', port=6379)

def get_message_history():
    messages = []
    # Iterate through all keys starting with 'message:'
    for key in cache.scan_iter("message:*"):
        message = cache.get(key)
        if message is not None:
            # Decode the message from bytes to a string
            message = message.decode('utf-8')
            messages.append(message)
    # Return messages in reverse order (newest first)
    return messages[::-1]

def add_message(username, message):
    # Generate a unique ID for the message
    message_id = cache.incr('message_id')
    # Store the message in Redis with a key of 'message:<id>'
    cache.set('message:{}'.format(message_id), '{}: {}'.format(username, message))

@app.route('/', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        # Get the username and message from the form
        username = request.form['username']
        message = request.form['message']
        # Add the message to the chat history
        add_message(username, message)
    # Get the chat history
    messages = get_message_history()
    # Render the chat page with the chat history and a form to send messages
    return """
        <html>
            <head>
                <title>Flask Chat</title>
            </head>
            <body>
                <h1>Flask Chat</h1>
                <div>
                    <h2>Chat History</h2>
                    <ul>
                        {}
                    </ul>
                </div>
                <div>
                    <h2>Send Message</h2>
                    <form method="post">
                        <label for="username">Username:</label>
                        <input type="text" id="username" name="username" required><br>
                        <label for="message">Message:</label>
                        <textarea id="message" name="message" rows="5" cols="50" required></textarea><br>
                        <input type="submit" value="Send">
                    </form>
                </div>
            </body>
        </html>
    """.format('\n'.join('<li>{}</li>'.format(message) for message in messages))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
