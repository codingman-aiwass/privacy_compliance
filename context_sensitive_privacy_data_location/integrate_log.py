# 寻找佳涛找到中未出现在隐私政策里的数据项
import json
import os
import pickle
import shutil

from dealWithInputAndOutput import get_log_in_properties
from dealWithInputAndOutput import get_run_jar_settings
from dealWithInputAndOutput import get_settings_by_section_and_name
from get_dynamic_res import get_log

# config_settings读取
with open('config_settings.pkl', 'rb') as f:
    config_settings = pickle.load(f)
# dumpjson路径
dynamic_log_path = get_settings_by_section_and_name('dynamic-setting', 'json_log_path')
# 动态/静态分析结果存放路径
_, outputdir, _ = get_run_jar_settings()
# 隐私政策不合规文件存放路径
# pp_compliance_dir = ''
# 我的APK静态分析结果存放路径
apk_static_dir = get_log_in_properties('../Privacy-compliance-detection-2.1/core/RunningConfig.properties',
                                       'resultSavePath')
pp_missing_dir = '../Privacy-compliance-detection-2.1/core/final_res/pp_missing'
# 最终整合的log存放路径
# final_res_log_dir = ''
pp_compliance_dir, final_res_log_dir = get_settings_by_section_and_name('static-setting-and-pp-setting',
                                                                        'pp_compliance_dir',
                                                                        'final_res_log_dir')
# 把output文件夹中以相同包名开头的归为一类,方便遍历整合
prefix_set = set()
prefix_dict = {}
for file_name in os.listdir(outputdir):
    prefix_set.add(file_name[:file_name.index('_')])
for prefix in prefix_set:
    prefix_dict[prefix] = []
for prefix in prefix_set:
    for file_name in os.listdir(outputdir):
        if file_name.startswith(prefix) and file_name.endswith('_output_filtered_labeled.json'):
            prefix_dict[prefix].append(file_name)
# 加一层过滤，不要整合本次运行没有指定的app
with open('../AppUIAutomator2Navigation/apk_pkgName.txt','r',encoding='utf-8') as f:
    contents = set([line.strip('\n').split('|')[0].strip() for line in f.readlines()])
keys = list(prefix_dict.keys())
for app in keys:
    if app not in contents:
        prefix_dict.pop(app,f"{app} does not exists in apk_pkgName.txt...")
