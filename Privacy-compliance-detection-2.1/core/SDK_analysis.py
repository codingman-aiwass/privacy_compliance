from bs4 import BeautifulSoup
import chardet
import os
import re
import json
import time
import math
import bs4.element
from selenium_driver import driver
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
            for cell in cells:
                if 'rowspan' in cell.attrs:
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
        if td.get('colspan'):
            #print("该行进行了列合并"+td.get_text())
            return True
    return False
def table_headers_find(row,i,count_column):
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
            else:
                if i+1 == len(count_column):
                    return []
                else:
                    try:
                        if count_column[i]>count_column[i-1] and count_column[i] == count_column[i+1]:#如果该行和前面行不一样列数，同时又和后面列数相同，则该行为表头
                            for td in tds:
                                th_td_list.append(td.get_text())
                            return th_td_list
                        elif count_column[i]<count_column[i-1] and count_column[i] == count_column[i+1]:
                            for td in tds:
                                th_td_list.append(td.get_text())
                            return th_td_list
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
def table_handle_no_rowspan(table):
    table_dict_list = []
    rows = table.find_all('tr')
    count_column, aver = count_row_column(rows)
    for i in range(0, len(rows)):
        sdk_dict = {}
        th_list = table_headers_find(rows[i], i, count_column)
        if th_list and 'colspan' not in th_list:
            for th in th_list:
                sdk_dict[th] = None
            sdk_dict['url-list'] = None
            if len(sdk_dict) > 1:  # 防止合并列的情况
                table_dict_list.append(sdk_dict)
            else:
                print("表头只有一个值")
        else:
            if len(table_dict_list) > 0:
                td_list, url_list = table_td_extract(rows[i])
                # 找到最近的表头
                nearly_th_dict = find_th_dict(table_dict_list, aver)
                if len(nearly_th_dict) == 0:
                    nearly_th_dict = table_dict_list[0]
                sdk_dict_temp = td_dict_write(td_list, nearly_th_dict, i, count_column)
                if url_list:
                    sdk_dict_temp['url-list'] = url_list
                if sdk_dict_temp:
                    table_dict_list.append(sdk_dict_temp)
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
            if rowspan_judge(table):
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
    if check_elements(text,key_word,0,3):
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
def sdk_link_judge(links):
    '''
    :param links: 标记为超链接的节点列表
    :return: 判定为sdk描述链接的列表
    '''
    url_dict = {'description':None,'url':None,'soup':None,'table-result':None,'display-result':None}
    sdk_word_url_dict_list = []
    for link in links:
        if is_valid_url(link.get('href')):
            title = link.get_text()
            # 通过链接的名字判断是不是，如果能判断，则
            if sdk_title_judge(title):
                url_dict['description'] = title
                url_dict['url'] = link.get('href')
                temp = dict(url_dict)
                sdk_word_url_dict_list.append(temp)
            else:
                parent_tag = link.parent
                # 通过父节点中对链接的描述判断
                if len(parent_tag.get_text())<45:
                    if sdk_title_judge(parent_tag.get_text()):
                        url_dict['description'] = parent_tag.get_text()
                        url_dict['url'] = link.get('href')
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
            try:
                soup = driver.get_privacypolicy_html(url)
                temp = soup.get_text()
                if check_elements(temp,key_word):
                    url_dict['url'] = url
                    url_dict['soup'] = soup
                    sdk_url_soup_dict_list.append(url_dict)
            except Exception as e:
                print(e)
    return sdk_url_soup_dict_list
def display_handle(soup):
    display_dict_list = []
    display_bs_point = positioning_display_div(soup)
    display_list = display_text_extract(display_bs_point)
    if display_list:
        display_dict_list = display_list_change_dictlist(display_list)
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
def run_sdk_link_judge(soup):
    '''
    :param soup: 隐私政策soup文件
    :return: 判定为sdk子链接的soup文件列表
    '''
    links = soup.find_all('a')
    sdk_dict_list = sdk_link_judge(links)
    try:
        if sdk_dict_list:#从原页面链接描述判定
            for d in sdk_dict_list:
                sdk_soup = driver.get_privacypolicy_html(d['url'])
                if sdk_soup:
                    d['soup'] = soup
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
    final_result = {'table-result-len':None,'table-url':[],'table-result':[],'display-result-len':None,'display-url':[],'display-result':[],'false-url':[]}
    if soup == None:
        soup = driver.get_privacypolicy_html(url)
    if soup:#判断有无sdk子链接
        sdk_dict_list = run_sdk_link_judge(soup)
        sdk_dict_list = remove_duplicates(sdk_dict_list)
        if sdk_dict_list:
            for sdk_dict in sdk_dict_list:
                #table处理
                try:
                    print(sdk_dict['url'])
                    table_dict_list = run_table_handle(url = sdk_dict['url'])#解析子链接soup文件：表格解析
                    if table_dict_list:
                        try:
                            final_result['table-url'].append([sdk_dict['description'],sdk_dict['url']])
                        except:
                            final_result['table-url'].append([sdk_dict['url']])
                        final_result['table-result'].extend(table_dict_list)
                    else:# 不是，则判断是否为陈列形式
                        display_dict_list = run_display_handle(url = sdk_dict['url'])
                        if display_dict_list:
                            try:
                                final_result['display-url'].append([sdk_dict['description'], sdk_dict['url']])
                            except:
                                final_result['display-url'].append([sdk_dict['url']])
                            final_result['display-result'].append(display_dict_list)
                        else:
                            try:
                                final_result['false-url'].append([sdk_dict['description'], sdk_dict['url']])
                            except:
                                final_result['false-url'].append([sdk_dict['url']])
                except Exception as e:
                    print(e)
                    #是，则解析陈列形式
                #不是，则导入llm
        #无，则查看原页面中的形式，是列表/陈述形式/llm
        else:
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
    start_time = time.time()
    random_50()
    end_time = time.time()
    total_time = end_time - start_time
    print("程序运行时间：", total_time, "秒")