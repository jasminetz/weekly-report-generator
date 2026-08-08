---
name: weekly-report-generator
description: >
  生成周报（Markdown）。当用户提到"周报"、"weekly report"、"本周工作汇总"、"本周提交"、
  "本周变更"、"generate weekly report"、"/weekly-report" 时触发。
  NOT 月报/日报/年报 — 那些不是这个技能的范围。
---

# 周报生成器

扫描本周（周一 00:00 至周日 23:59）的 Git 提交和 TODO 变更，生成结构化周报
Markdown 文件，保存到 `reports/` 目录。

## 语言策略

报告语言**跟随用户的提示词语言**：
- 用户用中文提问 → 报告标题、章节名全部用中文（周报、概览、提交记录、TODO 变更…）
- 用户用英文提问 → 报告标题、章节名全部用英文（Weekly Report, Overview, Commit Log, TODO Changes…）
- 不要混用中英文章节名

## 前置要求

- 当前目录必须是 Git 仓库
- 项目根目录存在 `reports/` 目录（如不存在则自动创建）

## 工作流程

### 第一步：确定时间范围

计算本周一 00:00 和本周日 23:59 的日期。使用 ISO 8601 格式（`YYYY-MM-DD`）。

- 周一 = 本周第一个工作日
- 周日 = 本周最后一天

如果今天是周一，则本周从今天开始；如果今天是周日，则本周到当天结束。
使用 `date` 命令计算，兼容 macOS 和 Linux。

### 第二步：收集 Git 提交记录

对当前分支执行 `git log`，过滤出本周时间范围内的提交：

```bash
git log --oneline --since="<周一>T00:00:00" --until="<周日>T23:59:59" --author-date-order
```

如果本周没有提交，报告中写明"本周无提交"即可，不视为错误。

如果提交数量较多（超过 30 条），使用 `--format` 输出更丰富的信息：
```bash
git log --since="<周一>T00:00:00" --until="<周日>T23:59:59" \
  --format="%h %s (%an, %ad)" --date=short --author-date-order
```

### 第三步：收集 TODO 变更

**3a. 代码中的 TODO/FIXME/HACK 注释变更**

使用 `git diff` 查看本周范围内的变更，过滤新增和删除的 TODO 标记：

```bash
# 获取本周范围内的 diff
git diff $(git log --since="<周一>T00:00:00" --until="<周日>T23:59:59" --format=%H | tail -1)^..HEAD -- '*.js' '*.ts' '*.py' '*.java' '*.go' '*.rs' '*.jsx' '*.tsx' '*.vue' '*.rb' '*.swift' '*.kt' '*.c' '*.cpp' '*.h' '*.md'
```

在 diff 输出中搜索以下关键词的新增行（以 `+` 开头的行）：
- `TODO`
- `FIXME`
- `HACK`
- `XXX`
- `OPTIMIZE`
- `BUG`

同时统计删除的行（以 `-` 开头的行）中是否包含上述标记，表示已解决/移除的待办项。

**3b. TODO.md 文件变更**

检查 `TODO.md`（或 `todo.md`）是否存在。如果存在，查看其在本周范围内的变更：

```bash
git log --since="<周一>T00:00:00" --until="<周日>T23:59:59" --oneline -- TODO.md todo.md
```

如果文件存在且有变更，在报告中展示 diff 摘要。

### 第四步：收集统计信息

汇总以下统计数据：
- 本周总提交数
- 参与提交的作者列表
- 新增/删除的文件数
- 新增的 TODO 数量
- 已解决的 TODO 数量

使用以下命令辅助统计：
```bash
# 提交数和作者
git shortlog -sn --since="<周一>T00:00:00" --until="<周日>T23:59:59"

# 文件变更统计
git diff --stat $(git log --since="<周一>T00:00:00" --until="<周日>T23:59:59" --format=%H | tail -1)^..HEAD
```

### 第五步：生成周报

按以下模板生成 Markdown 文件，保存到 `reports/weekly-report-YYYY-MM-DD.md`
（日期使用本周日，即报告覆盖的结束日期）：

```markdown
# 周报：YYYY-MM-DD ~ YYYY-MM-DD

> 自动生成于 YYYY-MM-DD HH:MM
> 分支：<branch-name>

## 📊 概览

| 指标 | 数量 |
|------|------|
| 提交数 | N |
| 参与作者 | N 人 |
| 新增 TODO | N |
| 已解决 TODO | N |

## 👥 贡献者

| 作者 | 提交数 |
|------|--------|
| ... | ... |

## 📝 提交记录

| 哈希 | 描述 | 作者 | 日期 |
|------|------|------|------|
| ... | ... | ... | ... |

### 提交详情

<!-- 如果提交数 ≤ 10，可展开每个提交的详细 diff 摘要 -->

## ✅ TODO 变更

### 新增待办项

<!-- 列出本周新增的 TODO/FIXME/HACK 等，包含文件路径和行内容 -->

### 已解决待办项

<!-- 列出本周删除的 TODO/FIXME/HACK 等，表示已完成或移除 -->

## 📋 TODO.md 变更

<!-- 如果 TODO.md 有变更则展示，否则写"无变更" -->

## 📈 文件变更摘要

<!-- git diff --stat 的输出摘要 -->
```

### 第六步：告知用户

生成完成后，告知用户报告已保存的路径，并简要概述关键数据：
- 本周提交数
- 新增/解决 TODO 数
- 报告文件路径

## 注意事项

- 所有 `git` 命令都应在项目根目录下执行
- 如果本周范围没有提交，使用 `HEAD` 作为 diff 的参考点
- 对于大型仓库，只扫描常见源代码文件类型，避免扫描二进制文件或 `node_modules`
- 文件路径使用相对于项目根目录的相对路径
- Markdown 中的 emoji 用于提高可读性，不要过度使用
