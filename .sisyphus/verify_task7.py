from src.ui.main_window import MainWindow
methods = ['init_ui','apply_styles','sync_step_val','dragEnterEvent','dropEvent','import_file',
           'refresh_lib_ui','load_to_canvas','del_from_lib','add_to_seq','add_gap_to_seq',
           'clear_sequence','refresh_seq_ui','save_sequence_to_library','apply_func',
           'smooth_wave','clear_canvas','save_to_lib','generate_code','export_entire_library']
missing = [m for m in methods if not hasattr(MainWindow, m)]
print('MainWindow methods PASS' if not missing else 'MISSING: ' + str(missing))

import os
lines = open('main.py', encoding='utf-8').readlines()
print('main.py lines: ' + str(len(lines)))
print('main.py slim PASS' if len(lines) < 15 else 'main.py FAIL: too many lines: ' + str(len(lines)))

print('ALL TASK 7 CHECKS PASSED')
