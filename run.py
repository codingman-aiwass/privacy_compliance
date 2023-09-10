import configparser
import getopt
import os
import pickle
import signal
import subprocess
import sys
import platform
import json

from configobj import ConfigObj


# from context_sensitive_privacy_data_location.integrate_log import main as integrate


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


# 默认情况下,直接按顺序执行

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


def determine_aapt(os_type):
    # Modify the properties file
    props = ConfigObj('RunningConfig.properties', encoding='UTF8')

    # Modify the 'apk' setting in the properties file
    props['aapt'] = './config/build-tools-{}/aapt'.format(os_type)

    # Save the modified properties file
    with open('RunningConfig.properties', 'wb',encoding='UTF8') as prop_file:
        props.write(prop_file)


print('input apks to analysis(give absolute path)...')
apk_path = input()
config_apks_to_analysis(apk_path)
cur_path = os.getcwd()

# if config_settings['code_inspection'] == 'true':
os.chdir('./Privacy-compliance-detection-2.1/core')
# 确定使用哪一种aapt
determine_aapt(get_OS_type())
os_type = get_OS_type()
if os_type in ['linux', 'mac']:
    execute_cmd_with_timeout('sh static-run.sh')
elif os_type == 'win':
    execute_cmd_with_timeout('PowerShell.exe .\static-run.ps1')
print('finish code_inspection of apk.')
os.chdir(cur_path)

if config_settings['get_pp_from_app_store'] == 'true':
    execute_cmd_with_timeout('python3 get_urls.py')
else:
    # 动态运行获取隐私政策
    os.chdir('./AppUIAutomator2Navigation')
    with open('apk_pkgName.txt') as f:
        content = f.readlines()
    pkgName_appName_list = [item.rstrip('\n') for item in content]
    for pkgName_appName in pkgName_appName_list:
        try:
            pkgName, appName = pkgName_appName.split(' | ')
            # 判断操作系统版本,分win和linux/mac
            os_type = get_OS_type()
            if os_type in ['linux', 'mac']:
                execute_cmd_with_timeout(
                    './run.sh {} {} {}'.format(pkgName, appName, config_settings['dynamic_ui_depth']))
            else:
                execute_cmd_with_timeout(
                    'PowerShell.exe ./run.ps1 {} {} {}'.format(pkgName, appName, config_settings['dynamic_ui_depth']))
        except Exception:
            print('error occurred, continue...')
    os.chdir(cur_path)
    # 从动态分析的文件夹中获取得到的隐私政策url,按照app分类,查看是否其下的文件夹中有隐私政策url,任意找到一个就返回
    apps_folders = os.listdir('./AppUIAutomator2Navigation/collectData')
    app_dict = {}
    app_set = set()
    app_pp = {}
    for app_folder in apps_folders:
        if app_folder == '.DS_Store':
            continue
        app = app_folder[:app_folder.index('-')]
        if app not in app_set:
            app_set.add(app)
            app_dict[app] = [app_folder]
        else:
            app_dict[app].append(app_folder)
    for key, val in app_dict.items():
        for folder in val:
            dirs = os.listdir('./AppUIAutomator2Navigation/collectData' + '/' + folder)
            if 'PrivacyPolicy' not in dirs:
                continue
            elif 'PrivacyPolicy' in dirs:
                # 找到了隐私政策，break 返回
                pp_file = os.listdir('./AppUIAutomator2Navigation/collectData' + '/' + folder + '/PrivacyPolicy/')[
                    0]
                with open(
                        './AppUIAutomator2Navigation/collectData' + '/' + folder + '/PrivacyPolicy/' + pp_file) as f:
                    pp_url = f.readlines()[0].strip(',\n')
                if 'html' in pp_url:
                    app_pp[key] = pp_url[:pp_url.index('html') + 4]
                elif 'htm' in pp_url:
                    app_pp[key] = pp_url[:pp_url.index('htm') + 3]
                break
    # app_pp 中存放隐私政策url和包名
    with open('./Privacy-compliance-detection-2.1/core/pkgName_url.json', 'w') as f:
        json.dump(app_pp, f, indent=4, ensure_ascii=True)
    with open('pkgName_url.json', 'w') as f:
        json.dump(app_pp, f, indent=4, ensure_ascii=True)
    # 对app_pp和app_set集合做差集，得到缺失隐私政策的app
    apps_missing_pp = app_set - set(app_pp.keys())
    with open('apps_missing_pp_url.txt','w',encoding='utf8') as f:
        for item in apps_missing_pp:
            f.write(item)
            f.write('\n')

