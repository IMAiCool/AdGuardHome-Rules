import os
import sys
import re

# 添加工作目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入各个功能模块
import download_and_merge_rules
import detect_black_white_conflicts
import handle_hierarchy_conflicts
import deduplicate_and_format
import validate_and_clean_hosts_adguard
import split_adguard_black_white
import merge_black_domains
import extract_domains_from_rules
import classify_rules

def main():
    """执行完整的广告规则处理流程"""
    try:
        print("1. 开始下载并合并规则...")
        download_and_merge_rules.main()
        
        print("\n2. 规则分类...")
        classify_rules.main()
        
        print("\n3. 验证和清理主机规则...")
        validate_and_clean_hosts_adguard.main()
        
        print("\n4. 拆分黑白名单...")
        split_adguard_black_white.main()
        
        print("\n5. 从规则中提取域名...")
        extract_domains_from_rules.main()
        
        print("\n6. 合并黑名单域名...")
        merge_black_domains.main()
        
        print("\n7. 检测黑白名单冲突...")
        detect_black_white_conflicts.main()
        
        print("\n8. 处理层级冲突...")
        handle_hierarchy_conflicts.main()
        
        print("\n9. 去重和格式化...")
        deduplicate_and_format.main()
        
        print("\n所有处理步骤已完成")
        
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()