import os
import re

def filter_hosts(input_file):
    filtered = []
    exclude_keywords = ['local', 'localhost', 'boardcasthost']
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            line_strip = line.strip().lower()
            if not line_strip:
                continue
            # 排除指定关键字
            if any(k in line_strip for k in exclude_keywords):
                continue
            # 排除 0.0.0.0 0.0.0.0
            if line_strip == '0.0.0.0 0.0.0.0':
                continue
            filtered.append(line.strip())
    return filtered

def has_special_chars(line):
    # 特殊符号 / \ ? [ ] # =
    if re.search(r'[\\/\\?\[\]#=]', line):
        return True
    # 判断 | 是否出现在 ^ 之后，意思是 ^ 后面紧跟 |
    # 例如匹配 ^| 或者 ...^|
    # 先找所有 ^ 出现的位置，检查紧跟的字符是不是 |
    positions = [m.start() for m in re.finditer(r'\^', line)]
    for pos in positions:
        if pos + 1 < len(line) and line[pos + 1] == '|':
            return True
    return False

def filter_adguard(input_file):
    adguard_keep = []
    others = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            line_strip = line.strip()
            if not line_strip:
                continue
            if has_special_chars(line_strip):
                others.append(line_strip)
            else:
                adguard_keep.append(line_strip)
    return adguard_keep, others

def write_list_to_file(lines, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        for line in lines:
            f.write(line + '\n')

def main():
    hosts_file = './others/hosts'
    adguard_file = './others/adguard.txt'
    others_file = './others/others.txt'
    adguardrules_file = './others/adguardrules.txt'

    # 过滤hosts
    filtered_hosts = filter_hosts(hosts_file)
    write_list_to_file(filtered_hosts, hosts_file)
    print(f"Hosts过滤后条目数: {len(filtered_hosts)}")

    # 过滤adguard，部分移动到others
    adguard_keep, others_extra = filter_adguard(adguard_file)
    # 先把过滤后的adguard写回adguardrules.txt
    write_list_to_file(adguard_keep, adguardrules_file)
    # others.txt 追加新筛选出来的others_extra内容
    if others_extra:
        with open(others_file, 'a', encoding='utf-8') as f:
            for line in others_extra:
                f.write(line + '\n')
    print(f"AdGuard规则过滤后条目数: {len(adguard_keep)}，其他转移到others.txt条目数: {len(others_extra)}")

if __name__ == '__main__':
    main()
