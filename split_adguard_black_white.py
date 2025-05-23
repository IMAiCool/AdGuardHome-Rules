import os

def classify_adguard_black_white(input_file):
    black_list = []
    white_list = []
    others = []

    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            rule = line.strip()
            if not rule:
                continue
            if rule.startswith('||'):
                black_list.append(rule)
            elif rule.startswith('@@'):
                white_list.append(rule)
            else:
                others.append(rule)

    return black_list, white_list, others

def write_lines(lines, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        for line in lines:
            f.write(line + '\n')

def main():
    input_file = './others/adguardrules.txt'

    black, white, others = classify_adguard_black_white(input_file)

    write_lines(black, './others/adguard-black.txt')
    write_lines(white, './others/adguard-white.txt')
    write_lines(others, './others/adguard-others.txt')

    print(f"分类完成: 黑名单 {len(black)} 条，白名单 {len(white)} 条，其他 {len(others)} 条")

if __name__ == '__main__':
    main()
