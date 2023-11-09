import json
import os
from run_privacypolicy import run_write_json
from url_analysis import run_url_analysis
from compliance_analysis import run_compliance_analysis
import time
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
def sdk_hebing():
    folder_path = 'PrivacyPolicySaveDir'  # 将 path/to/folder 替换为你的文件夹路径
    for file_name in os.listdir(folder_path):
        if file_name.endswith('sdk.json'):
            try:
                with open(folder_path+"/"+file_name,'r',encoding='utf-8')as f:
                    sdk_data = json.load(f)
                f.close()
                with open(folder_path+"/"+file_name[:-9]+".json",'r',encoding='utf-8')as f:
                    all =json.load(f)
                f.close()
                all.append(sdk_data)
                with open(folder_path+"/"+file_name[:-9]+".json",'w',encoding='utf-8')as f:
                    json.dump(all, f, ensure_ascii=False, indent=2)
                f.close()
                file_path = os.path.join(folder_path, file_name)
                os.remove(file_path)
            except:
                pass
if __name__ == '__main__':
    #run_handle("D:/中山/ali/privacy policy/ali")
    start_time = time.time()
    delete_privacy_json()
    main("pkgName_url(1).json")
    run_compliance_analysis()
    end_time = time.time()
    total_time = end_time - start_time
    sdk_hebing()
    print("程序运行时间：", total_time, "秒")
