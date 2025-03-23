import streamlit as st
from google.cloud import bigquery
import pandas as pd
import matplotlib.pyplot as plt
import logging
import os

#Logging
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(
    filename=os.path.join(log_dir, "dashboard.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logging.info("Streamlit Dashboard Started")


st.title("Media Analytics Dashboard")


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\dell\Downloads\youtube-analytics-454211-6e15abea6a50.json"
client = bigquery.Client()

@st.cache_data
def fetch_youtube_data():
    logging.info("Fetching YouTube data from BigQuery.")
    try:
        query = """
        SELECT video_id, title, channel_title, category_id, publish_time, views, likes, comment_count, 
            comments_disabled, tags, thumbnail_link, description
        FROM `youtube-analytics-454211.media_analytics.youtube_videos`
        """
        df = client.query(query).to_dataframe()
        df['publish_time'] = pd.to_datetime(df['publish_time']).dt.tz_localize(None)
        logging.info(f"YouTube data loaded successfully with {df.shape[0]} records.")
        return df
    except Exception as e:
        logging.error(f"Error fetching YouTube data: {e}")
        return pd.DataFrame()

youtube_df = fetch_youtube_data()

@st.cache_data
def load_news_data():
    file_path = r"C:\Users\dell\Desktop\Media\news_category_cleaned.csv"
    logging.info("Loading news dataset.")
    
    try:
        temp_df = pd.read_csv(file_path, nrows=5)
        num_columns = temp_df.shape[1]
        
        if num_columns == 5:
            column_names = ["category", "headline", "authors", "short_description", "date"]
        elif num_columns == 6:
            column_names = ["category", "headline", "authors", "link", "short_description", "date"]
        else:
            logging.error(f"Unexpected column count: {num_columns}. Check dataset format.")
            st.error(f"Unexpected column count: {num_columns}. Check dataset format.")
            return pd.DataFrame()
        
        df = pd.read_csv(file_path, names=column_names, header=0)
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        logging.info(f"News data loaded successfully with {df.shape[0]} records.")
        return df
    except Exception as e:
        logging.error(f"Error loading news data: {e}")
        return pd.DataFrame()

news_df = load_news_data()

st.sidebar.header("Filters")

data_selection = st.sidebar.radio("Select Dataset", ("YouTube Analytics", "News Articles"))

if data_selection == "YouTube Analytics":
    logging.info("YouTube Analytics selected.")

    category_options = ["All"] + list(youtube_df['category_id'].astype(str).unique())
    selected_category = st.sidebar.selectbox("Select Category", category_options, key="youtube_category")

    start_date = st.sidebar.date_input("Start Date", youtube_df['publish_time'].min(), key="youtube_start")
    end_date = st.sidebar.date_input("End Date", youtube_df['publish_time'].max(), key="youtube_end")

    channel_options = ["All"] + list(youtube_df['channel_title'].unique())
    selected_channel = st.sidebar.selectbox("Select Channel", channel_options, key="youtube_channel")

    search_keyword = st.sidebar.text_input("Search in Title/Tags", key="youtube_search")

    filtered_df = youtube_df[
        (youtube_df['publish_time'] >= pd.Timestamp(start_date)) & 
        (youtube_df['publish_time'] <= pd.Timestamp(end_date))
    ]

    if selected_category != "All":
        filtered_df = filtered_df[filtered_df['category_id'].astype(str) == selected_category]

    if selected_channel != "All":
        filtered_df = filtered_df[filtered_df['channel_title'] == selected_channel]

    if search_keyword:
        filtered_df = filtered_df[
            filtered_df['title'].str.contains(search_keyword, case=False, na=False) |
            filtered_df['tags'].str.contains(search_keyword, case=False, na=False)
        ]

    logging.info(f"Filtered YouTube data: {filtered_df.shape[0]} records found.")

    st.dataframe(filtered_df)

    x_values = filtered_df["views"]
    y_values = filtered_df["likes"]
    sizes = filtered_df["comment_count"]
    colors = filtered_df["category_id"]

    fig, ax = plt.subplots(figsize=(10, 6))
    scatter = ax.scatter(x_values, y_values, s=sizes, c=colors, cmap='viridis', alpha=0.6)
    ax.set_xlabel("Views")
    ax.set_ylabel("Likes")
    ax.set_title("Scatter Plot (Views vs Likes)")
    st.pyplot(fig)

    top_channels = filtered_df['channel_title'].value_counts().head(10)
    st.bar_chart(top_channels)

    st.subheader("Trending Videos Preview")
    for index, row in filtered_df.head(5).iterrows():
        st.image(row['thumbnail_link'], caption=row['title'])

else:
    logging.info("News Articles selected.")

    news_categories = ["All"] + sorted(news_df['category'].dropna().unique().tolist())
    selected_news_category = st.sidebar.selectbox("Select News Category", news_categories, key="news_category")
    search_news_keyword = st.sidebar.text_input("Search in Headlines", key="news_search")
    news_start_date = st.sidebar.date_input("Start Date", news_df['date'].min(), key="news_start")
    news_end_date = st.sidebar.date_input("End Date", news_df['date'].max(), key="news_end")

    filtered_news_df = news_df[(news_df['date'] >= pd.Timestamp(news_start_date)) & 
                                (news_df['date'] <= pd.Timestamp(news_end_date))]

    if selected_news_category != "All":
        filtered_news_df = filtered_news_df[filtered_news_df['category'] == selected_news_category]

    if search_news_keyword:
        filtered_news_df = filtered_news_df[filtered_news_df['headline'].str.contains(search_news_keyword, case=False, na=False)]

    logging.info(f"Filtered News data: {filtered_news_df.shape[0]} records found.")

    st.subheader("Filtered News Articles")

    records_per_page = 100
    num_pages = max((len(filtered_news_df) // records_per_page) + (1 if len(filtered_news_df) % records_per_page > 0 else 0), 1)
    page_number = st.sidebar.number_input("Page Number", min_value=1, max_value=num_pages, step=1, value=1, key="news_page")

    if filtered_news_df.empty:
        logging.warning("No articles found for selected filters.")
        st.warning("No articles found for the selected filters.")
    else:
        start_idx = (page_number - 1) * records_per_page
        end_idx = min(start_idx + records_per_page, len(filtered_news_df))
        displayed_news_df = filtered_news_df.iloc[start_idx:end_idx]
        st.dataframe(displayed_news_df)

        st.subheader("Articles Published Per Day")
        articles_per_day = filtered_news_df.groupby(filtered_news_df['date'].dt.date).size()
        st.line_chart(articles_per_day)

        st.subheader("Most Active Authors")
        top_authors = filtered_news_df['authors'].value_counts().head(5)
        st.bar_chart(top_authors)

        st.subheader("Trending News Articles")
        for index, row in displayed_news_df.iterrows():
            st.write(f"**Headline:** {row['headline']}")
            st.write(f"**Author(s):** {row['authors']}")
            st.write(f"**Category:** {row['category']}")
            st.write(f"**Published On:** {row['date'].date()}")
            st.write(f"**Summary:** {row['short_description']}")
            if "link" in news_df.columns and pd.notna(row.get("link")):
                st.write(f"[Read more]({row['link']})")
            st.write("---")
