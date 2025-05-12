import json
import requests
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import pytz
import os
import sys
from collections import defaultdict

def get_rule_count(url):
    response = requests.get(url)
    response.raise_for_status()
    lines = response.text.splitlines()
    count = sum(1 for line in lines if line.strip() and not line.strip().startswith(('#', '!')))
    return count

def load_config(config_file):
    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def generate_chart(history_data, output_path):
    plt.rcParams['font.family'] = ['SimHei']  # 使用中文字体（黑体）
    plt.rcParams['axes.unicode_minus'] = False

    timestamps = [entry["timestamp"] for entry in history_data]
    domain_names = set()
    for entry in history_data:
        domain_names.update(entry["counts"].keys())
    domain_names = sorted(domain_names)

    x = np.arange(len(timestamps))
    width = 0.1
    fig, ax = plt.subplots(figsize=(10, 6))

    for i, domain in enumerate(domain_names):
        y = [entry["counts"].get(domain, 0) for entry in history_data]
        ax.bar(x + i * width, y, width, label=domain)

    ax.set_xlabel("时间（北京时间）")
    ax.set_ylabel("规则数量")
    ax.set_title("各域名规则数量历史记录")
    ax.set_xticks(x + width * len(domain_names) / 2)
    ax.set_xticklabels(timestamps, rotation=45, ha='right')
    ax.legend()

    plt.tight_layout()
    plt.savefig(output_path)

def main():
    config_file = sys.argv[1] if len(sys.argv) > 1 else 'config.json'
    config = load_config(config_file)

    # 使用 pytz 获取当前北京时间
    tz = pytz.timezone("Asia/Shanghai")
    now = datetime.now(tz)
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

    badge_data = {}
    history_data = []

    badge_dir = "badge_data"
    os.makedirs(badge_dir, exist_ok=True)

    history_path = os.path.join(badge_dir, "history.json")
    if os.path.exists(history_path):
        with open(history_path, 'r', encoding='utf-8') as f:
            history_data = json.load(f)

    counts = {}
    for domain, url in config.items():
        try:
            count = get_rule_count(url)
            counts[domain] = count
            badge_data[domain] = {
                "schemaVersion": 1,
                "label": domain,
                "message": str(count),
                "color": "blue"
            }
        except Exception as e:
            print(f"获取 {domain} 的规则数时出错: {e}")

    # 记录当前数据点（含北京时间戳）
    history_data.append({
        "timestamp": timestamp,
        "counts": counts
    })

    # 限制历史记录长度（可选）
    # history_data = history_data[-100:]

    # 保存 badge json 和历史记录 json
    for domain, data in badge_data.items():
        save_json(data, os.path.join(badge_dir, f"{domain}.json"))

    save_json(history_data, history_path)

    # 生成图表
    chart_path = os.path.join(badge_dir, "rule_counts_chart.png")
    generate_chart(history_data, chart_path)

if __name__ == "__main__":
    main()