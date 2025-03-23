import streamlit as st
from google.cloud import bigquery
import pandas as pd
import matplotlib.pyplot as plt  
import logging
import os


logging.basicConfig(level=logging.INFO)
logging.info("Dashboard started successfully!")


st.title("Media Analytics Dashboard")

# Google Cloud details 
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\dell\Downloads\youtube-analytics-454211-6e15abea6a50.json"


client = bigquery.Client() 


@st.cache_data
def fetch_data():
    query = """
    SELECT video_id, title, channel_title, category_id, publish_time, views, likes, comment_count, 
        comments_disabled, tags, thumbnail_link, description
    FROM youtube-analytics-454211.media_analytics.youtube_videos
    """
    return client.query(query).to_dataframe()

df = fetch_data()


df['publish_time'] = pd.to_datetime(df['publish_time']).dt.tz_localize(None)


st.sidebar.header("Filters")


category_options = ["All"] + list(df['category_id'].astype(str).unique())
selected_category = st.sidebar.selectbox("Select Category", category_options)


start_date = st.sidebar.date_input("Start Date", df['publish_time'].min())
end_date = st.sidebar.date_input("End Date", df['publish_time'].max())


channel_options = ["All"] + list(df['channel_title'].unique())
selected_channel = st.sidebar.selectbox("Select Channel", channel_options)


search_keyword = st.sidebar.text_input("Search in Title/Tags")


filtered_df = df[
    (df['publish_time'] >= pd.Timestamp(start_date)) & 
    (df['publish_time'] <= pd.Timestamp(end_date))
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


st.dataframe(filtered_df)


x_values = filtered_df["views"]
y_values = filtered_df["likes"]
sizes = filtered_df["comment_count"]  
colors = filtered_df["category_id"]   


fig, ax = plt.subplots(figsize=(10, 6))  
scatter = ax.scatter(
    x_values, y_values,
    s=sizes, c=colors, cmap='viridis', alpha=0.6  
)


ax.set_xlabel("Views")
ax.set_ylabel("Likes")
ax.set_title("Scatter Plot (Views vs Likes)")


st.pyplot(fig)

 
top_channels = filtered_df['channel_title'].value_counts().head(10)
st.bar_chart(top_channels)


st.subheader("Trending Videos Preview")
for index, row in filtered_df.head(5).iterrows():
    st.image(row['thumbnail_link'], caption=row['title'])