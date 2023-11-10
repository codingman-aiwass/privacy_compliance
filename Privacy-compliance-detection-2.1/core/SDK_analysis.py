from bs4 import BeautifulSoup
import chardet
import os
import re
import json
import time
import math
import bs4.element
from selenium_driver import driver
from urllib.parse import urlparse
from urllib.parse import urljoin
table_false = 0
def text_format(text):
    text = text.replace(" ", '')
    text = text.replace("﻿", '')
    text = text.replace("\n", '')
    text = text.replace("\t", '')
    text = text.replace(" ", '')
    text = text.replace("•",'')
    return text
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
def check_elements(_str,str_list,max = None,min = None):
    '''
    :param str_list: 字符串列表
    :param _str: string
    :param max: 界限值
    :return: 若列表中超过max个元素在字符串中，则返回true
    '''
    if max ==None:
        max = 1
    if min == None:
        min = 100
    count = 0
    for item in str_list:
        if item in _str:
            count += 1
    if count > max:
        if count < min:
            return True
        else:
            return False
    else:
        return False
def get_html_soup(html_filename):
    '''
    :param html_filename:.html文件的路径
    :return:返回该html文件的soup对象
    '''
    with open(html_filename,'rb')as f:
        html = chardet.detect(f.read())
    f.close()
    with open(html_filename,'r',encoding=html['encoding'])as f:
        result = f.read()
    f.close()
    #print(html['encoding'])
    soup = BeautifulSoup(result,'html.parser')
    return soup
def rowspan_judge(table):
    if table:
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all(['td', 'th'])
            for cell in cells:#如果该值大于1，则表明发生行合并
                if 'rowspan' in cell.attrs:
                    try:
                        if int(cell.attrs['rowspan'])<2:
                            return False
                        else:
                            return True
                    except:
                        return True
    return False
def count_row_column(rows):
    '''
    计算一个表格中每一行的列数
    :param rows: 表格所有行
    :return:每行列数列表
    '''
    count_column = []
    for row in rows:
        tds = row.find_all('td')
        if tds:
            count_column.append(len(tds))
        else:
            ths = row.find_all('th')
            if ths:
                count_column.append(len(ths))
    if len(count_column)<=1:
        return count_column,0
    temp_c = count_column[:]
    min_value = min(temp_c)
    temp_c.remove(min_value)
    aver = math.floor(sum(temp_c)/len(temp_c))
    if aver == 1:
        return count_column, aver
    return count_column,aver-1
def colspan_judge(tds):
    '''
    :param row: 表格的一行中所有列元素列表
    :return: 如果该行进行了列合并，则返回true
    '''
    for td in tds:
        if 'colspan'in td.attrs:#如果该值大于1则表明发生了列合并
            #print("该行进行了列合并"+td.get_text())
            try:
                if int(td.attrs['colspan'])<2:
                    return False
                else:
                    return True
            except:
                return True
    return False
