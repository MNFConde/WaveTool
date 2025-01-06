from tinydb import TinyDB, Query
q = Query()

# db = TinyDB('db.json')
# q = Query()
# # db.insert({'type': 'apple', 'count': 7})
# # db.insert({'type': 'peach', 'count': 3})
# # db.insert({'type': 'peach', 'count': 3})
# # db.insert_multiple([
# #     {'type': 'apple', 'count': 1},
# #     {'type': 'apple', 'count': 2},
# #     {'type': 'apple', 'count': 3},
# #     {'type': 'apple', 'count': 4},
# #     {'type': 'apple', 'count': 5},
# # ]) # 按顺序批量插入
# print(len(db))
# print(db.get(doc_id = len(db))) # 获取id最大的记录（最后一条）
# print(db.get(doc_id = len(db)+1)) # 获取id最大的记录（最后一条）的部分值，找不到就返回 None


gacha_type = {
    1: "UP角色池",
    2: "UP武器池",
    3: "常驻角色池",
    4: "常驻武器池",
    5: "新手池",
    6: "新手自选池",
    7: "感恩自选池",
}



# t1 = db.table(gacha_type[1]) # 不用显式创建，没有会自己创建的
# t1.insert_multiple([
#     {'type': 'apple', 'count': 1},
#     {'type': 'apple', 'count': 2},
#     {'type': 'apple', 'count': 3},
#     {'type': 'apple', 'count': 4},
#     {'type': 'apple', 'count': 5},
# ]) # 按顺序批量插入

db = TinyDB('gacha_database.json')
# print(sum([len(db.table(i)) for i in db.tables()]))
for i in db.tables():
    print(i)
    print(*db.table(i).all()[-18:], sep='\n')
