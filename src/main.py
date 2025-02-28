import streamlit as st

pages = {
    "抽卡数据": [
        st.Page(
            "pages_dir/gacha_records.py", 
            title="抽卡记录", 
            icon=":material/dashboard:",
        ),
        st.Page(
            "pages_dir/analysis.py", 
            title="抽卡数据分析",
            icon=":material/analytics:",
        ),
    ], 
    "设置": [
        st.Page(
            "pages_dir/settings.py", 
            title="基本设置", 
            icon=":material/settings:",
        )
    ]
}

nav = st.navigation(pages, expanded=False)
nav.run()