def table_headers_find(row,i,count_column,false_colspan = None):
    '''

    :param row: 表格的一行
    :param i: 表格第i行
    :param count_column: 表格每行的列数统计列表
    :return: 表头列表
    '''
    th_list = []
    th_td_list = []
    ths = row.find_all('th')
    if ths:
        for th in ths:
            th_list.append(text_format(th.get_text()))
        return th_list
    else:#无th的情况,
        tds = row.find_all('td')
        #判断该行是否是列合并，如果是列合并则要求下一行
        if tds:
            if i == 0:
                if count_column[i]<count_column[i+1] and colspan_judge(tds):#第一行情况
                    return ['colspan']
                else:#第一行为表头，非列合并
                    for td in tds:
                        th_td_list.append(text_format(td.get_text()))
                    if th_td_list and len(list(set(th_td_list))) == len(th_td_list):#防止明明是列合并，但colspan判断失效
                        return th_td_list
                    else:
                        return['false_colspan']
            else:
                if i+1 == len(count_column):
                    return []
                else:
                    try:
                        if count_column[i]>count_column[i-1] and count_column[i] == count_column[i+1]:#如果该行和前面行不一样列数，同时又和后面列数相同，则该行为表头
                            for td in tds:
                                th_td_list.append(text_format(td.get_text()))
                            if th_td_list and len(list(set(th_td_list))) == len(th_td_list):  # 防止明明是列合并，但colspan判断失效
                                return th_td_list
                            else:
                                return ['false_colspan']
                        elif count_column[i]<count_column[i-1] and count_column[i] == count_column[i+1]:
                            for td in tds:
                                th_td_list.append(text_format(td.get_text()))
                            if th_td_list and len(list(set(th_td_list))) == len(th_td_list):  # 防止明明是列合并，但colspan判断失效
                                return th_td_list
                            else:
                                return ['false_colspan']
                        elif false_colspan:#前一行判断为colspan，但列数一样的行
                            for td in tds:
                                th_td_list.append(text_format(td.get_text()))
                            if th_td_list and len(list(set(th_td_list))) == len(th_td_list):  # 防止明明是列合并，但colspan判断失效
                                temp_new_list_20 = [s for s in th_td_list if len(s)>20]
                                if temp_new_list_20:
                                    return []
                                temp_new_list_38 = [s for s in th_td_list if 3<len(s)<8]
                                if len(temp_new_list_38)>len(th_td_list)/2-1:
                                    return th_td_list
                            else:
                                return ['false_colspan']
                    except:
                        print("")
    return []
def find_th_dict(table_dict_list,n = None):
    '''
    :param table_dict_list:  表格分析字典列表
    :param n: 找到含有 n 个 None 值的字典
    :return: 它会从列表的最后一个字典开始往前遍历，直到找到含有 n 个 None 值的字典，然后返回该字典。如果找不到满足条件的字典，则返回 []。
    '''
    for i in range(len(table_dict_list)-1, -1, -1):
        if list(table_dict_list[i].values()).count(None) >= n:
            return table_dict_list[i]
    return []
def table_td_extract(row):
    td_list = []
    tds = row.find_all('td')
    if tds:
        for td in tds:
            td_list.append(text_format(td.get_text()))
    url_list = []
    a_tag = row.find_all('a')
    for a in a_tag:
        url_list.append([a.get_text(),a.get('href')])
    return td_list,url_list
def td_dict_write(td_list,th_dict,i,count_column):
    try:
        if count_column[i] == count_column[i-1]:
            temp_dict = dict(th_dict)
            if len(td_list)+1 == len(th_dict):
                a= 0
                for key in temp_dict:
                    if key != 'url-list':
                        temp_dict[key] = td_list[a]
                        a += 1
                sdk_dict_td = dict(temp_dict)
                return sdk_dict_td
            else:
                return {}
    except:
        return False
    return {}
def table_headers_thead(thead):
    th_list = []
    tds = thead.find_all('td')
    if tds:
        for td in tds:
            th_list.append(td.get_text())
    return th_list
def table_handle_no_rowspan(table):
    table_dict_list = []
    rows = table.find_all('tr')
    count_column, aver = count_row_column(rows)
    thead_flag = 0
    th_list = []
    for i in range(0, len(rows)):
        sdk_dict = {}
        if thead_flag == 0:
            thead = table.find('thead')
            if thead:
                th_list = table_headers_thead(thead)
                thead_flag = 1
            else:
                thead_flag = -1
        if thead_flag == -1 or thead_flag == 1:
            if 'false_colspan' in th_list:
                # 表示发生了列合并，则该行不写，并且下一行作为新表头？这里有个问题是，我记得有的是中间断开了，但是并没有产生新的表
                th_list = table_headers_find(rows[i], i, count_column,false_colspan=True)# 该行为合并列行
            else:
                th_list = table_headers_find(rows[i], i, count_column)
        if th_list and 'colspan' not in th_list and 'false_colspan' not in th_list and len(th_list)>1:
            for th in th_list:
                sdk_dict[th] = None
            sdk_dict['url-list'] = None
            if len(sdk_dict) > 1:  # 防止合并列的情况
                table_dict_list.append(dict(sdk_dict))
            else:
                print("表头只有一个值")
        else:
            if len(table_dict_list) > 0:
                td_list, url_list = table_td_extract(rows[i])
                # 增加新的行的数据的判断，防止出现列合并，但colspan判断失败的现象
                if td_list and len(list(set(td_list)))<len(td_list):
                    th_list = ['false_colspan'] #发生了列合并
                    continue
                # 找到最近的表头
                nearly_th_dict = find_th_dict(table_dict_list, aver)
                if len(nearly_th_dict) == 0:
                    nearly_th_dict = table_dict_list[0]
                sdk_dict_temp = td_dict_write(td_list, nearly_th_dict, i, count_column)
                if url_list:
                    sdk_dict_temp['url-list'] = url_list
                if sdk_dict_temp:
                    table_dict_list.append(dict(sdk_dict_temp))
                #else:
                 #   print("写入行数据失败")
    return table_dict_list
