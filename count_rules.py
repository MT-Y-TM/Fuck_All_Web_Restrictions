import json
import sys
import os
import requests # <--- 新增导入
import datetime # <--- 新增导入
# 如果你想确保时间戳是北京时间，可以安装 pytz 并导入
# import pytz

# 获取输入JSON文件路径 (预计为 config.json)
if len(sys.argv) < 2:
    print("Usage: python count_rules.py <path_to_config.json>", file=sys.stderr)
    sys.exit(1)

input_json_path = sys.argv[1]

# 定义输出文件的目录和文件名
output_dir = "badge_data"
output_json_filename = "domain_count_data.json"
output_json_path = os.path.join(output_dir, output_json_filename)

# <--- 新增历史数据文件和图表文件相关的定义 --->
history_filename = "count_history.json"
history_output_path = os.path.join(output_dir, history_filename)
chart_template_filename = "chart_template.html" # 需要在主分支创建这个模板文件
chart_output_filename = "chart.html"
chart_output_path = os.path.join(output_dir, chart_output_filename)

# GitHub Pages 上历史文件的原始 URL (用于下载现有历史)
# 请替换 <your-github-username> 和 <your-repo-name>
# 这里我直接用你的仓库信息了
github_username = "MT-Y-TM"
repo_name = "Fuck_All_Web_Restrictions"
# 注意这里是 gh-pages 分支的 raw 文件 URL
history_raw_url = f"https://raw.githubusercontent.com/{github_username}/{repo_name}/gh-pages/{history_filename}"


try:
    # 读取输入 JSON 文件
    print(f"Attempting to read JSON file from: {input_json_path}")
    with open(input_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # --- 调试: 输出读取到的 JSON 内容 ---
    print("\n--- Successfully loaded JSON content ---")
    # print(json.dumps(data, indent=2, ensure_ascii=False)) # 完整输出可能过长，先注释掉
    print(f"Loaded JSON with keys: {list(data.keys())[:5]}...") # 打印部分键名 instead
    print("------------------------------------\n")
    # --- 调试结束 ---

    # 统计 rules 列表中包含 "domain" 键的字典数量 (方案 A)
    count = 0
    if isinstance(data, dict) and 'rules' in data and isinstance(data['rules'], list):
        rules_list = data['rules']
        print(f"Found 'rules' list with {len(rules_list)} total rules. Counting rules with 'domain' key.")

        for i, rule in enumerate(rules_list):
            if isinstance(rule, dict) and "domain" in rule:
                count += 1
                # print(f" - Rule {i}: Found 'domain' key. Current total count: {count}") # 调试输出

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

    # <--- 新增：处理历史数据 --->
    history_data = []
    # 尝试从 GitHub Pages 下载现有的历史文件
    print(f"Attempting to download history from: {history_raw_url}")
    try:
        response = requests.get(history_raw_url)
        response.raise_for_status() # 如果下载失败 (非 2xx 状态码)，抛出 HTTPError
        history_data = response.json()
        print("Successfully downloaded existing history.")
        if not isinstance(history_data, list):
            print(f"Warning: Downloaded history is not a list (type: {type(history_data)}). Starting with empty history.", file=sys.stderr)
            history_data = [] # 如果下载的数据格式不对，重置为空列表
    except requests.exceptions.RequestException as e:
        # 404 错误表示文件不存在，这是第一次运行或分支刚创建时的正常情况
        if isinstance(e, requests.exceptions.HTTPError) and e.response.status_code == 404:
            print("History file not found (404). Starting with empty history.")
            history_data = []
        else:
            # 其他下载错误，打印警告但不中断流程
            print(f"Warning: Could not download existing history file: {e}", file=sys.stderr)
            history_data = []

    # 获取当前 UTC 时间戳 (Actions 默认用 UTC)
    now_utc = datetime.datetime.now(datetime.UTC)
    timestamp = now_utc.isoformat()
    # 如果你想用北京时间作为记录的时间戳，需要额外处理和安装 pytz
    # beijing_tz = pytz.timezone('Asia/Shanghai')
    # now_bjt = datetime.datetime.now(beijing_tz)
    # timestamp = now_bjt.isoformat() # ISO 格式包含时区信息

    # 创建新的历史记录条目
    new_history_entry = {"date": timestamp, "count": count}
    print(f"Adding new history entry: {new_history_entry}")

    # 将新条目追加到历史数据列表 (可选：检查是否重复，避免短时间内重复记录)
    # 简单的检查：如果最新一条记录的时间和数量与当前一致，可能跳过追加
    if not history_data or history_data[-1].get("count") != count:
         history_data.append(new_history_entry)
         print("New entry added to history.")
    else:
         print("Count has not changed. Skipping adding new history entry.")


    # <--- 新增：生成图表 HTML 文件 --->
    print(f"Attempting to read chart template from: {chart_template_filename}")
    try:
        with open(chart_template_filename, 'r', encoding='utf-8') as f:
            chart_template_content = f.read()
        print("Successfully read chart template.")
    except FileNotFoundError:
        print(f"Error: Chart template file not found at {chart_template_filename}. Cannot generate chart page.", file=sys.stderr)
        chart_template_content = "<h1>Error: Chart template not found!</h1>" # 提供一个错误提示内容


    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    # 将徽章数据写入 JSON 文件到指定目录
    print(f"Writing badge data to: {output_json_path}")
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(badge_data, f, indent=2, ensure_ascii=False)

    # 将更新后的历史数据写入历史文件到指定目录
    print(f"Writing history data to: {history_output_path}")
    with open(history_output_path, 'w', encoding='utf-8') as f:
        json.dump(history_data, f, indent=2, ensure_ascii=False)

    # 将图表 HTML 内容写入文件到指定目录
    print(f"Writing chart page to: {chart_output_path}")
    with open(chart_output_path, 'w', encoding='utf-8') as f:
        f.write(chart_template_content) # 图表数据通过 JS 动态加载，所以直接写模板内容

    print("Script finished successfully.")

except FileNotFoundError as e:
    print(f"Error: Required file not found: {e}", file=sys.stderr)
    sys.exit(1) # 脚本出错时退出，让 Action 失败
except json.JSONDecodeError:
    print(f"Error: Could not decode JSON from {input_json_path}. Check JSON syntax.", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"An unexpected error occurred: {e}", file=sys.stderr)
    sys.exit(1)
