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

def display_feed(feed_data, feed_name, page=1, items_per_page=10):
    """顯示單個 feed 的內容，帶分頁功能"""
    st.write(f"Last updated: {feed_data['feed_updated']}")
    
    total_entries = len(feed_data['entries'])
    total_pages = math.ceil(total_entries / items_per_page)
    
    start_idx = (page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, total_entries)
    
    for entry in feed_data['entries'][start_idx:end_idx]:
        with st.expander(f"**{entry['title']}**\n*{entry['title_translated']}*"):
            st.write(f"Published: {entry['published']}")
            st.markdown(entry['tldr'])
            st.markdown(f"[PubMed]({entry['link']})")
    
    # 分頁控制
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("首頁", key=f"{feed_name}_first", disabled=(page == 1)):
            st.session_state[f"{feed_name}_page"] = 1
    with col2:
        if st.button("上一頁", key=f"{feed_name}_prev", disabled=(page == 1)):
            st.session_state[f"{feed_name}_page"] -= 1
    with col3:
        st.write(f"第 {page} 頁，共 {total_pages} 頁")
    with col4:
        if st.button("下一頁", key=f"{feed_name}_next", disabled=(page == total_pages)):
            st.session_state[f"{feed_name}_page"] += 1
    with col5:
        if st.button("末頁", key=f"{feed_name}_last", disabled=(page == total_pages)):
            st.session_state[f"{feed_name}_page"] = total_pages

def main():
    st.set_page_config(page_title="PubMed RSS 閱讀器", page_icon="📚")
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
            # 初始化或更新分頁狀態
            if f"{feed_name}_page" not in st.session_state:
                st.session_state[f"{feed_name}_page"] = 1
            display_feed(feed_data, feed_name, st.session_state[f"{feed_name}_page"])
    
    st.sidebar.write(f"數據最後處理時間: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
