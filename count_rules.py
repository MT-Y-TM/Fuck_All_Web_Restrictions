import json
import sys
import os
import requests # 需要这个库来下载字体和历史文件
import datetime
# import pytz # 如果需要精确的北京时间戳，请取消注释并安装 pytz

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdates
from matplotlib import font_manager # 需要这个来管理字体

# <--- 配置 Matplotlib，解决中文显示和负号问题 --->
# 我们将下载字体文件并在运行时加载，所以先注释掉基于系统字体的设置
# plt.rcParams['font.sans-serif'] = [...]
plt.rcParams['axes.unicode_minus'] = False # 解决负号'-'显示为方块的问题


# 获取输入JSON文件路径 (预计为 config.json)
if len(sys.argv) < 2:
    print("Usage: python count_rules.py <path_to_config.json>", file=sys.stderr)
    sys.exit(1)

input_json_path = sys.argv[1]

# 定义输出文件的目录和文件名
output_dir = "badge_data"
output_json_filename = "domain_count_data.json"
output_json_path = os.path.join(output_dir, output_json_filename)

# 历史数据文件和图表图片文件名
history_filename = "count_history.json"
history_output_path = os.path.join(output_dir, history_filename)
chart_image_filename = "domain_rules_trend.png"
chart_image_path = os.path.join(output_dir, chart_image_filename)


# GitHub Pages 上历史文件的原始 URL (用于下载现有历史)
github_username = "MT-Y-TM" # 请确保这里是你的 GitHub 用户名
repo_name = "Fuck_All_Web_Restrictions" # 请确保这里是你的仓库名
history_raw_url = f"https://raw.githubusercontent.com/{github_username}/{repo_name}/gh-pages/{history_filename}"

# <--- 字体下载相关的定义和代码 --->
# Source Han Sans SC (简体中文) Regular OTF 字体文件在 Adobe 官方 release 仓库的 URL
# 这个 URL 比较稳定
font_url = "https://github.com/adobe-fonts/source-han-sans/raw/release/SubsetOTF/CN/SourceHanSansSC-Regular.otf"
font_local_filename = "SourceHanSansSC-Regular.otf" # 保存在本地的文件名
font_local_path = os.path.join(output_dir, font_local_filename) # 保存在输出目录中


