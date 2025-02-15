# AI Chatbot

A modern Flask-based AI chatbot that uses the OpenAI API to provide intelligent responses. Features a clean, responsive UI inspired by ChatGPT with chat history management and markdown support.

## Features

- 🤖 OpenAI GPT-3.5 Turbo Integration
- 💾 Persistent chat history with SQLite
- 🔑 Secure API key management
- 🎨 Modern, responsive UI with Bootstrap 5
- 📱 Mobile-friendly design
- ✨ Real-time loading indicators
- 📝 Markdown formatting support
- 🔄 Chat context retention (last 10 messages)
- 🗑️ Chat management (create, view, delete)

## Setup

1. **Clone the repository**

```bash
git clone https://github.com/unknownTheFirst/AI-chat-website-.git
cd AI-chat-website-
```

2. **Create a virtual environment**

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Unix/MacOS
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Create a .env file**

```env
SECRET_KEY=your-secret-key-here  # For Flask session encryption
```

5. **Initialize the database**

```bash
python main.py
```

6. **Access the application**

- Open your browser and navigate to `http://localhost:5000`
- Enter your OpenAI API key when prompted
- Start chatting!

## Project Structure

```
.
├── main.py                 # Main application file
├── requirements.txt        # Project dependencies
├── .env                    # Environment variables
├── chatbot.db             # SQLite database
├── static/                # Static files
│   ├── css/              # CSS styles
│   │   └── style.css     # Custom styling
├── templates/             # HTML templates
│   ├── api_key_form.html # API key input form
│   ├── base.html         # Base template
│   ├── chat.html         # Chat interface
│   ├── confirm_delete.html# Delete confirmation
│   └── home.html         # Home page
```

## Features in Detail

### Chat Management

- Create new chats
- View chat history
- Delete conversations
- Automatic chat titling based on first message

### Security

- Secure API key storage in session
- CSRF protection
- Input validation
- Error handling for API issues

### UI Features

- Dark theme
- Loading indicators
- Responsive design
- Message history
- Easy navigation

## Technical Details

- **Framework**: Flask 3.0.2
- **Database**: SQLite with SQLAlchemy
- **Frontend**: Bootstrap 5 with custom CSS
- **API**: OpenAI GPT-3.5 Turbo
- **Authentication**: Session-based API key storage

## Requirements

- Python 3.8+
- OpenAI API key
- Modern web browser
- Internet connection

## Error Handling

The application handles various error cases:

- Invalid API keys
- Rate limiting
- Quota exceeded
- Network issues
- Invalid inputs

## Important Notes Before Running

1. **API Key Security**:

   - Never commit your OpenAI API key
   - Keep your `.env` file private
   - Don't share your `chatbot.db` file

2. **First Time Setup**:
   - Create a new `.env` file (it's not included in the repository)
   - Generate a new `SECRET_KEY` for your Flask application
   - The database will be created automatically on first run

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

Copyright © 2025 Ankith. All rights reserved.

## Acknowledgments

- OpenAI for the GPT-3.5 API
- Flask and its extensions
- Bootstrap for the UI framework
