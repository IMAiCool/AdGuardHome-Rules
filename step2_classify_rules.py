import os
import re

os.makedirs("./Classification", exist_ok=True)

# 判断是否是 IP 地址（v4 或简化 v6）
def is_ip(s):
    return re.match(r"^(127\.0\.0\.1|0\.0\.0\.0|::)$", s)

# 判断是否是 IP hosts 规则：IP + 非IP，第二项允许包含 localhost 或 broadcasthost
def is_hosts_rule(line):
    parts = line.strip().split()
    if len(parts) != 2:
        return False
    ip, host = parts
    # host 不能是 IP、本地保留名，必须是域名
    if is_ip(ip) and not re.match(r"^\d{1,3}(\.\d{1,3}){3}$", host) and host not in {"localhost", "broadcasthost","local","localhost.localdomain"}:
        return True
    return False

# 判断是否为标准 AdGuard 规则
def is_adguard_rule(line):
    line = line.strip()
    # 匹配标准结构，包括允许的后缀，禁止其他非法参数
    pattern = r"^(@@)?\|\|[\w\-\.\*]+(\^(\*|\||\$important)?)?$"
    return re.fullmatch(pattern, line) is not None

# 判断是否为纯域名规则（可含末尾 ^，但不能含 ||、$、/ 等）
def is_domain_rule(line):
    line = line.strip()
    if ' ' in line or '||' in line or '@@' in line or '$' in line or '/' in line:
        return False
    return re.match(r"^[a-zA-Z0-9\-\.]+(\^)?$", line) is not None

# 主函数
def classify_rules(input_file):
    hosts, adguard, domain, others = [], [], [], []

    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            raw = line.strip()
            if not raw:
                continue
            if is_hosts_rule(raw):
                hosts.append(raw)
            elif is_adguard_rule(raw):
                adguard.append(raw)
            elif is_domain_rule(raw):
                domain.append(raw)
            else:
                others.append(raw)

    # 写入文件
    with open("./Classification/hosts", "w", encoding="utf-8") as f:
        f.write("\n".join(hosts) + "\n")
    with open("./Classification/adguard-rules.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(adguard) + "\n")
    with open("./Classification/domain.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(domain) + "\n")
    with open("./Classification/others.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(others) + "\n")

    # 控制台输出
    print("处理完成")
    print("------------------------------------------------------------")
    print(f"纯hosts规则{len(hosts)}条,输出到./Classification/hosts")
    print(f"标准adguard规则{len(adguard)}条输出到./Classification/adguard-rules.txt")
    print(f"纯域名规则{len(domain)}条./Classification/domain.txt")
    print(f"其他规则{len(others)}条./Classification/others.txt")
    print("------------------------------------------------------------")


def main():
    """执行完整的广告规则分类流程"""
    classify_rules("./Merge-rule/merge_rules.txt")


if __name__ == "__main__":
    main()
