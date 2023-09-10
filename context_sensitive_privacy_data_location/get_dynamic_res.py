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
                    # 此处需要选择一个Dumpjson文件夹里的json，最后用于整合。我们选择时间最久的那个。
                    # 由于这个文件夹里面可能不止一个json，不能单纯的只把第一个拿出来。
                    dumpjson_folder = file_name + '/Dumpjson/'
                    jsons = os.listdir(dynamic_log_path + '/' + dumpjson_folder)
                    if len(jsons) == 1 and jsons[0].endswith('.json'):
                        prefix_dict[prefix] = file_name + '/Dumpjson/' + os.listdir(dynamic_log_path + '/' + file_name + '/Dumpjson')[0]
                    else:
                        # 此时Dumpjson中有多个json日志，挑选时间最长的那一个
                        time_stamp = 0
                        target_json = ''
                        for json_file in jsons:
                            if json_file.endswith('json'):
                                cur_time = int(json_file[json_file.index('&time') + 5:json_file.index('s.json')])
                                if cur_time >= time_stamp:
                                    time_stamp = cur_time
                                    target_json = json_file
                        prefix_dict[prefix] = dumpjson_folder + target_json
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
        'python3 integrate_dynamic.py {} {}'.format(new_name, outputdir + '/' + key + '_dynamic_output.json'))

    execute_cmd_with_timeout(
        'python3 data_item_infer.py {} {}'.format(outputdir + '/' + key + '_dynamic_output.json',
                                                  outputdir + '/' + key + '_dynamic_output_filtered.json'))

    execute_cmd_with_timeout(
        'python3 label_new_or_old.py {} {}'.format(outputdir + '/' + key + '_dynamic_output_filtered.json',
                                                   outputdir + '/' + key + '_dynamic_output_filtered_labeled.json'))
