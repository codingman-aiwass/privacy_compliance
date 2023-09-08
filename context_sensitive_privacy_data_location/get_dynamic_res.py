import os
import shutil
from run_jar import execute_cmd_with_timeout
from dealWithInputAndOutput import get_run_jar_settings
from dealWithInputAndOutput import get_settings_by_section_and_name

# 首先,需要得到动态输出的日志
# dynamic_log_path = r'../AppUIAutomator2Navigation-main/dumpjson'
dynamic_log_path = get_settings_by_section_and_name('dynamic-setting', 'json_log_path')

_, outputdir, _ = get_run_jar_settings()


# 从dumpjson文件夹里的一堆log中找出时间最久的log
def get_log():
    prefix_set = set()
    for file_name in os.listdir(dynamic_log_path):
        if file_name.startswith('.'):
            continue
        # print(file_name[file_name.index('&time') + 5 :file_name.index('.json') - 1])
        prefix_set.add(file_name[:file_name.index('-')])
    prefix_dict = {}
    for prefix in prefix_set:
        timestamp = 0
        for file_name in os.listdir(dynamic_log_path):
            if file_name.startswith('.'):
                continue
            if file_name.startswith(prefix):
                # print(file_name)
                cur_timestamp = file_name[file_name.index('-') + 1:]
                tmp = cur_timestamp.split('-')
                cur_timestamp = int(tmp[0] + tmp[1])
                if int(cur_timestamp) > timestamp:
                    timestamp = int(cur_timestamp)
                    prefix_dict[prefix] = file_name + '/Dumpjson/' + os.listdir(dynamic_log_path + '/' + file_name + '/Dumpjson')[0]

    # print(prefix_dict)
    return prefix_dict


# 得到log之后,需要重命名一下,复制到output文件夹下,然后依次送给 integrate_dynamic \ data_item_infer \ label_new_or_old 处理

app_name_log_dict = get_log()
# print(app_name_log_dict)
for key, val in app_name_log_dict.items():
    new_name = outputdir + '/' + key + '_dynamic.json'
    if new_name[new_name.rindex('/') + 1:] in os.listdir(outputdir):
        print(new_name + ' existed, continue...')
        continue
    shutil.copyfile(dynamic_log_path + '/' + val, new_name)

    execute_cmd_with_timeout(
        'python integrate_dynamic.py {} {}'.format(new_name, outputdir + '/' + key + '_dynamic_output.json'))

    execute_cmd_with_timeout(
        'python data_item_infer.py {} {}'.format(outputdir + '/' + key + '_dynamic_output.json',
                                                 outputdir + '/' + key + '_dynamic_output_filtered.json'))

    execute_cmd_with_timeout(
        'python label_new_or_old.py {} {}'.format(outputdir + '/' + key + '_dynamic_output_filtered.json',
                                                  outputdir + '/' + key + '_dynamic_output_filtered_labeled.json'))
