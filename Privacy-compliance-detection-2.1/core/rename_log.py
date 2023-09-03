import os
import json


def rename():
    with open("Dict/包名.json", 'r', encoding='utf-8') as f:
        ch_name_list = json.load(f)
    path = "PrivacyPolicySaveDir"
    if os.listdir(path):
        for filename in os.listdir(path):
            if filename.endswith(".json"):
                flag = 0
                old_name = os.path.join(path, filename)
                print(old_name)
                for ch in ch_name_list:
                    try:
                        if ch["app"] in filename:
                            new_filename = ch["app"] + ".json"
                            new_name = os.path.join(path, new_filename)
                            print(new_name)
                            try:
                                os.rename(old_name, new_name)
                            except Exception as e:
                                print(e)
                            flag = 1
                            break
                    except:
                        for c in ch["app"]:
                            if c in filename:
                                new_filename = ch["app"][0] + ".json"
                                new_name = os.path.join(path, new_filename)
                                try:
                                    os.rename(old_name, new_name)
                                except Exception as e:
                                    print(e)
                                flag = 1
                                break
                if flag == 0:
                    with open(path + "/" + filename, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    f.close()
                    for ch in ch_name_list:
                        json_str = json.dumps(data, ensure_ascii=False)
                        try:
                            if ch["app"] in json_str:
                                new_filename = ch["app"] + ".json"
                                new_name = os.path.join(path, new_filename)
                                try:
                                    os.rename(old_name, new_name)
                                except Exception as e:
                                    print(e)
                                break
                        except:
                            continue

if __name__ == '__main__':
    rename()