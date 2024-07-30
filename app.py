import streamlit as st
import json
import datetime
import requests
import math
import logging

logging.basicConfig(level=logging.INFO)

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
            entry for entry in feed_data.get('entries', [])
            if not search_term or
            search_term in entry.get('title', '').lower() or
            search_term in entry.get('title_translated', '').lower() or
            search_term in entry.get('tldr', '').lower()
        ]
        
        if filtered_entries:
            result[feed_name] = {
                'feed_title': feed_data.get('feed_title', 'Unknown Feed'),
                'feed_link': feed_data.get('feed_link', '#'),
                'feed_updated': feed_data.get('feed_updated', 'Unknown date'),
                'entries': filtered_entries
            }
    
    return result
    
def display_entries(data, journal_urls, items_per_page=10):
    """顯示所有選中期刊的條目，帶分頁功能"""
    try:
        all_entries = []
        for feed_name, feed_data in data.items():
            all_entries.extend([(entry, feed_name) for entry in feed_data.get('entries', [])])
        
        all_entries.sort(key=lambda x: x[0].get('published', ''), reverse=True)
        
        total_entries = len(all_entries)
        total_pages = max(1, math.ceil(total_entries / items_per_page))

        if 'current_page' not in st.session_state:
            st.session_state.current_page = 1

        st.session_state.current_page = min(st.session_state.current_page, total_pages)

        start_idx = (st.session_state.current_page - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, total_entries)
        
        entries_container = st.container()
        
        if total_entries > 0:
            with entries_container:
                for i, (entry, feed_name) in enumerate(all_entries[start_idx:end_idx], start=1):
                    title = entry.get('title', 'No Title')
                    title_translated = entry.get('title_translated', 'No Translated Title')
                    unique_title = f"**{title}**\n*{title_translated}*"
                    key = f"expander_{st.session_state.current_page}_{i}"
                    logging.info(f"Creating expander with key: {key}")
                    with st.expander(label=unique_title, expanded=False, icon="📍", key=key):
                        st.write(f"發布日期: {entry.get('published', 'Unknown date')}")
                        st.markdown(entry.get('tldr', 'No summary available'))
                        journal_url = journal_urls.get(feed_name, "#")
                        if journal_url != "#":
                            st.markdown(f"🔗 [PubMed]({entry.get('link', '#')}) 📚 [{feed_name}]({journal_url})")
                        else:
                            st.markdown(f"🔗 [PubMed]({entry.get('link', '#')}) 📚 {feed_name}")

            st.write("---")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                def change_page():
                    st.session_state.current_page = st.session_state.new_page
                    st.rerun()

                st.number_input(
                    f"頁碼 (共 {total_pages} 頁)",
                    min_value=1,
                    max_value=total_pages,
                    value=st.session_state.current_page,
                    step=1,
                    key="new_page",
                    on_change=change_page
                )
        else:
            st.write("沒有找到符合條件的文章。")
    except Exception as e:
        logging.error(f"Error in display_entries: {str(e)}")
        st.error("An error occurred while displaying entries. Please try again.")

def show_introduction():
    """顯示最終更新後的系統介紹，包含警語"""
    st.markdown("""
    ## 🌟 主要功能與特點

    - 瀏覽並搜索聽力學、語言治療及相關跨領域期刊的最新文章
    - 期刊分為三類：聽力學、語言治療、橫跨兩類，方便快速查找
    - 提供英文原文和中文翻譯的雙語支持
    - 每篇文章都有 AI 生成的中文 TL;DR 摘要
    - 顯示每個期刊的文章數量，幫助您了解更新情況
    - 查看文章的中英文標題、發布日期和中文摘要
    - 提供每篇 PubMed 連結和期刊官方網站連結
    - 定期自動更新，確保獲取最新研究資訊
    
    ## ⚠️ 注意事項

    請注意，AI 處理生成的 TL;DR 摘要和中文翻譯可能存在錯誤或不準確之處。為確保資訊的準確性，我們強烈建議您參考原文內容。這些 AI 生成的內容僅供快速瀏覽參考，不應替代對原始研究論文的仔細閱讀和理解。
    """)

def main():
    try:
        st.set_page_config(page_title="聽語期刊速報", page_icon="📚", layout="wide")

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
            st.error("Failed to load data from GitHub. Please try again later.")
            return
        
        # 加載期刊配置
        try:
            with open('journal_config.json', 'r', encoding='utf-8') as f:
                journal_config = json.load(f)
        except FileNotFoundError:
            st.error("Journal configuration file not found. Please check your setup.")
            return
        except json.JSONDecodeError:
            st.error("Invalid journal configuration file. Please check the file format.")
            return
        
        # 創建期刊名稱到 URL 的映射
        journal_urls = {j['name']: j['url'] for c in journal_config['categories'].values() for j in c}

        # 將主標題移到 tab 上方
        st.title("📚 聽語期刊速報")

        tab1, tab2 = st.tabs(["🏠 主頁", "ℹ️ 系統介紹"])
        
        with tab1:
            # 搜索框移到主畫面最上方
            search_term = st.text_input("🔍 搜索文章 (標題或摘要)", "", key="search_input")

            # 側邊欄：篩選器
            with st.sidebar:
                st.subheader("期刊選擇")
                
                selected_feeds = []
                
                for category, journals in journal_config['categories'].items():
                    with st.expander(f"📂 {category}", expanded=True):
                        for journal in journals:
                            if journal['name'] in data:
                                article_count = len(data[journal['name']]['entries'])
                                if st.checkbox(f"{journal['name']} ({article_count})", key=f"checkbox_{journal['name']}"):
                                    selected_feeds.append(journal['name'])
                
                all_categorized_journals = [j['name'] for c in journal_config['categories'].values() for j in c]
                uncategorized_journals = [feed for feed in data.keys() if feed not in all_categorized_journals]
                if uncategorized_journals:
                    st.warning(f"警告：以下期刊未被分類：{', '.join(uncategorized_journals)}")

            # 主內容區
            if search_term != st.session_state.previous_search or selected_feeds != st.session_state.previous_feeds:
                st.session_state.current_page = 1
                st.session_state.previous_search = search_term
                st.session_state.previous_feeds = selected_feeds

            filtered_data = search_entries(data, search_term, selected_feeds if selected_feeds else None)
            
            if filtered_data:
                total_feeds = len(filtered_data)
                total_articles = sum(len(feed_data['entries']) for feed_data in filtered_data.values())
                
                st.write(f"📊 顯示 {total_feeds} 個期刊中的 {total_articles} 篇文章")              
                display_entries(filtered_data, journal_urls)
            else:
                st.write("沒有找到符合條件的文章。")
        
        with tab2:
            show_introduction()
    except Exception as e:
        logging.error(f"Error in main function: {str(e)}")
        st.error("An unexpected error occurred. Please try again later.")

if __name__ == "__main__":
    main()
