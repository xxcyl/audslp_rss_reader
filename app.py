import streamlit as st
import feedparser
import datetime
import time
import json
import os

@st.cache_data(ttl=600)  # Cache for 10 minutes
def fetch_feed(url):
    return feedparser.parse(url)

def parse_pubdate(pubdate_str):
    try:
        return datetime.datetime.strptime(pubdate_str, "%a, %d %b %Y %H:%M:%S %Z")
    except ValueError:
        return datetime.datetime.now()

def load_data(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return {}

def save_data(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f)

def update_feed_data(feed, existing_data):
    feed_data = existing_data.get(feed.feed.title, [])
    new_entries = []
    for entry in feed.entries:
        entry_data = {
            'title': entry.title,
            'published': entry.published,
            'summary': entry.summary,
            'link': entry.link
        }
        if entry_data not in feed_data:
            new_entries.append(entry_data)
    feed_data = new_entries + feed_data  # 新條目加到前面
    return feed_data

def display_feed(feed_data, limit=15):
    for entry in feed_data[:limit]:
        st.subheader(entry['title'])
        st.write(f"Published: {parse_pubdate(entry['published']).strftime('%Y-%m-%d %H:%M:%S')}")
        st.write(entry['summary'])
        st.markdown(f"[Read more]({entry['link']})")
        st.markdown("---")

def main():
    st.title("PubMed Multi-Source RSS Reader with History")

    rss_sources = {
        "Ear Hear": "https://pubmed.ncbi.nlm.nih.gov/rss/journals/8005585/?limit=15&name=Ear%20Hear&utm_campaign=journals",
        "Hear Res": "https://pubmed.ncbi.nlm.nih.gov/rss/journals/7900445/?limit=15&name=Hear%20Res&utm_campaign=journals"
    }

    data_file = 'rss_history.json'
    feed_data = load_data(data_file)

    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = time.time()

    refresh = st.button("Refresh RSS Feeds")

    if refresh:
        st.session_state.last_refresh = time.time()
        for source_name, rss_url in rss_sources.items():
            feed = fetch_feed(rss_url)
            feed_data[source_name] = update_feed_data(feed, feed_data)
        save_data(feed_data, data_file)
        st.experimental_rerun()

    st.write(f"Last refreshed: {datetime.datetime.fromtimestamp(st.session_state.last_refresh).strftime('%Y-%m-%d %H:%M:%S')}")

    tabs = st.tabs(list(rss_sources.keys()))

    for tab, source_name in zip(tabs, rss_sources.keys()):
        with tab:
            st.header(source_name)
            if source_name in feed_data:
                display_feed(feed_data[source_name])
            else:
                st.write("No data available. Please refresh.")

    # 顯示歷史數據的選項
    st.sidebar.header("Historical Data")
    selected_source = st.sidebar.selectbox("Select Source", list(rss_sources.keys()))
    num_entries = st.sidebar.slider("Number of entries to show", 1, 100, 15)

    if selected_source in feed_data:
        st.sidebar.subheader(f"Showing {num_entries} entries from {selected_source}")
        display_feed(feed_data[selected_source], num_entries)
    else:
        st.sidebar.write("No historical data available for this source.")

if __name__ == "__main__":
    main()
