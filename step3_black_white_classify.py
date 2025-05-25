import os

# 创建输出目录
os.makedirs('./BAWLC', exist_ok=True)

# 黑名单IP
blacklist_ips = {'0.0.0.0', '127.0.0.1', '::'}

# 计数器
counts = {
    'hosts_black': 0,
    'hosts_white': 0,
    'adguard_black': 0,
    'adguard_white': 0,
}

# 文件路径
file_map = {
    'hosts_black': './BAWLC/hosts_black.txt',
    'hosts_white': './BAWLC/hosts_white.txt',
    'adguard_black': './BAWLC/adguard-black.txt',
    'adguard_white': './BAWLC/adguard-white.txt',
}

# 写入器
writers = {
    key: open(path, 'w', encoding='utf-8')
    for key, path in file_map.items()
}

def classify_hosts(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            rule = line.strip()
            if not rule:
                continue
            parts = rule.split()
            if parts[0] in blacklist_ips:
                writers['hosts_black'].write(rule + '\n')
                counts['hosts_black'] += 1
            else:
                writers['hosts_white'].write(rule + '\n')
                counts['hosts_white'] += 1

def classify_adguard(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            rule = line.strip()
            if not rule:
                continue
            if rule.startswith('||'):
                writers['adguard_black'].write(rule + '\n')
                counts['adguard_black'] += 1
            elif rule.startswith('@@'):
                writers['adguard_white'].write(rule + '\n')
                counts['adguard_white'] += 1

def close_all():
    for w in writers.values():
        w.close()

def print_report():
    print("黑白名单分类完成")
    print("------------------------------------------------------------")
    print(f"./BAWLC/hosts_black.txt 规则数量{counts['hosts_black']}条")
    print(f"./BAWLC/hosts_white.txt 规则数量{counts['hosts_white']}条")
    print(f"./BAWLC/adguard-black.txt 规则数量{counts['adguard_black']}条")
    print(f"./BAWLC/adguard-white.txt 规则数量{counts['adguard_white']}条")
    print("------------------------------------------------------------")

def main():
    """提供统一入口函数"""
    classify_hosts('./Classification/hosts')
    classify_adguard('./Classification/adguard-rules.txt')
    close_all()
    print_report()