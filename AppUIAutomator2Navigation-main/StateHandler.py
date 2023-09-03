from RuntimeContent import *
import time
from Config import *
from RestartException import RestartException
from core_functions import *
from DeviceHelper import *
from StatRecorder import *
import random
from StateChecker import *
from Utils.LogUtils import *

class StateHandler(object):
    @classmethod
    def click_one_ele(cls, content):
        # 遍历cur_screen的所有可点击组件
        cur_screen_node = get_cur_screen_node_from_context(content)
        cur_screen_pkg_name, cur_activity, ck_eles_text = get_screen_info_from_context(content)
        cur_screen_node_clickable_eles = cur_screen_node.get_diff_or_clickable_eles()

        clickable_ele_idx = cur_screen_node.already_clicked_cnt
        while clickable_ele_idx < len(cur_screen_node_clickable_eles):
            cur_clickable_ele_uid = cur_screen_node_clickable_eles[clickable_ele_idx]

            # TODO 仅调试使用
            # if clickable_ele_idx <= 0:
            #     cur_screen_node.already_clicked_cnt += 1
            #     clickable_ele_idx+=1
            #     continue
            cur_clickable_ele_dict = RuntimeContent.get_instance().get_ele_uid_map_by_uid(cur_clickable_ele_uid)

            loc_x, loc_y = get_location(cur_clickable_ele_dict)
            if loc_x >= 60 and loc_x <= 70 and loc_y == 162:
                cur_screen_node.already_clicked_cnt += 1
                clickable_ele_idx += 1
                continue
            if loc_x >= 998 and loc_x <= 1010 and loc_y >= 155 and loc_y <= 165:
                cur_screen_node.already_clicked_cnt += 1
                clickable_ele_idx += 1
                continue

            # for clickable_ele_idx, cur_clickable_ele_uid in enumerate(cur_screen_node_clickable_eles):
            # --------------------------------------
            # 判断当前组件是否需要访问
            # 1.如果没访问过，即vis_map[uid]=False，就直接访问
            # 2.如果访问过了，即vis_map[uid]=True,还得判断该组件是否是
            # 当前callmap的，如果是还需要递归判断该组件对应的call_map里面的节点(screen)
            # 的所有组件是否访问完毕

            # 表示该组件已经访问过
            # +1是因为下标从0开始
            # cur_screen_node.already_clicked_cnt = clickable_ele_idx + 1
            # uid = get_uid(cur_clickable_ele, d, umap, cur_activity)
            cur_screen_ele_dict = RuntimeContent.get_instance().get_ele_uid_map_by_uid(cur_clickable_ele_uid)
            if is_non_necessary_click(cur_screen_ele_dict):
                cur_screen_node.ele_vis_map[cur_clickable_ele_uid] = True
                if cur_screen_node.ele_uid_cnt_map.get(cur_clickable_ele_uid, None) is None:
                    cur_screen_node.ele_uid_cnt_map[cur_clickable_ele_uid] = 1
                else:
                    cur_screen_node.ele_uid_cnt_map[cur_clickable_ele_uid] += 1
                LogUtils.log_info(f"省略组件&{clickable_ele_idx}: {cur_clickable_ele_uid}")
                LogUtils.log_info("\n")
                clickable_ele_idx += 1
                cur_screen_node.already_clicked_cnt += 1
                continue

            if cur_screen_node.ele_vis_map.get(cur_clickable_ele_uid, False) == False:
                # 拿到该组件的坐标x, y
                cur_clickable_ele_dict = RuntimeContent.get_instance().get_ele_uid_map_by_uid(cur_clickable_ele_uid)
                loc_x, loc_y = get_location(cur_clickable_ele_dict)
                cur_screen_node.ele_vis_map[cur_clickable_ele_uid] = True
                # 点击该组件
                LogUtils.log_info(f"正常点击组件&{clickable_ele_idx}: {cur_clickable_ele_uid}")
                StatRecorder.get_instance().inc_total_ele_cnt()
                RuntimeContent.get_instance().set_last_screen_node(cur_screen_node)
                RuntimeContent.get_instance().set_last_clickable_ele_uid(cur_clickable_ele_uid)

                if cur_screen_node.ele_uid_cnt_map.get(cur_clickable_ele_uid, None) is None:
                    cur_screen_node.ele_uid_cnt_map[cur_clickable_ele_uid] = 1
                else:
                    cur_screen_node.ele_uid_cnt_map[cur_clickable_ele_uid] += 1

                cls.__click(loc_x, loc_y)
                return

            else:
                # if cur_screen_node.ele_uid_cnt_map.get(cur_clickable_ele_uid) is not None and cur_screen_node.ele_uid_cnt_map.get(cur_clickable_ele_uid) > Config.get_instance().get_CLICK_MAX_CNT():
                #     LogUtils.log_info(f"该组件点击次数过多不点了&{clickable_ele_idx}: {cur_clickable_ele_uid}")
                #     cur_screen_node.already_clicked_cnt += 1
                #     clickable_ele_idx += 1
                if cur_screen_node.call_map.get(cur_clickable_ele_uid, None) is not None:
                    next_screen_node = cur_screen_node.call_map.get(cur_clickable_ele_uid, None)
                    next_screen_all_text = next_screen_node.ck_eles_text

                    if check_is_error_clickable_ele(cur_clickable_ele_uid) == True:
                        LogUtils.log_info(f"该组件会触发error screen因此跳过&{clickable_ele_idx}: {cur_clickable_ele_uid}")
                        cur_screen_node.already_clicked_cnt += 1
                        clickable_ele_idx += 1
                        continue
                    if check_is_errorscreen(next_screen_all_text, ScreenCompareStrategy(LCSComparator())) == True:
                        LogUtils.log_info(f"该组件会触发error screen因此跳过&{clickable_ele_idx}: {cur_clickable_ele_uid}")
                        cur_screen_node.already_clicked_cnt += 1
                        clickable_ele_idx += 1
                        continue
                    if next_screen_node.pkg_name != Config.get_instance().get_target_pkg_name():
                        LogUtils.log_info(f"clickmap--next界面非本app本包名&{clickable_ele_idx}: {cur_clickable_ele_uid}")
                        cur_screen_node.already_clicked_cnt += 1
                        clickable_ele_idx += 1
                        continue

                    res_sim, res_depth = get_max_sim_from_screen_depth_map(next_screen_all_text,
                                                                           ScreenCompareStrategy(LCSComparator()))
                    if res_depth == -1:
                        LogUtils.log_info(f"clickmap--next界面是UndefineDepth&{clickable_ele_idx}: {cur_clickable_ele_uid}")
                        cur_screen_node.already_clicked_cnt += 1
                        clickable_ele_idx += 1
                        continue

                    if res_sim >= Config.get_instance().screen_similarity_threshold and res_depth > Config.get_instance().maxDepth:
                        LogUtils.log_info(f"clickmap--next界面是超过限制层数的&{clickable_ele_idx}: {cur_clickable_ele_uid}")
                        cur_screen_node.already_clicked_cnt += 1
                        clickable_ele_idx += 1
                        continue

                    if next_screen_node.get_isWebView():
                        LogUtils.log_info(
                            f"clickmap--next界面是WebView&{clickable_ele_idx}: {cur_clickable_ele_uid}")
                        cur_screen_node.already_clicked_cnt += 1
                        clickable_ele_idx += 1
                        continue

                    if next_screen_node.is_screen_clickable_finished():
                        LogUtils.log_info(f"clickmap--next界面点击完成&{clickable_ele_idx}: {cur_clickable_ele_uid}")
                        cur_screen_node.already_clicked_cnt += 1
                        clickable_ele_idx += 1
                        continue
                    else:
                    #TODO
                    # if cur_screen_node.is_cur_callmap_finish(next_screen_all_text, ScreenCompareStrategy(LCSComparator())) == False:
                        # click_map指示存在部分没完成
                        cur_clickable_ele_dict = RuntimeContent.get_instance().get_ele_uid_map_by_uid(
                            cur_clickable_ele_uid)
                        loc_x, loc_y = get_location(cur_clickable_ele_dict)
                        LogUtils.log_info(f"clickmap没完成点击组件&{clickable_ele_idx}: {cur_clickable_ele_uid}")
                        StatRecorder.get_instance().inc_total_ele_cnt()
                        RuntimeContent.get_instance().set_last_screen_node(cur_screen_node)
                        RuntimeContent.get_instance().set_last_clickable_ele_uid(cur_clickable_ele_uid)

                        if cur_screen_node.ele_uid_cnt_map.get(cur_clickable_ele_uid, None) is None:
                            cur_screen_node.ele_uid_cnt_map[cur_clickable_ele_uid] = 0
                        else:
                            cur_screen_node.ele_uid_cnt_map[cur_clickable_ele_uid] += 1

                        cls.__click(loc_x, loc_y)

                        return
                else:
                    LogUtils.log_info(f"已点击过&{clickable_ele_idx}: {cur_clickable_ele_uid}")
                    cur_screen_node.already_clicked_cnt += 1
                    clickable_ele_idx += 1


    @classmethod
    def get_permission_screen_node(cls, content):
        cur_screen_pkg_name, cur_activity, ck_eles_text = get_screen_info_from_context(content)
        screen_text = get_screen_text(content)
        cur_screen_node = ScreenNode()
        # cur_screen_node.info = cur_screen_info
        cur_screen_node.pkg_name = cur_screen_pkg_name
        cur_screen_node.activity_name = cur_activity
        d = Config.get_instance().get_device()
        cur_ck_eles = content["cur_ck_eles"]
        merged_diff = content["merged_diff"]
        cur_screen_node.screen_text = screen_text
        cur_screen_node.clickable_elements = cur_ck_eles
        cur_screen_node.ck_eles_text = ck_eles_text
        cur_screen_node.merged_diff = merged_diff
        return cur_screen_node

    @classmethod
    def random_click_ele(cls, content):
        LogUtils.log_info("可能产生了权限框")
        cur_screen_node = get_cur_screen_node_from_context(content)

        cur_screen_node_clickable_eles = cur_screen_node.get_diff_or_clickable_eles()

        choose = random.randint(0, len(cur_screen_node_clickable_eles) - 1)
        cur_clickable_ele_uid = cur_screen_node_clickable_eles[choose]

        cur_clickable_ele_dict = RuntimeContent.get_instance().get_ele_uid_map_by_uid(cur_clickable_ele_uid)
        loc_x, loc_y = get_location(cur_clickable_ele_dict)
        cur_screen_node.ele_vis_map[cur_clickable_ele_uid] = True
        # 点击该组件
        LogUtils.log_info(f"随机点击组件&{choose}: {cur_clickable_ele_uid}")
        StatRecorder.get_instance().inc_total_ele_cnt()
        RuntimeContent.get_instance().set_last_screen_node(cur_screen_node)
        RuntimeContent.get_instance().set_last_clickable_ele_uid(cur_clickable_ele_uid)

        cls.__click(loc_x, loc_y)


    @classmethod
    def random_click_backpath_ele(cls, content):
        # TODO
        LogUtils.log_info("可能产生了不可去掉的框")
        cur_screen_node = get_cur_screen_node_from_context(content)

        cur_screen_node_clickable_eles = cur_screen_node.get_diff_or_clickable_eles()
        cur_screen_pkg_name, cur_activity, ck_eles_text = get_screen_info_from_context(content)

        # TODO
        candidate = None
        if cur_screen_node.candidate_random_clickable_eles is None or len(
                cur_screen_node.candidate_random_clickable_eles) == 0:
            candidate = cur_screen_node.build_candidate_random_clickable_eles()
        else:
            candidate = cur_screen_node.candidate_random_clickable_eles

        if candidate is None or len(candidate) == 0:
            return

        choose = random.randint(0, len(cur_screen_node.candidate_random_clickable_eles) - 1)
        cur_clickable_ele_uid = cur_screen_node.candidate_random_clickable_eles[choose]

        cur_clickable_ele_dict = RuntimeContent.get_instance().get_ele_uid_map_by_uid(cur_clickable_ele_uid)
        loc_x, loc_y = get_location(cur_clickable_ele_dict)
        cur_screen_node.ele_vis_map[cur_clickable_ele_uid] = True
        # 点击该组件
        LogUtils.log_info(f"随机点击组件&{choose}: {cur_clickable_ele_uid}")
        StatRecorder.get_instance().inc_total_ele_cnt()
        RuntimeContent.get_instance().set_last_screen_node(cur_screen_node)
        RuntimeContent.get_instance().set_last_clickable_ele_uid(cur_clickable_ele_uid)

        cls.__click(loc_x, loc_y)

    @classmethod
    def add_not_target_pkg_name_screen_call_graph(cls, content):
        screen_map = RuntimeContent.get_instance().get_screen_map()
        ck_eles_text = content["ck_eles_text"]
        if screen_map.get(ck_eles_text, False) is not False:
            cur_screen_node = screen_map.get(ck_eles_text)
        else:
            cur_screen_pkg_name, cur_activity, ck_eles_text = get_screen_info_from_context(content)
            screen_text = get_screen_text_from_context(content)
            # 初始化cur_screen_node信息
            cur_screen_node = ScreenNode()
            cur_screen_node.pkg_name = cur_screen_pkg_name
            cur_screen_node.screen_text = screen_text
            cur_screen_node.activity_name = cur_activity
            cur_ck_eles = content["cur_ck_eles"]
            cur_screen_node.clickable_elements = cur_ck_eles
            cur_screen_node.ck_eles_text = ck_eles_text
            # 将cur_screen加入到全局记录的screen_map
            RuntimeContent.get_instance().put_screen_map(ck_eles_text, cur_screen_node)
        # 将cur_screen加入到last_screen的子节点
        last_screen_node = RuntimeContent.get_instance().get_last_screen_node()
        if last_screen_node is not None:
            last_screen_node.add_child(cur_screen_node)

        last_clickable_ele_uid = RuntimeContent.get_instance().get_last_clickable_ele_uid()
        if last_clickable_ele_uid is not None and last_clickable_ele_uid != "":
            cur_screen_node.append_last_ck_ele_uid_list(last_clickable_ele_uid)

        if last_screen_node is not None:
            if last_screen_node.ck_eles_text == cur_screen_node.ck_eles_text:
                LogUtils.log_info("回到自己")
                last_screen_node.update_callmap_item(RuntimeContent.get_instance().get_last_clickable_ele_uid())
                pass
            elif check_cycle(cur_screen_node, last_screen_node, ScreenCompareStrategy(LCSComparator())) == True:
                # 产生了回边
                last_screen_node.cycle_set.add(RuntimeContent.get_instance().get_last_clickable_ele_uid())
                LogUtils.log_info("产生回边")
                last_screen_node.update_callmap_item(RuntimeContent.get_instance().get_last_clickable_ele_uid())
                pass
            else:
                if last_screen_node.ck_eles_text != "root":
                    # call_map会更新
                    last_screen_node.call_map[
                        RuntimeContent.get_instance().get_last_clickable_ele_uid()] = cur_screen_node
                # else:
                #     first_screen_text = ck_eles_text

        return cur_screen_node

    @classmethod
    def add_new_screen_call_graph(cls, content):
        cur_screen_pkg_name, cur_activity, ck_eles_text = get_screen_info_from_context(content)
        screen_text = get_screen_text_from_context(content)
        # 初始化cur_screen_node信息
        cur_screen_node = ScreenNode()
        cur_screen_node.pkg_name = cur_screen_pkg_name
        cur_screen_node.screen_text = screen_text
        cur_screen_node.activity_name = cur_activity
        cur_ck_eles = content["cur_ck_eles"]
        merged_diff = content["merged_diff"]
        sim = content.get("sim", None)
        most_similar_screen_node = content.get("most_similar_screen_node", None)
        if sim is not None and sim >= 0.70:
            # TODO
            most_sim_clickable_elements = most_similar_screen_node.get_exactly_clickable_eles()
            diff_list = get_two_clickable_eles_diff(cur_ck_eles, most_sim_clickable_elements)
            cur_screen_node.diff_clickable_elements = diff_list
        #     cur_screen_node.clickable_elements = clickable_eles
        #     # diff_text = get_screen_all_text_from_dict(diff_list, ele_uid_map)
        #     # ck_eles_text = diff_text
        #     cur_screen_node.all_text = ck_eles_text
        #     screen_map[ck_eles_text] = cur_screen_node
        # else:
        cur_screen_node.clickable_elements = cur_ck_eles
        cur_screen_node.ck_eles_text = ck_eles_text
        cur_screen_node.merged_diff = merged_diff

        # 将cur_screen加入到全局记录的screen_map
        RuntimeContent.get_instance().put_screen_map(ck_eles_text, cur_screen_node)
        # 将cur_screen加入到last_screen的子节点
        last_screen_node = RuntimeContent.get_instance().get_last_screen_node()
        if last_screen_node is not None:
            last_screen_node.add_child(cur_screen_node)



        last_clickable_ele_uid = RuntimeContent.get_instance().get_last_clickable_ele_uid()
        if last_clickable_ele_uid is not None and last_clickable_ele_uid != "":
            cur_screen_node.append_last_ck_ele_uid_list(last_clickable_ele_uid)

        if last_screen_node is not None:
            if last_screen_node.ck_eles_text == cur_screen_node.ck_eles_text:
                LogUtils.log_info("回到自己")
                last_screen_node.update_callmap_item(RuntimeContent.get_instance().get_last_clickable_ele_uid())
                pass
            elif check_cycle(cur_screen_node, last_screen_node, ScreenCompareStrategy(LCSComparator())) == True:
                # 产生了回边
                check_cycle(cur_screen_node, last_screen_node, ScreenCompareStrategy(LCSComparator()))
                last_screen_node.cycle_set.add(RuntimeContent.get_instance().get_last_clickable_ele_uid())
                LogUtils.log_info("产生回边")
                last_screen_node.update_callmap_item(RuntimeContent.get_instance().get_last_clickable_ele_uid())
                pass
            else:
                # call_map会更新
                last_screen_node.call_map[RuntimeContent.get_instance().get_last_clickable_ele_uid()] = cur_screen_node
                # else:
                #     first_screen_text = ck_eles_text

        return cur_screen_node

    @classmethod
    def add_exist_screen_call_graph(cls, content):
        # cur_screen_pkg_name, cur_activity, ck_eles_text, cur_screen_info = get_screen_info(d)
        cur_screen_pkg_name, cur_activity, ck_eles_text = get_screen_info_from_context(content)
        cur_screen_node = get_cur_screen_node_from_context(content)

        # 将cur_screen加入到last_screen的子节点
        last_screen_node = RuntimeContent.get_instance().get_last_screen_node()
        if last_screen_node is not None:
            last_screen_node.add_child(cur_screen_node)
        last_clickable_ele_uid = RuntimeContent.get_instance().get_last_clickable_ele_uid()
        if last_clickable_ele_uid is not None and last_clickable_ele_uid != "":
            cur_screen_node.append_last_ck_ele_uid_list(last_clickable_ele_uid)

        if last_screen_node is not None:
            if last_screen_node.ck_eles_text == cur_screen_node.ck_eles_text:
                LogUtils.log_info("回到自己")
                last_screen_node.update_callmap_item(RuntimeContent.get_instance().get_last_clickable_ele_uid())
                pass
            elif check_cycle(cur_screen_node, last_screen_node, ScreenCompareStrategy(LCSComparator())) == True:
                # 产生了回边
                last_screen_node.cycle_set.add(RuntimeContent.get_instance().get_last_clickable_ele_uid())
                LogUtils.log_info("产生回边")
                last_screen_node.update_callmap_item(RuntimeContent.get_instance().get_last_clickable_ele_uid())
                pass
            else:
                if last_screen_node.ck_eles_text != "root":
                    # call_map会更新
                    last_screen_node.call_map[
                        RuntimeContent.get_instance().get_last_clickable_ele_uid()] = cur_screen_node
                # else:
                #     first_screen_text = ck_eles_text

        return cur_screen_node

    @classmethod
    def handle_kill_other_app(cls, content):
        non_pkg_name = content["cur_screen_pkg_name"]
        d = Config.get_instance().get_device()
        d.app_stop(non_pkg_name)
        time.sleep(3)
        start_pkg_name = Config.get_instance().get_target_pkg_name()
        d.app_start(start_pkg_name)
        time.sleep(3)

    @classmethod
    def handle_exist_screen(cls, content):
        cur_screen_node = cls.add_exist_screen_call_graph(content)
        print_screen_info(content, False)
        cls.click_one_ele(content)

    @classmethod
    def handle_terminate(cls, content):
        raise Exception("完成")

    @classmethod
    def handle_new_screen(cls, content):
        cur_screen_node = cls.add_new_screen_call_graph(content)
        content["cur_screen_node"] = cur_screen_node
        print_screen_info(content, True)
        cls.click_one_ele(content)

    @classmethod
    def handle_outsystem_special_screen(cls, content):
        cur_screen_node = cls.add_not_target_pkg_name_screen_call_graph(content)
        content["cur_screen_node"] = cur_screen_node
        print_screen_info(content, True)
        cls.random_click_ele(content)

    @classmethod
    def handle_special_screen(cls, content):
        cur_screen_node = cls.add_exist_screen_call_graph(content)
        print_screen_info(content, True)
        cls.random_click_backpath_ele(content)

    @classmethod
    def handle_system_permission_screen(cls, content):
        cur_screen_node = cls.add_not_target_pkg_name_screen_call_graph(content)
        content["cur_screen_node"] = cur_screen_node
        print_screen_info(content, True)
        cls.random_click_ele(content)

    @classmethod
    def handle_exit_app(cls, content):
        cur_screen_node = cls.add_not_target_pkg_name_screen_call_graph(content)
        content["cur_screen_node"] = cur_screen_node
        cls.__press_back()
        RuntimeContent.get_instance().set_last_screen_node(None)
        RuntimeContent.get_instance().set_last_clickable_ele_uid("")

    @classmethod
    def handle_double_press(cls, content):
        cls.__double_press_back()
        RuntimeContent.get_instance().set_last_screen_node(None)
        RuntimeContent.get_instance().set_last_clickable_ele_uid("")

    @classmethod
    def handle_inputmethod(cls, content):
        cls.__press_back()
        # 输入法不需要处理
        # RuntimeContent.get_instance().set_last_screen_node(None)
        # RuntimeContent.get_instance().set_last_clickable_ele_uid("")

    @classmethod
    def handle_WebView_screen(cls, content):
        cur_screen_node = cls.add_not_target_pkg_name_screen_call_graph(content)
        cur_screen_node.set_isWebView(True)
        content["cur_screen_node"] = cur_screen_node
        print_screen_info(content, True)
        cls.__press_back()
        RuntimeContent.get_instance().set_last_screen_node(None)
        RuntimeContent.get_instance().set_last_clickable_ele_uid("")

    @classmethod
    def handle_ExceedDepth(cls, content):
        cur_screen_node = cls.add_not_target_pkg_name_screen_call_graph(content)
        cur_screen_node.set_isWebView(True)
        content["cur_screen_node"] = cur_screen_node
        print_screen_info(content, True)
        cls.__press_back()
        RuntimeContent.get_instance().set_last_screen_node(None)
        RuntimeContent.get_instance().set_last_clickable_ele_uid("")

    @classmethod
    def handle_UndefineDepth(cls, content):
        cur_screen_node = cls.add_not_target_pkg_name_screen_call_graph(content)
        cur_screen_node.set_isWebView(True)
        content["cur_screen_node"] = cur_screen_node
        print_screen_info(content, True)
        cls.__press_back()
        RuntimeContent.get_instance().set_last_screen_node(None)
        RuntimeContent.get_instance().set_last_clickable_ele_uid("")

    @classmethod
    def handle_finish_screen(cls, content):
        cur_screen_node = cls.add_exist_screen_call_graph(content)
        cls.__press_back()
        RuntimeContent.get_instance().set_last_screen_node(None)
        RuntimeContent.get_instance().set_last_clickable_ele_uid("")

    @classmethod
    def handle_error_screen(cls, content):
        cls.__press_back()
        RuntimeContent.get_instance().set_last_screen_node(None)
        RuntimeContent.get_instance().set_last_clickable_ele_uid("")

    @classmethod
    def handle_stuck_restart(cls, content):
        cur_screen_node = cls.add_not_target_pkg_name_screen_call_graph(content)
        content["cur_screen_node"] = cur_screen_node

        cur_screen_ck_eles_text = content["ck_eles_text"]
        RuntimeContent.get_instance().append_error_screen_list(cur_screen_ck_eles_text)
        #TODO 应该把所有last_clickable_ele_uid加进来
        last_ck_ele_uid = RuntimeContent.get_instance().get_last_clickable_ele_uid()
        if last_ck_ele_uid is not None and last_ck_ele_uid != "":
            RuntimeContent.get_instance().append_error_clickable_ele_uid_list(last_ck_ele_uid)
        cur_screen_node = content.get("cur_screen_node", None)
        if cur_screen_node is not None:
            last_ck_ele_uid_list = cur_screen_node.get_last_ck_ele_uid_list()
            RuntimeContent.get_instance().append_more_error_ck_ele_uid_list(last_ck_ele_uid_list)

        raise RestartException("重启机制")

    @classmethod
    def handle_homes_screen_restart(cls, content):
        raise RestartException("重启机制")

    @classmethod
    def __press_back(cls):
        d = Config.get_instance().get_device()
        d.press("back")
        LogUtils.log_info("进行回退")
        time.sleep(Config.get_instance().get_sleep_time_sec())
        return

    @classmethod
    def __double_press_back(cls):
        d = Config.get_instance().get_device()
        d.press("back")
        d.press("back")
        time.sleep(Config.get_instance().get_sleep_time_sec())
        return

    @classmethod
    def __click(cls, x, y):
        d = Config.get_instance().get_device()
        d.click(x, y)
        time.sleep(Config.get_instance().get_sleep_time_sec())
        return
