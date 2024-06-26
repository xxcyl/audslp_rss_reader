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
        # 使用標題和翻譯標題作為展開器的標題
        with st.expander(f"**{entry['title']}**\n*{entry['title_translated']}*"):
            st.write(f"Published: {entry['published']}")
            
            # 顯示 TL;DR 摘要
            st.markdown(entry['tldr'])
            
            # 顯示原文鏈接
            st.markdown(f"[閱讀原文]({entry['link']})")
        
        st.markdown("---")

def main():
    st.title("PubMed RSS 閱讀器")
    
    github_repo = "xxcyl/rss-feed-processor"
    file_path = "rss_data_bilingual.json"
    
    data = load_json_data_from_github(github_repo, file_path)
    if data is None:
        return
    
    # 創建側邊欄選擇器
    selected_feed = st.sidebar.selectbox(
        "選擇 RSS feed",
        options=list(data.keys())
    )
    
    # 顯示選定的 feed
    if selected_feed in data:
        display_feed(data[selected_feed])
    else:
        st.write("請從側邊欄選擇一個 feed。")
    
    st.sidebar.write(f"數據最後處理時間: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
