import json
import re
from bs4 import BeautifulSoup
from bs4 import element
from selenium_driver import driver
from SDK_analysis import run_SDK_analysis
def read_txt_file(file_path):
# 打开文件
    with open(file_path, 'r') as f:
# 读取所有行
        lines = f.readlines()
# 关闭文件
    f.close()
# 返回列表
    new_lines = [string.replace('\n','') for string in lines]
    return new_lines
def read_json_file(file_path):
    with open(file_path,'r',encoding='utf-8')as f:
        data = json.load(f)
    f.close()
    return data
def has_chinese_char(text):
    pattern = re.compile(r'[\u4e00-\u9fa5]')
    match = pattern.search(text)
    if match:
        return True
    else:
        return False
def html_response_soup(url):
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
def extract_chinese(text):
    pattern = re.compile(r'[\u4e00-\u9fa5]')
    # 匹配所有中文字符的正则表达式，范围为Unicode编码中的中文字符
    chinese_chars = re.findall(pattern, text)
    return ''.join(chinese_chars)
def html_handle(soup):
    #得到网页title:
    title_tag = soup.title
    #print(title_tag)
    #print(extract_chinese(str(title_tag)))
    #得到隐私政策内容,在<body></body>标签
    body_tag = soup.body
    result = []
    for child in body_tag.children:
        text = []
        if len(list(child.children)) > 0:
            for grand in child.children:
                temp = grand.get_text()
                temp = temp.replace(" ", "\n")
                if is_contain_chinese(temp):
                    text.append(temp)
        if text:
            result.extend(text)
    return extract_chinese(str(title_tag)), result
def spilt_join_tags(text):
    pattern = re.compile(r'<[^>]+>')
    result = pattern.split(text)
    res = ''.join(s+'\n' for s in result)
    return res
def has_more_than_newlines(text):
    count = text.count('\n')
    return count >= 20
def is_contain_chinese(s):
    """
    判断字符串s是否含有中文字符
    """
    pattern = re.compile(r'[\u4e00-\u9fa5]')  # 匹配中文字符的正则表达式
    chinese_chars = pattern.findall(s)
    return len(chinese_chars) >= 5
def is_element_tag(c):
    return isinstance(c,element.Tag)
def nbsp_rechange(result_list):
    result = []
    if result_list:
        for r in result_list:
            r = r.replace(" ",' ')
            result.append(r)
    return result
def pingjie_merge(new_result):
    temp_list = [",","，","、","/","“","”","如","-","或","(","（","."]
    if new_result:
        new_list = []
        merge_next = False
        merged_r = ""
        # ，为末尾,则该元素与下一个元素合并
        for r in new_result:
            if merge_next:
                temp = merged_r + r
                merged_r = temp
                merge_next = False
                new_list.append(merged_r)
            elif any(r.endswith(t) for t in temp_list):
                merged_r = r
                merge_next = True
            else:
                new_list.append(r)
        return new_list
def pingjie_previous(result_list):
    new_result = []
    previous_element = None
    temp_list = ["：",":","”","“","/",",","是指","，","指",")","）","、","】","]","-","或"]
    if result_list:
        for r in result_list:
            #:,为首，则该元素与上一个元素合并
            if previous_element is not None and any(r.startswith(t) for t in temp_list):
                temp = previous_element + r
                new_result[-1] = temp
            else:
                new_result.append(r)
                previous_element = r
    return new_result
def pingjie(result_list):
    #由于html排版等原因，一句话可能在同级的不同标签，借此拼接。
    new_result = pingjie_previous(result_list)
    #，为末尾,则该元素与下一个元素合并
    new_result = pingjie_merge(pingjie_merge(new_result))
    return pingjie_merge(new_result)
def html_handle2(soup):
    title_tag = soup.title
    body_tag =soup.body
    result = []
    for c in body_tag.contents:
        if is_element_tag(c):
            if is_contain_chinese(str(c)):
                for child in c.children:
                    text = []
                    if is_element_tag(child):
                        #(child.prettify())
                        for grand in child.children:
                            if is_element_tag(grand):
                                temp = grand.get_text()
                                temp = temp.replace(" ", "\n")
                                if is_contain_chinese(temp):
                                    text.append(temp)
                            if isinstance(grand,element.NavigableString):
                                text.append(grand)
                    if isinstance(child,element.NavigableString):
                        text.append(str(child))
                    if text:
                        result.extend(text)
    return extract_chinese(str(title_tag)), result
def redirection_judge(soup):
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
def url_analysis(url):
    '''
    :param url: 隐私政策链接
    :return: 在Privacypolicy_txt目录下，生成以页面title命名的txt隐私政策文本
    '''
    soup = html_response_soup(url)
    if soup:
        try:
            name, result = html_handle(soup)
            if result:
                if len(result)>4:
                    with open('Privacypolicy_txt/'+name+".txt",'w',encoding='utf-8')as f:
                        for i in result:
                            f.write("%s\n" % i)
                    print(str(url)+"解析成功"+name)
                    f.close()
                else:
                    name,result = html_handle2(soup)
                    with open('Privacypolicy_txt/'+name+".txt",'w',encoding='utf-8')as f:
                        for i in result:
                            f.write("%s\n" % i)
                    f.close()
                    print(str(url) + "解析成功" + name)
        except:
            try:
                name, res = html_handle2(soup)
                if res:
                    with open('Privacypolicy_txt/' + name + ".txt", 'w', encoding='utf-8') as f:
                        for i in res:
                            f.write("%s\n" % i)
                    f.close()
                    print(str(url) + "解析成功" + name)
            except Exception as e:
                print(str(url)+"解析失败！失败原因："+str(e))
