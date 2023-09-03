import re
import jieba
import json
data_handle_list = [line.strip() for line in open("Dict/隐私数据项_3_30.txt", encoding="utf-8").readlines()]
stopwords = [line.strip() for line in open("stopwords/hit_stopwords.txt", encoding="utf-8").readlines()]  # 加载停用词
purpose_doamin_stopwords = [line.strip() for line in open("stopwords/purpose_domain_stopwords.txt", encoding="utf-8").readlines()]
with open("Dict/0504-data-permission-map.json", 'r', encoding='utf-8')as f:
    permission_data_map = json.load(f)
f.close()
def purpose_cut(result,j):
    a = 0
    for i in result:
        result[a] = i[j:-1]
        a = a+1
    return result
def purpose_base_approach_ch(str_):
    result_list = []
    result = re.findall(r'以便.*?[,|，|。|.|;|；|:|：]',str_)
    if result:
        result_list.append(result[0][:-1])
    result = re.findall(r'以核验.*?[,|，|。|.|;|；|:|：]',str_)
    if result:
        result_list.append(result[0][1:-1])
    result = re.findall(r'判断您.*?[,|，|。|.|;|；|:|：]', str_)
    if result:
        result_list.append(result[0][:-1])
        #return [result_sentence[0][2:-1]]
    result = re.findall(r'完成.*?[,|，|。|.|;|；|:|：]',str_)
    if result:
        result_list.append(result[0][2:-1])
        #return [result_sentence[0][2:-1]]
    result = re.findall(r'作为.*?[,|，|。|.|;|；|:|：]',str_)
    if result:
        result_list.append(result[0][:-1])
    result = re.findall(r'向您推荐.*?[,|，|。|.|;|；|:|：]', str_)
    if result:
        result_list.append(result[0][2:-1])
        #return [result_sentence[0][2:-1]]
    result = re.findall(r'当您.*?[时|,|，|。|.|;|；|:|：]', str_)
    if result:
        result_list.append(result[0][1:-1])
    result = re.findall(r'用于.*?[,|，|。|.|;|；|:|：]',str_)
    if result:
        result_list.append(result[0][2:-1])
    result = re.findall(r'选于.*?[,|，|。|.|;|；|:|：]', str_)
    if result:
        result_list.append(result[0][2:-1])
        #return [result_sentence[0][2:-1]]
    result = re.findall(r'目的是.*?[,|，|。|.|;|；|:|：]',str_)
    if result:
        result_list.append(result[0][3:-1])
        #return [result_sentence[0][3:-1]]
    result = re.findall(r'目的是为了.*?[,|，|。|.|;|；|:|：]',str_)
    if result:
        result_list.append(result[0][3:-1])
        #return [result_sentence[0][5:-1]]
    result = re.findall(r'以此.*?[,|，|。|.|;|；|:|：]',str_)
    if result:
        result_list.append(result[0][:-1])
        #return [result_sentence[0][2:-1]]
    result = re.findall(r'以获取.*?[,|，|。|.|;|；|:|：]',str_)
    if result:
        result_list.append(result[0][1:-1])
    result = re.findall(r'以优化.*?[,|，|。|.|;|；|:|：]', str_)
    if result:
        result_list.append(result[0][1:-1])
        #return [result_sentence[0][3:-1]]
    result = re.findall(r'以证实.*?[,|，|。|.|;|；|:|：]', str_)
    if result:
        result_list.append(result[0][1:-1])
    result = re.findall(r'以创建.*?[,|，|。|.|;|；|:|：]', str_)
    if result:
        result_list.append(result[0][1:-1])
    result = re.findall(r'目的是为.*?[,|，|。|.|;|；|:|：]',str_)
    if result:
        result_list.append(result[0][4:-1])
        #return [result_sentence[0][4:-1]]
    result = re.findall(r'为了.*?[,|，|。|.|;|；|:|：|您]',str_)
    if result:
        result_list.append(result[0][2:-1])
        #return [result_sentence[0][2:-1]]
    result = re.findall(r'是为了.*?[,|，|。|.|;|；|:|：]',str_)
    if result:
        result_list.append(result[0][3:-1])
    result = re.findall(r'为便于.*?[,|，|。|.|;|；|:|：]', str_)
    if result:
        result_list.append(result[0][3:-1])
    result = re.findall(r'为保障.*?[,|，|。|.|;|；|:|：]', str_)
    if result:
        result_list.append(result[0][1:-1])
    result = re.findall(r'为注册.*?[,|，|。|.|;|；|:|：]', str_)
    if result:
        result_list.append(result[0][1:-1])
    result = re.findall(r'帮助您.*?[,|，|。|.|;|；|:|：]', str_)
    if result:
        result_list.append(result[0][3:-1])
    result = re.findall(r'为您提供.*?[,|，|。|.|;|；|:|：]',str_)
    if result:
        result_list.append(result[0][2:-1])
    result = re.findall(r'以向您提供.*?[,|，|。|.|;|；|:|：]',str_)
    if result:
        result_list.append(result[0][2:-1])
    result = re.findall(r'不断改进.*?[,|，|。|.|;|；|:|：]',str_)
    if result:
        result_list.append(result[0][2:-1])
    result = re.findall(r'实现.*?[,|，|。|.|;|；|:|：]',str_)
    if result:
        result_list.append(result[0][:-1])
    result = re.findall(r'身份认证', str_)
    if result:
        result_list.append(result[0][:])
    result = re.findall(r'为完成.*?[,|，|。|.|;|；|:|：]',str_)
    if result:
        result_list.append(result[0][1:-1])
    result = re.findall(r'为履行.*?[,|，|。|.|;|；|:|：]', str_)
    if result:
        result_list.append(result[0][1:-1])
    result = re.findall(r'防范.*?[,|，|。|.|;|；|:|：]', str_)
    if result:
        result_list.append(result[0][:-1])
    result = re.findall(r'为确保.*?[,|，|。|.|;|；|:|：|、]', str_)
    if result:
        result_list.append(result[0][1:-1])
    result = re.findall(r'您使用.*?[时|,|，|。|.|;|；|:|：|、]',str_)
    if result:
        result_list.append(result[0][:-1])
    result = re.findall(r'您参加.*?[时]',str_)
    if result:
        result_list.append(result[0][:-1])
    result = re.findall(r'您注册.*?[时]',str_)
    if result:
        result_list.append(result[0][:-1])
    result = re.findall(r'申请.*?[时]',str_)
    if result:
        result_list.append(result[0][:-1])
    result = re.findall(r'使用.*?功能', str_)
    if result:
        if '信息' not in result[0] and '地址' not in result[0] and "您" not in result[0]:
            result_list.append(result[0][:])
    result = re.findall(r'参加.*?活动', str_)
    if result:
        result_list.append(result[0][2:])
    result = re.findall(r'发出.*?提醒', str_)
    if result:
        if '信息' not in result[0]:
            result_list.append(result[0][2:])
    result = re.findall(r'使用.*?服务', str_)
    if result:
        if '信息' not in result[0] or "您" not in result[0]:
            result_list.append(result[0][:])
    result = re.findall(r'确定.*?身份', str_)
    if result:
        result_list.append(result[0][:])
    result = re.findall(r'使用.*?模式', str_)
    if result:
        if '信息' not in result[0] and "您" not in result[0]:
            result_list.append(result[0][:])
    result = re.findall(r'推送.*?[,|，|。|.|;|；|:|：]', str_)
    if result:
        result_list.append(result[0][:-1])
    result = re.findall(r'与我们.*?[,|，|。|.|;|；|:|：]', str_)
    if result:
        result_list.append(result[0][:-1])
    result = re.findall(r'需确认.*?[,|，|。|.|;|；|:|：]', str_)
    if result:
            result_list.append(result[0][1:-1])
    result = re.findall(r'为提高.*?[,|，|。|.|;|；|:|：]', str_)
    if result:
            result_list.append(result[0][1:-1])
    result = re.findall(r'以符合.*?[,|，|。|.|;|；|:|：]', str_)
    if result:
            result_list.append(result[0][3:-1])
    result = re.findall(r'在.*?过程中',str_)
    if result:
        result_list.append(result[0][:-1])
    result = re.findall(r'为识别.*?[,|，|。|.|;|；|:|：]',str_)
    if result:
        result_list.append(result[0][:-1])
    result = re.findall(r'匹配您.*?[,|，|。|.|;|；|:|：]',str_)
    if result:
        result_list.append(result[0][3:-1])
    result = re.findall(r'在您.*?后', str_)
    if result:
        result_list.append(result[0][:-1])
    result = re.findall(r'若您需要.*?[,|，|。|.|;|；|:|：]',str_)
    if result:
        result_list.append(result[0][:-1])
    result = re.findall(r'进行.*?[，|)|。|,|:|;|；|：]',str_)
    if result:
        if "信息" not in result[0] and "地址" not in result[0]:
            result_list.append(result[0][:-1])
    result = re.findall(r'向您提供.*?[,|，|。|.|;|；|:|：]',str_)
    if result:
        result_list.append(result[0][:-1])
    result = re.findall(r'做出.*?[,|，|。|.|;|；|:|：]',str_)
    if result:
        result_list.append(result[0][2:-1])
    result = re.findall(r'校验.*?[,|，|。|.|;|；|:|：]', str_)
    if result:
        result_list.append(result[0][:-1])
    result = re.findall(r'共享', str_)
    if result:
        result_list.append(result[0])
    return result_list