def table_handle_rowspan(table):
    table_dict_list_row = []
    return table_dict_list_row
def tables_handle(soup):
    '''
    :param soup: 待处理页面
    :return: 字典列表
    '''
    all_table_dict_list = []
    rowspan_count = 0
    tables = soup.find_all('table')
    if tables:
        for table in tables:
            if rowspan_judge(table):#判断是否有行合并
                rowspan_count +=1
                temp_ro = table_handle_rowspan(table)[:]
                all_table_dict_list.extend(temp_ro)
            else:
                temp_n_ro = table_handle_no_rowspan(table)[:]
                all_table_dict_list.extend(temp_n_ro)
    return all_table_dict_list,rowspan_count
def find_a_tag(child):
    if isinstance(child,bs4.element.Tag):
        link_list =[]
        a_tags = child.find_all('a')
        for a in a_tags:
            try:
                temp_url = a['href']
                if is_valid_url(temp_url):
                    link_list.append(a['href'])
                elif is_valid_url(a.get_text()):
                    link_list.append(a.get_text())
            except:
                continue
        return link_list
    return False
def display_text_extract2(display_bs_point):
    display_list = []
    all_display_list = []
    for child in display_bs_point:
        temp_a_link = find_a_tag(child)
        if temp_a_link:
            try:
                for i in child:
                    temp_text = text_format(i.get_text())
                    if temp_text:
                        display_list.append(temp_text)
                display_list.append({'url': temp_a_link})
                all_display_list.append(display_list)
                display_list = []
            except:
                display_list.append(child.get_text())
                display_list.append({'url': temp_a_link})
                all_display_list.append(display_list)
                display_list = []
    return all_display_list
def point_text(child):
    result = []
    sdk_url_list = find_a_tag(child)
    if sdk_url_list:
        result.append({'url': sdk_url_list})
    if child.name == 'ul':
        for li in child:
            result.append(text_format(li.get_text()))
        return result
    return []
def display_text_extract(display_bs_point):
    '''
    :param display_bs_point: 包含所有display的父节点
    :return:
    '''
    display_list = []
    all_display_list = []
    flag = 0
    flag2 = 0
    if display_bs_point:
        for child in display_bs_point:
            temp_text = text_format(child.get_text())
            if temp_text and flag:
                temp_list = point_text(child)
                if temp_list:
                    display_list.extend(temp_list)
                    all_display_list.append(display_list[:])
                    display_list = []
                else:
                    sdk_url_list = find_a_tag(child)
                    if sdk_url_list:
                        display_list.append({'url':sdk_url_list})
                    display_list.append(temp_text)
            elif temp_text == '':
                if child.name:
                    flag = 1#找到第一个空位
                    if display_list:
                        all_display_list.append(display_list[:])
                        display_list = []
            elif len(display_list) > 30:
                flag2 = 1
    #if flag2 and display_bs_point:
     #   print("切割存在问题！")
    if len(all_display_list) ==0:
        all_display_list = display_text_extract2(display_bs_point)
    return all_display_list
