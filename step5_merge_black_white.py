import os
import re

# 创建输出目录
os.makedirs('./ipombaw', exist_ok=True)

# ========== 黑名单合并去重 ==========
blacklist_set = set()

def load_domains_to_set(filepath, domain_set):
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            domain = line.strip()
            if domain:
                domain_set.add(domain)

def process_blacklist():
    """处理黑名单合并去重"""
    load_domains_to_set('./stripping_rules/hosts-domain.txt', blacklist_set)
    load_domains_to_set('./stripping_rules/adguard-bdomain.txt', blacklist_set)

    blacklist_output = './ipombaw/BlackList_tmp.txt'
    with open(blacklist_output, 'w', encoding='utf-8') as f:
        for domain in sorted(blacklist_set):
            f.write(domain + '\n')

    print("黑名单合并成功")
    print("------------------------------------------------------------")
    print(f"{blacklist_output} 规则数量{len(blacklist_set)}条")
    print("------------------------------------------------------------")

# ========== 白名单处理 ==========
white_input = './stripping_rules/adguard-wbdomain.txt'
white_2d_output = './ipombaw/white_2d.txt'
white_tmp_output = './ipombaw/WhiteList_tmp.txt'

white_2d_count = 0
white_tmp_count = 0

def process_whitelist():
    """处理白名单分类"""
    global white_2d_count, white_tmp_count
    
    with open(white_input, 'r', encoding='utf-8') as fin, \
         open(white_2d_output, 'w', encoding='utf-8') as f2d, \
         open(white_tmp_output, 'w', encoding='utf-8') as ftmp:

        for line in fin:
            domain = line.strip()
            if not domain:
                continue

            # 判断是否为一级域名，仅一个点且格式为 xxx.tld
            if re.fullmatch(r'[a-zA-Z0-9-]+\.[a-zA-Z]+', domain):
                f2d.write(domain + '\n')
                white_2d_count += 1
            else:
                ftmp.write(domain + '\n')
                white_tmp_count += 1

    print("白名单初步处理完成")
    print("------------------------------------------------------------")
    print(f"./ipombaw/WhiteList_tmp.txt 规则数量{white_tmp_count}条")
    print("------------------------------------------------------------")

def main():
    """提供统一入口函数"""
    process_blacklist()
    process_whitelist()