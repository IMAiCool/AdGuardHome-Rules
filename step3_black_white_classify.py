import os
import re

# 路径设置
hosts_path = "./Classification/hosts"
adguard_path = "./Classification/adguard-rules.txt"
output_dir = "./BAWLC"

os.makedirs(output_dir, exist_ok=True)

# 分类 hosts 黑白名单
def classify_hosts():
    black_ips = {"127.0.0.1", "0.0.0.0", "::"}
    black = []
    others = []

    with open(hosts_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) == 2 and parts[0] in black_ips:
                black.append(line)
            else:
                others.append(line)

    with open(f"{output_dir}/hosts_black.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(black))
    with open(f"{output_dir}/hosts_others.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(others))

    return len(black), len(others)

# 分类 adguard 黑白名单
def classify_adguard():
    black = []
    white = []

    with open(adguard_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("@@"):
                white.append(line)
            elif line.startswith("||"):
                black.append(line)

    with open(f"{output_dir}/adguard-black.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(black))
    with open(f"{output_dir}/adguard-white.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(white))

    return len(black), len(white)

def main():
    # 执行分类
    hosts_black_count, hosts_others_count = classify_hosts()
    ad_black_count, ad_white_count = classify_adguard()

    # 控制台输出
    print("黑白名单分类完成")
    print("------------------------------------------------------------")
    print(f"./BAWLC/hosts_black.txt 规则数量{hosts_black_count}条")
    print(f"./BAWLC/hosts_others.txt 规则数量{hosts_others_count}条")
    print(f"./BAWLC/adguard-black.txt 规则数量{ad_black_count}条")
    print(f"./BAWLC/adguard-white.txt 规则数量{ad_white_count}条")
    print("------------------------------------------------------------")

if __name__ == "__main__":
    main()
