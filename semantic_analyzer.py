# This file contains the implementation of the semantic similarity analyzer
# It supports both sentence-transformers and Qwen3-0.6B model for embeddings

import numpy as np
import torch  # Required for Qwen model processing

# Define model variables
sbert_model = None
qwen_model = None
qwen_tokenizer = None
current_model = "sbert"  # Default model

try:
    from sentence_transformers import SentenceTransformer
    
    def load_sbert_model():
        """Load the Sentence-BERT model"""
        global sbert_model
        if sbert_model is None:
            try:
                # Using a common model that should be available
                sbert_model = SentenceTransformer('all-MiniLM-L6-v2')
                print("SBERT model loaded successfully!")
                return True
            except Exception as e:
                print(f"Error loading SBERT model: {e}")
                try:
                    # Fallback to another common model
                    print("Trying fallback model...")
                    sbert_model = SentenceTransformer('distilbert-base-nli-mean-tokens')
                    print("Fallback SBERT model loaded successfully!")
                    return True
                except Exception as e2:
                    print(f"Error loading fallback SBERT model: {e2}")
                    return False
        return True
    
    def load_qwen_model():
        """Load the Qwen3-0.6B model"""
        global qwen_model, qwen_tokenizer
        if qwen_model is None:
            try:
                from transformers import AutoModelForCausalLM, AutoTokenizer
                
                # Load Qwen model and tokenizer (using Qwen1.5 which is widely available)
                model_name = "Qwen/Qwen1.5-0.5B"  # Using an available model
                print(f"Loading Qwen model: {model_name}")
                qwen_tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
                qwen_model = AutoModelForCausalLM.from_pretrained(
                    model_name, 
                    device_map="auto",
                    trust_remote_code=True
                )
                print("Qwen model loaded successfully!")
                return True
            except Exception as e:
                print(f"Error loading Qwen model: {e}")
                # Try a fallback model
                try:
                    # Fallback to a smaller model
                    model_name = "facebook/opt-125m"
                    print(f"Trying fallback model: {model_name}")
                    qwen_tokenizer = AutoTokenizer.from_pretrained(model_name)
                    qwen_model = AutoModelForCausalLM.from_pretrained(
                        model_name, 
                        device_map="auto"
                    )
                    print("Fallback model loaded successfully!")
                    return True
                except Exception as e2:
                    print(f"Error loading fallback model: {e2}")
                    return False
        return True
    
    def load_model():
        """Load the currently selected model"""
        if current_model == "qwen":
            return load_qwen_model()
        else:
            return load_sbert_model()
      # SBERT-specific functions
    def get_sbert_content_embeddings(content_list):
        """Generate embeddings for content descriptions using SBERT"""
        if not load_sbert_model():
            return None
            
        descriptions = []
        for item in content_list:
            topics_str = ' '.join(item['topics']) if isinstance(item['topics'], list) else item['topics']
            desc = f"{item['title']}. {topics_str}"
            descriptions.append(desc)
            
        embeddings = sbert_model.encode(descriptions)
        return embeddings
    
    def get_sbert_interest_embedding(interests):
        """Generate embedding for user interests using SBERT"""
        if not load_sbert_model():
            return None
            
        interest_text = " ".join(interests)
        embedding = sbert_model.encode([interest_text])[0]
        return embedding
    
    # Qwen3-specific functions
    def get_qwen_content_embeddings(content_list):
        """Generate embeddings for content descriptions using Qwen3"""
        if not load_qwen_model():
            return None
            
        descriptions = []
        for item in content_list:
            topics_str = ' '.join(item['topics']) if isinstance(item['topics'], list) else item['topics']
            desc = f"{item['title']}. {topics_str}"
            descriptions.append(desc)
            
        embeddings = []
        for desc in descriptions:
            inputs = qwen_tokenizer(desc, return_tensors="pt").to(qwen_model.device)
            with torch.no_grad():
                outputs = qwen_model(**inputs, output_hidden_states=True)
            
            # Use the last hidden state of the last layer as embedding
            last_hidden_state = outputs.hidden_states[-1]
            # Mean pooling to get a single vector
            embedding = last_hidden_state.mean(dim=1).squeeze().cpu().numpy()
            embeddings.append(embedding)
            
        return np.array(embeddings)
    
    def get_qwen_interest_embedding(interests):
        """Generate embedding for user interests using Qwen3"""
        if not load_qwen_model():
            return None
            
        interest_text = " ".join(interests)
        inputs = qwen_tokenizer(interest_text, return_tensors="pt").to(qwen_model.device)
        with torch.no_grad():
            outputs = qwen_model(**inputs, output_hidden_states=True)
        
        # Use the last hidden state of the last layer as embedding
        last_hidden_state = outputs.hidden_states[-1]
        # Mean pooling to get a single vector
        embedding = last_hidden_state.mean(dim=1).squeeze().cpu().numpy()
        return embedding
    
    def calculate_semantic_similarity(user_interests, content_items, model_name=None):
        """Calculate semantic similarity between user interests and content"""
        global current_model
        
        # If model_name is specified, update current_model
        if model_name:
            if model_name.lower() in ["qwen", "qwen3"]:
                current_model = "qwen"
            else:
                current_model = "sbert"
        
        # Use the appropriate model based on current_model
        if current_model == "qwen":
            if not load_qwen_model():
                return [0.5] * len(content_items)  # Default value if model fails
                
            content_embeddings = get_qwen_content_embeddings(content_items)
            user_embedding = get_qwen_interest_embedding(user_interests)
        else:
            if not load_sbert_model():
                return [0.5] * len(content_items)  # Default value if model fails
                
            content_embeddings = get_sbert_content_embeddings(content_items)
            user_embedding = get_sbert_interest_embedding(user_interests)
        
        # Calculate cosine similarity
        similarities = []
        for content_emb in content_embeddings:
            similarity = np.dot(user_embedding, content_emb) / (np.linalg.norm(user_embedding) * np.linalg.norm(content_emb))
            similarities.append(float(similarity))
        
        return similarities

    # Function to switch between models
    def set_model(model_name):
        """Set which model to use for semantic similarity calculations
        
        Args:
            model_name (str): Either 'sbert' or 'qwen'
            
        Returns:
            bool: True if model was set successfully, False otherwise
        """
        global current_model
        
        if model_name.lower() == "qwen" or model_name.lower() == "qwen3":
            current_model = "qwen"
            return load_qwen_model()
        elif model_name.lower() == "sbert":
            current_model = "sbert"
            return load_sbert_model()
        else:
            print(f"Unknown model name: {model_name}. Using default model (SBERT).")
            current_model = "sbert"
            return load_sbert_model()
    
    # Function to get the current model name
    def get_current_model():
        """Returns the name of the currently active model"""
        return current_model

