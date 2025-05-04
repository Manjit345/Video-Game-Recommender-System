import streamlit as st
import pandas as pd
import pickle

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
    .game-card {
        background: linear-gradient(135deg, #F5F7FA 0%, #E4E7EB 100%);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border: 1px solid #E2E8F0;
        transition: transform 0.2s ease;
    }
    .game-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0,0,0,0.15);
    }
    .game-title {
        font-size: 1.4rem;
        font-weight: bold;
        margin-bottom: 0.8rem;
        color: #2D3748;
    }
    .game-info {
        font-size: 1rem;
        color: #4A5568;
        line-height: 1.4;
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
    return model_data['games_df'][['title', 'genres']]

def get_recommendations_from_users(game_title, model_data, n=5):
    user_recommendations = model_data['recommendations_df'].merge(model_data['games_df'][['app_id', 'title', 'genres']], on='app_id',how='left')
    user_recommendations['genres'] = user_recommendations['genres'].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)
    users_who_liked = user_recommendations[(user_recommendations['title'] == game_title) & (user_recommendations['is_recommended'])]['user_id'].unique()
    recommendations = user_recommendations[(user_recommendations['user_id'].isin(users_who_liked)) & (user_recommendations['is_recommended']) & (user_recommendations['title'] != game_title)]
    recommendations = recommendations.groupby(['title', 'genres']).agg({'is_recommended': 'count'}).reset_index()
    return recommendations.nlargest(n, 'is_recommended')[['title', 'genres']]

def get_recommendations_from_similarity(game_title, model_data, n=5):
    similarity_matrix = model_data['tfidf_matrix']
    games_df = model_data['games_df']
    game_idx = games_df[games_df['title'] == game_title].index[0]
    similar_scores = similarity_matrix[game_idx]
    similar_games = list(enumerate(similar_scores))
    similar_games = sorted(similar_games, key=lambda x: x[1], reverse=True)
    recommendations = []
    for idx in similar_games[1:n+1]:recommendations.append({'title': games_df.iloc[idx]['title'],'genres': games_df.iloc[idx]['genres']})
    
    return pd.DataFrame(recommendations)

def get_recommendations(game_title, model_data, n=5):
    recommendations = get_recommendations_from_users(game_title, model_data, n)
    if recommendations.empty:
        recommendations = get_recommendations_from_similarity(game_title, model_data, n)
    
    return recommendations

def display_game_card(game):
    st.markdown(f"""
    <div class="game-card">
        <div class="game-title">{game['title']}</div>
    </div>
    """, unsafe_allow_html=True)

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
                    'title': original_game['title']
                }
                display_game_card(original_game_data)
                st.subheader("Then you might also like")
                for _, game in recommendations.iterrows():
                    display_game_card(game)
            else:
                st.warning(f"Sorry but couldn't find any good recommendations based on '{selected_game}'.")

if __name__ == "__main__":
    main()