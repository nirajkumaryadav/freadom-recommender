from flask import Flask, request, jsonify
from recommendation_engine import recommend_content, analyze_reading_history
from text_analyzer import analyze_text_complexity, extract_topics
import database

# Import the simplified analyzer instead of the full semantic analyzer
import sys
import os
print("Current working directory:", os.getcwd())
# Add simplified analyzer module
try:
    import simple_analyzer
    print("Successfully imported simple_analyzer")
except ImportError as e:
    print(f"Error importing simple_analyzer: {e}")

app = Flask(__name__)

@app.route('/api/setup', methods=['GET'])
def setup_database():
    """Initialize the database with sample data"""
    database.create_database()
    return jsonify({"message": "Database initialized successfully"})

@app.route('/api/recommend/<int:user_id>', methods=['GET'])
def get_recommendations(user_id):
    """Get content recommendations for a user"""
    count = request.args.get('count', default=3, type=int)
    recommendations = recommend_content(user_id, n_recommendations=count)
    return jsonify(recommendations)

@app.route('/api/analyze', methods=['POST'])
def analyze_text():
    """Analyze text complexity and extract topics"""
    data = request.json
    if 'text' not in data:
        return jsonify({"error": "No text provided"}), 400
    
    analysis = analyze_text_complexity(data['text'])
    topics = extract_topics(data['text'])
    
    return jsonify({
        "analysis": analysis,
        "topics": topics
    })

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get list of all users"""
    users = database.get_users().to_dict('records')
    return jsonify(users)

@app.route('/api/user/<int:user_id>/progress', methods=['GET'])
def get_user_progress(user_id):
    """Get reading progress for a user"""
    progress = analyze_reading_history(user_id)
    return jsonify(progress)

@app.route('/api/user/<int:user_id>/read/<int:content_id>', methods=['POST'])
def mark_as_read(user_id, content_id):
    """Mark content as read by user"""
    success = database.update_user_history(user_id, content_id)
    
@app.route('/api/settings/model', methods=['POST'])
def set_semantic_model():
    """Set the semantic model to use for recommendations"""
    from semantic_analyzer import set_model, get_current_model
    
    data = request.json
    if 'model' not in data:
        return jsonify({
            "error": "No model specified",
            "current_model": get_current_model()
        }), 400
    
    model_name = data['model']
    if set_model(model_name):
        return jsonify({
            "message": f"Model set to {get_current_model()} successfully",
            "current_model": get_current_model()
        })
    else:
        return jsonify({
            "error": f"Failed to set model to {model_name}",
            "current_model": get_current_model()
        }), 500
        
@app.route('/api/settings/model', methods=['GET'])
def get_semantic_model():
    """Get the current semantic model being used for recommendations"""
    from semantic_analyzer import get_current_model
    
    return jsonify({
        "current_model": get_current_model()
    })

@app.route('/api/user/<int:user_id>/read/<int:content_id>', methods=['POST'])
def mark_content_read(user_id, content_id):
    """Mark content as read by user"""
    success = database.update_user_history(user_id, content_id)
    
    if success:
        return jsonify({"message": f"Content {content_id} marked as read by user {user_id}"})
    else:
        return jsonify({"error": "Failed to update reading history"}), 400

@app.route('/api/setup/models', methods=['GET'])
def setup_models():
    """Download and setup AI models"""
    try:
        # Import here to avoid circular imports
        from semantic_analyzer import load_sbert_model, load_qwen_model
        
        # Try to load both models
        sbert_success = load_sbert_model()
        qwen_success = load_qwen_model()
        
        if sbert_success and qwen_success:
            return jsonify({"message": "Both SBERT and Qwen models loaded successfully"})
        elif sbert_success:
            return jsonify({"message": "SBERT model loaded successfully, but Qwen model failed"})
        elif qwen_success:
            return jsonify({"message": "Qwen model loaded successfully, but SBERT model failed"})
        else:
            return jsonify({"error": "Failed to load both models"}), 500
    except Exception as e:
        return jsonify({"error": f"Error loading models: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)