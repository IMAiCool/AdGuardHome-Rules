
import os
import re
import requests
from datetime import datetime
from urllib.parse import urlparse

INPUT_DIR = "input"
OUTPUT_DIR = "output"
OTHERS_DIR = "others"
LOG_DIR = "Log"

def load_local_rules(file_path):
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return f.readlines()

def load_upstream_rules(urls_file):
    rules = []
    sources = []
    with open(urls_file, "r", encoding="utf-8") as f:
        for line in f:
            if ':' not in line:
                continue
            name, url = line.strip().split(':', 1)
            try:
                response = requests.get(url.strip(), timeout=20)
                response.raise_for_status()
                content = response.text
                cleaned = [l for l in content.splitlines() if l.strip() and not l.startswith(('!', '#', '['))]
                rules.extend(cleaned)
                sources.append(name.strip())
            except Exception as e:
                print(f"[!] 下载失败: {name.strip()} - {e}")
    return rules, sources

def write_file(filepath, lines, meta_name, meta_usage, total_upstream, rule_count):
    header = [
        f"! 规则名称: {meta_name}",
        f"! 用途: {meta_usage}",
        f"! 来源: 本地规则 + 上游规则",
        f"! 上游总规则数量: {total_upstream}",
        f"! 本文件规则数量: {rule_count}",
        f"! 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"! 更新周期: 每12小时",
        ""
    ]
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(header))
        f.write("\n".join(lines))

def is_host_rule(line):
    return re.match(r"^(0.0.0.0|127.0.0.1)\s+([a-zA-Z0-9.-]+)$", line)

def normalize_host_rule(line):
    parts = line.strip().split()
    if len(parts) == 2:
        return f"127.0.0.1 {parts[1]}"
    return None

def is_css_rule(line):
    return any(s in line for s in ['/', '\\', '[', ']', '?'])

def classify_adguard_rule(line):
    line = line.strip()
    if line.startswith('@@'):
        return 'white'
    elif line.startswith('||'):
        return 'black'
    return None

def extract_domain(line):
    line = line.strip()
    if line.startswith('127.0.0.1'):
        return line.split()[1]
    match = re.search(r"(?:\|\|)([a-z0-9.-]+)", line)
    return match.group(1) if match else None

def format_adguard_rule(domain, allow=False):
    return f"@@||{domain}^" if allow else f"||{domain}^"

def main():
    local_rules = load_local_rules(os.path.join(INPUT_DIR, "local-rules.txt"))
    upstream_rules, source_names = load_upstream_rules(os.path.join(INPUT_DIR, "urls.txt"))
    total_upstream = len(upstream_rules)
    all_rules = local_rules + upstream_rules

    with open(os.path.join(OTHERS_DIR, "alllist.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(all_rules))

    hosts, adguard, css = [], [], []
    for line in all_rules:
        line = line.strip()
        if not line:
            continue
        if is_host_rule(line):
            norm = normalize_host_rule(line)
            if norm: hosts.append(norm)
        elif is_css_rule(line):
            css.append(line)
        else:
            adguard.append(line)

    with open(os.path.join(OTHERS_DIR, "hosts.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(set(hosts)))
    with open(os.path.join(OTHERS_DIR, "adguard-rules.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(adguard))
    with open(os.path.join(OTHERS_DIR, "all.css"), "w", encoding="utf-8") as f:
        f.write("\n".join(css))

    blacklist, whitelist = set(), set()
    for rule in adguard:
        if is_css_rule(rule):
            continue
        kind = classify_adguard_rule(rule)
        domain = extract_domain(rule)
        if domain and kind == 'black':
            blacklist.add(format_adguard_rule(domain))
        elif domain and kind == 'white':
            whitelist.add(format_adguard_rule(domain, allow=True))

    write_file(os.path.join(OUTPUT_DIR, "blacklist.txt"), sorted(blacklist), "黑名单规则", "屏蔽广告、恶意域名等", total_upstream, len(blacklist))
    write_file(os.path.join(OUTPUT_DIR, "whitelist.txt"), sorted(whitelist), "白名单规则", "放行某些被误拦的正常站点", total_upstream, len(whitelist))

    host_domains = {extract_domain(line) for line in hosts if extract_domain(line)}
    black_domains = {extract_domain(line) for line in blacklist if extract_domain(line)}
    white_domains = {extract_domain(line) for line in whitelist if extract_domain(line)}

    delete_log = []
    list_both_log = []
    delete_parent_log = []

    final_black = set()
    for d in black_domains.union(host_domains):
        if d in white_domains:
            delete_log.append(d)
            continue
        conflict = d in black_domains and d in host_domains
        if conflict:
            list_both_log.append(d)
            host_domains.discard(d)
        if any(p for p in white_domains if d.endswith("." + p)):
            delete_parent_log.append(d)
            continue
        final_black.add(d)

    with open(os.path.join(LOG_DIR, "delete-rules.log"), "w", encoding="utf-8") as f:
        f.write("\n".join(delete_log))
    with open(os.path.join(LOG_DIR, "list-in-both.log"), "w", encoding="utf-8") as f:
        f.write("\n".join(list_both_log))
    with open(os.path.join(LOG_DIR, "delete_rules.log"), "w", encoding="utf-8") as f:
        f.write("\n".join(delete_parent_log))

    black_list_rules = [format_adguard_rule(d) for d in final_black]
    white_list_rules = [format_adguard_rule(d, allow=True) for d in white_domains]

    write_file(os.path.join(OUTPUT_DIR, "black_list.txt"), sorted(black_list_rules), "黑名单规则", "屏蔽广告、恶意域名等", total_upstream, len(black_list_rules))
    write_file(os.path.join(OUTPUT_DIR, "white_list.txt"), sorted(white_list_rules), "白名单规则", "放行某些被误拦的正常站点", total_upstream, len(white_list_rules))

    # 控制台输出
    print(f"[规则处理报告] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-------------------------------------")
    print(f"■ 输入规则统计")
    print(f"  ├─ 本地规则: {len(local_rules)}条")
    print(f"  └─ 远程规则: {len(upstream_rules)}条（{'/'.join(source_names)}）")
    print(f"■ 分类处理结果")
    print(f"  ├─ 基础规则(alllist.txt): {len(all_rules)}条")
    print(f"  ├─ CSS/正则规则(all.css): {len(css)}条")
    print(f"  ├─ hosts规则初筛(hosts): {len(hosts)}条")
    print(f"  └─ adguard规则初筛(blacklist.txt): {len(blacklist)}条")
    print(f"■ 冲突处理统计")
    print(f"  ├─ 直接冲突条目: {len(delete_log)}条（delete-rules.log）")
    print(f"  ├─ 黑名单冲突条目: {len(list_both_log)}条（list-in-both.log）")
    print(f"  └─ 层级冲突条目: {len(delete_parent_log)}条（delete_rules.log）")
    print(f"■ 最终生效规则")
    print(f"  ├─ 黑名单生效: {len(black_list_rules)}条（output/black_list.txt）")
    print(f"  └─ 白名单生效: {len(white_list_rules)}条（output/white_list.txt）")
    print(f"\n下次更新: {(datetime.now()).replace(hour=(datetime.now().hour + 12) % 24).strftime('%Y-%m-%d %H:%M:%S')}")
if __name__ == "__main__":
    main()
