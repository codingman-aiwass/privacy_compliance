import configparser
import getopt
import os
import pickle
import threading
import signal
import subprocess
import sys
import platform
import json

from configobj import ConfigObj

from AppUIAutomator2Navigation.stop_and_run_uiautomator import rerun_uiautomator2
from get_urls import get_pkg_names_from_input_list
from get_urls import get_pp_from_app_store


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


def execute_cmd_with_timeout(cmd, timeout=1800):
    p = subprocess.Popen(cmd, stderr=subprocess.STDOUT, shell=True)
    try:
        p.wait(timeout)
    except subprocess.TimeoutExpired:
        p.send_signal(signal.SIGINT)
        p.wait()


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
    with open('RunningConfig.properties', 'wb') as prop_file:
        props.write(prop_file)


# 通过给定的apk路径，判断该路径下有多少个apk文件。该apk_path中可能会有多个路径，彼此之间用;隔开。
def get_apks_num(apk_path):
    pathes = apk_path.split(';')
    app_set = set()
    for single_path in pathes:
        if single_path.endswith('.apk'):
            app_set.add(single_path[single_path.rindex('/') + 1:])
        elif os.path.isdir(single_path):
            files = os.listdir(single_path)
            apk_files = [apk_file for apk_file in files if apk_file.endswith('.apk')]
            app_set.update(apk_files)
    # print(app_set)
    return len(app_set)


def clear_app_cache(app_package_name):
    print('正在清除应用包名为{}的数据。。。'.format(app_package_name))
    execute_cmd_with_timeout('adb shell pm clear {}'.format(app_package_name))
    print('清除完毕。')


def clear_all_files_in_folder(folder):
    # 删除传入的文件夹里所有的文件
    for root, dirs, files in os.walk(folder, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))

# 运行整套工具之前，完成必要的初始化。
def initSettings():
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
                           'pp_print_sensitive_item': 'true', 'pp_print_others': 'true',
                           'pp_print_long_sentences': 'true',
                           'dynamic_print_full_ui_content': 'true', 'dynamic_print_sensitive_item': 'true',
                           'get_pp_from_app_store': 'false', 'get_pp_from_dynamically_running_app': 'true',
                           'dynamic_ui_depth': '3', 'dynamic_run_time': '600', 'run_in_docker': 'true'}

    else:
        for opt, arg in opts:
            if opt == '-h':
                print('run.py -c config.ini')
            # elif opt == '-c':
            elif opt in ("-c", "--config"):
                config_settings = get_config_settings(arg)

    # 默认情况下,直接按顺序执行,判断是否在docker中执行
    if config_settings['run_in_docker'] == 'true':
        apk_path = (os.getcwd() + os.path.sep + 'apks').replace('\\', '/')
    elif config_settings['run_in_docker'] == 'false':
        print('input apks to analysis(give absolute path)...')
        apk_path = input().replace("\\", "/")
    config_apks_to_analysis(apk_path)
    cur_path = os.getcwd()
    total_apks_to_analysis = get_apks_num(apk_path)
    return config_settings,cur_path,apk_path,get_OS_type(),total_apks_to_analysis

# 运行code_inspection部分
def run_code_inspection(cur_path,total_apks_to_analysis,os_type):
    os.chdir('./Privacy-compliance-detection-2.1/core')
    # 确定使用哪一种aapt
    determine_aapt(os_type)
    # 这里需要改为根据需要分析的apk的数量决定超时时间。写死3600的话就只会跑3600s就退出。剩下的app就没法继续分析。
    # 通过查看指定的路径下有多少个apk，根据apk的个数确定超时中断时间。
    if os_type in ['linux', 'mac']:
        # 防止因为换行符问题报错
        print("执行sed -i 's/\r$//' static-run.sh")
        execute_cmd_with_timeout("sed -i 's/\r$//' static-run.sh")
        execute_cmd_with_timeout('sh static-run.sh', 3600 * total_apks_to_analysis)
    elif os_type == 'win':
        execute_cmd_with_timeout('PowerShell.exe .\static-run.ps1', 3600 * total_apks_to_analysis)
    print('finish code_inspection of apk.')
    os.chdir(cur_path)

