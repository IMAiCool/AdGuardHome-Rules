#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
import requests
import datetime
import threading
from pathlib import Path
from collections import defaultdict

# ===== 配置路径 =====
INPUT_DIR = Path("input")
OUTPUT_DIR = Path("output")
OTHERS_DIR = Path("others")
LOG_DIR = Path("Log")

# ===== 文件名定义 =====
LOCAL_RULE_FILE = INPUT_DIR / "local-rules.txt"
URLS_FILE = INPUT_DIR / "urls.txt"
ALL_LIST_FILE = OTHERS_DIR / "alllist.txt"
HOSTS_FILE = OTHERS_DIR / "hosts.txt"
ADGUARD_FILE = OTHERS_DIR / "adguard-rules.txt"
CSS_FILE = OTHERS_DIR / "all.css"

BLACKLIST_DOMAIN = OTHERS_DIR / "blacklist-domain.txt"
WHITELIST_DOMAIN = OTHERS_DIR / "whitelist-domain.txt"
HOSTS_DOMAIN = OTHERS_DIR / "hosts-domain.txt"

BLACKLIST_FILE = OUTPUT_DIR / "black_list.txt"
WHITELIST_FILE = OUTPUT_DIR / "white_list.txt"

LIST_IN_ALL_LOG = LOG_DIR / "list-in-all.log"
LIST_IN_BOTH_LOG = LOG_DIR / "list-in-both.log"
DELETE_HIERARCHY_LOG = LOG_DIR / "delete_Hierarchy.log"
DELETE_WHITE_LOG = LOG_DIR / "delete_white.log"
DELETE_RULES_LOG = LOG_DIR / "delete-rules.log"

# ===== 正则表达式 =====
HOSTS_RE = re.compile(r"^(?:0\.0\.0\.0|127\.0\.0\.1)\s+([\w.-]+)$")
ADGUARD_RE = re.compile(r"^(\@\@)?\|\|([\w.-]+)\^.*$")
SPECIAL_CHARS_RE = re.compile(r"[\\/\?\[\]]")

