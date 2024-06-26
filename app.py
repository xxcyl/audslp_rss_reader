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
    """搜索指定 feed 中符合關鍵字的條目"""
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

    # 使用 session_state 來保存當前頁碼
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1

    # 顯示文章列表
    start_idx = (st.session_state.current_page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, total_entries)
    
    st.write(f"顯示第 {start_idx + 1} 到 {end_idx} 篇文章，共 {total_entries} 篇")
    
    for entry, feed_title in all_entries[start_idx:end_idx]:
        with st.expander(f"**{entry['title']}**\n*{entry['title_translated']}* (來自: {feed_title})"):
            st.write(f"Published: {entry['published']}")
            st.markdown(entry['tldr'])
            st.markdown(f"[PubMed]({entry['link']})")

    # 底部分頁控件
    st.write("---")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button("◀◀ 首頁"):
            st.session_state.current_page = 1
            st.experimental_rerun()
    
    with col2:
        if st.button("◀ 上一頁") and st.session_state.current_page > 1:
            st.session_state.current_page -= 1
            st.experimental_rerun()
    
    with col3:
        st.write(f"第 {st.session_state.current_page} 頁，共 {total_pages} 頁")
    
    with col4:
        if st.button("下一頁 ▶") and st.session_state.current_page < total_pages:
            st.session_state.current_page += 1
            st.experimental_rerun()
    
    with col5:
        if st.button("末頁 ▶▶"):
            st.session_state.current_page = total_pages
            st.experimental_rerun()

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
        # 搜索框移到最上方
        search_term = st.text_input("搜索文章 (標題或摘要)", "")
        
        st.write("---")  # 分隔線
        
        # 將 feed 名稱按字母順序排序
        feed_names = sorted(list(data.keys()))
        
        # 使用 checkbox 來選擇 feed
        selected_feeds = []
        for feed in feed_names:
            if st.checkbox(feed, key=feed):
                selected_feeds.append(feed)
        
        st.write("---")  # 分隔線
        st.write("未選擇任何 Feed 時將顯示所有 Feed 的文章")

    # 主內容區
    filtered_data = search_entries(data, search_term, selected_feeds if selected_feeds else None)
    
    if filtered_data:
        total_feeds = len(filtered_data)
        total_articles = sum(len(feed_data['entries']) for feed_data in filtered_data.values())
        if selected_feeds:
            st.write(f"顯示 {total_feeds} 個選定 feed 中的 {total_articles} 篇文章")
        else:
            st.write(f"顯示所有 {total_feeds} 個 feed 中的 {total_articles} 篇文章")
        display_entries(filtered_data)
    else:
        st.write("沒有找到符合條件的文章。")

if __name__ == "__main__":
    main()
