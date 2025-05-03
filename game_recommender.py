import streamlit as st
import pandas as pd
import pickle
import os

# Set page configuration
st.set_page_config(
    page_title="Steam Game Recommender",
    page_icon="🎮",
    layout="wide"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .game-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .game-title {
        font-size: 1.3rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .game-info {
        font-size: 0.9rem;
        color: #555;
    }
    .similarity-score {
        font-size: 0.9rem;
        font-weight: bold;
        color: #1E88E5;
    }
</style>
""", unsafe_allow_html=True)

# Function to load the model
@st.cache_resource
def load_model():
    with open('model.pkl', 'rb') as f:
        model_data = pickle.load(f)
    return model_data

@st.cache_data
def load_games_list():
    if os.path.exists('games_list.csv'):
        return pd.read_csv('games_list.csv')
    else:
        model_data = load_model()
        return model_data['games_df'][['title']]

def get_recommendations(game_title, model_data, method='hybrid'):
    games_df = model_data['games_df']
    cosine_sim = model_data['cosine_sim']
    indices = model_data['indices']
    
    if method == 'content-based' or method == 'hybrid':
        # Content-based approach
        try:
            idx = indices[game_title]
            sim_scores = list(enumerate(cosine_sim[idx]))
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            sim_scores = sim_scores[1:6]  # Get top 5 similar games (excluding the input game)
            game_indices = [i[0] for i in sim_scores]
            
            recommendations = games_df.iloc[game_indices][['name', 'genres', 'tags']].copy()
            recommendations['similarity_score'] = [i[1] for i in sim_scores]
            
            return recommendations, 'content-based'
        except:
            if method == 'hybrid':
                # If content-based fails and we're using hybrid, try collaborative
                pass
            else:
                st.error(f"Error finding recommendations for {game_title} using content-based filtering")
                return pd.DataFrame(), None
    
    if method == 'collaborative' or method == 'hybrid':
        # Collaborative approach
        try:
            game_similarity_df = model_data['game_similarity_df']
            if game_title in game_similarity_df.columns:
                similar_games = game_similarity_df[game_title].sort_values(ascending=False)[1:6].index.tolist()
                similarity_scores = game_similarity_df[game_title].sort_values(ascending=False)[1:6].values.tolist()
                
                recommendations = pd.DataFrame({
                    'name': similar_games,
                    'similarity_score': similarity_scores
                })
                
                recommendations = recommendations.merge(games_df[['name', 'genres', 'tags']], on='name')
                
                return recommendations, 'collaborative'
        except:
            if method == 'hybrid':
                # If collaborative fails and we're using hybrid, content-based was already tried
                pass
            else:
                st.error(f"Error finding recommendations for {game_title} using collaborative filtering")
                return pd.DataFrame(), None
    
    # If we get here with hybrid method, both approaches failed
    return pd.DataFrame(), None

def display_game_card(game):
    st.markdown(f"""
    <div class="game-card">
        <div class="game-title">{game['name']}</div>
        <div class="game-info"><b>Genres:</b> {game['genres']}</div>
        <div class="game-info"><b>Tags:</b> {game['tags']}</div>
        <div class="similarity-score">Similarity Score: {game['similarity_score']:.2f}</div>
    </div>
    """, unsafe_allow_html=True)

def main():
    st.markdown('<h1 class="main-header">Steam Game Recommender 🎮</h1>', unsafe_allow_html=True)
    try:
        model_data = load_model()
        games_list = load_games_list()
        game_titles = sorted(games_list['name'].unique())
    except Exception as e:
        st.error(f"Error loading model data: {e}")
        return
    st.sidebar.title("Filtering Options")
    if 'genres' in games_list.columns:
        all_genres = []
        for genres_str in games_list['genres'].dropna().unique():
            if genres_str:
                all_genres.extend([g.strip() for g in genres_str.split(',')])
        unique_genres = sorted(list(set(all_genres)))
        
        selected_genres = st.sidebar.multiselect(
            "Filter by Genre",
            unique_genres
        )
        
        if selected_genres:
            filtered_games = []
            for _, game in games_list.iterrows():
                if pd.notna(game['genres']):
                    game_genres = [g.strip() for g in game['genres'].split(',')]
                    if any(genre in game_genres for genre in selected_genres):
                        filtered_games.append(game['name'])
            game_titles = sorted(filtered_games)
    
    # Method selection
    recommendation_method = st.sidebar.radio(
        "Recommendation Method",
        ['hybrid', 'content-based', 'collaborative'],
        index=0
    )
    
    # Main content area
    st.subheader("Select a game to get recommendations")
    
    # Game selection
    selected_game = st.selectbox("Choose a game", game_titles)
    
    if st.button("Get Recommendations"):
        with st.spinner("Finding similar games..."):
            recommendations, method_used = get_recommendations(selected_game, model_data, recommendation_method)
            
            if not recommendations.empty:
                st.success(f"Found {len(recommendations)} recommendations using {method_used} filtering!")
                
                # Display the original game
                st.subheader("Selected Game")
                original_game = model_data['games_df'][model_data['games_df']['name'] == selected_game].iloc[0]
                original_game_data = {
                    'name': original_game['name'],
                    'genres': original_game['genres'],
                    'tags': original_game['tags'],
                    'similarity_score': 1.0  # Self-similarity is 1.0
                }
                display_game_card(original_game_data)
                
                # Display recommendations
                st.subheader("Recommended Games")
                for _, game in recommendations.iterrows():
                    display_game_card(game)
            else:
                st.warning(f"No recommendations found for '{selected_game}' using {recommendation_method} filtering.")
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.info(
        "This recommendation system uses both content-based filtering (based on game attributes) "
        "and collaborative filtering (based on user recommendations) to suggest similar games."
    )

if __name__ == "__main__":
    main()