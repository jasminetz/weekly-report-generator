# Weekly Report Generator

基于 Claude Code Skill 的周报自动生成工具 —— 扫描本周 Git 提交记录和 TODO 变更，输出结构化 Markdown 周报。

## 功能

- 自动检测当前仓库本周（周一至周日）的所有 Git 提交
- 追踪代码中 TODO / FIXME / HACK / XXX / OPTIMIZE / BUG 标记的新增与解决
- 监控 `TODO.md` 文件变更
- 汇总统计数据（提交数、贡献者、文件变更量）
- 输出结构化 Markdown 周报至 `reports/` 目录
- 支持中英文双语，语言自动跟随用户提示词

## 项目结构

```
claude_deepseek/
├── .claude/
│   ├── skills/
│   │   ├── weekly-report-generator/     # 周报生成器 Skill
│   │   │   ├── SKILL.md                 # 技能定义与工作流程
│   │   │   └── evals/evals.json         # 评估用例
│   │   ├── weekly-report-generator-workspace/  # 评估工作区
│   │   │   ├── build_benchmark.py       # 基准测试构建脚本
│   │   │   ├── grade_evals.py           # 评估评分脚本
│   │   │   └── iteration-1/             # 第 1 轮迭代
│   │   │       ├── benchmark.json       # 基准测试结果
│   │   │       ├── benchmark.md         # 基准测试报告
│   │   │       ├── review.html          # 评估审查页面
│   │   │       ├── chinese-weekly-report/   # 中文周报评估
│   │   │       ├── english-weekly-report/   # 英文周报评估
│   │   │       └── todo-focused-report/     # TODO 重点周报评估
│   │   └── skill-creator/               # Skill 创建工具链
│   │       ├── SKILL.md
│   │       ├── agents/                  # 评估 Agent 定义
│   │       ├── scripts/                 # 辅助脚本
│   │       └── eval-viewer/             # 评估结果可视化
│   ├── CLAUDE.md
│   └── setting.json
├── reports/                             # 生成的周报输出目录
│   ├── weekly-report-2026-08-03.md
│   ├── weekly-report-2026-08-09.md
│   └── weekly-report-2026-08-03-to-2026-08-09.md
├── prompt.txt                           # Skill 创建指令
└── README.md
```

## 使用方式

在 Claude Code 对话中直接触发：

```
帮我生成这周的周报
```

或英文：

```
Generate a weekly report for this week
```

Skill 会自动：
1. 计算本周日期范围
2. 执行 `git log` 收集提交记录
3. 扫描代码 diff 中的 TODO 标记变更
4. 生成报告保存到 `reports/weekly-report-YYYY-MM-DD.md`

## 周报内容

生成的周报包含以下章节：

| 章节 | 说明 |
|------|------|
| 📊 概览 | 提交数、贡献者、新增/解决 TODO 数 |
| 👥 贡献者 | 本周活跃作者及提交数 |
| 📝 提交记录 | 每条提交的哈希、描述、作者、日期 |
| ✅ TODO 变更 | 新增和已解决的 TODO/FIXME/HACK 标记 |
| 📋 TODO.md 变更 | 项目 TODO 文件变更摘要 |
| 📈 文件变更摘要 | `git diff --stat` 统计输出 |

## 基准测试结果

基于 `deepseek-v4-pro[1m]` 模型，3 个评估用例各运行 1 次：

| 指标 | 使用 Skill | 不使用 Skill | 提升 |
|------|-----------|-------------|------|
| 通过率 | **92%** ± 14% | 83% ± 19% | +9% |
| 耗时 | 600.8s | 460.7s | — |
| Token | 23015 | 16848 | — |

Skill 在通过率上有明显提升（92% vs 83%），尤其在中文和 TODO 重点场景下达到 100% 通过率。

## 评估用例

| ID | 场景 | 断言数 |
|----|------|--------|
| 1 | 中文提示：帮我生成这周的周报 | 8 |
| 2 | 英文提示：Generate a weekly report | 8 |
| 3 | 中文提示：生成本周工作周报，重点列出 TODO/FIXME | 8 |

## 依赖

- Claude Code（支持 Skill 功能）
- Git 仓库
- 当前分支有本周提交记录

如果本周无提交，报告会如实标注"本周无提交"而非报错。
