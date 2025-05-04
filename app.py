from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for
from chatbot import CollegeChatbot
import time
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)
chatbot = CollegeChatbot()

# Dark theme HTML templates
BASE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Great Sage - {title}</title>
    <style>
        :root {{
            --primary: #6c5ce7;
            --secondary: #a29bfe;
            --dark: #1e272e;
            --darker: #171e24;
            --light: #f5f6fa;
            --gray: #808e9b;
            --success: #00b894;
            --warning: #fdcb6e;
            --danger: #d63031;
        }}
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}
        body {{
            background-color: var(--dark);
            color: var(--light);
            min-height: 100vh;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px 0;
            border-bottom: 1px solid var(--gray);
            margin-bottom: 30px;
        }}
        .logo {{
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 1.5rem;
            font-weight: bold;
            color: var(--primary);
        }}
        .logo img {{
            width: 40px;
            height: 40px;
        }}
        nav ul {{
            display: flex;
            gap: 20px;
            list-style: none;
        }}
        nav a {{
            color: var(--light);
            text-decoration: none;
            transition: color 0.3s;
            font-weight: 500;
        }}
        nav a:hover {{
            color: var(--primary);
        }}
        .active {{
            color: var(--primary) !important;
            border-bottom: 2px solid var(--primary);
        }}
        .chat-container {{
            background: var(--darker);
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            overflow: hidden;
            height: 70vh;
            display: flex;
            flex-direction: column;
            margin-bottom: 20px;
        }}
        .chat-header {{
            background: var(--primary);
            color: white;
            padding: 15px;
            text-align: center;
            font-size: 1.2rem;
        }}
        #chatWindow {{
            flex: 1;
            padding: 15px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}
        .user-message {{
            align-self: flex-end;
            background: var(--primary);
            color: white;
            padding: 10px 15px;
            border-radius: 18px 18px 0 18px;
            max-width: 70%;
        }}
        .bot-message {{
            align-self: flex-start;
            background: var(--gray);
            padding: 10px 15px;
            border-radius: 18px 18px 18px 0;
            max-width: 70%;
        }}
        .chat-input {{
            display: flex;
            padding: 10px;
            border-top: 1px solid var(--gray);
        }}
        #userInput {{
            flex: 1;
            padding: 12px 15px;
            background: var(--darker);
            border: 1px solid var(--gray);
            border-radius: 20px;
            outline: none;
            color: var(--light);
        }}
        #sendButton {{
            margin-left: 10px;
            padding: 12px 25px;
            background: var(--primary);
            color: white;
            border: none;
            border-radius: 20px;
            cursor: pointer;
            transition: background 0.3s;
        }}
        #sendButton:hover {{
            background: var(--secondary);
        }}
        .typing-indicator {{
            display: inline-flex;
            gap: 5px;
            padding: 10px;
            background: var(--gray);
            border-radius: 18px;
        }}
        .typing-dot {{
            width: 8px;
            height: 8px;
            background: var(--light);
            border-radius: 50%;
            animation: typing 1.4s infinite ease-in-out;
        }}
        .dashboard-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }}
        .card {{
            background: var(--darker);
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        }}
        .card h3 {{
            color: var(--primary);
            margin-bottom: 15px;
        }}
        footer {{
            text-align: center;
            padding: 20px;
            margin-top: 50px;
            border-top: 1px solid var(--gray);
            color: var(--gray);
        }}
        @keyframes typing {{
            0%, 60%, 100% {{ transform: translateY(0); }}
            30% {{ transform: translateY(-5px); }}
        }}
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
</head>
<body>
    <div class="container">
        <header>
            <div class="logo">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z" fill="#6c5ce7"/>
                    <path d="M12 6c-3.31 0-6 2.69-6 6s2.69 6 6 6 6-2.69 6-6-2.69-6-6-6zm0 10c-2.21 0-4-1.79-4-4s1.79-4 4-4 4 1.79 4 4-1.79 4-4 4z" fill="#a29bfe"/>
                    <path d="M12 10c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z" fill="#6c5ce7"/>
                </svg>
                <span>Great Sage</span>
            </div>
            <nav>
                <ul>
                    <li><a href="/" class="{{ 'active' if active_page == 'home' }}">Chat</a></li>
                    <li><a href="/dashboard" class="{{ 'active' if active_page == 'dashboard' }}">Dashboard</a></li>
                    <li><a href="/about" class="{{ 'active' if active_page == 'about' }}">About</a></li>
                </ul>
            </nav>
        </header>

        {content}

        <footer>
            <p>&copy; {year} Great Sage AI. All rights reserved.</p>
        </footer>
    </div>

    {scripts}
