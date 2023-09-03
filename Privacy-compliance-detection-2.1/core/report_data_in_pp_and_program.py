import json
import os

def edit_distance_similarity(str1, str2):
    m = len(str1)
    n = len(str2)
    dp = [[0 for j in range(n + 1)] for i in range(m + 1)]
    for i in range(m + 1):
        for j in range(n + 1):
            if i == 0:
                dp[i][j] = j
            elif j == 0:
                dp[i][j] = i
            elif str1[i - 1] == str2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i][j - 1], dp[i - 1][j], dp[i - 1][j - 1])
    return (1 - (dp[m][n] / max(m,n)))


apks = [item[:-5] for item in os.listdir('./PrivacyPolicySaveDir/') if item.endswith('.json')]
print(apks)

for apk in apks:
    pp_miss_data_item_cnt = 0
    pp_miss_data_items = set()

    program_miss_data_item_cnt = 0
    program_miss_data_items = set()

    pp_total = 0
    program_total = 0
    try:
        with open('./ResultSaveDir/' + apk + '_method_scope.json','r') as f:
            program_report_items = json.load(f)
        with open('./PrivacyPolicySaveDir/' + apk + '.json','r') as f:
            privacy_policy_items = json.load(f)
    except FileNotFoundError :
        print('{} log not exsit in folders'.format(apk))
        print('------------------------------')
        continue
    
    print('process {} now...'.format(apk))

    data_en_set = set()
    data_en_set.update(set([s.lower() for s in privacy_policy_items[0].get('data-en-total') if s is not None]))
    # print('data-en-set:',data_en_set)
    # 将data-en-chatgpt-total去重并加入data_en_chatgpt_set集合
    data_en_chatgpt_set = set()
    for single_chatgpt_list in privacy_policy_items[0].get('data-en-chatgpt-total'):
        inner_tuple = tuple([s.lower() for s in single_chatgpt_list if s is not None])
        data_en_chatgpt_set.add(inner_tuple)
    # print('data-en-chatgpt-set',data_en_chatgpt_set)
    pp_total = len(data_en_set)
    
    program_data_points_set = set()
    
    pp_missing_items = []
    program_missing_items = []

    # 遍历所有的program_report_items,看看哪些数据项是只在program_report_items里而不在隐私政策里的
    for d in program_report_items:
        privacy_data_items =  d['privacy_data_items'].strip("[]").split(", ")
        third_party_data_items = d["3rd_privacy_data_items"].strip("[]").split(", ")
        
        program_data_points_set.update(privacy_data_items)
        program_data_points_set.update(third_party_data_items)


        # program_total += (len(privacy_data_items) + len(third_party_data_items))
        missing_privacy_data_items = []
        missing_3rd_party_data_items = []
        # 在将privacy_policy_items里的 data-en-total 和
        # program_report_items 里的privacy_data_items 以及 third_party_data_items里的数据项作对比,
        # 如果privacy_data_items 和 third_party_data_items 里的数据项不在data-en-list里,
        # 输出clazz,method,privacy_items,method_contain_privacy_item
        for string in privacy_data_items:
            # 遍历静态分析找到的所有第一方隐私数据项,判断是否在chatgpt_list中
            flag = True
            # 此处修改逻辑为判断data-en-chatgpt-list里的每个tuple里是否有元素满足条件
            for chatgpt_list in data_en_chatgpt_set:
            # for str_in_data_en_set in data_en_set:
                for str_in_chatgpt_list in chatgpt_list:
                    if len(str_in_chatgpt_list) > 0 and len(string) > 0 and \
                        edit_distance_similarity(string,str_in_chatgpt_list) >= 0.75:
                        flag = False
                        break
                # if len(str_in_data_en_set) > 0 and len(string) > 0 and \
                #     edit_distance_similarity(string,str_in_data_en_set) >= 0.75:
                #     flag = False
                #     break
            if flag:
                if len(string) > 1:
                    pp_miss_data_item_cnt += 1
                    pp_miss_data_items.add(string)
                    missing_privacy_data_items.append(string)
        for string in third_party_data_items:
            # 遍历静态分析找到的所有第三方隐私数据项,判断是否在chatgpt_list中
            flag = True
            # 此处修改逻辑为判断data-en-chatgpt-list里的每个tuple里是否有元素满足条件
            # for str_in_data_en_set in data_en_set:
            for chatgpt_list in data_en_chatgpt_set:
                for str_in_chatgpt_list in chatgpt_list:
                    if len(str_in_chatgpt_list) > 0 and len(string) > 0 and \
                        edit_distance_similarity(string,str_in_chatgpt_list) >= 0.75:
                        flag = False
                        break
                # if len(str_in_data_en_set) > 0 and len(string) > 0 and \
                #     edit_distance_similarity(string,str_in_data_en_set) >= 0.75:
                #     # 说明这个 程序找到的第三方数据项 在隐私政策里
                #     flag = False
                #     break
            if flag:
                if len(string) > 1:
                    pp_miss_data_item_cnt += 1
                    pp_miss_data_items.add(string)
                    missing_3rd_party_data_items.append(string)
        
        if len(missing_privacy_data_items) > 0 or len(missing_3rd_party_data_items) > 0:
            tmp = {}
            tmp['clazz'] = d['clazz']
            tmp['method'] = d['method']
            tmp['privacy_data_items'] = []
            tmp['3rd_party_privacy_data_items'] = []
            tmp['method_contain_privacy_item'] = d['stmt_method_contain_privacy_item'].strip("[]").split(", ")
            tmp['3rd_method_contain_privacy_item'] = d['3rd_stmt_method_contain_privacy_item'].strip("[]").split(", ")

            tmp['privacy_data_items'].extend(missing_privacy_data_items)
            tmp['3rd_party_privacy_data_items'].extend(missing_3rd_party_data_items)
            pp_missing_items.append(tmp)

    program_total = len(program_data_points_set)
    # 遍历所有的隐私政策数据项,查看哪些数据项是只在隐私政策里,程序中没有的
    for item in privacy_policy_items[1]:
        tmp = {}
        tmp['pp_data_item'] = []
        tmp['pp_data_purpose'] = []
        tmp['pp_sentence'] = ''
        tmp['pp_collector'] = []
        data_en_list = [s.lower() for s in item.get('data-en-list') if s is not None]
        chatgpt_list = item.get('data-en-chatgpt-list')
        results = item.get('result_sentence')
        if len(data_en_list) != len(chatgpt_list):
            # 说明有的data_en_list中的部分隐私数据项没有对应的chatgpt生成的同义词列表
            # print('此data_en_list中的部分隐私数据项没有对应的chatgpt生成的同义词列表')
            # print('data-en-list:',data_en_list)
            # print('data-en-chatgpt-list',data_en_chatgpt_set)
            # print('continue...')
            # print('-------------------------------------------')
            continue
        # 目前逻辑,从JSON中获取result_sentence以及其中包含的data-en,再判断这些个data-en是否在程序中
        # 修改后的逻辑:从原本的data-en所对应的data-en-chatgpt-list里的三个短语中判断是否有任意一个出现在程序中

        # 此处遍历result_sentence里的每个字典,并判断这每个字典里的data-en是否存在,存在则判断是否在程序中
        for result in results:
            # result_data_en_chatgpt_list存放result_data_en对应的同义词列表
            result_data_en_chatgpt_list = None
            flag = True
            index = 0
            if result.get('data-en') is not None:
                result_data_en = result.get('data-en').lower()
                result_data_en_chatgpt_list = [s.lower() for s in chatgpt_list[index] if s is not None]
                # 说明该data-en有对应的data-en-chatgpt-list,判断这个chatgpt-list中是否有项目存在程序中
                for str_in_program_data_points_set in program_data_points_set:
                    # 遍历chatgpt-list,判断是否有项目存在程序中
                    for result_data_en_in_chatgpt_item in result_data_en_chatgpt_list:
                        if len(str_in_program_data_points_set) > 0 and len(result_data_en_in_chatgpt_item) > 0 and \
                            edit_distance_similarity(result_data_en_in_chatgpt_item,str_in_program_data_points_set) >= 0.75:
                            flag = False
                            break
                if flag:
                    if len(result.get('data-en')) > 1:
                        # program_miss_data_item_cnt += 1
                        tmp['pp_sentence'] = item.get('orig-sentence')
                        tmp['pp_data_item'].append(result_data_en)
                        tmp['pp_data_purpose'].append('\n'.join(result.get('purpose-en')))
                        tmp['pp_collector'].append('\n'.join(result.get('subject')))

                index+=1
            else:
                # 说明该JSON里的一个字典里的data-en为空,跳过不判断.
                continue
            # for str_in_program_data_points_set in program_data_points_set:
            #     if len(str_in_program_data_points_set) > 0 and len(result_data_en) > 0 and \
            #         edit_distance_similarity(result_data_en,str_in_program_data_points_set) >= 0.75:
            #         flag = False
            #         break
            # if flag:
            #     if len(result.get('data-en')) > 1:
            #         # program_miss_data_item_cnt += 1
            #         tmp['pp_sentence'] = item.get('orig-sentence')
            #         tmp['pp_data_item'].append(result.get('data-en'))
            #         tmp['pp_data_purpose'].append('\n'.join(result.get('purpose-en')))
            #         tmp['pp_collector'].append('\n'.join(result.get('subject')))
        
        
        if len(tmp['pp_data_item']) > 0:
            program_missing_items.append(tmp)
            program_miss_data_items.update(tmp['pp_data_item'])
    # print('res:')
    # print(pp_missing_items)
    # print(program_missing_items)
    with open('./final_res/pp_missing/' + apk + '_pp_missing_items.json','w') as f:
        statistic_res = {'total_pp_data_items_cnt':pp_total,'total_program_data_items_cnt':program_total,
                         'in_program_but_not_in_pp':len(pp_miss_data_items)}
        # detailed_report = {'in_program_but_not_in_pp_detailed':list(pp_miss_data_items)}
        # print('in_program_but_not_in_pp:',pp_miss_data_items)
        # print('----------------------------')
        tmp = []
        tmp.append(statistic_res)
        # tmp.append(detailed_report)
        tmp.extend(pp_missing_items)
        pp_missing_items = tmp
        tmp1_json = json.dumps(pp_missing_items,indent=4)
        f.write(tmp1_json)
    
    # with open('./final_res/program_missing/' + apk + '_program_missing_items.json','w') as f:
    #     statistic_res = {'total_pp_data_items_cnt':pp_total,'total_program_data_items_cnt':program_total,
    #                      'in_pp_but_not_in_program':len(program_miss_data_items)}
    #     # detailed_report = {'in_pp_but_not_in_program_detail':list(program_miss_data_items)}
    #     # print('in_pp_but_not_in_program:',program_miss_data_items)
    #     # print('----------------------------')
    #     tmp = []
    #     tmp.append(statistic_res)
    #     # tmp.append(detailed_report)
    #     tmp.extend(program_missing_items)
    #     program_missing_items = tmp
    #     tmp1_json = json.dumps(program_missing_items,ensure_ascii=False,indent=4)
    #     f.write(tmp1_json)