try:
    # 确保输出目录存在 (在下载字体前创建)
    os.makedirs(output_dir, exist_ok=True)

    # <--- 下载字体文件 --->
    print(f"Attempting to download font from: {font_url}")
    try:
        font_response = requests.get(font_url, stream=True)
        font_response.raise_for_status() # 如果下载失败 (非 2xx 状态码)，抛出 HTTPError
        with open(font_local_path, 'wb') as f:
            for chunk in font_response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Successfully downloaded font to: {font_local_path}")

        # <--- 将字体添加到 Matplotlib 的字体管理器并设置 --->
        # 这使得 Matplotlib 可以通过字体家族名称找到并使用这个字体
        font_manager.fontManager.addfont(font_local_path)
        # 获取字体属性，以便找到 Matplotlib 注册的精确字体家族名称
        font_properties = font_manager.FontProperties(fname=font_local_path)
        font_family_name = font_properties.get_name()
        print(f"Font '{font_family_name}' added to font manager.")

        # 设置 Matplotlib 使用这个字体家族来绘制文本
        plt.rcParams['font.family'] = font_family_name
        print(f"Matplotlib font set to '{font_family_name}'.")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading font file: {e}", file=sys.stderr)
        print("Chinese characters may not display correctly.", file=sys.stderr)
        # 继续执行，但没有下载到字体，中文可能仍是方块


    # 读取输入 JSON 文件
    print(f"Attempting to read JSON file from: {input_json_path}")
    with open(input_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # --- 调试: 输出读取到的 JSON 内容 ---
    # print("\n--- Successfully loaded JSON content ---")
    # print(json.dumps(data, indent=2, ensure_ascii=False))
    # print("------------------------------------\n")
    # --- 调试结束 ---

    # 统计 rules 列表中包含 "domain" 键的字典数量 (方案 A)
    count = 0
    if isinstance(data, dict) and 'rules' in data and isinstance(data['rules'], list):
        rules_list = data['rules']
        print(f"Found 'rules' list with {len(rules_list)} total rules. Counting rules with 'domain' key.")

        for i, rule in enumerate(rules_list):
            if isinstance(rule, dict) and "domain" in rule:
                count += 1

        print(f"Finished counting. Total 'domain' rules count: {count}")
    else:
        print("Warning: Could not find the expected 'rules' list directly under the root in the JSON structure or it's not a list. Count will be 0.", file=sys.stderr)
        count = 0

    # 准备 Shields.io 徽章数据
    badge_data = {
        "schemaVersion": 1,
        "label": "Domain Rules",
        "message": str(count),
        "color": "blue"
    }

    # <--- 处理历史数据 --->
    history_data = []
    print(f"Attempting to download history from: {history_raw_url}")
    try:
        response = requests.get(history_raw_url)
        response.raise_for_status()
        history_data = response.json()
        print("Successfully downloaded existing history.")
        if not isinstance(history_data, list):
            print(f"Warning: Downloaded history is not a list (type: {type(history_data)}). Starting with empty history.", file=sys.stderr)
            history_data = []
    except requests.exceptions.RequestException as e:
        if isinstance(e, requests.exceptions.HTTPError) and e.response.status_code == 404:
            print("History file not found (404). Starting with empty history.")
            history_data = []
        else:
            print(f"Warning: Could not download existing history file: {e}", file=sys.stderr)
            history_data = []

    # 获取当前 UTC 时间戳
    now_utc = datetime.datetime.now(datetime.UTC)
    timestamp = now_utc.isoformat()

    # 创建新的历史记录条目
    new_history_entry = {"date": timestamp, "count": count}
    print(f"Adding new history entry: {new_history_entry}")

    # 将新条目追加到历史数据列表 (检查是否重复)
    if not history_data or history_data[-1].get("count") != count:
         history_data.append(new_history_entry)
         print("New entry added to history.")
    else:
         print("Count has not changed. Skipping adding new history entry.")

    # <--- 使用 Matplotlib 生成图表 --->
    print("Generating chart image using Matplotlib...")
    try:
        # 提取日期和数量
        # 确保历史数据列表非空
        if not history_data:
             print("History data is empty. Cannot generate chart.")
             # 可以选择在这里退出或生成一个表示无数据的空白图
             # 为了确保生成文件，即使无数据也继续，但不生成图表图片
             pass # 继续执行脚本，但不生成图表图片
        else:
            dates = [datetime.datetime.fromisoformat(entry['date']) for entry in history_data]
            counts_list = [entry['count'] for entry in history_data]

            # 如果没有数据点，不生成图表 (这个检查在处理历史数据前做更合适)
            # 这里的检查是确保至少有一个点来绘图
            if len(dates) < 1:
                print("Not enough data points to generate chart. Skipping chart generation.")
            else:
                fig, ax = plt.subplots(figsize=(10, 5))

                # <--- 应用颜色和绘制线图 --->
                line_color = '#F06292' # Material Design Pink 300
                ax.plot(dates, counts_list, marker='o', linestyle='-', color=line_color)

                # <--- 格式化 X 轴为年月日 --->
                ax.xaxis.set_major_locator(mdates.AutoDateLocator())
                date_form = mdates.DateFormatter('%Y-%m-%d')
                ax.xaxis.set_major_formatter(date_form)

                # <--- 设置标题和轴标签 (使用中文)，现在应该能正常显示了 --->
                # 这些中文文本应该会使用上面加载的字体来显示
                plt.xlabel('时间')
                plt.ylabel('规则数量')
                plt.title('规则历史数量统计') # 设置标题
                plt.grid(True)
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()

                # <--- Y 轴刻度尝试显示整数 --->
                ax.yaxis.get_major_locator().set_params(integer=True)
                # 调整 Y 轴范围
                if counts_list:
                     max_count = max(counts_list)
                     # 确保包含 0，并留出空间，防止所有点都在同一条线上导致 Matplotlib 自动设置范围很奇怪
                     # 如果所有点都一样，手动设置一个稍微大一点的范围
                     if max_count == min(counts_list):
                         ax.set_ylim(max(0, max_count - 5), max_count + 5) # 如果所有值都一样，设置一个固定的 ±5 范围
                         if max_count == 0: ax.set_ylim(-1, 10) # 如果都是0，设置0-10范围
                     else:
                          ax.set_ylim(0, max_count * 1.1 + (5 if max_count < 10 else max_count * 0.1)) # 确保包含 0，并留出空间，根据最大值调整


                # 确保输出目录存在 (这里只需要用于保存输出文件)
                os.makedirs(output_dir, exist_ok=True)
                # 保存图表为图片文件
                plt.savefig(chart_image_path)
                print(f"Chart image saved to: {chart_image_path}")

                plt.close(fig) # 关闭图表，释放内存

    except Exception as e:
         print(f"Warning: Could not generate chart image: {e}", file=sys.stderr)


    # 确保输出目录存在 (再次检查)
    os.makedirs(output_dir, exist_ok=True)

    # 将徽章数据写入 JSON 文件到指定目录
    print(f"Writing badge data to: {output_json_path}")
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(badge_data, f, indent=2, ensure_ascii=False)

    # 将更新后的历史数据写入历史文件到指定目录
    print(f"Writing history data to: {history_output_path}")
    with open(history_output_path, 'w', encoding='utf-8') as f:
        json.dump(history_data, f, indent=2, ensure_ascii=False)

    print("Script finished successfully.")

except FileNotFoundError as e:
    print(f"Error: Required file not found: {e}", file=sys.stderr)
    sys.exit(1)
except json.JSONDecodeError:
    print(f"Error: Could not decode JSON from {input_json_path}. Check JSON syntax.", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"An unexpected error occurred: {e}", file=sys.stderr)
    sys.exit(1)
