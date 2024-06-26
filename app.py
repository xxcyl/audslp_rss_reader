import streamlit as st
import json
import datetime
import requests

def load_json_data_from_github(repo, file_path):
    """從 GitHub 加載 JSON 數據"""
    url = f"https://raw.githubusercontent.com/{repo}/main/{file_path}"
    response = requests.get(url)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        st.error(f"Failed to load data from GitHub. Status code: {response.status_code}")
        return None

def display_feed(feed_data):
    """顯示單個 feed 的內容"""
    st.write(f"Last updated: {feed_data['feed_updated']}")
    
    for entry in feed_data['entries']:
        # 使用標題和翻譯標題作為展開器的標題
        with st.expander(f"**{entry['title']}**\n*{entry['title_translated']}*"):
            st.write(f"Published: {entry['published']}")
            
            # 顯示 TL;DR 摘要
            st.markdown(entry['tldr'])
            
            # 顯示 PubMed 鏈接
            st.markdown(f"[PubMed]({entry['link']})")

def main():
    st.set_page_config(page_title="PubMed RSS 閱讀器", page_icon="📚", layout="wide")
    st.title("PubMed RSS 閱讀器")

    github_repo = "xxcyl/rss-feed-processor"
    file_path = "rss_data_bilingual.json"
    
    data = load_json_data_from_github(github_repo, file_path)
    if data is None:
        return
    
    # 創建標籤
    tabs = st.tabs(list(data.keys()))
    
    # 在每個標籤中顯示相應的 feed
    for tab, (feed_name, feed_data) in zip(tabs, data.items()):
        with tab:
            st.header(feed_name)
            display_feed(feed_data)
    
    st.sidebar.write(f"數據最後處理時間: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
