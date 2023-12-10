import os
import sys
import traceback

from selenium_driver import driver
import re
import dashscope
from dashscope import Generation
from http import HTTPStatus
import json
dashscope.api_key="sk-14cf2f9bce7e4991a6887b0a3ff9c758"
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
def redirection_judge(soup):########################
    #print(str(soup))
    if re.search(r'window\.location\.href',str(soup)):
        #获取指向的URL
        script_tags = soup.find_all('script')
        for script_tag in script_tags:
            script_content = script_tag.string
            if script_content is not None and 'window.location.href' in script_content:
                url_match = re.search(r'window\.location\.href\s*=\s*["\'](.*?)["\']',script_content)
                if url_match:
                    target_url = url_match.group(1)
                    target_soup = html_response_soup(target_url)
                    if target_soup:
                        return target_soup
                    else:
                        return False
    else:
        return False
def is_valid_url(url):########################
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
def permission_son_html_soup(pp_soup):
    '''
    :param url: 隐私政策url
    :return: 返回权限声明页面的html对象
    '''
    try:
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
    except Exception as e:
        print(e)
    return False
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
def query_result_handle(i,temp_result):
    result_dict = {"permission": None, "judgment": 0, "description": None}
    try:
        if temp_result["judgment"] == 1:
            result_dict["permission"] = i
            result_dict["judgment"] = 1
            result_dict["description"] = temp_result["description"]
            return dict(result_dict),1
    except:
        if "1" in str(temp_result):
            result_dict["permission"] = i
            result_dict["judgment"] = 1
            result_dict["description"] = str(temp_result)
            return dict(result_dict),1
    return  {"permission":None,"judgment":0,"description":None},0
def run_permission_query(permission_list,prompt_f,url = None,txt_name = None):
    result_dict_list = []
    permission_son_txt = None
    result_dict = {"permission":None,"judgment":0,"description":None}
    if txt_name:
        with open(txt_name,'r',encoding='utf-8')as f:
            privacy_policy = f.read().replace('\n',' ')
        f.close()
    elif url:
        soup = html_response_soup(url)
        if soup:
            privacy_policy = soup.get_text()
            permission_soup = permission_son_html_soup(soup)
            if permission_soup:
                permission_son_txt = permission_soup.get_text()
        else:
            print("爬取  "+url+"  失败！")
    if permission_list and privacy_policy:
        for i in permission_list:
            temp_dict =  {"permission":None,"judgment":0,"description":None}
            flag = 0
            if i in privacy_policy or permission_son_txt and i in permission_son_txt:
                result_dict["permission"] = i
                result_dict["judgment"] = 1
                result_dict["description"] = "直接匹配"
                result_dict_list.append(dict(result_dict))
            else:#输入大模型。
                if permission_son_txt:#优先权限子链接页面输入判断
                    temp_prompt = prompt_f.format(i,permission_son_txt)
                    print(temp_prompt)
                    temp_result = query_LLM_qianwen(temp_prompt)
                    temp_dict,flag = query_result_handle(i,temp_result)
                    if temp_dict["permission"]:
                        result_dict_list.append(dict(temp_dict))
            #如果没有在权限子链接中，则继续输入隐私政策查询
                if flag == 0:
                    temp_prompt = prompt_f.format(i,privacy_policy)
                    print(temp_prompt)
                    temp_result = query_LLM_qianwen(temp_prompt)
                    temp_dict, flag = query_result_handle(i, temp_result)
                    if temp_dict["permission"]:
                        result_dict_list.append(dict(temp_dict))
                if not temp_dict["permission"]:
                    result_dict["permission"] = i
                    result_dict["judgment"] = 0
                    result_dict["description"] = ""
                    result_dict_list.append(dict(result_dict))
    else:
        print("错误输入！")
    with open("permission_query_result.json",'w',encoding='utf-8')as f:
        json.dump(result_dict_list,f,indent=4, ensure_ascii=False)
    f.close()
