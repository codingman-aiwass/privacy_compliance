import configparser
import platform
import subprocess
import re
import os
import shutil

def check_nvidia_driver_installed():
    try:
        # 执行命令 "nvidia-smi" 并捕获输出结果
        result = subprocess.run(['nvidia-smi'], capture_output=True)
        output = result.stdout.decode()

        # 如果输出结果包含 "NVIDIA" 字符串，则说明安装了NVIDIA驱动
        if 'NVIDIA' in output:
            return True
        else:
            return False
    except FileNotFoundError:
        # 如果命令 "nvidia-smi" 不存在，则说明未安装NVIDIA驱动
        return False


def prepareADB():
    # 调用命令行程序并获取输出
    command = "adb shell ip -f inet addr show wlan0"
    output = subprocess.check_output(command, shell=True).decode("utf-8")

    # 使用正则表达式提取需要的字符串
    pattern = r"inet (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
    match = re.search(pattern, output)
    if match:
        ip_address = match.group(1)

        # 将提取的字符串写入文件
        with open("IP.txt", "w") as file:
            file.write(ip_address + ':12005')
    commands = [
        f'adb tcpip 12005',
        f'adb connect {ip_address}:12005',
        f'adb kill-server'
    ]
    for command in commands:
        subprocess.run(command, shell=True)


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


def determine_host_os_type(os_type):
    config = configparser.ConfigParser()
    config.read(
        './docker_result/config.ini')  # Replace 'config.ini' with the path to your INI file

    # Modify the 'apk' setting in the INI file
    config.set('running_settings', 'host_machine_os_type',
               os_type)  # Replace 'section_name' with the appropriate section name in your INI file

    # Save the modified INI file
    with open('./docker_result/config.ini',
              'w') as config_file:  # Replace 'config.ini' with the path to your INI file
        config.write(config_file)
    


