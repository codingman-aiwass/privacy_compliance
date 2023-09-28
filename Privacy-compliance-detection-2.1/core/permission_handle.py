import json
import re
import jieba
import spacy
from url_analysis import html_response_soup
from url_analysis import redirection_judge
from url_analysis import read_txt_file
permission_doamin_stopwords = [line.strip() for line in open("stopwords/permission_domain_stopwords.txt", encoding="utf-8").readlines()]
stopwords = [line.strip() for line in open("stopwords/hit_stopwords.txt", encoding="utf-8").readlines()]  # 加载停用词
#permission_doamin_stopwords = [line.strip() for line in open("stopwords/permission_domain_stopwords.txt", encoding="utf-8").readlines()]
#stopwords = [line.strip() for line in open("stopwords/hit_stopwords.txt", encoding="utf-8").readlines()]  # 加载停用词
with open('Dict/txt_permission.json', 'r', encoding='utf-8') as f:
    p_map = json.load(f)
f.close()
with open("Dict/0504_permission描述汇总_Protection-level_.json", 'r', encoding='utf-8') as f:
    permission_des = json.load(f)
f.close()
def permission_base_approach(sentence):
    result_list = []
    result = re.findall(r'授权.*权限',sentence)
    if result:
        result_list.append(result[0][2:])
    result = re.findall(r'申请.*权限', sentence)
    if result:
        result_list.append(result[0][2:])
    result = re.findall(r'的.*权限', sentence)
    if result:
        result_list.append(result[0][2:])
    result = re.findall(r'及.*权限', sentence)
    if result:
        result_list.append(result[0][2:])
    result = re.findall(r'发送.*权限', sentence)
    if result:
        result_list.append(result[0][2:])
    result = re.search(r"(\S+)权限", sentence)
    if result:
        extracted_text = result.group(1)
        result_list.append(extracted_text)
    result = re.findall(r'享受.*权限',sentence)
    if result:
        result_list.append(result[0][2:])
    result = re.findall(r'开启.*权限',sentence)
    if result:
        result_list.append(result[0][2:])
    result = re.findall(r'需要.*权限',sentence)
    if result:
        result_list.append(result[0][2:])
    result = re.findall(r'使用.*权限',sentence)
    if result:
        result_list.append(result[0][2:])
    result = re.findall(r'-.*权限',sentence)
    if result:
        result_list.append(result[0][1:])
    result = re.findall(r'(?<=，)[\w\/\\]+权限',sentence)
    if result:
        result_list.append(result[0])
    result = re.findall(r'蓝牙', sentence)
    if result:
        result_list.append("蓝牙")
    return result_list
def delete_domain_stopwords(domain_stopwords_list,str_):
    for words in domain_stopwords_list:
        if words:
            str_ = str_.replace(words,"")
    if str_ == '系统系统':
        str_ = '系统'
    return str_
def spilt_str(result):
    if result:
        r = re.split(r'[、，/（）。：;；!和及或等并与1234567890]', result)
        return r
def remove_stopwords(sentence):
    #删除句子中的停用词，并返回句子。
    words = jieba.lcut(sentence)
    return ''.join([word for word in words if word not in stopwords])
def run_permission_base_approach(sentence):
    result_list = []
    #文本提取直接描述权限的文字。
    '''
    result = re.findall(r'蓝牙', sentence)
    if result:
        result_list.append("蓝牙")'''
    result = re.findall(r'.*?权限',sentence)
    #result_cut = []用于调试
    if result:
        sentence_list = re.split(r'[,，\t]',sentence)
        for s in sentence_list:
            result = permission_base_approach(s)
            if result:
                for r in result:
                    r_list= spilt_str(r)
                    for r_s in r_list:
                        r_s = delete_domain_stopwords(permission_doamin_stopwords,remove_stopwords(r_s))
                        if r_s:
                            result_list.append(r_s)
    #return list(set(result_list)),result_cut
    return list(set(result_list))
