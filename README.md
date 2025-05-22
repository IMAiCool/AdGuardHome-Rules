# AdGuard Rule Merger Tool

## 项目概述
本工具用于合并本地与上游的广告过滤规则，自动分类为 hosts、adguard-rules、css，并进行黑白名单分类与冲突清理，输出标准格式规则文件。每12小时自动更新一次。

## 功能特点
- 支持从 `local-rules.txt` 与 `urls.txt` 合并规则
- 分类输出为 hosts、adguard-rules、css
- 标准 AdGuard 黑白名单格式处理
- 域名冲突与白名单优先处理机制
- 输出详细日志与统计信息
- 每12小时自动执行更新任务

## 输入文件目录结构
- `input/local-rules.txt`: 本地规则
- `input/urls.txt`: 上游规则，格式为 `规则名称: URL`

## 输出目录结构
- `output/black_list.txt`: 标准黑名单规则
- `output/white_list.txt`: 标准白名单规则
- `others/`: 存放中间结果，如 `alllist.txt`, `adguard-rules.txt`
- `Log/`: 冲突处理日志，如 `delete-rules.log`

## 控制台输出示例
```
[规则处理报告] 2025-05-22 14:30:00
-------------------------------------
■ 输入规则统计
  ├─ 本地规则: 12,340条 
  └─ 远程规则: 1,258,792条（EasyList/AdGuard等15个源）

■ 分类处理结果
  ├─ 基础规则(alllist.txt): 983,452条
  ├─ CSS/正则规则(all.css): 275,340条
  ├─ hosts规则初筛(hosts): 896,732条
  └─ adguard规则初筛(blacklist.txt):896,732条

■ 冲突处理统计
  ├─ 直接冲突条目: 3,215条（delete-rules.log）
  ├─ 黑名单冲突条目:2253条(list-in-both.log)
  └─ 层级冲突条目: 1,842条（delete_rules.log）

■ 最终生效规则
  ├─ 黑名单生效: 754,417条（output/black_list.txt）
  └─ 白名单生效: 78,048条（output/white_list.txt）

下次更新: 2025-05-22 02:30:00
```

## 使用说明
运行脚本 `scripts/adguard_rule_merger.py` 开始处理任务。可设为定时任务自动更新。
