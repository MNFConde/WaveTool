import streamlit as st
import tkinter as tk
from tkinter import filedialog
from settings_and_function import settings
import pandas as pd

# Set up tkinter
root = tk.Tk()
root.withdraw()
# Make folder picker dialog appear on top of other windows
root.wm_attributes('-topmost', 1)

def path_set(label_name: str, segment_name: str, note: str = '', init_path: str = '') -> str:
    
    if segment_name not in st.session_state:
        st.session_state[segment_name] = init_path
    
    st.markdown('##### ' + label_name)
    
    st.write(note)
    
    dirname_selected = None
    dirname = ''
    col1, col2 = st.columns([4, 1])
    empty_text = col1.empty()
    empty_text.text_input(
        '', 
        st.session_state[segment_name], 
        label_visibility='collapsed', 
        autocomplete='on',
        key=segment_name + 'input' 'a',
    )
    choice = col2.button('浏览文件', key=segment_name + 'button' + 'a')
    if choice:
        dirname_selected = filedialog.askdirectory(master=root)
    dirname = dirname_selected if dirname_selected else dirname
    dirname = empty_text.text_input(
        '', 
        dirname, 
        label_visibility='collapsed', 
        autocomplete='on',
        key=segment_name + 'input' + 'b'
    )
    st.session_state[segment_name] = dirname
    st.write(st.session_state[segment_name])

@st.cache_data
def gacha_records_show():
    st.markdown("#### 数据")
    pages = st.tabs(settings.gacha_type.values())
    for i in settings.gacha_type.keys():
        gacha_name = settings.gacha_type[i]
        page = pages[i - 1]
        with page:
            t = settings.analysis_db.table(gacha_name)
            print(t.all())
            df = pd.DataFrame(t.all())
            st.dataframe(
                df, 
                column_order=[
                    'time',
                    'name',
                    'qualityLevel',
                    'resourceType',
                    'pity_num',
                ],
                column_config={
                    'time': st.column_config.Column(
                        label='日期',
                        width="small"
                    ),
                    'name': st.column_config.Column(
                        label='名称',
                        width="small"
                    ),
                    'qualityLevel': '星级',
                    'resourceType': '类型',
                    'pity_num': '抽数',
                },
                use_container_width=True,
                hide_index=True)

def app_page():
    tab1, tab2 = st.tabs(["抽卡记录", "设置"])
    with tab1:
        st.header("抽卡记录")
        
        subtab1, subtab2 = st.tabs(['数据', '汇总'])
        with subtab1:
            gacha_records_show()
        with subtab2:
            st.markdown("#### 汇总")
        
    with tab2:
        st.header("设置")
        st.write("")
        path_set('游戏目录', 'game_path', '找到安装目录下的 Wuthering Waves 文件夹')
        path_set('数据存放目录', 'data_path')
        path_set('日志存放目录', 'log_path')
        path_set('缓存存放目录', 'cache_path')
        
if __name__ == "__main__":
    app_page()