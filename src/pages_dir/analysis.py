import streamlit as st
import sys
sys.path.append("..")
import settings_and_function as SF
from streamlit_raw_echarts import st_echarts, JsCode

# 每次重新生成，不缓存了

def get_and_analysis():
    db = SF.settings.gacha_db
    