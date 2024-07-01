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
    """搜索指定期刊中符合關鍵字的條目"""
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
    """顯示所有選中期刊的條目，帶分頁功能"""
    all_entries = []
    for feed_name, feed_data in data.items():
        all_entries.extend([(entry, feed_name) for entry in feed_data['entries']])
    
    all_entries.sort(key=lambda x: x[0]['published'], reverse=True)
    
    total_entries = len(all_entries)
    total_pages = max(1, math.ceil(total_entries / items_per_page))

    # 確保當前頁碼不超過總頁數
    st.session_state.current_page = min(st.session_state.current_page, total_pages)

    # 計算當前頁的文章範圍
    start_idx = (st.session_state.current_page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, total_entries)
    
    if total_entries > 0:
        # 顯示當前頁的文章
        for entry, feed_name in all_entries[start_idx:end_idx]:
            with st.expander(f"📍 **{entry['title']}**\n*{entry['title_translated']}*"):
                st.write(f"發布日期: {entry['published']}")
                st.markdown(entry['tldr'])
                st.markdown(f"🔗 [PubMed]({entry['link']}) 📚 {feed_name}")

        # 底部分頁控件
        st.write("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            page = st.number_input(f"頁碼 (共 {total_pages} 頁)", min_value=1, max_value=total_pages, value=st.session_state.current_page, step=1, key="page_number")
        
        # 如果頁碼改變，更新 session_state
        if page != st.session_state.current_page:
            st.session_state.current_page = page
            st.experimental_rerun()
    else:
        st.write("沒有找到符合條件的文章。")

def show_introduction():
    """顯示最終更新後的系統介紹，包含警語"""
    st.markdown("""
    ## 🌟 主要功能與特點

    - 瀏覽並搜索聽力學、語言治療及相關跨領域期刊的最新文章
    - 期刊分為：聽力學、語言治療、橫跨兩類，可從側邊欄快速查找
    - 提供英文原文和中文翻譯的雙語支持
    - 每篇文章都有 AI 生成的中文 TL;DR 摘要
    - 顯示每個期刊的文章數量，幫助您了解更新情況
    - 查看文章的中英文標題、發布日期和中文摘要
    - 提供每篇 PubMed 連結
    - 定期自動更新，確保獲取最新研究資訊
    
    ## ⚠️ 注意事項

    請注意，AI 處理生成的 TL;DR 摘要和中文翻譯可能存在錯誤或不準確之處。為確保資訊的準確性，我們強烈建議您參考原文內容。這些 AI 生成的內容僅供快速瀏覽參考，不應替代對原始研究論文的仔細閱讀和理解。
    """)
    
def main():
    st.set_page_config(page_title="聽語期刊速報", page_icon="📚", layout="wide")

    # 初始化 session_state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1
    if 'previous_search' not in st.session_state:
        st.session_state.previous_search = ""
    if 'previous_feeds' not in st.session_state:
        st.session_state.previous_feeds = []

    github_repo = "xxcyl/rss-feed-processor"
    file_path = "rss_data_bilingual.json"
    
    data = load_json_data_from_github(github_repo, file_path)
    if data is None:
        return
    
    # 主要內容區
    tab1, tab2 = st.tabs(["🏠 主頁", "ℹ️ 系統介紹"])
    
    with tab1:
        # 側邊欄：篩選器
        with st.sidebar:
            st.title("📚 聽語期刊速報")
            
            # 搜索框
            search_term = st.text_input("🔍 搜索文章 (標題或摘要)", "")
            
            # 預定義期刊類別
            categories = {
                "聽力學": ["Ear and Hearing", "Hearing Research", "Trends in Hearing", "International Journal of Audiology", "Journal of Audiology and Otology", "American Journal of Audiology", "Seminars in Hearing", "Audiology and Neurotology", "Scientific Reports w/ hearing keyword"],
                "語言治療": ["Dysphagia", "American Journal of Speech-Language Pathology"],
                "橫跨兩類": ["Journal of Speech, Language, and Hearing Research", "Language, Speech, and Hearing Services in Schools"]
            }
            
            selected_feeds = []
            
            # 為每個類別創建一個可折疊的部分
            for category, journals in categories.items():
                with st.expander(f"📂 {category}", expanded=True):
                    for feed in sorted(journals):
                        if feed in data:
                            article_count = len(data[feed]['entries'])
                            if st.checkbox(f"{feed} ({article_count})", key=feed):
                                selected_feeds.append(feed)
            
            # 檢查是否有未分類的期刊
            all_categorized_journals = [j for c in categories.values() for j in c]
            uncategorized_journals = [feed for feed in data.keys() if feed not in all_categorized_journals]
            if uncategorized_journals:
                st.warning(f"警告：以下期刊未被分類：{', '.join(uncategorized_journals)}")

        # 檢查是否需要重置頁碼
        if search_term != st.session_state.previous_search or selected_feeds != st.session_state.previous_feeds:
            st.session_state.current_page = 1
            st.session_state.previous_search = search_term
            st.session_state.previous_feeds = selected_feeds

        # 主內容區
        filtered_data = search_entries(data, search_term, selected_feeds if selected_feeds else None)
        
        if filtered_data:
            total_feeds = len(filtered_data)
            total_articles = sum(len(feed_data['entries']) for feed_data in filtered_data.values())
            
            # 在側邊欄搜索框下方顯示文章統計信息
            with st.sidebar:
                st.write(f"📊 顯示 {total_feeds} 個期刊中的 {total_articles} 篇文章")
                st.write("---")  # 分隔線
            
            display_entries(filtered_data)
        else:
            st.write("沒有找到符合條件的文章。")
    
    with tab2:
        show_introduction()

if __name__ == "__main__":
    main()
