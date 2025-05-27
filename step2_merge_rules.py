import os

def merge_dedup(input_files, output_file):
    seen = set()
    with open(output_file, 'w', encoding='utf-8') as fw:
        for file in input_files:
            if not os.path.exists(file):
                continue
            with open(file, 'r', encoding='utf-8') as fr:
                for line in fr:
                    line = line.strip()
                    if line and line not in seen:
                        fw.write(line + '\n')
                        seen.add(line)
    print("[merge] 合并去重完成")
