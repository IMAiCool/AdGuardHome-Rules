import os
import re
import requests
from datetime import datetime, timedelta
from urllib.parse import urlparse

# 目录设置
INPUT_DIR = 'input'
OUTPUT_DIR = 'output'
LOG_DIR = 'Log'
OTHERS_DIR = 'others'

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(OTHERS_DIR, exist_ok=True)

# 规则文件名
LOCAL_RULES_FILE = os.path.join(INPUT_DIR, 'local-rules.txt')
URLS_FILE = os.path.join(INPUT_DIR, 'urls.txt')

# 正则表达式定义
ADGUARD_STANDARD_RE = re.compile(
    r'^(?:\|\|[^\/\?\[\\\]]+\^(\$important)?|@@\|\|[^\/\?\[\\\]]+\^(\$important)?|@@\|\|[^\/\?\[\\\]]+|'
    r'\|\|[^\/\?\[\\\]]+)$')

SPECIAL_CHARS = set('/?\\[]')

# 时间格式
NOW = datetime.now()
NEXT_UPDATE = NOW + timedelta(hours=12)
NOW_STR = NOW.strftime('%Y-%m-%d %H:%M:%S')
NEXT_UPDATE_STR = NEXT_UPDATE.strftime('%Y-%m-%d %H:%M:%S')

