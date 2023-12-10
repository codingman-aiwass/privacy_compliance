### File Description

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
  Other dictionaries show the class and method the privacy data item in and the method signature of the method call containing the privacy data item and if it comes from 3rd party.


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
- `PrivacyPolicySaveDir` Folder to store the json processing result of the privacy policy
- `model` stores the models that need to be installed to run the program


### Prerequisites

- openJDK8
- python3.8.0
- adb tool
- An Android device with Root and frida-server.


### Setup & Run

In order to get logs and results, there are 4 modules that can be executed separately and 1 one-command-run module.


#### Static Code Analysis(Code Inspection Module)
Make sure you are at {your workdir}/privacy_compliance/Privacy-compliance-detection-2.1/core
##### How to run
- Open the `RunningConfig.properties` and add the absolute path of apk(s) or folder(s) after the `apk=` . Seperate each absolute path with ; . For example:`apk=/home/test/;/home/test_apk;/home/test_apks/淘宝联盟.apk;/home/youku.apk;`
- Run `./static-run.sh`(in Unix-like OS) or run `powershell.exe .\static-run.ps1`(in Windows) in current directory to start static code analysis. Its results are in ./ResultSaveDir. If you do not want to analysis static code analysis, but want to execute **AppUIAutomator2Navigation** part , you can run `java -jar getApkInfo.jar`(in Unix-Like OS) or run `powershell.exe .\getApkInfo.ps1`(in Windows) to get package name and app name of apks specified in RunningConfig.properties above.
- If you want to execute the **PrivacyPolicy_handle** section below, run `python3 get_permission_list.py` in current directory to get permissions of apks. Its results are in ./permissions


#### PrivacyPolicy_handle(Privacy Policy Analysis Module)
Make sure you are at {your workdir}/privacy_compliance/Privacy-compliance-detection-2.1/core

##### Prerequisites
- Run `pip install spacy==3.5.0`
- Run `pip install model/zh_core_web_trf-3.5.0-py3-none-any.whl`
- Run `pip install model/zh_core_web_md-3.5.0-py3-none-any.whl`
- Run `pip install jieba`
- Run `pip install bs4`
- Run `pip install alibabacloud_alimt20181012==1.1.0`
- Run `pip install alibabacloud_teaopenai==0.3.2`
- Run `pip install hanlp`
- Run `pip install selinium`
- Run `pip install dashscope`
- Configure the Chromedriver in your machine.
- Configure Ali Translation key and secret in `api_key.ini`.
- Configure LLM api-key in `api_key.ini`

##### How to run
- Run `python3 get_permission_list.py` to get permissions of apks. Its results are in ./permissions
- Run `python3 privacy-policy-main.py`. Its results are in ./PrivacyPolicySaveDir


If you want to run permission check or compliance_check via LLM, you can execute the following script respectively:
- Run `python3 permission_query.py` or `python3 compliance_analysis.py`

Results of the above 2 scripts are in ./permission_query_res_save_dir and ./compliance_query_res_save_dir,respectively.

If you want to get privacy data items in decompiled code but not in privacy policy.

Make sure you have run the static code analysis(static-run.sh or .\static-run.ps1) and privacy policy analysis(privacy-policy-main.py).
- Run `python3 report_data_in_pp_and_program.py` to start comparing. Its results are in ./final_res/pp_missing

#### AppUIAutomator2Navigation(Dynamic Test Module)
Make sure you are at {your workdir}/privacy_compliance/AppUIAutomator2Navigation
##### Prerequisites
- Run `pip install -r requirements.txt`
- Run `pip install -r requirements_yolov5.txt`
- Make sure to has a real mobile phone which has root permission.
- Make sure to have frida-server 15.1.24, and it should be located in /data/local/tmp and renamed frida15, i.e., you should have /data/local/tmp/frida15 in your android device plugged in the host machine.
- Make sure to install the latest tessearct and its language package in your local machine. https://github.com/tesseract-ocr/tesseract
- Make sure the system encoding is UTF8 instead of GBK.
##### How to run
- Configure what apps to dynamically test in `apk_pkgName.txt`. It should be package name and app name of the app. For example, com.shuqi.controller | 书旗小说
- Configure running parameters in config.ini.(Optional)
- Run `python3 run_config.py`. Its results are in ./collectData

