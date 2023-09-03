from ScreenCompareStrategy import *
from RuntimeContent import *
from Utils.LogUtils import *
from Config import *

# 检测多层环
def check_cycle(cur_node: ScreenNode, last_node: ScreenNode, screen_compare_strategy: ScreenCompareStrategy):
    similarity = screen_compare_strategy.compare_screen(cur_node.ck_eles_text, last_node.ck_eles_text)
    if similarity >= Config.get_instance().screen_similarity_threshold:
        return True

    # if cur_node.children is None or len(cur_node.children) == 0:
    #     return False
    if cur_node.call_map is None or len(cur_node.call_map) == 0 or cur_node.call_map is {}:
        return False
    # for child in cur_node.children:
    #     if screen_compare_strategy.compare_screen(child.all_text, last_node.all_text)[0] == True:
    #         return True
    #     else:
    #         res = check_cycle(child, last_node, screen_compare_strategy)
    #         if res == True:
    #             return True
    for child in cur_node.call_map.values():
        child_sim = screen_compare_strategy.compare_screen(child.ck_eles_text, last_node.ck_eles_text)
        if child_sim >= Config.get_instance().screen_similarity_threshold:
            return True
        else:
            res = check_cycle(child, last_node, screen_compare_strategy)
            if res == True:
                return True
    return False


def is_non_necessary_click(cur_clickable_ele_dict):
    if cur_clickable_ele_dict.get("resource-id") == "com.alibaba.android.rimet:id/toolbar":
        return True
    if cur_clickable_ele_dict.get("resource-id") == "com.alibaba.android.rimet:id/back_layout":
        return True

    text = cur_clickable_ele_dict.get("text")

    # TODO 暂时忽略钉钉创建团队的场景
    non_necessary_list = ["相机", "照片", "拍照", "手机文件", "相册", "相片", "拍摄", "关注", "粉丝", "退出登陆", "注销", "付款",
                          "退出登录", "退出当前账号", "下载", "分享", "浏览器", "安装", "浮窗", "更新", "支付", "预订", "评论", "换一换",
                          "image", 'Image', "photo", "Photo", "视频", "语音", "创建团队", "直播"]
    for non_necessary_str in non_necessary_list:
        if non_necessary_str in text:
            return True

    return False


def print_screen_info(content, is_new):
    cur_screen_node = get_cur_screen_node_from_context(content)
    LogUtils.log_info("*" * 100)
    if is_new:
        LogUtils.log_info(f"该screen为新: {cur_screen_node.ck_eles_text[0:-1]}--总共{len(cur_screen_node.clickable_elements)}, 减少{cur_screen_node.merged_diff}")
        if cur_screen_node.diff_clickable_elements is not None:
            LogUtils.log_info(f"差分后的数量为 {len(cur_screen_node.diff_clickable_elements)}")

    else:
        LogUtils.log_info(f"该screen已存在: {cur_screen_node.ck_eles_text[0:-1]}--总共{len(cur_screen_node.clickable_elements)}, 减少{cur_screen_node.merged_diff}")
        if cur_screen_node.diff_clickable_elements is not None:
            LogUtils.log_info(f"差分后的数量为 {len(cur_screen_node.diff_clickable_elements)}")

    LogUtils.log_info("*" * 100)


# def get_two_clickable_eles_diff(cur_eles, cur_activity, last_eles, last_activity):
#     if last_eles is None or cur_eles is None or len(last_eles) == 0 or len(cur_eles) == 0:
#         return False, None
#     if cur_activity != last_activity:
#         return False, None
#     if len(cur_eles) <= len(last_eles):
#         return False, None
#
#     # union_eles = union(d, cur_eles, cur_activity, last_eles, last_activity)
#     intersection_eles = list(set(cur_eles).intersection(set(last_eles)))
#     is_overlap = False
#     if len(intersection_eles) / len(last_eles) >= 0.80:
#         diff_eles = []
#         is_overlap = True
#         diff_eles = list(set(cur_eles).difference(last_eles))
#         Logger.get_instance().print(f"出现了重叠,可能为框,差分之后数量为{len(diff_eles)}")
#         return is_overlap, diff_eles
#     else:
#         return is_overlap, None

