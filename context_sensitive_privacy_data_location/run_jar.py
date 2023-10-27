import os
import subprocess
import signal
from dealWithInputAndOutput import get_run_jar_settings

############################
# Following parameter need #
# to be change.           ##
############################

# LayoutBuilder jar.
# jar_path = r'H:\PrivacyLegal\testApp\MySootAndroid0707.jar'
jar_path = r'./LayoutBuilder.jar'
# ResourceDecompiler jar.
# decompile_jar_path = r'H:\PrivacyLegal\testApp\MySootAndroidDecompiler.jar'
decompile_jar_path = r'./ResourceDecompiler.jar'
# android sdk path
# android_sdk_path = r'F:\Android\Sdk\platforms'
# android_sdk_path = r'/Users/anran/myfiles/隐私合规/Privacy-compliance-detection-2.0/core/config/androidJar'
# output path
# output_dir = r'H:\Privacy\testOutput0706'
# output_dir = r'./Output0801'
# apk store path

# directory = r'H:\SDKPrivacyLegal\demoApps\googleApps'
# directory = r'/Users/anran/myfiles/隐私合规/apks'

android_sdk_path, output_dir, directories = get_run_jar_settings()


def execute_cmd_with_timeout(cmd, timeout=600):
    p = subprocess.Popen(cmd, stderr=subprocess.STDOUT, shell=True)
    try:
        p.wait(timeout)
    except subprocess.TimeoutExpired:
        p.send_signal(signal.SIGINT)
        p.wait()


def traverse(directory):
    apk_name_list = []
    if directory.endswith('.apk'):
        apk_name_list.append(directory)
    else:
        for fileName in os.listdir(directory):
            if fileName.endswith('.apk'):
                fileName = os.path.join(directory, fileName)
                apk_name_list.append(fileName)

    # run output
    for fileName in apk_name_list:
        print(fileName)
        try:
            # execute_cmd_with_timeout(r'java -jar {} {} {} {}'.format(jar_path, android_sdk_path, "/""+fileName+"/"", r'H:\SDKPrivacyLegal\demoApps\googleApps'))
            execute_cmd_with_timeout(r'java -jar -Xmx16G {} {} {} {}'.format(jar_path, android_sdk_path, fileName, output_dir))
        except Exception as e:
            print(e)

    # decompile apk.
    # for fileName in apk_name_list:
    #     print(fileName)
    #     os.system(r'java -jar {} {}'.format(decompile_jar_path, "\""+fileName+"\""))


# decompile apk.
def traverse_decompile(directory):
    apk_name_list = []
    if directory.endswith('.apk'):
        apk_name_list.append(directory)
    else:
        for fileName in os.listdir(directory):
            if fileName.endswith('.apk') and fileName[:-4] + '_decompile' not in os.listdir():
                fileName = os.path.join(directory, fileName)
                apk_name_list.append(fileName)

    for fileName in apk_name_list:
        print(fileName)
        if not os.path.exists(fileName[:-4] + '_decompile'):
            os.system(r'java -jar -Xmx8G {} {}'.format(decompile_jar_path, fileName))


# run output
def traverse_output(directory):
    apk_name_list = []
    if directory.endswith('.apk'):
        apk_name_list.append(directory)
    else:
        for fileName in os.listdir(directory):
            if fileName.endswith('.apk'):
                fileName = os.path.join(directory, fileName)
                apk_name_list.append(fileName)

    for fileName in apk_name_list:
        print(fileName)
        try:
            execute_cmd_with_timeout(r'java -jar -Xmx8G {} {} {} {}'.format(jar_path, android_sdk_path, fileName, output_dir))
        except Exception as e:
            print(e)


if __name__ == '__main__':
    print(directories)
    for directory in directories.split(';'):
        if len(directory) > 0:
            traverse_decompile(directory)
            traverse(directory)