os.chdir('./Privacy-compliance-detection-2.1/core')
execute_cmd_with_timeout('python3 privacy-policy-main.py')
execute_cmd_with_timeout('python3 report_data_in_pp_and_program.py')
os.chdir(cur_path)

if config_settings['ui_static'] == 'true':
    os.chdir('./context_sensitive_privacy_data_location')
    execute_cmd_with_timeout('python3 run_jar.py')
    execute_cmd_with_timeout('python3 run_UI_static.py')
    os.chdir(cur_path)

if config_settings['ui_dynamic'] == 'true' and config_settings['get_pp_from_app_store'] == 'true':
    print('this module has been run before...')
    pass
    # os.chdir('./AppUIAutomator2Navigation-main')
    # with open('apk_pkgName.txt') as f:
    #     content = f.readlines()
    # pkgName_appName_list = [item.rstrip('\n') for item in content]
    # for pkgName_appName in pkgName_appName_list:
    #     try:
    #         pkgName, appName = pkgName_appName.split(' | ')
    #         # TODO 还有'get_pp_from_dynamically_running_app', 'dynamic_ui_depth', 'dynamic_pp_parsing'需要配置
    #         # 判断操作系统版本,分win和linux/mac
    #         os_type = get_OS_type()
    #         if os_type in ['linux', 'mac']:
    #             execute_cmd_with_timeout(
    #                 './run.sh {} {} {}'.format(pkgName, appName, config_settings['dynamic_ui_depth']))
    #         else:
    #             execute_cmd_with_timeout(
    #                 './run.ps1 {} {} {}'.format(pkgName, appName, config_settings['dynamic_ui_depth']))
    #     except Exception:
    #         print('error occurred, continue...')
    # os.chdir(cur_path)
elif config_settings['ui_dynamic'] == 'true' and config_settings['get_pp_from_app_store'] == 'false':
    os.chdir('./AppUIAutomator2Navigation')
    with open('apk_pkgName.txt') as f:
        content = f.readlines()
    pkgName_appName_list = [item.rstrip('\n') for item in content]
    for pkgName_appName in pkgName_appName_list:
        try:
            pkgName, appName = pkgName_appName.split(' | ')
            # TODO 还有'get_pp_from_dynamically_running_app', 'dynamic_ui_depth', 'dynamic_pp_parsing'需要配置
            # 判断操作系统版本,分win和linux/mac
            os_type = get_OS_type()
            if os_type in ['linux', 'mac']:
                execute_cmd_with_timeout(
                    './run.sh {} {} {}'.format(pkgName, appName, config_settings['dynamic_ui_depth']))
            else:
                execute_cmd_with_timeout(
                    'PowerShell.exe .\run.ps1 {} {} {}'.format(pkgName, appName, config_settings['dynamic_ui_depth']))
        except Exception:
            print('error occurred, continue...')
    os.chdir(cur_path)

os.chdir('./context_sensitive_privacy_data_location')
execute_cmd_with_timeout('python3 get_dynamic_res.py')
# integrate(config_settings)
# 保存字典config_settings,然后让integrate log读取
with open('config_settings.pkl', 'wb') as f:
    pickle.dump(config_settings, f, pickle.HIGHEST_PROTOCOL)
execute_cmd_with_timeout('python3 integrate_log.py')
