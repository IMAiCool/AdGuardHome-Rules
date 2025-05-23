
# AdGuard规则合并与分类处理脚本

---

## 一、项目简介

本项目为一套Python脚本，旨在自动化处理AdGuard及相关规则列表的下载、合并、分类、去重和格式化。  
支持从多个上游规则源和本地规则文件同步内容，统一规范化规则格式，检测并处理黑白名单冲突及域名层级冲突，最终输出标准化黑白名单文件，方便后续在AdGuard等软件中直接使用。

---

## 二、功能模块说明

### 1. 规则下载与合并（`download_and_merge_rules`）

- 从指定URLs列表下载远程规则文件
- 读取本地规则文件
- 剔除规则头部信息与注释
- 合并所有规则，去重后输出到统一文件

### 2. 规则分类（`classify_rules`）

- 根据规则格式判断类别  
  - IP与域名格式规则输出到`hosts`文件  
  - AdGuard规则格式输出到`adguard.txt`  
  - 其他格式规则输出到`others.txt`

### 3. hosts和AdGuard规则格式检查与清理（`validate_and_clean_hosts_adguard`）

- hosts文件剔除包含 `local`、`localhost`、`boardcasthost` 字符的规则，以及不合法的IP条目
- AdGuard规则中过滤带有特殊字符（`/ \ ? [ ] # =`）或格式异常的规则，移入others文件

### 4. AdGuard黑白名单分类（`split_adguard_black_white`）

- 根据规则前缀分为黑名单（`||`开头）、白名单（`@@`开头）及其它三类文件

### 5. 域名剥离（`extract_domains_from_rules`）

- 从黑白名单及hosts文件中提取纯域名部分，输出为去格式化的纯域名列表文件

### 6. 黑名单域名合并（`merge_black_domains`）

- 合并hosts剥离域名与黑名单剥离域名，去重后输出

### 7. 黑白名单冲突检测（`detect_black_white_conflicts`）

- 检测黑白名单中同时出现的域名
- 冲突条目输出到日志，注明行号及冲突原因
- 非冲突条目分别输出最终黑白名单文件

### 8. 域名层级冲突处理（`handle_hierarchy_conflicts`）

- 检查同一文件内是否存在父子域名同时出现
- 保留父域名，剔除子域名，记录删除日志及所在行号
- 没有找到父域的子域名分别输出到指定fallback文件

### 9. 黑白名单去重与格式化（`deduplicate_and_format_black_white`）

- 对最终黑白名单文件进行全行去重
- 白名单剔除二级域名条目
- 黑名单格式化为 `||example.com^`
- 白名单格式化为 `@@||example.com^`

---

## 三、目录结构

```
project_root/
│
├─ input/                # 输入文件目录
│   ├─ urls.txt          # 远程规则URL列表，格式：规则名: URL
│   └─ local-rules.txt   # 本地规则文件
│
├─ others/               # 中间处理文件输出目录
│   ├─ merged-rules.txt
│   ├─ hosts
│   ├─ adguard.txt
│   ├─ others.txt
│   ├─ adguard-black.txt
│   ├─ adguard-white.txt
│   ├─ adguard-others.txt
│   ├─ adguard-blackd.txt
│   ├─ adguard-whited.txt
│   ├─ hostsd
│   ├─ black.txt
│   ├─ blacklist.txt
│   ├─ whitelist.txt
│   ├─ AdBlacklist.txt
│   └─ AdWhitelist.txt
│
├─ Log/                  # 日志文件目录
│   ├─ list-in-both.log          # 黑白名单冲突日志
│   └─ delete_Hierarchy.log      # 域名层级冲突删除日志
│
├─ output/               # 最终输出目录
│   ├─ black_list.txt    # 格式化黑名单最终文件
│   └─ white_list.txt    # 格式化白名单最终文件
│
└─ script.py             # 主脚本文件，包含所有功能模块及主函数
```

---

## 四、运行说明

1. 将远程规则URL列表放入 `./input/urls.txt` ，格式为 `规则名: URL`
2. 本地规则放入 `./input/local-rules.txt`
3. 运行 `python script.py`
4. 脚本执行完成后，中间文件输出于 `./others/`，日志输出于 `./Log/`，最终黑白名单分别输出到 `./output/`
5. 查看日志文件确认冲突及层级冲突详情

---

## 五、注意事项

- 确保执行脚本的目录存在上述目录结构或提前创建
- 保证网络畅通以正确下载远程规则
- 文件编码均为UTF-8
- 规则格式的准确性直接影响分类与剔除的效果
