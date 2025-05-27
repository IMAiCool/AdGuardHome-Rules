import re
import os

def classify_rules(input_file):
    os.makedirs('./Classification', exist_ok=True)
    domain_path = './Classification/domain.txt'
    others_path = './Classification/others.txt'

    # adguard规则正则
    adguard_re = re.compile(r'^(?:@@)?\|\|[\w\.-]+(\^(\$important|\|)?)?$')

    with open(input_file, 'r', encoding='utf-8') as fin, \
         open(domain_path, 'w', encoding='utf-8') as fdomain, \
         open(others_path, 'w', encoding='utf-8') as fothers:
        for line in fin:
            line = line.strip()
            if not line:
                continue
            if adguard_re.match(line):
                fdomain.write(line + '\n')
            else:
                fothers.write(line + '\n')
    print("[classify] 分类完成")
