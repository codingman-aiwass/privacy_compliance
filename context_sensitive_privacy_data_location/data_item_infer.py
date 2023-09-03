import json
import os.path
import sys

import hanlp
import re
from typing import List
from dealWithInputAndOutput import get_input_args

tok = hanlp.load(hanlp.pretrained.tok.COARSE_ELECTRA_SMALL_ZH)
pos = hanlp.load(hanlp.pretrained.pos.CTB9_POS_ELECTRA_SMALL)
dep = hanlp.load(hanlp.pretrained.dep.CTB7_BIAFFINE_DEP_ZH)

verbs_list = ['编辑', '设置', '修改', '发布']
verbs_list_En = ['modify', 'edit', 'upload']
# setting
pn_list = ['你', '您', '我']

verbs_list_screen_en = ['edit', 'set', 'add']


def split_camel_case(word):
    # 使用正则表达式匹配驼峰命名的模式
    pattern = r'(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])'
    words = re.findall(pattern, word)
    # 将单词转为小写
    words = [w.lower() for w in words]
    return words


def handle_dep_pn(dep_result: List[dict]) -> dict:
    nn_items = dict()
    condition_items = dict()

    # find all nn
    for dep_item in dep_result:
        if dep_item['upos'] == 'NN':
            nn_items[dep_item['id']] = dep_item

    # find modifier of nn, recursively
    # 先找到一个有指代的nn
    for key in nn_items.keys():
        nn_item = nn_items[key]
        conjunction_stack = []
        if modifier_found(dep_result, nn_item, conjunction_stack):
            for conjunction in conjunction_stack:
                nn_item['form'] = conjunction['form'] + nn_item['form']
            condition_items[nn_item['id']] = nn_item

    # 然后进行传播
    while True:
        pre_len = len(condition_items.keys())
        handle_pn_propagation(condition_items, nn_items)
        after_len = len(condition_items.keys())
        if pre_len == after_len:
            break

    handle_nn_propagation(condition_items, nn_items)

    return condition_items


# resolve PN propagation: 您的简历信息、软件习惯  --> 您的简历信息、您的软件习惯
def handle_pn_propagation(condition_items: dict, nn_items: dict):
    for key in nn_items.keys():
        nn_item = nn_items[key]
        if nn_item['head'] in condition_items.keys() and nn_item['deprel'] == 'conj':
            condition_items[nn_item['id']] = nn_item
        elif nn_item['head'] in condition_items.keys() and nn_item['deprel'] == 'dep':
            condition_items[nn_item['id']] = nn_item

    added_dict = dict()
    for key in condition_items.keys():
        condition_item = condition_items[key]
        if condition_item['head'] in nn_items.keys() and condition_item['deprel'] == 'conj':
            added_dict[condition_item['head']] = nn_items[condition_item['head']]
        elif condition_item['head'] in nn_items.keys() and condition_item['deprel'] == 'dep':
            added_dict[condition_item['head']] = nn_items[condition_item['head']]
    for key in added_dict.keys():
        condition_items[key] = added_dict[key]


# resolve NN propagation: 您的 简历 信息 -->  您的简历信息
def handle_nn_propagation(condition_items: dict, nn_items: dict):
    appending_list_items = dict()
    for key in nn_items.keys():
        nn_item = nn_items[key]
        if nn_item['head'] in condition_items.keys() and nn_item['deprel'] == 'nn':
            item_id = nn_item['head']
            if item_id not in appending_list_items.keys():
                appending_list_items[item_id] = [nn_item['form']]
            else:
                appending_list_items[item_id].append(nn_item['form'])

    for key in appending_list_items.keys():
        while len(appending_list_items[key]) != 0:
            added_form = appending_list_items[key].pop()
            condition_items[key]['form'] = added_form + condition_items[key]['form']


def modifier_found(dep_result: List[dict], nn_item: dict, conjunction_stack: list) -> bool:
    for dep_item in dep_result:
        if dep_item['head'] == nn_item['id'] and dep_item['upos'] == 'PN' and dep_item['deprel'] == 'assmod':
            return True
        elif dep_item['head'] == nn_item['id'] and dep_item['upos'] == 'PN' and dep_item['deprel'] == 'nsubj':
            return True
        elif dep_item['head'] == nn_item['id'] and dep_item['deprel'] == 'rcmod':
            conjunction_stack.append(dep_item)
            return modifier_found(dep_result, dep_item, conjunction_stack)

    return False


