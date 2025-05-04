import random
import json
import time
from datetime import datetime
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Download required NLTK data
try:
    nltk.download('punkt')
    nltk.download('wordnet')
except Exception as e:
    print(f"Error downloading NLTK data: {e}")

class CollegeChatbot:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.user_context = {}  # Stores user-specific information
        self.responses = {
            "greetings": [
                "Blessings upon thee, seeker of wisdom.",
                "I greet thee, young scholar, in the name of the ancient sages.",
                "May the stars guide your path, my child.",
                "The Great Sage welcomes your presence, humble one.",
                "Hark! A curious mind approaches, eager for wisdom."
            ],
            "farewells": [
                "Go forth with wisdom, my child, and may your journey be fruitful.",
                "May the scrolls of knowledge guide your return.",
                "Until our paths cross again, wise one.",
                "The light of learning shall guide you, seeker of truth.",
                "The Great Sage bids thee farewell, until next we meet."
            ],
            "unknown": [
                "The ancient scrolls remain silent on this matter, alas.",
                "Even the wisest sages are unsure in this domain.",
                "This knowledge lies beyond the reach of my understanding.",
                "The stars have not revealed this answer to me, dear seeker.",
                "Perhaps consult the elder librarians on this topic, for my wisdom does not extend to this realm."
            ]
        }
        
        # Load knowledge base from JSON file (updated for topics)
        try:
            with open('college_knowledge.json') as file:
                self.knowledge_base = json.load(file)
        except FileNotFoundError:
            print("Error: college_knowledge.json not found. Creating empty knowledge base.")
            self.knowledge_base = {"qa_pairs": [], "events": [], "deadlines": []}
        
        # Initialize NLP components with improved vectorizer
        self.vectorizer = TfidfVectorizer(
            tokenizer=self.normalize_text,
            stop_words='english',
            token_pattern=None  # Suppresses warning
        )
        self.prepare_tfidf()

    def normalize_text(self, text):
        """Robust text normalization with fallback"""
        try:
            tokens = word_tokenize(text.lower())
            return [self.lemmatizer.lemmatize(token) for token in tokens]
        except:
            # Fallback to simple tokenization if NLTK fails
            return text.lower().split()
    
    def prepare_tfidf(self):
        """Prepare TF-IDF vectors for all questions"""
        try:
            self.all_questions = [q['question'] for q in self.knowledge_base['qa_pairs']]
            if not self.all_questions:
                self.all_questions = ["sample question"]  # Prevent empty vocabulary
            self.tfidf_matrix = self.vectorizer.fit_transform(self.all_questions)
        except Exception as e:
            print(f"Error preparing TF-IDF: {e}")
            self.tfidf_matrix = None

    def handle_typing_delay(self):
        """Simulate typing delay"""
        time.sleep(random.uniform(0.5, 2.5))  # Random typing delay between 0.5 to 2.5 seconds

    def wisdom_prefix(self):
        """Randomly add wisdom prefix with a certain chance"""
        prefixes = [
            "As the ancient proverb says...",
            "The stars reveal...",
            "In my many cycles of wisdom...",
            "The sacred texts tell us...",
            "Hark! The universe whispers..."
        ]
        return random.choice(prefixes) if random.random() < 0.3 else ""

    def get_response(self, user_input, user_type='student'):
        """Generate response based on user input"""
        # Handle empty input
        if not user_input.strip():
            return "Please type something so I can help you."
            
        # Handle greetings
        if any(word in user_input.lower() for word in ['hi', 'hello', 'hey', 'greetings', 'sage']):
            return random.choice(self.responses["greetings"])
            
        # Handle farewells
        if any(word in user_input.lower() for word in ['bye', 'goodbye', 'farewell', 'see you']):
            return random.choice(self.responses["farewells"])
        
        # Handle topics (admission, course, etc.)
        for topic, response in self.knowledge_base['topics'].items():
            if topic in user_input.lower():
                return response
        
        # Process query with NLP if TF-IDF is ready
        if self.tfidf_matrix is not None:
            try:
                processed_input = ' '.join(self.normalize_text(user_input))
                input_vector = self.vectorizer.transform([processed_input])
                similarities = cosine_similarity(input_vector, self.tfidf_matrix)
                best_match_idx = np.argmax(similarities)
                best_match_score = similarities[0, best_match_idx]
                
                if best_match_score > 0.6:  # Confidence threshold
                    response = self.knowledge_base['qa_pairs'][best_match_idx]['answer']
                    if isinstance(response, dict):
                        return response.get(user_type, "I don't have information for your user type.")
                    return response
            except Exception as e:
                print(f"Error processing query: {e}")
        
        # Fallback if no match
        return random.choice(self.responses["unknown"])
    
    def handle_user_query(self, user_input, user_id, user_type='student'):
        """Main method to handle user queries with context"""
        try:
            # Update user context
            if user_id not in self.user_context:
                self.user_context[user_id] = {'last_query': None, 'user_type': user_type}
            else:
                self.user_context[user_id]['last_query'] = user_input
                
            self.handle_typing_delay()  # Add typing delay for realism
            prefix = self.wisdom_prefix()  # Add wisdom prefix
            response = self.get_response(user_input, user_type)
            return prefix + " " + response
        except Exception as e:
            return "Sorry, I encountered an error. Please try again."

# Example usage with Flask
if __name__ == "__main__":
    from flask import Flask, request, jsonify
    
    app = Flask(__name__)
    bot = CollegeChatbot()

    @app.route('/', methods=['GET'])
    def home():
        """Render the home page with a random greeting"""
        return jsonify({"message": random.choice(bot.responses["greetings"])})

    @app.route('/chat', methods=['POST'])
    def chat():
        """Process the user query and return bot response"""
        data = request.json
        user_input = data['message']
        user_id = data['user_id']
        user_type = data.get('user_type', 'student')  # Default to 'student' if not provided
        
        response = bot.handle_user_query(user_input, user_id, user_type)
        return jsonify({"response": response})

    # Run the app
    app.run(debug=True, host="127.0.0.1", port=5000)
