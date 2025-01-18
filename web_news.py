import streamlit as st
import requests
from datetime import datetime, timedelta
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_news_app():
    # Configure page
    st.set_page_config(
        page_title="Financial News Dashboard",
        page_icon="📈",
        layout="wide"
    )

    # Add title and description
    st.title("📰 Financial News Dashboard")
    st.markdown("Stay updated with the latest news in Finance, Crypto, Stocks, and ESG")

    # Get API key from environment variable or secrets
    api_key = os.getenv('NEWS_API_KEY') or st.secrets["NEWS_API_KEY"]
    
    if not api_key:
        st.error("NEWS_API_KEY not found in environment variables or secrets")
        return

    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Category selection
    category = st.sidebar.selectbox(
        "Select News Category",
        ["Finance", "Cryptocurrency", "Stock Market", "ESG", "All"]
    )
    
    # Date range
    days_ago = st.sidebar.slider("Select news from last N days", 1, 7, 3)
    
    # Number of articles
    article_count = st.sidebar.slider("Number of articles to display", 5, 30, 10)

    # Create search queries based on category
    search_queries = {
        "Finance": "financial OR banking OR economy",
        "Cryptocurrency": "cryptocurrency OR bitcoin OR blockchain",
        "Stock Market": "stock market OR wall street OR nasdaq OR dow jones",
        "ESG": "ESG OR sustainable investing OR green finance",
        "All": "(financial OR cryptocurrency OR stock market OR ESG)"
    }

    @st.cache_data(ttl=3600)  # Cache data for 1 hour
    def fetch_news(query, days, count):
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Format dates for API
        from_date = start_date.strftime('%Y-%m-%d')
        to_date = end_date.strftime('%Y-%m-%d')
        
        # API endpoint
        url = "https://newsapi.org/v2/everything"
        
        # Parameters for the API request
        params = {
            'q': query,
            'from': from_date,
            'to': to_date,
            'language': 'en',
            'sortBy': 'publishedAt',
            'apiKey': api_key,
            'pageSize': count
        }
        
        try:
            response = requests.get(url, params=params)
            return response.json()
        except Exception as e:
            st.error(f"Error fetching news: {str(e)}")
            return None

    # Show loading spinner while fetching news
    with st.spinner('Fetching latest news...'):
        # Fetch news based on selected category
        query = search_queries[category]
        news_data = fetch_news(query, days_ago, article_count)

    if news_data and news_data.get('status') == 'ok':
        articles = news_data['articles']
        
        # Convert to DataFrame for easier handling
        df = pd.DataFrame(articles)
        
        # Display news cards
        for idx, article in df.iterrows():
            with st.container():
                col1, col2 = st.columns([2, 6])
                
                with col1:
                    if article['urlToImage']:
                        try:
                            st.image(article['urlToImage'], use_column_width=True)
                        except:
                            st.image("https://via.placeholder.com/300x200?text=No+Image", use_column_width=True)
                    else:
                        st.image("https://via.placeholder.com/300x200?text=No+Image", use_column_width=True)
                
                with col2:
                    st.markdown(f"### [{article['title']}]({article['url']})")
                    st.markdown(f"**Source:** {article['source']['name']}")
                    st.markdown(f"**Published:** {article['publishedAt'][:10]}")
                    st.markdown(article['description'])
                
                st.markdown("---")
    else:
        if news_data:
            st.error(f"Error: {news_data.get('message', 'Unknown error')}")
        else:
            st.error("Failed to fetch news data")

if __name__ == "__main__":
    create_news_app()
