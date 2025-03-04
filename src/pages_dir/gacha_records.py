import streamlit as st
from streamlit_raw_echarts import st_echarts, JsCode
from settings_and_function import settings
import settings_and_function as SF
import pandas as pd
import sys
from streamlit_theme import st_theme
sys.path.append("..")
import os
from get_save_gacha_record import get_save_gacha_main
from analysis_gacha_record import AnalysisData
from streamlit_js_eval import streamlit_js_eval

def theme_color():
    theme = st_theme(key="aavvb")
    if theme:
        theme = theme['base']
        if theme == "dark":
            return "#FFFFFF"
        elif theme == "light":
            return "#000000"

    return None

global_color = theme_color()
def echart_gacha_record(df):
    page_wide = streamlit_js_eval(js_expressions='Object.values(document.getElementsByClassName("stVerticalBlock")).map((item)=>item.offsetWidth).reduce((item1, item2)=>item1>item2?item1:item2)')
    print(page_wide)
    options = {
        # "color": [color_from_pity_num(i) for i in df['pity_num']],
        "xAxis": {
            "show": False, 
        },
        "yAxis": [
            {
                "data": [{
                    "value": i,
                    "textStyle": {
                        "fontWeight": "bolder",
                        "fontSize": 15,
                        "color": global_color,
                    }
                } for i in list(df['name'])],
                "axisLine": {
                    "show": False,
                },
                "axisTick": {
                    "show": False,
                },
            },
            {
                "data": [{
                    "value": i,
                    "textStyle": {
                        "fontWeight": "bolder",
                        "fontSize": 15,
                        "color": global_color,
                    }
                } for i in list(df['pity_num'])],
                "axisLine": {
                    "show": False,
                },
                "axisTick": {
                    "show": False,
                },
            },
        ],
        "animation": False,
        "tooltip": {
            "show": True,
            "trigger": "item",
            "showContent": True,
            "triggerOn": "mousemove",
            "formatter": JsCode('''function(params){return params.name+'<br>抽数：'+ params.data.value +'<br>时间：'+ params.data.time}''')
        },
        "series": [
            {
                "name": "抽数",
                "type": "bar",
                "zlevel": 1,
                "data": [
                    {
                        "value": int(df["pity_num"][i]),
                        "time": df['time'][i],
                        "itemStyle": {
                            "color": 'red' if int(df["pity_num"][i]) > 70 else 'green',
                            "barBorderRadius": 30,
                        }
                    } for i in range(len(df))
                ],
                "barWidth": 20,
                "barCategoryGap": 5,
            },
            {
                "name": "背景",
                "type": "bar",
                "barWidth": 20,
                "barCategoryGap": 5,
                "barGap": '-100%',
                "data": [
                    {
                        "value": 90,
                        "time": df['time'][i],
                        "itemStyle": {
                            "normal": {
                                "color": "#eee",
                                "barBorderRadius": 30,
                                "opacity": 0,
                            },
                        }
                            
                    } for i in range(len(df))
                ],
                "tooltip": {
                    "show": False,
                },
                "emphasis": {
                    "disabled": True,
                },
                "select": {
                    "disabled": True,
                },
                "legendHoverLink": False,
                
            },
        ]
    }
    st_echarts(
        option=options,
        width=700,
        height=str(len(df) * 40 + 120) + "px",
    )

def color_from_pity_num(num: int):
    if type(num) == str:
        num = int(num)
    if num >= 70:
        return "#7e403f"
    else:
        return "#30835f"

def gacha_record_show():
    st.markdown("#### 数据展示")
    four = st.checkbox('展示四星')
    eql = st.columns(len(settings.gacha_type.keys()), gap="small")
    button_list = []
    for i in range(len(settings.gacha_type.keys())):
        with eql[i]:
            gacha_name = settings.gacha_type[i + 1]
            button_list.append(st.button(gacha_name, use_container_width=True))
    for i in range(len(button_list)):
        if button_list[i]:
            break
        elif i == len(button_list) - 1:
            i = 0
    
    gacha_name = settings.gacha_type[i + 1]
    if four:
        levels = (5, 4)
        level_pages = ['五星', '四星']
    else:
        levels = (5, )
        level_pages = ['五星', ]
    for i in range(len(levels)):
        level_page = level_pages[i]
        level = levels[i]
        st.markdown("##### " + gacha_name + level_page)
        t = settings.analysis_db.table(
            SF.data_to_analysis_name_trans(gacha_name, level)
        )
        df = pd.DataFrame(t.all())
        df = df.drop('qualityLevel', axis=1)
        echart_gacha_record(df)
            

def get_gacha_records():
    st.markdown("#### 获取记录")
    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button("获取记录"):
            get_save_gacha_main()
    with b2:
        if st.button("重新分析记录"):
            os.remove(settings.analysis_db_path)
            a = AnalysisData()
            a.save_analysis_result(a.analysis_gacha_records())
    with b3:
        if st.button("获取并分析记录"):
            get_save_gacha_main()
            a = AnalysisData()
            a.save_analysis_result(a.analysis_gacha_records())

st.header("抽卡记录")

get_gacha_records()
gacha_record_show()