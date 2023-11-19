import configparser
import datetime
import getopt
import json
import os
import pickle
import platform
import shutil
import signal
import subprocess
import sys
import threading
import time
import traceback
from configobj import ConfigObj

from AppUIAutomator2Navigation.stop_and_run_uiautomator import rerun_uiautomator2
from get_urls import get_pkg_names_from_input_list
from get_urls import get_pp_from_app_store


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


def execute_cmd_with_timeout(cmd, timeout=1800, cwd=None):
    if cwd is None:
        p = subprocess.Popen(cmd, stderr=subprocess.STDOUT, shell=True)
    else:
        p = subprocess.Popen(cmd, stderr=subprocess.STDOUT, shell=True, cwd=cwd)
    try:
        p.wait(timeout)
    except subprocess.TimeoutExpired:
        p.send_signal(signal.SIGINT)
        p.wait()


def get_OS_type():
    sys_platform = platform.platform().lower()
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
    props = ConfigObj('Privacy-compliance-detection-2.1/core/RunningConfig.properties', encoding='UTF8')

    # Modify the 'apk' setting in the properties file
    props['aapt'] = './config/build-tools-{}/aapt'.format(os_type)

    # Save the modified properties file
    with open('Privacy-compliance-detection-2.1/core/RunningConfig.properties', 'wb') as prop_file:
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
    config_settings = {'ui_static': 'true', 'ui_dynamic': 'true', 'code_inspection': 'true',
                       'run_code_inspection': 'true',
                       'pp_print_permission_info': 'true', 'pp_print_sdk_info': 'true',
                       'pp_print_sensitive_item': 'true', 'pp_print_others': 'true',
                       'pp_print_long_sentences': 'true',
                       'dynamic_print_full_ui_content': 'true', 'dynamic_print_sensitive_item': 'true',
                       'get_pp_from_app_store': 'false',
                       'analysis_privacy_policy': 'true',
                       'run_ui_static': 'true', 'run_dynamic_part': 'true',
                       'dynamic_ui_depth': '3', 'dynamic_run_time': '180',
                       'clear_cache': 'true', 'rerun_uiautomator2': 'true', 'start_frida': 'true',
                       'searchprivacypolicy': 'true', 'drawappcallgraph': 'false', 'screenuidrep': "loc",
                       'clear_final_res_dir_before_run': 'true',
                       'clear_tmp_output_dir_before_run': 'true', 'multi-thread': "low"}
    in_docker = False
    if len(opts) == 0:
        # 没有指定配置文件,按照默认配置来
        # 根据是否在docker中运行，决定使用不同的默认config_settings
        if get_OS_type() in ['win', 'mac']:
            in_docker = False
        elif get_OS_type() == 'linux':
            output_info = subprocess.check_output(
                'if [ -f /.dockerenv ]; then echo "inside docker";else echo "in real world";fi', shell=True)
            if output_info == b'inside_docker\n':
                in_docker = True
            elif output_info == b'in real world\n':
                in_docker = False
        if in_docker:
            # 默认状态，只获取隐私政策，不考虑覆盖率
            # 在docker中,默认会执行prepareInDocker.sh,在这个脚本里会启动frida,所以没必要让start_frida为true
            config_settings['host_machine_os_type'] = 'linux'
            config_settings['start_frida'] = 'false'

    else:
        for opt, arg in opts:
            if opt == '-h':
                print('run.py -c config.ini')
            # elif opt == '-c':
            elif opt in ("-c", "--config"):
                config_settings = get_config_settings(arg)
                print('content of config_settings', config_settings)

    # 默认情况下,直接按顺序执行,判断是否在docker中执行
    if in_docker:
        apk_path = (os.getcwd() + os.path.sep + 'apks').replace('\\', '/')
        host_machine_os_type = config_settings['host_machine_os_type']
        # 执行初始化脚本，prepareInDocker.sh
        if host_machine_os_type in ['win', 'mac']:
            # 在run_docker时判断宿主机操作系统的类型，并在config.ini中添加host_os_type一栏，从这里获取操作系统的类型，并判断执行哪一个prepareInDocker.sh
            execute_cmd_with_timeout("bash prepareInDocker.sh")
            execute_cmd_with_timeout("bash prepareInDocker.sh")
        elif host_machine_os_type == 'linux':
            execute_cmd_with_timeout("bash prepareInDocker_linux.sh")

    elif in_docker is False:
        print('input apks to analysis(give absolute path)...')
        apk_path = input().replace("\\", "/")
    # 清空正在运行的第三方应用程序和Google Chrome
    # 非docker环境下也需要清除后台所有程序

    # 暂时弃用启动前清空后台的操作。
    # if get_OS_type() == 'mac':
    #     print('kill all background apps in unix-like os!')
    #     # subprocess.run("sed -i 's/\r$//' kill_all_background_apps.sh", shell=True)
    #     execute_cmd_with_timeout("dos2unix *.sh")
    #     execute_cmd_with_timeout("bash kill_all_background_apps.sh")
    # elif get_OS_type() == 'linux':
    #     print('kill all background apps in unix-like os!')
    #     subprocess.run("sed -i 's/\r$//' *.sh", shell=True)
    #     execute_cmd_with_timeout("bash kill_all_background_apps.sh")
    # elif get_OS_type() == 'win':
    #     print('kill all background apps in win!')
    #     execute_cmd_with_timeout("powershell.exe .\\kill_all_background_apps.ps1")

    # 保留在unix-like os上将Windows上的换行符替换为unix-like os上的换行符的逻辑，防止执行shell脚本的时候报错。
    if get_OS_type() == 'mac':
        execute_cmd_with_timeout("dos2unix *.sh")
        subprocess.run("sed -i 's/\r$//' *.sh", shell=True)
    elif get_OS_type() == 'linux':
        subprocess.run("sed -i 's/\r$//' *.sh", shell=True)
    config_apks_to_analysis(apk_path)
    cur_path = os.getcwd()
    total_apks_to_analysis = get_apks_num(apk_path)
    # 创建存放日志的文件夹，基于时间
    time_now = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    os.makedirs(f'./logs/log_{time_now}')
    log_folder_path = f'{cur_path}/logs/log_{time_now}/'
    return config_settings, cur_path, apk_path, get_OS_type(), total_apks_to_analysis, log_folder_path