def find_parent_with_most_children(soup):
    max_child_count = 0
    parent_with_most_children = None

    def traverse(node):
        nonlocal max_child_count, parent_with_most_children
        if len(node.contents) > max_child_count:
            max_child_count = len(node.contents)
            parent_with_most_children = node
        for child in node.contents:
            if child.name is not None:
                traverse(child)
    traverse(soup)
    return parent_with_most_children
def positioning_display_div(soup):
    '''
    :param soup: sdk页面soup
    :return: 返回包含display声明的bs节点
    '''
    display_bs_point = find_parent_with_most_children(soup)
    if display_bs_point:
        return display_bs_point
    return False
def sdk_title_judge(text):
    '''
    :param text: 待判定为描述sdk的短文本
    :return: 如果是描述sdk则返回True，否则返回False
    '''
    key_word = ["第三方","sdk","共享","合作","运营","关联"]
    #小写处理
    text = text.lower()
    if check_elements(text,key_word,0,6):
        return True
    return False
def rule_cut(s):
    delimiters = ["：",":"]
    result = {}
    for delimiter in delimiters:
        if delimiter in s:
            split_list = s.split(delimiter)
            if len(split_list)==2:
                result[split_list[0]] = split_list[1]
            elif len(split_list)>2:
                result[split_list[0]] = "".join(split_list[1:])
            break
    if result =={}:
        result['text'] = s
    return result
def has_url_dict(lst,string = None):
    '''
    :param lst: 列表
    :param string: 字典键
    :return: 如果列表中包含string为键的字典，返回该字典元素
    '''
    if string == None:
        string = 'url'
    for item in lst:
        if isinstance(item, dict) and string in item:
            return item
    return False
def display_list_change_dictlist(display_list):
    '''
    :param display_list: 保存陈述的二维列表
    :return:
    '''
    display_dict_list = []
    display_dict = {}
    judge_sentence = ['我们','。',',','我','，']
    for display in display_list:
        judge_count = 0
        for i in range(0,len(display)):#这里假定已经切割好了
            if check_elements(display[i],judge_sentence,3):#判断是否为正式句子而非陈列形式。
                judge_count +=1
            if judge_count>len(display)//2-1:
                display_dict = {}
                break
            else:
                if i ==0:
                    display_dict['name'] = display[i]
                elif isinstance(display[i],dict):
                    continue
                else:#按照规则切割，没有对应规则的键为’text'：
                    temp_dict = rule_cut(display[i])
                    if isinstance(temp_dict,dict) and temp_dict:
                        display_dict.update(dict(temp_dict))
        temp_item = has_url_dict(display)
        if temp_item:
            display_dict['url'] = temp_item['url'][:]
        if display_dict:
            display_dict_list.append(dict(display_dict))
            display_dict = {}
    return display_dict_list
def remove_duplicates(lst):
    '''
    :param lst: 字典列表
    :return: 去掉重复键'url'的字典
    '''
    unique_lst = []
    urls = set()
    for d in lst:
        if d.get('url') not in urls:
            urls.add(d.get('url'))
            unique_lst.append(d)
    return unique_lst
def relative_url_judge(base_url,relative_url):
    try:
        parsed_href = urlparse(relative_url)
        if not parsed_href.scheme:
            absolute_url = urljoin(base_url, relative_url)
        #print("相对路径")
            return absolute_url
        else:
            return relative_url
        #print("绝对路径")
    except:
        return relative_url

