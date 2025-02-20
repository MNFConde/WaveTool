from settings_and_function import settings
import settings_and_function as SF
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
        
    def analysis_gacha_records(self, levels_list: list = [4, 5], time_limit_tuple: tuple = (None, None)):
        db_tables_name = settings.gacha_db.tables()
        search_list_sum = 0
        db_analysis_dict = dict()
        for level in levels_list:
            
            # 扩展搜索，在搜索的时候完成抽数计算与文档项过滤
            # search_list= [self.search_extend(level, table_name, time_limit_tuple) for table_name in db_tables_name]
            search_doc_dict= {
                self.data_to_analysis_name_trans(table_name, level): self.search_extend(level, table_name, time_limit_tuple) for table_name in db_tables_name}
            # search_list_sum += sum(list(map(lambda i: len(i), search_list)))
            search_list_sum += sum(list(map(lambda i: len(i), search_doc_dict.values())))
            db_analysis_dict.update(search_doc_dict)
            # db_analysis_dict.update(
            #     dict(
            #         zip(
            #             map(
            #                 lambda i: self.data_to_analysis_name_trans(i, level),
            #                 db_tables_name,
            #             ),
            #             [
            #                 list(
            #                     self.pity_calculate(
            #                         map(
            #                             lambda i: [
            #                                 i['name'], 
            #                                 i.doc_id,   # 在这里将 doc_id 提出来
            #                                 i['qualityLevel'], 
            #                                 i['resourceType'],
            #                                 i['time']
            #                             ], 
            #                             doc_list,
            #                         )
            #                     )
            #                 ) for doc_list in search_list
            #             ]
            #         )
            #     )
            # )
        print(search_list_sum)
        return db_analysis_dict

    def save_analysis_result(self, result_dict):
        # db = settings.analysis_db
        db = self.analysis_db
        # 之后的存储以传进来的字典的 key 为准
        tables_name = result_dict.keys()
        print("一共有 {} 个表".format(len(tables_name)))
        for name in tables_name:
            # insert_analysis_records = list(map(
            #     lambda i: dict(zip(
            #         ['name', 'doc_id', 'qualityLevel', 'resourceType', 'time', 'pity_num'],
            #         i,
            #     )),
            #     result_dict[name],
            # ))
            insert_analysis_records = result_dict[name]
            self.remove_yidian_record(db, name)
            # print("缓存了{} 条".format(SF.sorted_insert_or_update(
            #     db, 
            #     name, 
            #     insert_analysis_records, 
            #     settings.get_table_time(db, name),
            # )))
            table = db.table(name)
            print(table.insert_multiple(insert_analysis_records))
            print(len(insert_analysis_records))
        print(SF.calculate_db_len(db))

    @staticmethod
    def pity_calculate(doc_list) -> list:
        if type(doc_list) == map:
            doc_list = list(doc_list)
        if len(doc_list) == 0:
            return []
        doc_list[0].append(doc_list[0][1])
        result = [doc_list[0]]
        for ind, doc in enumerate(doc_list[1:], start=1):
            pity_num = doc[1] - doc_list[ind - 1][1]
            doc.append(pity_num)
            result.append(doc)
        
        # 这里处理最后一条记录的情况，无论记录是什么，都是多出来辅助计算垫抽数的，所以要修改记录为已垫
        result[-1][:4] = ['已垫', '-', '-', '-']
        return result    
    
    @staticmethod
    def pity_calculate_dict(doc_list: list) -> list:
        '''
        doc_list: list[TinyDBDocument]
        '''
        dict_keys = ('name', 'doc_id', 'qualityLevel', 'resourceType')
        dict_values = ('已垫', '-', '-', '-')
        
        if type(doc_list) == map:
            doc_list = list(doc_list)
        
        if len(doc_list) < 2:
            if len(doc_list) == 1:
                for i in range(4):
                    doc_list[-1][dict_keys[i]] = dict_values[i]
            return doc_list
        
        doc_list[0]['pity_num'] = doc_list[0].doc_id
        doc_list[0]['doc_id'] = doc_list[0].doc_id
        result = [doc_list[0]]
        for ind, doc in enumerate(doc_list[1:], start=1):
            pity_num = doc.doc_id - doc_list[ind - 1].doc_id
            doc['pity_num'] = pity_num
            doc['doc_id'] = doc.doc_id
            result.append(doc)
        
        # 这里处理最后一条记录的情况，无论记录是什么，都是多出来辅助计算垫抽数的，所以要修改记录为已垫
        
        for i in range(4):
            result[-1][dict_keys[i]] = dict_values[i]
        
        return result    
    
    @staticmethod
    def data_to_analysis_name_trans(data_table_name: str, level: int):
        return data_table_name + '_lv' + str(level)
    
    @staticmethod
    def remove_yidian_record(database, table_name):
        '''
        去除数据库中的已垫记录（最后一条）
        '''
        table = database.table(table_name)
        if len(table) != 0:
            table.remove(doc_ids=[len(table)])
    
    def search_extend(self, level: int, data_table_name: str, time_limit_tuple: tuple) -> list:
        '''
        在最后额外加入最新的记录，以便后续的处理计算
        加入判断功能（doc_id），使得其可以读取已有的处理结果而不必反复处理
        加入抽数计算部分
        加入文档项过滤部分
        -> list[dict{'name', 'doc_id', 'qualityLevel', 'resourceType', 'time', 'pity_num'}]
        '''
        # 查询符合等级要求的记录
        focus_table = settings.gacha_db.table(data_table_name)
        search_docs_list = focus_table.search(
            (
                (Query().qualityLevel == level) 
            )
            & Query().time.test(self.time_func(time_limit_tuple))
        )
        
        # 获取之前的分析结果的倒数第二个记录的 doc_id
        analysis_table_name = self.data_to_analysis_name_trans(data_table_name, level)
        if analysis_table_name in self.analysis_db.tables():
            analysis_target_table = self.analysis_db.table(analysis_table_name)
            exist_second_last_doc = analysis_target_table.get(doc_id = len(analysis_target_table) - 1)
            exist_second_last_doc_id = exist_second_last_doc['doc_id'] if exist_second_last_doc else 0
        else:
            exist_second_last_doc_id = 0
        search_docs_list = [i for i in search_docs_list if i.doc_id > exist_second_last_doc_id]
        last_doc = focus_table.get(doc_id=len(focus_table))
        
        # 直接在这一步就进行抽数计算
        # 如果 search_docs_list 为空，抽数计算需要特别处理
        '''
        00: {'cardPoolType': '武器精准调谐', 'resourceId': 21020024, 'qualityLevel': 4, 'resourceType': '武器', 'name': '行进序曲', 'count': 1, 'time': '2024-07-27 15:56:59'}
        '''
        # last_doc 存在：可能有记录更新也可能没有，所以search_docs_list可能存在可能不存在
        # last_doc 不存在：之前没有进行过分析，一定存在 search_docs_list 
        if last_doc:
            if not search_docs_list:
                last_doc['pity_num'] = last_doc.doc_id - exist_second_last_doc_id
                last_doc['doc_id'] = last_doc.doc_id
                search_docs_list.append(last_doc)
            else:
                search_docs_list.append(last_doc)
        
        search_docs_list = self.pity_calculate_dict(search_docs_list)
        needed_values = ('name', 'doc_id', 'qualityLevel', 'resourceType', 'time', 'pity_num')
        
        # 过滤出需要的项
        search_docs_list = list(
            map(
                lambda i: {doc_key: doc_value for doc_key, doc_value in i.items() if doc_key in needed_values},
                search_docs_list
            )
        )
        return search_docs_list
    
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
# pprint(a.analysis_gacha_records())
a.save_analysis_result(a.analysis_gacha_records())