# 运行code_inspection部分
def run_code_inspection(cur_path, total_apks_to_analysis, os_type, log_folder_path, config_settings):
    determine_aapt(os_type)
    if config_settings['run_code_inspection'] == 'true':
        print('start run_code_inspection at {}...'.format(time.ctime()))
        # os.chdir('./Privacy-compliance-detection-2.1/core')
        # 确定使用哪一种aapt
        # 这里需要改为根据需要分析的apk的数量决定超时时间。写死3600的话就只会跑3600s就退出。剩下的app就没法继续分析。
        # 通过查看指定的路径下有多少个apk，根据apk的个数确定超时中断时间。
        stdout_file = log_folder_path + 'run_code_inspection_output.log'
        stderr_file = log_folder_path + 'run_code_inspection_error.log'
        if os_type in ['linux', 'mac']:
            with open(stdout_file, "w") as stdout, open(stderr_file, "w") as stderr:
                subprocess.run(["sh", "static-run.sh"],
                               cwd=os.path.join(cur_path, 'Privacy-compliance-detection-2.1', 'core'),
                               timeout=3600 * total_apks_to_analysis, stdout=stdout, stderr=stderr)
        elif os_type == 'win':
            with open(stdout_file, "w") as stdout, open(stderr_file, "w") as stderr:
                subprocess.run(["PowerShell.exe", ".\static-run.ps1"],
                               cwd=os.path.join(cur_path, 'Privacy-compliance-detection-2.1', 'core'),
                               timeout=3600 * total_apks_to_analysis, stdout=stdout, stderr=stderr)
        print('finish code_inspection of apk at {}...'.format(time.ctime()))
        # os.chdir(cur_path)
    elif config_settings['run_code_inspection'] == 'false':
        print('start get apk info at {}...'.format(time.ctime()))
        stdout_file = log_folder_path + 'get_apk_info_output.log'
        stderr_file = log_folder_path + 'get_apk_info_error.log'
        if os_type in ['linux', 'mac']:
            with open(stdout_file, "w") as stdout, open(stderr_file, "w") as stderr:
                subprocess.run("java -jar getApkInfo.jar",
                               cwd=os.path.join(cur_path, 'Privacy-compliance-detection-2.1', 'core'),
                               timeout=10, stdout=stdout, stderr=stderr, shell=True)
        elif os_type == 'win':
            with open(stdout_file, "w") as stdout, open(stderr_file, "w") as stderr:
                subprocess.run("powershell.exe .\\getApkInfo.ps1",
                               cwd=os.path.join(cur_path, 'Privacy-compliance-detection-2.1', 'core'),
                               timeout=10, stdout=stdout, stderr=stderr, shell=True)
        print('finish get apk info at at {}...'.format(time.ctime()))


