import os
import sys
import re

# 添加工作目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入各个功能模块
import step1_merge_download
import step2_classify_rules
import step3_black_white_classify
import step4_strip_domains
import step5_merge_black_white
import step6_conflict_processing
import step7_format_standardization

def main():
    """执行完整的广告规则处理流程"""
    try:
        print("1. 开始下载并合并规则...")
        step1_merge_download.main()
        
        print("\n2. 规则分类...")
        step2_classify_rules.main()
        
        print("\n3. 拆分黑白名单...")
        step3_black_white_classify.main()
        
        print("\n4. 去除域名格式...")
        step4_strip_domains.main()
        
        print("\n5. 合并黑名单...")
        step5_merge_black_white.main()
        
        print("\n6. 处理冲突...")
        step6_conflict_processing.main()
        
        print("\n7. 格式标准化...")
        step7_format_standardization.main()
        
        print("\n所有处理步骤已完成")
        
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()