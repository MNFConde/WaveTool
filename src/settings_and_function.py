from tinydb import TinyDB, Query
from datetime import datetime
import os


# gacha_db = TinyDB('./gacha_database.json')
# gacha_records = Query()

# file_path = r"D:\game\鸣潮\Wuthering Waves\Wuthering Waves Game\Client\Saved\Logs\Client.log"
# url_api = '''https://gmserver-api.aki-game2.com/gacha/record/query'''
# url_api_2 = '''https://coapi.cn/v1/mc/gacha.php'''
# # save_path = r"D:\software\启动器\log_save.json"

# post_header = {
#     "User-Agent": "Mozilla/5.0",
#     "Content-Type": "application/json",
# }

# gacha_type = {
#     1: "UP角色池",
#     2: "UP武器池",
#     3: "常驻角色池",
#     4: "常驻武器池",
#     5: "新手池",
#     6: "新手自选池",
#     7: "感恩自选池",
# }

# time_format = r'%Y-%m-%d %H:%M:%S'

# init_args = {
#     "game_path"  : "",
#     "data_path"  : './',
#     "log_path"   : './log',
#     "cache_path" : './cache',
#     "database_lastest_record_time" : '1970-01-01 00:00:00',
#     "analysis_lastest_record_time" : '1970-01-01 00:00:00',
# }