def run_permission_query_cut(permission_list,prompt_f,url = None,txt_name = None):
    result_dict_list = []
    permission_son_txt = None
    result_dict = {"permission":None,"judgment":0,"description":None}
    if txt_name:
        with open(txt_name,'r',encoding='utf-8')as f:
            privacy_policy = f.read().replace('\n',' ')
        f.close()
    elif url:
        soup = html_response_soup(url)
        if soup:
            privacy_policy = soup.get_text()
            permission_soup = permission_son_html_soup(soup)
            if permission_soup:
                permission_son_txt = permission_soup.get_text()
        else:
            print("爬取  "+url+"  失败！")
    if permission_list and privacy_policy:
        for i in permission_list:
            temp_dict =  {"permission":None,"judgment":0,"description":None}
            flag = 0
            if i in privacy_policy or permission_son_txt and i in permission_son_txt:
                result_dict["permission"] = i
                result_dict["judgment"] = 1
                result_dict["description"] = "直接匹配"
                result_dict_list.append(dict(result_dict))
            else:#输入大模型。
                if permission_son_txt:#优先权限子链接页面输入判断
                    temp_prompt = prompt_f.format(i,permission_son_txt)
                    print(temp_prompt)
                    temp_result = query_LLM_qianwen(temp_prompt)
                    temp_dict,flag = query_result_handle(i,temp_result)
                    if temp_dict["permission"]:
                        result_dict_list.append(dict(temp_dict))
            #如果没有在权限子链接中，则继续输入
                if flag == 0:
                    privacy_policy_segments = cut_privacy_policy(privacy_policy)
                    print("切割长度：--"+str(len(privacy_policy_segments)))
                    for pp in privacy_policy_segments:
                        if flag == 0 and len(pp)>10:
                            temp_prompt = prompt_f.format(i,pp)
                            print(temp_prompt)
                            temp_result = query_LLM_qianwen(temp_prompt)
                            temp_dict, flag = query_result_handle(i, temp_result)
                            if temp_dict["permission"]:
                                result_dict_list.append(dict(temp_dict))
                if not temp_dict["permission"]:
                    result_dict["permission"] = i
                    result_dict["judgment"] = 0
                    result_dict["description"] = ""
                    result_dict_list.append(dict(result_dict))
    else:
        print("错误输入！")
    with open(f"permission_query_res_save_dir/{os.path.basename(txt_name)[:-4]}_permission_query_result.json",'w',encoding='utf-8')as f:
        json.dump(result_dict_list,f,indent=4, ensure_ascii=False)
    f.close()

