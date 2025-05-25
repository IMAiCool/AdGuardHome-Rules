import os
import re
from datetime import datetime

# 输入输出路径
ad_black_path = './output/AdBlackList.txt'
ad_white_path = './output/AdWhiteList.txt'
adguard_black_path = './output/AdGuardHomeBlack.txt'
adguard_white_path = './output/AdGuardHomeWhite.txt'

# 确保输出目录存在
os.makedirs('./output', exist_ok=True)

def load_lines(path):
    with open(path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def save_lines(path, lines, header):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(header + '\n')
        for line in lines:
            f.write(line + '\n')

def is_ip(line):
    # 判断整行是否为纯IP (IPv4或IPv6)
    ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    ipv6_pattern = r'^([0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}$'
    return re.match(ipv4_pattern, line) or re.match(ipv6_pattern, line)

def process_blacklist(lines):
    # 去除含 localhost 相关条目，去除纯IP条目
    filtered = []
    for line in lines:
        if 'localhost' in line:
            continue
        if is_ip(line):
            continue
        filtered.append(line)
    # 标准化为 ||example.com^ 格式
    std_lines = []
    for line in filtered:
        # 提取域名部分，防止重复加 || 和 ^，一般line是域名或带注释，这里直接加
        domain = line
        if domain.startswith('||') and domain.endswith('^'):
            std_lines.append(domain)
        else:
            std_lines.append(f'||{domain}^')
    return std_lines

def process_whitelist(lines):
    # 去除纯IP条目
    filtered = [line for line in lines if not is_ip(line)]
    # 标准化为 @@||example.com^ 格式
    std_lines = []
    for line in filtered:
        domain = line
        if domain.startswith('@@||') and domain.endswith('^$important'):
            std_lines.append(domain)
        else:
            # 纯域名行转成@@||example.com^
            std_lines.append(f'@@||{domain}^$important')
    return std_lines

def main():
    """提供统一入口函数"""
    # 获取当前时间字符串
    now = datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')

    # 读取文件
    black_lines = load_lines(ad_black_path)
    white_lines = load_lines(ad_white_path)

    # 处理黑名单
    processed_black = process_blacklist(black_lines)
    # 处理白名单
    processed_white = process_whitelist(white_lines)

    # 生成头部信息
    header_black = (f"! 规则更新时间 {now}\n"
                    f"! 本规则数量 {len(processed_black)}条\n"
                    "! 更新频率 12小时\n"
                    "! 规则名称 AdBlackList")
    header_white = (f"! 规则更新时间 {now}\n"
                    f"! 本规则数量 {len(processed_white)}条\n"
                    "! 更新频率 12小时\n"
                    "! 规则名称 AdWhiteList")

    # 保存文件
    save_lines(adguard_black_path, processed_black, header_black)
    save_lines(adguard_white_path, processed_white, header_white)

    print("格式标准化完成")
    print("------------------------------------------------------------")
    print(f"./output/AdGuardHomeBlack.txt 规则数量{len(processed_black)}条")
    print(f"./output/AdGuardHomeWhite.txt 规则数量{len(processed_white)}条")
    print("------------------------------------------------------------")