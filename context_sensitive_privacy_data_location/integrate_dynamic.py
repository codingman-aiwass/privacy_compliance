import json
import sys
from dealWithInputAndOutput import get_input_args


def read_dynamic_json(input_file: str, output_file: str):
    """
    Read the dynamic result, convert to the static form.
    :param input_file: the file path of dynamic result.
    :param output_file: the store path of converted result.
    """

    # drop duplicate text
    visited_set = set()

    with open(input_file, 'r', encoding='utf-8') as f:
        dynamic_result = json.load(f)
    converted_result = dict()
    converted_result['AppName'] = ''
    converted_result['outputObjects'] = []

    for screen_object in dynamic_result:
        text_total = screen_object['ck_eles_text']
        output_object = dict()
        output_object['HostName'] = screen_object['activity_name']
        output_object['layouts'] = []

        layout_object = dict()
        layout_object['LayoutName'] = ''
        layout_object['LayoutTitle'] = ''
        layout_object['texts'] = []
        for text in text_total.replace(' ', ',').replace('&', ',').split(','):
            if text in visited_set:
                continue
            visited_set.add(text)

            text_object = dict()
            text_object['Text'] = text
            text_object['UIClassName'] = ''
            text_object['UserContext'] = '1'

            layout_object['texts'].append(text_object)

        output_object['layouts'].append(layout_object)
        converted_result['outputObjects'].append(output_object)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(converted_result, f, indent=2, ensure_ascii=False)


if __name__ == '__main__':
    # input_json, output_json = get_input_args("integrate_dynamic_input_args")
    input_json, output_json = sys.argv[1], sys.argv[2]
    read_dynamic_json(input_json, output_json)
