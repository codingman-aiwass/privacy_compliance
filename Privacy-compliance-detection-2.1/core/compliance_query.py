import os
import sys
import traceback

import configparser

from selenium_driver import driver
import re
import dashscope
from dashscope import Generation
from http import HTTPStatus
import json
def get_config_settings(config_file):
    config = configparser.ConfigParser()
    config.read(config_file, encoding='utf-8')
    pairs = []
    for section in config.sections():
        pairs.extend(config.items(section))
    dic = {}
    for key, value in pairs:
        dic[key] = value
    return dic
config_settings = get_config_settings('api_key.ini')
dashscope.api_key=config_settings['dashscope_api_key']
def split_str_5000(str_list):
    if str_list:
        for i in range(0,len(str_list)):
            if len(str_list[i])>5200:
                temp1 = int(len(str_list[i])/2)
                for a in range(1,1000):
                    if temp1<len(str_list[i]) and str_list[i][temp1] == '。' or str_list[i][temp1] == '\n':
                        temp_str = str_list[i][:]
                        del str_list[i]
                        str_list.insert(i,temp_str[:temp1])
                        str_list.insert(i,temp_str[temp1:])
                        break
                    else:
                        temp1 +=1
        for i in range(0,len(str_list)):
            if len(str_list[i])>5300:
                temp1 = int(len(str_list[i])/2)
                for a in range(1,1000):
                    if temp1<len(str_list[i]) and str_list[i][temp1] == '。' or str_list[i][temp1] == '\n':
                        temp_str = str_list[i][:]
                        del str_list[i]
                        str_list.insert(i,temp_str[:temp1])
                        str_list.insert(i,temp_str[temp1:])
                        break
                    else:
                        temp1 +=1
    return str_list
def html_response_soup(url):##################################合并时记得替换
    try:
        soup = driver.get_privacypolicy_html(url)
        if soup:
            return soup
        else:
            print("获取网页"+url+"失败！")
            return None
    except Exception as e:
        print("请求"+str(url)+"失败："+str(e))
        return None
def cut_privacy_policy(long_string):
    '''
    :param long_string: 隐私政策长文本
    :param n: 需要将隐私政策切成n部分。
    :return: 返回包含n个以内字符串元素的列表,这个n为字符串长度除以4000
    '''
    #如果字符串大小小于3000，则直接返回该字符串列表，只有这一个元素。
    if len(long_string)<3500:
        return [long_string]
    else:
        segments = split_str_5000([long_string])
        return segments
    return []
def query_LLM_qianwen(prompt_text):
    result = None
    temp_dict = ""
    t1 = ""
    response = Generation.call(
        model='qwen-14b-chat',
        #model='qwen-7b-chat-v1',
        prompt=prompt_text
    )
    if response.status_code == HTTPStatus.OK:
        temp = json.dumps(response.output, indent=4, ensure_ascii=False)
        try:
            temp_dict = json.loads(temp)
            result = json.loads(temp_dict['text'])
        except:
            try:
                if isinstance(temp_dict, dict):
                    result = temp_dict
                else:
                    temp_dict = json.loads(temp)
                    t1 = json.loads(temp_dict)
                    result = json.loads(t1['text'])
            except:
                if isinstance(t1,dict):
                    result = t1
                else:
                    result = temp
    return result
def run_compliance_query(compliance_list,prompt_f,url = None,txt_name = None):
    result_dict_list = []
    if txt_name:
        with open(txt_name,'r',encoding='utf-8')as f:
            privacy_policy = f.read().replace('\n',' ')
        f.close()
    elif url:
        soup = html_response_soup(url)
        if soup:
            privacy_policy = soup.get_text()
        else:
            print("爬取  "+url+"  失败！")
    if compliance_list and privacy_policy:
        for i in compliance_list:
            temp_dict =  {"compliance":i,"result":[]}
            temp_prompt = prompt_f.format(i, privacy_policy)
            temp_result = query_LLM_qianwen(temp_prompt)
            temp_dict["result"].append(temp_result)
            result_dict_list.append(dict(temp_dict))
    else:
        print("错误输入！")
    with open("compliance_query_result.json",'w',encoding='utf-8')as f:
        json.dump(result_dict_list,f,indent=4, ensure_ascii=False)
    f.close()
def run_compliance_query_cut(compliance_list,prompt_f,url = None,txt_name = None):
    result_dict_list = []
    privacy_policy = None
    if txt_name:
        with open(txt_name,'r',encoding='utf-8')as f:
            privacy_policy = f.read().replace('\n',' ')
        f.close()
    elif url:
        soup = html_response_soup(url)
        if soup:
            privacy_policy = soup.get_text()
        else:
            print("爬取  "+url+"  失败！")
    if compliance_list and privacy_policy:
        for i in compliance_list:
            temp_dict =  {"compliance":i,"result":[]}
            privacy_policy_segments = cut_privacy_policy(privacy_policy)
            for pp in privacy_policy_segments:
                temp_prompt = prompt_f.format(i, pp)
                temp_result = query_LLM_qianwen(temp_prompt)
                temp_dict["result"].append(temp_result)
            result_dict_list.append(dict(temp_dict))
    else:
        print("错误输入！")
    with open(f"compliance_query_res_save_dir/{os.path.basename(txt_name)[:-4]}_compliance_query_result.json",'w',encoding='utf-8')as f:
        json.dump(result_dict_list,f,indent=4, ensure_ascii=False)
    f.close()