# print(prefix_dict)
# 开始遍历字典
for app_name, jsons in prefix_dict.items():
    if len(jsons) == 0:
        continue
    text_label_pairs_1 = None
    text_label_pairs_2 = None
    # 通过这个循环读取了静态/动态的JSON结果
    for json_file in jsons:
        with open(outputdir + '/' + json_file) as f:
            data = json.load(f)
        output_objects = data["outputObjects"]
        if 'static' in json_file:
            # text_label_pairs_1 = [(obj["text"], obj["label"]) for obj in output_objects]
            text_label_pairs_1 = [(obj["text"]) for obj in output_objects]

        elif 'dynamic' in json_file:
            # text_label_pairs_2 = [(obj["text"], obj["label"]) for obj in output_objects]
            text_label_pairs_2 = [(obj["text"]) for obj in output_objects]


    # 读取我之前的pp_missing结果,准备加入最后的汇总文件里
    try:
        with open(pp_missing_dir + '/' + app_name + '_pp_missing_items.json', 'r', encoding='utf-8') as f:
            pp_missing = json.load(f)
            pp_missing_items = pp_missing[1]
    except FileNotFoundError:
        print('find no pp_missing_file: ' + pp_missing_dir + '/' + app_name + '_pp_missing_items.json')
    try:
        # 读取佳颖的隐私政策中冗长的句子，以及另外几个不合规的分析
        with open(pp_compliance_dir + '/' + app_name + '.json', 'r', encoding='utf-8') as f:
            pp = json.load(f)
            data_cn_total = pp[0]['data-cn-total']
            try:
                permission_list = pp[0]['permission_list']
            except KeyError:
                permission_list = 'not found'

            # TODO 此处还需要细分各类情况.比如声明权限信息 SDK信息,等等.需要多设置几个变量接收
            pp_compliance = pp[2]
    except FileNotFoundError:
        # 进入这个except的话，就说明隐私政策解析文件不存在，即pkgName.json文件不存在
        print('find no privacy policy analysis result: ' + pp_compliance_dir + '/' + app_name + '.json')
        data_cn_total = None
        permission_list = None
        pp_compliance = None

    try:
        with open(pp_compliance_dir + '/' + app_name + '_sdk.json', 'r', encoding='utf-8') as f:
            pp_sdk = json.load(f)
    except FileNotFoundError:
        print(
            'find no privacy policy sdk result: ' + pp_compliance_dir + '/' + app_name + '_sdk.json')
        pp_sdk = None

    final_res = []
    pairs_1 = []
    # 检查哪一些text不在隐私政策中
    # 检查佳涛的
    # 检查之前先检测data_cn_total是否为None
    # 为None说明没有拿到隐私政策分析结果，无需进入循环进行检测
    if text_label_pairs_1 is not None and data_cn_total is not None:
        for text in text_label_pairs_1:
            flag = True
        # for text, label in text_label_pairs_1:
            for pp_item in data_cn_total:
                if text in pp_item:
                    # print(text, label)
                    # pairs_1.append((text, label))
                    # pairs_1.append(text)
                    flag = False
                    break
            if flag is True:
                pairs_1.append(text)
    # 检查东鹏的
    pairs_2 = []
    if text_label_pairs_2 is not None and data_cn_total is not None:
        for text in text_label_pairs_2:
            flag = True
        # for text, label in text_label_pairs_2:
            for pp_item in data_cn_total:
                if text in pp_item:
                    # print(text, label)
                    # pairs_2.append((text, label))
                    # pairs_2.append(text)
                    flag = False
                    break
            if flag is True:
                pairs_2.append(text)
    # 在这里加一层过滤。使用从大量app的隐私政策中提取出来的隐私数据项和pairs_1，pairs_2的结果做交集，过滤掉一些乱码或者无意义数据。
    # 确保最终报告的数据项是有意义的
    with open('total_pp_privacy_data_items.txt', 'r', encoding='utf8') as f:
        contents = f.readlines()
    total_pp_data_items = set(contents)
    pairs_1 = list(total_pp_data_items.intersection(set(pairs_1)))
    pairs_2 = list(total_pp_data_items.intersection(set(pairs_2)))
    # TODO 此处可以根据config的配置情况,使用if-else判断输出什么log
    data_item = {}
    if config_settings['code_inspection'] == 'true':
        data_item['code_inspection'] = pp_missing_items
    if config_settings['ui_static'] == 'true':
        data_item['context_sensitive_privacy_data_item_located'] = pairs_1
    if config_settings['dynamic_print_sensitive_item'] == 'true' and config_settings['ui_dynamic'] == 'true':
        data_item['dynamic_sensitive_item'] = pairs_2
    if config_settings['pp_print_permission_info'] == 'true':
        data_item['permission_list'] = permission_list
    if config_settings['pp_print_sensitive_item'] == 'true':
        data_item['pp_data_items'] = data_cn_total
    #  暂时把sdk信息放在这里
    if config_settings['pp_print_sdk_info'] == 'true':
        data_item['pp_sdk_info'] = pp_sdk
    if config_settings['pp_print_others'] == 'true':
        data_item['compliance_analysis_part_1'] = {}
        if pp_compliance is not None:
            data_item['compliance_analysis_part_1']['data_recall'] = pp_compliance['compliance-analysis'][
                'data-recall']
            data_item['compliance_analysis_part_1']['account_delete'] = pp_compliance['compliance-analysis'][
                'account-delete']
            data_item['compliance_analysis_part_1']['complaint_channel'] = pp_compliance['compliance-analysis'][
                'complaint-channel']
        else:
            data_item['compliance_analysis_part_1']['data_recall'] = 'not found'
            data_item['compliance_analysis_part_1']['account_delete'] = 'not found'
            data_item['compliance_analysis_part_1']['complaint_channel'] = 'not found'
    if config_settings['pp_print_long_sentences'] == 'true':
        if pp_compliance is not None:
            data_item['pp_long_sentences'] = pp_compliance['compliance-analysis']['long-sentence-judge']
        else:
            data_item['pp_long_sentences']= 'not found'
    if config_settings['dynamic_print_full_ui_content'] == 'true' and config_settings['ui_dynamic'] == 'true':
        # 把dumpjson里的JSON日志拷贝过来,代码逻辑去别的文件拷贝一份
        app_name_log_dict = get_log()
        # 删掉本次分析未指定的app 的json log
        with open('../AppUIAutomator2Navigation/apk_pkgName.txt', 'r', encoding='utf-8') as f:
            contents = set([line.strip('\n').split('|')[0].strip() for line in f.readlines()])
        keys = list(app_name_log_dict.keys())
        for app in keys:
            if app not in contents:
                app_name_log_dict.pop(app, f"{app} does not exists in apk_pkgName.txt...")

        for key, val in app_name_log_dict.items():
            new_name = final_res_log_dir + '/' + key + '_dynamic.json'
            if new_name[new_name.rindex('/') + 1:] in os.listdir(final_res_log_dir):
                # print(new_name + ' existed, continue...')
                continue
            shutil.copyfile(dynamic_log_path + '/' + val, new_name)

    # final_res.append({'privacy_policy_analysis': pp_compliance})
    # data_item = {'context_sensitive_privacy_data_item_located': pairs_1, 'dynamic_UI_explore': pairs_2,
    #              'code_inspection': pp_missing_items}
    final_res.append(data_item)

    # final_res.append(pairs_1)
    # final_res.append(pairs_2)
    # final_res.append(pp_missing_items)
    with open(final_res_log_dir + '/' + app_name + '.json', 'w') as f:
        tmp_json = json.dumps(final_res, indent=4, ensure_ascii=False)
        f.write(tmp_json)
