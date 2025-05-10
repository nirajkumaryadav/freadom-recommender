import json
import numpy as np
import pandas as pd
from database import get_user_data, get_all_content
from text_analyzer import analyze_text_complexity
from vocabulary_analyzer import assess_vocabulary_difficulty

# Try to use simplified analyzer first, fall back to semantic_analyzer if not available
try:
    from simple_analyzer import calculate_semantic_similarity, get_current_model
    print("Using simplified analyzer for recommendations")
except ImportError:
    try:
        from semantic_analyzer import calculate_semantic_similarity, get_current_model
        print("Using semantic analyzer for recommendations")
    except ImportError:
        print("Warning: No semantic analyzer available. Using dummy similarity function.")
        
        def calculate_semantic_similarity(user_interests, content_items):
            """Dummy similarity function that returns 0.5 for all items"""
            print("Using dummy similarity function")
            return [0.5] * len(content_items)
        
        def get_current_model():
            """Dummy function for model name"""
            return "dummy"

def recommend_content(user_id, n_recommendations=3):
    """Generate personalized content recommendations"""
    user = get_user_data(user_id)
    
    if user is None:
        return {"error": "User not found"}
    
    all_content = get_all_content()
    
    # Filter out already read content
    unread_content = all_content[~all_content['id'].isin(user['history'])]
    
    if unread_content.empty:
        return {"message": "No new content available"}
    
    # Convert DataFrame to list of dicts for processing
    content_items = unread_content.to_dict('records')
    
    # Calculate reading level appropriateness
    # Target slightly above user's current level to encourage growth (but not too much)
    target_level = min(5.0, user['reading_level'] * 1.1)
    level_scores = 1 - (np.abs(unread_content['reading_level'] - target_level) / 5)
      # Calculate interest match using semantic similarity with the currently selected model
    from semantic_analyzer import calculate_semantic_similarity, get_current_model
    interest_scores = calculate_semantic_similarity(user['interests'], content_items)
    print(f"Using {get_current_model()} model for semantic similarity")
    
    # Calculate popularity score (normalized)
    popularity_scores = unread_content['popularity'] / unread_content['popularity'].max()
    
    # Combine scores with weights
    # 60% interest match, 30% reading level appropriateness, 10% popularity
    final_scores = (0.6 * np.array(interest_scores) + 
                   0.3 * np.array(level_scores) + 
                   0.1 * np.array(popularity_scores))
    
    # Add scores to DataFrame - using .loc to avoid the SettingWithCopyWarning
    unread_content.loc[:, 'recommendation_score'] = final_scores
    
    # Get top recommendations
    recommendations = unread_content.sort_values('recommendation_score', ascending=False).head(n_recommendations)
    
    # Format results with explanation
    result = []
    for i, (index, rec) in enumerate(recommendations.iterrows()):
        try:
            # Find the index in unread_content that corresponds to this recommendation
            # This is the actual index in the DataFrame, not the content ID
            content_mask = unread_content['id'] == rec['id']
            if not any(content_mask):
                raise ValueError(f"Content ID {rec['id']} not found in unread_content")
                
            # Get the index position (row number) in the unread_content DataFrame
            content_index = content_mask.idxmax()
            
            # Calculate how much each factor contributed using the DataFrame index
            interest_contribution = 0.6 * interest_scores[content_mask.tolist().index(True)]
            level_contribution = 0.3 * level_scores[content_mask.tolist().index(True)]  
            popularity_contribution = 0.1 * popularity_scores[content_mask.tolist().index(True)]
            
            # Format as percentage of total score
            total = interest_contribution + level_contribution + popularity_contribution
            interest_pct = round(interest_contribution / total * 100)
            level_pct = round(level_contribution / total * 100)
            popularity_pct = round(popularity_contribution / total * 100)
            
            result.append({
                'id': int(rec['id']),
                'title': rec['title'],
                'author': rec['author'],
                'genre': rec['genre'],
                'reading_level': float(rec['reading_level']),
                'age_range': rec['age_range'],
                'topics': rec['topics'],
                'recommendation_score': float(rec['recommendation_score']),
                'match_reason': {
                    'interest_match': interest_pct,
                    'reading_level_match': level_pct,
                    'popularity': popularity_pct
                }
            })
        except (ValueError, IndexError, KeyError) as e:
            # Fallback with default contribution percentages if we can't calculate them
            print(f"Error calculating match reasons for content {rec['id']}: {e}")
            result.append({
                'id': int(rec['id']),
                'title': rec['title'],
                'author': rec['author'],
                'genre': rec['genre'],
                'reading_level': float(rec['reading_level']),
                'age_range': rec['age_range'],
                'topics': rec['topics'],
                'recommendation_score': float(rec['recommendation_score']),
                'match_reason': {
                    'interest_match': 60,
                    'reading_level_match': 30,
                    'popularity': 10
                }
            })
    
    return result

def analyze_reading_history(user_id):
    """Analyze user's reading history and progress"""
    user = get_user_data(user_id)
    
    if user is None:
        return {"error": "User not found"}
    
    if not user['history']:
        return {"message": "No reading history available"}
    
    # Get all content read by user
    from database import get_content_by_ids
    history = get_content_by_ids(user['history'])
    
    if history.empty:
        return {"message": "No reading history available"}
    
    # Calculate reading progress metrics
    avg_level = history['reading_level'].mean()
    reading_trend = []
    
    # Sort history by complexity to see progression
    sorted_history = history.sort_values('reading_level')
    
    # Extract topics of interest based on reading history
    all_topics = []
    for topics in history['topics']:
        all_topics.extend(topics)
    
    from collections import Counter
    topic_counter = Counter(all_topics)
    top_topics = [item[0] for item in topic_counter.most_common(5)]
    
    return {
        "reading_level": float(user['reading_level']),
        "average_content_level": float(avg_level),
        "progress_trend": float(user['reading_level'] - avg_level),  # Positive if improving
        "books_read": len(user['history']),
        "favorite_topics": top_topics,
        "history": sorted_history[['id', 'title', 'reading_level']].to_dict('records')
    }

if __name__ == "__main__":
    # Test function
    print(recommend_content(1, 2))