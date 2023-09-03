import re
import spacy
from Privacy_Policy_approach import remove_stopwords
from Privacy_Policy_approach import delete_purpose
purpose_doamin_stopwords = [line.strip() for line in open("stopwords/purpose_domain_stopwords.txt", encoding="utf-8").readlines()]
nlp_trf = spacy.load("zh_core_web_trf")
def single_purpose(text,nlp):
    #使用依存句法分析提取谓语与其宾语
    #text = "您使用本产品接入的第三方服务"
    predicate = None
    doc = nlp(text)
    for token in doc:
        if token.dep_ == "ROOT":
            predicate = token
            object = [child for child in token.children if child.dep_ == "dobj"]
            if object:
                object = object[0]
            else:
                object = None
    if predicate:
        if object:
            return [predicate.text,object.text]
        else:
            return []
    else:
        return []
def delete_data_in_purpose(str_):
    result_list = []
    result = re.findall(r'提供.*?[,|，|。|.|;|；|:|：]', str_+'.')
    if result:
        result_list.append(result[0][:-1])
    result = re.findall(r'收集.*?[,|，|。|.|;|；|:|：]', str_+'.')
    if result:
        result_list.append(result[0][:-1])
    for i in result_list:
        if i:
            str_ =str_.replace(i,"")
    return str_
def delete_domain_stopwords(domain_stopwords_list,str_):
    for words in domain_stopwords_list:
        if words:
            str_ = str_.replace(words,"")
    return str_
def delete_contain(str_):
    #删除句子中包含（），()之类的
    result_list = []
    result = re.findall(r'（.*?[）|)|（|(|.]', str_+".")
    if result:
        result_list.append(result[0][:])
    result = re.findall(r'\(.*?[）|)|（|(|.]', str_+".")
    if result:
        result_list.append(result[0][:])
    for i in result_list:
        if i:
            str_ =str_.replace(i[:-1],"")
    return str_
def spilt_str(result):
    result = re.sub(r'\d+','',result)
    if result:
        r = re.split(r'[、，/（）。：;；!“”""和及或并中时与]', result)
        return r
    else:
        return []
def purpose_handle_single(purpose):
    purpose = delete_data_in_purpose(purpose)
    purpose = delete_contain(purpose)
    purpose_list = spilt_str(purpose)
    result_list = []
    for pi in purpose_list:
        if pi:
            result = delete_domain_stopwords(purpose_doamin_stopwords,remove_stopwords(pi))
            if len(result)<=4 and len(result)>1:
                result_list.append(result)
            else:
                spacy_result = single_purpose(result,nlp_trf)
                if spacy_result:
                    result_list.append(spacy_result[0]+spacy_result[1])
    return list(set(result_list))
def purpose_handle_single_2(purpose):
    purpose_list = spilt_str(purpose)
    for pi in purpose_list:
        pi = remove_stopwords(pi)
        purpose_result = delete_domain_stopwords(purpose_doamin_stopwords,pi)
        if purpose_result:
            return [purpose_result]
        else:
            if "服务" in pi:
                return []
            if "功能" in pi:
                return []
            if "操作" in pi:
                return []
            if "内容" in pi:
                return []
            if "过程" in pi:
                return []
    return []
def run_purpose_handle(purpose_list):
    purpose_cn_list = []
    purpose_en_list = []
    flag = 0
    for pi in purpose_list:
        pi = re.sub(r"\s+", "", pi)
        pi_result_list = purpose_handle_single(pi)
        if pi_result_list:
            for r in pi_result_list:
                if len(r)>1:
                    if r == '服务':
                        purpose_cn_list.append('')
                    else:
                        purpose_cn_list.append(r)
        else:
            pi_result_list2 = purpose_handle_single_2(pi)
            if pi_result_list2:
                if len(pi_result_list2[0])>1:
                    if pi_result_list2[0] == '服务':
                        purpose_cn_list.append('')
                    else:
                        purpose_cn_list.append(pi_result_list2[0])
                    purpose_cn_list = list(set(purpose_cn_list))
        if "服务" in pi or "功能" in pi:
            flag = 1
    if not purpose_cn_list and flag:
        purpose_cn_list.append("")
    purpose_cn_list = list(set(purpose_cn_list))
    purpose_cn_list = [x for x in purpose_cn_list if x != "提供服务"]
    purpose_cn_list = delete_purpose(purpose_cn_list)
    purpose_cn_list = list(set(purpose_cn_list))
    return purpose_cn_list,purpose_en_list