# 运行隐私政策获取模块
def get_privacy_policy(os_type,config_settings,cur_path):
    if config_settings['get_pp_from_app_store'] == 'true':
        if os_type == 'win':
            execute_cmd_with_timeout('python get_urls.py')
        elif os_type in ['mac', 'linux']:
            execute_cmd_with_timeout('python3 get_urls.py')
    else:
        # 动态运行获取隐私政策
        os.chdir('./AppUIAutomator2Navigation')
        with open('apk_pkgName.txt','r',encoding='utf-8') as f:
            content = f.readlines()
        pkgName_appName_list = [item.rstrip('\n') for item in content]
        for pkgName_appName in pkgName_appName_list:
            try:
                pkgName, appName = pkgName_appName.split(' | ')
                appName = appName.strip('\'')
                # 清除app缓存数据
                clear_app_cache(pkgName)
                # 重启uiautomator2
                rerun_uiautomator2()
                if os_type in ['linux', 'mac']:
                    execute_cmd_with_timeout(
                        'python3 run.py {} {} {} {}'.format(pkgName, appName, config_settings['dynamic_ui_depth'],
                                                            config_settings['dynamic_run_time']),timeout=int(config_settings['dynamic_run_time']))
                else:
                    execute_cmd_with_timeout(
                        'python run.py {} {} {} {}'.format(pkgName, appName, config_settings['dynamic_ui_depth'],
                                                           config_settings['dynamic_run_time']),timeout=int(config_settings['dynamic_run_time']))

            except Exception:
                print(Exception)
                print('error occurred, continue...')
        os.chdir(cur_path)
        # 从动态分析的文件夹中获取得到的隐私政策url,按照app分类,查看是否其下的文件夹中有隐私政策url,任意找到一个就返回
        apps_folders = os.listdir('./AppUIAutomator2Navigation/collectData')
        app_dict = {}
        # 改为从AppUIAutomator2Navigation中获取应用名
        with open('./AppUIAutomator2Navigation/apk_pkgName.txt', 'r', encoding='utf-8') as f:
            content = f.readlines()
            content = [content.split(' | ')[0] for content in content]
            app_set = set(content)
            print('app_set:{}'.format(app_set))

        apps_missing_pp = set()
        app_pp = {}
        for app_folder in apps_folders:
            if app_folder == '.DS_Store':
                continue
            app = app_folder[:app_folder.index('-')]
            if app in app_set:
                app_dict[app] = app_folder
        print('app_dict')
        print(app_dict)
        for key, val in app_dict.items():
            dirs = os.listdir('./AppUIAutomator2Navigation/collectData' + '/' + val)
            if 'PrivacyPolicy' not in dirs:
                print('privacy policy not in ', val)
                apps_missing_pp.add(key)
                continue
            elif 'PrivacyPolicy' in dirs:
                # 找到了隐私政策,修改此处逻辑，判断是否有多行，有多行返回列表；只有一行返回字符串
                pp_file = os.listdir('./AppUIAutomator2Navigation/collectData' + '/' + val + '/PrivacyPolicy/')[
                    0]
                with open(
                        './AppUIAutomator2Navigation/collectData' + '/' + val + '/PrivacyPolicy/' + pp_file,'r',encoding='utf-8') as f:
                    content = f.readlines()
                    content = [item.strip('\n') for item in content]
                    print('content in txt file of PrivacyPolicy', content)
                    pp_url = content
                    print('pp_url:', pp_url)
                    if len(pp_url) == 1:
                        if 'html' in pp_url[0]:
                            app_pp[key] = pp_url[0][:pp_url[0].index('html') + 4]
                        elif 'htm' in pp_url[0]:
                            app_pp[key] = pp_url[0][:pp_url[0].index('htm') + 3]
                    elif len(pp_url) > 1:
                        # TODO 目前先在我这边，对于获取到了多个URL链接的，只保留以.html/htm结尾的，或者含有html/htm的链接
                        # 从这里开始=======
                        for url in pp_url:
                            if url.endswith('html') or url.endswith('htm'):
                                app_pp[key] = url
                                break
                            if 'html' in url or 'htm' in url:
                                app_pp[key] = url
                        # 如果最终app_pp中不含有key，说明找到的全部都不是隐私政策URL，等于没找到隐私政策
                        if key not in app_pp or type(app_pp[key]) != str:
                            print('privacy policy not in ', val)
                            apps_missing_pp.add(key)
                        # TODO 到这里结束========

                        # 下面这行语句会保留所有的URL到一个列表中,是原本做法。
                        # app_pp[key] = pp_url

        # 对app_pp和app_set集合做差集，得到缺失隐私政策的app
        # apps_missing_pp = app_set - set(app_pp.keys())
        with open('dynamic_apps_missing_pp_url.txt', 'w', encoding='utf8') as f:
            for item in apps_missing_pp:
                f.write(item)
                f.write('\n')
        if len(apps_missing_pp) > 0:
            # 说明有隐私政策动态分析没有找到，去app store获取
            print('find pp missing,try to get from app store...')
            pp_urls, missing_urls = get_pp_from_app_store(get_pkg_names_from_input_list(list(apps_missing_pp)))
            app_pp.update(pp_urls)
            # 输出仍然找不到的隐私政策
            if len(missing_urls) > 0:
                with open('apps_still_missing_pp_urls.txt', 'w',encoding='utf-8') as f:
                    for item in missing_urls:
                        f.write(item)
                        f.write('\n')
        # app_pp 中存放隐私政策url和包名

        with open('./Privacy-compliance-detection-2.1/core/pkgName_url.json', 'w',encoding='utf-8') as f:
            json.dump(app_pp, f, indent=4, ensure_ascii=True)
        print(app_pp)
    os.chdir(cur_path)

