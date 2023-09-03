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
            text_label_pairs_1 = [(obj["text"], obj["label"]) for obj in output_objects]
        elif 'dynamic' in json_file:
            text_label_pairs_2 = [(obj["text"], obj["label"]) for obj in output_objects]

    # 读取我之前的pp_missing结果,准备加入最后的汇总文件里
    try:
        with open(pp_missing_dir + '/' + app_name + '_pp_missing_items.json', 'r') as f:
            pp_missing = json.load(f)
            pp_missing_items = pp_missing[1]
        # 读取佳颖的隐私政策中冗长的句子，以及另外几个不合规的分析
        with open(pp_compliance_dir + '/' + app_name + '.json', 'r') as f:
            pp = json.load(f)
            data_cn_total = pp[0]['data-cn-total']
            permission_list = pp[0]['permission_list']

            # TODO 此处还需要细分各类情况.比如声明权限信息 SDK信息,等等.需要多设置几个变量接收
            pp_compliance = pp[2]

        final_res = []
        pairs_1 = []
        # 检查哪一些text不在隐私政策中
        # 检查佳涛的
        if text_label_pairs_1 is not None:
            for text, label in text_label_pairs_1:
                for pp_item in data_cn_total:
                    if text in pp_item:
                        # print(text, label)
                        pairs_1.append((text, label))

        # 检查东鹏的
        pairs_2 = []
        if text_label_pairs_2 is not None:
            for text, label in text_label_pairs_2:
                for pp_item in data_cn_total:
                    if text in pp_item:
                        # print(text, label)
                        pairs_2.append((text, label))
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
        if config_settings['pp_print_others'] == 'true':
            data_item['compliance_analysis_part_1'] = {}
            data_item['compliance_analysis_part_1']['data_recall'] = pp_compliance['compliance-analysis'][
                'data-recall']
            data_item['compliance_analysis_part_1']['account_delete'] = pp_compliance['compliance-analysis'][
                'account-delete']
            data_item['compliance_analysis_part_1']['complaint_channel'] = pp_compliance['compliance-analysis'][
                'complaint-channel']
        if config_settings['pp_print_long_sentences'] == 'true':
            data_item['pp_long_sentences'] = pp_compliance['compliance-analysis']['long-sentence-judge']
        if config_settings['dynamic_print_full_ui_content'] == 'true' and config_settings['ui_dynamic'] == 'true':
            # 把dumpjson里的JSON日志拷贝过来,代码逻辑去别的文件拷贝一份
            app_name_log_dict = get_log()
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
    except FileNotFoundError:
        print(pp_missing_dir + '/' + app_name + '_pp_missing_items.json')
        print(pp_compliance_dir + '/' + app_name + '.json')
        print(final_res_log_dir + '/' + app_name + '.json')

        print('missing pp_missing or privacy policy log..continue..')
        print('---------')
