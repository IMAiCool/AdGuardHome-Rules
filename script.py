import os
from modules import download, merge, classify, classify_final, strip_rules, merge_bw_tmp, conflict_handler, standardize

def main():
    os.makedirs('./input', exist_ok=True)
    os.makedirs('./output', exist_ok=True)
    os.makedirs('./Log', exist_ok=True)

    download.download_upstream_rules()

    local_files = [f'./local/{fname}' for fname in os.listdir('./local') if fname.endswith('.txt')]
    merge.merge_dedup(local_files, './input/all_rules.txt')

    classify.classify_rules('./input/all_rules.txt')

    classify_final.classify_final()

    classify_bw.classify_black_white()

    strip_rules.strip_rules()

    merge_bw_tmp.merge_black_white_tmp()

    conflict_handler.detect_conflicts()

    standardize.standardize_format()

    print("全部步骤完成！")

if __name__ == "__main__":
    main()
