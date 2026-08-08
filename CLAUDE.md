# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目名称
claude_deepseek

## 项目概述
Claude Code 配置与技能集合项目，包含自定义 skills、权限配置和周报生成工具。

## 目录结构
- `.claude/skills/` - 自定义技能（weekly-report-generator, skill-creator 等）
- `.claude/setting.json` - 权限与行为配置
- `reports/` - 周报输出目录
- `prompt.txt` - 提示词模板
- `README.md` - 项目说明

## 权限配置
`.claude/setting.json` 中配置了以下权限：
- **允许**: Read, Write, `npm *`, `git *`, `node *`
- **禁止**: `rm -rf *`
- **autoCompactThreshold**: 80

## 技能
- `weekly-report-generator` - 根据 Git 提交记录生成周报 Markdown
- `skill-creator` - 创建和优化技能