def data_item_contain(str_):
    result_list = []
    pattern = r"您选择提供([\w、]+)，"
    match = re.search(pattern, str_)
    if match:
        data = match.group(1).split("、")
        return data
    result = re.findall(r'信息：包括.*[|。|.|;|；]',str_)
    if result:
        result_list.append(result[0][5:-1])
    result = re.findall(r'访问.*[。|.|;|；|:|：|，|,]', str_)
    if result:
        result_list.append(result[0][5:-1])
    result = re.findall(r'选择.*[。|.|;|；|:|：|，|,]', str_)
    if result:
        result_list.append(result[0][2:-1])
    result = re.findall(r'信息，包括.*[|。|.|;|；]',str_)
    if result:
        result_list.append(result[0][5:-1])
    result = re.findall(r'信息包括.*[|。|.|;|；]',str_)
    if result:
        result_list.append(result[0][4:-1])
    result = re.findall(r'信息（包括.*[。|.|;|；]',str_)
    if result:
        result_list.append(result[0][5:-1])
    result = re.findall(r'信息\(包括.*[。|.|;|；]',str_)
    if result:
        result_list.append(result[0][5:-1])
    result = re.findall(r'存储为.*?[。|.|;|；|:|：]',str_)
    if result:
        result_list.append(result[0][4:-1])
    result = re.findall(r'包括您的.*?[。|.|;|；|:|：]',str_)
    if result:
        result_list.append(result[0][4:-1])
    result = re.findall(r'记录，包括.*[。|.|;|；]', str_)
    if result:
        result_list.append(result[0][5:-1])
    result = re.findall(r'记录您.*?[,|，|。|.|;|；]', str_)
    if result:
        result_list.append(result[0][3:-1])
    result = re.findall(r'提供您.*?[,|，|。|.|;|；|:|：]',str_)
    if result:
        result_list.append(result[0][3:-1])
    result = re.findall(r'接收.*?[,|，|。|.|;|；|:|：]', str_)
    if result:
        result1 = re.findall(r'接收方.*?[,|，|。|.|;|；|:|：]',result[0])
        if not result1:
            result_list.append(result[0][1:-1])
    result = re.findall(r'(收集.*[,|，|。|.|;|；|:|：])', str_)
    if result:
        return [result[0][2:-1]]
    result = re.findall(r'收集、使用您的.*?[,|，|。|.|;|；|:|：]',str_)
    if result:
        result_list.append(result[0][7:-1])
    result = re.findall(r'共享您.*?[,|，|。|.|;|；|:|：]',str_)
    if result:
        result_list.append(result[0][3:-1])
    result = re.findall(r'将您的.*?[,|，|。|.|;|；|:|：]',str_)
    if result:
        result_list.append(result[0][3:-2])
    result = re.findall(r'将获取.*?[。|.|;|；|:|：|，|,]', str_)
    if result:
        result_list.append(result[0][3:-2])
    result = re.findall(r'向我们提供.*?[,|，|。|.|;|；|:|：]',str_)
    if result:
        result_list.append(result[0][5:-1])
    result = re.findall(r'提交.*?[,|，|。|.|;|；|:|：|或]',str_)
    if result:
        result_list.append(result[0][2:-1])
    result = re.findall(r'收集的.*?[,|，|。|.|;|；|:|：]',str_)
    if result:
        result_list.append(result[0][3:-1])
    result = re.findall(r'收集您.*?[,|，|。|.|;|；|:|：]',str_)
    if result:
        result_list.append(result[0][3:-1])
    result = re.findall(r'收集.*信息]', str_)
    if result:
        result_list.append(result[0][2:])
    pattern = r"我们会收集.*?您的(.*)"
    match = re.search(pattern, str_)
    if match:
        collected_info = match.group(1)
        result_list.append(collected_info)
    result = re.findall(r'整合您.*?[,|，|。|.|;|；|:|：]',str_)
    if result:
        result_list.append(result[0][3:-1])
    result = re.findall(r'选择提供.*?[,|，|。|.|;|；|:|：]',str_)
    if result:
        result_list.append(result[0][4:-1])
    result = re.findall(r'使用您.*?[,|，|。|.|;|；|:|：]',str_)
    if result:
        result_list.append(result[0][3:-1])
    result = re.findall(r'使用的您.*?[,|，|。|.|;|；|:|：]',str_)
    if result:
        result_list.append(result[0][4:-1])
    result = re.findall(r'提供您的.*?[,|，|。|.|;|；|:|：]',str_)
    if result:
        result_list.append(result[0][4:-1])
    result = re.findall(r'根据您.*?[,|，|。|.|;|；|:|：]', str_)
    if result:
        result_list.append(result[0][3:-1])
    result = re.findall(r'保存您.*?[,|，|。|.|;|；|:|：]', str_)
    if result:
        result_list.append(result[0][3:-1])
    result = re.findall(r'需要提供.*?[,|，|。|.|;|；|:|：]',str_)
    if result:
        result_list.append(result[0][4:-1])
    result = re.findall(r'要求提供.*?[,|，|。|.|;|；|:|：]', str_)
    if result:
        result_list.append(result[0][4:-1])
    result = re.findall(r'基于您.*?[,|，|。|.|;|；|:|：]',str_)
    if result:
        result_list.append(result[0][3:-1])
    result = re.findall(r'获取您.*?[,|，|。|.|;|；|:|：]',str_)
    if result:
        result_list.append(result[0][3:-1])
    result = re.findall(r'内容（包括.*?[,|，|。|.|;|；|:|：]', str_)
    if result:
        result_list.append(result[0][5:-1])
    result = re.findall(r'需要您提供.*?[,|，|。|.|;|；|:|：]',str_)
    if result:
        result_list.append(result[0][5:-1])
    result = re.findall(r'您提供.*?[,|，|。|.|;|；|:|：]', str_)
    if result:
        result_list.append(result[0][3:-1])
    result = re.findall(r'提供.*?[,|，|。|.|;|；|:|：]', str_)
    if result:
        result_list.append(result[0][2:-1])
    result = re.findall(r'我们会收集.*?[,|，|。|.|;|；|:|：]',str_)
    if result:
        result_list.append(result[0][5:-1])
    result = re.findall(r'提取您.*?[。|.|;|；|:|：|,|，]',str_)
    if result:
        result_list.append(result[0][3:-1])
    result = re.findall(r'您留下.*?[。|.|;|；|:|：|,|，]', str_)
    if result:
        result_list.append(result[0][1:-1])
    result = re.findall(r'包括.*信息',str_)#包括：设备信息、服务日志信息
    if result:
        result_list.append(result[0][2:])
    result = re.findall(r'读取.*?[。|.|;|；|:|：|,|，]', str_)
    if result:
        result_list.append(result[0][2:-1])
    result = re.findall(r'您的.*将被收集',str_)
    if result:
        result_list.append(result[0][2:-4])
    result = re.findall(r'向我们发送.*?[。|.|;|；|:|：|,|，]',str_)
    if result:
        result_list.append(result[0][2:-4])
    return result_list
