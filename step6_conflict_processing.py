import os
from collections import defaultdict

# 路径配置

os.makedirs('./Log', exist_ok=True)
os.makedirs('./output', exist_ok=True)

white_tmp_path = './ipombaw/WhiteList_tmp.txt'
black_tmp_path = './ipombaw/BlackList_tmp.txt'
conflict_log_path = './Log/Conflict_handling.log'
white_clean_path = './ipombaw/WhiteList.txt'
black_clean_path = './ipombaw/BlackList.txt'
hierarchy_log_path = './Log/Hierarchy_conflict.log'
output_white_path = './output/AdWhiteList.txt'
output_black_path = './output/AdBlackList.txt'

def load_domains_with_line_numbers(file_path):
    domain_to_lines = defaultdict(list)
    with open(file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            domain = line.strip()
            if domain:
                domain_to_lines[domain].append(i)
    return domain_to_lines

def find_hierarchy_conflicts(domains):
    domain_set = set(domains)
    conflicts = {}
    clean = []
    domain_to_line = {domain: i + 1 for i, domain in enumerate(domains)}

    for domain in domains:
        parts = domain.split('.')
        for i in range(1, len(parts)):
            parent = '.'.join(parts[i:])
            if parent in domain_set:
                conflicts[domain] = parent
                break
        else:
            clean.append(domain)
    return conflicts, clean, domain_to_line

def main():
    """提供统一入口函数"""
    if os.path.exists(white_tmp_path) and os.path.exists(black_tmp_path):
        white_domains = load_domains_with_line_numbers(white_tmp_path)
        black_domains = load_domains_with_line_numbers(black_tmp_path)

        conflict_domains = set(white_domains.keys()) & set(black_domains.keys())

        with open(conflict_log_path, 'w', encoding='utf-8') as conflict_log, \
             open(white_clean_path, 'w', encoding='utf-8') as white_out, \
             open(black_clean_path, 'w', encoding='utf-8') as black_out:

            for domain in sorted(conflict_domains):
                white_lines = ','.join(map(str, white_domains[domain]))
                black_lines = ','.join(map(str, black_domains[domain]))
                conflict_log.write(f"{domain} #该条目为黑白名单冲突,在./ipombaw/WhiteList_tmp.txt第{white_lines}行,在./ipombaw/BlackList_tmp.txt第{black_lines}行\n")

            for domain in sorted(set(white_domains.keys()) - conflict_domains):
                white_out.write(domain + '\n')

            for domain in sorted(set(black_domains.keys()) - conflict_domains):
                black_out.write(domain + '\n')

        conflict_count = len(conflict_domains)

        def load_cleaned_list(path):
            with open(path, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]

        white_list = load_cleaned_list(white_clean_path)
        black_list = load_cleaned_list(black_clean_path)

        white_conflicts, white_clean, white_line_map = find_hierarchy_conflicts(white_list)
        black_conflicts, black_clean, black_line_map = find_hierarchy_conflicts(black_list)

        with open(hierarchy_log_path, 'w', encoding='utf-8') as log:
            for domain, parent in white_conflicts.items():
                log.write(f"{domain} #该条目为白名单内的层级冲突,其上级域名{parent}在中第{white_line_map[parent]}行\n")
            for domain, parent in black_conflicts.items():
                log.write(f"{domain} #该条目为黑名单内的层级冲突,其上级域名{parent}在中第{black_line_map[parent]}行\n")

        with open(output_white_path, 'w', encoding='utf-8') as f:
            for domain in sorted(white_clean):
                f.write(domain + '\n')

        with open(output_black_path, 'w', encoding='utf-8') as f:
            for domain in sorted(black_clean):
                f.write(domain + '\n')

        print("黑白名单冲突处理完成")
        print("------------------------------------------------------------")
        print(f"./Log/Conflict_handling.log 共计{conflict_count}条,相关信息已打印到log")
        print("------------------------------------------------------------")
        print("层级冲突处理完成")
        hierarchy_count = len(white_conflicts) + len(black_conflicts)
        print("------------------------------------------------------------")
        print(f"./Log/Hierarchy_conflict.log 共{hierarchy_count}条,相关信息已打印到log")
        print(f"处理后的白名单{len(white_clean)}条,已保存到./output/AdWhiteList.txt")
        print(f"处理后的黑名单{len(black_clean)}条,已保存到./output/AdBlackList.txt")
        print("------------------------------------------------------------")

    else:
        print("错误：缺少必要的输入文件，请确认 ./ipombaw/WhiteList_tmp.txt 和 ./ipombaw/BlackList_tmp.txt 文件存在。")