#### context_sensitive_privacy_data_location(Static UI Analysis Module)
Make sure you are at {your workdir}/privacy_compliance/context_sensitive_privacy_data_location

##### Prerequisites
- Run `pip install hanlp[full] -U`
- Run `pip install configobj`
- Run `pip install configparser`
- Run `pip install chardet`
##### How to run
- Open the ` RunningConfig.ini` and add the absolute path of apk(s) or folder(s) after the `apk=` . Seperate each absolute path with ; . For example:`apk=/home/test/;/home/test_apk;/home/test_apks/淘宝联盟.apk;/home/youku.apk;`
- Run `python3 run_jar.py`
- Run `python3 run_UI_static.py`





#### One command run
If you choose to run this, you **should not** change settings in above modules, i.e., you should not change settings in RunningConfig.ini and RunningConfig.properties.

Make sure you are at `{your workdir}/privacy_compliance` first.
##### Prerequisites
If you haven't executed all 4 modules above. You need to do the following steps.

If you have done the following steps, you don't need to the steps in prerequisites of the above 4 modules again when executing any one of the above 4 modules.
- Run `pip install -r requirements.txt`
- Run `pip install -r requirements_yolov5.txt`
- Run `pip install hanlp[full] -U`
- Make sure to has a real mobile phone which has root permission.
- Make sure to have frida-server 15.1.24, and it should be located in /data/local/tmp and renamed frida15, i.e., you should have /data/local/tmp/frida15 in your android device plugged in the host machine.
- Install the ChromeDriver according to the Chrome version in your local machine.
- Install the tesseract and configure its language package. https://github.com/tesseract-ocr/tesseract
- Make sure the system encoding is UTF8 instead of GBK.
- Configure Ali Translation key and secret in `./Privacy-compliance-detection-2.1/core/api_key.ini`
- Configure Ali LLM api-key in `./Privacy-compliance-detection-2.1/core/api_key.ini`
##### How to run
- Configure running parameters in config.ini.(Optional)
- If you want to run with config file, run`python3 one_command_run.py -c config.ini`, else run `python3 one_command_run.py`
- If you want to ask llm about privacy policy. You can go to `Privacy-compliance-detection-2.1/core` and execute `python3 compliance_analysis.py` or `python3 permission_query.py`.

The final logs are in ./final_res_log_dir

### Note

Make sure the file directory structure is like this:

- privacy_compliance
  - AppUIAutomator2Navigation
  - context_sensitive_privacy_data_location
  - Privacy-compliance-detection-2.1
  - run.py
  - get_urls.py
  - config.ini
  - requirements.txt
  - requirements_yolov5.txt
  - final_res_log_dir
  - logs
  
**Final integrated logs are in final_res_log_dir**

When using One command run module, the output will be redirected to ./logs. There are logs of different modules.

It usually takes about 10 minutes for a single privacy policy to be processed. If an element is missing from the English list, the translation fails. Try again.

In Static Code analysis, there may be some error in Soot initialization and then you fail to get result.
It seems like this in log file:"

start initSootConfig()

Error in initSootConfig... 

initSootConfig error info:null 

Exit singleAnalysis due to initSootConfigError... 

" 

You just need to delete the log file in `logsPath` directory and rerun `./static-run.sh` or `powershell.exe .\static-run.ps1` for one or more times.

If you found `Nothing to output to json file,exit...` in the end of log file, it means that the program find no privacy data item in this apk.

We set a timeout threshold of 1 hour for code inspection. if we can not finish analysis in 1 hour, the program will kill the current analysis and continue to analyze the next apk.

The python version must be python3.8.0, or errors will occur.

