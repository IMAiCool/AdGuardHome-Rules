
# 🛡️ AdGuard 规则处理工具

一个用于自动合并、清洗、分类和生成 AdGuard 规则的 Python 工具，支持黑白名单划分、冲突检测、格式标准化和日志记录。适用于广告屏蔽、隐私保护、DNS 过滤等场景。

## 📂 项目目录结构

```
main/
├── adguard_rule_processor.py    # 主程序
├── input/                       # 输入规则目录
│   ├── local-rules.txt          # 本地规则
│   └── urls.txt                 # 远程规则源（格式: 名称:URL）
├── output/                      # 输出黑白名单规则
│   ├── black_list.txt
│   ├── white_list.txt
│   ├── blacklist-domain.txt
│   ├── whitelist-domain.txt
│   └── hosts-domain.txt
├── others/                      # 中间文件目录
│   ├── alllist.txt
│   ├── hosts.txt
│   ├── adguard-rules.txt
│   └── all.css
├── Log/                         # 日志文件目录
│   ├── list-in-all.log
│   ├── list-in-both.log
│   ├── delete_Hierarchy.log
│   ├── delete_white.log
│   └── delete-rules.log
```

## ⚙️ 功能特性

- ✅ 合并本地和远程规则
- ✅ 过滤注释与空行
- ✅ 自动分类为：
  - `hosts` 格式
  - 标准 AdGuard 格式（黑白名单）
  - 含特殊字符的规则
- ✅ 黑白名单自动划分与去重
- ✅ 冲突处理（包括层级域名冲突）
- ✅ 标准输出 AdGuard 黑白名单
- ✅ 输出处理日志与统计信息
- ✅ 支持每 12 小时自动更新

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install requests
```

### 2. 准备输入文件

#### `input/local-rules.txt`

自定义本地规则，一行一个。

#### `input/urls.txt`

格式：

```
规则名称1:https://example.com/rule1.txt
规则名称2:https://example.com/rule2.txt
```

### 3. 运行程序

```bash
python adguard_rule_processor.py
```

### 4. 查看输出结果

- 黑白名单规则输出在 `output/` 目录：
  - `black_list.txt`
  - `white_list.txt`

- 日志文件和中间文件可在 `Log/` 和 `others/` 目录查看。

## 🕒 定时自动更新（Linux）

使用 `crontab` 每 12 小时自动执行：

```bash
crontab -e
```

添加以下行：

```bash
0 */12 * * * /usr/bin/python3 /your/path/adguard_rule_processor.py >> /your/path/Log/cron.log 2>&1
```

