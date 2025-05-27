import os

def merge_black_white_tmp():
    os.makedirs('./ipombaw', exist_ok=True)

    def read_set(file):
        if not os.path.exists(file):
            return set()
        with open(file, 'r', encoding='utf-8') as f:
            return set(line.strip() for line in f if line.strip())

    hosts_bdomain = read_set('./stripping_rules/hosts-bdomain.txt')
    domain = read_set('./stripping_rules/domain.txt')
    adguard_bdomain = read_set('./stripping_rules/adguard-bdomain.txt')
    adguard_wdomain = read_set('./stripping_rules/adguard-wdomain.txt')
    hosts_odomain = read_set('./stripping_rules/hosts-odomain.txt')

    black_tmp = hosts_bdomain.union(domain).union(adguard_bdomain)
    white_tmp = adguard_wdomain.union(hosts_odomain)

    with open('./ipombaw/BlackList_tmp.txt', 'w', encoding='utf-8') as f:
        for d in sorted(black_tmp):
            f.write(d + '\n')

    with open('./ipombaw/WhiteList_tmp.txt', 'w', encoding='utf-8') as f:
        for d in sorted(white_tmp):
            f.write(d + '\n')

    print("[merge_bw_tmp] 黑白名单初步合并完成")