if __name__ == '__main__':
    prompt_f = """你将分析下面用三个横杠分隔的隐私政策片段文本和用三个横杠分隔的权限，只需返回下文要求的文本分析的json格式结果，而不是代码步骤。请以里面的内容为基础，判断有无提到使用---{}权限---，并提取原文中描述使用该权限的字句并以json格式提供以下keys:judgment,description
注意事项：
-需要先读取整个隐私政策片段文本再做判断。
-只返回一个基于整个文本的最终判断结果，且不要返回指定之外的key值。
-权限定义只是辅助权限判断任务，请聚焦分析三个单引号分隔的权限。
权限定义：
-人体传感器BODY_SENSORS权限定义：授权应用访问那些被用于测量用户身体状况的传感器数据。
-ACCESS_FINE_LOCATION权限定义:获取精准的位置，如gps。
-ACCESS_COARSE_LOCATION权限定义：获取 (基于网络的)大概位置。
-RECORD_AUDIO权限定义：授权应用可以使用麦克风。
分析通过以下步骤：
步骤1：读取隐私政策文本。
步骤2：理解三个单引号中分隔的权限意义，
步骤3：基于读取的隐私政策文本，判断是否声明使用三个单引号中分隔的权限
步骤4：如果判断该隐私政策声明使用了这个权限，提取原文中描述使用该权限的字句；如果无，则不提取。
步骤5：返回json格式结果。keys中judgment的值为0或1，0表示该隐私政策文本未声明使用该权限，这时description值为空；1表示该隐私政策文本声明使用该权限，description的值为步骤3提取的字句。
---{}---
"""
    permission_list = ["蓝牙","摄像头","麦克风","计步传感器","相册","相机","位置","通讯录","接收短信", "发送短信","通知","存储","运动健康","拨打电话",
                       "粗略位置","剪贴板","定位","存储读写","日历","图片库"]
    ###分段输入隐私政策查询，适用于大模型输入字数受限情况。
    #输入隐私政策url
    if 'compliance_query_res_save_dir' not in os.listdir('.'):
        os.mkdir('compliance_query_res_save_dir')

    # 尝试从Privacypolicy_txt中获取隐私政策文本txt
    # try:
    #     pkgName_or_folder = sys.argv[1]
    #     use_history = sys.argv[2]
    #     successful_set = None
    #     if use_history == 'y':
    #         # 尝试读取AppUIAutomator2Navigation下的successful_query_compliance.txt
    #         try:
    #             with open('../../AppUIAutomator2Navigation/successful_query_permission.txt','r',encoding='utf-8') as f:
    #                 successful_set = set([line for line in f.readlines()])
    #         except FileNotFoundError:
    #             print('successful_query_compliance.txt not exists...')
    #     if '/' in pkgName_or_folder:
    #         # 说明是文件夹
    #         pkgNames = os.listdir(pkgName_or_folder)
    #         for app in pkgNames:
    #             if successful_set is not None:
    #                 if app not in successful_set:
    #                     print('have to query permission in if...')
    #                     run_permission_query_cut(permission_list, prompt_f, url=None, txt_name=f"{pkgName_or_folder}/{app}")
    #             else:
    #                 # 走到这里，说明successful_set 为空，那就必须分析了
    #                 print('have to query permission in if-else...')
    #                 run_permission_query_cut(permission_list, prompt_f, url=None, txt_name=f"{pkgName_or_folder}/{app}")
    #     else:
    #         # 说明是单个应用的包名
    #         if successful_set is not None:
    #             # 没有请求成功的才需要分析
    #             if pkgName_or_folder not in successful_set:
    #                 print('have to query permission in else-if...')
    #                 run_permission_query_cut(permission_list, prompt_f, url=None,
    #                                      txt_name="Privacypolicy_txt/" + f"{pkgName_or_folder}.txt")
    #         else:
    #             # 走到这里，说明successful_set 为空，那就必须分析了
    #             print('have to query permission in else-else...')
    #             run_permission_query_cut(permission_list, prompt_f, url=None, txt_name="Privacypolicy_txt/" + f"{pkgName_or_folder}.txt")
    # except IndexError:
    while True:
        input_url_or_txt = input('input privacy policy of url or txt you want to query,q to quit.')
        if input_url_or_txt == 'q':
            break
        elif input_url_or_txt.endswith('.txt'):
            run_permission_query_cut(permission_list, prompt_f, url=None,
                                     txt_name="Privacypolicy_txt/" + input_url_or_txt)
        else:
            run_permission_query_cut(permission_list, prompt_f, url=input_url_or_txt,
                                     txt_name=None)
        # 没有获取到输入的应用包名，直接尝试分析Privacypolicy_txt下的所有文本
        # traceback.print_stack()
        # pkgNames = os.listdir('Privacypolicy_txt')
        # for app in pkgNames:
        #     print('have to query permission in IndexError exception...')
        #     run_permission_query_cut(permission_list,prompt_f,url = None,txt_name="Privacypolicy_txt/"+app)
    #或是输入txt文件的地址
    #run_permission_query_cut(permission_list,prompt_f,txt_name = "Privacypolicy_txt/"+"cn.damai.txt")

    ###完整的隐私政策输入：
    #输入隐私政策url
    #run_permission_query(permission_list,prompt_f,url = None)
    # 或是输入txt文件的地址
    # run_permission_query(permission_list,prompt_f,txt_name = "Privacypolicy_txt/"+"cn.damai.txt")