</body>
</html>
'''

CHAT_PAGE = '''
<div class="chat-container">
    <div class="chat-header">
        <h2>Great Sage College Assistant</h2>
    </div>
    <div id="chatWindow">
        <div class="bot-message">Greetings! I am the Great Sage, your wise college assistant. How may I enlighten you today?</div>
    </div>
    <div class="chat-input">
        <input type="text" id="userInput" placeholder="Ask your question..." autofocus>
        <button id="sendButton"><i class="fas fa-paper-plane"></i> Send</button>
    </div>
</div>

<script>
    const chatWindow = document.getElementById('chatWindow');
    const userInput = document.getElementById('userInput');
    const sendButton = document.getElementById('sendButton');

    function addMessage(text, isUser) {
        const messageDiv = document.createElement('div');
        messageDiv.className = isUser ? 'user-message' : 'bot-message';
        messageDiv.innerHTML = text;
        chatWindow.appendChild(messageDiv);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    function showTyping() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'bot-message';
        typingDiv.innerHTML = `
            <div class="typing-indicator">
                <div class="typing-dot" style="animation-delay: 0s"></div>
                <div class="typing-dot" style="animation-delay: 0.2s"></div>
                <div class="typing-dot" style="animation-delay: 0.4s"></div>
            </div>
        `;
        chatWindow.appendChild(typingDiv);
        chatWindow.scrollTop = chatWindow.scrollHeight;
        return typingDiv;
    }

    async function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;
        
        addMessage(message, true);
        userInput.value = '';
        
        const typingElement = showTyping();
        
        try {
            const response = await axios.post('/chat', {
                message: message,
                user_type: 'student',
                user_id: '{{ session.user_id }}'
            });
            chatWindow.removeChild(typingElement);
            addMessage(response.data.answer, false);
        } catch (error) {
            chatWindow.removeChild(typingElement);
            addMessage('Sorry, something went wrong. Please try again later.', false);
        }
    }

    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
</script>
'''

DASHBOARD_PAGE = '''
<div class="dashboard-cards">
    <div class="card">
        <h3>Recent Conversations</h3>
        <ul>
            {% for conversation in conversations %}
                <li>{{ conversation }}</li>
            {% endfor %}
        </ul>
    </div>
    <div class="card">
        <h3>User Statistics</h3>
        <p>Total Conversations: {{ stats.total_conversations }}</p>
        <p>Last Active: {{ stats.last_active }}</p>
    </div>
</div>
'''

ABOUT_PAGE = '''
<div class="card">
    <h3>About the Great Sage</h3>
    <p>The Great Sage is an AI assistant designed to help you with your college-related questions and tasks. Developed with a deep understanding of college life and academics, the Great Sage is your trusted guide throughout your academic journey.</p>
    <p>Created by Aayush Rawat, a final-year Computer Science student at Chandigarh University.</p>
</div>
'''

@app.route('/')
def home():
    session['user_id'] = str(int(time.time()))
    return render_template_string(BASE_TEMPLATE.format(
        title='Home', content=CHAT_PAGE, active_page='home', year=datetime.now().year, scripts=''
    ))

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json['message']
    user_id = request.json['user_id']
    response = chatbot.get_response(user_message)
    return jsonify(answer=response)

@app.route('/dashboard')
def dashboard():
    # Mocking user stats and conversation data
    user_stats = {
        'total_conversations': 42,
        'last_active': '2025-05-03 14:00'
    }
    conversations = ['Hello, how can I start my project?', 'What courses do I need for my degree?']
    return render_template_string(BASE_TEMPLATE.format(
        title='Dashboard', content=DASHBOARD_PAGE, active_page='dashboard', year=datetime.now().year,
        scripts='', conversations=conversations, stats=user_stats
    ))

@app.route('/about')
def about():
    return render_template_string(BASE_TEMPLATE.format(
        title='About', content=ABOUT_PAGE, active_page='about', year=datetime.now().year, scripts=''
    ))

if __name__ == '__main__':
    app.run(debug=True)
