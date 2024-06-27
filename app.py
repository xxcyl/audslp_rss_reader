import streamlit as st
import json
import datetime
import requests
import math

# ... [其他函數保持不變] ...

def show_introduction():
    """顯示簡化的系統介紹，包含警語"""
    st.markdown("""
    ## 🌟 主要功能與特點

    - 📰 瀏覽並搜索多個聽力學期刊的最新文章
    - 🌐 提供英文原文和中文翻譯的雙語支持
    - 🧠 每篇文章都有 AI 生成的中文 TL;DR 摘要
    - 📊 按期刊分類查看文章，並顯示文章數量統計
    - ℹ️ 查看文章的中英文標題、發布日期和中文摘要
    - 🔗 直接跳轉到 PubMed 閱讀全文
    - 🔄 定期自動更新，確保獲取最新研究資訊
    
    ## ⚠️ 注意事項

    請注意，AI 處理生成的 TL;DR 摘要和中文翻譯可能存在錯誤或不準確之處。為確保信息的準確性，我們強烈建議您參考原文內容。這些 AI 生成的內容僅供快速瀏覽參考，不應替代對原始研究論文的仔細閱讀和理解。
    """)

def main():
    st.set_page_config(page_title="聽力期刊速報", page_icon="📚", layout="wide")

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
            # 將標題移到側邊欄最上方
            st.title("📚 聽力期刊速報")
            
            # 搜索框
            search_term = st.text_input("🔍 搜索文章 (標題或摘要)", "")
            
            # 將期刊名稱按字母順序排序
            feed_names = sorted(list(data.keys()))
            
            # 使用 checkbox 來選擇期刊，並顯示文章數量
            selected_feeds = []
            for feed in feed_names:
                article_count = len(data[feed]['entries'])
                if st.checkbox(f"{feed} ({article_count})", key=feed):
                    selected_feeds.append(feed)

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
