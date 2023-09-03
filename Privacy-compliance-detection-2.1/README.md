#### File Description

- `config` Folder to store config files of static analyzer.
- `static-run.sh` Shell script to start analyzing apks.
- `RunningConfig.properties` Setting file to control file output directory. You can choose to analyze a single apk or apks in a folder. But do not change other setting like logsPath, AndroidJar, resultSavePath, printToFile.
- `logsPath` Folder to store log files.
  - Log files are named like apkName_output_info.log, for example, 阿里小号_output_info.log. 
    It contains start time of analysis, start of Soot Init, end of Soot Init, number of method this analysis collected, number of 3rd stmt collected, number of 1st party privacy data items, 3rd party privacy data items collected and total time cost(ms).
- `ResultSaveDir` Folder to store result json files.
  - Result json file are named like apkName_method_scope.json, for example, 阿里小号_method_scope.json. 
    It contains all 1st privacy data items (privacy_data_items) collected and the class and method they are in, number of 1st privacy data items collected(num_of_privacy_data_items), number of common data items in this class and method, subsignature of the method call that contains 1st privacy data items, subsignature of the method call that contains common data items, 3rd party privacy data items collected, subsignature of the method call that contains 1st privacy data items, the number of 3rd party privacy data items.
- `final_res/pp_missing` Folder to store each apk's privacy data items found in static analysis but not in privacy policy. 
  The first key-val dictionary shows the number of all privacy data items found in privacy policy(total_pp_data_items_cnt), the number of all privacy data items found by static analysis(total_program_data_items_cnt) and the number of privacy data items found by static analysis but not in privacy policy(in_program_but_not_in_pp). \
  Other dictionaries show the class and method the privacy data item in and the method subsinature of the method call containing the privacy data item and if it comes from 3rd party.


- `privacy-policy-main.py` Enter the folder where the privacy policy text to be processed resides in the following format:
  
- `Privacy_Policy_approach.py`  Privacy policy text processing method to extract data-cn, purpose-cn and subject from a single sentence.
- `url.txt` Write the privacy policy url to be resolved in line to this file.
- `purpose_handle.py` purpose of extraction and refining (purpose-cn).
- `permission_handle.py` Extract the permissions mentioned in a single privacy policy (s_list) and output the Android permission list (permission_list).
- `run_privacypolicy.py` Process the (.txt) file, get the data item (data-cn-total), purpose (purpose-cn-total), subject (subject), and permission (permission_list), and output the json result.
- `_translate.py` Process the (.txt) file, get the data item (data-cn-total), purpose (purpose-cn-total), subject (subject), and permission (permission_list), and output the json result.
- `Privacypolicy_txt` Folder to store the privacy policy (.txt) to be processed.The text of the page privacy policy obtained by url parsing will also be included.
- `Dict` Folder to store data item dictionaries and permission - related dictionaries 
- `stopwords` Floder to store the stop glossary needed to process the privacy policy
- `PrivacyPolicySaveDir` Floder to store the json processing result of the privacy policy
- `model` stores the models that need to be installed to run the program


#### Prerequisites

- openJDK8
- python3.10
- spacy==3.5.0
- jieba==0.42.1
- beautifulsoup4==4.12.2
- alibabacloud-alimt20181012==1.1.0
- alibabacloud-tea==0.3.2
- hanlp


#### Setup & Run

In order to get logs and results, you need to do the following steps:

''' PrivacyPolicy_handle Setup&Run '''

- Make sure the url is correctly written to the url.txt file.
- `pip install spacy==3.5.0`
- `pip install Privacy-compliance-detection-2.1/core/model/zh_core_web_trf-3.5.0-py3-none-any.whl`
- `pip install Privacy-compliance-detection-2.1/core/model/zh_core_web_md-3.5.0-py3-none-any.whl`
- `pip install jieba`
- `pip install bs4`
- `pip install alibabacloud_alimt20181012==1.1.0`
- `pip install alibabacloud_teaopenai==0.3.2`
- `pip install hanlp`



- `python3 privacy-policy-main.py`

'''AppUIAutomator2Navigation-main Setup&&Run'''

Make sure to has a real mobile phone and well setup  and python3.10.10. The following blog tells how to set up.

https://blog.csdn.net/weixin_44786530/article/details/124079242

Config what app to dynamically test in `config.py` . It should be package name of the app.

- Install miniconda3
- `conda create -n py310 python=3.10.10`
- `conda activate py310`
- `pip install uiautomator2`

 Run `python3 run.py` 

''' Static analysis Setup&Run '''

- Open the `RunningConfig.properties` and add the absolute path of apk(s) or folder(s) after the `apk=` . Seperate each absolute path with ; . For example:`apk=/home/test/;/home/test_apk;/home/test_apks/淘宝联盟.apk;/home/youku.apk;`

- Run `./static-run.sh` in current directory to start analysis.
- Put all privacy policy analysis json file to the `PrivacyPolicySaveDir` directory. **Attention**: The naming of the privacy policy analysis json file **must be the same** as the name of the apk file. For example, there is an apk file named **taobao.apk** in `apks` folder, then there must be a privacy policy analysis json file named **taobao.json** in `PrivacyPolicySaveDir`.


''' Compliance detection Setup&Run '''

- Run `python3 report_data_in_pp_and_program.py` to start comparing.

'''context_sensitive_privacy_data_location Setup&Run'''

You can set outputdir and apks to analysis and other config in the RunningConfig.ini

- Run `python3 run_jar.py`
- Run `python3 run_UI_static.py`



'''One command run'''

Make sure you are at `./隐私合规` first, and then run `python3 run.py` .

#### Note

Make sure the file directory structure is like this:

- $(pwd)
  - AppUIAutomator2Navigation-main
  - context_sensitive_privacy_data_location
  - Privacy-compliance-detection-2.1
  - run.py
  
**Final integrate logs lie in ./context_sensitive_privacy_data_location/final_res_log_dir**



Make sure the files in the "model" directory are installed.
It usually takes about 10 minutes for a single privacy policy to be processed. If an element is missing from the English list, the translation fails. Try again.

There may be some error in Soot initialization and then you fail to get result.
It seems like this in log file: 
"start initSootConfig() 
Error in initSootConfig... 
initSootConfig error info:null 
Exit singleAnalysis due to initSootConfigError... 
" 
You just need to delete the log file in `logsPath` directory and rerun `./run.sh` for one or more times.

If you found `Nothing to output to json file,exit...` in the end of log file, it means that the program find no privacy data item in this apk.

We set a timeout threshold of 1 hour. if we can not finish analysis in 1 hour, the program will kill the current analysis and continue to analyze the next apk.
