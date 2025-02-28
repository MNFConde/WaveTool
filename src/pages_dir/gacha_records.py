import streamlit as st
from streamlit_raw_echarts import st_echarts, JsCode
from settings_and_function import settings
import settings_and_function as SF
import pandas as pd
import sys
sys.path.append("..")
from get_save_gacha_record import get_save_gacha_main
from analysis_gacha_record import AnalysisData


def echart_gacha_record(df):
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
                # "label": {
                #     "show": True,
                #     "position": "right",
                # },  
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
                        "value": 100,
                        "time": df['time'][i],
                        "itemStyle": {
                            "normal": {
                                "color": "#eee",
                                "barBorderRadius": 30,
                            },
                        }
                            
                    } for i in range(len(df))
                ],
                "tooltip": {
                    "show": False,
                },
                "emphasis": {
                    "disabled": True,
                }
            },
        ]
    }
    st_echarts(
        option=options,
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
    st.markdown("#### 数据")
    four = st.checkbox('展示四星')
    for i in settings.gacha_type.keys():
        gacha_name = settings.gacha_type[i]
        if four:
            levels = (5, 4)
            level_pages = ['五星', '四星']
        else:
            levels = (5, )
            level_pages = ['五星', ]
        for i in range(len(levels)):
            level_page = level_pages[i]
            st.markdown("##### " + gacha_name + level_page)
            level = levels[i]
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
        if st.button("分析记录"):
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