if __name__ == '__main__':
    os_type = get_OS_type()
    determine_host_os_type(os_type)
    # 往config.ini中添加host_machine_os_type一项，方便在docker中运行的时候选择不同的prepareInDocker.sh
    if os_type in ['win', 'mac']:
        prepareADB()
        print('run adb kill-server')
        subprocess.run("adb kill-server", shell=True)
    # prepareADB()
    # 复制需要分析的apk文件到apks文件夹里
    elif os_type == 'linux':
        print('run adb kill-server')
        subprocess.run("adb kill-server",shell=True)
    directories = input(
        "please input absolute path of apk(s)/folder(s) contained apk(s),seperated by ; e.g. /Users/apks;/Users/apks/test.apk\n")
    apk_name_set = set()
    curdir = os.getcwd()
    for directory in directories.split(';'):
        if len(directory) > 0:
            if directory.endswith('.apk'):
                apk_name_set.add(directory)
            else:
                for fileName in os.listdir(directory):
                    if fileName.endswith('.apk'):
                        fileName = os.path.join(directory, fileName)
                        apk_name_set.add(fileName)
    # 先检查apks里面有没有本次分析所需要的apk
    apk_name_set_with_only_fileName = set([filePath[filePath.rindex(os.path.sep):] for filePath in apk_name_set])
    delete_apks_not_this_time = set(os.listdir(curdir + os.path.sep + 'apks')) - apk_name_set_with_only_fileName
    # 删除这些apk
    for delete_apk in delete_apks_not_this_time:
        delete_file = curdir + os.path.sep + 'apks' + os.path.sep + delete_apk
        if os.path.isdir(delete_file):
            if os_type in ['linux','mac']:
                subprocess.run(f"rm -rf {delete_file}",shell=True)
            else:
                shutil.rmtree(delete_file)
        else:
            os.remove(delete_file)
    # 将本次需要分析的apk复制到此处
    for apk in apk_name_set:
        fileName = apk[apk.rindex(os.path.sep) + 1:]
        target_path = curdir + os.path.sep + 'apks' + os.path.sep + fileName
        if os.path.exists(target_path):
            continue
        shutil.copyfile(apk, target_path)

    # 判断docker容器是否存在

    # 根据操作系统判断该调用什么命令行启动docker
    # 还要根据该操作系统上是否安装了nvidia显卡判断是否启用GPU
    # 调用函数进行检查
    if check_nvidia_driver_installed():
        print("宿主机已安装NVIDIA显卡驱动")
        win_command = f'docker run -it --name privacy_compliance -v {curdir}/docker_result/logs:/app/logs  -v {curdir}/docker_result/code_inspection_result/logsPath:/app/Privacy-compliance-detection-2.1/core/logsPath -v {curdir}/docker_result/code_inspection_result/ResultSaveDir:/app/Privacy-compliance-detection-2.1/core/ResultSaveDir -v {curdir}/docker_result/code_inspection_result/pp_missing:/app/Privacy-compliance-detection-2.1/core/final_res/pp_missing -v {curdir}/docker_result/dynamic_run_result:/app/AppUIAutomator2Navigation/collectData -v {curdir}/docker_result/privacy_policy_analysis_result:/app/Privacy-compliance-detection-2.1/core/PrivacyPolicySaveDir -v {curdir}/docker_result/static_UI_run_result:/app/context_sensitive_privacy_data_location/tmp-output -v {curdir}/docker_result/final_result:/app/context_sensitive_privacy_data_location/final_res_log_dir -v {curdir}/docker_result/apps_still_missing_pp_urls.txt:/app/docker_result/apps_still_missing_pp_urls.txt -v {curdir}/docker_result/config.ini:/app/config.ini -v {curdir}/docker_result/dynamic_apps_missing_pp_url.txt:/app/dynamic_apps_missing_pp_url.txt -v {curdir}/IP.txt:/app/IP.txt -v {curdir}/prepareInDocker.sh:/app/prepareInDocker.sh -v {curdir}/apks:/app/apks -v {curdir}/run.py:/app/run.py -v {curdir}/run.sh:/app/run.sh --gpus all privacy_compliance_image:v1.0'
        mac_command = f'docker run -it --name privacy_compliance -v {curdir}/docker_result/logs:/app/logs  -v {curdir}/docker_result/code_inspection_result/logsPath:/app/Privacy-compliance-detection-2.1/core/logsPath -v {curdir}/docker_result/code_inspection_result/ResultSaveDir:/app/Privacy-compliance-detection-2.1/core/ResultSaveDir -v {curdir}/docker_result/code_inspection_result/pp_missing:/app/Privacy-compliance-detection-2.1/core/final_res/pp_missing -v {curdir}/docker_result/dynamic_run_result:/app/AppUIAutomator2Navigation/collectData -v {curdir}/docker_result/privacy_policy_analysis_result:/app/Privacy-compliance-detection-2.1/core/PrivacyPolicySaveDir -v {curdir}/docker_result/static_UI_run_result:/app/context_sensitive_privacy_data_location/tmp-output -v {curdir}/docker_result/final_result:/app/context_sensitive_privacy_data_location/final_res_log_dir -v {curdir}/docker_result/apps_still_missing_pp_urls.txt:/app/docker_result/apps_still_missing_pp_urls.txt -v {curdir}/docker_result/config.ini:/app/config.ini -v {curdir}/docker_result/dynamic_apps_missing_pp_url.txt:/app/dynamic_apps_missing_pp_url.txt -v {curdir}/IP.txt:/app/IP.txt -v {curdir}/prepareInDocker.sh:/app/prepareInDocker.sh -v {curdir}/apks:/app/apks -v {curdir}/run.py:/app/run.py -v {curdir}/run.sh:/app/run.sh --gpus all privacy_compliance_image:v1.0'
        linux_command = f'docker run -it --privileged --name privacy_compliance -v /dev/bus/usb:/dev/bus/usb -v {curdir}/docker_result/logs:/app/logs  -v {curdir}/docker_result/code_inspection_result/logsPath:/app/Privacy-compliance-detection-2.1/core/logsPath -v {curdir}/docker_result/code_inspection_result/ResultSaveDir:/app/Privacy-compliance-detection-2.1/core/ResultSaveDir -v {curdir}/docker_result/code_inspection_result/pp_missing:/app/Privacy-compliance-detection-2.1/core/final_res/pp_missing -v {curdir}/docker_result/dynamic_run_result:/app/AppUIAutomator2Navigation/collectData -v {curdir}/docker_result/privacy_policy_analysis_result:/app/Privacy-compliance-detection-2.1/core/PrivacyPolicySaveDir -v {curdir}/docker_result/static_UI_run_result:/app/context_sensitive_privacy_data_location/tmp-output -v {curdir}/docker_result/final_result:/app/context_sensitive_privacy_data_location/final_res_log_dir -v {curdir}/docker_result/apps_still_missing_pp_urls.txt:/app/docker_result/apps_still_missing_pp_urls.txt -v {curdir}/docker_result/config.ini:/app/config.ini -v {curdir}/docker_result/dynamic_apps_missing_pp_url.txt:/app/dynamic_apps_missing_pp_url.txt -v {curdir}/IP.txt:/app/IP.txt -v {curdir}/prepareInDocker.sh:/app/prepareInDocker.sh -v {curdir}/apks:/app/apks -v {curdir}/run.py:/app/run.py -v {curdir}/run.sh:/app/run.sh --gpus all privacy_compliance_image:v1.0'
    else:
        print("宿主机未安装NVIDIA显卡驱动")
        win_command = f'docker run -it --name privacy_compliance -v {curdir}/docker_result/logs:/app/logs  -v {curdir}/docker_result/code_inspection_result/logsPath:/app/Privacy-compliance-detection-2.1/core/logsPath -v {curdir}/docker_result/code_inspection_result/ResultSaveDir:/app/Privacy-compliance-detection-2.1/core/ResultSaveDir -v {curdir}/docker_result/code_inspection_result/pp_missing:/app/Privacy-compliance-detection-2.1/core/final_res/pp_missing -v {curdir}/docker_result/dynamic_run_result:/app/AppUIAutomator2Navigation/collectData -v {curdir}/docker_result/privacy_policy_analysis_result:/app/Privacy-compliance-detection-2.1/core/PrivacyPolicySaveDir -v {curdir}/docker_result/static_UI_run_result:/app/context_sensitive_privacy_data_location/tmp-output -v {curdir}/docker_result/final_result:/app/context_sensitive_privacy_data_location/final_res_log_dir -v {curdir}/docker_result/apps_still_missing_pp_urls.txt:/app/docker_result/apps_still_missing_pp_urls.txt -v {curdir}/docker_result/config.ini:/app/config.ini -v {curdir}/docker_result/dynamic_apps_missing_pp_url.txt:/app/dynamic_apps_missing_pp_url.txt -v {curdir}/IP.txt:/app/IP.txt -v {curdir}/prepareInDocker.sh:/app/prepareInDocker.sh -v {curdir}/apks:/app/apks -v {curdir}/run.py:/app/run.py -v {curdir}/run.sh:/app/run.sh privacy_compliance_image:v1.0'
        mac_command = f'docker run -it --name privacy_compliance -v {curdir}/docker_result/logs:/app/logs  -v {curdir}/docker_result/code_inspection_result/logsPath:/app/Privacy-compliance-detection-2.1/core/logsPath -v {curdir}/docker_result/code_inspection_result/ResultSaveDir:/app/Privacy-compliance-detection-2.1/core/ResultSaveDir -v {curdir}/docker_result/code_inspection_result/pp_missing:/app/Privacy-compliance-detection-2.1/core/final_res/pp_missing -v {curdir}/docker_result/dynamic_run_result:/app/AppUIAutomator2Navigation/collectData -v {curdir}/docker_result/privacy_policy_analysis_result:/app/Privacy-compliance-detection-2.1/core/PrivacyPolicySaveDir -v {curdir}/docker_result/static_UI_run_result:/app/context_sensitive_privacy_data_location/tmp-output -v {curdir}/docker_result/final_result:/app/context_sensitive_privacy_data_location/final_res_log_dir -v {curdir}/docker_result/apps_still_missing_pp_urls.txt:/app/docker_result/apps_still_missing_pp_urls.txt -v {curdir}/docker_result/config.ini:/app/config.ini -v {curdir}/docker_result/dynamic_apps_missing_pp_url.txt:/app/dynamic_apps_missing_pp_url.txt -v {curdir}/IP.txt:/app/IP.txt -v {curdir}/prepareInDocker.sh:/app/prepareInDocker.sh -v {curdir}/apks:/app/apks -v {curdir}/run.py:/app/run.py -v {curdir}/run.sh:/app/run.sh privacy_compliance_image:v1.0'
        # linux端暂时不使用--privileged 方法
        linux_command = f'docker run -it --privileged --name privacy_compliance -v /dev/bus/usb:/dev/bus/usb -v {curdir}/docker_result/logs:/app/logs  -v {curdir}/docker_result/code_inspection_result/logsPath:/app/Privacy-compliance-detection-2.1/core/logsPath -v {curdir}/docker_result/code_inspection_result/ResultSaveDir:/app/Privacy-compliance-detection-2.1/core/ResultSaveDir -v {curdir}/docker_result/code_inspection_result/pp_missing:/app/Privacy-compliance-detection-2.1/core/final_res/pp_missing -v {curdir}/docker_result/dynamic_run_result:/app/AppUIAutomator2Navigation/collectData -v {curdir}/docker_result/privacy_policy_analysis_result:/app/Privacy-compliance-detection-2.1/core/PrivacyPolicySaveDir -v {curdir}/docker_result/static_UI_run_result:/app/context_sensitive_privacy_data_location/tmp-output -v {curdir}/docker_result/final_result:/app/context_sensitive_privacy_data_location/final_res_log_dir -v {curdir}/docker_result/apps_still_missing_pp_urls.txt:/app/docker_result/apps_still_missing_pp_urls.txt -v {curdir}/docker_result/config.ini:/app/config.ini -v {curdir}/docker_result/dynamic_apps_missing_pp_url.txt:/app/dynamic_apps_missing_pp_url.txt -v {curdir}/IP.txt:/app/IP.txt -v {curdir}/prepareInDocker.sh:/app/prepareInDocker.sh -v {curdir}/apks:/app/apks -v {curdir}/run.py:/app/run.py -v {curdir}/run.sh:/app/run.sh privacy_compliance_image:v1.0'
    
    
    # linux_command = f'docker run -it --name privacy_compliance --privileged -v /dev/bus/usb:/dev/bus/usb -v {curdir}/docker_result/code_inspection_result/logsPath:/app/Privacy-compliance-detection-2.1/core/logsPath -v {curdir}/docker_result/code_inspection_result/ResultSaveDir:/app/Privacy-compliance-detection-2.1/core/ResultSaveDir -v {curdir}/docker_result/code_inspection_result/pp_missing:/app/Privacy-compliance-detection-2.1/core/final_res/pp_missing -v {curdir}/docker_result/dynamic_run_result:/app/AppUIAutomator2Navigation/collectData -v {curdir}/docker_result/privacy_policy_analysis_result:/app/Privacy-compliance-detection-2.1/core/PrivacyPolicySaveDir -v {curdir}/docker_result/static_UI_run_result:/app/context_sensitive_privacy_data_location/tmp-output -v {curdir}/docker_result/final_result:/app/context_sensitive_privacy_data_location/final_res_log_dir -v {curdir}/docker_result/apps_still_missing_pp_urls.txt:/app/docker_result/apps_still_missing_pp_urls.txt -v {curdir}/docker_result/config.ini:/app/config.ini -v {curdir}/docker_result/dynamic_apps_missing_pp_url.txt:/app/dynamic_apps_missing_pp_url.txt -v {curdir}/prepareInDocker.sh:/app/prepareInDocker.sh -v {curdir}/apks:/app/apks --gpus all privacy_compliance_image'
    if os_type == 'win':
        subprocess.run('PowerShell.exe .\check_remove_container.ps1',shell=True)
        subprocess.run(win_command, shell=True)
    elif os_type == 'mac':
        subprocess.run("sed -i 's/\r$//' check_remove_container.sh", shell=True)
        subprocess.run("sed -i 's/\r$//' prepareInDocker.sh", shell=True)
        subprocess.run('bash check_remove_container.sh',shell=True)
        subprocess.run(mac_command, shell=True)
        # subprocess.run('exit',shell=True)
    elif os_type == 'linux':
        subprocess.run("sed -i 's/\r$//' check_remove_container.sh", shell=True)
        subprocess.run("sed -i 's/\r$//' prepareInDocker_linux.sh", shell=True)
        subprocess.run('bash check_remove_container.sh',shell=True)
        subprocess.run(linux_command, shell=True)
        # subprocess.run('exit',shell=True)
