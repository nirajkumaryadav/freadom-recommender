import streamlit as st
import requests
import json

# Page configuration
st.set_page_config(
    page_title="Freadom Recommender - Simple Test",
    page_icon="📚",
    layout="wide"
)

# Define API URL
API_URL = "http://localhost:5000/api"

# Header
st.title('📚 Freadom Book Recommender')
st.write('A simplified interface for testing the recommendation engine')
st.markdown('---')

# Get users from API
try:
    users_response = requests.get(f"{API_URL}/users")
    users = users_response.json()
    user_options = {user['name']: user['id'] for user in users}
    
    # Display user selection
    st.header('Select a user')
    selected_user_name = st.selectbox('Choose a user:', list(user_options.keys()))
    selected_user_id = user_options[selected_user_name]
    
    # Show user details
    user_details = next((user for user in users if user['id'] == selected_user_id), None)
    if user_details:
        st.write(f"Age: {user_details['age']}")
        st.write(f"Reading level: {user_details['reading_level']:.1f}/5.0")
    
    # Get recommendations for the selected user
    if st.button('Get Recommendations'):
        with st.spinner('Getting recommendations...'):
            try:
                # Check which model is being used
                model_response = requests.get(f"{API_URL}/settings/model")
                model_info = model_response.json()
                st.info(f"Using model: {model_info.get('current_model', 'unknown')}")
                
                # Get recommendations
                recs_response = requests.get(f"{API_URL}/recommend/{selected_user_id}?count=3")
                recommendations = recs_response.json()
                
                if isinstance(recommendations, list):
                    st.header('Recommended Books')
                    
                    for i, rec in enumerate(recommendations):
                        st.subheader(f"{i+1}. {rec['title']}")
                        st.write(f"Author: {rec['author']}")
                        st.write(f"Genre: {rec['genre']}")
                        st.write(f"Reading Level: {rec['reading_level']:.1f}/5.0")
                        st.write(f"Age Range: {rec['age_range']}")
                        st.write(f"Topics: {', '.join(rec['topics'])}")
                        
                        # Match reasons
                        if 'match_reason' in rec:
                            st.write("Match Reasons:")
                            match_reason = rec['match_reason']
                            st.progress(match_reason['interest_match']/100)
                            st.caption(f"Interest match: {match_reason['interest_match']}%")
                            st.progress(match_reason['reading_level_match']/100)
                            st.caption(f"Reading level match: {match_reason['reading_level_match']}%")
                            st.progress(match_reason['popularity']/100)
                            st.caption(f"Popularity: {match_reason['popularity']}%")
                        
                        st.markdown("---")
                else:
                    st.error(f"Error: {recommendations.get('error', 'Unknown error')}")
                    
            except Exception as e:
                st.error(f"Error getting recommendations: {str(e)}")
except Exception as e:
    st.error(f"Error connecting to API: {str(e)}")
    st.info("Make sure the Flask API is running on http://localhost:5000")

# Footer
st.markdown("---")
st.caption("Freadom Book Recommender - Simplified Test Interface")
