import os
import re

# 创建分类目录
os.makedirs('./Classification', exist_ok=True)

# 分类统计
count_hosts = 0
count_adguard = 0
count_domain = 0
count_others = 0

# 分类文件路径
file_hosts = './Classification/hosts'
file_adguard = './Classification/adguard-rules.txt'
file_domain = './Classification/domain.txt'
file_others = './Classification/others.txt'

# 分类写入器
writers = {
    'hosts': open(file_hosts, 'w', encoding='utf-8'),
    'adguard': open(file_adguard, 'w', encoding='utf-8'),
    'domain': open(file_domain, 'w', encoding='utf-8'),
    'others': open(file_others, 'w', encoding='utf-8'),
}

# 匹配规则
adguard_patterns = [
    r'^\|\|[^^]+$',                          # ||example.com
    r'^\|\|[^^]+\^$',                        # ||example.com^
    r'^@@\|\|[^^]+$',                        # @@||example.com
    r'^@@\|\|[^^]+\^$',                      # @@||example.com^
    r'^\|\|[^^]+\^\$important$',             # ||example.com^$important
    r'^@@\|\|[^^]+\^\$important$',           # @@||example.com^$important
]

domain_pattern = re.compile(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
ip_pattern = re.compile(r'^(127\.0\.0\.1|0\.0\.0\.0|::)[\s\t]+[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

def classify_rule(rule: str):
    global count_hosts, count_adguard, count_domain, count_others

    # 判断 hosts
    if ip_pattern.match(rule):
        writers['hosts'].write(rule + '\n')
        count_hosts += 1
    # 判断 AdGuard
    elif any(re.match(pat, rule) for pat in adguard_patterns):
        writers['adguard'].write(rule + '\n')
        count_adguard += 1
    # 判断域名
    elif domain_pattern.match(rule):
        writers['domain'].write(rule + '\n')
        count_domain += 1
    else:
        writers['others'].write(rule + '\n')
        count_others += 1

def classify_rules(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            rule = line.strip()
            if rule:
                classify_rule(rule)

def close_files():
    for w in writers.values():
        w.close()

def print_report():
    print("处理完成")
    print("------------------------------------------------------------")
    print(f"纯hosts规则{count_hosts}条,输出到./Classification/hosts")
    print(f"标准adguard规则{count_adguard}条输出到./Classification/adguard-rules.txt")
    print(f"纯域名规则{count_domain}条./Classification/domain.txt")
    print(f"其他规则{count_others}条./Classification/others.txt")
    print("------------------------------------------------------------")

def main():
    """提供统一入口函数"""
    classify_rules('./Merge-rule/merge_rules.txt')
    close_files()
    print_report()