import configparser
import os
from configobj import ConfigObj


class Properties:
    fileName = ''

    def __init__(self, fileName):
        self.fileName = fileName

    def getProperties(self):
        try:
            pro_file = open(self.fileName, 'r')
            properties = {}
            for line in pro_file:
                if line.find('=') > 0:
                    strs = line.replace('\n', '').split('=')
                    properties[strs[0]] = strs[1]
        except Exception:
            raise Exception
        else:
            pro_file.close()
            return properties


curpath = os.path.dirname(os.path.realpath(__file__))
inipath = os.path.join(curpath, 'RunningConfig.ini')

conf = configparser.ConfigParser()

conf.read(inipath, encoding='utf-8')


def get_run_jar_settings():
    return conf.items('run_jar_settings')[0][1], conf.items('run_jar_settings')[1][1], \
           conf.items('run_jar_settings')[2][1]


def get_input_args(name):
    return conf.items(name)[0][1], conf.items(name)[1][1]


def get_settings_by_section_and_name(section_name, *args):
    if len(args) == 1:
        return conf.get(section_name, args[0])
    else:
        tmp_list = []
        for arg in args:
            tmp_list.append(conf.get(section_name, arg))
        return tmp_list


def get_log_in_properties(file_name, *args):
    # p = Properties(file_name)
    # properties = p.getProperties()
    # tmp_list = []
    # for arg in args:
    #     print(arg)
    #     print(properties)
    #     tmp_list.append(properties[arg])
    # if len(tmp_list) == 1:
    #     return tmp_list[0]
    # else:
    #     return tmp_list

    props = ConfigObj(file_name, encoding='UTF8')
    if len(args) == 1:
        return props[args[0]]
    else:
        tmp_list = []
        for arg in args:
            tmp_list.append(props[arg])
        return tmp_list
