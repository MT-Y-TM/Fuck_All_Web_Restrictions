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

    # 统计包含 "domain" 键的规则中，其对应列表的元素总数 (方案 C)
    count = 0
    # 检查路径是否存在且是预期的类型 (字典 -> 字典 -> 列表)
    if isinstance(data, dict) and 'routing' in data and isinstance(data['routing'], dict) and 'rules' in data['routing'] and isinstance(data['routing']['rules'], list):
        rules_list = data['routing']['rules']
        print(f"Found 'routing.rules' list with {len(rules_list)} rules. Counting 'domain' list items.") # <--- 调试输出

        for i, rule in enumerate(rules_list): # <--- 添加索引方便调试
            # 检查元素是字典，包含 "domain" 键，并且 "domain" 的值是一个列表
            if isinstance(rule, dict) and "domain" in rule:
                domain_value = rule["domain"]
                if isinstance(domain_value, list):
                    count += len(domain_value) # <--- 统计列表元素的个数并累加
                    print(f" - Rule {i}: Found 'domain' list with {len(domain_value)} items. Current total count: {count}") # <--- 调试输出
                elif isinstance(domain_value, str):
                     count += 1 # <--- 如果 domain 是字符串，统计为 1 个
                     print(f" - Rule {i}: Found 'domain' string. Current total count: {count}") # <--- 调试输出
                else:
                     print(f" - Rule {i}: Found 'domain' key but value is not list or string (type: {type(domain_value)}). Skipping.") # <--- 调试输出
            # else:
            #     print(f" - Rule {i}: No 'domain' key or not a dictionary. Skipping.") # <--- 如果想看跳过的规则，可以取消注释

        print(f"Finished counting. Total 'domain' items count: {count}") # <--- 调试输出
    else:
        print("Warning: Could not find the expected 'routing.rules' list in the JSON structure or it's not a list. Count will be 0.", file=sys.stderr)
        count = 0 # Set count to 0 if structure is wrong

    # 准备 Shields.io 需要的 JSON 数据
    badge_data = {
        "schemaVersion": 1,
        "label": "Domain Items", # <--- 修改标签，反映统计的是子项数量
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