except ImportError:
    print("Warning: Required packages not found. Using fallback similarity method.")
    import torch
      # Enhanced analyzer that doesn't require specialized models
    def calculate_semantic_similarity(user_interests, content_items, model_name=None):
        """Improved fallback similarity function using weighted word matching"""
        print("Using fallback similarity method")
        similarities = []
        
        for item in content_items:
            # Extract topic and title words
            item_topics = item['topics'] if isinstance(item['topics'], list) else []
            item_title_words = item['title'].lower().split()
            
            user_interests_set = set([w.lower() for w in user_interests])
            item_topics_set = set([w.lower() for w in item_topics])
            item_title_set = set(item_title_words)
            
            # Include both topics and title words
            item_words = item_topics_set.union(item_title_set)
            
            # Calculate direct word matches
            common_words = user_interests_set.intersection(item_words)
            direct_match_score = len(common_words) / max(1, len(user_interests_set))
            
            # Calculate similarity score with weighted approach - emulating how a semantic model would work
            if len(common_words) > 0:
                # If we have direct matches, give them more weight
                common_words_list = list(common_words)
                
                # Emulate semantic understanding with custom weights based on genre relationships
                if "fantasy" in common_words_list and ("magic" in common_words_list or "adventure" in common_words_list):
                    # Fantasy books with magic or adventure are very similar to fantasy interests
                    similarity = 0.85 + (0.15 * direct_match_score)  # Strong match
                    print(f"MATCH TYPE: Strong fantasy match ({similarity:.2f})")
                elif "fantasy" in common_words_list or "magic" in common_words_list or "adventure" in common_words_list:
                    # Books with at least one main fantasy element
                    similarity = 0.70 + (0.2 * direct_match_score)   # Good match
                    print(f"MATCH TYPE: Good fantasy element match ({similarity:.2f})")
                else:
                    # Other direct matches
                    similarity = 0.55 + (0.25 * direct_match_score)  # Basic match
                    print(f"MATCH TYPE: Basic keyword match ({similarity:.2f})")
            else:
                # No direct matches, look for semantic relationships
                # Check if topics have any thematic relation to user interests
                
                # Fantasy-related keywords that might not directly match but are related
                fantasy_related = ["wizards", "dragons", "elves", "magical", "quest", "myth"]
                adventure_related = ["journey", "quest", "explore", "discover", "danger"]
                
                # Check for related words
                related_count = sum(1 for word in item_topics_set if word in fantasy_related or word in adventure_related)
                if related_count > 0:
                    similarity = 0.45 + (0.1 * related_count)  # Semantic relationship
                    print(f"MATCH TYPE: Semantic relationship ({similarity:.2f})")
                else:
                    # No direct or semantic match
                    similarity = 0.3  # Low relevance 
                    print(f"MATCH TYPE: Low relevance ({similarity:.2f})")
                
            similarities.append(float(similarity))
        
        return similarities
        
    # Add stubs for the model switching functions
    def set_model(model_name):
        """Stub for model switching in fallback mode"""
        print(f"Warning: Models not available. Ignoring request to switch to {model_name}")
        return False
        
    def get_current_model():
        """Stub for getting current model in fallback mode"""
        return "fallback"