# 运行隐私政策获取模块
def get_privacy_policy(os_type, config_settings, cur_path, total_apk, log_folder_path):
    print('start get_privacy_policy at {}...'.format(time.ctime()))
    stdout_file = log_folder_path + 'get_privacy_policy_output.log'
    stderr_file = log_folder_path + 'get_privacy_policy_error.log'
    if config_settings['get_pp_from_app_store'] == 'true':
        if os_type == 'win':
            # execute_cmd_with_timeout('python get_urls.py')
            with open(stdout_file, "a") as stdout, open(stderr_file, "a") as stderr:
                subprocess.run('python get_urls.py y', timeout=total_apk * 300, stdout=stdout, stderr=stderr,
                               shell=True)
        elif os_type in ['mac', 'linux']:
            # execute_cmd_with_timeout('python3 get_urls.py')
            with open(stdout_file, "a") as stdout, open(stderr_file, "a") as stderr:
                subprocess.run('python3 get_urls.py y', timeout=total_apk * 300, stdout=stdout, stderr=stderr,
                               shell=True)
        print('finish get_privacy_policy at {}...'.format(time.ctime()))
        if config_settings['analysis_privacy_policy'] == 'true':
            print('start analysis_privacy_policy at {}...'.format(time.ctime()))
            analysis_privacy_policy(total_apks_to_analysis, os_type, cur_path, log_folder_path)
            print('end analysis_privacy_policy at {}...'.format(time.ctime()))
    else:
        # 动态运行获取隐私政策
        # os.chdir('./AppUIAutomator2Navigation')
        # 检查是否有上次运行时留下的记录
        if 'successful_analysis_pp.txt' in os.listdir(os.path.join(cur_path, 'AppUIAutomator2Navigation')):
            os.remove(os.path.join(cur_path, 'AppUIAutomator2Navigation', 'successful_analysis_pp.txt'))
        with open(os.path.join(cur_path, 'AppUIAutomator2Navigation', 'apk_pkgName.txt'), 'r', encoding='utf-8') as f:
            content = f.readlines()
        pkgName_appName_list = [item.rstrip('\n') for item in content]
        if config_settings['searchprivacypolicy'] == 'true':
            # with open(os.path.join(cur_path,'AppUIAutomator2Navigation','apk_pkgName.txt'), 'r', encoding='utf-8') as f:
            #     content = f.readlines()
            # pkgName_appName_list = [item.rstrip('\n') for item in content]
            for pkgName_appName in pkgName_appName_list:
                try:
                    pkgName, appName = pkgName_appName.split(' | ')
                    appName = appName.strip('\'')
                    # 清除app缓存数据
                    print(f'在get privacy policy, 包名为{pkgName}')
                    clear_app_cache(pkgName)
                    # 重启uiautomator2
                    rerun_uiautomator2()
                    if os_type in ['linux', 'mac']:
                        # execute_cmd_with_timeout(
                        #     'python3 run.py {} {} {} {}'.format(pkgName, appName, config_settings['dynamic_ui_depth'],
                        #                                         config_settings['dynamic_run_time']),
                        #     timeout=int(config_settings['dynamic_run_time']),cwd=os.path.join(cur_path, 'AppUIAutomator2Navigation'))
                        # 重启frida
                        if config_settings['start_frida'] == 'true':
                            try:
                                execute_cmd_with_timeout("bash start_frida15.sh", timeout=10)
                            except Exception:
                                print("start frida done.")
                        with open(stdout_file, "a") as stdout, open(stderr_file, "a") as stderr:
                            subprocess.run(["python3", "run.py", pkgName, appName, config_settings['dynamic_ui_depth'],
                                            config_settings['dynamic_run_time'], config_settings['searchprivacypolicy'],
                                            config_settings['drawappcallgraph'], config_settings['screenuidrep']],
                                           cwd=os.path.join(cur_path, 'AppUIAutomator2Navigation'),
                                           timeout=int(config_settings['dynamic_run_time']) + 600, stdout=stdout,
                                           stderr=stderr)
                    else:
                        # 重启frida
                        if config_settings['start_frida'] == 'true':
                            try:
                                execute_cmd_with_timeout("powershell.exe .\\start_frida15.ps1", timeout=10)
                            except Exception:
                                print("start frida done.")
                        # execute_cmd_with_timeout(
                        #     'python run.py {} {} {} {}'.format(pkgName, appName, config_settings['dynamic_ui_depth'],
                        #                                        config_settings['dynamic_run_time']),
                        #     timeout=int(config_settings['dynamic_run_time']),cwd=os.path.join(cur_path, 'AppUIAutomator2Navigation'))
                        with open(stdout_file, "a") as stdout, open(stderr_file, "a") as stderr:
                            subprocess.run(["python", "run.py", pkgName, appName, config_settings['dynamic_ui_depth'],
                                            config_settings['dynamic_run_time'], config_settings['searchprivacypolicy'],
                                            config_settings['drawappcallgraph'], config_settings['screenuidrep']],
                                           cwd=os.path.join(cur_path, 'AppUIAutomator2Navigation'),
                                           timeout=int(config_settings['dynamic_run_time']) + 600, stderr=stderr,
                                           stdout=stdout)

                    # 运行结束后，使用adb关闭该应用的进程
                    execute_cmd_with_timeout(f"adb shell am force-stop {pkgName}", cwd=cur_path)
                    print(f'kill_app.sh in dynamic_run in try..,kill {pkgName}')
                    time.sleep(2)
                except Exception as e:
                    print(e)
                    traceback.print_exc()
                    print('error occurred, continue...')
                    # 使用adb关闭该应用的进程
                    execute_cmd_with_timeout(f"adb shell am force-stop {pkgName}", cwd=cur_path)
                    print(f'kill_app.sh in dynamic_run exception..,kill {pkgName}')
                    time.sleep(2)
        # os.chdir(cur_path)
        print('finish get_privacy_policy at {}...'.format(time.ctime()))
        apps_folders = os.listdir(os.path.join(cur_path, 'AppUIAutomator2Navigation', 'collectData'))
        app_dict = {}
        pkgName_appName_dict = {}
        # 保存包名/应用名键值对到字典中
        for pkgName_appName in pkgName_appName_list:
            pkgName, appName = pkgName_appName.split(' | ')
            appName = appName.strip('\'')
            pkgName_appName_dict[pkgName] = appName

        # 改为从AppUIAutomator2Navigation中获取应用名
        # with open('./AppUIAutomator2Navigation/apk_pkgName.txt', 'r', encoding='utf-8') as f:
        with open(os.path.join(cur_path, 'AppUIAutomator2Navigation', 'apk_pkgName.txt'), 'r', encoding='utf-8') as f:
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
        # 成功找到隐私政策URL的app数量
        cnt_pp_num = 0
        # 此时需要读取successful_analysis_pp.txt的记录,看哪些是成功请求到了的URL,这里就不再分析
        # 但是没有请求成功的,这里还要继续尝试
        # 由于存在运行时间过短的可能性，这时successful_analysis_pp.txt可能压根没有产生
        try:
            with open(os.path.join(cur_path, 'AppUIAutomator2Navigation', 'successful_analysis_pp.txt'), 'r',
                      encoding='utf-8') as f:
                content = f.readlines()
            successful_pp_set = set([item.rstrip('\n') for item in content])
        except FileNotFoundError:
            successful_pp_set = set()

        for key, val in app_dict.items():
            # dirs = os.listdir('./AppUIAutomator2Navigation/collectData' + '/' + val)
            dirs = os.listdir(os.path.join(cur_path, 'AppUIAutomator2Navigation', 'collectData', val))
            if 'PrivacyPolicy' in dirs:
                cnt_pp_num += 1
            if 'PrivacyPolicy' not in dirs:
                print('privacy policy not in ', val)
                apps_missing_pp.add(key)
                continue
            # 由于引入了使用守护线程检测是否获取到隐私政策以及在消费者方法中实现了调用隐私政策解析模块,原本设想这一分支暂时不需要调用,以免造成重复调用
            # 如果这个隐私政策URL没有在守护线程中成功分析,也需要再次分析
            elif key not in successful_pp_set and 'PrivacyPolicy' in dirs:
                print('There may be not enough time for subprocess to analysis privacy policy in dynamic part, '
                      'so analysis again.')
                # 找到了隐私政策,修改此处逻辑，判断是否有多行，有多行返回列表；只有一行返回字符串
                # pp_file = os.listdir('./AppUIAutomator2Navigation/collectData' + '/' + val + '/PrivacyPolicy/')[
                #     0]
                pp_file = \
                    os.listdir(
                        os.path.join(cur_path, 'AppUIAutomator2Navigation', 'collectData', val, 'PrivacyPolicy'))[0]
                # with open(
                #         './AppUIAutomator2Navigation/collectData' + '/' + val + '/PrivacyPolicy/' + pp_file, 'r',
                #         encoding='utf-8') as f:
                #         os.path.join(cur_path, 'AppUIAutomator2Navigation','collectData',val,'PrivacyPolicy',pp_file)
                with open(os.path.join(cur_path, 'AppUIAutomator2Navigation', 'collectData', val, 'PrivacyPolicy',
                                       str(pp_file)), 'r', encoding='utf-8') as f:
                    content = f.readlines()
                    content = [item.strip('\n') for item in content]
                    print('content in txt file of PrivacyPolicy', content)
                    pp_url = content
                    print('pp_url:', pp_url)
                    if len(pp_url) == 1:
                        if 'html' in pp_url[0]:
                            app_pp[key] = [pp_url[0][:pp_url[0].index('html') + 4]][:]
                        elif 'htm' in pp_url[0]:
                            app_pp[key] = [pp_url[0][:pp_url[0].index('htm') + 3]][:]
                        else:
                            if pp_url[0].endswith('.1.1'):
                                # 只有这一个结果，还是不合格的，视为没找到隐私政策
                                print('privacy policy not in ', val)
                                apps_missing_pp.add(key)
                            else:
                                app_pp[key] = pp_url[:]
                    elif len(pp_url) > 1:
                        app_pp[key] = pp_url[:]

        # 对app_pp和app_set集合做差集，得到缺失隐私政策的app
        # apps_missing_pp = app_set - set(app_pp.keys())
        # with open('dynamic_apps_missing_pp_url.txt', 'w', encoding='utf8') as f:
        with open(os.path.join(cur_path, 'dynamic_apps_missing_pp_url.txt'), 'w', encoding='utf8') as f:
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
                # with open('apps_still_missing_pp_urls.txt', 'w', encoding='utf-8') as f:
                with open(os.path.join(cur_path, 'apps_still_missing_pp_urls.txt'), 'w', encoding='utf-8') as f:
                    for item in missing_urls:
                        f.write(item)
                        f.write('\n')
        # app_pp 中存放隐私政策url和包名
        # 将最终输出给隐私政策分析模块的文件修改为 包名:[应用名，[url列表]]的形式
        for key, val in app_pp.items():
            if type(val) == list:
                app_pp[key] = [pkgName_appName_dict[key], val]
            else:
                app_pp[key] = [pkgName_appName_dict[key], [val]]

        # with open('./Privacy-compliance-detection-2.1/core/pkgName_url.json', 'w', encoding='utf-8') as f:
        with open(os.path.join(cur_path, 'Privacy-compliance-detection-2.1', 'core', 'pkgName_url.json'), 'w',
                  encoding='utf-8') as f:
            json.dump(app_pp, f, indent=4, ensure_ascii=False)
        print('app_pp', app_pp)
        # 如果成功请求数量小于成功获取到隐私政策URL的应用数量,或者有些app未能hook到隐私政策,也需要再次启动隐私政策解析模块
        if config_settings['analysis_privacy_policy'] == 'true' and (
                len(apps_missing_pp) > 0 or cnt_pp_num != len(successful_pp_set)):
            print('start analysis_privacy_policy at {}...'.format(time.ctime()))
            analysis_privacy_policy(total_apks_to_analysis, os_type, cur_path, log_folder_path)
            print('end analysis_privacy_policy at {}...'.format(time.ctime()))
    # os.chdir(cur_path)


