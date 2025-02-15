from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired
from datetime import datetime, timezone, timedelta
import os
from dotenv import load_dotenv
from openai import OpenAI
import secrets

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chatbot.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)

# Initialize extensions
db = SQLAlchemy(app)
bootstrap = Bootstrap5(app)

# Database Models
class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    messages = db.relationship('Message', backref='chat', lazy=True)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    is_bot = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)

# Forms
class MessageForm(FlaskForm):
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send')

@app.route('/')
def home():
    if 'api_key' not in session:
        return render_template('api_key_form.html')
    
    chats = Chat.query.order_by(Chat.created_at.desc()).all()
    return render_template('home.html', chats=chats)

@app.route('/submit_api_key', methods=['POST'])
def submit_api_key():
    api_key = request.form.get('api_key')
    remember = request.form.get('remember') == 'on'
    
    if not api_key:
        flash('API key is required', 'danger')
        return redirect(url_for('home'))
    
    if not api_key.startswith('sk-'):
        flash('Invalid API key format. It should start with "sk-"', 'danger')
        return redirect(url_for('home'))
    
    try:
        client = OpenAI(api_key=api_key)
        # Test the API key with a simple chat completion
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=5
        )
        
        session['api_key'] = api_key
        if remember:
            session.permanent = True
        
        flash('API key successfully verified', 'success')
        return redirect(url_for('home'))
        
    except Exception as e:
        print(f"API Key Error: {str(e)}")
        error_msg = str(e)
        if 'invalid_api_key' in error_msg:
            flash('Invalid API key. Please check your API key and try again.', 'danger')
        elif 'insufficient_quota' in error_msg:
            flash('Your API key has insufficient quota. Please check your OpenAI account.', 'danger')
        else:
            flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('home'))

@app.route('/chat/new', defaults={'chat_id': None})
@app.route('/chat/<int:chat_id>')
def chat(chat_id):
    if 'api_key' not in session:
        flash('Please enter your API key first', 'warning')
        return redirect(url_for('home'))
    
    if chat_id is None:
        chat = Chat(title="New Chat")
        db.session.add(chat)
        db.session.commit()
        return redirect(url_for('chat', chat_id=chat.id))
        
    chat = Chat.query.get_or_404(chat_id)
    form = MessageForm()
    messages = Message.query.filter_by(chat_id=chat_id).order_by(Message.timestamp).all()
    
    return render_template('chat.html', 
                         chat=chat, 
                         form=form, 
                         messages=messages)

@app.route('/chat/<int:chat_id>', methods=['POST'])
def send_message(chat_id):
    if 'api_key' not in session:
        flash('Please enter your API key first', 'warning')
        return redirect(url_for('home'))
        
    chat = Chat.query.get_or_404(chat_id)
    form = MessageForm()
    
    if form.validate_on_submit():
        user_content = form.message.data.strip()
        if not user_content:
            return redirect(url_for('chat', chat_id=chat_id))

        user_message = Message(content=user_content, is_bot=False, chat_id=chat_id)
        db.session.add(user_message)
        db.session.commit()
        
        try:
            client = OpenAI(api_key=session['api_key'])
            chat_history = Message.query.filter_by(chat_id=chat_id).order_by(Message.timestamp).all()
            
            messages = [
                {"role": "system", "content": """You are a helpful and knowledgeable AI assistant. 
                Provide clear, accurate, and detailed responses while maintaining a friendly tone.
                If you're unsure about something, admit it rather than making assumptions.
                Format your responses using Markdown when appropriate for better readability."""}
            ]
            
            for msg in chat_history[-10:]:
                role = "assistant" if msg.is_bot else "user"
                messages.append({"role": role, "content": msg.content})
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=2000,
                temperature=0.7,
                presence_penalty=0.6,
                frequency_penalty=0.5
            )
            
            bot_response = response.choices[0].message.content.strip()
            
            if len(chat_history) == 1:
                chat.title = user_content[:30] + "..." if len(user_content) > 30 else user_content
                db.session.add(chat)
            
            bot_message = Message(content=bot_response, is_bot=True, chat_id=chat_id)
            db.session.add(bot_message)
            db.session.commit()
            
        except Exception as e:
            error_message = "I apologize, but I encountered an error."
            print(f"Chat Error: {str(e)}")
            
            if "insufficient_quota" in str(e):
                error_message = "Your API key has insufficient quota. Please check your OpenAI account."
            elif "invalid_api_key" in str(e):
                error_message = "Invalid API key. Please check your API key and try again."
            elif "rate_limit" in str(e):
                error_message = "Rate limit exceeded. Please wait a moment before sending another message."
            
            bot_message = Message(content=error_message, is_bot=True, chat_id=chat_id)
            db.session.add(bot_message)
            db.session.commit()
        
        return redirect(url_for('chat', chat_id=chat_id))
    
    return redirect(url_for('chat', chat_id=chat_id))

@app.route('/delete_chat/<int:chat_id>', methods=['GET', 'POST'])
def delete_chat(chat_id):
    if request.method == 'GET':
        return render_template('confirm_delete.html', chat_id=chat_id)
    
    chat = Chat.query.get_or_404(chat_id)
    Message.query.filter_by(chat_id=chat_id).delete()
    db.session.delete(chat)
    db.session.commit()
    flash('Chat deleted successfully', 'success')
    return redirect(url_for('home'))

@app.route('/forget_api_key')
def forget_api_key():
    session.pop('api_key', None)
    flash('API key has been removed', 'info')
    return redirect(url_for('home'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
