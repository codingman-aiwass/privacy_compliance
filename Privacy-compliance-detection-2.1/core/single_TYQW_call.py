# coding: utf-8
import json
import requests
import base64
def test(prompt,privacy_policy_text):
    url = 'http://47.106.173.151:6006/qwen'
    headers = {
        'Content-Type': 'application/json'
    }
    prompt_text_tmp = f"""{prompt}，隐私政策文本：{privacy_policy_text}"""
    data = {'prompt_text': str(base64.b64encode(prompt_text_tmp.encode('utf-8')))}
    response = requests.post(url, data=json.dumps(data, ensure_ascii=True), headers=headers)
    # 获取响应结果
    result = response.text.encode().decode("unicode_escape")

    print('result:\n{}'.format(result))
    return 'result:\n{}'.format(result)
def get_pp_data_text(txt_name):
    text = ""
    if txt_name.endswith('.json'):
        with open("PrivacyPolicySaveDir/"+txt_name, encoding="utf-8")as f:
            data = json.load(f)
        f.close()
        for i in data[1]:
            data_text = data_text +"\n"+i["orig-sentence"]
    #print(data_text)
    return data_text
if __name__ == '__main__':
    # 静态分析拿到的权限在隐私政策中是否被明确声明使用,输出是/不是
    # 监管标准也要.
    txt_name = "UC浏览器.json"
    prompt ="请帮我提取出该隐私政策中声明收集的所有数据，不可省略"
    #get_pp_text(txt_name)
    test(prompt,get_pp_data_text(txt_name))