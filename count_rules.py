import json
import sys
import os

# 获取输入JSON文件路径 (预计为 config.json)
# 作为脚本的第一个参数
if len(sys.argv) < 2:
    print("Usage: python count_rules.py <path_to_config.json>", file=sys.stderr)
    sys.exit(1)

input_json_path = sys.argv[1]

# 定义输出文件的目录和完整路径
output_dir = "badge_data"
output_json_filename = "domain_count_data.json"
output_json_path = os.path.join(output_dir, output_json_filename)

try:
    # 读取输入 JSON 文件
    print(f"Attempting to read JSON file from: {input_json_path}") # <--- 调试输出
    with open(input_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # --- 调试: 输出读取到的 JSON 内容 ---
    print("\n--- Successfully loaded JSON content ---")
    # 使用 json.dumps 格式化输出，方便在 Action 日志中查看
    # ensure_ascii=False 可以让中文字符正常显示
    print(json.dumps(data, indent=2, ensure_ascii=False))
    print("------------------------------------\n")
    # --- 调试结束 ---

    # 统计 routing.rules 列表中包含 "domain" 键的字典数量 (方案 A)
    count = 0
    # 检查路径是否存在且是预期的类型 (字典 -> 字典 -> 列表)
    if isinstance(data, dict) and 'routing' in data and isinstance(data['routing'], dict) and 'rules' in data['routing'] and isinstance(data['routing']['rules'], list):
        rules_list = data['routing']['rules']
        print(f"Found 'routing.rules' list with {len(rules_list)} total rules. Counting rules with 'domain' key.") # <--- 调试输出

        for i, rule in enumerate(rules_list): # <--- 添加索引方便调试
            # 检查当前规则元素是否是字典，并且是否包含 "domain" 这个键
            if isinstance(rule, dict) and "domain" in rule: # <--- 这里的逻辑就是统计包含 "domain" 键的字典个数
                count += 1 # <--- 找到一个包含 "domain" 键的字典，计数加一
                print(f" - Rule {i}: Found 'domain' key. Current total count: {count}") # <--- 调试输出
            # else:
            #     print(f" - Rule {i}: No 'domain' key or not a dictionary. Skipping.") # <--- 如果想看跳过的规则，可以取消注释

        print(f"Finished counting. Total 'domain' rules count: {count}") # <--- 调试输出
    else:
        print("Warning: Could not find the expected 'routing.rules' list in the JSON structure or it's not a list. Count will be 0.", file=sys.stderr)
        count = 0

    # 准备 Shields.io 需要的 JSON 数据
    badge_data = {
        "schemaVersion": 1,
        "label": "Domain Rules", # <--- 标签改回 "Domain Rules"
        "message": str(count),   # 数量转为字符串
        "color": "blue"          # 徽章颜色
    }

    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    # 将徽章数据写入 JSON 文件到指定目录
    print(f"Writing badge data to: {output_json_path}") # <--- 调试输出
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(badge_data, f, indent=2, ensure_ascii=False)

    print("Script finished successfully.") # <--- 调试输出

except FileNotFoundError:
    print(f"Error: Input file not found at {input_json_path}", file=sys.stderr)
    sys.exit(1) # 脚本出错时退出，让 Action 失败
except json.JSONDecodeError:
    print(f"Error: Could not decode JSON from {input_json_path}. Check JSON syntax.", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"An unexpected error occurred: {e}", file=sys.stderr)
    sys.exit(1)
