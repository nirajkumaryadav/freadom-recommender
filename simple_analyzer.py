# A simplified semantic analyzer that doesn't require model downloads
# Use this for testing the Freadom system without Hugging Face credentials

def calculate_semantic_similarity(user_interests, content_items, model_name=None):
    """Calculate semantic similarity using keyword matching"""
    print("Using simple keyword matching for semantic similarity...")
    
    similarities = []
    
    for item in content_items:
        # Get item topics and title
        topics = item.get('topics', []) if isinstance(item.get('topics'), list) else []
        title_words = item['title'].lower().split() if 'title' in item else []
        
        # Convert user interests to lowercase set
        user_interests_lower = set(interest.lower() for interest in user_interests)
        
        # Convert item keywords to lowercase set
        item_keywords = set(topic.lower() for topic in topics).union(set(word.lower() for word in title_words))
        
        # Direct matches
        direct_matches = user_interests_lower.intersection(item_keywords)
        direct_match_score = len(direct_matches) / max(1, len(user_interests_lower))
        
        # Calculate final score with weighting
        if len(direct_matches) > 0:
            # Fantasy-related special weighting
            if "fantasy" in direct_matches and ("magic" in direct_matches or "adventure" in direct_matches):
                similarity = 0.9  # Strong match for fantasy + magic/adventure
                print(f"Item {item['id']} - STRONG match: fantasy + magic/adventure ({similarity:.2f})")
            elif "fantasy" in direct_matches or "magic" in direct_matches or "adventure" in direct_matches:
                similarity = 0.75  # Good match for fantasy or magic or adventure
                print(f"Item {item['id']} - GOOD match: fantasy OR magic OR adventure ({similarity:.2f})")
            else:
                similarity = 0.5 + (0.4 * direct_match_score)  # Basic match based on proportion
                print(f"Item {item['id']} - BASIC match: {len(direct_matches)} keywords ({similarity:.2f})")
        else:
            # Related topic matching (indirect matches)
            fantasy_keywords = {"wizard", "dragon", "magical", "elf", "quest", "myth", "spell"}
            adventure_keywords = {"journey", "quest", "explore", "discover", "danger", "expedition"}
            
            # Check for related words
            related_matches = sum(1 for word in item_keywords if word in fantasy_keywords or word in adventure_keywords)
            
            if related_matches > 0:
                similarity = 0.3 + (0.1 * related_matches)  # Some relation but not direct
                print(f"Item {item['id']} - RELATED match: {related_matches} related words ({similarity:.2f})")
            else:
                similarity = 0.1  # Very low similarity
                print(f"Item {item['id']} - NO match ({similarity:.2f})")
        
        similarities.append(float(similarity))
    
    return similarities

def get_current_model():
    """Return the current model name (for API compatibility)"""
    return "fallback"

def set_model(model_name):
    """Dummy function for API compatibility"""
    print(f"Note: Model switching not available in simplified mode. Requested: {model_name}")
    return True
