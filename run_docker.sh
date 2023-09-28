docker run -it -v ./docker_result/code_inspection_result/logsPath:/app/Privacy-compliance-detection-2.1/core/logsPath \
 -v ./docker_result/code_inspection_result/ResultSaveDir:/app/Privacy-compliance-detection-2.1/core/ResultSaveDir  \
 -v ./docker_result/code_inspection_result/pp_missing:/app/Privacy-compliance-detection-2.1/core/final_res/pp_missing  \
 -v ./docker_result/dynamic_run_result:/app/AppUIAutomator2Navigation/collectData  \
 -v ./docker_result/privacy_policy_analysis_result:/app/Privacy-compliance-detection-2.1/core/PrivacyPolicySaveDir  \
 -v ./docker_result/static_UI_run_result:/app/context_sensitive_privacy_data_location/tmp-output  \
 -v ./docker_result/final_result:/app/context_sensitive_privacy_data_location/final_res_log_dir  \
 -v ./docker_result/apps_still_missing_pp_urls.txt:/app/docker_result/apps_still_missing_pp_urls.txt  \
 -v ./docker_result/config.ini:/app/config.ini  \
 -v ./docker_result/dynamic_apps_missing_pp_url.txt:/app/dynamic_apps_missing_pp_url.txt privacy_compliance_image