def sdk_link_judge(url,links):
    '''
    :param links: 标记为超链接的节点列表
    :return: 判定为sdk描述链接的列表
    '''
    url_dict = {'description':None,'url':None,'soup':None,'table-result':None,'display-result':None}
    sdk_word_url_dict_list = []
    for link in links:
        son_url = None
        if url!=None:
            son_url = relative_url_judge(url,link.get('href'))
        if son_url ==None:
            son_url = link.get('href')
        if is_valid_url(son_url):
            title = link.get_text()
            # 通过链接的名字判断是不是，如果能判断，则
            if sdk_title_judge(title):
                url_dict['description'] = title
                url_dict['url'] = son_url
                temp = dict(url_dict)
                sdk_word_url_dict_list.append(temp)
            else:
                parent_tag = link.parent
                # 通过父节点中对链接的描述判断
                temp_p =parent_tag.get_text()
                if len(parent_tag.get_text())<45:
                    if sdk_title_judge(parent_tag.get_text()):
                        url_dict['description'] = parent_tag.get_text()
                        url_dict['url'] = son_url
                        temp = dict(url_dict)
                        sdk_word_url_dict_list.append(temp)
                    else:
                        grand_parent = parent_tag.parent
                        temp_p2 = grand_parent.get_text()
                        if len(grand_parent.get_text())<45:
                            if sdk_title_judge(grand_parent.get_text()):
                                url_dict['description'] = grand_parent.get_text()
                                url_dict['url'] = son_url
                                temp = dict(url_dict)
                                sdk_word_url_dict_list.append(temp)
    sdk_word_url_dict_list = remove_duplicates(sdk_word_url_dict_list)
    #如果description与url相等，那么如果列表长度大于2，则删除该元素
    for d in sdk_word_url_dict_list:
        try:
            if d['description'] == d['url'] and len(sdk_word_url_dict_list)>1:
                sdk_word_url_dict_list.remove(d)
        except Exception as e:
            print(e)
    return sdk_word_url_dict_list
def sdk_soup_judge(links):
    '''
    :param links: 标记为超链接的节点列表
    :return: 判定为sdk描述页面soup的列表
    '''
    url_dict = {'description': None, 'url': None,'soup':None,'table-result':None,'display-result':None}
    url_list = []
    sdk_url_soup_dict_list = []
    key_word = ["第三方","sdk","共享","合作","运营","关联"]
    for link in links:
        if is_valid_url(link.get('href')):
            url_list.append(link.get('href'))
    if url_list:
        for url in url_list:
            if url == 'https://terms.alicdn.com/legal-agreement/terms/suit_bu1_other/suit_bu1_other202112201639_51546.html':
                print(url)
            try:
                soup = driver.get_privacypolicy_html(url)
                temp = soup.get_text()
                if check_elements(temp,key_word):
                    if "权限列表" in temp and "安卓" in temp:
                        continue
                    #增加一个不是隐私政策页面，也不是权限列表页面
                    if temp.count("儿童")>3:
                        continue
                    else:
                        url_dict['url'] = url
                        url_dict['soup'] = soup
                        sdk_url_soup_dict_list.append(dict(url_dict))
            except Exception as e:
                print(e)
    return sdk_url_soup_dict_list
def futher_display_dict_handle(display_dict_list):
    count_d = []
    for dis_dict in display_dict_list:
        count_d.append(len(dis_dict.items()))
    average = sum(count_d)/len(count_d)
    if average == display_dict_list[0]:
        return display_dict_list
    for i in range(0,len(count_d)):
        if count_d[i]>=average:
            temp_dict = dict(display_dict_list[i])
            temp_key_list = list(temp_dict.keys())
            break
    for i in range(0,len(count_d)):
        if count_d[i]<average:
            longest_key = None
            longest_len = 0
            for key,value in display_dict_list[i].items():
                if isinstance(value,str) and len(value) >longest_len:
                    longest_key =key
                    longest_len = len(value)
            temp_str = display_dict_list[i].copy()[longest_key]
            key_list = list(dict(display_dict_list[i]).keys())
            if 'text' not in key_list:
                key_list.append('text')
            temp_key_list = [x for x in temp_key_list if x not in key_list]
            result_split =[]
            #result_split = [temp_str.split(k)[0]+k+temp_str.split(k)[1] for k in temp_key_list]
            for k in temp_key_list:
                flag = temp_str.split(k)
                if len(flag)>1:
                    result_split.append(flag[0])
                    result_split.append(k)
                    temp_str=flag[1]
                if k== temp_key_list[-1]:
                    result_split.append(temp_str)
            for a in range(0,len(result_split)):
                if a==0:
                    display_dict_list[i][longest_key] = result_split[a]
                else:
                    if result_split[a] in temp_key_list:
                        try:
                            display_dict_list[i][result_split[a]] = result_split[a+1]
                        except:
                            pass
    return display_dict_list
