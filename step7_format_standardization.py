import re
from datetime import datetime

def is_ip_line(line):
    # 纯IP地址行（IPv4 或 IPv6简化判断）
    ipv4_pattern = r"^\d{1,3}(\.\d{1,3}){3}$"
    ipv6_pattern = r"^([0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}$"
    return re.match(ipv4_pattern, line) or re.match(ipv6_pattern, line)

def load_and_clean(file_path, remove_localhost=False, remove_ip=False):
    cleaned = []
    with open(file_path, encoding='utf-8') as f:
        for line in f:
            l = line.strip()
            if not l:
                continue
            # 新增：清理以.结尾的行
            if l.endswith('.'):
                l = l.rstrip('.')
            if remove_localhost and 'localhost' in l:
                continue
            if remove_ip and is_ip_line(l):
                continue
            cleaned.append(l)
    return cleaned

def write_with_header(file_path, rules, rule_name):
    now = datetime.now()
    now_str = f"{now.year}年{now.month}月{now.day}日 {now.hour:02}:{now.minute:02}:{now.second:02}"
    header = [
        f"! 规则更新时间 {now_str}",
        f"! 本规则数量 {len(rules)}条",
        "! 更新频率 12小时",
        f"! 规则名称 {rule_name}",
        ""
    ]
    with open(file_path, 'w', encoding='utf-8') as f:
        for line in header:
            f.write(line + "\n")
        for rule in rules:
            f.write(rule + "\n")

def normalize_blacklist(lines):
    # example.com -> ||example.com^
    normalized = []
    invalid_log = "./Log/others.log"
    
    with open(invalid_log, "a", encoding='utf-8') as log_f:
        for line in lines:
            if not line:
                continue
            # 新增：检测.js结尾的无效条目
            if line.lower().endswith('.js'):
                log_f.write(f"{line} #该条目为.js结尾的无效条目\n")
                continue
            # 新增：检测非字母结尾条目
            if line and not line[-1].isalpha():
                log_f.write(f"{line} #该条目为非字母结尾的无效条目\n")
                continue
            # 转换
            domain = line.strip()
            domain = domain.rstrip('^')
            normalized.append(f"||{domain}^")
    return normalized

def normalize_whitelist(lines):
    # example.com -> @@||example.com^
    normalized = []
    invalid_log = "./Log/others.log"
    
    with open(invalid_log, "a", encoding='utf-8') as log_f:
        for line in lines:
            if not line:
                continue
            # 新增：检测.js结尾的无效条目
            if line.lower().endswith('.js'):
                log_f.write(f"{line} #该条目为.js结尾的无效条目\n")
                continue
            # 新增：检测非字母结尾条目
            if line and not line[-1].isalpha():
                log_f.write(f"{line} #该条目为非字母结尾的无效条目\n")
                continue
            domain = line.strip()
            domain = domain.rstrip('^')
            normalized.append(f"@@||{domain}^")
    return normalized


def main():
    # 路径定义
    ad_black_path = "./output/AdBlackList.txt"
    ad_white_path = "./output/AdWhiteList.txt"

    out_black = "./output/AdGuardHomeBlack.txt"
    out_white = "./output/AdGuardHomeWhite.txt"

    # 1. 加载并清理AdBlackList：去掉含localhost 和纯IP行
    black_rules = load_and_clean(ad_black_path, remove_localhost=True, remove_ip=True)

    # 2. 加载并清理AdWhiteList：去掉纯IP行
    white_rules = load_and_clean(ad_white_path, remove_localhost=False, remove_ip=True)

    # 3. 格式标准化
    black_normalized = normalize_blacklist(black_rules)
    white_normalized = normalize_whitelist(white_rules)

    # 4. 写入文件并添加头部信息
    write_with_header(out_black, black_normalized, "AdBlackList")
    write_with_header(out_white, white_normalized, "AdWhiteList")

    # 输出控制台信息
    print("格式标准化完成")
    print("------------------------------------------------------------")
    print(f"{out_black} 规则数量{len(black_normalized)}条")
    print(f"{out_white} 规则数量{len(white_normalized)}条")
    print("------------------------------------------------------------")


if __name__ == "__main__":
    main()
