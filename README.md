# AdGuard 规则合并去重工具说明文档-ChatGPT构建编写

* * *

## 一、项目简介

本项目用于合并本地规则文件和多个上游规则 URL 中的 AdGuard 规则，实现规则去重、黑白名单分类及格式转换，最终输出多份规则文件，方便 AdGuardHome 或类似工具使用。

* * *

## 二、功能需求

1. **输入规则来源**
  
  * 本地规则文件（`local_rules.txt`）
  * 上游规则 URL 列表文件（`urls.txt`）
2. **规则合并及输出**
  
  * 所有上游规则不去重，直接合并保存为 `output/all_rules.txt`
  * 规则中包含特殊字符（`/`, `=`, `\`, `#`, `?`, `(`, `)`, 其中 `#` 不在规则首位）的规则，直接剔除出 `output/all_rules.txt`，分别保存到 `output/blacklist_css.txt` 和 `output/whitelist_css.txt`
3. **黑白名单分类**
  
  * 清理后的规则根据是否以 `@@` 开头进行黑名单或白名单分类
  * 本地规则与上游规则合并，去重后加入对应名单
  * 规则格式剥离为纯域名格式后再去重
4. **冲突处理**
  
  * 如果某域名同时存在黑白名单，删除黑名单条目
  * 如果黑名单中存在某域名，其上级域名从白名单中删除
5. **格式化输出**
  
  * 最终规则统一转为 AdGuard 规则格式：
    * 黑名单：`||域名^`
    * 白名单：`@@||域名^`
  * 本地规则读取时，先剥除 `$important` 标记
  * 规则末尾不再添加 `$important`
6. **统计信息与文件头部**
  
  * 每份输出文件头部包含：
    * 上游规则 URL 列表
    * 规则条目数量
    * 本地规则条目数量
    * 更新时间（执行时间）
    * 更新频率（默认 12 小时）
7. **输出文件**
  
  * `output/all_rules.txt`：合并的所有上游规则（不去重）
  * `output/blacklist_css.txt`：含特殊字符的黑名单规则
  * `output/whitelist_css.txt`：含特殊字符的白名单规则
  * `output/blacklist.txt`：最终处理后的黑名单规则
  * `output/whitelist.txt`：最终处理后的白名单规则

* * *

## 三、运行环境及依赖

* Python 3.x
* 依赖库：
  * `requests`

安装依赖：

    pip install requests

* * *

## 四、文件说明

* `local_rules.txt`：本地规则文件，规则以文本形式存放，白名单规则以 `@@` 开头
* `urls.txt`：上游规则 URL 列表，每行一个 URL
* `output/`：输出目录，保存生成的规则文件

* * *

## 五、使用说明

1. 准备好 `local_rules.txt` 和 `urls.txt`，放置于脚本同目录
2. 运行脚本：
  
      python your_script.py
  
3. 结果文件保存在 `output/` 文件夹
4. 查看控制台输出的统计信息

* * *

## 六、规则处理流程简述

1. 读取本地规则，去除 `$important`，分类黑白名单
2. 下载并合并上游规则，输出 `output/all_rules.txt`
3. 剔除特殊字符规则，保存 `output/blacklist_css.txt` 和 `output/whitelist_css.txt`
4. 分类、去重、合并本地规则
5. 域名提取、冲突清理
6. 格式化输出到 `output/blacklist.txt` 和 `output/whitelist.txt`
7. 添加文件头部元信息

* * *

## 七、统计信息输出示例

    ✅ 规则处理完成
    📥 上游规则总条数（含注释/特殊）：12345
    📄 本地黑名单规则数：678
    📄 本地白名单规则数：234
    🚫 含特殊字符规则（blacklist_css.txt）：45
    🚫 含特殊字符规则（whitelist_css.txt）：12
    ✅ 最终黑名单规则数（blacklist.txt）：7890
    ✅ 最终白名单规则数（whitelist.txt）：3456
    📂 输出文件位于：output/all_rules.txt

* * *

## 八、注意事项

* 确保网络畅通
* 本地规则格式需规范
* 更新频率可自行调整
* 确保 `output/` 写权限

* * *

## 九、总结

本工具自动化管理 AdGuard 规则，简化合并与冲突处理，提供标准化输出，适用于定时更新与维护。

* * *

## 十、GitHub Actions 自动化操作流程

### 1. 自动执行脚本

在项目根目录下创建 `.github/workflows/run_script.yml` 文件，内容如下：

    name: Run AdGuard Rule Script
    
    on:
      schedule:
        - cron: '0 */12 * * *'  # 每 12 小时执行一次
      workflow_dispatch:        # 允许手动触发
    
    jobs:
      build:
        runs-on: ubuntu-latest
        steps:
          - name: Checkout repository
            uses: actions/checkout@v3
    
          - name: Set up Python
            uses: actions/setup-python@v4
            with:
              python-version: '3.x'
    
          - name: Install dependencies
            run: pip install requests
    
          - name: Run script
            run: python your_script.py
    
          - name: Upload output
            uses: actions/upload-artifact@v3
            with:
              name: output-files
              path: ./output

### 2. 设置推送输出结果到仓库（可选）

如需将 `output/` 内容自动提交至 GitHub 仓库，请在工作流中追加以下步骤：

          - name: Commit and push output
            run: |
              git config user.name "github-actions[bot]"
              git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
              git add output
              git commit -m "🔄 自动更新规则文件"
              git push

### 3. 手动运行工作流

* 进入 GitHub 仓库
* 点击 `Actions` 标签
* 选择工作流名称
* 点击 `Run workflow` 按钮

### 4. 查看任务是否成功执行

* 在 `Actions` 页签中查看工作流运行历史
* 查看日志输出、检查结果文件是否正确上传或提交

* * *

## 十一、加速中国大陆访问的建议

若您的 AdGuardHome 部署在中国大陆，建议：

* 使用国内 CDN 加速访问 output 文件，例如将 `output` 目录托管在：
  * jsDelivr
  * 腾讯云对象存储 + CDN
  * Gitee Pages
* 或将仓库同步到国内镜像服务

* * *
