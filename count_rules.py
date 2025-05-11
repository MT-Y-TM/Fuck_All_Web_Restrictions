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
output_dir = "badge_data"  # <--- 新增：定义输出目录的名称
output_json_filename = "domain_count_data.json" # <--- 输出文件的名称
output_json_path = os.path.join(output_dir, output_json_filename) # <--- 构建完整的输出文件路径

try:
    # 读取输入 JSON 文件
    with open(input_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 统计包含 "domain" 键的规则数量
    count = 0
    if isinstance(data, dict) and 'routing' in data and isinstance(data['routing'], dict) and 'rules' in data['routing'] and isinstance(data['routing']['rules'], list):
        rules_list = data['routing']['rules']
        for rule in rules_list:
            if isinstance(rule, dict) and "domain" in rule:
                count += 1
    else:
        print("Warning: Could not find the expected 'routing.rules' list in the JSON structure.", file=sys.stderr)
        count = 0

    # 准备 Shields.io 需要的 JSON 数据
    badge_data = {
        "schemaVersion": 1,
        "label": "Domain Rules",
        "message": str(count),
        "color": "blue"
    }

    # <--- 新增：确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    # 将徽章数据写入 JSON 文件到指定目录
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(badge_data, f, indent=2, ensure_ascii=False)

    print(f"Successfully counted {count} domain rules and saved badge data to {output_json_path}")

except FileNotFoundError:
    print(f"Error: Input file not found at {input_json_path}", file=sys.stderr)
    sys.exit(1)
except json.JSONDecodeError:
    print(f"Error: Could not decode JSON from {input_json_path}", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"An unexpected error occurred: {e}", file=sys.stderr)
    sys.exit(1)
