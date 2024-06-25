# streamlit_app.py

import streamlit as st
import json
import datetime
import requests

def load_json_data_from_github(repo, file_path):
    url = f"https://raw.githubusercontent.com/{repo}/main/{file_path}"
    response = requests.get(url)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        st.error(f"Failed to load data from GitHub. Status code: {response.status_code}")
        return None

def display_feed(feed_data):
    st.header(feed_data['feed_title'])
    st.write(f"Last updated: {feed_data['feed_updated']}")
    
    for entry in feed_data['entries']:
        st.subheader(entry['title'])
        st.write(f"Published: {entry['published']}")
        st.write(entry['summary'])
        st.markdown(f"[Read more]({entry['link']})")
        st.markdown("---")

def main():
    st.title("PubMed RSS Reader")

    github_repo = "xxcyl/rss-feed-processor"
    file_path = "rss_data.json"

    data = load_json_data_from_github(github_repo, file_path)
    if data is None:
        return

    tabs = st.tabs(list(data.keys()))

    for tab, (source_name, feed_data) in zip(tabs, data.items()):
        with tab:
            display_feed(feed_data)

    st.sidebar.write(f"Data last processed: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