class WaveToolArgs():
    '''
    一个参数类
        1. 记录参数，并且保持全局一致
        2. 作为设置项，可以热更新，并且在更新时向参数json中存入一份
        3. 初始时若没有进行设置，使用标志来判断是否可以使用某种功能
    记录同样放入数据库中
        4. 记录时间，包括数据库中记录的最新时间以及数据分析过的数据中最新的记录的时间
    '''
    def __init__(self):
        self.args_json_path = './args.json'
        self.args_db = TinyDB(self.args_json_path)
        self.url_api = '''https://gmserver-api.aki-game2.com/gacha/record/query'''
        self.url_api_2 = '''https://coapi.cn/v1/mc/gacha.php'''
        self.post_header = {
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "application/json",
        }
        self.gacha_type = {
            1: "UP角色池",
            2: "UP武器池",
            3: "常驻角色池",
            4: "常驻武器池",
            5: "新手池",
            6: "新手自选池",
            7: "感恩自选池",
        }

        self.time_format = r'%Y-%m-%d %H:%M:%S'
        self.time_init_str = '1970-01-01 00:00:00'
        
        self.init_args = {
            "game_path"  : "",
            "data_path"  : os.path.abspath('./'),
            "log_path"   : os.path.abspath('./log'),
            "cache_path" : os.path.abspath('./cache'),
            # "database_lastest_record_time" : '1970-01-01 00:00:00',
            # "analysis_lastest_record_time" : '1970-01-01 00:00:00',
        }
        
        if len(self.args_db) == 0:
            self.args_db.insert(self.init_args)
        self.set_args_from_database()
    
    def is_time_init(self, datetime_value):
        stand_time = datetime.strptime(self.time_init_str, self.time_format)
        if datetime_value == stand_time:
            return True
        elif datetime_value > stand_time:
            return False
        raise ValueError
    
    def set_args_from_database(self):
        args_dict = self.args_db.get(doc_id = len(self.args_db))
        self.set_args(args_dict)

    @property
    def game_log_path(self) -> str:
        return self.game_path + '\Wuthering Waves Game\Client\Saved\Logs\Client.log'
    
    @property
    def cache_size(self):
        if not os.path.exists(self.cache_path):
            return 0
        dir_bytes = get_dir_size(self.cache_path)
        if dir_bytes < 1024:
            return "{} B({} 字节)".format(dir_bytes, dir_bytes)
        elif dir_bytes < pow(1024, 2):
            return "{} KB ({} 字节)".format(dir_bytes // 1024, dir_bytes)
        else:
            return "{} KB ({} 字节)".format(dir_bytes // pow(1024, 2), dir_bytes)
    
    @property
    def settings_complete(self):
        if self.game_path != "":
            return True
        return False
    
    @property
    def gacha_time(self):
        return self.database_time
    
    @property
    def gacha_db(self):
        return TinyDB(os.path.join(self.data_path, 'gacha_database.json'))
        # return TinyDB(os.path.join(self.data_path, 'gacha_database_test.json'))
    
    @property
    def analysis_db(self):
        return TinyDB(os.path.join(self.cache_path, 'analysis_result.json'))
    
    # def is_gacha_time_init(self):
    #     if self.database_time == self.init_args['database_lastest_record_time']:
    #         return True
    #     return False

    # def renew_gacha_time(self):
    #     '''
    #     找到所有表中的最新时间，比较之后输出其中最新的那个
    #     该函数不利于更加细致的控制
    #     '''
    #     db = self.gacha_db
    #     time_list = []
    #     for gacha_name in self.gacha_type.values():
    #         gacha_table = db.table(gacha_name)
    #         table_lastest_time_record = gacha_table.get(doc_id = len(gacha_table))
    #         if table_lastest_time_record:
    #             time_list.append(
    #                 datetime.strptime(
    #                     table_lastest_time_record['time'], 
    #                     self.time_format,
    #                 )
    #             )
    #     # if time_list:
    #     #     # self.database_time = datetime.strftime(max(time_list), self.time_format)
    #     #     self.database_time = max(time_list)
    #     self.database_time = max(time_list) if time_list else datetime.strptime(self.time_init_str, self.time_format)
    
    # def gacha_table_time(self, table_name):
    #     db = self.gacha_db
    #     table = db.table(table_name)
    #     lastest_record = table.get(doc_id = len(table))
    #     if lastest_record:
    #         return datetime.strptime(lastest_record['time'], self.time_format)
    #     return datetime.strptime(self.time_init_str, self.time_format)
    
    def get_table_time(self, db, table_name):
        table = db.table(table_name)
        lastest_record = table.get(doc_id = len(table))
        if lastest_record:
            return datetime.strptime(lastest_record['time'], self.time_format)
        return datetime.strptime(self.time_init_str, self.time_format)

    # def renew_analysis_time(self):
    #     db = self.analysis_db
    #     tables_name = self.gacha_type.values()
    #     time_list = []
    #     for name in tables_name:
    #         table = db.table(name)
    #         table_lastest_time_record = table.get(doc_id = len(table))
    #         if table_lastest_time_record:
    #             time_list.append(
    #                 datetime.strptime(
    #                     table_lastest_time_record['time'],
    #                     self.time_format,
    #                 )
    #             )
    #     # if time_list:
    #     #     # self.analysis_time = datetime.strftime(max(time_list), self.time_format)
    #     #     self.analysis_time = max(time_list)
    #     self.analysis_time = max(time_list) if time_list else datetime.strptime(self.time_init_str, self.time_format)
            
    def set_args(self, args_dict: dict):
        '''
        {
            "game_path": ,
            "data_path": ,
            "log_path" : ,
            "cache_path" : ,
            "database_lastest_record_time" : '',
            "analysis_lastest_record_time" : '',
        }
        '''
        while 1:
            try:
                self.game_path = args_dict['game_path']
                self.data_path = args_dict['data_path']
                self.log_path = args_dict['log_path']
                self.cache_path = args_dict['cache_path']
                # self.database_time = args_dict['database_lastest_record_time']
                # self.analysis_time = args_dict['analysis_lastest_record_time']
                # if not os.path.exists(self.log_path):
                #     os.mkdir(self.log_path)
                # if not os.path.exists(self.cache_path):
                #     os.mkdir(self.cache_path)
                break
            except Exception:
                signal = input("参数损坏或不全，是否重置？[y/n]")
                if signal == 'y' or signal == 'Y':
                    self.init_args()
                    continue
                else:
                    print("无法执行")
                    break

    # 更新设置
    def fresh_args(self, args_dict: dict):
        # args_dict 并不一定有所有的参数
        for args_name, args_value in args_dict.items():
            self.args_db.update(
                {
                    args_name: args_value
                }, 
                doc_ids=[len(self.args_db)], 
            )
        self.set_args_from_database()
    
    def save_args(self):
        args_dict = {
            "game_path": self.game_path,
            "data_path": self.data_path,
            "log_path" : self.log_path,
            "cache_path" : self.cache_path,
            # "database_lastest_record_time" : self.database_time,
            # "analysis_lastest_record_time" : self.analysis_time,
        }
        self.fresh_args(args_dict)
    
    # 重置设置
    def initial_args(self):
        self.args_db.truncate()
        self.args_db.insert(self.init_args)
        self.set_args_from_database()



# 计算文件夹大小
def get_dir_size(path_str):
    total = 0
    with os.scandir(path_str) as dir:
        for dir_content in dir:
            if dir_content.is_file():
                total += dir_content.stat().st_size
            elif dir_content.is_dir():
                total += get_dir_size(dir_content.path)
    return total

# 计算数据库所有表中文档个数
def calculate_db_len(db):
    sum = 0
    for name in db.tables():
        sum += len(db.table(name))
    return sum

# 按照时间来排除哪些文档不该插入
def sorted_insert_or_update_with_time(
        db,
        table_name: str, 
        insert_records: list, 
        lastest_time: datetime = None,
        is_reversed: bool = False,
        check_function = None,
    ) -> int:
    '''
    lastest_time: datetime
    check_function: function
    is_reversed: 本函数需要逆序传入，默认传入的是顺序
        1. 如果传入数据是从大到小，该项置为 True
        2. 如果从小到大，则不必传入
    '''
    
    table = db.table(table_name)
    
    if not is_reversed:
        insert_records = insert_records[::-1]
    
    # 从头到尾时间由大到小，减轻比对数量，并且后续切片时不会多出一条
    if not settings.is_time_init(lastest_time) and insert_records: # insert_record 为空时 i 会不存在
        
        # 比对传入的 gacha_records 的时间
        for i in range(len(insert_records)):
            record = insert_records[i]
            record_time = datetime.strptime(record['time'], settings.time_format)
            
            if record_time > lastest_time:
                continue
            else:
                break
            
        insert_list = insert_records[:i]
    else:
        insert_list = insert_records
    
    # 记录新插入的数据条数
    new_records_num = len(insert_list)
    
    # 额外的检查环节
    if check_function:
        insert_list = list(map(check_function, insert_list))
    
    # 批量插入切片
    table.insert_multiple(insert_list[::-1])
    
    return new_records_num

def data_to_analysis_name_trans(data_table_name: str, level: int):
    return data_table_name + '_lv' + str(level)


settings = WaveToolArgs()
settings.game_path = r"D:\game\鸣潮\Wuthering Waves"
# settings.initial_args()
# print(settings.database_time)
# a.set_args_from_database()