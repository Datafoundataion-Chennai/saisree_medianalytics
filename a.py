import streamlit as st
from google.cloud import bigquery
import pandas as pd
import matplotlib.pyplot as plt  
import logging
import os


logging.basicConfig(level=logging.INFO)
logging.info("Dashboard started successfully!")

st.title("Media Analytics Dashboard")


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\dell\Downloads\youtube-analytics-454211-6e15abea6a50.json"


client = bigquery.Client()

# NewsData
@st.cache_data
def load_news_data():
    file_path = r"C:\Users\dell\Desktop\Media\news_category_cleaned.csv"
    temp_df = pd.read_csv(file_path, nrows=5)
    num_columns = temp_df.shape[1]
    if num_columns == 5:
        column_names = ["category", "headline", "authors", "short_description", "date"]
    elif num_columns == 6:
        column_names = ["category", "headline", "authors", "link", "short_description", "date"]
    else:
        st.error(f"Unexpected column count: {num_columns}. Check the dataset format.")
        return pd.DataFrame()
    return pd.read_csv(file_path, names=column_names, header=0)

news_df = load_news_data()
news_df['date'] = pd.to_datetime(news_df['date'], errors='coerce')

 
st.sidebar.header("News Filters")
news_categories = ["All"] + sorted(news_df['category'].dropna().unique().tolist())
selected_news_category = st.sidebar.selectbox("Select News Category", news_categories)

authors = ["All"] + sorted(news_df['authors'].dropna().unique().tolist())
selected_author = st.sidebar.selectbox("Select Author", authors)

news_start_date = st.sidebar.date_input("Start Date", news_df['date'].min())
news_end_date = st.sidebar.date_input("End Date", news_df['date'].max())

search_news_keyword = st.sidebar.text_input("Search in Headlines")

filtered_news_df = news_df[(news_df['date'] >= pd.Timestamp(news_start_date)) & 
                            (news_df['date'] <= pd.Timestamp(news_end_date))]

if selected_news_category != "All":
    filtered_news_df = filtered_news_df[filtered_news_df['category'] == selected_news_category]

if selected_author != "All":
    filtered_news_df = filtered_news_df[filtered_news_df['authors'] == selected_author]

if search_news_keyword:
    filtered_news_df = filtered_news_df[filtered_news_df['headline'].str.contains(search_news_keyword, case=False, na=False)]

st.subheader("Filtered News Articles")
st.dataframe(filtered_news_df)


'''st.subheader("Top 10 News Categories")
top_categories = filtered_news_df['category'].value_counts().head(10)
st.bar_chart(top_categories)'''


st.subheader("Articles Published Per Day")
articles_per_day = filtered_news_df.groupby(filtered_news_df['date'].dt.date).size()
st.line_chart(articles_per_day)


st.subheader("Most Active Authors")
top_authors = filtered_news_df['authors'].value_counts().head(10)
st.bar_chart(top_authors)

st.subheader("Trending News Articles")
for index, row in filtered_news_df.head(5).iterrows():
    st.write(f"**Headline:** {row['headline']}")
    st.write(f"**Author(s):** {row['authors']}")
    st.write(f"**Category:** {row['category']}")
    st.write(f"**Published On:** {row['date'].date()}")
    st.write(f"**Summary:** {row['short_description']}")
    if "link" in news_df.columns and pd.notna(row.get("link")):
        st.write(f"[Read more]({row['link']})")
    st.write("---")