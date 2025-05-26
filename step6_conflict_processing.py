import os

# 文件路径
white_tmp = "./ipombaw/WhiteList_tmp.txt"
black_tmp = "./ipombaw/BlackList_tmp.txt"
conflict_log = "./Log/both-in-white-and-black.log"
hierarchy_conflict_log = "./Log/Hierarchy_conflict.log"
white_final = "./output/AdWhiteList.txt"
black_final = "./output/AdBlackList.txt"

os.makedirs("./Log", exist_ok=True)
os.makedirs("./output", exist_ok=True)
os.makedirs("./output", exist_ok=True)

# 读取文件，保存条目及行号
def read_with_line_num(file_path):
    mapping = {}
    with open(file_path, encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            item = line.strip()
            if item:
                mapping[item] = i
    return mapping

white_map = read_with_line_num(white_tmp)
black_map = read_with_line_num(black_tmp)

def main():
    # 1. 处理白黑名单冲突
    conflicts = []
    white_only = []
    black_only = []

    for w_rule, w_line in white_map.items():
        if w_rule in black_map:
            b_line = black_map[w_rule]
            conflicts.append(f"{w_rule} #该条目为黑白名单冲突,在./ipombaw/WhiteList_tmp.txt第{w_line}行,在./ipombaw/BlackList_tmp.txt第{b_line}行")
        else:
            white_only.append(w_rule)

    for b_rule, b_line in black_map.items():
        if b_rule not in white_map:
            black_only.append(b_rule)

    with open(conflict_log, "w", encoding='utf-8') as f:
        for line in conflicts:
            f.write(line + "\n")

    with open("./ipombaw/WhiteList.txt", "w", encoding='utf-8') as f:
        for line in white_only:
            f.write(line + "\n")

    with open("./ipombaw/BlackList.txt", "w", encoding='utf-8') as f:
        for line in black_only:
            f.write(line + "\n")

    print("黑白名单冲突处理完成")
    print("------------------------------------------------------------")
    print(f"{conflict_log} 共计{len(conflicts)}条,相关信息已打印到log")
    print("------------------------------------------------------------")

    # 2. 层级冲突处理

    # 读取冲突后名单
    def read_list(file_path):
        with open(file_path, encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]

    white_list = read_list("./ipombaw/WhiteList.txt")
    black_list = read_list("./ipombaw/BlackList.txt")

    # 建立域名反向索引（方便查找上级域名）
    def domain_levels(domain):
        return domain.split('.')

    def is_subdomain(sub, dom):
        # 判断sub是否是dom的子域名
        return sub == dom or sub.endswith('.' + dom)

    # 查找层级冲突，记录冲突条目及行号和说明
    def find_hierarchy_conflicts(domain_list, file_name):
        conflict_entries = []
        # map 域名到行号
        domain_to_line = {d: i+1 for i, d in enumerate(domain_list)}
        domain_set = set(domain_list)
        for d in domain_list:
            parts = domain_levels(d)
            # 检查上级域名是否存在
            for i in range(1, len(parts)):
                parent = '.'.join(parts[i:])
                if parent in domain_set and parent != d:
                    # 发生层级冲突
                    conflict_entries.append(
                        f"{d}#{file_name}内的层级冲突,其上级域名{parent}在第{domain_to_line[parent]}行"
                    )
                    break
        return conflict_entries


    white_hconflicts = find_hierarchy_conflicts(white_list, "白名单")
    black_hconflicts = find_hierarchy_conflicts(black_list, "黑名单")

    # 写入层级冲突日志
    with open(hierarchy_conflict_log, "w", encoding='utf-8') as f:
        for line in white_hconflicts + black_hconflicts:
            f.write(line + "\n")

    # 从白名单和黑名单中过滤掉层级冲突条目
    def filter_conflicts(orig_list, conflicts):
        conflict_domains = set()
        for c in conflicts:
            domain = c.split('#')[0]
            conflict_domains.add(domain)
        return [d for d in orig_list if d not in conflict_domains]

    white_filtered = filter_conflicts(white_list, white_hconflicts)
    black_filtered = filter_conflicts(black_list, black_hconflicts)

    # 写入最终结果
    with open(white_final, "w", encoding='utf-8') as f:
        for d in white_filtered:
            f.write(d + "\n")

    with open(black_final, "w", encoding='utf-8') as f:
        for d in black_filtered:
            f.write(d + "\n")

    print("层级冲突处理完成")
    print("------------------------------------------------------------")
    print(f"{hierarchy_conflict_log} 共{len(white_hconflicts) + len(black_hconflicts)}条,相关信息已打印到log")
    print(f"处理后的白名单{len(white_filtered)}条,已保存到{white_final}")
    print(f"处理后的黑名单{len(black_filtered)}条,已保存到{black_final}")
    print("------------------------------------------------------------")


if __name__ == "__main__":
    main()
