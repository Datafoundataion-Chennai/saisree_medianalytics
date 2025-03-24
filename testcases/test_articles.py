import unittest
import pandas as pd


def fetch_youtube_data():
    """Mock function to fetch YouTube data"""
    data = {
        "video_id": ["vid1", "vid2"],
        "title": ["Video A", "Video B"],
        "channel_title": ["Channel 1", "Channel 2"],
        "category_id": [1, 2],
        "publish_time": [pd.Timestamp("2023-05-01"), pd.Timestamp("2023-06-01")],
        "views": [1000, 2000],
        "likes": [100, 200],
        "comment_count": [10, 20],
        "comments_disabled": [False, True],
        "tags": ["tag1,tag2", "tag3,tag4"],
        "thumbnail_link": ["link1", "link2"],
        "description": ["Desc A", "Desc B"]
    }
    return pd.DataFrame(data)

def load_news_data():
    """Mock function to load News data"""
    data = {
        "category": ["Politics", "Sports"],
        "headline": ["Election updates", "Football final"],
        "authors": ["Author A", "Author B"],
        "short_description": ["Latest election news", "Final match review"],
        "date": [pd.Timestamp("2023-05-01"), pd.Timestamp("2023-06-01")]
    }
    return pd.DataFrame(data)

class TestMediaAnalyticsDashboard(unittest.TestCase):
    
    def test_fetch_youtube_data(self):
        """Test if YouTube data loads correctly"""
        df = fetch_youtube_data()
        self.assertFalse(df.empty, "YouTube DataFrame is empty!")
        expected_columns = ["video_id", "title", "channel_title", "category_id", "publish_time", "views", "likes", 
                            "comment_count", "comments_disabled", "tags", "thumbnail_link", "description"]
        self.assertTrue(set(expected_columns).issubset(df.columns), "YouTube DataFrame missing expected columns")
    
    def test_load_news_data(self):
        """Test if News data loads correctly"""
        df = load_news_data()
        self.assertFalse(df.empty, "News DataFrame is empty!")
        expected_columns = ["category", "headline", "authors", "short_description", "date"]
        self.assertTrue(set(expected_columns).issubset(df.columns), "Unexpected News DataFrame column format!")
    
    def test_youtube_data_filtering_by_date(self):
        """Test YouTube data filtering by date range"""
        df = fetch_youtube_data()
        start_date, end_date = pd.Timestamp("2023-01-01"), pd.Timestamp("2023-12-31")
        filtered_df = df[(df['publish_time'] >= start_date) & (df['publish_time'] <= end_date)]
        self.assertTrue((filtered_df['publish_time'] >= start_date).all() and 
                        (filtered_df['publish_time'] <= end_date).all(), "YouTube date filtering failed!")
    
    def test_news_data_filtering_by_category(self):
        """Test News data filtering by category"""
        df = load_news_data()
        category = "Politics"
        filtered_df = df[df['category'] == category]
        self.assertTrue((filtered_df['category'] == category).all(), "News category filtering failed!")
    
    def test_news_data_search_by_keyword(self):
        """Test News data search functionality"""
        df = load_news_data()
        keyword = "Election"
        filtered_df = df[df['headline'].str.contains(keyword, case=False, na=False)]
        self.assertTrue(all(keyword.lower() in str(title).lower() for title in filtered_df['headline']), 
                        "News keyword search failed!")

if __name__ == '__main__':
    unittest.main()
