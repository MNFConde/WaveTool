import ctypes
import sys
import chardet
import re
import requests
import json
# import settings
from settings import settings
from datetime import datetime

new_record_standard_time = None

class NetWorkError(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message
    
    def __str__(self):
        return "状态码 {} : {}".format(self.code, self.message)
    
class WaveUrlTimeOut(Exception):
    def __init__(self, message = None):
        self.message = message
        self.text = "获取到的 url 超时，请重新打开游戏内的祈愿记录以获取最新的 url"
        
    def __str__(self):
        if self.message:
            return "\n【错误信息】{}\n【提示】{}".format(self.message, self.text)
        return "{}".format(self.text)

def is_admin():
    '''
    判断管理员权限
    '''
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def get_encoding(file):
    '''
    获取文件编码类型
    '''
    with open(file, 'rb') as f:
        return chardet.detect(f.read())['encoding']


def read_lines(file_path, N):
    '''
    生成器函数，用于每次读取 N 行
    '''
    encode = get_encoding(file_path)
    encode = "utf-8" if not encode else encode
    with open(file_path, 'r', encoding=encode) as f:
        try:
            while True:
                lines = ''.join([next(f) for _ in range(N)])
                if not lines:
                    break
                yield lines
        except StopIteration:
            return 


def search_file_through_lines(file_path: str, line_num: int, target_str: str):
    '''
    在 log 文件中逐行搜索目标 url
    '''
    lastest_url_chunk = None
    for i in read_lines(file_path, line_num):
        if target_str in i:
            lastest_url_chunk = i
    return lastest_url_chunk


def get_post_url(file_path: str):
    '''
    正则过滤出参数
    '''
    searched_str = "aki-gm-resources.aki-game.com"
    file_chunk = search_file_through_lines(file_path, 10, searched_str)
    if not file_chunk:
        raise Exception("目标 url 不存在，请登陆游戏打开祈愿历史记录！")
    return re.findall(r"(?<=https://aki-gm-resources.aki-game.com/aki/gacha/index.html#/record)\?.*(?=\",)", file_chunk)[-1]

def make_post_url(url_api: str, url_para: dict) -> str:
    '''
    从参数构建请求 url
    '''
    url_para_str = '?'
    for i, j in url_para.items():
        url_para_str += i + '=' + j + '&' # 将参数拼接为 url 
    return url_api + url_para_str[:-1]

def get_url_para_from_log() -> dict:
    url_para_str = get_post_url(settings.game_log_path)
    print(url_para_str)
    url_para_dict = {
        'svr_id'       : re.search(r'(?<=svr_id=).*?(?=&)', url_para_str).group(),
        'player_id'    : re.search(r'(?<=player_id=).*?(?=&)', url_para_str).group(),
        'lang'         : re.search(r'(?<=lang=).*?(?=&)', url_para_str).group(),
        'gacha_id'     : re.search(r'(?<=gacha_id=).*?(?=&)', url_para_str).group(),
        'gacha_type'   : re.search(r'(?<=gacha_type=).*?(?=&)', url_para_str).group(),
        'svr_area'     : re.search(r'(?<=svr_area=).*?(?=&)', url_para_str).group(),
        'record_id'    : re.search(r'(?<=record_id=).*?(?=&)', url_para_str).group(),
        'resources_id' : re.search(r'(?<=resources_id=).*', url_para_str).group(),
    }
    
    post_para_dict = {
        "playerId"     : url_para_dict['player_id'],
        "cardPoolId"   : url_para_dict['resources_id'],
        "cardPoolType" : url_para_dict['gacha_type'],
        "languageCode" : url_para_dict['lang'],
        "serverId"     : url_para_dict['svr_id'],
        "recordId"     : url_para_dict['record_id']
    }
    
    return post_para_dict


def get_pointed_type_gacha_records(
        gacha_type: int, 
        post_para_dict: dict,
    ) -> list:
    '''
    请求指定类型的祈愿数据，返回一个列表，其中的元素为字典，类似于：
    {'cardPoolType': '角色精准调谐', 'resourceId': 21030023, 'qualityLevel': 3, 'resourceType': '武器', 'name': '源能佩枪·测叁', 'count': 1, 'time': '2024-08-02 23:46:33'}
    '''
    post_para_dict["cardPoolType"] = str(gacha_type)
    gacha_data = requests.post(
        settings.url_api, 
        json=post_para_dict, 
        headers=settings.post_header
    )
    
    if gacha_data.status_code != 200:
        raise NetWorkError(gacha_data.status_code, "请求出错！")
    
        # 这里打印日志
    
    gacha_dict = json.loads(gacha_data.text)
    if gacha_dict['code'] == -1:
        raise WaveUrlTimeOut(gacha_dict['message'])
    
    return gacha_dict['data']

def insert_or_update(gacha_id: int, gacha_records: list) -> int:
    gacha_table = settings.gacha_db.table(settings.gacha_type[gacha_id])
    # 从数据库中读取最后一条消息的时间
    
    
    # 从头到尾时间由大到小，减轻比对数量，并且后续切片时不会多出一条
    if settings.is_gacha_time_init() and gacha_records: # gacha_record 为空时 i 会不存在
        
        # 比对传入的 gacha_records 的时间
        for i in range(len(gacha_records)):
            record = gacha_records[i]
            record_time = datetime.strptime(record['time'], settings.time_format)
            
            if record_time > settings.gacha_time:
                continue
            else:
                break
            
        insert_list = gacha_records[:i]
    else:
        insert_list = gacha_records
    
    # 记录新插入的数据条数
    new_records_num = len(insert_list)
    
    # 批量插入切片
    gacha_table.insert_multiple(insert_list[::-1])
    
    return new_records_num



def get_save_all_type_gacha_records(post_para_dict: dict) -> dict:
    '''
    -> dict[str: int]
    '''
    all_get_records_num = 0
    all_update_records_num = 0
    
    for gacha_id, gacha_name in settings.gacha_type.items():
        # post_para_dict['']
        # 一次请求以及三次重试
        print("正在读取{}卡池".format(gacha_name))
        for _ in range(4):
            gacha_records: list = []
            try:
                gacha_records = get_pointed_type_gacha_records(gacha_id, post_para_dict)
                get_records_num = len(gacha_records)
                break
            except WaveUrlTimeOut as w: # 把异常抛给更上层
                raise WaveUrlTimeOut(w.message + str({
                    "get_records_num"    : all_get_records_num + get_records_num,
                    "update_records_num" : all_update_records_num,
                }))
            except Exception as e:
                if _ == '0':
                    print("请求卡池类型【{}】失败，错误信息：{}，开始重试".format(gacha_name, str(e)))
                    continue
                print("重试第 {} 次失败！".format(_))
                
        if gacha_records == [] and _ != 0: # 有可能本来某个卡池就没有记录
            # 重试仍然失败，则跳过该类型卡池
            print("重试失败，跳过该类卡池！")
        
        # 顺序导入，减轻后续遍历时的条数
        update_records_num = insert_or_update(gacha_id, gacha_records)
        print("读取{}条".format(get_records_num))
        print("更新{}条".format(update_records_num))
        all_update_records_num += update_records_num
    
    # 该值只在获取记录后更新
    settings.renew_gacha_time()
    
    return {
        "get_records_num"    : all_get_records_num,
        "update_records_num" : all_update_records_num,
    }

def get_save_gacha_main():
    if settings.settings_complete:
        para = get_url_para_from_log()
        try:
            return get_save_all_type_gacha_records(para)
        except WaveUrlTimeOut as e:
            return e.message
        except Exception as e:
            print(str(e))
    else:
        print("请先进行设置！")

if __name__ == "__main__":
    # if not is_admin():
    #     ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    #     print("使用管理员权限")
    
    # a = get_pointed_type_gacha_records(1, get_url_para_from_log())
    # print(type(a))
    # print(type(a[0]))
    # print(a[0])
    print(get_save_gacha_main())

