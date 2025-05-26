import os
import re
import urllib.request
from datetime import datetime

# ---------- 配置 ----------
INPUT_LOCAL_RULES = "./input/local-rules.txt"
INPUT_URLS_CONF = "./input/urls.conf"

DIR_MERGE_RULE = "./Merge-rule"
DIR_CLASSIFY = "./Classification"
DIR_BAWLC = "./BAWLC"
DIR_STRIPPING = "./stripping_rules"
DIR_IPOMBAW = "./ipombaw"
DIR_TMP = "./TMP"
DIR_LOG = "./Log"
DIR_OUTPUT = "./output"

# ---------- 辅助函数 ----------

def ensure_dirs():
    for d in [DIR_MERGE_RULE, DIR_CLASSIFY, DIR_BAWLC, DIR_STRIPPING,
              DIR_IPOMBAW, DIR_TMP, DIR_LOG, DIR_OUTPUT]:
        os.makedirs(d, exist_ok=True)

def read_file_lines(filepath):
    if not os.path.isfile(filepath):
        return []
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        return [line.strip() for line in f if line.strip()]

def write_file_lines(filepath, lines):
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

def log_write(filepath, lines):
    with open(filepath, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")

def is_valid_entry(line):
    # 有效条件
    if not line:
        return False
    line = line.strip()
    valid_starts = ('@@', '||', '127.0.0.1', '0.0.0.0', '::')
    if line.startswith(valid_starts):
        # 额外检查特殊字符
        if re.search(r"[\/\\\[\]\?~]", line):
            return False
        # 检查#前一字符是否字母数字
        hash_pos = line.find('#')
        if hash_pos > 0 and re.match(r"[a-zA-Z0-9]", line[hash_pos-1]):
            return False
        return True
    # 以字母数字开头或.或者-开头的也允许
    if re.match(r"^[a-zA-Z0-9\.\-]", line):
        # 同样检查特殊字符和#
        if re.search(r"[\/\\\[\]\?~]", line):
            return False
        hash_pos = line.find('#')
        if hash_pos > 0 and re.match(r"[a-zA-Z0-9]", line[hash_pos-1]):
            return False
        return True
    return False

def download_url(url):
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            if resp.status == 200:
                data = resp.read().decode('utf-8', errors='ignore')
                return data.splitlines()
            else:
                return None
    except Exception as e:
        return None

def remove_comments_and_headers(lines):
    res = []
    removed_count = 0
    for l in lines:
        l_strip = l.strip()
        if not l_strip or l_strip.startswith('!') or l_strip.startswith('[') or l_strip.startswith('#'):
            removed_count += 1
            continue
        res.append(l_strip)
    return res, removed_count

# ---------- 1. 下载并过滤规则 ----------
def download_and_filter_rules():
    print("处理过程如下")
    print("------------------------------------------------------------")

    # 读取远程规则URLs
    urls = []
    url_names = []
    if os.path.isfile(INPUT_URLS_CONF):
        with open(INPUT_URLS_CONF, "r", encoding="utf-8") as f:
            for line in f:
                line=line.strip()
                if not line or ':' not in line:
                    continue
                name, url = line.split(':',1)
                name = name.strip()
                url = url.strip()
                if url:
                    url_names.append(name)
                    urls.append(url)

    all_rules = []
    total_downloaded = 0

    for i, url in enumerate(urls):
        name = url_names[i]
        print(f"正在下载{name}规则")
        lines = download_url(url)
        if lines is None:
            print("下载失败")
            print("------------------------------------------------------------")
            continue
        total_downloaded += len(lines)
        all_rules.extend(lines)
        print(f"下载成功,规则数量: {len(lines)}条")
        print("------------------------------------------------------------")

    # 读取本地规则
    local_rules = read_file_lines(INPUT_LOCAL_RULES)
    all_rules.extend(local_rules)

    # 去除头部注释信息
    all_rules, removed_head_count = remove_comments_and_headers(all_rules)

    # 分离有效和无效条目
    valid_rules = []
    invalid_rules = []
    for r in all_rules:
        if is_valid_entry(r):
            valid_rules.append(r)
        else:
            invalid_rules.append(r)

    # 输出
    write_file_lines(f"{DIR_MERGE_RULE}/merge_rules.txt", valid_rules)
    write_file_lines(f"{DIR_MERGE_RULE}/merge_others.txt", invalid_rules)

    print("正在去除头部信息和注释")
    print(f"去除条目{removed_head_count}条,输出到{DIR_MERGE_RULE}/merge_others.txt")
    print(f"最终结果输出到了{DIR_MERGE_RULE}/merge_rules.txt {len(valid_rules)}条规则")
    print("------------------------------------------------------------")

# ---------- 2. 规则分类 ----------
def classify_rules():
    lines = read_file_lines(f"{DIR_MERGE_RULE}/merge_rules.txt")

    hosts = []
    adguard = []
    domain = []
    others = []

    ip_pattern = re.compile(r"^(127\.0\.0\.1|0\.0\.0\.0|::)")
    ip_line_pattern = re.compile(r"^((?:\d{1,3}\.){3}\d{1,3})\s+([\w\.\-]+)$")

    # hosts 判断: IP 域名格式（但不含localhost broadcasthost）
    # adguard规则格式较复杂，简化判断含||和^等，允许*在||与^之间
    # 域名规则，允许带或不带结尾^

    def is_hosts(line):
        if ip_line_pattern.match(line):
            # 拒绝包含localhost或broadcasthost
            if "localhost" in line or "broadcasthost" in line:
                return False
            return True
        if ip_pattern.match(line):
            # 仅IP地址开头的规则且格式正确视为hosts
            return True
        return False

    def is_adguard(line):
        # 标准adguard规则，符合描述的格式
        # ||example.com ||example.com^ ||example.com^$important ||example.com^* 等
        # 允许@@开头的白名单规则
        line = line.strip()
        if line.startswith("@@"):
            line = line[2:]
        if line.startswith("||"):
            # 允许*存在于||与^之间，复杂规则暂不严格解析，简单判断
            # 允许后面带^和参数等
            return True
        if line.startswith("|") or "^" in line or "$" in line:
            return True
        return False

    def is_domain(line):
        # 纯域名，允许末尾^
        # 不能带空格、特殊符号
        line = line.strip()
        if ' ' in line or '/' in line or '\\' in line:
            return False
        # 只允许字母数字-和.及末尾^
        if re.match(r"^[a-zA-Z0-9\.\-]+\^?$", line):
            return True
        return False

    for l in lines:
        if is_hosts(l):
            hosts.append(l)
        elif is_adguard(l):
            adguard.append(l)
        elif is_domain(l):
            domain.append(l)
        else:
            others.append(l)

    write_file_lines(f"{DIR_CLASSIFY}/hosts", hosts)
    write_file_lines(f"{DIR_CLASSIFY}/adguard-rules.txt", adguard)
    write_file_lines(f"{DIR_CLASSIFY}/domain.txt", domain)
    write_file_lines(f"{DIR_CLASSIFY}/others.txt", others)

    print("处理完成")
    print("------------------------------------------------------------")
    print(f"纯hosts规则{len(hosts)}条,输出到{DIR_CLASSIFY}/hosts")
    print(f"标准adguard规则{len(adguard)}条输出到{DIR_CLASSIFY}/adguard-rules.txt")
    print(f"纯域名规则{len(domain)}条.{DIR_CLASSIFY}/domain.txt")
    print(f"其他规则{len(others)}条.{DIR_CLASSIFY}/others.txt")
    print("------------------------------------------------------------")

# ---------- 3. 黑白名单分类 ----------
def classify_black_white():
    hosts_lines = read_file_lines(f"{DIR_CLASSIFY}/hosts")
    adguard_lines = read_file_lines(f"{DIR_CLASSIFY}/adguard-rules.txt")

    hosts_black = []
    hosts_others = []
    for line in hosts_lines:
        if line.startswith(('0.0.0.0', '127.0.0.1', '::')):
            hosts_black.append(line)
        else:
            hosts_others.append(line)

    adguard_black = []
    adguard_white = []
    for line in adguard_lines:
        if line.startswith('||'):
            adguard_black.append(line)
        elif line.startswith('@@'):
            adguard_white.append(line)

    write_file_lines(f"{DIR_BAWLC}/hosts_black.txt", hosts_black)
    write_file_lines(f"{DIR_BAWLC}/hosts_others.txt", hosts_others)
    write_file_lines(f"{DIR_BAWLC}/adguard-black.txt", adguard_black)
    write_file_lines(f"{DIR_BAWLC}/adguard-white.txt", adguard_white)

    print("黑白名单分类完成")
    print("------------------------------------------------------------")
    print(f"{DIR_BAWLC}/hosts_black.txt 规则数量{len(hosts_black)}条")
    print(f"{DIR_BAWLC}/hosts_white.txt 规则数量{len(hosts_others)}条")
    print(f"{DIR_BAWLC}/adguard-black.txt 规则数量{len(adguard_black)}条")
    print(f"{DIR_BAWLC}/adguard-white.txt 规则数量{len(adguard_white)}条")
    print("------------------------------------------------------------")

# ---------- 4. 格式剥离 ----------
def stripping_rules():
    # 读取文件，剥离域名输出
    def strip_host_line(line):
        # IP 域名格式，返回域名部分
        parts = line.strip().split()
        if len(parts) >= 2:
            return parts[1]
        return ""

    def strip_adguard_line(line):
        # 去除开头的@@|| 或||，去除后面的^及参数
        # 如: @@||example.com^$important -> example.com
        # ||example.com^* -> example.com
        line = line.strip()
        if line.startswith('@@'):
            line = line[2:]
        if line.startswith('||'):
            line = line[2:]
        # 去除 ^ 及后面部分
        line = re.split(r"[\^\$\*\|]", line)[0]
        return line

    def strip_domain_line(line):
        # 纯域名，去除末尾^
        return line.rstrip('^').strip()

    hosts_black = read_file_lines(f"{DIR_BAWLC}/hosts_black.txt")
    hosts_others = read_file_lines(f"{DIR_BAWLC}/hosts_others.txt")
    adguard_black = read_file_lines(f"{DIR_BAWLC}/adguard-black.txt")
    adguard_white = read_file_lines(f"{DIR_BAWLC}/adguard-white.txt")
    domain_lines = read_file_lines(f"{DIR_CLASSIFY}/domain.txt")

    hosts_bdomain = [strip_host_line(l) for l in hosts_black if strip_host_line(l)]
    hosts_odomain = [strip_host_line(l) for l in hosts_others if strip_host_line(l)]
    adguard_bdomain = [strip_adguard_line(l) for l in adguard_black if strip_adguard_line(l)]
    adguard_wdomain = [strip_adguard_line(l) for l in adguard_white if strip_adguard_line(l)]
    domain_clean = [strip_domain_line(l) for l in domain_lines if strip_domain_line(l)]

    write_file_lines(f"{DIR_STRIPPING}/hosts-bdomain.txt", hosts_bdomain)
    write_file_lines(f"{DIR_STRIPPING}/hosts-odomain.txt", hosts_odomain)
    write_file_lines(f"{DIR_STRIPPING}/adguard-bdomain.txt", adguard_bdomain)
    write_file_lines(f"{DIR_STRIPPING}/adguard-wdomain.txt", adguard_wdomain)
    write_file_lines(f"{DIR_STRIPPING}/domain.txt", domain_clean)

    print("格式剥离完成")
    print("------------------------------------------------------------")
    print(f"{DIR_STRIPPING}/hosts-bdomain.txt 规则数量{len(hosts_bdomain)}条")
    print(f"{DIR_STRIPPING}/hosts-odomain.txt 规则数量{len(hosts_odomain)}条")
    print(f"{DIR_STRIPPING}/adguard-bdomain.txt 规则数量{len(adguard_bdomain)}条")
    print(f"{DIR_STRIPPING}/adguard-wdomain.txt 规则数量{len(adguard_wdomain)}条")
    print(f"{DIR_STRIPPING}/domain.txt 规则数量{len(domain_clean)}条")
    print("------------------------------------------------------------")

# ---------- 5. 黑白名单初步合并 ----------
def initial_merge_black_white():
    # 合并 hosts 和 adguard 中的黑白名单域名，去重输出到 ipombaw
    def merge_and_unique(files):
        merged = []
        for f in files:
            merged.extend(read_file_lines(f))
        return sorted(set(merged))

    black_merged = merge_and_unique([
        f"{DIR_STRIPPING}/adguard-bdomain.txt",
        f"{DIR_STRIPPING}/hosts-bdomain.txt",
        f"{DIR_STRIPPING}/domain.txt"
    ])
    white_merged = merge_and_unique([
        f"{DIR_STRIPPING}/adguard-wdomain.txt",
        f"{DIR_STRIPPING}/hosts-odomain.txt"
    ])

    write_file_lines(f"{DIR_IPOMBAW}/black.txt", black_merged)
    write_file_lines(f"{DIR_IPOMBAW}/white.txt", white_merged)

    print("黑白名单初步合并完成")
    print("------------------------------------------------------------")
    print(f"{DIR_IPOMBAW}/black.txt 规则数量{len(black_merged)}条")
    print(f"{DIR_IPOMBAW}/white.txt 规则数量{len(white_merged)}条")
    print("------------------------------------------------------------")

# ---------- 6. 冲突处理 ----------
def conflict_processing():
    # 第一阶段：黑白名单交叉冲突检查
    black = set(read_file_lines(f"{DIR_IPOMBAW}/black.txt"))
    white = set(read_file_lines(f"{DIR_IPOMBAW}/white.txt"))

    # 交叉冲突：同时存在于黑白名单
    overlap = black.intersection(white)

    conflict_log = []
    if overlap:
        conflict_log.append(f"【第一阶段黑白冲突共{len(overlap)}条】")
        for item in overlap:
            conflict_log.append(f"黑白名单冲突：{item}")
        # 冲突域名从白名单去除（保持黑名单优先）
        white = white - overlap

    # 第二阶段：同名单内上级域名冲突检测（白名单和黑名单分别处理）
    def detect_parent_child_conflict(domain_set):
        # 找出域名的父域存在于集合中冲突的域名
        conflict_pairs = []
        domain_list = sorted(domain_set)
        domain_set = set(domain_list)
        for d in domain_list:
            parts = d.split('.')
            # 检查父级域名是否存在于集合中
            for i in range(1, len(parts)):
                parent = ".".join(parts[i:])
                if parent != d and parent in domain_set:
                    conflict_pairs.append((d, parent))
                    break
        return conflict_pairs

    white_conflicts = detect_parent_child_conflict(white)
    black_conflicts = detect_parent_child_conflict(black)

    if white_conflicts:
        conflict_log.append(f"【第二阶段白名单层级冲突共{len(white_conflicts)}条】")
        for c, p in white_conflicts:
            conflict_log.append(f"白名单层级冲突：{c} 与 {p}")

    if black_conflicts:
        conflict_log.append(f"【第二阶段黑名单层级冲突共{len(black_conflicts)}条】")
        for c, p in black_conflicts:
            conflict_log.append(f"黑名单层级冲突：{c} 与 {p}")

    # 输出冲突日志
    log_write(f"{DIR_LOG}/conflict_log.txt", conflict_log)

    # 生成最终黑白名单，去除层级冲突的子域名（保留父域）
    def filter_conflict(domains, conflicts):
        # 移除冲突中的子域名，保留父域名
        remove_set = set(c for c, p in conflicts)
        return sorted(set(domains) - remove_set)

    white_final = filter_conflict(white, white_conflicts)
    black_final = filter_conflict(black, black_conflicts)

    write_file_lines(f"{DIR_OUTPUT}/AdWhiteList.txt", white_final)
    write_file_lines(f"{DIR_OUTPUT}/AdBlackList.txt", black_final)

    print("冲突处理完成")
    print("------------------------------------------------------------")
    print(f"./output/AdWhiteList.txt 规则数量{len(white_final)}条")
    print(f"./output/AdBlackList.txt 规则数量{len(black_final)}条")
    print("------------------------------------------------------------")

# ---------- 7. 格式标准化 ----------
def standardize_format():
    white_file = f"{DIR_OUTPUT}/AdWhiteList.txt"
    black_file = f"{DIR_OUTPUT}/AdBlackList.txt"
    log_others = []

    white_lines = read_file_lines(white_file)
    black_lines = read_file_lines(black_file)

    def is_illegal_entry(line):
        # 1. 以非字母结尾的条目
        if not line[-1].isalpha():
            return True
        # 2. 以.js结尾的条目
        if line.endswith(".js"):
            return True
        # 3. 含有字符串local host（不区分大小写）
        if re.search(r"local|host", line, re.I):
            return True
        return False

    white_filtered = []
    for line in white_lines:
        if is_illegal_entry(line):
            log_others.append(f"白名单异常条目: {line}")
        else:
            white_filtered.append(line)

    black_filtered = []
    for line in black_lines:
        if is_illegal_entry(line):
            log_others.append(f"黑名单异常条目: {line}")
        else:
            black_filtered.append(line)

    # 记录异常条目日志
    log_write(f"{DIR_LOG}/others.txt", log_others)

    # 标准化规则转换
    def white_to_adguard(line):
        # example.com -> @@||example.com^
        return f"@@||{line}^"

    def black_to_adguard(line):
        # example.com -> ||example.com^
        return f"||{line}^"

    white_adguard = [white_to_adguard(l) for l in white_filtered]
    black_adguard = [black_to_adguard(l) for l in black_filtered]

    now_str = datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")
    def header_info(name, count):
        return [
            f"! 规则更新时间 {now_str}",
            f"! 本规则数量 {count}条",
            f"! 更新频率 12小时",
            f"! 规则名称 {name}"
        ]

    white_header = header_info("AdWhiteList", len(white_adguard))
    black_header = header_info("AdBlackList", len(black_adguard))

    write_file_lines(f"{DIR_OUTPUT}/AdGuardHomeWhite.txt", white_header + white_adguard)
    write_file_lines(f"{DIR_OUTPUT}/AdGuardHomeBlack.txt", black_header + black_adguard)

    print("格式标准化完成")
    print("------------------------------------------------------------")
    print(f"./output/AdGuardHomeBlack.txt 规则数量{len(black_adguard)}条")
    print(f"./output/AdGuardHomeWhite.txt 规则数量{len(white_adguard)}条")
    print("------------------------------------------------------------")

    # 新增：删除 AdWhiteList.txt 中的一级域名（一级域名 + 顶级域名）
def remove_top_level_domains():
    white_file = f"{DIR_OUTPUT}/AdWhiteList.txt"
    lines = read_file_lines(white_file)

    def is_top_level_domain(domain):
        parts = domain.split('.')
        # 判断是否是一级域名（两个部分，例 example.com）
        return len(parts) == 2

    filtered = [line for line in lines if not is_top_level_domain(line)]

    write_file_lines(white_file, filtered)
    print(f"一级域名过滤完成，剩余规则数量{len(filtered)}条")

def remove_top_and_one_level_domains():
    white_file = f"{DIR_OUTPUT}/AdWhiteList.txt"
    lines = read_file_lines(white_file)

    def is_top_or_one_level_domain(domain):
        parts = domain.split('.')
        # 删除一段（顶级域名）或两段（一级域名）
        return len(parts) <= 2

    filtered = [line for line in lines if not is_top_or_one_level_domain(line)]

    write_file_lines(white_file, filtered)
    print(f"一级域名及顶级域名过滤完成，剩余规则数量{len(filtered)}条")

# ---------- 主流程 ----------
def main():
    ensure_dirs()
    download_and_filter_rules()
    classify_rules()
    classify_black_white()
    stripping_rules()
    initial_merge_black_white()
    conflict_processing()
    remove_top_level_domains() 
    standardize_format()

if __name__ == "__main__":
    main()
