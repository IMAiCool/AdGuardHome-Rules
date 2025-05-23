import os

def load_domains_with_line_numbers(filepath):
    """
    返回字典：{域名: 行号}
    """
    domain_line_map = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            domain = line.strip()
            if domain:
                domain_line_map[domain] = i
    return domain_line_map

def write_conflict_log(conflicts, black_map, white_map, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        for domain in sorted(conflicts):
            black_line = black_map.get(domain, '?')
            white_line = white_map.get(domain, '?')
            f.write(f"{domain} #当前域名为黑白名单冲突剔除,位于black.txt第{black_line}行,位于adguard-whited.txt第{white_line}行\n")

def write_list(lines, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        for line in sorted(lines):
            f.write(line + '\n')

def main():
    black_file = './others/black.txt'
    white_file = './others/adguard-whited.txt'
    conflict_log = './Log/list-in-both.log'
    blacklist_out = './others/blacklist.txt'
    whitelist_out = './others/whitelist.txt'

    black_map = load_domains_with_line_numbers(black_file)
    white_map = load_domains_with_line_numbers(white_file)

    black_domains = set(black_map.keys())
    white_domains = set(white_map.keys())

    conflicts = black_domains.intersection(white_domains)
    only_black = black_domains - conflicts
    only_white = white_domains - conflicts

    write_conflict_log(conflicts, black_map, white_map, conflict_log)
    write_list(only_black, blacklist_out)
    write_list(only_white, whitelist_out)

    print(f"冲突域名（同时存在于黑白名单）共 {len(conflicts)} 条，已写入 {conflict_log}")
    print(f"黑名单独有域名 {len(only_black)} 条，写入 {blacklist_out}")
    print(f"白名单独有域名 {len(only_white)} 条，写入 {whitelist_out}")

if __name__ == '__main__':
    main()
