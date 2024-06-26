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

def search_entries(data, search_term, selected_feeds):
    """搜索所選 feed 中符合關鍵字的條目"""
    if not search_term and not selected_feeds:
        return data
    
    result = {}
    search_term = search_term.lower() if search_term else ""
    
    for feed_name, feed_data in data.items():
        if selected_feeds and feed_name not in selected_feeds:
            continue
        
        filtered_entries = [
            entry for entry in feed_data['entries']
            if not search_term or
            search_term in entry['title'].lower() or
            search_term in entry['title_translated'].lower() or
            search_term in entry['tldr'].lower()
        ]
        
        if filtered_entries:
            result[feed_name] = {
                'feed_title': feed_data['feed_title'],
                'feed_link': feed_data['feed_link'],
                'feed_updated': feed_data['feed_updated'],
                'entries': filtered_entries
            }
    
    return result

def display_entries(data, items_per_page=10):
    """顯示所有選中 feed 的條目，帶分頁功能"""
    all_entries = []
    for feed_data in data.values():
        all_entries.extend([(entry, feed_data['feed_title']) for entry in feed_data['entries']])
    
    all_entries.sort(key=lambda x: x[0]['published'], reverse=True)
    
    total_entries = len(all_entries)
    total_pages = max(1, math.ceil(total_entries / items_per_page))

    # 分頁控件
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        page = st.number_input(f"頁碼 (共 {total_pages} 頁)", min_value=1, max_value=total_pages, value=1, step=1)
    
    start_idx = (page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, total_entries)
    
    st.write(f"顯示第 {start_idx + 1} 到 {end_idx} 篇文章，共 {total_entries} 篇")
    
    for entry, feed_title in all_entries[start_idx:end_idx]:
        with st.expander(f"**{entry['title']}**\n*{entry['title_translated']}* (來自: {feed_title})"):
            st.write(f"Published: {entry['published']}")
            st.markdown(entry['tldr'])
            st.markdown(f"[PubMed]({entry['link']})")

def main():
    st.set_page_config(page_title="聽力期刊速報", page_icon="📚", layout="wide")
    st.title("📚 聽力期刊速報")

    github_repo = "xxcyl/rss-feed-processor"
    file_path = "rss_data_bilingual.json"
    
    data = load_json_data_from_github(github_repo, file_path)
    if data is None:
        return
    
    # 側邊欄：篩選器
    with st.sidebar:
        st.header("篩選器")
        feed_names = list(data.keys())
        selected_feeds = st.multiselect("選擇要顯示的 Feed", feed_names, default=feed_names)
        search_term = st.text_input("搜索文章 (標題或摘要)", "")

    # 主內容區
    filtered_data = search_entries(data, search_term, selected_feeds)
    
    if filtered_data:
        total_feeds = len(filtered_data)
        total_articles = sum(len(feed_data['entries']) for feed_data in filtered_data.values())
        st.write(f"顯示 {total_feeds} 個 feed 中的 {total_articles} 篇文章")
        display_entries(filtered_data)
    else:
        st.write("沒有找到符合條件的文章。")

if __name__ == "__main__":
    main()