# 隐私政策分析模块
def analysis_privacy_policy(total_apks_to_analysis, os_type, cur_path, log_folder_path):
    print('start analysis_privacy_policy at {}...'.format(time.ctime()))
    stdout_file = log_folder_path + 'analysis_privacy_policy_output.log'
    stderr_file = log_folder_path + 'analysis_privacy_policy_error.log'
    # os.chdir('./Privacy-compliance-detection-2.1/core')
    # 删除调用前清空之前结果的逻辑
    # if 'Privacypolicy_txt' in os.listdir(os.path.join(cur_path, 'Privacy-compliance-detection-2.1', 'core')):
    #     clear_all_files_in_folder(
    #         os.path.join(cur_path, 'Privacy-compliance-detection-2.1', 'core', 'Privacypolicy_txt'))
    # if 'PrivacyPolicySaveDir' in os.listdir(os.path.join(cur_path, 'Privacy-compliance-detection-2.1', 'core')):
    #     clear_all_files_in_folder(
    #         os.path.join(cur_path, 'Privacy-compliance-detection-2.1', 'core', 'PrivacyPolicySaveDir'))
    if 'Privacypolicy_txt' not in os.listdir(os.path.join(cur_path, 'Privacy-compliance-detection-2.1', 'core')):
        os.mkdir(os.path.join(cur_path, 'Privacy-compliance-detection-2.1', 'core', 'Privacypolicy_txt'))
    if 'PrivacyPolicySaveDir' not in os.listdir(os.path.join(cur_path, 'Privacy-compliance-detection-2.1', 'core')):
        os.mkdir(os.path.join(cur_path, 'Privacy-compliance-detection-2.1', 'core', 'PrivacyPolicySaveDir'))
    try:
        if os_type == 'win':
            # execute_cmd_with_timeout('python privacy-policy-main.py', timeout=total_apks_to_analysis * 600,cwd=os.path.join(cur_path, 'Privacy-compliance-detection-2.1', 'core'))
            with open(stdout_file, "a") as stdout, open(stderr_file, "a") as stderr:
                subprocess.run(['python', 'privacy-policy-main.py'],
                               cwd=os.path.join(cur_path, 'Privacy-compliance-detection-2.1', 'core'),
                               timeout=total_apks_to_analysis * 600, stdout=stdout, stderr=stderr)
        elif os_type in ['linux', 'mac']:
            # execute_cmd_with_timeout('python3 privacy-policy-main.py', timeout=total_apks_to_analysis * 600,cwd=os.path.join(cur_path, 'Privacy-compliance-detection-2.1', 'core'))
            with open(stdout_file, "a") as stdout, open(stderr_file, "a") as stderr:
                subprocess.run(['python3', 'privacy-policy-main.py'],
                               cwd=os.path.join(cur_path, 'Privacy-compliance-detection-2.1', 'core'),
                               timeout=total_apks_to_analysis * 600, stdout=stdout, stderr=stderr)
    except UnboundLocalError:
        print('隐私政策解析失败，continue。。。')
    # os.chdir(cur_path)
    print('end analysis_privacy_policy at {}...'.format(time.ctime()))


