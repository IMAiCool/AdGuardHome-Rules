import os
import re

def strip_rules():
    os.makedirs('./stripping_rules', exist_ok=True)

    # hosts-black.txt剥离
    with open('./BAWLC/hosts_black.txt', 'r', encoding='utf-8') as fin, \
         open('./stripping_rules/hosts-bdomain.txt', 'w', encoding='utf-8') as fout:
        for line in fin:
            line = line.strip()
            # 去除IP部分，只保留域名
            parts = line.split()
            if len(parts) > 1:
                domain = parts[1]
                domain = domain.rstrip('^')
                fout.write(domain + '\n')

    # hosts-others.txt剥离
    with open('./BAWLC/hosts_others.txt', 'r', encoding='utf-8') as fin, \
         open('./stripping_rules/hosts-odomain.txt', 'w', encoding='utf-8') as fout:
        for line in fin:
            line = line.strip()
            parts = line.split()
            if len(parts) > 1:
                domain = parts[1]
                domain = domain.rstrip('^')
                fout.write(domain + '\n')

    # adguard-black.txt剥离
    with open('./BAWLC/adguard-black.txt', 'r', encoding='utf-8') as fin, \
         open('./stripping_rules/adguard-bdomain.txt', 'w', encoding='utf-8') as fout:
        for line in fin:
            domain = line.strip().lstrip('||')
            domain = re.sub(r'\^(\$important|\*|\|)?$', '', domain)
            fout.write(domain + '\n')

    # adguard-white.txt剥离
    with open('./BAWLC/adguard-white.txt', 'r', encoding='utf-8') as fin, \
         open('./stripping_rules/adguard-wdomain.txt', 'w', encoding='utf-8') as fout:
        for line in fin:
            domain = line.strip().lstrip('@@||')
            domain = re.sub(r'\^(\$important|\*|\|)?$', '', domain)
            fout.write(domain + '\n')

    # Classification/domain.txt剥离
    with open('./Classification/domain.txt', 'r', encoding='utf-8') as fin, \
         open('./stripping_rules/domain.txt', 'w', encoding='utf-8') as fout:
        for line in fin:
            domain = line.strip().rstrip('^')
            fout.write(domain + '\n')

    print("[strip_rules] 规则剥离完成")