def remove_stopwords(sentence):
    #删除句子中的停用词，并返回句子。
    sentence = sentence.upper()
    words = jieba.lcut(sentence)
    return ''.join([word for word in words if word not in stopwords])
def data_handle(data):
    data = remove_stopwords(data)
    result = []
    for dh in data_handle_list:
        if dh in data:
            result.append(dh)
    return list(set(result))
def third_item(str_):
    match = []
    result = re.findall(r'与.*?共享',str_)
    if result:
        match.append("3st")
    pattern = r"第三方"
    matches = re.findall(pattern, str_)
    if matches:
        match.append("3st")
    pattern = r"我们"
    matches = re.findall(pattern, str_)
    if matches:
        match.append("1st")
    pattern = r"合作方"
    matches = re.findall(pattern, str_)
    if matches:
        match.append("3st")
    return list(set(match))
def data_item_single_simple(data):
    result = []
    if len(data)>10:
        for dh in data_handle_list:
            if dh in data:
                result.append(dh)
        if result:
            return result
        else:
            return []
    if len(data)<2:
        return [""]
    else:
        return [data]
def delete_purpose(purpose_list):
    #尝试将提取出的重复目的子句从目标句子中删除
    purpose_list = list(set(purpose_list))
    result = purpose_list[:]
    for i in range(len(purpose_list)):
        for j in range(0, len(purpose_list)):
            if purpose_list[j] in purpose_list[i]:
                if purpose_list[j] != purpose_list[i]:
                    if purpose_list[j] in result:
                        result.remove(purpose_list[j])
    return result
def run_str(str_):
    d_list = []
    ds = []
    p = purpose_base_approach_ch(str_)
    p1 =[]
    if p :
        p = delete_purpose(p)
        for pi in p:
            if pi:
                str_ = str_.replace(pi,"")
                p1.append(pi)
    th = third_item(str_)
    if th:
        th = list(set(th))
    d = data_item_contain(str_)
    if d:
        d = spilt_list(d)
        for di in d:
            di = remove_stopwords(di) #去除data里面的停用词
            if di:
                ds.append(di)
        ds = list(set(ds))#去重
        for data in ds:
            data_result_list = data_item_single_simple(data)
            if data_result_list:
                for d_data in data_result_list:
                    d_to_p = []
                    d_to_p.append(d_data)
                    d_to_p.append(th)
                    d_to_p.append(p1)
                    d_list.append(d_to_p)
    return d_list,ds
def spilt_list(result):
    r = []
    if result:
        for a in result:
            if a:
                for b in spilt_str(a):
                    r.append(b)
        return r
def spilt_str(result):
    if result:
        r = re.split(r'[、，/（）。：;；!和及或等并与1234567890]', result)
        return r