# ===== 函数定义 =====
def download_remote_rules():
    all_rules = []
    source_names = []
    if not URLS_FILE.exists():
        return [], []
    
    with open(URLS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if ":" not in line:
                continue
            name, url = line.strip().split(":", 1)
            try:
                resp = requests.get(url.strip(), timeout=15)
                if resp.status_code == 200:
                    lines = [l for l in resp.text.splitlines() if not l.startswith("!") and l.strip()]
                    all_rules.extend(lines)
                    source_names.append(name.strip())
            except:
                continue
    return all_rules, source_names

def read_local_rules():
    if LOCAL_RULE_FILE.exists():
        with open(LOCAL_RULE_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("!")]
    return []

def save_list(path, lines, header=None):
    with open(path, "w", encoding="utf-8") as f:
        if header:
            f.write(header + "\n")
        for line in lines:
            f.write(line + "\n")

def extract_domain(line):
    m = HOSTS_RE.match(line)
    if m:
        return m.group(1)
    m = ADGUARD_RE.match(line)
    if m:
        return m.group(2)
    return None

def format_adguard(domain, white=False):
    return f"@@||{domain}^" if white else f"||{domain}^"

def remove_hierarchy(domain_list):
    deleted = set()
    domains = set(domain_list)
    for domain in list(domains):
        parts = domain.split(".")
        for i in range(1, len(parts)):
            upper = ".".join(parts[i:])
            if upper in domains and domain in domains:
                deleted.add(upper)
                domains.discard(upper)
    return domains, deleted

def standardize_hosts(lines):
    return [f"127.0.0.1 {extract_domain(line)}" for line in lines if extract_domain(line)]

# ===== 主处理流程 =====
def main():
    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(OTHERS_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)

    local_rules = read_local_rules()
    remote_rules, source_names = download_remote_rules()
    all_rules = local_rules + remote_rules
    save_list(ALL_LIST_FILE, all_rules)

    # 分类
    hosts, adguard, css = [], [], []
    for line in all_rules:
        if HOSTS_RE.match(line):
            hosts.append(line)
        elif ADGUARD_RE.match(line) and not SPECIAL_CHARS_RE.search(line):
            adguard.append(line)
        else:
            css.append(line)

    hosts = list(set(standardize_hosts(hosts)))
    save_list(HOSTS_FILE, hosts)
    save_list(ADGUARD_FILE, adguard)
    save_list(CSS_FILE, css)

    # 黑白名单划分
    blacklist, whitelist = set(), set()
    for rule in adguard:
        m = ADGUARD_RE.match(rule)
        if not m: continue
        domain = m.group(2)
        if m.group(1):
            whitelist.add(domain)
        else:
            blacklist.add(domain)

    # 冲突处理
    host_domains = set([extract_domain(r) for r in hosts])
    list_in_all = whitelist & (host_domains | blacklist)
    list_in_both = host_domains & blacklist

    host_domains -= list_in_all | list_in_both
    blacklist -= list_in_all
    whitelist -= list_in_all
    
    # 层级冲突处理
    blacklist, deleted_hierarchy = remove_hierarchy(blacklist)
    whitelist, deleted_white = remove_hierarchy(whitelist)

    # 保存中间域名
    save_list(HOSTS_DOMAIN, sorted(host_domains))
    save_list(BLACKLIST_DOMAIN, sorted(blacklist))
    save_list(WHITELIST_DOMAIN, sorted(whitelist))

    # 最终规则输出
    final_black = sorted(set([format_adguard(d) for d in blacklist | host_domains]))
    final_white = sorted(set([format_adguard(d, white=True) for d in whitelist]))

    dup_black = len(final_black) - len(set(final_black))
    dup_white = len(final_white) - len(set(final_white))

    save_list(BLACKLIST_FILE, final_black)
    save_list(WHITELIST_FILE, final_white)
    save_list(DELETE_RULES_LOG, [f"重复黑名单: {dup_black} 条", f"重复白名单: {dup_white} 条"])

    save_list(LIST_IN_ALL_LOG, list(sorted(list_in_all)))
    save_list(LIST_IN_BOTH_LOG, list(sorted(list_in_both)))
    save_list(DELETE_HIERARCHY_LOG, list(sorted(deleted_hierarchy)))
    save_list(DELETE_WHITE_LOG, list(sorted(deleted_white)))

    now = datetime.datetime.now()
    next_update = now + datetime.timedelta(hours=12)

    print("[规则处理报告]", now.strftime("%Y-%m-%d %H:%M:%S"))
    print("-------------------------------------")
    print(f"■ 输入规则统计\n  ├─ 本地规则: {len(local_rules):,}条 ")
    print(f"  └─ 远程规则: {len(remote_rules):,}条（{len(source_names)}个源）")
    print(f"\n■ 分类处理结果")
    print(f"  ├─ 基础规则(alllist.txt): {len(all_rules):,}条")
    print(f"  ├─ CSS/正则规则(all.css): {len(css):,}条")
    print(f"  ├─ hosts规则初筛(hosts): {len(hosts):,}条")
    print(f"  └─ adguard规则初筛(adguard): {len(adguard):,}条")
    print(f"\n■ 冲突处理统计")
    print(f"  ├─ 直接冲突条目: {len(list_in_all):,}条（list-in-all.log）")
    print(f"  ├─ 黑名单冲突条目:{len(list_in_both):,}条(list-in-both.log)")
    print(f"  ├─ 黑白名单冲突条目:{len(deleted_white):,}条(delete_white.log)")
    print(f"  ├─ 去重条目:{dup_black + dup_white:,}条(delete-rules.log)")
    print(f"  └─ 层级冲突条目: {len(deleted_hierarchy):,}条（delete_Hierarchy.log）")
    print(f"\n■ 最终生效规则")
    print(f"  ├─ 黑名单生效: {len(final_black):,}条（output/black_list.txt）")
    print(f"  └─ 白名单生效: {len(final_white):,}条（output/white_list.txt）")
    print(f"\n下次更新: {next_update.strftime('%Y-%m-%d %H:%M:%S')}\n")

if __name__ == '__main__':
    main()
