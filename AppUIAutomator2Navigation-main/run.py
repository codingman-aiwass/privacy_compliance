from FSM import *
from Utils.JsonUtils import *
from RestartException import RestartException
from Utils.SavedInstanceUtils import *
from queue import Queue
from FridaLibs.mq_producer import Producer
from Utils.DrawGraphUtils import *

def suppress_keyboard_interrupt_message():
    old_excepthook = sys.excepthook

    def new_hook(exctype, value, traceback):
        if exctype != KeyboardInterrupt:
            old_excepthook(exctype, value, traceback)
        else:
            LogUtils.log_info('\nKeyboardInterrupt ...')
            LogUtils.log_info('do something after Interrupt ...')
            StatRecorder.get_instance().print_result()
            RuntimeContent.get_instance().clear_state_list()
            RuntimeContent.get_instance().clear_screen_list()
            JsonUtils.dump_screen_map_to_json()
            SavedInstanceUtils.dump_pickle(RuntimeContent.get_instance())

            # 绘制App界面跳转图
            if Config.get_instance().isDrawAppCallGraph:
                DrawGraphUtils.draw_callgraph(Config.get_instance().get_CollectDataName())
    sys.excepthook = new_hook


if __name__ == "__main__":
    # pkgName = sys.argv[1]
    # with open('tmp.txt', 'w') as f:
    #     f.write(pkgName)

    LogUtils.setup()
    if Config.get_instance().is_saved_start:
        runtime = SavedInstanceUtils.load_pickle(Config.get_instance().get_pickle_file_name())
        root = runtime.screen_map["root"]
    else:
        root = ScreenNode()
        root.ck_eles_text = "root"
        RuntimeContent.get_instance().set_last_screen_node(root)
        RuntimeContent.get_instance().set_last_clickable_ele_uid("dummy_root_element")
        RuntimeContent.get_instance().put_screen_map("root", root)

    suppress_keyboard_interrupt_message()
    # 计时开始
    StatRecorder.get_instance().set_start_time()

    restart_cnt = 0
    while True:
        ## 启动app
        d = Config.get_instance().get_device()
        d.app_start(Config.get_instance().get_target_pkg_name(), use_monkey=True)
        time.sleep(10)

        queue = Queue()
        producer = Producer('Producer', queue)
        consumer_fsm = FSM('Consumer', queue)
        # consumer = Consumer('Con', queue)
        producer.start()
        consumer_fsm.start()
        # producer.join()
        # consumer.join()

        try:
            RuntimeContent.get_instance().set_last_screen_node(root)
            FSM.start()
        except RestartException as e:
            StatRecorder.get_instance().inc_restart_cnt()
            LogUtils.log_info("需要重启")
            logging.exception(e)
            StatRecorder.get_instance().print_result()
            RuntimeContent.get_instance().clear_state_list()
            RuntimeContent.get_instance().clear_screen_list()
            JsonUtils.dump_screen_map_to_json()
            SavedInstanceUtils.dump_pickle(RuntimeContent.get_instance())
            d.app_stop(Config.get_instance().get_target_pkg_name())
            time.sleep(10)
        except Exception as e:
            logging.exception(e)
            StatRecorder.get_instance().print_result()
            RuntimeContent.get_instance().clear_state_list()
            RuntimeContent.get_instance().clear_screen_list()
            JsonUtils.dump_screen_map_to_json()
            SavedInstanceUtils.dump_pickle(RuntimeContent.get_instance())
            break

        # 绘制App界面跳转图
        if Config.get_instance().isDrawAppCallGraph:
            DrawGraphUtils.draw_callgraph(Config.get_instance().get_CollectDataName())

    LogUtils.log_info("程序结束")
