import os

def detect_conflicts():
    os.makedirs('./Log', exist_ok=True)
    os.makedirs('./TMP', exist_ok=True)

    def read_list(file):
        if not os.path.exists(file):
            return []
        with open(file, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]

    white_list = read_list('./ipombaw/WhiteList_tmp.txt')
    black_list = read_list('./ipombaw/BlackList_tmp.txt')

    white_set = set(white_list)
    black_set = set(black_list)

    both_log = []
    white_tmp = set()
    black_tmp = set(black_set)  # copy

    # 先处理冲突：同域名在白黑名单中均存在
    for domain in white_set.intersection(black_set):
        # 检查黑名单中是否存在其上级域名
        parent_found = False
        parts = domain.split('.')
        for i in range(1, len(parts)):
            parent = '.'.join(parts[i:])
            if parent in black_set and parent != domain:
                parent_found = True
                # 记录日志
                both_log.append(f"{domain} 上级域名 {parent} 在黑名单中存在")
                white_tmp.add(domain)
                black_tmp.discard(domain)
                break
        if not parent_found:
            # 记录日志
            both_log.append(f"{domain} 同时出现在黑白名单中")
    # 写日志
    with open('./Log/both-in-white-and-black.log', 'w', encoding='utf-8') as flog:
        for line in both_log:
            flog.write(line + '\n')

    # 没有冲突的直接写入TMP目录
    with open('./TMP/White_list_tmp.txt', 'w', encoding='utf-8') as fwhite:
        for w in white_tmp.union(white_set - black_set):
            fwhite.write(w + '\n')

    with open('./TMP/Black_list_tmp.txt', 'w', encoding='utf-8') as fblack:
        for b in black_tmp:
            fblack.write(b + '\n')

    # 同文件层级冲突检测
    hierarchy_log = []
    def check_hierarchy_conflict(lines, list_name):
        lines = sorted(lines)
        conflict_domains = []
        domain_index = {d: i for i, d in enumerate(lines)}

        for i in range(len(lines)):
            for j in range(i + 1, len(lines)):
                # 如果j是i的上级域名
                if lines[j].endswith(lines[i]):
                    conflict_domains.append((lines[i], lines[j]))
        for low, high in conflict_domains:
            hierarchy_log.append(f"{low}#{list_name}内层级冲突,上级域名{high}")

    with open('./TMP/Black_list_tmp.txt', 'r', encoding='utf-8') as fblack:
        black_lines = [line.strip() for line in fblack if line.strip()]
    with open('./TMP/White_list_tmp.txt', 'r', encoding='utf-8') as fwhite:
        white_lines = [line.strip() for line in fwhite if line.strip()]

    check_hierarchy_conflict(black_lines, '黑名单')
    check_hierarchy_conflict(white_lines, '白名单')

    with open('./Log/Hierarchy_conflict.log', 'w', encoding='utf-8') as flog:
        for line in hierarchy_log:
            flog.write(line + '\n')

    # 输出最终无冲突列表
    with open('./output/AdBlackList.txt', 'w', encoding='utf-8') as fblack:
        for d in black_lines:
            if not any(d in c for c in hierarchy_log):
                fblack.write(d + '\n')

    with open('./output/AdWhiteList.txt', 'w', encoding='utf-8') as fwhite:
        for d in white_lines:
            if not any(d in c for c in hierarchy_log):
                fwhite.write(d + '\n')

    print("[conflict_handler] 冲突检测完成")