def handle_dep(dep_result: List[dict]) -> List[dict]:
    condition_item = dict()
    tmp_condition_item = dict()
    tmp_condition_item_list = list()
    conjunction_id_to_item_dict = dict()
    conjunction_nn_id_set = set()

    for dep_item in dep_result:
        if dep_item['deprel'] == 'pobj' and dep_item['upos'] == 'NN':
            tmp_condition_item = dep_item
            conjunction_nn_id_set.add(dep_item['id'])
            conjunction_id_to_item_dict[dep_item['id']] = dep_item
            print('pobj extracted: ', tmp_condition_item)

    if len(tmp_condition_item.keys()) == 0:
        return [dict()]

    # conjunction of PN and word conjunction
    # 您的简历信息、软件习惯  --> 您的简历信息、您的软件习惯
    for i in range(len(dep_result)):
        dep_item = dep_result[i]
        if dep_item['deprel'] == 'dep' and dep_item['head'] == tmp_condition_item['id'] and dep_item['upos'] == 'NN' or \
                dep_item['deprel'] == 'conj' and dep_item['head'] == tmp_condition_item['id'] and dep_item[
            'upos'] == 'NN':
            tmp_condition_item_list.append(dep_item)
            conjunction_id_to_item_dict[dep_item['id']] = dep_item

    # conjunction of pobj
    # conjunct 简历 and 信息 to 简历信息
    for i in range(len(dep_result)):
        dep_item = dep_result[i]
        if dep_item['deprel'] == 'nn' and dep_item['head'] in conjunction_id_to_item_dict.keys():
            conjunction_nn_id_set.add(dep_item['id'])
            conjunction_nn_id_set.add(dep_item['head'])
            conjunction_id_to_item_dict[dep_item['head']]['form'] = dep_item['form'] + \
                                                                    conjunction_id_to_item_dict[dep_item['head']][
                                                                        'form']
        elif dep_item['deprel'] == 'nn' and dep_item['head'] in conjunction_nn_id_set:
            conjunction_nn_id_set.add(dep_item['id'])
            conjunction_id_to_item_dict[dep_item['head']]['form'] = dep_item['form'] + \
                                                                    conjunction_id_to_item_dict[dep_item['head']][
                                                                        'form']

    for dep_item in dep_result:
        if dep_item['deprel'] == 'assmod' and dep_item['head'] in conjunction_nn_id_set and dep_item['upos'] == 'PN':
            condition_item = tmp_condition_item
            tmp_condition_item_list.append(condition_item)

    if len(condition_item.keys()) == 0:
        return [dict()]

    return tmp_condition_item_list


def clear_data(data: dict) -> dict:
    for host_object in data['outputObjects']:
        for layout_object in host_object['layouts']:
            if 'LayoutTitle' in layout_object.keys():
                title = layout_object['LayoutTitle']
            else:
                layout_object['LayoutTitle'] = ''

            for text_object in layout_object['texts']:
                text = text_object['Text']
                text = text.replace(' ', '').replace('\n', '')
                text_object['Text'] = text
    return data


