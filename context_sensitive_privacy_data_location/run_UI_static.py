import json
import os
import shutil
import re
import platform

from dealWithInputAndOutput import get_run_jar_settings
from run_jar import execute_cmd_with_timeout

def get_OS_type():
    sys_platform = platform.platform().lower()
    os_type = ''
    if "windows" in sys_platform:
        os_type = 'win'
    elif "darwin" in sys_platform or 'mac' in sys_platform:
        os_type = 'mac'
    elif "linux" in sys_platform:
        os_type = 'linux'
    else:
        print('Unknown OS,regard as linux...')
        os_type = 'linux'
    return os_type


def get_ends_with_suffix_files_in_folder(folder, suffix) -> list:
    res = []
    for file_name in os.listdir(folder):
        if file_name.endswith(suffix):
            res.append(os.path.join(folder, file_name))
    return res


# 对于静态UI分析
# 首先,需要运行run_jar批量处理apk
# execute_cmd_with_timeout('python run_jar.py')

# 其次,需要依次循环调用data_item_infer和label_new_or_old进行标记
# 需要读取输出结果文件夹里的文件
_, outputdir, _ = get_run_jar_settings()
output_jsons = get_ends_with_suffix_files_in_folder(outputdir, '_output.json')
# 读取json文件里的包名,修改文件名
for output_json in output_jsons:
    with open(output_json, 'r') as f:
        content = json.load(f)
    appName = content.get('AppName')
    if 'dynamic' in output_json:
        continue
    # 判断文件名中是否含有整数
    # if re.compile(r'\b\d+\b').search(output_json):
    #     continue
    # os.rename(output_json, appName + output_json[output_json.index('_'):])
    new_name = output_json[:output_json.rindex('/') + 1] + appName + '_static' + output_json[output_json.rindex('_output'):]
    print(output_json)
    print(new_name)
    print('------')
    try:
        shutil.copyfile(output_json, new_name)
    except shutil.SameFileError:
        print('{} and {} is the same file...'.format(output_json,new_name))
        print('-------------------')


output_jsons = get_ends_with_suffix_files_in_folder(outputdir, '_static_output.json')
print(output_jsons)
os_type = get_OS_type()
for output_json in output_jsons:
    print('output_json',output_json,'static_output_filtered_labeled.json',output_json[:output_json.index(
        "_")] + '_static_output_filtered_labeled.json')
    if os_type == 'win':
        execute_cmd_with_timeout('python data_item_infer_new.py {} {}'.format(output_json, output_json[:output_json.index(
            "_")] + '_static_output_filtered_labeled.json'))
    elif os_type in ['mac','linux']:
        execute_cmd_with_timeout(
            'python3 data_item_infer_new.py {} {}'.format(output_json, output_json[:output_json.index(
                "_")] + '_static_output_filtered_labeled.json'))
print("=============================")
# output_filtered_jsons = get_ends_with_suffix_files_in_folder(outputdir, '_static_output_filtered.json')
# print(output_filtered_jsons)
# for output_filtered_json in output_filtered_jsons:
#     print('output_filtered_json',output_filtered_json)
#     print('output_filtered_labeled_json',output_filtered_json[:output_filtered_json.index("_")] + '_static_output_filtered_labeled.json')
#     execute_cmd_with_timeout('python3 label_new_or_old.py {} {}'.format(output_filtered_json, output_filtered_json[
#                                                                                               :output_filtered_json.index(
#                                                                                                   "_")] + '_static_output_filtered_labeled.json'))
