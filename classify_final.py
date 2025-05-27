import os
import re

def classify_final():
    os.makedirs('./BAWLC', exist_ok=True)
    # 规则分别放入黑白名单文件和others文件夹

    # hosts文件分类
    hosts_path = './Classification/hosts.txt'
    if not os.path.exists(hosts_path):
        print("[classify_final] hosts.txt 不存在，跳过")
        return

    hosts_black_path = './BAWLC/hosts_black.txt'
    hosts_others_path = './BAWLC/hosts_others.txt'

    with open(hosts_path, 'r', encoding='utf-8') as fin, \
         open(hosts_black_path, 'w', encoding='utf-8') as fblack, \
         open(hosts_others_path, 'w', encoding='utf-8') as fothers:
        for line in fin:
            line = line.strip()
            if line.startswith(('0.0.0.0', '127.0.0.1', '::')):
                fblack.write(line + '\n')
            else:
                fothers.write(line + '\n')

    # adguard分类
    adguard_path = './Classification/domain.txt'
    adguard_black_path = './BAWLC/adguard-black.txt'
    adguard_white_path = './BAWLC/adguard-white.txt'

    with open(adguard_path, 'r', encoding='utf-8') as fin, \
         open(adguard_black_path, 'w', encoding='utf-8') as fblack, \
         open(adguard_white_path, 'w', encoding='utf-8') as fwhite:
        for line in fin:
            line = line.strip()
            if line.startswith('||'):
                fblack.write(line + '\n')
            elif line.startswith('@@'):
                fwhite.write(line + '\n')

    print("[classify_final] 黑白名单分类完成")
