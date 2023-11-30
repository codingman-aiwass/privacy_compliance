import json
import os
import sys

from run_privacypolicy import run_write_json
from url_analysis import run_url_analysis
from compliance_analysis import run_compliance_analysis
def run_handle(filepath,only_analysis_pkgName_url = 'n'):
    filename_list = os.listdir(filepath)
    apps = set(filename_list)
    if only_analysis_pkgName_url == 'y':
        try:
            with open('pkgName_url.json', 'r', encoding='utf8') as f:
                json_file = json.load(f)
                apps = set(json_file.keys())
        except FileNotFoundError:
            # 找不到pkgName_url.json的话，就按原本的方法进行。。
            print('no pkgName_url.json, fail to analysis...')

    for i in filename_list:
        if i.endswith(".txt") and (i[:-4] in apps or i in apps):
            run_write_json(filepath+"/"+i,"PrivacyPolicySaveDir/"+i[:-4])
            print(i+"已处理完成！")

def main(filename,only_analysis_pkgName_url = 'n'):
    run_url_analysis(filename)
    if only_analysis_pkgName_url == 'n':
        run_handle("Privacypolicy_txt")
    else:
        run_handle("Privacypolicy_txt",'y')

def delete_privacy_json():
    folder_path = 'Privacypolicy_txt'
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.txt'):
            file_path = os.path.join(folder_path, file_name)
            os.remove(file_path)
if __name__ == '__main__':
    # 添加一个参数，在守护线程中调用这个模块的话，只分析pkgName_url.json里的app的隐私政策，而不是分析Privacypolicy_txt里的所有隐私政策
    try:
        only_analysis_pkgName_url = sys.argv[1]
        main("pkgName_url.json",'y')
        run_compliance_analysis('y')
    except IndexError:
        # 采用默认情况
        print('no args input.')
        delete_privacy_json()
        main("pkgName_url.json")
        run_compliance_analysis()

    #run_handle("D:/中山/ali/privacy policy/ali")
    # delete_privacy_json()