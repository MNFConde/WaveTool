import streamlit as st
from tkinter import filedialog, Tk
from settings_and_function import settings

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
    # st.write(st.session_state[segment_name])

st.header("设置")
st.write("")
path_set('游戏目录', 'game_path', '找到安装目录下的 Wuthering Waves 文件夹', init_path=settings.game_path)
path_set('数据存放目录', 'data_path', init_path=settings.data_path)
path_set('日志存放目录', 'log_path', init_path=settings.game_log_path)
path_set('缓存存放目录', 'cache_path', init_path=settings.cache_path)