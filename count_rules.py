import json
import sys
import os

# 获取输入JSON文件路径 (预计为 config.json)
if len(sys.argv) < 2:
    print("Usage: python count_rules.py <path_to_config.json>", file=sys.stderr)
    sys.exit(1)
input_json_path = sys.argv[1]

output_dir = "badge_data"
output_json_filename = "domain_count_data.json"
output_json_path = os.path.join(output_dir, output_json_filename)

try:
    # 读取输入 JSON 文件
    print(f"Attempting to read JSON file from: {input_json_path}")
    with open(input_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 调试：打印整个 JSON
    print("\n--- Successfully loaded JSON content ---")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    print("------------------------------------\n")

    # 统计包含 "domain" 键的规则数
    count = 0
    if isinstance(data, dict) and 'rules' in data and isinstance(data['rules'], list):
        rules_list = data['rules']
        print(f"Found 'rules' list with {len(rules_list)} items.")
        for i, rule in enumerate(rules_list):
            if isinstance(rule, dict) and "domain" in rule:
                count += 1
                print(f" - Rule {i}: Found 'domain' key. Current total count: {count}")
    else:
        print("Warning: Could not find the expected 'rules' list directly under the root.", file=sys.stderr)

    print(f"Finished counting. Total 'domain' rules count: {count}")

    # 准备 Shields.io 徽章数据
    badge_data = {
        "schemaVersion": 1,
        "label": "现有规则数量",
        "message": str(count),
        "color": "blue"
    }

    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    # 写入输出文件
    print(f"Writing badge data to: {output_json_path}")
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(badge_data, f, indent=2, ensure_ascii=False)

    print("Script finished successfully.")

except FileNotFoundError:
    print(f"Error: Input file not found at {input_json_path}", file=sys.stderr)
    sys.exit(1)
except json.JSONDecodeError:
    print(f"Error: Could not decode JSON from {input_json_path}. Check JSON syntax.", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"An unexpected error occurred: {e}", file=sys.stderr)
    sys.exit(1)
