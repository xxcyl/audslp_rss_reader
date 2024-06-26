import streamlit as st
import json
import datetime
import requests
import math

def load_json_data_from_github(repo, file_path):
    """從 GitHub 加載 JSON 數據"""
    url = f"https://raw.githubusercontent.com/{repo}/main/{file_path}"
    response = requests.get(url)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        st.error(f"Failed to load data from GitHub. Status code: {response.status_code}")
        return None

def display_feed(feed_data, feed_name, items_per_page=10):
    """顯示單個 feed 的內容，帶分頁功能"""
    st.write(f"Last updated: {feed_data['feed_updated']}")
    
    total_entries = len(feed_data['entries'])
    total_pages = max(1, math.ceil(total_entries / items_per_page))

    # 先創建一個空的佔位符來顯示分頁控件
    paging_placeholder = st.empty()
    
    # 顯示內容
    entries_placeholder = st.empty()
    
    # 在底部創建分頁控件
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        page = st.number_input(f"頁碼 (共 {total_pages} 頁)", min_value=1, max_value=total_pages, value=1, step=1, key=f"{feed_name}_page")
    
    start_idx = (page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, total_entries)
    
    # 使用 entries_placeholder 顯示內容
    with entries_placeholder.container():
        for entry in feed_data['entries'][start_idx:end_idx]:
            with st.expander(f"**{entry['title']}**\n*{entry['title_translated']}*"):
                st.write(f"Published: {entry['published']}")
                st.markdown(entry['tldr'])
                st.markdown(f"[PubMed]({entry['link']})")
    
    # 使用 paging_placeholder 在頂部顯示當前頁碼信息
    paging_placeholder.write(f"當前頁面: {page} / {total_pages}")
            
def main():
    st.set_page_config(page_title="聽力期刊速報", page_icon="📚")
    st.title("📚 聽力期刊速報")

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
            display_feed(feed_data, feed_name)
        

if __name__ == "__main__":
    main()