if __name__ == '__main__':
    prompt_f = '''你将分析下面用三个横杠分隔的隐私政策文本和用三个井号分隔的监管项。请基于隐私政策内容判断是否违反该监管项，并以json格式提供以下keys:comprehend,relevance,judgment,description
注意事项：
-监管项中可能会存在并列的细分监管描述，如果要判断隐私政策文本不违反监管项，则这些细分监管描述也必须全部不违反。
分析通过以下步骤：
步骤1：读取并理解监管项,如果理解了监管项，则comprehend值为1，不理解为0.
步骤2：读取隐私政策文本，如果该隐私政策文本与监管项有关，则relevance值为1，进入步骤3；无关则为0并且进入步骤5，其余键的值为空.
步骤3：如果该隐私政策文本有关，relevance值为1，则进一步分析该隐私政策文本是否违反该监管项，如果违反则judgement值为1，不违反则为0；
步骤4：description的值为步骤3中违反或者不违反监管项的原因。
步骤5：返回json结果。
###{}###
---{}---
'''


    compliance_list = ["未建立并公布个人信息安全投诉、举报渠道，或未在承诺时限内（承诺时限不得超过15个工作日，无承诺时限的，以15个工作日为限）受理并处理的。"]
    ###分段输入隐私政策查询，适用于大模型输入字数受限情况。
    # 输入隐私政策url
    #run_compliance_query_cut(compliance_list, prompt_f, url=None)
    # 或是输入txt文件的地址
    # run_compliance_query_cut(compliance_list,prompt_f,txt_name="Privacypolicy_txt/"+"com.youku.phone.txt")
    if 'permission_query_res_save_dir' not in os.listdir('.'):
        os.mkdir('permission_query_res_save_dir')

    # try:
    #     pkgName_or_folder = sys.argv[1]
    #     use_history = sys.argv[2]
    #     successful_set = None
    #     if use_history == 'y':
    #         # 尝试读取AppUIAutomator2Navigation下的successful_query_compliance.txt
    #         try:
    #             with open('../../AppUIAutomator2Navigation/successful_query_compliance.txt','r',encoding='utf-8') as f:
    #                 successful_set = set([line for line in f.readlines()])
    #         except FileNotFoundError:
    #             print('successful_query_compliance.txt not exists...')
    #     if '/' in pkgName_or_folder:
    #         # 说明是文件夹
    #         pkgNames = os.listdir(pkgName_or_folder)
    #         for app in pkgNames:
    #             if successful_set is not None:
    #                 if app not in successful_set:
    #                     print('have to query compliance in if...')
    #                     run_compliance_query_cut(compliance_list,prompt_f, url=None, txt_name=f"{pkgName_or_folder}/{app}")
    #             else:
    #                 # 走到这里，说明successful_set 为空，那就必须分析了
    #                 print('have to query compliance in if-else...')
    #                 run_compliance_query_cut(compliance_list,prompt_f, url=None, txt_name=f"{pkgName_or_folder}/{app}")
    #     else:
    #         # 说明是单个应用的包名
    #         if successful_set is not None:
    #             # 没有请求成功的才需要分析
    #             if pkgName_or_folder not in successful_set:
    #                 print('have to query compliance... in else if')
    #                 run_compliance_query_cut(compliance_list,prompt_f, url=None,
    #                                      txt_name="Privacypolicy_txt/" + f"{pkgName_or_folder}.txt")
    #         else:
    #             # 走到这里，说明successful_set 为空，那就必须分析了
    #             print('have to query compliance... in else-else')
    #             run_compliance_query_cut(compliance_list, prompt_f, url=None, txt_name="Privacypolicy_txt/" + f"{pkgName_or_folder}.txt")
    #
    # except IndexError:
    while True:
        input_url_or_txt = input('input privacy policy of url or txt you want to query,q to quit.')
        if input_url_or_txt == 'q':
            break
        elif input_url_or_txt.endswith('.txt'):
            run_compliance_query_cut(compliance_list, prompt_f, url=None, txt_name="Privacypolicy_txt/" + input_url_or_txt)
        else:
            run_compliance_query_cut(compliance_list, prompt_f, url=input_url_or_txt,
                                     txt_name=None)

        # 没有获取到输入的应用包名，直接尝试分析Privacypolicy_txt下的所有文本
        # pkgNames = os.listdir('Privacypolicy_txt')
        # for app in pkgNames:
        #     print('have to query permission in IndexError exception...')
        #     run_compliance_query_cut(compliance_list,prompt_f,url = None,txt_name="Privacypolicy_txt/"+app)


    # try:
    #     pkgName = sys.argv[1]
    #     run_compliance_query_cut(compliance_list,prompt_f,txt_name="Privacypolicy_txt/"+f"{pkgName}.txt")
    # except IndexError:
    #     # 没有获取到输入的应用包名，直接尝试分析Privacypolicy_txt下的所有文本
    #     pkgNames = os.listdir('Privacypolicy_txt')
    #     for app in pkgNames:
    #         run_compliance_query_cut(compliance_list,prompt_f,txt_name="Privacypolicy_txt/"+app)
    ###完整的隐私政策输入：
    # 输入隐私政策url
    # run_compliance_query(compliance_list,prompt_f,url = None)
    # 或是输入txt文件的地址
    # run_compliance_query(compliance_list,prompt_f,txt_name = "Privacypolicy_txt/"+"cn.damai.txt")