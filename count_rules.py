import json
import sys
import os
import requests
import datetime
import pytz # 导入 pytz 库用于处理时区

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdates

# <--- 配置 Matplotlib --->
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
chart_image_path = os.path.join(output_dir, chart_image_filename)

# GitHub Pages 上历史文件的原始 URL (用于下载现有历史)
github_username = "MT-Y-TM" # 请确保这里是你的 GitHub 用户名
repo_name = "Fuck_All_Web_Restrictions" # 请确保这里是你的仓库名
history_raw_url = f"https://raw.githubusercontent.com/{github_username}/{repo_name}/gh-pages/{history_filename}"

try:
    # 确保输出目录存在 (在保存文件前创建)
    os.makedirs(output_dir, exist_ok=True)

    # 读取输入 JSON 文件
    with open(input_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 统计 rules 列表中包含 "domain" 键的字典数量
    count = 0
    if isinstance(data, dict) and 'rules' in data and isinstance(data['rules'], list):
        rules_list = data['rules']
        for rule in rules_list:
            if isinstance(rule, dict) and "domain" in rule:
                count += 1

    # 准备 Shields.io 徽章数据
    badge_data = {
        "schemaVersion": 1,
        "label": "Domain Rules",
        "message": str(count),
        "color": "blue"
    }

    # 处理历史数据
    history_data = []
    try:
        # 尝试从 GitHub Pages 下载现有的历史文件
        response = requests.get(history_raw_url)
        response.raise_for_status() # 如果请求失败（如404或其他错误），则抛出异常
        history_data = response.json()
        # 简单检查确保读取到的是列表
        if not isinstance(history_data, list):
            print(f"Warning: Downloaded history file content is not a list. Starting new history.", file=sys.stderr)
            history_data = []
    except requests.exceptions.RequestException as e:
        if isinstance(e, requests.exceptions.HTTPError) and e.response.status_code == 404:
            # 如果历史文件不存在 (404错误)，则从一个空列表开始
            print(f"Info: History file not found at {history_raw_url}. Starting new history.", file=sys.stderr)
            history_data = []
        else:
            # 记录其他下载错误，但继续使用空历史列表
            print(f"Warning: Could not download existing history file from {history_raw_url}: {e}", file=sys.stderr)
            history_data = []
    except json.JSONDecodeError:
         # 记录JSON解码错误，但继续使用空历史列表
         print(f"Warning: Could not decode JSON from existing history file {history_raw_url}. Starting new history.", file=sys.stderr)
         history_data = []


    # --- START: 使用 pytz 获取并格式化北京时间 ---
    # 定义北京时间区 (CST, UTC+8)
    # 'Asia/Shanghai' 是 IANA 时区数据库中常用于表示北京/上海的时区名称
    beijing_tz = pytz.timezone('Asia/Shanghai')
    # 获取当前 UTC 时间，然后转换为北京时间
    now_utc = datetime.datetime.now(datetime.UTC)
    now_beijing = now_utc.astimezone(beijing_tz)
    # 生成包含时区信息的 ISO 8601 格式时间戳 (使用北京时间)
    timestamp = now_beijing.isoformat()
    # --- END: 使用 pytz 获取并格式化北京时间 ---

    new_history_entry = {"date": timestamp, "count": count}

    # 将新条目追加到历史数据列表 (检查是否重复 - 避免连续运行且计数未变时重复记录)
    # 检查历史数据是否为空，或者最后一个条目的计数是否与当前计数不同
    if not history_data or history_data[-1].get("count") != count:
         history_data.append(new_history_entry)


    # 生成图表图片
    try:
        # 检查是否有足够的数据点来绘制图表
        if history_data: # 只有在历史数据不为空时才尝试绘图
            # 将 ISO 字符串日期转换回 datetime 对象 (fromisoformat 会处理时区信息)
            dates = []
            counts_list = []
            for entry in history_data:
                try:
                    # 确保entry['date']和entry['count']存在且有效
                    if 'date' in entry and 'count' in entry:
                         dates.append(datetime.datetime.fromisoformat(entry['date']))
                         counts_list.append(entry['count'])
                    else:
                         print(f"Warning: Skipping invalid history entry format: {entry}", file=sys.stderr)
                         continue # 跳过格式不正确的条目
                except (ValueError, TypeError) as e:
                    # 记录无效的历史条目但继续
                    print(f"Warning: Skipping invalid history entry data: {entry} ({e})", file=sys.stderr)
                    continue # 跳过数据无效的条目

            if dates: # 确保在跳过无效条目后 dates 列表不为空
                fig, ax = plt.subplots(figsize=(10, 5))

                # Matplotlib 样式设置
                fig_bg_color = '#FCE4EC' # Material Design Pink 50
                axes_bg_color = '#FFFFFF' # 保留坐标轴背景为白色
                fig.patch.set_facecolor(fig_bg_color)
                ax.patch.set_facecolor(axes_bg_color)

                line_color = '#F06292' # Material Design Pink 300
                ax.plot(dates, counts_list, marker='o', linestyle='-', color=line_color)

                text_color = '#424242' # Material Design Grey 800
                plt.xlabel('Time', color=text_color, fontweight='bold') # 加粗 X 轴标签
                plt.ylabel('Rules Count', color=text_color, fontweight='bold') # 加粗 Y 轴标签
                plt.title('Domain Rules History Count', color=text_color, fontweight='bold') # 加粗标题
                ax.tick_params(axis='x', colors=text_color) # 设置刻度标签颜色
                ax.tick_params(axis='y', colors=text_color)

                grid_color = '#e0e0e0' # Material Design Grey 300
                ax.grid(True, color=grid_color) # 显示网格线并设置颜色

                # 格式化 X 轴为年月日时分 (显示小时和分钟对于北京时间可能有用)
                ax.xaxis.set_major_locator(mdates.AutoDateLocator())
                date_form = mdates.DateFormatter('%Y-%m-%d %H:%M') # 添加了时分
                ax.xaxis.set_major_formatter(date_form)

                plt.xticks(rotation=45, ha='right') # 旋转 X 轴标签
                plt.tight_layout() # 自动调整布局

                # Y 轴刻度设置和范围调整
                ax.yaxis.get_major_locator().set_params(integer=True) # 尝试显示整数刻度
                if counts_list: # 确保 counts_list 不为空
                    max_count = max(counts_list)
                    min_count = min(counts_list)
                    if max_count == min_count:
                        # 如果所有值都相同，设置一个稍微大一点的范围
                        ax.set_ylim(max(0, max_count - 5), max_count + 5)
                        if max_count == 0: ax.set_ylim(-1, 10) # 特殊情况：如果都是 0
                    else:
                         # 标准范围从 0 到最大值 + 一点空间 (例如 10%)
                         ax.set_ylim(0, max_count * 1.1)
                         # 如果有负数（尽管对于计数 unlikely），调整最小范围
                         if min_count < 0 and ax.get_ylim()[0] > min_count * 1.1:
                              ax.set_ylim(min_count * 1.1, ax.get_ylim()[1])
                else: # 处理 counts_list 在过滤无效条目后为空的情况
                     ax.set_ylim(0, 10) # 设置一个默认的小范围


                # 保存图表为图片文件
                plt.savefig(chart_image_path)
                plt.close(fig) # 关闭图表以释放内存

    except Exception as e:
         # 记录绘图失败时的警告，但不影响脚本流程
         print(f"Warning: Could not generate chart image: {e}", file=sys.stderr)
         pass # 继续脚本执行


    # 确保输出目录存在 (防止前面绘图失败导致目录未创建，虽然可能性不大)
    os.makedirs(output_dir, exist_ok=True)

    # 写入徽章数据
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(badge_data, f, indent=2, ensure_ascii=False)

    # 写入历史数据
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
