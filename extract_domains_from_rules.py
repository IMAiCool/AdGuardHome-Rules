import os
import re

def extract_domain_from_adguard_rule(line):
    line = line.strip()
    # 去掉可能的白名单前缀 @@
    if line.startswith('@@'):
        line = line[2:]
    # 确保以 || 开头
    if not line.startswith('||'):
        return ''  # 不符合预期格式，返回空

    # 去掉前导 ||
    line = line[2:]

    # 找 ^ 的位置
    caret_pos = line.find('^')
    if caret_pos != -1:
        domain = line[:caret_pos]
    else:
        domain = line

    return domain.strip()

def extract_domain_from_hosts_rule(line):
    parts = line.strip().split()
    if len(parts) == 1:
        return parts[0]
    elif len(parts) > 1:
        return parts[1]
    return ''

def process_file(input_path, output_path, mode='adguard'):
    domains = set()
    with open(input_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if mode == 'adguard':
                domain = extract_domain_from_adguard_rule(line)
            else:
                domain = extract_domain_from_hosts_rule(line)
            if domain:
                domains.add(domain)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        for d in sorted(domains):
            f.write(d + '\n')

def main():
    process_file('./others/adguard-black.txt', './others/adguard-blackd.txt', mode='adguard')
    process_file('./others/adguard-white.txt', './others/adguard-whited.txt', mode='adguard')
    process_file('./others/hosts', './others/hostsd', mode='hosts')
    print("域名提取完成，输出到 adguard-blackd.txt, adguard-whited.txt, hostsd")

if __name__ == '__main__':
    main()
