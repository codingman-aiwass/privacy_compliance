import os
if 'NVIDIA_VISIBLE_DEVICES' in os.environ:
    os.environ["CUDA_VISIBLE_DEVICES"] = "-1"  # 强制使用cpu
from run_privacypolicy import run_write_json
from url_analysis import run_url_analysis
from compliance_analysis import run_compliance_analysis
def run_handle(filepath):
    filename_list = os.listdir(filepath)
    for i in filename_list:
        if i.endswith(".txt"):
            run_write_json(filepath+"/"+i,"PrivacyPolicySaveDir/"+i[:-4])
            print(i+"已处理完成！")
def main(filename):
    try:
        run_url_analysis(filename)
    except:
        print(filename+"爬取失败")
    run_handle("Privacypolicy_txt")
def delete_privacy_json():
    folder_path = 'PrivacyPolicySaveDir'  # 将 path/to/folder 替换为你的文件夹路径
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.json'):
            file_path = os.path.join(folder_path, file_name)
            os.remove(file_path)
    folder_path = 'Privacypolicy_txt'  # 将 path/to/folder 替换为你的文件夹路径
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.txt'):
            file_path = os.path.join(folder_path, file_name)
            os.remove(file_path)
if __name__ == '__main__':
    #run_handle("D:/中山/ali/privacy policy/ali")
    # delete_privacy_json()
    main("pkgName_url.json")
    run_compliance_analysis()
