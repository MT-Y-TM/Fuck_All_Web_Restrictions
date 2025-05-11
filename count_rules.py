import json
import sys
import os
import requests # 需要这个库来下载历史文件
import datetime

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
chart_image_path = os.path.join(output_dir, chart_image_path)

# GitHub Pages 上历史文件的原始 URL (用于下载现有历史)
github_username = "MT-Y-TM" # 请确保这里是你的 GitHub 用户名
repo_name = "Fuck_All_Web_Restrictions" # 请确保这里是你的仓库名
history_raw_url = f"https://raw.githubusercontent.com/{github_username}/{repo_name}/gh-pages/{history_filename}"

# <--- 移除字体下载相关的定义和 try/except 块 --->
# 所有字体下载相关的变量定义和整个 try/except 代码块都已移除


try:
    # 确保输出目录存在 (在保存文件前创建)
    os.makedirs(output_dir, exist_ok=True)

    # 读取输入 JSON 文件 (移除调试打印)
    # print(...) # 已移除
    with open(input_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # print(...) # 已移除

    # 统计 rules 列表中包含 "domain" 键的字典数量 (方案 A)
    count = 0
    # 检查根是否是字典，并且包含 'rules' 键，且 'rules' 的值是列表
    if isinstance(data, dict) and 'rules' in data and isinstance(data['rules'], list):
        rules_list = data['rules']
        # print(...) # 已移除
        for i, rule in enumerate(rules_list):
            # 检查当前规则元素是否是字典，并且是否包含 "domain" 这个键
            if isinstance(rule, dict) and "domain" in rule:
                count += 1
                # print(...) # 已移除
        # print(...) # 已移除
    else:
        # print(...) # 已移除 (警告信息)
        count = 0 # 如果路径未找到，计数仍然是 0

    # 准备 Shields.io 徽章数据 (保留逻辑)
    badge_data = {
        "schemaVersion": 1,
        "label": "Domain Rules",
        "message": str(count),
        "color": "blue"
    }

    # 处理历史数据 (保留逻辑，移除调试打印)
    # print(...) # 已移除
    history_data = []
    try:
        response = requests.get(history_raw_url)
        response.raise_for_status()
        history_data = response.json()
        # print(...) # 已移除 (成功下载提示)
        if not isinstance(history_data, list):
            # print(...) # 已移除 (警告信息)
            history_data = []
    except requests.exceptions.RequestException as e:
        if isinstance(e, requests.exceptions.HTTPError) and e.response.status_code == 404:
            # print(...) # 已移除 (404 提示)
            history_data = []
        else:
            # print(...) # 已移除 (其他错误警告)
            history_data = []

    # 获取当前 UTC 时间戳
    now_utc = datetime.datetime.now(datetime.UTC)
    timestamp = now_utc.isoformat()
    new_history_entry = {"date": timestamp, "count": count}
    # print(...) # 已移除 (添加新条目提示)

    # 将新条目追加到历史数据列表 (检查是否重复)
    if not history_data or history_data[-1].get("count") != count:
         history_data.append(new_history_entry)
         # print(...) # 已移除 (条目已添加提示)
    else:
         # print(...) # 已移除 (计数未改变提示)
         pass # 如果代码块为空，保留 pass 以避免语法错误

    # 生成图表图片 (保留逻辑，简化设置，使用英文文本)
    # print("Generating chart image using Matplotlib...") # 已移除
    try:
        # 检查是否有足够的数据点来绘制图表
        if not history_data or len(history_data) < 1:
             # print("Not enough data points to generate chart. Skipping chart generation.") # 已移除
             pass # 如果没有数据，跳过绘图
        else:
            # 提取日期和数量
            dates = [datetime.datetime.fromisoformat(entry['date']) for entry in history_data]
            counts_list = [entry['count'] for entry in history_data]

            # 创建图表
            fig, ax = plt.subplots(figsize=(10, 5))

            # 绘制线图 (使用默认蓝色)
            ax.plot(dates, counts_list, marker='o', linestyle='-', color='b') # 使用默认蓝色

            # 格式化 X 轴为年月日
            ax.xaxis.set_major_locator(mdates.AutoDateLocator())
            date_form = mdates.DateFormatter('%Y-%m-%d') # 日期格式
            ax.xaxis.set_major_formatter(date_form)

            # 设置标题和轴标签 (使用英文文本)
            plt.xlabel('Time') # X 轴标签
            plt.ylabel('Rules Count') # Y 轴标签
            plt.title('Domain Rules History Count') # 图表标题
            plt.grid(True) # 显示网格线
            plt.xticks(rotation=45, ha='right') # 旋转 X 轴标签
            plt.tight_layout() # 自动调整布局

            # Y 轴刻度尝试显示整数
            ax.yaxis.get_major_locator().set_params(integer=True) # 强制主刻度为整数
            # 调整 Y 轴范围
            if counts_list: # 确保 counts_list 非空
                 max_count = max(counts_list)
                 min_count = min(counts_list)
                 # 如果所有值都相同，设置一个稍微大一点的范围
                 if max_count == min_count:
                     # 确保范围包含 0 (如果最小值 >= 0)
                     ax.set_ylim(max(0, max_count - 5), max_count + 5)
                     if max_count == 0: ax.set_ylim(-1, 10) # 特殊情况：如果都是 0，设置 0-10 范围
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
            # print(f"Chart image saved to: {chart_image_path}") # 已移除

            plt.close(fig) # 关闭图表，释放内存

    except Exception as e:
         # print(f"Warning: Could not generate chart image: {e}", file=sys.stderr) # 已移除
         pass # 即使绘图失败也继续执行脚本

    # 确保输出目录存在 (重复检查已移除)
    # os.makedirs(output_dir, exist_ok=True)

    # 写入徽章数据 (保留逻辑，移除调试打印)
    # print(f"Writing badge data to: {output_json_path}") # 已移除
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(badge_data, f, indent=2, ensure_ascii=False)

    # 写入历史数据 (保留逻辑，移除调试打印)
    # print(f"Writing history data to: {history_output_path}") # 已移除
    with open(history_output_path, 'w', encoding='utf-8') as f:
        json.dump(history_data, f, indent=2, ensure_ascii=False)

    # print("Script finished successfully.") # 已移除

except FileNotFoundError as e:
    print(f"Error: Required file not found: {e}", file=sys.stderr) # 保留错误打印
    sys.exit(1)
except json.JSONDecodeError:
    print(f"Error: Could not decode JSON from {input_json_path}. Check JSON syntax.", file=sys.stderr) # 保留错误打印
    sys.exit(1)
except Exception as e:
    print(f"An unexpected error occurred: {e}", file=sys.stderr) # 保留错误打印
    sys.exit(1)
