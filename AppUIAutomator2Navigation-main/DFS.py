# cur_activity
# for....所有能点击的组件:
#   click()
# 否则当前没东西可点了，back ，不写成dfs
from ScreenNode import *
from ScreenCompareStrategy import *
import time
import signal
from core_functions import *
 
# 自定义超时异常
class TimeoutError(Exception):
    def __init__(self, msg):
        super(TimeoutError, self).__init__()
        self.msg = msg

def time_out(interval, callback):
    def decorator(func):
        def handler(signum, frame):
            raise TimeoutError("run func timeout")
 
        def wrapper(*args, **kwargs):
            try:
                signal.signal(signal.SIGALRM, handler)
                signal.alarm(interval)       # interval秒后向进程发送SIGALRM信号
                result = func(*args, **kwargs)
                signal.alarm(0)              # 函数在规定时间执行完后关闭alarm闹钟
                return result
            except TimeoutError as e:
                callback(e)
        return wrapper
    return decorator
 
def timeout_callback(e):
    print("超时回调函数")
 
@time_out(3, timeout_callback)
def testTimeOut():
    while(True):
        print(100)
        time.sleep(1)


def dfs_screen(last_screen_all_text, last_clickable_ele, last_activity):
    # 获取当前screen
    global first_activity
    global total_eles_cnt
    global first_screen_text
    cur_screen_pkg_name, cur_activity, cur_screen_all_text, cur_screen_info = get_screen_info(d)
    # cur_screen_sig = get_signature(cur_screen_info)

    # 不是当前要测试的app, 返回
    if cur_screen_pkg_name != target_pkg_name:
        d.press("back")
        time.sleep(sleep_time_sec)
        return
    

    #EditText点击之后或者其他情况会有输入框，此时无法点击其他组件
    #因此需要back消除输入框，然后return
    if last_clickable_ele is not None:
        # 用更加 general的方法来规避输入法输入框
        if("EditText" in last_clickable_ele.get("class")):
            ## 避免某些情况点了页面上肉眼不可见的EditText,这个时候不会有inputmethod.lation,如果back的话会出问题
            if(d(packageName = "com.google.android.inputmethod.latin").exists()):
                # print("文本框回退")
                d.press("back")
                return
    
        elif (d(packageName = "com.google.android.inputmethod.latin").exists()):
            # print("文本框回退")
            d.press("back")
            cur_screen_pkg_name, cur_activity, cur_screen_all_text, cur_screen_info = get_screen_info(d)
            # cur_screen_sig = get_signature(cur_screen_info)
    
    # screen没有变化说明该组件不会造成页面跳转
    if screen_compare_strategy.compare_screen(cur_screen_all_text, last_screen_all_text)[0] == True:
        #TODO
        # 给一个容错机会,点过组件无效可能只是因为屏幕挡住了
        if last_clickable_ele.get("class") == "android.widget.CheckBox":
            pass
        else:
            last_clickable_ele_uuid = get_unique_id(d, last_clickable_ele, last_activity)
            ele_vis_map[last_clickable_ele_uuid] = False
        return
    # if scur_screen_all_text == last_screen_all_text:
    #     return
    
    stat_activity_set.add(cur_activity) #统计结果用
    stat_screen_set.add(cur_screen_all_text) #统计结果用

    # 建Screen跳转图
    cur_screen_node = get_screennode_from_screenmap(screen_map, cur_screen_all_text, screen_compare_strategy)
    # 记录merged前后减少的组件个数
  
    if cur_screen_node is None:
        # 初始化cur_screen_node信息
        cur_screen_node = ScreenNode()
        cur_screen_node.info = cur_screen_info
        # cur_screen_node.sig = cur_screen_sig
        cur_screen_node.ck_eles_text = cur_screen_all_text
        cur_screen_node.pkg_name = cur_screen_pkg_name
        cur_screen_node.activity_name = cur_activity
        clickable_eles, res_merged_diff = get_merged_clickable_elements(d, ele_uuid_map, cur_activity)
        cur_screen_node.merged_diff = res_merged_diff
        cur_screen_node.clickable_elements = clickable_eles
        # 将cur_screen加入到全局记录的screen_map
        screen_map[cur_screen_all_text] = cur_screen_node
        # 将cur_screen加入到last_screen的子节点
        # last_screen_node = screen_map.get(last_screen_all_text)
        last_screen_node = get_screennode_from_screenmap(screen_map, last_screen_all_text, screen_compare_strategy)
        last_screen_node.add_child(cur_screen_node)
        print()
        print("*"*100)
        print(f"该screen为新: {cur_screen_node.ck_eles_text[0:-1]}--总共{len(cur_screen_node.clickable_elements)}, 减少{cur_screen_node.merged_diff}")
        print("*"*100)
        print()
    else:
        print()
        print("*"*100)
        print(f"该screen已存在: {cur_screen_node.ck_eles_text[0:-1]}--总共{len(cur_screen_node.clickable_elements)}, 减少{cur_screen_node.merged_diff}")
        print("*"*100)
        print()
        if cur_screen_node.is_screen_clickable_finished():
            print("当前Screen已经点击完, 不需要再点")
            if screen_compare_strategy.compare_screen(first_screen_text, cur_screen_all_text)[0] == True:
                print("最后一个界面不回退")
            else:
                print("正常回退")
                d.press("back")
                time.sleep(sleep_time_sec)
            return

    

    #如果触发了新的界面，这个时候要判断是否存在回边，存在环就不加call_map
    #表示虽然该组件能触发新界面，但是会产生回边，因此不能将screen加入call_map
    if last_screen_all_text != "root":
        # last_screen_node = screen_map.get(last_screen_all_text)
        last_screen_node = get_screennode_from_screenmap(screen_map, last_screen_all_text, screen_compare_strategy)
        # if last_screen_node.find_ancestor(cur_screen_all_text):
        if check_cycle(cur_screen_node, last_screen_node, screen_compare_strategy) == True:
            #产生了回边
            pass
        else:
            # last_clickale_ele_uuid = get_uuid(last_clickable_ele, d, umap, last_activity)
            last_clickale_ele_uuid = get_unique_id(d, last_clickable_ele, last_activity)
            last_screen_node.call_map[last_clickale_ele_uuid] = cur_screen_all_text
    else:
        first_screen_text = cur_screen_all_text
        first_activity = cur_activity
    
    # 遍历cur_screen的所有可点击组件
    cur_screen_node_clickable_eles = cur_screen_node.clickable_elements

    clickable_ele_idx = 0
    while clickable_ele_idx < len(cur_screen_node_clickable_eles):
        cur_clickable_ele = cur_screen_node_clickable_eles[clickable_ele_idx]
    # for clickable_ele_idx, cur_clickable_ele in enumerate(cur_screen_node_clickable_eles):

        #--------------------------------------
        #判断当前组件是否需要访问
        #1.如果没访问过，即vis_map[uuid]=False，就直接访问
        #2.如果访问过了，即vis_map[uuid]=True,还得判断该组件是否是
        #当前callmap的，如果是还需要递归判断该组件对应的call_map里面的节点(screen)
        #的所有组件是否访问完毕

        #判断当前界面是否真的为当前界面？
        temp_screen_pkg, temp_activity, temp_screen_all_text, temp_screen_info = get_screen_info(d)
        if (cur_screen_pkg_name != temp_screen_pkg) or (cur_activity != temp_activity):
            print("循环过程中界面不一样, return-----------------------")
            return
        if not screen_compare_strategy.compare_screen(cur_screen_all_text, temp_screen_all_text)[0]:
            print("循环过程中界面不一样, return-----------------------")
            return
        

        # 表示该组件已经访问过
        # +1是因为下标从0开始
        cur_screen_node.already_clicked_cnt = clickable_ele_idx + 1
        # uuid = get_uuid(cur_clickable_ele, d, umap, cur_activity)
        uuid = get_unique_id(d, cur_clickable_ele, cur_activity)

        ## 简单地判断screen左上角的back按钮, 方便debug
        if cur_clickable_ele.get("resource-id") == "com.alibaba.android.rimet:id/toolbar":
            ele_vis_map[uuid] = True
            print(f"省略组件&{clickable_ele_idx}: {uuid}")
            clickable_ele_idx +=1
            continue
        if cur_clickable_ele.get("resource-id") == "com.alibaba.android.rimet:id/back_layout":
            ele_vis_map[uuid] = True
            print(f"省略组件&{clickable_ele_idx}: {uuid}")
            clickable_ele_idx +=1
            continue
        if "相机" in cur_clickable_ele.get("text"):
            ele_vis_map[uuid] = True
            print(f"省略组件&{clickable_ele_idx}: {uuid}")
            clickable_ele_idx +=1
            continue
        if "照片" in cur_clickable_ele.get("text"):
            ele_vis_map[uuid] = True
            print(f"省略组件&{clickable_ele_idx}: {uuid}")
            clickable_ele_idx +=1
            continue
        if "拍照" in cur_clickable_ele.get("text"):
            ele_vis_map[uuid] = True
            print(f"省略组件&{clickable_ele_idx}: {uuid}")
            clickable_ele_idx +=1
            continue
        if "手机文件" in cur_clickable_ele.get("text"):
            ele_vis_map[uuid] = True
            print(f"省略组件&{clickable_ele_idx}: {uuid}")
            clickable_ele_idx +=1
            continue


    
        if ele_vis_map.get(uuid, False) == False:
            # 拿到该组件的坐标x, y
            loc_x, loc_y = get_location(cur_clickable_ele)
            ele_vis_map[uuid] = True
            #点击该组件
            # cur_screen_node.already_clicked_cnt = get_uuid_cnt(uuid)
   
            print(f"正常点击组件&{clickable_ele_idx}: {uuid}")
            total_eles_cnt +=1 #统计的组件点击次数+1

            d.click(loc_x, loc_y)
            time.sleep(sleep_time_sec)
            
            dfs_screen(cur_screen_all_text, cur_clickable_ele, cur_activity)

        else:
            if cur_screen_node.call_map.get(uuid, None) is not None:
                target_screen_all_text = cur_screen_node.call_map.get(uuid)
                if cur_screen_node.is_all_children_finish(target_screen_all_text, screen_compare_strategy) == False:
                    # click_map指示存在部分没完成
                    loc_x, loc_y = get_location(cur_clickable_ele)
                    # 点击该组件
                    # cur_screen_node.already_clicked_cnt = get_uuid_cnt(uuid)
    
                    print(f"clickmap没完成点击组件&{clickable_ele_idx}: {uuid}")
                    total_eles_cnt +=1 #统计的组件点击次数+1
                    
                    d.click(loc_x, loc_y) 
                    time.sleep(sleep_time_sec)
                    
                    if cur_clickable_ele is None:
                        raise Exception

                    dfs_screen(cur_screen_all_text, cur_clickable_ele, cur_activity)
                else:
                    print(f"clickmap--该界面点击完成&{clickable_ele_idx}: {uuid}----界面{cur_screen_node.ck_eles_text[0:-1]}")
            else:
                print(f"clickmap不存在&{clickable_ele_idx}: {uuid}")
        

        clickable_ele_idx +=1

        #TODO
        #追加判断,如果循环结束发现该组件click_map对应的下一个Screen存在没点的组件,就让循环再执行
        #防止的意外情况A->B->C, C->back->A,此时for循环结束后,即使B还没点完,也不会再继续点B
        #具体案例:ScreenA->Dialog ScreenB -> ScreenC, ScreenC -> back -> ScreenA
        if cur_screen_node.call_map.get(uuid, None) is not None:
            target_screen_all_text = cur_screen_node.call_map.get(uuid)
            if cur_screen_node.is_all_children_finish(target_screen_all_text, screen_compare_strategy) == False:
                clickable_ele_idx -= 1
                print("存在容错情况, 追加一次循环i--")

        

    # for循环遍历结束back返回上一层界面



    # 如果当前的activity是first activity,就不让退出

    # if first_activity is None:
    #     raise Exception
    # else:
    #     top_activity = get_top_activity(d)
    #     if top_activity is None:
    #         raise Exception
    #     if first_activity not in top_activity:
    #         print("正常回退")
    #         d.press("back")
    #         time.sleep(sleep_time_sec)

    if first_screen_text == "" or first_screen_text is None:
        raise Exception
    else:
        temp_screen_pkg, temp_activity, temp_screen_all_text, temp_screen_info = get_screen_info(d)
        if (cur_screen_pkg_name != temp_screen_pkg) or (cur_activity != temp_activity):
            print("循环过程结束界面不一样, return-----------------------")
            return
        if not screen_compare_strategy.compare_screen(cur_screen_all_text, temp_screen_all_text)[0]:
            print("循环过程结束不一样, return-----------------------")
            return
        
        if screen_compare_strategy.compare_screen(first_screen_text, temp_screen_all_text)[0] == True:
            print("最后一个界面不回退")
        else:
            print("正常回退")
            d.press("back")
            time.sleep(sleep_time_sec)