def display_handle(soup):
    display_dict_list = []
    display_bs_point = positioning_display_div(soup)
    display_list = display_text_extract(display_bs_point)
    if display_list:
        display_dict_list = display_list_change_dictlist(display_list)
        #对形成的结果进一步处理
        display_dict_list = futher_display_dict_handle(display_dict_list)
    return display_dict_list
def run_table_handle(url=None,soup = None):
    '''
    :param url: sdk声明链接
    :param soup: sdk声明页面soup
    :return: 返回该页面表格提取字典列表
    '''
    table_dict_list_result = []
    if soup == None:
        soup = driver.get_privacypolicy_html(url)
    if soup:
        table_dict_list_result,rowspan_count = tables_handle(soup)
    #for i in table_dict_list_result:
     #   print(i)
    #if rowspan_count>0:
     #   print("行合并表格数："+str(rowspan_count))
    return table_dict_list_result
def run_display_handle(url=None,soup = None):
    display_dict_list_result = []
    if soup == None:
        soup = driver.get_privacypolicy_html(url)
    if soup:
        display_dict_list_result = display_handle(soup)
    #for i in display_dict_list_result:
     #   print(i)
    return display_dict_list_result
def run_sdk_link_judge(url=None,soup = None):
    '''
    :param soup: 隐私政策soup文件
    :return: 判定为sdk子链接的soup文件列表
    '''
    if soup ==None:
        soup = driver.get_privacypolicy_html(url)
    if soup:
        links = soup.find_all('a')
        sdk_dict_list = sdk_link_judge(url,links)
        try:
            if sdk_dict_list:#从原页面链接描述判定
                for d in sdk_dict_list:
                    sdk_soup = driver.get_privacypolicy_html(d['url'])
                    if sdk_soup:
                        d['soup'] = sdk_soup
            else:
            #从子页面文本描述判定
                sdk_dict_list.extend(sdk_soup_judge(links))
        except Exception as e:
            print(e)
    return sdk_dict_list
link_result = []
def run_SDK_analysis(url = None,soup = None):
    '''
    :param url: 隐私政策链接
    :param soup: 隐私政策页面soup
    :return: 返回sdk字典形式列表
    '''
    final_result = {'sdk-url-list':[],'table-result-len':None,'table-url':[],'table-result':[],'display-result-len':None,'display-url':[],'display-result':[],'false-url':[]}
    if soup == None:
        soup = driver.get_privacypolicy_html(url)
    if soup:#隐私政策链接
        sdk_dict_list = run_sdk_link_judge(url,soup)
        sdk_dict_list = remove_duplicates(sdk_dict_list)
        if sdk_dict_list:#判断有无sdk子链接
            for sdk_dict in sdk_dict_list:
                try:
                    final_result["sdk-url-list"].append({'description':sdk_dict['description'],'url':sdk_dict['url']})
                except:
                    final_result["sdk-url-list"].append({'description':None, 'url': sdk_dict['url']})
                    # table处理
                try:
                    print(sdk_dict['url'])
                    table_dict_list = run_table_handle(url = url,soup = sdk_dict['soup'])#解析子链接soup文件：表格解析
                    if table_dict_list:
                        try:
                            final_result['table-url'].append({'description':sdk_dict['description'],'url':sdk_dict['url']})
                        except:
                            final_result['table-url'].append({'description':None, 'url': sdk_dict['url']})
                        final_result['table-result'].extend(table_dict_list)
                    else:# 不是，则判断是否为陈列形式
                        display_dict_list = run_display_handle(url = url,soup = sdk_dict['soup'])
                        if display_dict_list:
                            try:
                                final_result['display-url'].append({'description':sdk_dict['description'],'url':sdk_dict['url']})
                            except:
                                final_result['display-url'].append({'description':None, 'url': sdk_dict['url']})
                            final_result['display-result'].extend(display_dict_list)
                        else:
                            try:
                                final_result['false-url'].append({'description':sdk_dict['description'],'url':sdk_dict['url']})
                            except:
                                final_result['false-url'].append({'description':None, 'url': sdk_dict['url']})
                except Exception as e:
                    print(e)
        else:#无sdk子链接
            #llm模块
            print("无sdk子链接！")
    else:
        print("隐私政策sdk分析失败！错误链接")
    final_result['table-result-len'] = len(final_result['table-result'])
    final_result['display-result-len'] = len(final_result['display-result'])
    return final_result