# 静态UI分析模块
def static_UI_analysis(total_apks_to_analysis, config_settings, os_type, cur_path, log_folder_path):
    print('start static_UI_analysis at {}...'.format(time.ctime()))
    stdout_file = log_folder_path + 'static_UI_analysis_output.log'
    stderr_file = log_folder_path + 'static_UI_analysis_error.log'
    if config_settings['run_ui_static'] == 'true':
        # os.chdir('./context_sensitive_privacy_data_location')
        if 'tmp-output' in os.listdir(os.path.join(cur_path, 'context_sensitive_privacy_data_location')):
            # shutil.rmtree('tmp-output')
            # os.mkdir('tmp-output')
            # 同理，不直接使用rmtree
            if config_settings['clear_tmp_output_dir_before_run'] == 'true':
                clear_all_files_in_folder(
                    os.path.join(cur_path, 'context_sensitive_privacy_data_location', 'tmp-output'))
        if 'tmp-output' not in os.listdir(os.path.join(cur_path, 'context_sensitive_privacy_data_location')):
            # os.mkdir('tmp-output')
            os.mkdir(os.path.join(cur_path, 'context_sensitive_privacy_data_location', 'tmp-output'))
        if 'final_res_log_dir' in os.listdir(os.path.join(cur_path, 'context_sensitive_privacy_data_location')):
            # shutil.rmtree('final_res_log_dir')
            # os.mkdir('final_res_log_dir')
            # 同理，不直接使用rmtree
            # clear_all_files_in_folder('./final_res_log_dir')
            if config_settings['clear_final_res_dir_before_run'] == 'true':
                clear_all_files_in_folder(
                    os.path.join(cur_path, 'context_sensitive_privacy_data_location', 'final_res_log_dir'))
        if 'final_res_log_dir' not in os.listdir(os.path.join(cur_path, 'context_sensitive_privacy_data_location')):
            # os.mkdir('final_res_log_dir')
            os.mkdir(os.path.join(cur_path, 'context_sensitive_privacy_data_location', 'final_res_log_dir'))
        if os_type == 'win':
            # execute_cmd_with_timeout('python run_jar.py', total_apks_to_analysis * 600)
            # execute_cmd_with_timeout('python run_UI_static.py')
            with open(stdout_file, "a") as stdout, open(stderr_file, "a") as stderr:
                subprocess.run(['python', 'run_jar.py'],
                               cwd=os.path.join(cur_path, 'context_sensitive_privacy_data_location'),
                               timeout=total_apks_to_analysis * 1200, stdout=stdout, stderr=stderr)
                subprocess.run(['python', 'run_UI_static.py'],
                               cwd=os.path.join(cur_path, 'context_sensitive_privacy_data_location'),
                               timeout=total_apks_to_analysis * 1200, stdout=stdout, stderr=stderr)
        elif os_type in ['linux', 'mac']:
            # execute_cmd_with_timeout('python3 run_jar.py', total_apks_to_analysis * 600)
            # print('execute python3 run_UI_static.py ....')
            # execute_cmd_with_timeout('python3 run_UI_static.py')
            # print('execute run_UI_static over...')
            with open(stdout_file, "a") as stdout, open(stderr_file, "a") as stderr:
                subprocess.run(['python3', 'run_jar.py'],
                               cwd=os.path.join(cur_path, 'context_sensitive_privacy_data_location'),
                               timeout=total_apks_to_analysis * 600, stdout=stdout, stderr=stderr)
                subprocess.run(['python3', 'run_UI_static.py'],
                               cwd=os.path.join(cur_path, 'context_sensitive_privacy_data_location'),
                               timeout=total_apks_to_analysis * 600, stdout=stdout, stderr=stderr)
        # os.chdir(cur_path)
    print('end static_UI_analysis at {}...'.format(time.ctime()))