if __name__ == "__main__":


    # try:
    #     testTimeOut()
    # except Exception as e:
    #     print(1)
    # 存储着整个app所有screen(ScrennNode) {key:screen_sig, val:screen_node}
    screen_map = {}
    # umap: {key:uid, value:cnt}
    # umap = {}
    # 全局记录每个组件的uuid {key:uuid, val:clickable_ele}
    ele_uuid_map = {}
    # 全局记录组件是否有被点击过 {key:uuid, val:true/false}
    ele_vis_map = {}

    sleep_time_sec = 5
    # 统计结果用
    total_eles_cnt = 0
    stat_screen_set = set()
    # total_screen_cnt = 0
    stat_activity_set = set()
    # total_activity_cnt = 0


    # 启动app开始执行
    d = Device()
    screen_compare_strategy = ScreenCompareStrategy(LCSComparator())
    # curr_pkg_name = "com.example.myapplication"
    target_pkg_name = "com.alibaba.android.rimet"
    # target_pkg_name = "com.ss.android.lark"
    # target_pkg_name = "com.cloudy.component"
    # target_pkg_name = "com.jingyao.easybike"

    # 第一个activity
    first_activity = None
    first_screen_text = ""
    d.app_start(target_pkg_name)
    time.sleep(sleep_time_sec)
 
    root = ScreenNode()
    root.ck_eles_text = "root"
    screen_map["root"] = root

    # try:
    dfs_screen("root", None, None)
    # except Exception as e:
    #     print(e)

    print("@"*100)
    print("@"*100)
    print(f"总共点击的activity个数 {len(stat_activity_set)}")
    print(f"总共点击的Screen个数: {len(stat_screen_set)}")
    print(f"总共点击的组件个数: {total_eles_cnt}")