def data_permission_similarity(ch_data_item_list):
    with open('Dict/0504-data-permission-map.json','r',encoding='utf-8')as f:
        d_p_map = json.load(f)
    f.close()
    permission_list = []
    for data in ch_data_item_list:
        for dp in d_p_map['result']:
            if data == dp['data']['data-cn']:
                if dp['permission']:
                    for p in dp['permission']:
                        permission_list.append(p[0])
    return permission_list
nlp = spacy.load("zh_core_web_md")  # 加载中文模型
def sim(x,y):
    doc1 = nlp(x)
    doc2 = nlp(y)
    similarity = doc1.similarity(doc2)
    if similarity>0.7:
        return True
    else:
        return False
def permission_text_description_resp(permission_txt_list):
    result = []
    if permission_txt_list:
        for p_txt in permission_txt_list:
            flag = 0
            for p in p_map:
                if p_txt == p[0]:
                    for pi in p[2]:
                        result.append(pi)
                    flag = 1
                    break
            if flag == 0:
                for p in p_map:
                    if sim(p_txt,p[0]):
                        for pi in p[2]:
                            result.append(pi)
                        break
    return result
def run_permission_handle(data_cn_total,sentence_list,url):
    '''
    8月修改：添加url处理部分
    '''
    #优先显示子url中提取的危险权限
    permission_url_list = run_permission_son_url_extract(url)
    print("子页面权限：")
    print(permission_url_list)
    #if permission_url_list:两个方法取并集
       # return permission_url_list
    #数据项间接获取权限
    #permission_list = data_permission_similarity(data_cn_total)
    #直接获取权限
    permi_list = []
    permission_txt_list = []
    #先从隐私政策中提取直接描述权限的短语文本
    for sentence in sentence_list:
        permission_txt = run_permission_base_approach(sentence)
        if permission_txt:
            for p in permission_txt:
                permission_txt_list.append(p)
    if permission_txt_list:
        permi_list = permission_text_description_resp(permission_txt_list)
        print(permission_txt_list)
        print("文本对应权限：")
        print(permi_list)
    #result = list(set(permi_list+permission_list))数据项匹配权限方法
    result = list(set(permi_list + permission_url_list))
    re_result = []
    #8月修改，只显示危险权限
    for per_di in permission_des:
        if 'dangerous' in per_di['Protection level']:
            if per_di["permission"] in result:
                re_result.append(per_di["permission"])
    return re_result
#8.20修改，解析权限声明子url,输入为对应的url，返回值为危险权限列表
def is_valid_url(url):
    #判断url格式是否正常
    if url:
        pattern = re.compile(r'^https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+')
        try:
            match = re.match(pattern, url)
            return bool(match)
        except:
            return False
    else:
        return False

def permission_son_html_url(url):
    '''
    :param url: 隐私政策url
    :return: 返回权限声明页面的html对象
    '''
    pp_soup = html_response_soup(url)
    links = pp_soup.find_all('a')
    if not links:
        pp_soup = redirection_judge(pp_soup)
        links = pp_soup.find_all('a')
    for link in links:
        if is_valid_url(link.get('href')):
            permission_soup = html_response_soup(link.get('href'))
            try:
                text = permission_soup.get_text()
                if "权限列表" in text and "安卓" in text:
                    #print(link.get('href'))
                    return permission_soup
            except:
                continue
    return False
def permission_son_html_extract(permission_soup):
    permission_list = []
    if permission_soup:
        text = permission_soup.get_text()
        uppercase_text = text.upper()
        if "传感器" in uppercase_text:
            permission_list.append("BODY_SENSORS")
        for per_di in permission_des:
            if 'dangerous' in per_di['Protection level']:
                if per_di["permission"] in uppercase_text:
                    permission_list.append(per_di["permission"])
    #print(permission_list)
    #print(len(permission_list))
    return permission_list
def run_permission_son_url_extract(url):
    permission_soup = permission_son_html_url(url)
    permission_list = permission_son_html_extract(permission_soup)
    return permission_list

if __name__ == '__main__':
    '''
    url_list = read_txt_file('url.txt')
    for url in url_list:
        permission_son_html_extract(permission_son_html_url(url))'''
    #run_permission_son_url_extract("https://terms.alicdn.com/legal-agreement/terms/suit_bu1_taobao/suit_bu1_taobao201703241622_61002.html")
