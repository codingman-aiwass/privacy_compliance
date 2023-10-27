import json
import re
import os
from Privacy_Policy_approach import data_handle
from purpose_handle import run_purpose_handle
from _translate import run_data_translate
from _translate import run_data_translate2
from Privacy_Policy_approach import delete_purpose
from Privacy_Policy_approach import run_str
from _translate import run_translate
from permission_handle import run_permission_handle
data_dict_json = "Dict/隐私数据项_3_30.json"
chatgpt_data_json = "Dict/0531chatgpt.json"
def test(ori_dir):
    #"../ALiYun_Chinese_0305.txt"。
    f = open(ori_dir,encoding="utf-8")
    text = f.read()
    f.close()
    result_list = re.split(r'[。?？\n]',text)
    s_list = [x.replace('\n','') for x in result_list]
    s_list1 = [i for i in s_list if i !='']
    s_list2 = [x+'。' for x in s_list1]#为每句话添加.
    print("Success!")
    return s_list2
def d_list_handle(d_list):
    #对初步识别的结果进行处理
    d_list_handle = []
    purpose_cn_list = []
    purpose_en_list = []
    data_en_list = []
    data_en_chatgpt_list = []
    purpose_cut = d_list[0][2][:]
    # purpose处理:还需要处理的是，要把purpose拼接在一起
    if d_list[0][2]:
        purpose_cn_list,purpose_en_list=run_purpose_handle(d_list[0][2])
    data_total_list = []
    for d_to_p in d_list:
        if d_to_p:
            data_list = data_handle(d_to_p[0])
            if data_list:
                for d in data_list:
                    data_total_list.append(d)
    if data_total_list:
        data_total_list = list(set(data_total_list))
        data_total_list = delete_purpose(data_total_list)
        for d in data_total_list:
            data_en = run_data_translate(d,data_dict_json)
            data_en_chatgpt = run_data_translate2(d,chatgpt_data_json)
            if not data_en_chatgpt:
                data_en_chatgpt = [data_en]
            data_en_list.append(data_en)
            data_dict = {
                    "data-cn": d,
                    "data-en": data_en,
                    "subject": d_list[0][1],
                    "purpose-cn": purpose_cn_list,
                    "purpose-en": purpose_en_list
                }
            if data_en_chatgpt:
                data_en_chatgpt_list.append(data_en_chatgpt)
            d_list_handle.append(data_dict)
    return d_list_handle,data_total_list,data_en_list,purpose_cn_list,purpose_en_list,purpose_cut,data_en_chatgpt_list
def run_write_json(single_txt_path,save_json_path):
    # 对单个文本进行切割处理。获得单个句子的字符串列表。
    data_dict_list = []
    s_list = test(single_txt_path)
    data_total_list = []
    data_total_list_en = []
    purpose_total_list = []
    purpose_total_list_en = []
    data_total_list_en_chatgpt = []
    sentence_count = 0
    for sentence in s_list:
        d_list,single_data_list_firsthandle = run_str(sentence)
        # 再次处理的函数
        if d_list:
            single_sentence_handle_dict_list,single_data_total_list,single_data_en_list,single_purpose_cn_list,single_purpose_en_list,purpose_cut,data_en_chatgpt_list = d_list_handle(d_list)
            if single_sentence_handle_dict_list:
                sentence_count += 1
                single_sentence_dict = {"orig-sentence": sentence,
                                        "data-cn-list":single_data_total_list,
                                        "data-en-list":single_data_en_list,
                                        "data-en-chatgpt-list":data_en_chatgpt_list,
                                        "purpose-cn-list":single_purpose_cn_list,
                                        "purpose-en-list":single_purpose_en_list,
                                        "result_sentence":single_sentence_handle_dict_list}
                data_dict_list.append(single_sentence_dict)
                for d in single_data_total_list:
                    if d:
                        data_total_list.append(d)
                for d in single_data_en_list:
                    if d:
                        data_total_list_en.append(d)
                data_total_list_en_chatgpt.extend(data_en_chatgpt_list)
                for p in single_purpose_cn_list:
                    if p :
                        purpose_total_list.append(p)
    purpose_total_list = list(set(purpose_total_list))
    #翻译目的
    purpose_total_list_en,ch_en_list = run_translate(purpose_total_list)
    total_dict ={
        "sentence-count":sentence_count,"data-count":len(data_total_list),"purpose-count":len(purpose_total_list),
        "data-cn-total":list(set(data_total_list)),"data-en-total":list(set(data_total_list_en)),"data-en-chatgpt-total":data_total_list_en_chatgpt,
        "purpose-cn-total":purpose_total_list,"purpose-en-total":list(set(purpose_total_list_en))
    }
    for single_dict in data_dict_list:
        if single_dict["purpose-cn-list"]:
            for cn in single_dict["purpose-cn-list"]:
                try:
                    single_dict["purpose-en-list"].append(ch_en_list[cn])
                except:
                    continue
            for r in single_dict["result_sentence"]:
                r["purpose-en"] = single_dict["purpose-en-list"][:]
    write_list = [total_dict,data_dict_list]
    #权限：
    #获取url
    with open("result_pkgName_url.json",'r',encoding='utf-8')as f:
        url_name_dict = json.load(f)
    f.close()
    url = url_name_dict[os.path.basename(single_txt_path)[:-4]]#只需要改这里的逻辑就行,解析文件名字提取url,+后面到
    print(os.path.basename(single_txt_path)[:-4]+"------------")
    try:
        permission_list = run_permission_handle(list(set(data_total_list)),s_list,url)
        total_dict["permission_list"] = list(set(permission_list))
    except Exception as e:
        print(os.path.basename(single_txt_path)[:-4]+"权限提取失败")
        print(e)
    with open(save_json_path+".json", "w", encoding="utf-8") as f:
        json.dump(write_list, f, ensure_ascii=False, indent=2)
    return True

