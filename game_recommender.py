import streamlit as st
import pandas as pd
import pickle
import requests
from io import BytesIO

st.set_page_config(
    page_title="Steam Game Recommender",
    page_icon="🎮",
    layout="wide"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2D3A8C;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    .game-title {
        font-size: 1.2rem;
        font-weight: bold;
        margin-top: 0.5rem;
        color: #2D3748;
        text-align: center;
    }

</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_model():
    with open('model.pkl', 'rb') as f:
        model_data = pickle.load(f)
    return model_data

@st.cache_data
def load_games_list():
    model_data = load_model()
    return model_data['games_df'][['title', 'genres', 'app_id']]

def get_recommendations_from_users(game_title, model_data, n=5):
    user_recommendations = model_data['recommendations_df'].merge(model_data['games_df'][['app_id', 'title', 'genres']], on='app_id', how='left')
    user_recommendations['genres'] = user_recommendations['genres'].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)
    users_who_liked = user_recommendations[(user_recommendations['title'] == game_title) & (user_recommendations['is_recommended'])]['user_id'].unique()
    recommendations = user_recommendations[(user_recommendations['user_id'].isin(users_who_liked)) & (user_recommendations['is_recommended']) & (user_recommendations['title'] != game_title)]
    recommendations = recommendations.groupby(['title', 'genres', 'app_id']).agg({'is_recommended': 'count'}).reset_index()
    return recommendations.nlargest(n, 'is_recommended')[['title', 'genres', 'app_id']]

def get_recommendations_from_similarity(game_title, model_data, n=5):
    similarity_matrix = model_data['tfidf_matrix']
    games_df = model_data['games_df']
    game_idx = games_df[games_df['title'] == game_title].index[0]
    similar_scores = similarity_matrix[game_idx]
    similar_games = list(enumerate(similar_scores))
    similar_games = sorted(similar_games, key=lambda x: x[1], reverse=True)
    recommendations = []
    for i, (idx, _) in enumerate(similar_games[1:n+1]):
        game = games_df.iloc[idx]
        recommendations.append({
            'title': game['title'],
            'genres': game['genres'],
            'app_id': game['app_id']
        })
    
    return pd.DataFrame(recommendations)

def get_recommendations(game_title, model_data, n=5):
    recommendations = get_recommendations_from_users(game_title, model_data, n)
    if len(recommendations) < n:
        similarity_recs = get_recommendations_from_similarity(game_title, model_data, n - len(recommendations))
        recommendations = pd.concat([recommendations, similarity_recs])
    
    return recommendations

@st.cache_data
def get_game_poster(app_id):
    try:
        steam_header_url = f"https://cdn.cloudflare.steamstatic.com/steam/apps/{app_id}/header.jpg"
        response = requests.get(steam_header_url, timeout=3)
        
        if response.status_code == 200:
            return BytesIO(response.content)
        else:
            return None
    except:
        return None

def display_game_card(game, cols):
    with cols:
        app_id = game.get('app_id')
        image_data = get_game_poster(app_id)
        if image_data:
            st.image(image_data, use_column_width=True)
        else:
            st.image(f"https://via.placeholder.com/460x215/CCCCCC/808080?text={game['title']}", use_column_width=True)
        st.markdown(f"<div class='game-title'>{game['title']}</div>", unsafe_allow_html=True)

def main():
    st.markdown('<h1 class="main-header">Steam Game Recommender 🎮</h1>', unsafe_allow_html=True)
    try:
        model_data = load_model()
        games_list = load_games_list()
        game_titles = sorted(games_list['title'].unique())
    except Exception as e:
        st.error(f"Error loading model data: {e}")
        return
    
    st.subheader("Select a game which you have played before")
    selected_game = st.selectbox("Choose a game", game_titles)
    
    if st.button("Get Recommendations"):
        with st.spinner("Finding the best recommendations for you..."):
            recommendations = get_recommendations(selected_game, model_data)
            
            if not recommendations.empty:
                st.subheader("If you loved")
                original_game = model_data['games_df'][model_data['games_df']['title'] == selected_game].iloc[0]
                original_game_data = {
                    'title': original_game['title'],
                    'app_id': original_game['app_id'],
                    'genres': original_game['genres']
                }
                
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    display_game_card(original_game_data, col2)
                
                st.subheader("Then you might also like")
                num_recommendations = len(recommendations)
                rows = (num_recommendations + 2) // 3
                
                for row in range(rows):
                    cols = st.columns(3)
                    for col_idx in range(3):
                        game_idx = row * 3 + col_idx
                        if game_idx < num_recommendations:
                            game = recommendations.iloc[game_idx]
                            display_game_card(game, cols[col_idx])
            else:
                st.warning(f"Sorry but couldn't find any good recommendations based on '{selected_game}'.")

if __name__ == "__main__":
    main()