import json
import sys
import os
import requests # 需要这个库来下载历史文件
import datetime
import pytz # 导入 pytz 库

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdates
# from matplotlib import font_manager # 字体管理器，当前方案不需要手动管理字体


# <--- 配置 Matplotlib (简化版，移除中文特定设置) --->
# 移除所有中文字体相关的 rcParams 设置
plt.rcParams['axes.unicode_minus'] = False # 保留这个，解决负号'-'显示问题


# 获取输入JSON文件路径 (预计为 config.json)
if len(sys.argv) < 2:
    print("Usage: python count_rules.py <path_to_config.json>", file=sys.stderr)
    sys.exit(1)

input_json_path = sys.argv[1]

# 定义输出文件的目录和文件名
output_dir = "badge_data"
output_json_filename = "domain_count_data.json"
output_json_path = os.path.join(output_dir, output_json_filename)

history_filename = "count_history.json"
history_output_path = os.path.join(output_dir, history_filename)
chart_image_filename = "domain_rules_trend.png"
# <--- 修正：删除重复且错误的下一行 --->
chart_image_path = os.path.join(output_dir, chart_image_filename)


# GitHub Pages 上历史文件的原始 URL (用于下载现有历史)
github_username = "MT-Y-TM" # 请确保这里是你的 GitHub 用户名
repo_name = "Fuck_All_Web_Restrictions" # 请确保这里是你的仓库名
history_raw_url = f"https://raw.githubusercontent.com/{github_username}/{repo_name}/gh-pages/{history_filename}"

# <--- 移除字体下载相关的定义和 try/except 块 --->
# 所有字体下载相关的变量定义和整个 try/except 代码块都已移除

# 定义北京时区
beijing_tz = pytz.timezone('Asia/Shanghai')