# 读取上游规则列表，格式：规则名称: URL
def read_upstream_urls():
    upstreams = {}
    with open(URLS_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or ':' not in line:
                continue
            name, url = line.split(':', 1)
            name = name.strip()
            url = url.strip()
            upstreams[name] = url
    return upstreams

# 下载远程规则
def download_upstream_rules(upstreams):
    rules = []
    upstream_names = []
    for name, url in upstreams.items():
        try:
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            content = resp.text
            # 去除注释和空行
            lines = [line.strip() for line in content.splitlines()]
            lines = [line for line in lines if line and not line.startswith('!') and not line.startswith('[Adblock')]
            rules.extend(lines)
            upstream_names.append(name)
        except Exception as e:
            print(f'下载失败: {name} {url} 错误: {e}')
    return rules, upstream_names

# 读取本地规则
def read_local_rules():
    if not os.path.isfile(LOCAL_RULES_FILE):
        return []
    with open(LOCAL_RULES_FILE, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f.readlines()]
    # 去除空行和注释行
    return [line for line in lines if line and not line.startswith('!')]

# 检查是否含特殊字符
def contains_special_char(line):
    return any(ch in line for ch in SPECIAL_CHARS)

# 规则分类：hosts / adguard / css
def classify_rules(rules):
    hosts = []
    adguard_rules = []
    css = []

    # hosts格式一般是 IP + 空格 + 域名，或者仅域名
    # 这里简化判断，判断是否包含空格且左边为IP或域名
    ip_pattern = re.compile(r'^(?:\d{1,3}\.){3}\d{1,3}$')

    for rule in rules:
        rule = rule.strip()
        if not rule:
            continue
        # 简单判断hosts：例如 "0.0.0.0 example.com" 或者类似域名形式
        if ' ' in rule:
            ip_part = rule.split(' ')[0]
            if ip_pattern.match(ip_part):
                # hosts规则
                # 检查是否含特殊符号
                if contains_special_char(rule):
                    css.append(rule)
                else:
                    hosts.append(rule)
                continue
        # 非hosts规则，判定为adguard格式或css
        # 判断是否符合标准adguard格式
        if ADGUARD_STANDARD_RE.match(rule):
            if contains_special_char(rule):
                css.append(rule)
            else:
                adguard_rules.append(rule)
        else:
            # 不符合adguard标准规则，视为css或正则
            css.append(rule)

    return hosts, adguard_rules, css

# 对adguard规则进行黑白名单分类
def classify_black_white(adguard_rules):
    blacklist = []
    whitelist = []
    css = []
    for rule in adguard_rules:
        # 白名单以 @@ 开头
        if rule.startswith('@@'):
            whitelist.append(rule)
        else:
            blacklist.append(rule)
    return blacklist, whitelist, css

# 去重函数，保留顺序
def unique_list(seq):
    seen = set()
    result = []
    for item in seq:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result

# 转换规则格式为域名（剥离格式）
def to_domain(rule):
    # 去除开头的 || 或 @@||
    domain = rule
    if rule.startswith('@@||'):
        domain = rule[4:]
    elif rule.startswith('||'):
        domain = rule[2:]
    elif rule.startswith('@@'):
        domain = rule[2:]
    # 去除尾部的 ^ 或 ^$important 等
    domain = re.sub(r'\^(\$important)?$', '', domain)
    # 可能还含有其他参数，简单去除 $, 后续可改进
    domain = domain.split('$')[0]
    domain = domain.strip()
    return domain.lower()

# 转换 hosts 规则到域名
def hosts_to_domain(line):
    # hosts 规则通常 "IP domain"
    parts = line.split()
    if len(parts) >= 2:
        return parts[1].lower()
    return ''

# 转换域名回adguard规则格式
def domain_to_black(domain):
    return f'||{domain}^'

def domain_to_white(domain):
    return f'@@||{domain}^'

# 查找上级域名
def parent_domain(domain):
    parts = domain.split('.')
    if len(parts) <= 2:
        return None
    return '.'.join(parts[1:])

# 写文件工具，带头部信息
def write_file_with_header(filepath, header_lines, lines):
    with open(filepath, 'w', encoding='utf-8') as f:
        for line in header_lines:
            f.write(line + '\n')
        f.write('\n')
        for line in lines:
            f.write(line + '\n')

# 主函数
def main():
    # 1. 读取上游规则URL列表
    upstreams = read_upstream_urls()

    # 2. 下载远程规则
    upstream_rules, upstream_names = download_upstream_rules(upstreams)

    # 3. 读取本地规则
    local_rules = read_local_rules()

    # 4. 合并规则
    all_rules = local_rules + upstream_rules

    # 写 all list
    write_file_with_header(
        os.path.join(OTHERS_DIR, 'alllist.txt'),
        [f'# 规则合并列表 - 更新时间: {NOW_STR}'],
        all_rules
    )

    # 5. 分类
    hosts, adguard_rules, css = classify_rules(all_rules)

    # 再检查 hosts 里是否有特殊字符，特殊字符的放到 css
    hosts_clean = []
    for h in hosts:
        if contains_special_char(h):
            css.append(h)
        else:
            hosts_clean.append(h)
    hosts = hosts_clean

    # 6. 对adguard规则再分类黑白名单
    blacklist, whitelist, css_extra = classify_black_white(adguard_rules)
    # 如果css_extra不为空，追加到css
    if css_extra:
        css.extend(css_extra)

    # 7. 去重 hosts, blacklist, whitelist
    hosts = unique_list(hosts)
    blacklist = unique_list(blacklist)
    whitelist = unique_list(whitelist)

    # 写分类文件到 others
    write_file_with_header(os.path.join(OTHERS_DIR, 'hosts.txt'), ['# hosts规则'], hosts)
    write_file_with_header(os.path.join(OTHERS_DIR, 'adguard-rules.txt'), ['# adguard规则'], adguard_rules)
    write_file_with_header(os.path.join(OTHERS_DIR, 'all.css'), ['# CSS及正则规则'], css)
    write_file_with_header(os.path.join(OTHERS_DIR, 'blacklist.txt'), ['# 黑名单规则'], blacklist)
    write_file_with_header(os.path.join(OTHERS_DIR, 'whitelist.txt'), ['# 白名单规则'], whitelist)

    # 8. 转换为 domain 格式
    hosts_domain = set(hosts_to_domain(line) for line in hosts)
    blacklist_domain = set(to_domain(r) for r in blacklist)
    whitelist_domain = set(to_domain(r) for r in whitelist)

    # 9. 去重交叉处理
    # 去重所有三组的交叉条目
    all_domains = hosts_domain | blacklist_domain | whitelist_domain

    # 去重条目 - 删除重复出现在多个列表中的
    delete_rules = set()
    # 统计交叉域名
    cross_domains = set()

    # 逻辑1: 域名在多个集合中都存在即为冲突（黑名单和白名单冲突，hosts和黑名单冲突等）
    # 先找重复
    # 交集hosts&blacklist
    hosts_blacklist_inter = hosts_domain & blacklist_domain
    # 交集hosts&whitelist
    hosts_whitelist_inter = hosts_domain & whitelist_domain
    # blacklist & whitelist
    blacklist_whitelist_inter = blacklist_domain & whitelist_domain

    # 根据规则删除和记录日志
    delete_rules.update(hosts_blacklist_inter)
    delete_rules.update(hosts_whitelist_inter)
    delete_rules.update(blacklist_whitelist_inter)

    # 删除交叉域名
    hosts_domain.difference_update(delete_rules)
    blacklist_domain.difference_update(delete_rules)
    whitelist_domain.difference_update(delete_rules)

    # 记录list-in-all.log (域名在白名单中同时也出现在hosts或黑名单中)
    list_in_all = hosts_whitelist_inter | blacklist_whitelist_inter

    # 记录list-in-both.log (域名同时出现在hosts和黑名单中)
    list_in_both = hosts_blacklist_inter

    # 处理层级冲突：
    # 若域名在hosts-domain或blacklist-domain中，且其上级域名存在于whitelist-domain中，则删除该上级域名，写入delete_Hierarchy.log
    delete_hierarchy = set()
    for domain in hosts_domain | blacklist_domain:
        pdom = parent_domain(domain)
        if pdom and pdom in whitelist_domain:
            whitelist_domain.remove(pdom)
            delete_hierarchy.add(pdom)

    # 若域名在whitelist-domain中，且其上级域名也在whitelist-domain中，删除其上级域名，写入delete_white.log
    delete_white = set()
    for domain in whitelist_domain.copy():
        pdom = parent_domain(domain)
        if pdom and pdom in whitelist_domain:
            whitelist_domain.remove(pdom)
            delete_white.add(pdom)

    # 写日志文件（完整条目格式）
    def write_log(filename, domainset):
        path = os.path.join(LOG_DIR, filename)
        with open(path, 'w', encoding='utf-8') as f:
            for d in sorted(domainset):
                f.write(d + '\n')

    write_log('delete-rules.log', delete_rules)
    write_log('list-in-all.log', list_in_all)
    write_log('list-in-both.log', list_in_both)
    write_log('delete_Hierarchy.log', delete_hierarchy)
    write_log('delete_white.log', delete_white)

    # 10. 合并 hosts-domain 和 blacklist-domain 为黑名单，格式化成标准adguard规则输出
    black_list_rules = [domain_to_black(d) for d in sorted(hosts_domain | blacklist_domain)]
    white_list_rules = [domain_to_white(d) for d in sorted(whitelist_domain)]

    # 头部信息生成
    def gen_header(name, purpose, upstream_names, total_upstream_count, local_count, rule_count):
        lines = [
            f'# 规则名称及用途: {name} - {purpose}',
            f'# 上游规则来源: {", ".join(upstream_names)}',
            f'# 上游规则总数: {total_upstream_count}',
            f'# 本规则数量: {rule_count}',
            f'# 本地规则数量: {local_count}',
            f'# 更新时间: {NOW_STR}',
            f'# 更新周期: 每12小时自动更新一次',
            '#' + '-'*40
        ]
        return lines

    total_upstream_count = len(upstream_rules)
    local_count = len(local_rules)

    black_header = gen_header('黑名单规则 black_list.txt', '屏蔽规则', upstream_names, total_upstream_count, local_count, len(black_list_rules))
    white_header = gen_header('白名单规则 white_list.txt', '放行规则', upstream_names, total_upstream_count, local_count, len(white_list_rules))

    # 写入 output
    write_file_with_header(os.path.join(OUTPUT_DIR, 'black_list.txt'), black_header, black_list_rules)
    write_file_with_header(os.path.join(OUTPUT_DIR, 'white_list.txt'), white_header, white_list_rules)

    # 11. 控制台输出报告
    print(f'[规则处理报告] {NOW_STR}')
    print('-------------------------------------')
    print('■ 输入规则统计')
    print(f'  ├─ 本地规则: {local_count}条')
    print(f'  └─ 远程规则: {total_upstream_count}条（{len(upstream_names)}个源）')
    print()
    print('■ 分类处理结果')
    print(f'  ├─ 基础规则(alllist.txt): {len(all_rules)}条')
    print(f'  ├─ CSS/正则规则(all.css): {len(css)}条')
    print(f'  ├─ hosts规则初筛(hosts.txt): {len(hosts)}条')
    print(f'  └─ adguard规则初筛(blacklist.txt): {len(blacklist)}条')
    print()
    print('■ 冲突处理统计')
    print(f'  ├─ 直接冲突条目: {len(list_in_all)}条（list-in-all.log）')
    print(f'  ├─ 黑名单冲突条目: {len(list_in_both)}条（list-in-both.log）')
    print(f'  ├─ 黑白名单冲突条目: {len(delete_white)}条（delete_white.log）')
    print(f'  ├─ 去重条目: {len(delete_rules)}条（delete-rules.log）')
    print(f'  └─ 层级冲突条目: {len(delete_hierarchy)}条（delete_Hierarchy.log）')
    print()
    print('■ 最终生效规则')
    print(f'  ├─ 黑名单生效: {len(black_list_rules)}条（output/black_list.txt）')
    print(f'  └─ 白名单生效: {len(white_list_rules)}条（output/white_list.txt）')
    print()
    print(f'下次更新: {NEXT_UPDATE_STR}')

if __name__ == '__main__':
    main()