class DateInfer:
    def __init__(self, input_file_path: str, output_file_path: str):
        self.input_file_path = input_file_path
        self.output_file_path = output_file_path
        self.json_list = self.init_json_list()
        self.text_tok_dict = self.init_text_tok()
        self.text_pos_dict = self.init_text_pos()
        self.text_dep_dict = self.init_text_dep()
        self.data_item_extracted = self.data_extract()
        self.data_item_implied = self.data_imply()

    def init_text_tok(self):
        text_tok_dict = dict()
        for host_object in self.json_list['outputObjects']:
            for layout_object in host_object['layouts']:
                title = layout_object['LayoutTitle']
                title_list = title.split(' ')
                for title_text in title_list:
                    if '[or]' in title_text:
                        continue
                    title_text = title_text.replace(' ', '').replace('\n', '')
                    if title_text == '':
                        continue
                    if title_text in text_tok_dict.keys():
                        continue
                    title_text_token = tok(title_text)
                    text_tok_dict[title_text] = title_text_token

                for text_object in layout_object['texts']:
                    text = text_object['Text']
                    if text == '':
                        continue
                    if text in text_tok_dict.keys():
                        continue
                    text_token = tok(text)
                    text_tok_dict[text] = text_token
        return text_tok_dict

    def init_text_pos(self):
        text_pos_dict = dict()
        for host_object in self.json_list['outputObjects']:
            for layout_object in host_object['layouts']:
                title = layout_object['LayoutTitle']
                title_list = title.split(' ')
                for title_text in title_list:
                    if '[or]' in title_text:
                        continue
                    title_text = title_text.replace(' ', '').replace('\n', '')
                    if title_text == '':
                        continue
                    if title_text in text_pos_dict.keys():
                        continue
                    title_text_pos = pos(self.text_tok_dict[title_text])
                    text_pos_dict[title_text] = title_text_pos

                for text_object in layout_object['texts']:
                    text = text_object['Text']
                    if text == '':
                        continue
                    if text in text_pos_dict.keys():
                        continue
                    text_pos = pos(self.text_tok_dict[text])
                    text_pos_dict[text] = text_pos
        return text_pos_dict

    def init_text_dep(self):
        text_dep_dict = dict()
        for host_object in self.json_list['outputObjects']:
            for layout_object in host_object['layouts']:
                title = layout_object['LayoutTitle']
                title_list = title.split(' ')
                for title_text in title_list:
                    if '[or]' in title_text:
                        continue
                    title_text = title_text.replace(' ', '').replace('\n', '')
                    if title_text == '':
                        continue
                    if title_text in text_dep_dict.keys():
                        continue

                    text_dep_input = []
                    for i in range(len(self.text_tok_dict[title_text])):
                        text_dep_input.append((self.text_tok_dict[title_text][i], self.text_pos_dict[title_text][i]))

                    title_text_dep = dep(text_dep_input)
                    text_dep_dict[title_text] = title_text_dep

                for text_object in layout_object['texts']:
                    text = text_object['Text']
                    if text == '':
                        continue
                    if text in text_dep_dict.keys():
                        continue

                    text_dep_input = []
                    for i in range(len(self.text_tok_dict[text])):
                        text_dep_input.append((self.text_tok_dict[text][i], self.text_pos_dict[text][i]))
                    text_dep = dep(text_dep_input)
                    text_dep_dict[text] = text_dep
        return text_dep_dict

    def init_json_list(self):
        with open(self.input_file_path, 'r', encoding='utf-8') as f:
            json_string = f.read()
        data = json.loads(json_string)
        data = clear_data(data)
        return data

    def is_data_item(self, text_obj: dict) -> bool:
        item_state = False
        text = text_obj['Text']
        if text == '':
            return item_state
        if text not in self.text_tok_dict:
            return item_state
        for p in self.text_pos_dict[text]:
            if p != 'NN':
                return item_state
        item_state = True

        return item_state

    def infer_layout_context(self, layout_title: str) -> str:
        layout_title = layout_title.replace(' ', '').replace('\n', '')
        if layout_title not in self.text_tok_dict.keys():
            return ''
        title_token = self.text_tok_dict[layout_title]
        title_pos = self.text_pos_dict[layout_title]

        title_set = set()
        context_word = ''
        context_similarity = -1
        for i in range(len(title_token)):
            if title_pos[i] == 'NN':
                title_set.add(title_token[i])
        if 'VV' not in title_pos:

            for host_object in self.json_list['outputObjects']:
                for layout_object in host_object['layouts']:
                    for text_object in layout_object['texts']:
                        text = text_object['Text']
                        if text == '':
                            continue

                        tmp_context_word = ''

                        # calculate similarity
                        text_token = self.text_tok_dict[text]
                        text_pos = self.text_pos_dict[text]
                        text_set = set()

                        if not self.is_context(text_object, text_token, text_pos):
                            continue

                        for i in range(len(text_token)):
                            if text_pos[i] == 'NN':
                                text_set.add(text_token[i])
                            elif text_pos[i] == 'VV':
                                tmp_context_word = text_token[i]

                        intersection = len(text_set.intersection(title_set))
                        union = len(text_set) + len(text_set) - intersection
                        if union == 0 or intersection == 0:
                            continue
                        tmp_context_similarity = intersection / union
                        if tmp_context_word == '':
                            continue
                        if tmp_context_similarity >= 0.5 and tmp_context_similarity > context_similarity:
                            context_word = tmp_context_word
                            context_similarity = tmp_context_similarity

        return context_word

    def calculate_text_similarity(self, text1, text2):
        text_token1 = tok(text1)
        text_token2 = tok(text2)

        text_pos1 = pos(text_token1)
        text_pos2 = pos(text_token2)

        text_set1 = set()
        text_set2 = set()
        for i in range(len(text_token1)):
            if text_pos1[i] == 'NN':
                text_set1.add(text_token1[i])
        for i in range(len(text_token2)):
            if text_pos2[i] == 'NN':
                text_set2.add(text_token2[i])

        intersection = len(text_set1.intersection(text_set2))
        union = len(text_set1) + len(text_set2) - intersection
        similarity = intersection / union
        print(similarity)
        print(intersection)
        print(union)
        return similarity

    def is_context(self, text_object, text_token, text_pos):
        if text_object['UserContext'] == '0':
            return False
        for i in range(len(text_token)):
            if text_pos[i] == 'VV':
                if text_token[i] in verbs_list:
                    return True

        return False

    def data_extract(self):
        data_item_extracted = []
        for host_object in self.json_list['outputObjects']:
            for layout_object in host_object['layouts']:
                for text_object in layout_object['texts']:
                    text = text_object['Text']

                    if text == '':
                        continue
                    jump_title = False
                    title_list = layout_object['LayoutTitle'].split(' ')
                    for title in title_list:
                        # filter out the text same as title.
                        if title == text:
                            jump_title = True
                    if jump_title:
                        continue
                    has_extracted = False

                    if text not in self.text_tok_dict.keys() or text not in self.text_pos_dict.keys():
                        continue

                    # context for simplest case:
                    # only noun
                    if 'VV' not in self.text_pos_dict[text]:
                        if text_object['UserContext'] == '0':
                            continue

                        # infer from UIClassName, HostName, LayoutName
                        # UIClassName: EditText -> Edit
                        ui_class_name = re.sub(r"(?P<key>[A-Z])", r"_\g<key>", text_object["UIClassName"])
                        ui_class_name = ui_class_name.strip('_').lower().split('.')
                        split_words = []
                        for class_name in ui_class_name:
                            for word in class_name.split('_'):
                                if len(word) == 0:
                                    continue
                                split_words.append(word)
                        ui_class_name = set(split_words)
                        for class_verb in verbs_list_En:
                            # calculate similarity
                            if class_verb in ui_class_name:
                                if self.is_data_item(text_object):
                                    data_item_extracted.append(text_object)
                                    has_extracted = True
                                    break
                        if has_extracted:
                            continue

                        # LayoutName: EditActivity -> Edit
                        layout_name = re.sub(r"(?P<key>[A-Z])", r"_\g<key>", layout_object["LayoutName"])
                        layout_name = layout_name.strip('_').lower().split('.')
                        split_words = []
                        for layout_name_split in layout_name:
                            for word in layout_name_split.split('_'):
                                if len(word) == 0:
                                    continue
                                split_words.append(word)
                        layout_name = set(split_words)
                        for class_verb in verbs_list_En:
                            # calculate similarity
                            if class_verb in layout_name:
                                if self.is_data_item(text_object):
                                    data_item_extracted.append(text_object)
                                    has_extracted = True
                                    break
                        if has_extracted:
                            continue

                        # HostName: EditActivity -> Edit
                        host_name = re.sub(r"(?P<key>[A-Z])", r"_\g<key>", host_object["HostName"])
                        host_name = host_name.strip('_').lower().split('.')
                        split_words = []
                        for host_name_split in host_name:
                            for word in host_name_split.split('_'):
                                if len(word) == 0:
                                    continue
                                split_words.append(word)
                        host_name = set(split_words)

                        for class_verb in verbs_list_En:
                            # calculate similarity
                            if class_verb in host_name:
                                if self.is_data_item(text_object):
                                    data_item_extracted.append(text_object)
                                    has_extracted = True
                                    break
                        if has_extracted:
                            continue

                        # infer from layout title
                        title_list = layout_object['LayoutTitle'].split(' ')
                        for title in title_list:
                            if title in self.text_tok_dict.keys():
                                title_text_token = self.text_tok_dict[title]
                                title_text_pos = self.text_pos_dict[title]
                                if 'VV' in title_text_pos:

                                    # if a title represent as a action, it should only have 'VV' and 'NN'
                                    action_representation = True
                                    action_nn = False
                                    action_vv = False
                                    for pos in title_text_pos:
                                        if pos == 'VV':
                                            action_vv = True
                                        elif pos == 'NN':
                                            action_nn = True
                                        if pos != 'VV' and pos != 'NN':
                                            action_representation = False
                                    action_representation = action_nn & action_vv & action_representation
                                    if not action_representation:
                                        continue

                                    for i in range(len(title_text_token)):
                                        if title_text_pos[i] == 'VV':
                                            if title_text_token[i] in verbs_list:
                                                if self.is_data_item(text_object):
                                                    data_item_extracted.append(text_object)
                                                    has_extracted = True
                                else:
                                    layout_context = self.infer_layout_context(title)
                                    if layout_context != '':
                                        if layout_context in verbs_list:
                                            if self.is_data_item(text_object):
                                                data_item_extracted.append(text_object)
                                                has_extracted = True

                            if has_extracted:
                                continue
        return data_item_extracted

    def data_imply(self):
        data_item_implied = []
        for host_object in self.json_list['outputObjects']:
            for layout_object in host_object['layouts']:
                for text_object in layout_object['texts']:
                    text = text_object['Text']
                    if text == '':
                        continue
                    if text_object['UserContext'] == '0':
                        continue

                    has_extracted = False

                    if text not in self.text_tok_dict.keys() or text not in self.text_pos_dict.keys() \
                            or text not in self.text_dep_dict.keys():
                        continue
                    data_dict = handle_dep_pn(self.text_dep_dict[text])

                    for key in data_dict.keys():
                        item = data_dict[key]
                        data_item_implied.append(item)
        return data_item_implied

    def show_result(self):
        text_obj_set_infer = set()
        text_obj_set_imply = set()

        print("\n----------Result of infer:")
        for text_object in self.data_item_extracted:
            if text_object['Text'] not in text_obj_set_infer:
                print(text_object['Text'], self.text_pos_dict[text_object['Text']])
                text_obj_set_infer.add(text_object['Text'])

        print("\n\n----------Result of imply:")
        for text_object in self.data_item_implied:
            if text_object['form'] not in text_obj_set_imply:
                print(text_object['form'])
                text_obj_set_imply.add(text_object['form'])

    def generate_result_file(self):
        text_obj_set_infer = set()
        text_obj_set_imply = set()
        json_output = dict()
        (_, json_output['AppName']) = os.path.split(self.input_file_path)
        json_output['outputObjects'] = list()

        for text_object in self.data_item_extracted:
            if text_object['Text'] not in text_obj_set_infer:
                text_obj_set_infer.add(text_object['Text'])
                json_output['outputObjects'].append({'text': text_object['Text']})
        for text_object in self.data_item_implied:
            if text_object['form'] not in text_obj_set_imply:
                text_obj_set_imply.add(text_object['form'])
                json_output['outputObjects'].append({'text': text_object['form']})
        with open(self.output_file_path, 'w', encoding='utf-8') as f:
            json.dump(json_output, f, indent=2, ensure_ascii=False)


if __name__ == '__main__':
    # 第一个参数是输入的json文件，这个json文件就是上一步LayoutBuilder的输出文件
    # 第二个参数是这一步输出文件的位置
    # input_json, output_json = get_input_args("data_item_infer_input_args")
    input_json, output_json = sys.argv[1], sys.argv[2]
    data_infer = DateInfer(input_json, output_json)
    data_infer.generate_result_file()
