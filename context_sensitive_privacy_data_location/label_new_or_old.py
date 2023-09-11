# -*- coding: UTF-8 -*-
import json
import sys
from dealWithInputAndOutput import get_input_args
dict_word_set = set()


def generate_dict_word():
    '''
    Generate keywords list.
    Store in `dict_word_set`.
    :return:
    '''
    with open(r'./PrivacyDataItem.csv', 'r', encoding='utf-8') as f:
        line = f.readline()
        while line:
            dict_word_set.add(line.strip())
            line = f.readline()


def label_new_or_old(input_file, output_file):
    """
    Label the result in filtered result.
    The word occured in `dict_word_set` is old.
    :param input_file: the filtered result.
    :param output_file: the output file path to store the labeled result.
    """
    generate_dict_word()

    with open(input_file, 'r', encoding='utf-8') as f:
        filtered_res = json.load(f)
    for text_object in filtered_res['outputObjects']:
        if text_object['text'] in dict_word_set:
            text_object['label'] = 'old'
        else:
            text_object['label'] = 'new'

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(filtered_res, f, indent=2, ensure_ascii=False)


if __name__ == '__main__':
    # input_json, output_json = get_input_args("label_new_or_old_input_args")
    input_json, output_json = sys.argv[1],sys.argv[2]
    # label_new_or_old(r'/Users/anran/myfiles/隐私合规/situation_sensitive_privacy_data_location/Output0801/饿了么_output_filtered.json',
    #                  r'/Users/anran/myfiles/隐私合规/situation_sensitive_privacy_data_location/Output0801/饿了么_output_filtered_labeled.json')
    label_new_or_old(input_json, output_json)
