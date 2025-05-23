import os
import re

def is_ip_rule(line):
    # 简单判断hosts格式IP规则，形如：0.0.0.0 example.com 或 127.0.0.1 example.com
    # 也允许只IP或者IP+域名
    return bool(re.match(r'^\s*(\d{1,3}\.){3}\d{1,3}\s+\S+', line))

def is_domain_rule(line):
    # 纯域名，比如 example.com 或带注释符号忽略已处理
    # 简单判断是否为域名，含字母数字点-，且不含特殊adblock符号
    return bool(re.match(r'^[\w.-]+\.[a-z]{2,}$', line))

def is_adguard_rule(line):
    # 判断是否是AdGuard格式，通常以||开头，可能带^或$important，或以@@开头（例外放这里）
    return line.startswith('||') or line.startswith('@@')

def classify_rules(input_file):
    hosts_rules = []
    adguard_rules = []
    others_rules = []

    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if is_ip_rule(line):
                hosts_rules.append(line)
            elif is_domain_rule(line):
                hosts_rules.append(line)
            elif is_adguard_rule(line):
                adguard_rules.append(line)
            else:
                others_rules.append(line)

    return hosts_rules, adguard_rules, others_rules

def write_list_to_file(lines, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        for line in lines:
            f.write(line + '\n')

def main():
    input_file = './others/merged-rules.txt'

    hosts_rules, adguard_rules, others_rules = classify_rules(input_file)

    write_list_to_file(hosts_rules, './others/hosts')
    write_list_to_file(adguard_rules, './others/adguard.txt')
    write_list_to_file(others_rules, './others/others.txt')

    print(f"分类完成：hosts({len(hosts_rules)}条), adguard({len(adguard_rules)}条), others({len(others_rules)}条)")

if __name__ == '__main__':
    main()
