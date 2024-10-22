import minimalmodbus
import time
import threading
from flask import Flask, render_template_string

# 配置电表
instrument = minimalmodbus.Instrument('/dev/ttyUSB0', 1)
instrument.serial.baudrate = 9600
instrument.serial.bytesize = 8
instrument.serial.parity = minimalmodbus.serial.PARITY_NONE
instrument.serial.stopbits = 1
instrument.serial.timeout = 1

# 创建Flask应用
app = Flask(__name__)

# 初始化电力参数存储
current_values = {
    'voltage_a': 0.0,
    'voltage_b': 0.0,
    'voltage_c': 0.0,
    'current_a': 0.0,
    'current_b': 0.0,
    'current_c': 0.0,
    'current_n': 0.0
}

# 网页模板，加入进度条表示电流状态
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Seeed机房电源监控</title>
    <meta http-equiv="refresh" content="2">
    <style>
        body {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            font-family: Arial, sans-serif;
        }
        .container {
            width: 400px;
            text-align: center;
        }
        .progress-bar {
            width: 300px;
            background-color: #e0e0e0;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px auto;
        }
        .progress {
            height: 20px;
            text-align: center;
            line-height: 20px;
            color: white;
            font-weight: bold;
        }
        .progress.green {
            background-color: #4caf50;
        }
        .progress.yellow {
            background-color: #ffeb3b;
            color: black;
        }
        .progress.red {
            background-color: #f44336;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>***机房电源监控</h1>
        <h2>电压</h2>
        <p>A相电压: {{ voltage_a }} V</p>
        <p>B相电压: {{ voltage_b }} V</p>
        <p>C相电压: {{ voltage_c }} V</p>
        <h2>电流</h2>
        <div>
            <p>A相电流: {{ current_a }} A</p>
            <div class="progress-bar">
                <div class="progress {{ current_a_color }}" style="width: {{ current_a_percent }}%;">{{ current_a_percent }}%</div>
            </div>
        </div>
        <div>
            <p>B相电流: {{ current_b }} A</p>
            <div class="progress-bar">
                <div class="progress {{ current_b_color }}" style="width: {{ current_b_percent }}%;">{{ current_b_percent }}%</div>
            </div>
        </div>
        <div>
            <p>C相电流: {{ current_c }} A</p>
            <div class="progress-bar">
                <div class="progress {{ current_c_color }}" style="width: {{ current_c_percent }}%;">{{ current_c_percent }}%</div>
            </div>
        </div>
        <div>
            <p>N线电流: {{ current_n }} A</p>
            <div class="progress-bar">
                <div class="progress {{ current_n_color }}" style="width: {{ current_n_percent }}%;">{{ current_n_percent }}%</div>
            </div>
        </div>
    </div>
</body>
</html>
"""

# 电流进度条颜色计算
def get_progress_color(current_value):
    percent = (current_value / 63) * 100
    if percent < 80:
        return "green"
    elif percent < 90:
        return "yellow"
    else:
        return "red"

def read_voltage_and_current():
    try:
        # 读取A、B、C相电压
        voltage_a = instrument.read_float(0x2100, 3)  # A相电压
        voltage_b = instrument.read_float(0x2102, 3)  # B相电压
        voltage_c = instrument.read_float(0x2104, 3)  # C相电压

        # 读取A、B、C相电流
        current_a = instrument.read_float(0x210C, 3)  # A相电流
        current_b = instrument.read_float(0x210E, 3)  # B相电流
        current_c = instrument.read_float(0x2110, 3)  # C相电流

        # 读取N线电流
        current_n = instrument.read_float(0x2112, 3)  # N线电流

        # 更新当前电力参数，设置显示格式
        current_values['voltage_a'] = round(voltage_a, 1)
        current_values['voltage_b'] = round(voltage_b, 1)
        current_values['voltage_c'] = round(voltage_c, 1)
        current_values['current_a'] = round(current_a, 2)
        current_values['current_b'] = round(current_b, 2)
        current_values['current_c'] = round(current_c, 2)
        current_values['current_n'] = round(current_n, 2)

        # 计算电流的百分比和颜色
        current_values['current_a_percent'] = round((current_a / 63) * 100, 1)
        current_values['current_b_percent'] = round((current_b / 63) * 100, 1)
        current_values['current_c_percent'] = round((current_c / 63) * 100, 1)
        current_values['current_n_percent'] = round((current_n / 63) * 100, 1)

        current_values['current_a_color'] = get_progress_color(current_a)
        current_values['current_b_color'] = get_progress_color(current_b)
        current_values['current_c_color'] = get_progress_color(current_c)
        current_values['current_n_color'] = get_progress_color(current_n)

    except Exception as e:
        print(f"读取电压或电流失败: {e}")

# 后台线程持续读取电压和电流值
def update_values():
    while True:
        read_voltage_and_current()
        time.sleep(2)  # 每隔2秒读取一次

# 网页路由
@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, **current_values)

# 启动后台线程来更新电力参数
threading.Thread(target=update_values, daemon=True).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6900)
