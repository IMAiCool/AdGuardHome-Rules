import os

def deduplicate_file(input_path, output_path):
    seen = set()
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]

    unique_lines = []
    for line in lines:
        if line not in seen:
            seen.add(line)
            unique_lines.append(line)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        for line in unique_lines:
            f.write(line + '\n')

def is_second_level_domain(domain):
    # 判断是否二级域名（如 example.com，10010.cn）
    # 简单规则：点分段长度等于2，即只含1个点
    return domain.count('.') == 1

def process_white_list_filter(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        domains = [line.strip() for line in f if line.strip()]

    # 删除二级域名
    filtered = [d for d in domains if not is_second_level_domain(d)]

    # 格式化为 @@||example.com^
    formatted = [f"@@||{d}^" for d in filtered]

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        for line in formatted:
            f.write(line + '\n')

def process_black_list_format(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        domains = [line.strip() for line in f if line.strip()]

    # 格式化为 ||example.com^
    formatted = [f"||{d}^" for d in domains]

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        for line in formatted:
            f.write(line + '\n')

def main():
    black_in = './others/AdBlcakList.txt'
    white_in = './others/AdWhitelist.txt'

    black_dedup = './output/black_list.txt'
    white_dedup = './output/white_list.txt'

    # 先去重
    deduplicate_file(black_in, black_dedup)
    deduplicate_file(white_in, white_dedup)

    # 黑名单格式化覆盖输出（black_list.txt）
    process_black_list_format(black_dedup, black_dedup)

    # 白名单过滤二级域名 + 格式化，覆盖输出（white_list.txt）
    process_white_list_filter(white_dedup, white_dedup)

    print("去重及格式化完成，输出文件:")
    print(f"黑名单: {black_dedup}")
    print(f"白名单: {white_dedup}")

if __name__ == '__main__':
    main()
