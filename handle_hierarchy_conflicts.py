import os

def get_parent_domain(domain):
    parts = domain.split('.')
    if len(parts) <= 1:
        return None
    return '.'.join(parts[1:])

def load_domains_with_lines(filepath):
    """
    返回字典 {域名: 行号}
    """
    domain_line_map = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            domain = line.strip()
            if domain:
                domain_line_map[domain] = i
    return domain_line_map

def find_hierarchy_conflicts_with_lines(domain_line_map):
    """
    domain_line_map: {域名: 行号}
    返回 (keep_set, to_delete_dict)
    to_delete_dict: {被删域名: (其所在行号, 上级域名, 上级行号)}
    """
    domains = set(domain_line_map.keys())
    to_delete = {}

    for domain in domains:
        parent = get_parent_domain(domain)
        while parent:
            if parent in domains:
                to_delete[domain] = (domain_line_map[domain], parent, domain_line_map[parent])
                break
            parent = get_parent_domain(parent)

    keep = domains - set(to_delete.keys())
    return keep, to_delete

def process_hierarchy_conflicts_with_log(input_path, delete_log_path, output_path):
    domain_line_map = load_domains_with_lines(input_path)
    keep, to_delete = find_hierarchy_conflicts_with_lines(domain_line_map)

    os.makedirs(os.path.dirname(delete_log_path), exist_ok=True)
    with open(delete_log_path, 'a', encoding='utf-8') as f:
        for domain in sorted(to_delete.keys()):
            domain_line, parent, parent_line = to_delete[domain]
            f.write(f"{domain} #该域名存在于{os.path.basename(input_path)}第{domain_line}行,其上级域名{parent}存在于{parent_line}行\n")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        for domain in sorted(keep):
            f.write(domain + '\n')

def main():
    # 黑名单处理
    process_hierarchy_conflicts_with_log(
        input_path='./others/blacklist.txt',
        delete_log_path='./Log/delete_Hierarchy.log',
        output_path='./others/AdBlcakList.txt'
    )
    # 白名单处理
    process_hierarchy_conflicts_with_log(
        input_path='./others/whitelist.txt',
        delete_log_path='./Log/delete_Hierarchy.log',
        output_path='./others/AdWhitelist.txt'
    )
    print("上下级域名冲突处理完成，详细删除日志写入 delete_Hierarchy.log")

if __name__ == '__main__':
    main()