def url_juudge(value):
    if len(value[1])==1:
        url = value[1][0]
        soup = html_response_soup(url)
        return soup, url
    elif len(value[1])<1:
        print("无有效输入隐私政策")
        return False
    else:
        for u in value[1]:
            soup = html_response_soup(u)
            try:
                temp_text = soup.get_text()
            except Exception as e:
                print(e)
            if value[0].replace("视频","") in temp_text and '隐私' in temp_text and '政策':
                return soup,u
    return None,value[1][0]
def clean_url_dict(packagename_url_dict):
    def check_suffix(s):
        suffix_list = ['css', 'js', 'ico','png','gif','webp','callback','aes','woff2','woff']
        for suffix in suffix_list:
            if s.endswith(suffix):
                return -1
            if suffix in s:
                return 0
        return 1
    if isinstance(packagename_url_dict,dict):
        result_dict ={}
        for key in packagename_url_dict:
            if len(packagename_url_dict[key][1])==1:
                result_dict[key] = packagename_url_dict[key][:]
                continue
            else:
                result_dict[key] = []
                result_dict[key].append(packagename_url_dict[key][0])
                temp = []
                temp1 = []
                for url in packagename_url_dict[key][1]:
                    flag = check_suffix(url)
                    if flag == 1:
                         temp.append(url)
                    if flag ==0:
                        temp1.append(url)
                if temp:
                    if len(temp)>1:
                        temp = list(set(temp))
                    result_dict[key].append(temp[:])
                else:
                    if temp1:
                        if len(temp1) > 1:
                            temp1 = list(set(temp1))
                        result_dict[key].append(temp1[:])
    else:
        print("输入错误")
    return result_dict
def url_analysis2(value_url,packagename):
    '''
    :param url: 隐私政策链接
    :param packagename: 应用程序对应的包名
    :return: 在Privacypolicy_txt目录下生成，以对应包名命名的txt隐私政策文本
    '''
    soup,url = url_juudge(value_url)
    if soup:
        try:
            name, result = html_handle(soup)
            SDK_result = run_SDK_analysis(url=url,soup=soup)
            if result:
                result = pingjie(nbsp_rechange(result))
                if len(result)>4:
                    with open('Privacypolicy_txt/'+packagename+".txt",'w',encoding='utf-8')as f:
                        for i in result:
                            f.write("%s\n" % i)
                    print(str(url)+"解析成功"+packagename)
                    f.close()
                else:
                    name,result = html_handle2(soup)
                    if result:
                        result = pingjie(nbsp_rechange(result))
                        with open('Privacypolicy_txt/'+packagename+".txt",'w',encoding='utf-8')as f:
                            for i in result:
                                f.write("%s\n" % i)
                        f.close()
                        print(str(url) + "解析成功" + packagename)
            if SDK_result:
                print("sdk解析成功！")
            with open('PrivacyPolicySaveDir/' + packagename + "_sdk.json", 'w', encoding='utf-8') as f:
                json.dump(SDK_result, f, ensure_ascii=False, indent=2)
            f.close()
        except:
            try:
                name, res = html_handle2(soup)
                SDK_result = run_SDK_analysis(url=url,soup=soup)
                if res:
                    res = pingjie(nbsp_rechange(res))
                    with open('Privacypolicy_txt/' + packagename + ".txt", 'w', encoding='utf-8') as f:
                        for i in res:
                            f.write("%s\n" % i)
                    f.close()
                    print(str(url) + "解析成功" + packagename)
                else:
                    soup = redirection_judge(soup)
                    if soup:
                        name,res2 = html_handle2(soup)
                        SDK_result = run_SDK_analysis(url=url, soup=soup)
                        if res2:
                            res2 = pingjie(nbsp_rechange(res2))
                            with open('Privacypolicy_txt/' + packagename +".txt", 'w', encoding='utf-8') as f:
                                for i in res2:
                                    f.write("%s\n" % i)
                            f.close()
                            print(str(url) + "解析成功" + packagename)
                if SDK_result:
                    print("sdk解析成功！")
                with open('PrivacyPolicySaveDir/'+packagename+"_sdk.json",'w',encoding='utf-8')as f:
                    json.dump(SDK_result, f, ensure_ascii=False, indent=2)
                f.close()
            except Exception as e:
                print(str(url)+"解析失败！失败原因："+str(e))
        return url
    else:
        print("无有效隐私政策链接输入")
        return None
def run_url_analysis(filepath):
    #如果是url.txt文件
    if filepath.endswith('txt'):
        url_list = read_txt_file(filepath)
        for url in url_list:
            url_analysis(url)
    #如果是json文件：
    if filepath.endswith('json'):
        new_pkgname_dict = {}
        packagename_url_dict = read_json_file(filepath)
        if packagename_url_dict:
            temp = clean_url_dict(packagename_url_dict)
            for key in temp:
                url = url_analysis2(temp[key],key)
                if url:
                    new_pkgname_dict[key] = url

        if new_pkgname_dict:
            with open("result_pkgName_url.json",'w',encoding='utf-8')as f:
                json.dump(new_pkgname_dict,f, ensure_ascii=False, indent=2)
            f.close()
if __name__ == '__main__':
    '''
    url_list = read_txt_file('url.txt')
    for url in url_list:
        url_analysis(url)    '''
    #read_json_file('temp/pkgName_url.json')
    #总体调试
    run_url_analysis('pkgName_url(1).json')
    #单个调试
    url_analysis2(['蚂蚁金融',["https://render.alipay.com/p/c/17fu1jxtj9a8"]],'蚂蚁金融')
    #table_static(html_response_soup('https://www.xiaohongshu.com/crown/community/third_checklist'))

