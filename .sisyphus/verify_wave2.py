from src.utils.data_loader import parse_json5_content, format_pulse_export, format_library_export
from src.utils.signal_ops import generate_wave, smooth_array
from src.ui.styles import MAIN_STYLESHEET
from src.ui.wave_canvas import WaveCanvas

print('data_loader OK')
print('signal_ops OK')
print('styles len=' + str(len(MAIN_STYLESHEET)))
print('wave_canvas type=' + str(type(WaveCanvas)))

r = generate_wave(0, 1, 100, 10)
assert len(r) == 10 and r[0] == 0 and max(r) > 90, 'generate_wave FAIL: ' + str(r)
print('generate_wave PASS: ' + str(r))

sm = smooth_array([0, 100, 0, 100, 0], 5)
assert sm[1] == 50 and sm[3] == 50, 'smooth_array FAIL: ' + str(sm)
print('smooth_array PASS: ' + str(sm))

c = MAIN_STYLESHEET
assert '#121212' in c and '#00ffcc' in c and 'QScrollBar' in c and '高对比度' in c
print('MAIN_STYLESHEET content PASS')

test_input = "[{id: 'test', name: 'wave1', pulseData: ['0A0A0A0A64646464']}]"
result = parse_json5_content(test_input)
assert len(result) == 1 and result[0]['name'] == 'wave1', 'parse_json5 FAIL: ' + str(result)
print('parse_json5_content PASS')

methods = ['update_geometry','paintEvent','draw_plot','handle_mouse','mousePressEvent','mouseMoveEvent','mouseReleaseEvent']
missing = [m for m in methods if not hasattr(WaveCanvas, m)]
assert not missing, 'WaveCanvas MISSING: ' + str(missing)
print('WaveCanvas methods PASS')

print('ALL WAVE 2 CHECKS PASSED')
