import json
import re
import os
import jieba
import spacy
nlp = spacy.load("zh_core_web_trf")
stopwords = [line.strip() for line in open("stopwords/hit_stopwords.txt", encoding="utf-8").readlines()]  # 加载停用词
def remove_stopwords(sentence):
    #删除句子中的停用词，并返回句子。
    words = jieba.lcut(sentence)
    return ''.join([word for word in words if word not in stopwords])
def word_frequency_statistics(sentence):
    sentence = remove_stopwords(sentence)#去除停用词
    words = jieba.lcut(sentence)#分词
    #print(words)
    word_count = {}
    for word in words:
        if word in word_count:
            word_count[word] += 1
        else:
            word_count[word] = 1
    return word_count
def word_frequency_statistics_judge(sentence):
    word_count = word_frequency_statistics(sentence)
    #遍历该字典，找到词频大于等于3的词，如果有，则该句冗长。
    for value in word_count.values():
        if value>=10:
            try:
                if word_count['信息']>=10:
                    continue
            except:
                return True
    return False
def subsection(text):
    #使用正则表达式匹配文本中的分段符号
    pattern = r'[一二三四五六七八九十]+、|附录'
    segments = re.split(pattern,text)[1:]
    # 将分段符号添加到每个段落的开头
    segments = [re.findall(pattern, text)[i] + segment for i, segment in enumerate(segments)]
    #segments = [segment.replace(" ","") for segment in segments]
    return segments
def subsection_number(text):
    pattern = r'[1234567890]+、'
    segments = re.split(pattern, text)[1:]
    # 将分段符号添加到每个段落的开头
    segments = [re.findall(pattern, text)[i] + segment for i, segment in enumerate(segments)]
    # segments = [segment.replace(" ","") for segment in segments]
    return segments
def subsection_2(text):
    #使用正则表达式匹配文本中的分段符号
    pattern = r'（[一二三四五六七八九十]+）'
    segments = re.split(pattern,text)[1:]
    # 将分段符号添加到每个段落的开头
    segments = [re.findall(pattern, text)[i] + segment for i, segment in enumerate(segments)]
    #segments = [segment.replace(" ","") for segment in segments]
    return segments
def run_subsection(text):
    seg_1 = subsection(text)
    if not seg_1:
        seg_1 = [text]
    segments = []
    for i in seg_1:
        temp1 = subsection_2(i)
        temp2 = subsection_number(i)
        if temp1:
            segments.extend(temp1)
        if temp2:
            segments.extend(temp2)
        if not temp1 and not temp2:
            segments.append(i)
    return segments
def read_txt(filename):
    with open(filename,'r',encoding="utf-8")as f:
        text = f.read()
    f.close()
    return text
def keyword_law8(segment):
    # law8: 未向用户提供撤回同意收集个人信息的途径、方式
    pattern = r'(?=.*撤回)(?=.*授权).*'
    #撤回您授权，撤回授权
    match = re.search(pattern,segment)
    if match:
        return segment
    pattern = r'(?=.*取消)(?=.*授权).*'
    match = re.search(pattern,segment)
    if match:
        return segment
    return False
def keyword_law10(segment):
    # law10: 未提供有效的更正、删除个人信息及注销用户账号功能
    pattern = r'更正|删除|注销'
    match = re.search(pattern,segment)
    if match:
        return segment
    return False
def keyword_law13(segment):
    # law13: 未建立并公布个人信息安全投诉、举报渠道
    pattern = r'投诉|举报'
    match = re.search(pattern,segment)
    if match:
        return segment
    return False
def sentence_segments(segments):
    '''
    :param segments: 输入分段的隐私政策列表
    :return: 返回句子级别隐私政策列表
    '''
    sentence_list = []
    return sentence_list
def test(ori_dir):
    #"../ALiYun_Chinese_0305.txt"。
    f = open(ori_dir,encoding="utf-8")
    text = f.read()
    f.close()
    result_list = re.split(r'[。?？\n]',text)
    s_list = [x.replace('\n','') for x in result_list]
    s_list1 = [i for i in s_list if i !='']
    s_list1 = [segment.replace(" ", "") for segment in s_list1]
    s_list2 = [x+'。' for x in s_list1]#为每句话添加.
    print("Success!")
    return s_list2
def long_sentence_judge(sentence_list):
    result = []
    for s in sentence_list:
        if len(s)>=100 and len(s)<=300:
            result.append(s)
    return result
def long_sentence_judge300(sentence_list):
    result = []
    for s in sentence_list:
        if len(s)>300:
            result.append(s)
    return result
def spilt_str(result):
    result = re.sub(r'\d+','',result)
    if result:
        r = re.split(r'[，（）。：;；!,.()、/》《]', result)
        return r
    else:
        return []
def son_sentence_long_judge(sentence):
    #按照标点符号分句。查看子句是否有大于50的，如果大于则返回True
    son_list = spilt_str(sentence)
    for son in son_list:
        if len(son)>=50:
            return True
    return False
    pattern = r"\（.*?\）"
    while re.search(pattern,sentence):
        sentence = re.sub(pattern,"",sentence)
def check_numbers(sentence):
    pattern = r"\d+"
    matches = re.findall(pattern, sentence)
    return len(matches) > 3
