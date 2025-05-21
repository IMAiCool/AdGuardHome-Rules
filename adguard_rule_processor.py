import os
import re
import requests
from datetime import datetime

# 创建输出目录
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 文件路径，改为output目录下
LOCAL_RULES_FILE = "local_rules.txt"
URLS_FILE = "urls.txt"
ALL_RULES_FILE = os.path.join(OUTPUT_DIR, "all_rules.txt")
BLACKLIST_FILE = os.path.join(OUTPUT_DIR, "blacklist.txt")
WHITELIST_FILE = os.path.join(OUTPUT_DIR, "whitelist.txt")
BLACKLIST_CSS_FILE = os.path.join(OUTPUT_DIR, "blacklist_css.txt")
WHITELIST_CSS_FILE = os.path.join(OUTPUT_DIR, "whitelist_css.txt")

# 特殊字符匹配
SPECIAL_CHAR_PATTERN = re.compile(r"(?<!^#).*[/=\\#\?\(\)]")
# 域名提取
DOMAIN_PATTERN = re.compile(r"^(?:@@)?(?:\|\|)?([a-zA-Z0-9\-_.]+)")

def read_local_rules():
    if not os.path.exists(LOCAL_RULES_FILE):
        return [], []
    with open(LOCAL_RULES_FILE, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    blacklist = [line for line in lines if not line.startswith("@@")]
    whitelist = [line for line in lines if line.startswith("@@")]
    return blacklist, whitelist

def read_urls():
    if not os.path.exists(URLS_FILE):
        return []
    with open(URLS_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def download_rules(urls):
    contents = []
    for url in urls:
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            lines = [line.strip() for line in resp.text.splitlines() if line.strip()]
            contents.extend(lines)
        except Exception as e:
            print(f"❌ 无法下载 {url}：{e}")
    return contents

def split_special_rules(rules):
    clean, special_bl, special_wl = [], [], []
    for rule in rules:
        if SPECIAL_CHAR_PATTERN.search(rule):
            (special_wl if rule.startswith("@@") else special_bl).append(rule)
        else:
            clean.append(rule)
    return clean, special_bl, special_wl

def extract_domain(rule):
    match = DOMAIN_PATTERN.match(rule)
    return match.group(1).lstrip('.') if match else None

def normalize_rules(rules):
    return list({extract_domain(r) for r in rules if extract_domain(r)})

def remove_conflicts(blacklist, whitelist):
    bl_set, wl_set = set(blacklist), set(whitelist)
    bl_set -= (conflict := bl_set & wl_set)

    def is_subdomain(sub, dom):
        return sub != dom and sub.endswith("." + dom)

    cleaned_wl = set()
    for w in wl_set:
        if not any(is_subdomain(w, b) for b in bl_set):
            cleaned_wl.add(w)

    return sorted(bl_set), sorted(cleaned_wl)

def format_adguard_rules(domains, is_whitelist=False):
    prefix = "@@||" if is_whitelist else "||"
    # 不再添加 $important
    return [f"{prefix}{d}^" for d in domains]

def write_file_with_header(path, rules, urls, local_count, desc):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header = [
        f"! 来源: {', '.join(urls) if urls else '无'}",
        f"! {desc}条目数量: {len(rules)}",
        f"! 来自本地规则条目数量: {local_count}",
        f"! 更新时间: {now}",
        f"! 更新频率: 每12小时",
        ""
    ]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(header + rules))

def main():
    # 读取本地规则和上游URL
    local_bl, local_wl = read_local_rules()
    urls = read_urls()
    upstream = download_rules(urls)

    # 输出全部上游规则（不去重）
    with open(ALL_RULES_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(upstream))

    # 剔除特殊字符规则
    cleaned, special_bl, special_wl = split_special_rules(upstream)
    with open(BLACKLIST_CSS_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(special_bl))
    with open(WHITELIST_CSS_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(special_wl))

    # 黑白名单初步划分
    upstream_bl = [r for r in cleaned if not r.startswith("@@")]
    upstream_wl = [r for r in cleaned if r.startswith("@@")]

    # 合并本地规则（排除重复）
    all_existing = set(upstream_bl + upstream_wl + special_bl + special_wl)
    upstream_bl += [r for r in local_bl if r not in all_existing]
    upstream_wl += [r for r in local_wl if r not in all_existing]

    # 提取域名 + 去重
    bl_domains = normalize_rules(upstream_bl)
    wl_domains = normalize_rules(upstream_wl)

    # 冲突处理
    bl_domains, wl_domains = remove_conflicts(bl_domains, wl_domains)

    # AdGuard格式化
    bl_formatted = format_adguard_rules(bl_domains)
    wl_formatted = format_adguard_rules(wl_domains, is_whitelist=True)

    # 写入结果
    write_file_with_header(BLACKLIST_FILE, bl_formatted, urls, len(local_bl), "黑名单")
    write_file_with_header(WHITELIST_FILE, wl_formatted, urls, len(local_wl), "白名单")

    # 控制台输出统计信息
    print("\n✅ 规则处理完成")
    print(f"📥 上游规则总条数（含注释/特殊）：{len(upstream)}")
    print(f"📄 本地黑名单规则数：{len(local_bl)}")
    print(f"📄 本地白名单规则数：{len(local_wl)}")
    print(f"🚫 含特殊字符规则（blacklist_css.txt）：{len(special_bl)}")
    print(f"🚫 含特殊字符规则（whitelist_css.txt）：{len(special_wl)}")
    print(f"✅ 最终黑名单规则数（blacklist.txt）：{len(bl_formatted)}")
    print(f"✅ 最终白名单规则数（whitelist.txt）：{len(wl_formatted)}")
    print(f"📂 所有合并规则保存在：{ALL_RULES_FILE}")

if __name__ == "__main__":
    main()