# 隐私政策分析模块
def analysis_privacy_policy(total_apks_to_analysis,os_type):
    os.chdir('./Privacy-compliance-detection-2.1/core')
    if 'Privacypolicy_txt' in os.listdir():
        clear_all_files_in_folder('./Privacypolicy_txt')
    if 'PrivacyPolicySaveDir' in os.listdir():
        clear_all_files_in_folder('./PrivacyPolicySaveDir')
    if 'Privacypolicy_txt' not in os.listdir():
        os.mkdir('Privacypolicy_txt')
    if 'PrivacyPolicySaveDir' not in os.listdir():
        os.mkdir('PrivacyPolicySaveDir')
    try:
        if os_type == 'win':
            execute_cmd_with_timeout('python privacy-policy-main.py',timeout=total_apks_to_analysis * 600)
            execute_cmd_with_timeout('python report_data_in_pp_and_program.py',timeout=total_apks_to_analysis * 600)
        elif os_type in ['linux', 'mac']:
            execute_cmd_with_timeout('python3 privacy-policy-main.py',timeout=total_apks_to_analysis * 600)
            execute_cmd_with_timeout('python3 report_data_in_pp_and_program.py',timeout=total_apks_to_analysis * 600)
    except UnboundLocalError:
        print('隐私政策解析失败，continue。。。')
    os.chdir(cur_path)

# 静态UI分析模块
def static_UI_analysis(total_apks_to_analysis,config_settings,os_type):
    if config_settings['ui_static'] == 'true':
        os.chdir('./context_sensitive_privacy_data_location')
        if 'tmp-output' in os.listdir():
            # shutil.rmtree('tmp-output')
            # os.mkdir('tmp-output')
            # 同理，不直接使用rmtree
            clear_all_files_in_folder('./tmp-output')
        if 'tmp-output' not in os.listdir():
            os.mkdir('tmp-output')
        if 'final_res_log_dir' in os.listdir():
            # shutil.rmtree('final_res_log_dir')
            # os.mkdir('final_res_log_dir')
            # 同理，不直接使用rmtree
            clear_all_files_in_folder('./final_res_log_dir')
        if 'final_res_log_dir' not in os.listdir():
            os.mkdir('final_res_log_dir')
        if os_type == 'win':
            execute_cmd_with_timeout('python run_jar.py', total_apks_to_analysis * 600)
            execute_cmd_with_timeout('python run_UI_static.py')
        elif os_type in ['linux', 'mac']:
            execute_cmd_with_timeout('python3 run_jar.py', total_apks_to_analysis * 600)
            print('execute python3 run_UI_static.py ....')
            execute_cmd_with_timeout('python3 run_UI_static.py')
            print('execute run_UI_static over...')
        os.chdir(cur_path)

