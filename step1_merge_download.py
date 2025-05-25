import os
import re
import requests

# 创建输出目录
os.makedirs('./Merge-rule', exist_ok=True)

# 特殊字符正则
special_chars_pattern = re.compile(r'[\/\?\#\\\[\]=]')

# 保留规则开头
valid_prefixes = ('@', '|', '127.0.0.1', '0.0.0.0', '::')

# 存储规则
all_valid_rules = []
all_invalid_rules = []

def download_remote_rules(urls_conf_path):
    print("处理过程如下")
    print("------------------------------------------------------------")

    with open(urls_conf_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or ':' not in line:
                continue
            name, url = map(str.strip, line.split(':', 1))
            print(f"正在下载{name}规则")
            try:
                response = requests.get(url, timeout=20)
                if response.status_code == 200:
                    lines = response.text.splitlines()
                    print(f"下载成功,规则数量: {len(lines)}条")
                    process_rules(lines)
                else:
                    print("下载失败")
            except Exception:
                print("下载失败")
    print("------------------------------------------------------------")

def load_local_rules(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        process_rules(lines)
    else:
        print(f"未找到本地规则文件: {file_path}")

def process_rules(lines):
    for line in lines:
        rule = line.strip()
        if not rule or rule.startswith(('!', '#')):
            continue
        if rule.startswith(valid_prefixes) and not special_chars_pattern.search(rule):
            all_valid_rules.append(rule)
        else:
            all_invalid_rules.append(rule)

def save_results():
    with open('./Merge-rule/merge_others.txt', 'w', encoding='utf-8') as f:
        for rule in all_invalid_rules:
            f.write(rule + '\n')

    with open('./Merge-rule/merge_rules.txt', 'w', encoding='utf-8') as f:
        for rule in all_valid_rules:
            f.write(rule + '\n')

    print("正在去除头部信息和注释")
    print(f"去除条目{len(all_invalid_rules)}条,输出到./Merge-rule/merge_others.txt")
    print(f"最终结果输出到了./Merge-rule/merge_rules.txt {len(all_valid_rules)}条规则")


def main():
    """提供统一入口函数"""
    load_local_rules('./input/local-rules.txt')
    download_remote_rules('./input/urls.conf')
    save_results()