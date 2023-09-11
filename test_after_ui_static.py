import configparser
import getopt
import os
import pickle
import shutil
import signal
import subprocess
import sys
import platform
import json


def get_config_settings(config_file):
    config = configparser.ConfigParser()
    config.read(config_file, encoding='utf-8')
    pairs = []
    for section in config.sections():
        pairs.extend(config.items(section))
    dic = {}
    for key, value in pairs:
        dic[key] = value
    return dic


def config_apks_to_analysis(apks):
    # Read input from the terminal
    new_apk_path = apks

    # Modify the INI file
    config = configparser.ConfigParser()
    config.read(
        'context_sensitive_privacy_data_location/RunningConfig.ini')  # Replace 'config.ini' with the path to your INI file

    # Modify the 'apk' setting in the INI file
    config.set('run_jar_settings', 'apk',
               new_apk_path)  # Replace 'section_name' with the appropriate section name in your INI file

    # Save the modified INI file
    with open('context_sensitive_privacy_data_location/RunningConfig.ini',
              'w') as config_file:  # Replace 'config.ini' with the path to your INI file
        config.write(config_file)

    # Modify the properties file
    props = ConfigObj('Privacy-compliance-detection-2.1/core/RunningConfig.properties',
                      encoding='UTF8')  # Replace 'config.properties' with the path to your properties file

    # Modify the 'apk' setting in the properties file
    props['apk'] = new_apk_path

    # Save the modified properties file
    with open('Privacy-compliance-detection-2.1/core/RunningConfig.properties',
              'wb') as prop_file:  # Replace 'config.properties' with the path to your properties file
        props.write(prop_file)




def execute_cmd_with_timeout(cmd, timeout=600):
    p = subprocess.Popen(cmd, stderr=subprocess.STDOUT, shell=True)
    try:
        p.wait(timeout)
    except subprocess.TimeoutExpired:
        p.send_signal(signal.SIGINT)
        p.wait()


from configobj import ConfigObj

input_argv = sys.argv[1:]
try:
    opts, args = getopt.getopt(input_argv, "hc:", ["config="])
except getopt.GetoptError:
    print('run.py -c <config.ini>')
    sys.exit(2)
config_settings = None
if len(opts) == 0:
    # 没有指定配置文件,按照默认配置来
    config_settings = {'ui_static': 'true', 'ui_dynamic': 'true', 'code_inspection': 'true',
                       'pp_print_permission_info': 'true', 'pp_print_sdk_info': 'true',
                       'pp_print_sensitive_item': 'true', 'pp_print_others': 'true', 'pp_print_long_sentences': 'true',
                       'dynamic_print_full_ui_content': 'true', 'dynamic_print_sensitive_item': 'true',
                       'get_pp_from_app_store': 'false', 'get_pp_from_dynamically_running_app': 'true',
                       'dynamic_ui_depth': '3', 'dynamic_pp_parsing': 'true'}

else:
    for opt, arg in opts:
        if opt == '-h':
            print('run.py -c config.ini')
        # elif opt == '-c':
        elif opt in ("-c", "--config"):
            config_settings = get_config_settings(arg)

os.chdir('./context_sensitive_privacy_data_location')
# execute_cmd_with_timeout('python3 --version')
# execute_cmd_with_timeout('pip3 list | grep hanlp')

# execute_cmd_with_timeout('python3 run_UI_static.py')

# execute_cmd_with_timeout('python3 get_dynamic_res.py')
# integrate(config_settings)
# 保存字典config_settings,然后让integrate log读取
with open('config_settings.pkl', 'wb') as f:
    pickle.dump(config_settings, f, pickle.HIGHEST_PROTOCOL)
execute_cmd_with_timeout('python3 integrate_log.py')