def get_two_clickable_eles_diff(cur_eles, last_eles):
    if last_eles is None or cur_eles is None or len(last_eles) == 0 or len(cur_eles) == 0:
        return None
    # if cur_activity != last_activity:
    #     return None
    # if len(cur_eles) <= len(last_eles):
    #     return False, None

    # union_eles = union(d, cur_eles, cur_activity, last_eles, last_activity)
    diff_eles = list(set(cur_eles).difference(last_eles))
    LogUtils.log_info(f"出现了重叠,可能为框,差分之后数量为{len(diff_eles)}")
    return diff_eles




def get_screen_info_from_context(content):
    cur_screen_pkg_name = content["cur_screen_pkg_name"]
    cur_activity = content["cur_activity"]
    ck_eles_text = content["ck_eles_text"]

    return cur_screen_pkg_name, cur_activity, ck_eles_text

def get_screen_text_from_context(content):
    return content["screen_text"]


def get_cur_screen_node_from_context(content):
    cur_screen_node = content["cur_screen_node"]
    return cur_screen_node

def get_screen_all_text_from_dict(clickable_eles, ele_uid_map):
    text = ""
    for ele_uid in clickable_eles:
        ele_dict = ele_uid_map[ele_uid]
        text += ele_dict.get("text")
    return text


def get_screennode_from_screenmap(screen_map: dict, ck_eles_text: str):
    if screen_map.get(ck_eles_text, None) is None:
        return None
    else:
        return screen_map.get(ck_eles_text)


# 从screen_map里得到取出和ck_eles_text满足相似度阈值且相似度最高的screen_node
def get_screennode_from_screenmap_by_similarity(ck_eles_text: str, screen_compare_strategy) -> ScreenNode:
    screen_map = RuntimeContent.get_instance().get_screen_map()
    if screen_map.get(ck_eles_text, False) is False:
        # 如果没有,则遍历找满足相似度阈值的
        max_similarity = 0
        res_node = None
        for candidate_ck_eles_text in screen_map.keys():
            cur_similarity = screen_compare_strategy.compare_screen(ck_eles_text, candidate_ck_eles_text)
            if cur_similarity >= Config.get_instance().screen_similarity_threshold:
                if cur_similarity > max_similarity:
                    max_similarity = cur_similarity
                    res_node = screen_map.get(candidate_ck_eles_text)
        # 返回的要么是None, 要么是相似性最大的screen_node
        return res_node

    # 说明该节点之前存在screen_map
    else:
        return screen_map.get(ck_eles_text)


def get_max_sim_from_screen_depth_map(ck_eles_text:str, screen_compare_strategy) -> tuple[float|int]:
    screen_depth_map = RuntimeContent.get_instance().screen_depth_map
    if screen_depth_map.get(ck_eles_text, False) is False:
        max_sim = 0
        res_depth = -1
        for candidate_ck_eles_text  in screen_depth_map.keys():
            cur_sim = screen_compare_strategy.compare_screen(ck_eles_text, candidate_ck_eles_text)
            if cur_sim >= Config.get_instance().screen_similarity_threshold:
                if cur_sim > max_sim:
                    max_sim = cur_sim
                    res_depth = screen_depth_map.get(candidate_ck_eles_text)
        return max_sim, res_depth
    return 1.0, screen_depth_map.get(ck_eles_text)
def get_max_similarity_screen_node(ck_eles_text: str, screen_compare_strategy) -> tuple[float | ScreenNode]:
    screen_map = RuntimeContent.get_instance().get_screen_map()
    if screen_map.get(ck_eles_text, False) is False:
        # 如果没有,则遍历找满足相似度阈值的
        max_similarity = 0
        res_node = None
        for candidate_ck_eles_text in screen_map.keys():
            cur_similarity = screen_compare_strategy.compare_screen(ck_eles_text, candidate_ck_eles_text)
            if cur_similarity >= Config.get_instance().screen_similarity_threshold:
                if cur_similarity > max_similarity:
                    max_similarity = cur_similarity
                    res_node = screen_map.get(candidate_ck_eles_text)
        # 返回的要么是None, 要么是相似性最大的screen_node
        return max_similarity, res_node

    # 说明该节点之前存在screen_map
    else:
        return 1.0, screen_map.get(ck_eles_text)

# def get_screennode_from_diffmap(diff_map: dict, screen_map, screen_compare_strategy):
#     for ck_eles_text in diff_map.keys():
#         res = get_screennode_from_screenmap(screen_map, ck_eles_text, screen_compare_strategy)
#         if res is not None:
#             return res
#     return None



