import os
import re
import requests
from datetime import datetime

# 配置
LOCAL_RULE_FILE = "local_rules.txt"
URLS_FILE = "urls.txt"
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def read_local_rules():
    if not os.path.exists(LOCAL_RULE_FILE):
        return []
    with open(LOCAL_RULE_FILE, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('!')]

def fetch_upstream_rules():
    if not os.path.exists(URLS_FILE):
        return [], []
    all_rules = []
    urls = []
    with open(URLS_FILE, 'r', encoding='utf-8') as f:
        for url in f:
            url = url.strip()
            if not url or url.startswith("#"):
                continue
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    rules = [line.strip() for line in response.text.splitlines() if line.strip() and not line.startswith('!')]
                    all_rules.extend(rules)
                    urls.append(url)
            except Exception as e:
                print(f"Failed to fetch {url}: {e}")
    return all_rules, urls

def is_css_rule(rule):
    return bool(re.search(r'[^:]#|\=|\/|\\|\?|\(|\)', rule))  # 仅#在首位不算

def extract_domain(rule):
    rule = re.sub(r'^\|\|', '', rule)
    rule = rule.split('/')[0]
    rule = rule.split('^')[0]
    return rule.strip()

def classify_rules(rules):
    blacklist, whitelist, blacklist_css, whitelist_css = set(), set(), set(), set()
    for rule in rules:
        if rule.startswith('@@'):
            domain = extract_domain(rule[2:])
            if is_css_rule(rule):
                whitelist_css.add(domain)
            else:
                whitelist.add(domain)
        else:
            domain = extract_domain(rule)
            if is_css_rule(rule):
                blacklist_css.add(domain)
            else:
                blacklist.add(domain)
    return blacklist, whitelist, blacklist_css, whitelist_css

def cleanup_conflicts(blacklist, whitelist):
    whitelist_cleaned = {w for w in whitelist if not any(w == b or w.endswith('.' + b) for b in blacklist)}
    blacklist_cleaned = blacklist - whitelist
    return blacklist_cleaned, whitelist_cleaned

def format_adguard(rules):
    return sorted([f"||{domain}^$important" for domain in rules])

def write_output(filename, rules, meta=None):
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, 'w', encoding='utf-8') as f:
        if meta:
            for line in meta:
                f.write(f"! {line}\n")
        for rule in sorted(rules):
            f.write(f"{rule}\n")

def main():
    local_rules = read_local_rules()
    upstream_rules, upstream_urls = fetch_upstream_rules()

    all_rules = upstream_rules + local_rules
    all_rules_unique = sorted(set(all_rules))
    all_rules_clean = [r for r in all_rules_unique if not is_css_rule(r)]
    css_rules = [r for r in all_rules_unique if is_css_rule(r)]

    # 生成 all_rules.txt
    write_output("all_rules.txt", all_rules_unique)

    # 黑白名单分类
    blacklist, whitelist, blacklist_css, whitelist_css = classify_rules(all_rules_clean)
    b_css, w_css, *_ = classify_rules(css_rules)
    blacklist_css |= b_css
    whitelist_css |= w_css

    # 处理冲突
    blacklist, whitelist = cleanup_conflicts(blacklist, whitelist)

    # 输出规则
    meta = [
        f"来源：{', '.join(upstream_urls)}",
        f"本地规则数：{len(local_rules)}",
        f"总规则数：{len(all_rules_unique)}",
        f"更新时间：{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC",
        f"更新频率：每12小时"
    ]
    write_output("blacklist.txt", format_adguard(blacklist), meta)
    write_output("whitelist.txt", format_adguard(whitelist), meta)
    write_output("blacklist_css.txt", sorted(blacklist_css))
    write_output("whitelist_css.txt", sorted(whitelist_css))

if __name__ == "__main__":
    main()