def spacy_node_count(sentence):
    if check_numbers(sentence):
        return False
    pattern = r"\（.*?\）"
    while re.search(pattern,sentence):
        sentence = re.sub(pattern,"",sentence)
    doc = nlp(sentence)
    num_nodes = len(doc)
    #删除为并列关系的节点数
    conj_count = 0
    for token in doc:
        if token.dep_ == "conj":
            conj_count+=1
    if num_nodes-conj_count>100:
        return True
    return False
def long_sentence_judge_more(sentence_13):
    result = []
    for sentence in sentence_13:
        if word_frequency_statistics_judge(sentence):  # 词频统计分析：
            result.append(sentence)
        if son_sentence_long_judge(sentence):#子句长度分析，子句超过50个字就算冗长。
            result.append(sentence)
        if spacy_node_count(sentence):
            result.append(sentence)
    return list(set(result))#去重
def run_long_sentence_judge(sentence_list):
    result3 = long_sentence_judge300(sentence_list)#句子长度超过300
    result13 = long_sentence_judge(sentence_list)#句子长度在100-300之间
    result = long_sentence_judge_more(result13)#筛选出100-300句子之间冗长的。
    result_dict = {
        'long-sentence-count':len(result)+len(result3),'long-sentence':result3+result
    }
    return result_dict
    #所以最后报告的结果应该是：300，100-300冗长，两个结果
def subsection_match(segments):
    '''
    :param segments: 分段的隐私政策文本
    :return: 返回匹配到以下法规关键词的分段文本
    '''
    result = {"data-recall":False,"account-delete":False,"complaint-channel":False,"撤回授权":[],"更正删除注销":[],"投诉举报":[]}
    result = {"data-recall": False, "account-delete": False, "complaint-channel": False}
    for segment in segments:
        temp8 = keyword_law8(segment)
        temp10 = keyword_law10(segment)
        temp13 = keyword_law13(segment)
        if temp8:
            #result["撤回授权"].append(temp8)
            result["data-recall"] = True
        if temp10:
            #result["更正删除注销"].append(temp10)
            result["account-delete"] = True
        if temp13:
            #result["投诉举报"].append(temp13)
            result["complaint-channel"] = True
    return result
def run_compliance_3(txt_path):
    filename_list = os.listdir(txt_path)
    t8_count,t10_count,t13_count = 0,0,0
    compliance3_result = []
    if filename_list:
        for i in filename_list:
            if i.endswith(".txt"):
                text = read_txt(txt_path+"/"+i)
                segments = run_subsection(text)
                result_dict = subsection_match(segments)
                if result_dict["data-recall"] == False:
                    t8_count +=1
                if result_dict["account-delete"] == False:
                    t10_count +=1
                if result_dict["complaint-channel"] == False:
                    t13_count +=1
                #with open("result/"+i[:-4]+".json",'w',encoding='utf-8')as f:
                 #   json.dump(result_dict,f,ensure_ascii=False, indent=2)
                #f.close()
                compliance3_result.append({i:result_dict})
    else:
        print("ERROR! 无隐私政策进行合规分析。")
    return compliance3_result
def run_compliance_4(txt_path,only_analysis_pkgName_url = 'n'):
    filename_list = os.listdir(txt_path)
    apps = set(filename_list)
    if only_analysis_pkgName_url == 'y':
        try:
            with open('pkgName_url.json', 'r', encoding='utf8') as f:
                json_file = json.load(f)
                apps = set(json_file.keys())
        except FileNotFoundError:
            # 找不到pkgName_url.json的话，就按原本的方法进行。。
            print('no pkgName_url.json, fail to analysis...')

    if filename_list:
        for i in filename_list:
            if i.endswith(".txt") and (i[:-4] in apps or i in apps):
                text = read_txt(txt_path+"/"+i)
                segments = run_subsection(text)
                result_dict = subsection_match(segments)
                #长句分析
                sentence_list = test(txt_path+"/"+i)
                sentence_result_dict = run_long_sentence_judge(sentence_list)
                result_dict['long-sentence-judge'] = sentence_result_dict
                with open("PrivacyPolicySaveDir/"+i[:-4]+".json",'r',encoding='utf-8')as f:
                    data = json.load(f)
                f.close()
                data.append({'compliance-analysis':result_dict})
                with open("PrivacyPolicySaveDir/"+i[:-4]+".json",'w',encoding='utf-8')as f:
                    json.dump(data,f,ensure_ascii=False, indent=2)
                f.close()
        return result_dict
    else:
        print("ERROR! 无隐私政策进行合规分析。")



def write_compliance_in_json(compliance3_list,longsentence_result,danger_permission_lost_result):
    return False
def run_compliance_analysis(only_analysis_pkgName_url = 'n'):
    #撤回授权、更正删除注销、投诉举报，分析对象隐私政策
    if only_analysis_pkgName_url == 'n':
        compliance4_list = run_compliance_4('Privacypolicy_txt')
    else:
        compliance4_list = run_compliance_4('Privacypolicy_txt','y')
    #{'data-recall': True, 'account-delete': True, 'complaint-channel': True}
    #长句检测，分析对象隐私政策
    #longsentence_result = run_long_sentence_judge('Privacypolicy_txt')
    #这里的长句分析并不完整。。。还有另一部分，我不知道放哪里了，绝了。tmd
    #write_compliance_in_json(compliance3_list,longsentence_result)
if __name__ == '__main__':
    run_compliance_analysis()
    #run_long_sentence_judge("Privacypolicy_txt")