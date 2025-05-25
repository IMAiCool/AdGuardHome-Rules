import os

# 输入文件
black_files = [
    "./stripping_rules/hosts-bdomain.txt",
    "./stripping_rules/domain.txt",
    "./stripping_rules/adguard-bdomain.txt"
]

white_files = [
    "./stripping_rules/adguard-wbdomain.txt",
    "./stripping_rules/hosts-odomain.txt"
]

# 输出文件
black_output = "./ipombaw/BlackList_tmp.txt"
white_output = "./ipombaw/WhiteList_tmp.txt"
white_2d_output = "./Log/white_2d.log"

os.makedirs("./ipombaw", exist_ok=True)


def is_second_level_domain(domain):
    parts = domain.split('.')
    return len(parts) == 2 and all(parts)


def main():
    # 读取合并黑名单
    black_set = set()
    for filepath in black_files:
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        black_set.add(line)

    # 写黑名单
    with open(black_output, "w", encoding="utf-8") as f:
        for domain in sorted(black_set):
            f.write(domain + "\n")

    print("黑名单合并成功")
    print("------------------------------------------------------------")
    print(f"{black_output} 规则数量{len(black_set)}条")
    print("------------------------------------------------------------")

    # 读取合并白名单
    white_set = set()
    for filepath in white_files:
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        white_set.add(line)

    # 判断是否一级域名.顶级域名
    white_2d = []
    white_other = []

    for domain in white_set:
        if is_second_level_domain(domain):
            white_2d.append(domain)
        else:
            white_other.append(domain)

    # 写白名单
    with open(white_output, "w", encoding="utf-8") as f:
        for domain in sorted(white_other):
            f.write(domain + "\n")

    with open(white_2d_output, "w", encoding="utf-8") as f:
        for domain in sorted(white_2d):
            f.write(domain + "\n")

    print("白名单初步处理完成")
    print("------------------------------------------------------------")
    print(f"{white_output} 规则数量{len(white_other)}条")
    print("------------------------------------------------------------")


if __name__ == "__main__":
    main()