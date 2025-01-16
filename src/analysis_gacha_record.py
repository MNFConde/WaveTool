from settings import settings
from tinydb import Query, TinyDB
import json
from datetime import datetime
from pprint import pprint

'''
{
    'cardPoolType': '角色精准调谐', --> setting.gacha_type
    'resourceId': 21030023, 
    'qualityLevel': 3,             --> [3, 4, 5]
    'resourceType': '武器',         --> [武器, 角色]
    'name': '源能佩枪·测叁', 
    'count': 1, 
    'time': '2024-08-02 23:46:33'
}

功能：
    1. 遍历指定时间段的数据（通过

'''

# print(settings.time_format)
# settings.time_format = '1'
# print(settings.time_format)

# print(settings.gacha_db.table(settings.gacha_type[1]).search(settings.gacha_records.qualityLevel == 5))

'''
{
    "name": {
        level: 3 | 4 | 5,
        num: 0 ~ 180,
        guarantee_type: None(level<5，除了up角色池以外的其它池子) | soft_guarantee | hard_guarantee,
        pity: 超级欧皇(0~14) | 欧皇(14~28) | 小欧皇(28~45) | 运气很好(45~64) | 一般(64~73) | 运气不佳(73~76) | 百里挑一的非酋(76~80)
    }
}
'''

class AnalysisData:
    def __init__(self):
        self.analysis_cache = settings.cache_path + "/analysis_cache"
        self.analysis_db_path = self.analysis_cache + "/analysis_result.json"
        # 下面这里要加上 create_dirs = True，用来保证文件所在的文件夹一定会存在
        self.analysis_db = TinyDB(self.analysis_db_path, create_dirs = True)
        
    def analysis_progress(self, time_limit_tuple: tuple = (None, None,)):
        db_tables_name = settings.gacha_db.tables()
        a = [
            settings.gacha_db.table(i).search(
                (
                    (Query().qualityLevel == 5) 
                    | (Query().qualityLevel == 4)
                )
                & Query().time.test(self.time_func(time_limit_tuple))
            ) for i in db_tables_name
        ]
        db_analysis_dict = dict(
            zip(
                db_tables_name, [
                    list(
                        map(
                            lambda i: (
                                i['name'], 
                                i.doc_id, 
                                i['qualityLevel'], 
                                i['resourceType'],
                                i['time']
                            ), 
                            doc,
                        )
                    ) for doc in a
                ]
            )
        )
        return (db_analysis_dict)
    
    @staticmethod
    def time_func(time_limit_tuple):
        if time_limit_tuple[0] and time_limit_tuple[1]:
            def time_test(time_str):
                pointed_time = datetime.strptime(time_str, settings.time_format)
                return  datetime.strptime(time_limit_tuple[0], settings.time_format) < pointed_time < datetime.strptime(time_limit_tuple[1], settings.time_format)
        elif not time_limit_tuple[0] and time_limit_tuple[1]:
            def time_test(time_str):
                pointed_time = datetime.strptime(time_str, settings.time_format)
                return pointed_time < datetime.strptime(time_limit_tuple[1], settings.time_format)
        elif time_limit_tuple[1] and not time_limit_tuple[0]:
            def time_test(time_str):
                pointed_time = datetime.strptime(time_str, settings.time_format)
                return datetime.strptime(time_limit_tuple[0], settings.time_format) < pointed_time
        else:
            def time_test(time_str):
                return True
        return time_test


a = AnalysisData()
pprint(a.analysis_progress())