# 动态APP测试模块，可能不会运行
def dynamic_app_test(config_settings, cur_path, os_type, log_folder_path):
    stdout_file = log_folder_path + 'dynamic_app_test_output.log'
    stderr_file = log_folder_path + 'dynamic_app_test_error.log'
    print('start dynamic_app_test at {}...'.format(time.ctime()))
    if config_settings['run_dynamic_part'] == 'true' and config_settings[
        'searchprivacypolicy'] == 'true':
        print('this module has been run before...')
    elif config_settings['run_dynamic_part'] == 'true' and config_settings[
        'searchprivacypolicy'] == 'false':
        print(
            "config_settings['run_dynamic_part'] == 'true' and config_settings['searchprivacypolicy'] == 'false'")
        # os.chdir('./AppUIAutomator2Navigation')
        # with open('apk_pkgName.txt', 'r', encoding='utf-8') as f:
        # 检查是否有上次运行时留下的记录
        if 'successful_analysis_pp.txt' in os.listdir(os.path.join(cur_path, 'AppUIAutomator2Navigation')):
            os.remove(os.path.join(cur_path, 'AppUIAutomator2Navigation', 'successful_analysis_pp.txt'))
        with open(os.path.join(cur_path, 'AppUIAutomator2Navigation', 'apk_pkgName.txt'), 'r', encoding='utf-8') as f:
            content = f.readlines()
        pkgName_appName_list = [item.rstrip('\n') for item in content]
        for pkgName_appName in pkgName_appName_list:
            try:
                pkgName, appName = pkgName_appName.split(' | ')
                appName = appName.strip('\'')
                if config_settings['clear_cache'] == 'true':
                    clear_app_cache(pkgName)
                if config_settings['rerun_uiautomator2'] == 'true':
                    rerun_uiautomator2()
                # 判断操作系统版本,分win和linux/mac
                if os_type in ['linux', 'mac']:
                    # 重启frida
                    if config_settings['start_frida'] == 'true':
                        try:
                            execute_cmd_with_timeout("bash start_frida15.sh", timeout=10)
                        except Exception:
                            print("start frida done.")
                    with open(stdout_file, "w") as stdout, open(stderr_file, "w") as stderr:
                        subprocess.run(["python3", "run.py", pkgName, appName, config_settings['dynamic_ui_depth'],
                                        config_settings['dynamic_run_time'], config_settings['searchprivacypolicy'],
                                        config_settings['drawappcallgraph'], config_settings['screenuidrep']],
                                       cwd=os.path.join(cur_path, 'AppUIAutomator2Navigation'),
                                       timeout=int(config_settings['dynamic_run_time']) + 600, stdout=stdout,
                                       stderr=stderr)
                    # execute_cmd_with_timeout(
                    #     'python3 run.py {} {} {} {}'.format(pkgName, appName, config_settings['dynamic_ui_depth'],
                    #                                         config_settings['dynamic_run_time']),
                    #     timeout=int(config_settings['dynamic_run_time']),cwd=os.path.join(cur_path, 'AppUIAutomator2Navigation'))
                else:
                    # 重启frida
                    if config_settings['start_frida'] == 'true':
                        try:
                            execute_cmd_with_timeout("powershell.exe .\\start_frida15.ps1", timeout=10)
                        except Exception:
                            print("start frida done.")
                    # execute_cmd_with_timeout(
                    #     'python run.py {} {} {} {}'.format(pkgName, appName, config_settings['dynamic_ui_depth'],
                    #                                        config_settings['dynamic_run_time']),
                    #     timeout=int(config_settings['dynamic_run_time']),cwd=os.path.join(cur_path, 'AppUIAutomator2Navigation'))

                    with open(stdout_file, "w") as stdout, open(stderr_file, "w") as stderr:
                        subprocess.run(["python", "run.py", pkgName, appName, config_settings['dynamic_ui_depth'],
                                        config_settings['dynamic_run_time'], config_settings['searchprivacypolicy'],
                                        config_settings['drawappcallgraph'], config_settings['screenuidrep']],
                                       cwd=os.path.join(cur_path, 'AppUIAutomator2Navigation'),
                                       timeout=int(config_settings['dynamic_run_time']) + 600, stdout=stdout,
                                       stderr=stderr)
                # 运行结束后，使用adb关闭该应用的进程
                execute_cmd_with_timeout(f"adb shell am force-stop {pkgName}", cwd=cur_path)
                print(f'kill_app.sh in dynamic_run try..,kill {pkgName}')
                time.sleep(2)
            except Exception as e:
                print(e)
                traceback.print_exc()
                # 运行结束后，使用adb关闭该应用的进程
                print('error occurred, continue...')
                execute_cmd_with_timeout(f"adb shell am force-stop {pkgName}", cwd=cur_path)
                print(f'kill_app.sh in dynamic_run exception..,kill {pkgName}')
                time.sleep(2)
        # os.chdir(cur_path)
    else:
        print('did not execute ui_dynamic...')
        print(config_settings['run_dynamic_part'], config_settings['get_pp_from_dynamically_running_app'])
    print('end dynamic_app_test at {}...'.format(time.ctime()))


