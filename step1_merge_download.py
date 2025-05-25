import os
import re
import requests

# 创建输出目录
os.makedirs("./Merge-rule", exist_ok=True)

# 读取本地规则
def read_local_rules(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return f.readlines()

# 读取上游规则链接
def read_urls_config(filepath):
    urls = {}
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or ":" not in line:
                continue
            name, url = line.split(":", 1)
            urls[name.strip()] = url.strip()
    return urls

# 下载规则
def download_rule(name, url):
    print(f"正在下载{name}规则")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        lines = response.text.splitlines()
        print(f"下载成功,规则数量: {len(lines)}条")
        return lines
    except Exception:
        print("下载失败")
        return []

# 判断是否为有效规则
def is_valid_rule(line):
    line = line.strip()
    if not line:
        return False

    # 合法开头匹配
    if not (
        line.startswith("@@") or
        line.startswith("||") or
        line.startswith("127.0.0.1") or
        line.startswith("0.0.0.0") or
        line.startswith("::") or
        re.match(r"^[a-zA-Z0-9]", line) or
        line.startswith(".") or
        line.startswith("-")
    ):
        return False

    # 包含非法字符
    if re.search(r"[\/\\\[\]\?\~]", line):
        return False

    # 检查 # 前是字母或数字
    hash_index = line.find("#")
    if hash_index > 0 and line[hash_index - 1].isalnum():
        return False

    return True

# 主程序
def main():
    print("处理过程如下")
    print("------------------------------------------------------------")

    all_rules = []

    # 本地规则
    local_rules = read_local_rules("./input/local-rules.txt")
    all_rules.extend(local_rules)

    # 下载上游规则
    urls = read_urls_config("./input/urls.conf")
    for name, url in urls.items():
        rules = download_rule(name, url)
        all_rules.extend(rules)

    print("------------------------------------------------------------")
    print("正在筛选有效条目")

    valid_rules = []
    invalid_rules = []

    for line in all_rules:
        if is_valid_rule(line):
            valid_rules.append(line.strip())
        else:
            invalid_rules.append(line.strip())

    # 输出无效规则
    with open("./Merge-rule/merge_others.txt", "w", encoding="utf-8") as f:
        for line in invalid_rules:
            f.write(line + "\n")

    # 输出有效规则
    with open("./Merge-rule/merge_rules.txt", "w", encoding="utf-8") as f:
        for line in valid_rules:
            f.write(line + "\n")

    print(f"去除无效条目{len(invalid_rules)}条,输出到./Merge-rule/merge_others.txt")
    print(f"最终结果输出到了./Merge-rule/merge_rules.txt {len(valid_rules)}条规则")

if __name__ == "__main__":
    main()