try:
    # 确保输出目录存在 (在保存文件前创建)
    os.makedirs(output_dir, exist_ok=True)

    # 读取输入 JSON 文件 (移除调试打印)
    with open(input_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 统计 rules 列表中包含 "domain" 键的字典数量 (方案 A)
    count = 0
    # 检查根是否是字典，并且包含 'rules' 键，且 'rules' 的值是列表
    if isinstance(data, dict) and 'rules' in data and isinstance(data['rules'], list):
        rules_list = data['rules']
        for i, rule in enumerate(rules_list):
            # 检查当前规则元素是否是字典，并且是否包含 "domain" 这个键
            if isinstance(rule, dict) and "domain" in rule:
                count += 1
    # else: print(...) # 已移除 (最后的统计总数打印)
    # 如果路径未找到，计数仍然是 0 (无需额外的 else 块来设置 count=0)


    # 准备 Shields.io 徽章数据 (保留逻辑)
    badge_data = {
        "schemaVersion": 1,
        "label": "Domain Rules",
        "message": str(count),
        "color": "blue"
    }

    # 处理历史数据 (保留逻辑，移除调试打印)
    history_data = []
    try:
        response = requests.get(history_raw_url)
        response.raise_for_status()
        history_data = response.json()
        if not isinstance(history_data, list):
            history_data = []
    except requests.exceptions.RequestException as e:
        if isinstance(e, requests.exceptions.HTTPError) and e.response.status_code == 404:
            history_data = []
        else:
            # 保留下载历史失败时的警告，但不影响流程
            print(f"Warning: Could not download existing history file: {e}", file=sys.stderr)
            history_data = []

    # 获取当前 UTC 时间戳 (这里保持获取 UTC 时间，方便存储和处理)
    now_utc = datetime.datetime.now(datetime.UTC)
    # 将 UTC 时间保存为 ISO 格式，包含时区信息 'Z' (代表 UTC) 或 '+00:00'
    # fromisoformat 可以正确解析
    timestamp = now_utc.isoformat()
    new_history_entry = {"date": timestamp, "count": count}

    # 将新条目追加到历史数据列表 (检查是否重复)
    if not history_data or history_data[-1].get("count") != count:
         history_data.append(new_history_entry)
    # else: print(...) # 已移除 (计数未改变提示)


    # 生成图表图片 (保留逻辑，移除调试打印)
    try:
        # 检查是否有足够的数据点来绘制图表 (至少一个点)
        if not history_data:
             pass # 跳过绘图如果历史数据为空
        else:
            # 解析 UTC 时间戳并转换为 UTC 感知的 datetime 对象
            utc_dates = [datetime.datetime.fromisoformat(entry['date']) for entry in history_data]
            counts_list = [entry['count'] for entry in history_data]

            # 将 UTC 时间转换为北京时间用于绘图
            beijing_dates = [utc_date.astimezone(beijing_tz) for utc_date in utc_dates]

            # 实际绘图只需要至少一个点
            if not beijing_dates: # 使用转换后的日期列表进行检查
                 pass
            else: # 只有当 beijing_dates 非空时才进行绘图
                fig, ax = plt.subplots(figsize=(10, 5))

                # 修改背景颜色
                fig_bg_color = '#FCE4EC' # Material Design Pink 50
                axes_bg_color = '#FFFFFF' # Keep axes background white
                fig.patch.set_facecolor(fig_bg_color)
                ax.patch.set_facecolor(axes_bg_color)


                # 绘制线图 (使用中性粉色主题颜色)
                line_color = '#F06292' # Material Design Pink 300
                # 使用转换后的北京时间进行绘图
                ax.plot(beijing_dates, counts_list, marker='o', linestyle='-', color=line_color)


                # <--- 修改文字/字体颜色和设置文本 (加粗) --->
                text_color = '#424242' # Material Design Grey 800

                # 设置标题和轴标签 (加粗并设置颜色)
                plt.xlabel('Time (Beijing Time)', color=text_color, fontweight='bold') # <--- 修改 X 轴标签，注明北京时间
                plt.ylabel('Rules Count', color=text_color, fontweight='bold') # <--- 加粗 Y 轴标签
                plt.title('Domain Rules History Count', color=text_color, fontweight='bold') # <--- 加粗标题
                # 设置刻度标签的颜色 (刻度标签通常不加粗)
                ax.tick_params(axis='x', colors=text_color)
                ax.tick_params(axis='y', colors=text_color)


                # 修改网格线颜色
                grid_color = '#e0e0e0' # Material Design Grey 300
                ax.grid(True, color=grid_color) # 显示网格线并设置颜色

                # 格式化 X 轴为年月日 (使用 mdates，它能处理带时区的时间对象)
                ax.xaxis.set_major_locator(mdates.AutoDateLocator())
                date_form = mdates.DateFormatter('%Y-%m-%d %H:%M') # 格式化包含小时分钟，更精确显示北京时间
                ax.xaxis.set_major_formatter(date_form)

                # 旋转 X 轴标签
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout() # 自动调整布局

                # Y 轴刻度尝试显示整数
                ax.yaxis.get_major_locator().set_params(integer=True)
                # 调整 Y 轴范围
                if counts_list: # 确保 counts_list 非空
                     max_count = max(counts_list)
                     min_count = min(counts_list)
                     # 如果所有值都相同，设置一个稍微大一点的范围
                     if max_count == min_count:
                         # 确保范围包含 0 (如果最小值 >= 0)
                         ax.set_ylim(max(0, max_count - 5), max_count + 5)
                         if max_count == 0: ax.set_ylim(-1, 10) # 特殊情况：如果都是 0
                     else:
                          # 标准范围从 0 到最大值 + 一点空间
                          ax.set_ylim(0, max_count * 1.1) # 简化范围
                          # 确保最小值不是负数时 Y 轴不显示负数
                          if min_count < 0 and ax.get_ylim()[0] > min_count * 1.1:
                               ax.set_ylim(min_count * 1.1, ax.get_ylim()[1])


                # 确保输出目录存在 (上面已检查过)
                # os.makedirs(output_dir, exist_ok=True)
                # 保存图表为图片文件
                plt.savefig(chart_image_path)
plt.close(fig) # 关闭图表


    except Exception as e:
         # 保留绘图失败时的警告，但不影响脚本流程
         print(f"Warning: Could not generate chart image: {e}", file=sys.stderr)
         pass

# 确保输出目录存在 (上面已检查过)
                # os.makedirs(output_dir, exist_ok=True)
                # 保存图表为图片文件
                plt.savefig(chart_image_path)
plt.close(fig) # 关闭图表


    except Exception as e:
         # 保留绘图失败时的警告，但不影响脚本流程
         print(f"Warning: Could not generate chart image: {e}", file=sys.stderr)
         pass


    # 确保输出目录存在 (防止前面绘图失败导致目录未创建)
    os.makedirs(output_dir, exist_ok=True)

    # 写入徽章数据 (保留逻辑)
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(badge_data, f, indent=2, ensure_ascii=False)

    # 写入历史数据 (保留逻辑)
    with open(history_output_path, 'w', encoding='utf-8') as f:
        json.dump(history_data, f, indent=2, ensure_ascii=False)


except FileNotFoundError as e:
    print(f"Error: Required file not found: {e}", file=sys.stderr)
    sys.exit(1)
except json.JSONDecodeError:
    print(f"Error: Could not decode JSON from {input_json_path}. Check JSON syntax.", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"An unexpected error occurred: {e}", file=sys.stderr)
    sys.exit(1)