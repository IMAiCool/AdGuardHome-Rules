import os
import re

# 输入文件路径
input_files = {
    "hosts_b": "./BAWLC/hosts_black.txt",
    "hosts_o": "./BAWLC/hosts_others.txt",
    "adguard_b": "./BAWLC/adguard-black.txt",
    "adguard_w": "./BAWLC/adguard-white.txt",
    "domain": "./Classification/domain.txt"
}

# 输出文件路径
output_dir = "./stripping_rules"
os.makedirs(output_dir, exist_ok=True)

output_files = {
    "hosts_b": f"{output_dir}/hosts-bdomain.txt",
    "hosts_o": f"{output_dir}/hosts-odomain.txt",
    "adguard_b": f"{output_dir}/adguard-bdomain.txt",
    "adguard_w": f"{output_dir}/adguard-wdomain.txt",
    "domain": f"{output_dir}/domain.txt"
}

# 剥离函数 - hosts格式 IP example => example
def strip_hosts(line):
    parts = line.strip().split()
    if len(parts) == 2:
        return parts[1]
    return None

# 剥离函数 - adguard格式
def strip_adguard(line):
    # 去掉开头的@@||或||，再剥离^及其后缀
    domain = re.sub(r"^(@@)?\|\|", "", line.strip())
    domain = re.split(r"\^", domain)[0]
    return domain if domain else None

# 剥离函数 - 纯域名，去除末尾^
def strip_domain(line):
    return line.strip().rstrip("^")


def main():
    counts = {}

    for key, input_path in input_files.items():
        process_func = processors[key]
        output_path = output_files[key]
        domains = []

        with open(input_path, "r", encoding="utf-8") as f:
            for line in f:
                result = process_func(line)
                if result:
                    domains.append(result)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(domains))

        counts[key] = len(domains)

    # 控制台输出
    print("域名剥离成功")
    print("------------------------------------------------------------")
    print(f"{output_files['hosts_b']} 规则数量{counts['hosts_b']}条")
    print(f"{output_files['hosts_o']} 规则数量{counts['hosts_o']}条")
    print(f"{output_files['adguard_b']} 规则数量{counts['adguard_b']}条")
    print(f"{output_files['adguard_w']} 规则数量{counts['adguard_w']}条")
    print(f"{output_files['domain']} 规则数量{counts['domain']}条")
    print("------------------------------------------------------------")


if __name__ == "__main__":
    main()

# 映射不同文件用不同剥离函数
processors = {
    "hosts_b": strip_hosts,
    "hosts_o": strip_hosts,
    "adguard_b": strip_adguard,
    "adguard_w": strip_adguard,
    "domain": strip_domain
}

