from tinydb import TinyDB, Query
from datetime import datetime

gacha_db = TinyDB('./gacha_database.json')
gacha_records = Query()

file_path = r"D:\game\鸣潮\Wuthering Waves\Wuthering Waves Game\Client\Saved\Logs\Client.log"
url_api = '''https://gmserver-api.aki-game2.com/gacha/record/query'''
url_api_2 = '''https://coapi.cn/v1/mc/gacha.php'''
# save_path = r"D:\software\启动器\log_save.json"

post_header = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/json",
}

gacha_type = {
    1: "UP角色池",
    2: "UP武器池",
    3: "常驻角色池",
    4: "常驻武器池",
    5: "新手池",
    6: "新手自选池",
    7: "感恩自选池",
}

time_format = r'%Y-%m-%d %H:%M:%S'


def get_lastest_time():
    '''
    找到所有表中的最新时间，比较之后输出其中最新的那个
    '''
    time_tuple = []
    for gacha_name in gacha_type.values():
        gacha_table = gacha_db.table(gacha_name)
        table_lastest_time_record = gacha_table.get(doc_id = len(gacha_table))
        if table_lastest_time_record:
            time_tuple.append(
                datetime.strptime(
                    table_lastest_time_record['time'], 
                    time_format,
                )
            )
    
    if time_tuple:
        return max(time_tuple)
    return None

