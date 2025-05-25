import os
import re

# 创建输出目录
os.makedirs('./stripping_rules', exist_ok=True)

# 文件路径映射
files = {
    'hosts': {
        'input': './BAWLC/hosts_black.txt',
        'output': './stripping_rules/hosts-domain.txt',
        'count': 0
    },
    'adguard_black': {
        'input': './BAWLC/adguard-black.txt',
        'output': './stripping_rules/adguard-bdomain.txt',
        'count': 0
    },
    'adguard_white': {
        'input': './BAWLC/adguard-white.txt',
        'output': './stripping_rules/adguard-wbdomain.txt',
        'count': 0
    },
}

# 剥离函数
def strip_hosts_line(line: str) -> str:
    parts = line.strip().split()
    return parts[1] if len(parts) >= 2 else None

def strip_adguard_line(line: str) -> str:
    line = line.strip()
    # 移除前缀
    line = re.sub(r'^(@@)?\|\|', '', line)
    # 去除 ^ 和后缀内容
    domain = re.split(r'[\^$]', line)[0]
    return domain

# 处理函数
def process_file(file_key: str):
    info = files[file_key]
    with open(info['input'], 'r', encoding='utf-8') as fin, \
         open(info['output'], 'w', encoding='utf-8') as fout:
        for line in fin:
            stripped = None
            if file_key == 'hosts':
                stripped = strip_hosts_line(line)
            else:
                stripped = strip_adguard_line(line)

            if stripped:
                fout.write(stripped + '\n')
                info['count'] += 1

# 主流程
def main():
    """提供统一入口函数"""
    for key in files:
        process_file(key)

    # 输出统计信息
    print("域名剥离成功")
    print("------------------------------------------------------------")
    print(f"./stripping_rules/hosts-domain.txt 规则数量{files['hosts']['count']}条")
    print(f"./stripping_rules/adguard-bdomain.txt 规则数量{files['adguard_black']['count']}条")
    print(f"./stripping_rules/adguard-wbdomain.txt 规则数量{files['adguard_white']['count']}条")
    print("------------------------------------------------------------")