import streamlit as st
import pandas as pd
import requests
import json
import time
from PIL import Image, ImageDraw
import io
import base64

# Set page config
st.set_page_config(
    page_title="Freadom Smart Recommendation",
    page_icon="📚",
    layout="wide"
)

# Initialize API endpoint
API_URL = "http://localhost:5000/api"

# Helper functions for UI
def create_user_avatar(name, size=100):
    """Create a simple avatar image with the user's initial"""
    img = Image.new('RGB', (size, size), color=(100, 100, 255))
    d = ImageDraw.Draw(img)
    d.ellipse((5, 5, size-5, size-5), fill=(200, 200, 255))
    
    # Add initial
    initial = name[0].upper() if name else "?"
    # In a real app, you'd use proper font handling
    d.text((size//2-10, size//2-15), initial, fill=(50, 50, 150), size=40)
    
    # Convert to base64 for display
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def get_reading_level_stars(level):
    """Convert numeric reading level to stars"""
    full_stars = int(level)
    half_star = level - full_stars >= 0.5
    
    stars = "★" * full_stars
    if half_star:
        stars += "½"
    
    return stars

def display_progress_bar(value, max_value=5):
    """Display a colorful progress bar"""
    percentage = value / max_value
    st.progress(percentage)
    
    # Use markdown to create aligned text without columns
    st.markdown(
        "<div style='display: flex; justify-content: space-between;'>"
        "<span>Easy</span><span>Hard</span>"
        "</div>", 
        unsafe_allow_html=True
    )

# Session state initialization
if "user_role" not in st.session_state:
    st.session_state.user_role = None

if "selected_user" not in st.session_state:
    st.session_state.selected_user = None

if "view" not in st.session_state:
    st.session_state.view = "home"

# Child-friendly view
def child_view():
    st.header("📚 My Reading Adventure")
    
    # Get user list
    try:
        response = requests.get(f"{API_URL}/users")
        users = response.json()
    except:
        st.error("Couldn't connect to the API. Is the Flask server running?")
        st.info("Run the Flask API with 'python app.py' in a separate terminal.")
        if st.button("Initialize Database"):
            try:
                response = requests.get(f"{API_URL}/setup")
                st.success("Database initialized! Please restart the app.")
            except:
                st.error("Couldn't connect to initialize the database.")
        return
    
    # Child-friendly user selector with avatars
    st.subheader("Who are you?")
    
    # Create columns for each user
    cols = st.columns(len(users))
    
    for i, user in enumerate(users):
        with cols[i]:
            avatar = create_user_avatar(user['name'])
            st.image(f"data:image/png;base64,{avatar}", width=100)
            if st.button(f"{user['name']}", key=f"user_{user['id']}"):
                st.session_state.selected_user = user['id']
                st.session_state.view = "recommendations"
            st.write(f"Age: {user['age']}")
    
    if "selected_user" in st.session_state and st.session_state.view == "recommendations":
        user_id = st.session_state.selected_user
        
        try:
            # Get user progress
            progress_response = requests.get(f"{API_URL}/user/{user_id}/progress")
            progress = progress_response.json()
            
            if "error" in progress or "message" in progress:
                # Show recommendations anyway
                st.info("No reading history yet. Let's find some books for you!")
            else:
                st.subheader("Your Reading Journey")
                st.write(f"Reading level: {get_reading_level_stars(progress['reading_level'])}")
                st.write(f"Books read: {progress['books_read']}")
                
                if progress.get("favorite_topics"):
                    st.write("Things you like:")
                    for topic in progress["favorite_topics"][:3]:
                        st.write(f"- {topic}")
            
            # Get recommendations
            response = requests.get(f"{API_URL}/recommend/{user_id}?count=3")
            recommendations = response.json()
            
            # Check which model is being used
            try:
                model_response = requests.get(f"{API_URL}/settings/model")
                current_model = model_response.json().get("current_model", "sbert")
                if current_model == "qwen":
                    st.caption("Using advanced AI for your recommendations! 🚀")
            except:
                pass  # Silently fail if can't get model info
            
            if isinstance(recommendations, list):
                st.subheader("📘 Books Just For You!")
                
                # Display recommendations in a child-friendly way
                for i, rec in enumerate(recommendations):
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        # Placeholder for book cover - in a real app, use actual book covers
                        avatar = create_user_avatar(rec['title'])
                        st.image(f"data:image/png;base64,{avatar}", width=120)
                    with col2:
                        st.subheader(rec['title'])
                        st.write(f"By {rec['author']}")
                        
                        # Difficulty indicator with stars instead of numbers
                        st.write("Reading Level: " + get_reading_level_stars(rec['reading_level']))
                        st.write(f"Good for ages: {rec['age_range']}")
                        
                        # Show why this book was recommended
                        st.write("This book matches:")
                        st.write(f"💙 Your interests: {rec['match_reason']['interest_match']}% | 📊 Your level: {rec['match_reason']['reading_level_match']}% | ⭐ Popularity: {rec['match_reason']['popularity']}%")
                        
                        if st.button(f"I want to read this!", key=f"read_{i}"):
                            # Mark as read
                            read_response = requests.post(f"{API_URL}/user/{user_id}/read/{rec['id']}")
                            st.balloons()
                            st.success("Great choice! Happy reading!")
                            time.sleep(1)  # Show success message briefly
                            st.experimental_rerun()  # Refresh to update recommendations
            else:
                st.error(f"Error: {recommendations.get('error', 'Unknown error')}")
        
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.info("Make sure the API server is running.")

# Teacher view
def teacher_view():
    st.header("👩‍🏫 Teacher Dashboard")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Student Progress", "Text Analysis", "Class Overview", "AI Model Settings"])
    
    with tab1:
        try:
            # Get user list
            response = requests.get(f"{API_URL}/users")
            users = response.json()
            
            selected_user = st.selectbox(
                "Select student:",
                [user['id'] for user in users],
                format_func=lambda x: next((user['name'] for user in users if user['id'] == x), "Unknown")
            )
            
            if selected_user:
                # Get student progress
                progress_response = requests.get(f"{API_URL}/user/{selected_user}/progress")
                progress = progress_response.json()
                
                if "error" not in progress and "message" not in progress:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Reading Profile")
                        
                        # Select user info from users list
                        user_info = next((user for user in users if user['id'] == selected_user), None)
                        if user_info:
                            st.write(f"**Name:** {user_info['name']}")
                            st.write(f"**Age:** {user_info['age']}")
                        
                        st.write(f"**Current Reading Level:** {progress['reading_level']:.1f}/5.0")
                        st.write("**Reading Level Progression:**")
                        display_progress_bar(progress['reading_level'])
                        
                        st.write(f"**Books Read:** {progress['books_read']}")
                        
                        # Progress indicator
                        progress_trend = progress['progress_trend']
                        if progress_trend > 0:
                            st.success(f"📈 Improving: Reading {progress_trend:.1f} levels above average")
                        elif progress_trend < 0:
                            st.warning(f"📉 Needs support: Reading {-progress_trend:.1f} levels below average")
                        else:
                            st.info("Reading at a consistent level")
                    
                    with col2:
                        st.subheader("Interest Areas")
                        if progress.get("favorite_topics"):
                            for topic in progress["favorite_topics"]:
                                st.write(f"- {topic}")
                        else:
                            st.write("No clear interests detected yet")
                    
                    # Show reading history
                    st.subheader("Reading History")
                    if progress.get("history"):
                        history_df = pd.DataFrame(progress["history"])
                        st.dataframe(history_df)
                    else:
                        st.info("No reading history available")
                else:
                    st.info(progress.get("message", "No progress data available for this student"))
        
        except Exception as e:
            st.error(f"Error loading student data: {str(e)}")
            st.info("Make sure the API server is running.")
    
    with tab2:
        st.subheader("Text Complexity Analyzer")
        st.write("Analyze reading materials to find appropriate content for your students")
        
        text_input = st.text_area("Paste text to analyze:", height=200)
        target_age = st.slider("Target age group:", 5, 12, 8)
        
        # Model selection in the sidebar for teachers
        st.sidebar.subheader("Advanced Settings")
        try:
            # Get current model
            model_response = requests.get(f"{API_URL}/settings/model")
            current_model = model_response.json().get("current_model", "sbert")
            
            st.sidebar.write("**Semantic Analysis Model:**")
            selected_model = st.sidebar.radio(
                "Select recommendation model", 
                ["sbert", "qwen3"], 
                index=0 if current_model == "sbert" else 1,
                help="SBERT is faster, Qwen3 has better understanding but is slower"
            )
            
            # Allow changing the model
            if selected_model.lower() != current_model.lower():
                if st.sidebar.button(f"Switch to {selected_model.upper()} model"):
                    with st.spinner(f"Switching to {selected_model.upper()} model..."):
                        try:
                            # Switch model via API
                            switch_response = requests.post(
                                f"{API_URL}/settings/model",
                                json={"model": selected_model}
                            )
                            
                            if switch_response.status_code == 200:
                                st.sidebar.success(f"Now using {selected_model.upper()} model for recommendations")
                            else:
                                st.sidebar.error(f"Failed to switch model: {switch_response.json().get('error', 'Unknown error')}")
                        except Exception as e:
                            st.sidebar.error(f"Error switching model: {str(e)}")
        except Exception as e:
            st.sidebar.warning(f"Cannot retrieve model settings: {str(e)}")
        
        if st.button("Analyze for Classroom Use") and text_input:
            with st.spinner("Analyzing text..."):
                try:
                    # Call API for analysis
                    response = requests.post(
                        f"{API_URL}/analyze",
                        json={"text": text_input}
                    )
                    
                    # Display teacher-focused results
                    result = response.json()
                    analysis = result["analysis"]
                    topics = result["topics"]
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Grade Level", f"{analysis['flesch_kincaid_grade']:.1f}")
                        st.metric("Reading Ease", f"{analysis['flesch_reading_ease']:.1f}/100")
                        st.metric("Vocabulary Richness", f"{analysis['vocabulary_richness']:.2f}")
                        st.metric("Word Count", analysis['word_count'])
                        st.metric("Sentence Count", analysis['sentence_count'])
                    
                    with col2:
                        # Appropriateness indicator
                        target_grade = target_age - 5  # Rough conversion from age to grade
                        diff = abs(analysis['flesch_kincaid_grade'] - target_grade)
                        
                        if diff < 1:
                            st.success("✅ Well suited for this age group")
                        elif diff < 2:
                            st.warning("⚠️ May need scaffolding for some students")
                        else:
                            st.error("❌ May be too challenging for this age group")
                        
                        st.write(f"**Key Topics:** {', '.join(topics)}")
                        
                        # Reading level conversion
                        st.write(f"**Freadom Reading Level:** {analysis['reading_level']}/5")
                        display_progress_bar(analysis['reading_level'])
                    
                    # Teaching suggestions
                    st.subheader("Teaching Suggestions")
                    if analysis['avg_sentence_length'] > 15:
                        st.write("- Consider pre-teaching complex sentence structures")
                    if analysis['vocabulary_richness'] > 0.6:
                        st.write("- Create a vocabulary preview for unusual words")
                    if analysis['reading_level'] >= 4:
                        st.write("- This text may work well for reading groups or guided reading")
                    if analysis['word_count'] < 100:
                        st.write("- Consider pairing with other short texts on similar topics")
                except Exception as e:
                    st.error(f"Analysis error: {str(e)}")
    
    with tab3:
        st.info("Class overview features will be available in future updates.")
    
    with tab4:
        st.subheader("AI Model Configuration")
        st.write("Select the AI model to use for book recommendations")
        
        # Get current model
        try:
            response = requests.get(f"{API_URL}/settings/model")
            current_model = response.json().get("current_model", "sbert")
        except Exception as e:
            st.error(f"Error fetching current model: {str(e)}")
            current_model = "unknown"
        
        # Display model information
        st.write("### Current Model")
        if current_model == "qwen":
            st.write("🤖 **Using:** Qwen3-0.6B")
            st.write("This model provides more advanced semantic understanding for better recommendations.")
        elif current_model == "sbert":
            st.write("🤖 **Using:** Sentence-BERT")
            st.write("This is a fast and efficient model for semantic similarity.")
        else:
            st.write("🤖 **Using:** Fallback mode")
            st.write("Using basic keyword matching as both main models failed to load.")
        
        # Model selection
        st.write("### Change Model")
        model_options = ["sbert", "qwen"]
        selected_model = st.radio(
            "Select recommendation model:",
            model_options,
            index=0 if current_model == "sbert" else 1,
            format_func=lambda x: "Sentence-BERT (Fast)" if x == "sbert" else "Qwen3-0.6B (Advanced)",
            horizontal=True
        )
        
        if st.button("Apply Model Change"):
            try:
                response = requests.post(
                    f"{API_URL}/settings/model",
                    json={"model": selected_model}
                )
                result = response.json()
                if "error" in result:
                    st.error(f"Error: {result['error']}")
                else:
                    st.success(f"Model changed to {result['current_model']} successfully!")
            except Exception as e:
                st.error(f"Error changing model: {str(e)}")
        
        # Model information
        st.write("### Model Information")
        with st.expander("About the models"):
            st.write("""
            **Sentence-BERT**:
            - Lightweight and fast model
            - Good for general text similarity
            - Lower resource usage
            - Suitable for most recommendations
            
            **Qwen3-0.6B**:
            - More advanced natural language understanding
            - Better semantic comprehension for nuanced content matching
            - Requires more computational resources
            - May have more accurate recommendations for complex texts
            """)
            
        # Troubleshooting
        with st.expander("Troubleshooting"):
            st.write("""
            If you encounter issues with the models:
            
            1. Ensure all dependencies are installed (`pip install -r requirements.txt`)
            2. Check that you have sufficient disk space for model files
            3. For some models, you may need Hugging Face authentication
            4. If a model fails to load, the system will fall back to simpler methods
            """)
            
        # Model download status
        with st.expander("Download models manually"):
            st.write("You can use the script below to download the models:")
            st.code("python download_models.py")
            if st.button("Download Models Now"):
                with st.spinner("Downloading models..."):
                    try:
                        result = requests.get(f"{API_URL}/setup/models")
                        st.success(f"Model download initiated: {result.json().get('message', '')}")
                    except Exception as e:
                        st.error(f"Error initiating model download: {str(e)}")

# Parent view
def parent_view():
    st.header("👨‍👩‍👧 Parent Dashboard")
    
    try:
        # Get user list
        response = requests.get(f"{API_URL}/users")
        users = response.json()
        
        # Filter to show only children (in a real app, you'd link parents to children)
        st.subheader("Your Children")
        
        selected_user = st.selectbox(
            "Select child:",
            [user['id'] for user in users],
            format_func=lambda x: next((user['name'] for user in users if user['id'] == x), "Unknown")
        )
        
        if selected_user:
            # Get child progress
            progress_response = requests.get(f"{API_URL}/user/{selected_user}/progress")
            progress = progress_response.json()
            
            if "error" not in progress and "message" not in progress:
                # User info
                user_info = next((user for user in users if user['id'] == selected_user), None)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Reading Progress")
                    if user_info:
                        st.write(f"**Name:** {user_info['name']}")
                        st.write(f"**Age:** {user_info['age']}")
                    
                    st.write(f"**Current Reading Level:** {progress['reading_level']:.1f}/5.0")
                    display_progress_bar(progress['reading_level'])
                    
                    st.write(f"**Books Read:** {progress['books_read']}")
                    
                    # Show progress in parent-friendly terms
                    progress_trend = progress['progress_trend']
                    if progress_trend > 0.5:
                        st.success("🌟 Great progress! Your child is advancing in reading skills.")
                    elif progress_trend > 0:
                        st.success("📈 Making good progress in reading skills.")
                    elif progress_trend > -0.5:
                        st.info("📊 Reading at a consistent level.")
                    else:
                        st.warning("💡 May need additional reading support.")
                
                with col2:
                    st.subheader("Reading Interests")
                    if progress.get("favorite_topics"):
                        st.write("Your child enjoys reading about:")
                        for topic in progress["favorite_topics"]:
                            st.write(f"- {topic}")
                        
                        st.write("**Tips to encourage reading:**")
                        st.write(f"- Look for more books about {', '.join(progress['favorite_topics'][:2])}")
                        st.write("- Set aside 20 minutes of daily reading time")
                        st.write("- Read together and discuss the stories")
                    else:
                        st.write("Not enough reading history to determine interests yet.")
                
                # Recent books
                st.subheader("Recent Books")
                if progress.get("history"):
                    history = progress["history"]
                    for book in history[-3:]:  # Show last 3 books
                        st.write(f"- {book['title']} (Level: {book['reading_level']:.1f}/5)")
                else:
                    st.info("No reading history available yet.")
                
                # Recommendations for parents
                st.subheader("Recommended Books")
                try:
                    # Show which model is being used
                    model_response = requests.get(f"{API_URL}/settings/model")
                    current_model = model_response.json().get("current_model", "sbert")
                    model_name = "Qwen3 (Advanced)" if current_model == "qwen" else "SBERT (Standard)" if current_model == "sbert" else "Basic"
                    st.caption(f"Using {model_name} AI model for recommendations")
                    
                    rec_response = requests.get(f"{API_URL}/recommend/{selected_user}?count=3")
                    recommendations = rec_response.json()
                    
                    if isinstance(recommendations, list):
                        st.write("Books your child might enjoy:")
                        for rec in recommendations:
                            st.write(f"- **{rec['title']}** by {rec['author']} (Age: {rec['age_range']})")
                    else:
                        st.info("No recommendations available at this time.")
                except Exception as e:
                    st.error(f"Error getting recommendations: {str(e)}")
            else:
                st.info(progress.get("message", "No reading data available for this child yet."))
                st.write("Encourage your child to read more books in the Freadom app!")
    
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.info("Make sure the API server is running.")

# Main app function
def main():
    # Create a book-themed logo
    book_logo_html = '''
    <svg width="150" height="80" xmlns="http://www.w3.org/2000/svg">
        <rect x="30" y="15" width="90" height="55" rx="3" fill="#1565c0"/>
        <rect x="33" y="18" width="84" height="49" rx="2" fill="#bbdefb"/>
        <text x="40" y="45" font-family="Arial" font-size="16" font-weight="bold" fill="#1565c0">Freadom</text>
        <text x="44" y="60" font-family="Arial" font-size="8" fill="#1565c0">Read Smart</text>
    </svg>
    '''
    logo_b64 = base64.b64encode(book_logo_html.encode('utf-8')).decode('utf-8')
    st.sidebar.markdown(f'<img src="data:image/svg+xml;base64,{logo_b64}" alt="Freadom Logo" width="150">', unsafe_allow_html=True)
    
    # Initialize database if needed
    if st.sidebar.button("Initialize Database"):
        try:
            response = requests.get(f"{API_URL}/setup")
            st.sidebar.success(response.json()["message"])
        except:
            st.sidebar.error("Could not connect to API. Make sure Flask server is running.")
            st.sidebar.info("Run 'python app.py' in a terminal window first.")
    
    # User role selection in sidebar
    if st.session_state.user_role is None:
        st.title("📚 Freadom Smart Reading")
        st.write("Welcome to the Freadom Smart Recommendation System!")
        st.write("This app helps children find the perfect books for their reading level and interests.")
        
        st.subheader("Choose your user type:")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("👧 I'm a Reader"):
                st.session_state.user_role = "child"
                st.experimental_rerun()
        
        with col2:
            if st.button("👩‍🏫 I'm a Teacher"):
                st.session_state.user_role = "teacher"
                st.experimental_rerun()
                
        with col3:
            if st.button("👨‍👩‍👧 I'm a Parent"):
                st.session_state.user_role = "parent"
                st.experimental_rerun()
    else:
        # Display current user role and option to switch
        st.sidebar.write(f"Current role: {st.session_state.user_role}")
        if st.sidebar.button("Switch User Role"):
            st.session_state.user_role = None
            st.session_state.selected_user = None
            st.session_state.view = "home"
            st.experimental_rerun()
            
        # Display the appropriate view
        if st.session_state.user_role == "child":
            child_view()
        elif st.session_state.user_role == "teacher":
            teacher_view()
        elif st.session_state.user_role == "parent":
            parent_view()

if __name__ == "__main__":
    main()
</copilot-edited-file>
```