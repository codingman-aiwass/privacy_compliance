import os
import platform
import subprocess
import re

from configobj import ConfigObj


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

if __name__ == '__main__':
    # 读取RunningConfig.properties里的apk，找到本次分析的apk
    # Modify the properties file
    if 'permissions' not in os.listdir():
        os.mkdir('permissions')
    os_type = get_OS_type()
    if os_type == 'win':
        base_command = 'aapt d badging '
    else:
        base_command = './aapt d badging '
    props = ConfigObj('RunningConfig.properties', encoding='UTF8')
    total_apks = set()
    apk_or_folders = props['apk'].split(';')
    for item in apk_or_folders:
        if item.endswith('.apk'):
            total_apks.add(item)
        else:
            if os.path.isdir(item):
                files_in_item = os.listdir(item)
                for inner_apk in files_in_item:
                    if inner_apk.endswith('.apk'):
                        total_apks.add(item + '/' + inner_apk)
    # 执行命令行程序并获取输出
    for apk in total_apks:
        command = base_command + apk
        output = subprocess.check_output(command, shell=True, text=True,cwd=os.path.dirname(props['aapt']))
        # 提取package名称
        package_name = re.search(r"package: name='([^']+)'", output).group(1)
        # 提取users-permission行
        permissions = [line.lstrip('uses-permission: name=').strip("'") for line in output.split('\n') if line.startswith('uses-permission')]

        # 将提取的行保存到txt文件
        with open(f'permissions/{package_name}.txt', 'w') as file:
            file.write('\n'.join(permissions))