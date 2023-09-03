# -*- coding: utf-8 -*-
import re
import json
from alibabacloud_alimt20181012.client import Client as alimt20181012Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_alimt20181012 import models as alimt_20181012_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient
ACCESS_KEY_ID = "LTAI5tH3Wa7UafkbDAn6ang1"
ACCESS_KEY_SECRET = "zjj6AS82Z5dBdffY3SSsgnuodE1GUS"
def create_client(
        access_key_id: str,
        access_key_secret: str,
) -> alimt20181012Client:
        config = open_api_models.Config(
            access_key_id=access_key_id,
            access_key_secret=access_key_secret
        )
        config.endpoint = f'mt.cn-hangzhou.aliyuncs.com'
        return alimt20181012Client(config)
def _translate(text):
    client = create_client(ACCESS_KEY_ID, ACCESS_KEY_SECRET)
    translate_general_request = alimt_20181012_models.TranslateGeneralRequest(
            format_type='text',
            source_language='zh',
            target_language='en',
            scene='general',
            source_text= text
        )
    try:
        runtime = util_models.RuntimeOptions()
        # 复制代码运行请自行打印 API 的返回值
        text_trans = client.translate_general_with_options(translate_general_request, runtime)
        return text_trans.body.data.__dict__['translated']
    except Exception as error:
        UtilClient.assert_as_string(error.message)
        return ""
def run_translate(text_list):
    ch_en_dict = {}
    if text_list:
        en_text = _translate(",".join((text_list)))
        en_list = re.split(r'[,，]',en_text)
        if len(text_list) ==  len(en_list):
            for i in range(0,len(text_list)):
                ch_en_dict[text_list[i]] = en_list[i]
        return en_list,ch_en_dict
    else:
        return [],ch_en_dict
def run_data_translate(data_cn,data_json_name):
    #data_en :str
    with open(data_json_name,'r',encoding='UTF-8') as f:
        data_dict_list = json.load(f)
    f.close()
    data_en = None
    for da_dict in data_dict_list:
        if da_dict['data-cn'] == data_cn:
            data_en = da_dict['data-en']
    return data_en
def run_data_translate2(data_cn,data_json_name):
    #data_en: list
    with open(data_json_name,'r',encoding='UTF-8') as f:
        data_dict_list = json.load(f)
    f.close()
    data_en = []
    for da_dict in data_dict_list:
        if da_dict['data-cn'] == data_cn:
            data_en = da_dict['data-en'][:]
            return data_en
    return data_en