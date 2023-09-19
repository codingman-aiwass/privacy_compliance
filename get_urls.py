# -*- coding: UTF-8 -*-
from lxml import etree
import requests
import re
import os
import json
from context_sensitive_privacy_data_location.dealWithInputAndOutput import get_log_in_properties


def get_pp_from_mi_store(pkg_name):
    response = requests.get('https://app.mi.com/details?id={}&ref=search'.format(pkg_name))
    html_content = response.text
    tree = etree.HTML(html_content)
    href = tree.xpath('//div[@class="float-right"]//a/@href')
    try:
        print(href[0])
        url_to_return = href[0]
        return url_to_return
    except IndexError:
        return None


def get_pp_from_tencent(pkg_name):
    response = requests.get('https://sj.qq.com/appdetail/{}'.format(pkg_name))
    html_content = response.text

    url_pattern = r'<a.*?href="(.*?)".*?>隐私政策</a>'
    matches = re.findall(url_pattern, html_content)
    if matches:
        if len(matches[0]) > 1:
            return matches[0][:]
        else:
            return None
    else:
        return None


def get_pkg_names_from_code_inspection():
    logs = os.listdir('./Privacy-compliance-detection-2.1/core/' + get_log_in_properties(
        './Privacy-compliance-detection-2.1/core/RunningConfig.properties', 'resultSavePath')[2:])
    logs = [item[:-len('_method_scope.json')] for item in logs]
    return logs

def get_pkg_names_from_apk_pkgNametxt():
    with open('./AppUIAutomator2Navigation/apk_pkgName.txt')as f:
        lines = f.readlines()
    pkg_name_list = []
    for line in lines:
        pkg_name_list.append(line.split(' | ')[0])
    return pkg_name_list
def get_pkg_names_from_input_list(pkg_name_list):
    return pkg_name_list

def get_pp_from_app_store(pkg_names):
    pp_urls = {}
    missing_urls = []
    for pkg_name in pkg_names:
        pp_url = None
        if len(pkg_name) > 3:
            try:
                pp_url = get_pp_from_tencent(pkg_name)
            except Exception:
                print('==========================================')
                print('error occurred in get_pp_from_tencent...')
                print('missing app is {}'.format(pkg_name))
                print('==========================================')
            if pp_url is None:
                try:
                    pp_url = get_pp_from_mi_store(pkg_name)
                except Exception:
                    print('==========================================')
                    print('error occurred in get_pp_from_mi_store...')
                    print('missing app is {}'.format(pkg_name))
                    print('==========================================')
                if pp_url is None:
                    print('==========================================')
                    print('{} not in store...'.format(pkg_name))
                    print('==========================================')
                    missing_urls.append(pkg_name)
                else:
                    pp_urls[pkg_name] = pp_url
                    # print(pp_url)
            else:
                pp_urls[pkg_name] = pp_url
                # print(pp_url)
    return pp_urls,missing_urls


if __name__ == '__main__':
    choice = True
    if os.path.exists('./Privacy-compliance-detection-2.1/core/pkgName_url.json'):
        print('pkgName_url exists,enter y to get privacy policy url from app store again,n to reuse privacy policy urls in pkgName_url.json.')
        input_ = input()
        if input_ == 'y':
            choice = True
        elif input_ == 'n':
            choice = False
        else:
            print('error input...')
    if choice:

        # pkg_names = get_pkg_names_from_apk_pkgNametxt()

        # pp_urls = {}
        # missing_urls = []
        # for pkg_name in pkg_names:
        #     if len(pkg_name) > 3:
        #         pp_url = get_pp_from_tencent(pkg_name)
        #         if pp_url is None:
        #             pp_url = get_pp_from_mi_store(pkg_name)
        #             if pp_url is None:
        #                 print('{} not in store...'.format(pkg_name))
        #                 missing_urls.append(pkg_name)
        #             else:
        #                 pp_urls[pkg_name] = pp_url
        #                 # print(pp_url)
        #         else:
        #             pp_urls[pkg_name] = pp_url
        #             # print(pp_url)
        pp_urls,missing_urls = get_pp_from_app_store(get_pkg_names_from_apk_pkgNametxt())

        with open('./Privacy-compliance-detection-2.1/core/pkgName_url.json', 'w') as f:
            json.dump(pp_urls, f, indent=4)
        if len(missing_urls) > 0:
            with open('./apps_missing_pp_url.txt', 'w') as f:
                for app in missing_urls:
                    f.write(app)
                    f.write('\n')
