import os
import re
from datetime import datetime

def standardize_format():
    os.makedirs('./Log', exist_ok=True)
    os.makedirs('./output', exist_ok=True)

    def check_others(file_path, log_path):
        others = []
        filtered = []
        with open(file_path, 'r', encoding='utf-8') as fin:
            for line in fin:
                line = line.strip()
                if not line:
                    continue
                # 以非字母结尾 或 以.js结尾 或 包含 local host
                if re.search(r'[^a-zA-Z0-9]$', line) or line.endswith('.js') or 'local' in line or 'host' in line:
                    others.append(line)
                else:
                    filtered.append(line)
        with open(log_path, 'w', encoding='utf-8') as flog:
            for l in others:
                flog.write(l + '\n')
        return filtered

    white_filtered = check_others('./output/AdWhiteList.txt', './Log/others.txt')
    black_filtered = check_others('./output/AdBlackList.txt', './Log/others.txt')

    def format_white(lines):
        res = []
        for line in lines:
            domain = line
            if domain.startswith('@@||'):
                res.append(domain)
            else:
                domain = domain.lstrip('@@||').rstrip('^$*|important')
                res.append(f'@@||{domain}^')
        return res

    def format_black(lines):
        res = []
        for line in lines:
            domain = line
            if domain.startswith('||'):
                res.append(domain)
            else:
                domain = domain.lstrip('||').rstrip('^$*|important')
                res.append(f'||{domain}^')
        return res

    white_final = format_white(white_filtered)
    black_final = format_black(black_filtered)

    def write_with_header(file_path, lines, rule_name):
        now = datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')
        header = [
            f'! 规则更新时间 {now}',
            f'! 本规则数量 {len(lines)}条',
            f'! 更新频率 12小时',
            f'! 规则名称 {rule_name}',
            ''
        ]
        with open(file_path, 'w', encoding='utf-8') as f:
            for h in header:
                f.write(h + '\n')
            for line in lines:
                f.write(line + '\n')

    write_with_header('./output/AdGuardHomeWhite.txt', white_final, 'AdWhiteList')
    write_with_header('./output/AdGuardHomeBlack.txt', black_final, 'AdBlackList')

    print("[standardize_format] 格式标准化完成")
