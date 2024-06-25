import streamlit as st
import feedparser
import datetime

def parse_pubdate(pubdate_str):
    try:
        return datetime.datetime.strptime(pubdate_str, "%a, %d %b %Y %H:%M:%S %Z")
    except ValueError:
        return datetime.datetime.now()

def display_feed(feed):
    st.header(feed.feed.title)
    st.write(f"Last updated: {feed.feed.updated}")

    for entry in feed.entries:
        st.subheader(entry.title)
        st.write(f"Published: {parse_pubdate(entry.published).strftime('%Y-%m-%d %H:%M:%S')}")
        st.write(entry.summary)
        st.markdown(f"[Read more]({entry.link})")
        st.markdown("---")

def main():
    st.title("PubMed Multi-Source RSS Reader")

    rss_sources = {
        "Ear Hear": "https://pubmed.ncbi.nlm.nih.gov/rss/journals/8005585/?limit=15&name=Ear%20Hear&utm_campaign=journals",
        "Hear Res": "https://pubmed.ncbi.nlm.nih.gov/rss/journals/7900445/?limit=15&name=Hear%20Res&utm_campaign=journals"
    }

    tabs = st.tabs(list(rss_sources.keys()))

    for tab, (source_name, rss_url) in zip(tabs, rss_sources.items()):
        with tab:
            feed = feedparser.parse(rss_url)
            display_feed(feed)

if __name__ == "__main__":
    main()
