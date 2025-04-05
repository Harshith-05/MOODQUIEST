"""
app.py

A MoodQuest chatbot application with an attractive animated green-black gradient
background, a modern, centered chatbot UI, emoji-enhanced elements, voice output,
voice input, and additional mini-game features.
"""

import os
import asyncio
import random
from flask import Flask, render_template_string, request, redirect, url_for, session, send_from_directory
from typing import Dict, List, Tuple

# ---------------------------
# MoodQuest Game Mechanic
# ---------------------------

class MoodQuestGame:
    """
    Implements the game mechanics for MoodQuest:
    - Tracks progress and selects challenges.
    - Provides unique responses, rewards, and additional mini-game prompts.
    """
    def __init__(self, config: Dict):
        self.config = config
        self.challenges = self._load_challenges()
        self.rewards = self._load_rewards()
        
    def _load_challenges(self) -> List[Dict]:
        return [
            {
                'id': 'self_reflection',
                'name': 'Mirror of Emotions',
                'description': 'Reflect on a recent emotional experience',
                'prompt': 'Think about a recent situation that affected your mood. What emotions did you feel?',
                'difficulty': 1
            },
            {
                'id': 'emotion_exploration',
                'name': 'Emotional Compass',
                'description': 'Explore the nuances of your emotions',
                'prompt': 'If your current emotion was a color, what would it be and why?',
                'difficulty': 2
            },
            {
                'id': 'growth_mindset',
                'name': 'Garden of Growth',
                'description': 'Cultivate a growth mindset',
                'prompt': "What's one small step you could take today to improve your mood?",
                'difficulty': 2
            }
        ]
        
    def _load_rewards(self) -> Dict[str, Dict]:
        return {
            'insight_gem': {
                'name': 'Insight Gem 💎',
                'description': 'A crystal containing a personal insight',
                'value': 10
            },
            'mood_mastery': {
                'name': 'Mood Master Badge 🏅',
                'description': 'Recognition of emotional awareness',
                'value': 20
            },
            'wisdom_scroll': {
                'name': 'Wisdom Scroll 📜',
                'description': 'Contains collected emotional wisdom',
                'value': 15
            }
        }
        
    async def process_turn(self, user_input: str, game_state: Dict) -> Tuple[str, Dict]:
        # Update progress based on user engagement
        progress = game_state.get('progress', 0)
        progress += 1
        game_state['progress'] = progress
        
        # Generate the standard challenge response
        challenge = self._select_challenge(game_state)
        response = self._generate_response(user_input, challenge, game_state)
        
        # Randomly trigger an extra mini-game (30% chance)
        mini_game_prompt = self._maybe_trigger_minigame()
        if mini_game_prompt:
            response += f"\n\nMini-Game: {mini_game_prompt}"
        
        # Grant a reward every 3 turns
        if self._check_reward_condition(game_state):
            reward = self._grant_reward(game_state)
            response += f"\n\n🎉 You've earned a {reward['name']}!\n{reward['description']}"
            
        return response, game_state
        
    def _select_challenge(self, game_state: Dict) -> Dict:
        progress = game_state.get('progress', 0)
        # Ensure difficulty is at least 1 to match available challenges
        difficulty = min(max(progress // 3, 1), 2)
        suitable_challenges = [c for c in self.challenges if c['difficulty'] <= difficulty]
        if not suitable_challenges:
            suitable_challenges = self.challenges
        # Cycle through challenges based on progress
        return suitable_challenges[progress % len(suitable_challenges)]
        
    def _generate_response(self, user_input: str, challenge: Dict, game_state: Dict) -> str:
        # Define various sentiment responses
        positive_responses = [
            "It's wonderful to see you're feeling positive! 😊",
            "Great vibes coming through! 😄",
            "Your positive energy is contagious! 😎"
        ]
        negative_responses = [
            "I'm sorry you're feeling down. Remember, it's okay to have tough moments. 💙",
            "It sounds like a rough day. I'm here for you. 🤗",
            "Take it easy—sometimes we all need a break. 💜"
        ]
        neutral_responses = [
            "Thanks for sharing your thoughts. 🤗",
            "I appreciate you opening up. 😊",
            "Thanks for trusting me with your thoughts. 😌"
        ]
        
        lower_input = user_input.lower()
        if any(word in lower_input for word in ["happy", "joy", "excited", "great", "good"]):
            sentiment_comment = random.choice(positive_responses)
        elif any(word in lower_input for word in ["sad", "unhappy", "depressed", "tired", "angry", "upset"]):
            sentiment_comment = random.choice(negative_responses)
        else:
            sentiment_comment = random.choice(neutral_responses)
        
        # Define different introduction phrases for the challenge
        if game_state.get('progress', 0) == 1:
            intro_phrases = [
                f"Welcome to your first challenge: {challenge['name']}! 🎮",
                f"Let's begin! Your challenge is: {challenge['name']}! 🚀",
                f"Starting off strong! Here's your challenge: {challenge['name']}! 💡"
            ]
        else:
            intro_phrases = [
                f"You're doing great! Next up: {challenge['name']}! 🔥",
                f"Keep it up! Here's your next challenge: {challenge['name']}! 🌟",
                f"Awesome progress! Ready for: {challenge['name']}? 🎯"
            ]
        
        intro_phrase = random.choice(intro_phrases)
        return f"{sentiment_comment}\n\n{intro_phrase}\n{challenge['prompt']}"
        
    def _maybe_trigger_minigame(self) -> str:
        # 30% chance to trigger a mini-game prompt
        if random.random() < 0.3:
            mini_games = [self._never_have_i_ever, self._quick_trivia]
            return random.choice(mini_games)()
        return ""
        
    def _never_have_i_ever(self) -> str:
        prompts = [
            "Never have I ever stayed up all night gaming. Have you? 🎮",
            "Never have I ever skipped breakfast. How about you? 🍳",
            "Never have I ever laughed so hard I cried. Has it happened to you? 😂"
        ]
        return random.choice(prompts)
    
    def _quick_trivia(self) -> str:
        trivia = [
            "Quick Trivia: What is the color of the sky on a clear day? 🌤️",
            "Quick Trivia: Which animal is known as man's best friend? 🐶",
            "Quick Trivia: How many continents are there on Earth? 🌍"
        ]
        return random.choice(trivia)
        
    def _check_reward_condition(self, game_state: Dict) -> bool:
        progress = game_state.get('progress', 0)
        return progress > 0 and progress % 3 == 0
        
    def _grant_reward(self, game_state: Dict) -> Dict:
        progress = game_state.get('progress', 0)
        reward_index = (progress // 3) % len(self.rewards)
        reward_id = list(self.rewards.keys())[reward_index]
        return self.rewards[reward_id]

# ---------------------------
# Flask Application
# ---------------------------

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a secure secret key

# Route to serve favicon
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

# Instantiate the game mechanic
mood_game = MoodQuestGame(config={})

# HTML Template with an attractive green-black animated gradient background,
# a modern chatbot UI with emoji-enhanced elements, voice output, and voice input.
TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>MoodQuest Chatbot 🤖</title>
  <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
  <style>
    /* Full-screen animated green-black gradient background */
    body, html {
      height: 100%;
      margin: 0;
      font-family: 'Arial', sans-serif;
      background: linear-gradient(45deg, #003300, #000000, #002200, #000000);
      background-size: 400% 400%;
      animation: gradientBG 15s ease infinite;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    @keyframes gradientBG {
      0% { background-position: 0% 50%; }
      50% { background-position: 100% 50%; }
      100% { background-position: 0% 50%; }
    }
    /* Chat container styling */
    .chat-container {
      background-color: rgba(255, 255, 255, 0.95);
      border-radius: 15px;
      box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
      width: 90%;
      max-width: 500px;
      padding: 20px;
      overflow: hidden;
    }
    .chat-header {
      text-align: center;
      margin-bottom: 10px;
      font-size: 1.8em;
      font-weight: bold;
      color: #333;
    }
    .chat-box {
      border: 1px solid #ccc;
      border-radius: 10px;
      padding: 15px;
      height: 300px;
      overflow-y: auto;
      background-color: #f8f8f8;
      margin-bottom: 15px;
    }
    .message {
      margin-bottom: 10px;
      word-wrap: break-word;
    }
    .message.user {
      text-align: right;
      color: #333;
    }
    .message.ai {
      text-align: left;
      color: #0077ff;
    }
    .input-group {
      margin-bottom: 10px;
    }
    .reset-btn {
      width: 100%;
    }
  </style>
</head>
<body>
  <div class="chat-container">
    <div class="chat-header">MoodQuest Chatbot 🤖</div>
    <div class="chat-box">
      {% for msg in history %}
        <div class="message {% if msg.sender == 'User' %}user{% else %}ai{% endif %}">
          <strong>{{ msg.sender }}:</strong> <span>{{ msg.message }}</span>
        </div>
      {% endfor %}
    </div>
    <form method="post">
      <div class="input-group">
        <input type="text" class="form-control" name="user_input" placeholder="Type or speak your message... 😀" required>
        <div class="input-group-append">
          <button type="button" class="btn btn-secondary" id="mic-btn">🎤</button>
          <button type="submit" class="btn btn-primary">Send 🚀</button>
        </div>
      </div>
    </form>
    <form method="get">
      <button type="submit" class="btn btn-danger reset-btn" formaction="{{ url_for('reset') }}">Reset Chat 🔄</button>
    </form>
  </div>

  <!-- JavaScript for voice output using the Web Speech API -->
  <script>
    function speakLastResponse() {
      const aiMessages = document.querySelectorAll('.message.ai span');
      if (aiMessages.length > 0) {
        const lastMsg = aiMessages[aiMessages.length - 1].innerText;
        const utterance = new SpeechSynthesisUtterance(lastMsg);
        utterance.lang = 'en-US';
        utterance.volume = 1;
        utterance.rate = 1;
        utterance.pitch = 1;
        window.speechSynthesis.speak(utterance);
      }
    }
    // Speak the last response after page load with a slight delay
    window.onload = function() {
      setTimeout(speakLastResponse, 1000);
    };
  </script>

  <!-- JavaScript for voice input using the Web Speech API -->
  <script>
    const micBtn = document.getElementById("mic-btn");
    const userInputField = document.querySelector('input[name="user_input"]');

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'en-US';

      micBtn.addEventListener("click", function() {
        recognition.start();
        micBtn.innerText = "🎤 Listening...";
      });

      recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        userInputField.value = transcript;
        micBtn.innerText = "🎤";
      };

      recognition.onerror = function(event) {
        console.error("Speech recognition error:", event.error);
        micBtn.innerText = "🎤";
      };
    } else {
      micBtn.style.display = "none";
    }
  </script>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    if "history" not in session:
        session["history"] = []
    if "game_state" not in session:
        session["game_state"] = {"progress": 0}
    
    history = session["history"]
    game_state = session["game_state"]
    
    if request.method == "POST":
        user_input = request.form.get("user_input")
        if user_input:
            # Add user's message to conversation history
            history.append({"sender": "User", "message": user_input})
            # Process turn using game mechanics
            response, game_state = asyncio.run(mood_game.process_turn(user_input, game_state))
            history.append({"sender": "MoodQuest", "message": response})
            session["game_state"] = game_state
            session["history"] = history
            return redirect(url_for("index"))
    
    return render_template_string(TEMPLATE, history=history)

@app.route("/reset")
def reset():
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