# 输出最终log
def printFinalLog(os_type, config_settings, total_apks, cur_path):
    print(f'Now at printFinalLog, at {os.getcwd()}')
    print('start printFinalLog at {}...'.format(time.ctime()))
    # print(os_type,config_settings)
    os.chdir('./context_sensitive_privacy_data_location')
    print(f'after os.chdir,now at {os.getcwd()}...')
    if config_settings['run_code_inspection'] == 'true':
        if os_type == 'win':
            execute_cmd_with_timeout('python report_data_in_pp_and_program.py', timeout=total_apks_to_analysis * 600,
                                     cwd=os.path.join(cur_path, 'Privacy-compliance-detection-2.1', 'core'))
        elif os_type in ['linux', 'mac']:
            execute_cmd_with_timeout('python3 report_data_in_pp_and_program.py', timeout=total_apks_to_analysis * 600,
                                     cwd=os.path.join(cur_path, 'Privacy-compliance-detection-2.1', 'core'))
    if os_type == 'win':
        execute_cmd_with_timeout('python get_dynamic_res.py', timeout=total_apks * 600)
    elif os_type in ['linux', 'mac']:
        execute_cmd_with_timeout('python3 get_dynamic_res.py', timeout=total_apks * 600)
    # integrate(config_settings)
    # 保存字典config_settings,然后让integrate log读取
    with open('config_settings.pkl', 'wb') as f:
        pickle.dump(config_settings, f, pickle.HIGHEST_PROTOCOL)

    if os_type == 'win':
        execute_cmd_with_timeout('python integrate_log.py', timeout=total_apks * 600)
    elif os_type in ['linux', 'mac']:
        execute_cmd_with_timeout('python3 integrate_log.py', timeout=total_apks * 600)
    # os.chdir(cur_path)
    # 把最终结果放在./privacy_compliance目录下,方便查看
    if os.path.exists("../final_res_log_dir"):
        shutil.rmtree("../final_res_log_dir")
    shutil.copytree("./final_res_log_dir", "../final_res_log_dir")
    print('end printFinalLog at {}...'.format(time.ctime()))


