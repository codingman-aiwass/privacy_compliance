import json

with open("chatgpt_all_cn2en.json",'r',encoding='utf-8')as f:
    chatgpt = json.load(f)
f.close()
'''
#将字符串中的_-替换为空格

result = []
for d in chatgpt:
    data = {"data-cn":d["data-cn"]}
    tem = []
    for t in d["data-en"]:
        t = t.replace("_", " ").replace("-", " ")
        tem.append(t)
    data["data-en"] = tem[:]
    result.append(data)
with open("0531chatgpt.json",'w',encoding='utf-8')as f:
    json.dump(result ,f, ensure_ascii=False, indent=2)
f.close()'''
def is_not_contain_chinese(str):
    #返回true，则不包含中文
    for ch in str:
        if '\u4e00' <= ch <= '\u9fff':
            return False
    return True

with open("隐私数据项_3_30.json",'r',encoding='utf-8')as f:
    data = json.load(f)
data_ch = []
for d in data:
    data_ch.append(d["data-cn"])
chatgpt_ch = []
for d in chatgpt:
    chatgpt_ch.append(d["data-cn"])
#找到漏掉的
result = [x for x in data_ch if x not in chatgpt_ch]
print(result)
print(len(result))
res = result[:]
for r in result:
    if is_not_contain_chinese(r):
        res.remove(r)
print(len(res))
with open("0531_data_miss_chatgpt.json",'w',encoding="utf-8")as f:
    json.dump(res, f, ensure_ascii=False, indent=2)
f.close()