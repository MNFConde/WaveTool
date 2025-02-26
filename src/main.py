import streamlit as st
from tkinter import filedialog, Tk
from settings_and_function import settings
import settings_and_function as SF
import pandas as pd

# Set up tkinter
root = Tk()
root.withdraw()
# Make folder picker dialog appear on top of other windows
root.wm_attributes('-topmost', 1)

def path_set(label_name: str, segment_name: str, note: str = '', init_path: str = '') -> str:
    
    if segment_name not in st.session_state:
        st.session_state[segment_name] = init_path
    
    st.markdown('##### ' + label_name)
    
    st.write(note)
    
    dirname_selected = None
    col1, col2 = st.columns([4, 1])
    empty_text = col1.empty()
    empty_text.text_input(
        label='1', 
        value=st.session_state[segment_name], 
        label_visibility='collapsed', 
        autocomplete='on',
        key=segment_name + 'input' + 'a',
    )
    choice = col2.button('浏览文件', key=segment_name + 'button' + 'a')
    if choice:
        dirname_selected = filedialog.askdirectory(master=root)
    if dirname_selected:
        st.session_state[segment_name] = dirname_selected
    empty_text.text_input(
        label='2', 
        value=st.session_state[segment_name], 
        label_visibility='collapsed', 
        autocomplete='on',
        key=segment_name + 'input' + 'b',
    )
    st.write(st.session_state[segment_name])

@st.cache_data
def gacha_records_show():
    st.markdown("#### 数据")
    pages = st.tabs(settings.gacha_type.values())
    for i in settings.gacha_type.keys():
        gacha_name = settings.gacha_type[i]
        page = pages[i - 1]
        with page:
            levels = (5, 4)
            level_pages = st.tabs(['五星', '四星'])
            for i in range(2):
                level_page = level_pages[i]
                level = levels[i]
                with level_page:
                    # t = settings.analysis_db.table(gacha_name)
                    t = settings.analysis_db.table(
                        SF.data_to_analysis_name_trans(gacha_name, level)
                    )
                    df = pd.DataFrame(t.all()[::-1])
                    df = df.drop('qualityLevel', axis=1)
                    st.dataframe(
                        df, 
                        column_order=[
                            'time',
                            'name',
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
                            'resourceType': '类型',
                            'pity_num': '抽数',
                        },
                        use_container_width=True,
                        hide_index=True
                    )

def data_summary():
    st.markdown("#### 汇总")
    '''
    抽卡数据统计：
        1. 总体评价
            总体抽数，5星出货率，四星出货率，欧非评价
        2. 饼图：
            依据不同的池子的占比，其中在不同的池子中划分5星和四星，
        3. 柱状图：
            依据不同的时间进行分割（天，月，年）来对比抽数
        
    '''
    
    return

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
        path_set('游戏目录', 'game_path', '找到安装目录下的 Wuthering Waves 文件夹', init_path=settings.game_path)
        path_set('数据存放目录', 'data_path', init_path=settings.data_path)
        path_set('日志存放目录', 'log_path', init_path=settings.game_log_path)
        path_set('缓存存放目录', 'cache_path', init_path=settings.cache_path)
        # color = st.color_picker("选择配色")
        # print(color)
        
        
if __name__ == "__main__":
    # color = st.get_option("theme.primaryColor")
    # print(color)
    st.set_option("client.toolbarMode", "auto")
    app_page()