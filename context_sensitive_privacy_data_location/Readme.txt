For static:
1. run `run_jar.py`
2. run `data_item_infer.py`
3. run `label_new_or_old.py` to distinguish the data item from traditional keyword list.

For dynamic:
1. get dynamic result (.json) from DongPeng.
2. run `integrate_dynamic.py` to convert the dynamic result to static immediate result, like the format of `run_jar.py`.
3. run `data_item_infer.py`
4. run `label_new_or_old.py`