def random_50():
    filepath = "D:\\中山\\隐私合规\\PrivacyLegal"
    filename_list = os.listdir(filepath)
    count = 0
    for i in filename_list:
        try:
            print(i)
            soup = get_html_soup(filepath+"\\"+i)
            if soup:
                result = run_SDK_analysis(soup = soup)
            if result:
                count +=1
                with open("random_50_9_24/"+i[:-5]+".json",'w',encoding='utf-8')as f:
                    json.dump(result,f,ensure_ascii=False,indent=2)
                f.close()
                print("已完成")
            if count==200:
                break
        except Exception as e:
            print(e)
if __name__ == '__main__':
    '''
    start_time = time.time()
    random_50()
    end_time = time.time()
    total_time = end_time - start_time
    print("程序运行时间：", total_time, "秒") '''
    result = run_SDK_analysis(url ='https://terms.alicdn.com/legal-agreement/terms/suit_bu1_alibaba_hema/suit_bu1_alibaba_hema202203300948_54070.html?spm=hemdefault.11124225.6429453315.1')
    #result = run_table_handle(url = "https://html5.moji.com/tpd/agreement/partners_info.html")
    #result = run_display_handle(url ="https://terms.alicdn.com/legal-agreement/terms/suit_bu1_alibaba_hema/suit_bu1_alibaba_hema202009041732_77262.html?spm=a1zaa.8161610.0.0.7e0915758VW7ME")
    with open('temp_sdk_result/com.wudaokou.hippo_sdk.json','w',encoding='utf-8')as f:
        json.dump(result,f,ensure_ascii=False,indent=2)#盒马漏掉了一个sdk链接，陈列形式的。
    f.close()
    #盒马的url判定有问题，然后可以追加一个，如果某个字典的键值对和周围不一样且里面有明显过长字符，则查找上一个字典的键看是否在里面，然后切割成为新的键值。
    '''
    print(futher_display_dict_handle([
        {
            "name": "Android版本：",
            "text": "支付宝",
            "运营方": "支付宝（中国）网络技术有限公司",
            "功能": "帮用户完成付款、提供安全认证服务",
            "收集个人信息类型": "电话状态、位置信息、设备标识符（IMEI、MAC地址、IMSI、BSSID、SSID、Androidid）、摄像头、Wi-Fi列表、写入SDcard数据、蓝牙MAC地址、应用列表",
            "隐私权政策链接": "https://render.alipay.com/p/c/k2cx0tg8",
            "url": [
                "https://render.alipay.com/p/c/k2cx0tg8"
            ]
        },
        {
            "name": "云闪付",
            "运营方": "中国银联股份有限公司功能帮用户完成付款、提供安全认证服务收集个人信息类型电话状态、位置信息、设备标识符（设备型号、设备名称、序列号、设备MAC地址、操作系统类型、IMEI）、AndroidID、AndroidOAID、OpenID、GUID、IMSI隐私权政策链接https://base.95516.com/s/wl//WebAPP/helpAgree/page/agreement/regPrivacy.html",
            "url": [
                "https://base.95516.com/s/wl/WebAPP/helpAgree/page/agreement/regPrivacy.html"
            ]
        }]
    ))
'''