# 动态APP测试模块，可能不会运行
def dynamic_app_test(config_settings,cur_path,os_type):
    if config_settings['ui_dynamic'] == 'true' and config_settings['get_pp_from_dynamically_running_app'] == 'true':
        print('this module has been run before...')
    elif config_settings['ui_dynamic'] == 'true' and config_settings['get_pp_from_dynamically_running_app'] == 'false':
        print(
            "config_settings['ui_dynamic'] == 'true' and config_settings['get_pp_from_dynamically_running_app'] == 'false'")
        os.chdir('./AppUIAutomator2Navigation')
        with open('apk_pkgName.txt','r',encoding='utf-8') as f:
            content = f.readlines()
        pkgName_appName_list = [item.rstrip('\n') for item in content]
        for pkgName_appName in pkgName_appName_list:
            try:
                pkgName, appName = pkgName_appName.split(' | ')
                appName = appName.strip('\'')
                # 判断操作系统版本,分win和linux/mac
                os_type = get_OS_type()
                if os_type in ['linux', 'mac']:
                    execute_cmd_with_timeout(
                        'python3 run.py {} {} {} {}'.format(pkgName, appName, config_settings['dynamic_ui_depth'],
                                                            config_settings['dynamic_run_time']))
                else:
                    execute_cmd_with_timeout(
                        'python run.py {} {} {} {}'.format(pkgName, appName, config_settings['dynamic_ui_depth'],
                                                           config_settings['dynamic_run_time']))
            except Exception:
                print('error occurred, continue...')
        os.chdir(cur_path)
    else:
        print('did not execute ui_dynamic...')
        print(config_settings['ui_dynamic'], config_settings['get_pp_from_dynamically_running_app'])

# 输出最终log
def printFinalLog(os_type):
    os.chdir('./context_sensitive_privacy_data_location')
    if os_type == 'win':
        execute_cmd_with_timeout('python get_dynamic_res.py')
    elif os_type in ['linux', 'mac']:
        execute_cmd_with_timeout('python3 get_dynamic_res.py')
    # integrate(config_settings)
    # 保存字典config_settings,然后让integrate log读取
    with open('config_settings.pkl', 'wb') as f:
        pickle.dump(config_settings, f, pickle.HIGHEST_PROTOCOL)

    if os_type == 'win':
        execute_cmd_with_timeout('python integrate_log.py')
    elif os_type in ['linux', 'mac']:
        execute_cmd_with_timeout('python3 integrate_log.py')
    os.chdir(cur_path)

if __name__ == '__main__':
    # code_inspection 最先执行，可以和 获取隐私政策部分、静态UI分析、动态测试 并行执行，分析隐私政策部分 必须在 获取隐私政策 后才能执行
    # 即可以并行的部分：run_code_inspection、 get_privacy_policy、 static_UI_analysis、 dynamic_app_test,
    # 分析隐私政策和整理最终log需要放在最后，顺序执行
    # 初始化放在最前，不和其他部分并行

    # 初始化
    config_settings,cur_path,apk_path,os_type,total_apks_to_analysis = initSettings()

    # 创建线程
    threads = []

    # 创建并启动线程1：run_code_inspection
    thread1 = threading.Thread(target=run_code_inspection, args=(cur_path, total_apks_to_analysis, os_type))
    threads.append(thread1)
    thread1.start()

    # 创建并启动线程2：get_privacy_policy
    thread2 = threading.Thread(target=get_privacy_policy, args=(os_type, config_settings, cur_path))
    threads.append(thread2)
    thread2.start()

    # 创建并启动线程3：static_UI_analysis
    thread3 = threading.Thread(target=static_UI_analysis, args=(total_apks_to_analysis, config_settings, os_type))
    threads.append(thread3)
    thread3.start()

    # 创建并启动线程4：dynamic_app_test
    thread4 = threading.Thread(target=dynamic_app_test, args=(config_settings, cur_path, os_type))
    threads.append(thread4)
    thread4.start()

    # 等待所有线程完成
    for thread in threads:
        thread.join()

    # 执行分析隐私政策
    analysis_privacy_policy(total_apks_to_analysis, os_type)

    # 执行整理最终log
    printFinalLog(os_type)

    # # 运行code_inspection
    # run_code_inspection(cur_path,total_apks_to_analysis,os_type)
    # # 获取隐私政策
    # get_privacy_policy(os_type,config_settings,cur_path)
    # # 静态UI分析
    # static_UI_analysis(total_apks_to_analysis,config_settings,os_type)
    # # 动态测试
    # dynamic_app_test(config_settings,cur_path,os_type)
    #
    # # 分析隐私政策
    # analysis_privacy_policy(total_apks_to_analysis, os_type)
    #
    # # 整理最终log
    # printFinalLog(os_type)
