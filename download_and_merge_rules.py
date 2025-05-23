import os
import re
import requests

def is_ip_line(line):
    # 简单判断是否包含IP开头的规则，如 0.0.0.0 或 192.168.
    return bool(re.match(r'^\s*(0\.0\.0\.0|127\.0\.0\.1|192\.168\.\d+\.\d+)', line))

def read_urls_file(file_path):
    urls = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or ':' not in line:
                continue
            name, url = line.split(':', 1)
            urls.append((name.strip(), url.strip()))
    return urls

def download_rule(url):
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        print(f"下载失败: {url} 原因: {e}")
        return ""

def remove_header_and_comments(rule_text):
    lines = rule_text.splitlines()
    start_index = 0
    for i, line in enumerate(lines):
        line_strip = line.strip()
        # 找首次出现 @ 或 | 或 IP 开头的规则
        if (line_strip.startswith('@') or line_strip.startswith('|') or is_ip_line(line_strip)):
            start_index = i
            break
    # 从start_index开始过滤注释行
    filtered_lines = []
    for line in lines[start_index:]:
        line_strip = line.strip()
        # 注释规则一般是以 ! 或 # 开头的行
        if line_strip.startswith('!') or line_strip.startswith('#') or not line_strip:
            continue
        filtered_lines.append(line_strip)
    return filtered_lines

def main():
    input_dir = './input'
    urls_file = os.path.join(input_dir, 'urls.txt')
    local_rules_file = os.path.join(input_dir, 'local-rules.txt')

    # 读取urls文件
    url_list = read_urls_file(urls_file)

    all_rules = set()

    # 下载并处理url规则
    for name, url in url_list:
        print(f"下载规则：{name}，地址：{url}")
        rule_text = download_rule(url)
        if not rule_text:
            continue
        filtered_lines = remove_header_and_comments(rule_text)
        all_rules.update(filtered_lines)

    # 读取本地规则
    if os.path.exists(local_rules_file):
        with open(local_rules_file, 'r', encoding='utf-8') as f:
            local_text = f.read()
        local_filtered_lines = remove_header_and_comments(local_text)
        all_rules.update(local_filtered_lines)

    print(f"合并去重后规则数量：{len(all_rules)}")

    # 输出到文件
    output_dir = './others'
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'merged-rules.txt')

    with open(output_file, 'w', encoding='utf-8') as f:
        for rule in sorted(all_rules):
            f.write(rule + '\n')

    print(f"合并规则写入文件：{output_file}")

if __name__ == '__main__':
    main()
