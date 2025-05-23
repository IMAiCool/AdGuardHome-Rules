import os

def merge_files_unique(file1, file2, output_file):
    domains = set()

    for filepath in [file1, file2]:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                domain = line.strip()
                if domain:
                    domains.add(domain)

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        for domain in sorted(domains):
            f.write(domain + '\n')

def main():
    file1 = './others/hostsd'
    file2 = './others/adguard-blackd.txt'
    output_file = './others/black.txt'

    merge_files_unique(file1, file2, output_file)
    print(f"合并完成，输出文件: {output_file}, 共 {len(open(output_file).readlines())} 条域名")

if __name__ == '__main__':
    main()
