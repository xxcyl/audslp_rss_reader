import streamlit as st
import feedparser
import datetime

def parse_pubdate(pubdate_str):
    try:
        return datetime.datetime.strptime(pubdate_str, "%a, %d %b %Y %H:%M:%S %Z")
    except ValueError:
        return datetime.datetime.now()

def main():
    st.title("PubMed RSS Reader")

    rss_url = "https://pubmed.ncbi.nlm.nih.gov/rss/journals/8005585/?limit=15&name=Ear%20Hear&utm_campaign=journals"
    
    feed = feedparser.parse(rss_url)

    st.header(feed.feed.title)
    st.write(f"Last updated: {feed.feed.updated}")

    for entry in feed.entries:
        st.subheader(entry.title)
        st.write(f"Published: {parse_pubdate(entry.published).strftime('%Y-%m-%d %H:%M:%S')}")
        st.write(entry.summary)
        st.markdown(f"[Read more]({entry.link})")
        st.markdown("---")

if __name__ == "__main__":
    main()
