import json
import sys
import os

# 获取输入JSON文件路径 (预计为 config.json)
# 作为脚本的第一个参数
if len(sys.argv) < 2:
    print("Usage: python count_rules.py <path_to_config.json>", file=sys.stderr)
    sys.exit(1)

input_json_path = sys.argv[1]
output_json_path = "domain_count_data.json" # 输出到这个文件，供 GitHub Pages 托管

try:
    # 读取输入 JSON 文件
    with open(input_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 统计包含 "domain" 键的规则数量
    # 根据 config.json 的结构，规则在 data['routing']['rules'] 列表中
    count = 0
    # 检查路径是否存在且是预期的类型 (字典 -> 字典 -> 列表)
    if isinstance(data, dict) and 'routing' in data and isinstance(data['routing'], dict) and 'rules' in data['routing'] and isinstance(data['routing']['rules'], list):
        rules_list = data['routing']['rules']
        for rule in rules_list:
            # 检查列表中的每个元素是否是字典，并且包含 "domain" 键
            if isinstance(rule, dict) and "domain" in rule:
                count += 1
    else:
        # 如果结构不匹配，打印警告并设置计数为 0
        print("Warning: Could not find the expected 'routing.rules' list in the JSON structure.", file=sys.stderr)
        count = 0

    # 准备 Shields.io 需要的 JSON 数据
    badge_data = {
        "schemaVersion": 1,
        "label": "Domain Rules", # 徽章左侧文本
        "message": str(count),   # 数量转为字符串
        "color": "pink"          # 徽章颜色，你可以改成 'green', 'yellow', 'red' 等
    }

    # 将徽章数据写入 JSON 文件
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(badge_data, f, indent=2, ensure_ascii=False) # 使用 ensure_ascii=False 确保中文字符正常显示（如果你的标签有中文）

    print(f"Successfully counted {count} domain rules and saved badge data to {output_json_path}")

except FileNotFoundError:
    print(f"Error: Input file not found at {input_json_path}", file=sys.stderr)
    sys.exit(1) # 脚本出错时退出，让 Action 失败
except json.JSONDecodeError:
    print(f"Error: Could not decode JSON from {input_json_path}", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"An unexpected error occurred: {e}", file=sys.stderr)
    sys.exit(1)
