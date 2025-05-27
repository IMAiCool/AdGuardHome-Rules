import subprocess
import sys

def run_script(script_name):
    """执行指定Python脚本"""
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            check=True,
            text=True,
            capture_output=True
        )
        print(f"✅ {script_name} 执行成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {script_name} 执行失败:")
        print(e.stderr)
        return False

if __name__ == "__main__":
    # 执行顺序列表
    scripts = [
        "step1_download_rules.py",      # 下载规则
        "step2_merge_rules.py",           # 合并规则
        "step3_classify_rules.py",        # 分类规则
        "step4_classify_black_white.py",  # 黑白名单分类
        "step5_strip_domains.py",         # 域名提取
        "step6_combine_black_white.py",   # 合并黑白名单
        "step7_conflict_handler.py",      # 冲突处理
        "step8_rule_standardizer.py"      # 规则标准化
    ]

    print("🚀 开始执行过滤规则处理流程...")
    for script in scripts:
        if not run_script(script):
            print(f"中断执行，请先解决 {script} 的问题")
            sys.exit(1)
    
    print("🎉 所有处理步骤已完成！")