if __name__ == '__main__':
    # code_inspection 最先执行，可以和 获取隐私政策部分、静态UI分析、动态测试 并行执行，分析隐私政策部分 必须在 获取隐私政策 后才能执行
    # 即可以并行的部分：run_code_inspection、 get_privacy_policy、 static_UI_analysis、 dynamic_app_test,
    # 分析隐私政策放在get_privacy_policy方法的最末尾,整理最终log需要放在最后，顺序执行
    # 初始化放在最前，不和其他部分并行

    # 初始化
    config_settings, cur_path, apk_path, os_type, total_apks_to_analysis, log_folder_path = initSettings()
    if config_settings['multi-thread'] == 'no':
        # 不使用多线程，串行执行
        # 运行code_inspection
        run_code_inspection(cur_path, total_apks_to_analysis, os_type, log_folder_path, config_settings)
        # 获取隐私政策
        get_privacy_policy(os_type, config_settings, cur_path, total_apks_to_analysis, log_folder_path)
        # 静态UI分析
        static_UI_analysis(total_apks_to_analysis, config_settings, os_type, cur_path, log_folder_path)
        # 动态测试
        dynamic_app_test(config_settings, cur_path, os_type, log_folder_path)

        # 分析隐私政策
        analysis_privacy_policy(total_apks_to_analysis, os_type, cur_path, log_folder_path)

        # 整理最终log
        printFinalLog(os_type, config_settings, total_apks_to_analysis, cur_path)
    elif config_settings['multi-thread'] == 'low':
        # 同时允许两个组件并行执行
        # 创建线程
        threads = []

        # 创建并启动线程1：run_code_inspection
        thread1 = threading.Thread(target=run_code_inspection,
                                   args=(cur_path, total_apks_to_analysis, os_type, log_folder_path, config_settings))
        # threads.append(thread1)
        thread1.start()

        # 创建并启动线程2：get_privacy_policy
        # 睡眠5s，以确保apk_pkgName.txt里的数据更新
        time.sleep(5)
        thread2 = threading.Thread(target=get_privacy_policy,
                                   args=(os_type, config_settings, cur_path, total_apks_to_analysis, log_folder_path))
        threads.append(thread2)
        thread2.start()

        # 创建并启动线程4：dynamic_app_test
        thread4 = threading.Thread(target=dynamic_app_test, args=(config_settings, cur_path, os_type, log_folder_path))
        threads.append(thread4)
        thread4.start()

        # 等待code_inspection线程结束
        thread1.join()
        # 创建并启动线程3：static_UI_analysis
        thread3 = threading.Thread(target=static_UI_analysis,
                                   args=(total_apks_to_analysis, config_settings, os_type, cur_path, log_folder_path))
        threads.append(thread3)
        thread3.start()
        # 等待所有线程完成
        for thread in threads:
            thread.join()

        # 执行整理最终log
        printFinalLog(os_type, config_settings, total_apks_to_analysis, cur_path)

    elif config_settings['multi-thread'] == 'high':
        # 同时允许三个组件并行执行
        # 创建线程
        threads = []

        # 创建并启动线程1：run_code_inspection
        thread1 = threading.Thread(target=run_code_inspection,
                                   args=(cur_path, total_apks_to_analysis, os_type, log_folder_path, config_settings))
        threads.append(thread1)
        thread1.start()

        # 创建并启动线程2：get_privacy_policy
        # 睡眠5s，以确保apk_pkgName.txt里的数据更新
        time.sleep(5)
        thread2 = threading.Thread(target=get_privacy_policy,
                                   args=(os_type, config_settings, cur_path, total_apks_to_analysis, log_folder_path))
        threads.append(thread2)
        thread2.start()

        # 创建并启动线程3：static_UI_analysis
        thread3 = threading.Thread(target=static_UI_analysis,
                                   args=(total_apks_to_analysis, config_settings, os_type, cur_path, log_folder_path))
        threads.append(thread3)
        thread3.start()

        # 创建并启动线程4：dynamic_app_test
        thread4 = threading.Thread(target=dynamic_app_test, args=(config_settings, cur_path, os_type, log_folder_path))
        threads.append(thread4)
        thread4.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()
        # 执行整理最终log
        printFinalLog(os_type, config_settings, total_apks_to_analysis, cur_path)
