# 💼 AI 求职助手 · Job Apply Assistant

贴一个 JD，AI 自动评估值不值得投、产出针对该 JD 定制的中文简历 PDF、给出投递行动清单。

> **定位**：**JD 评估 + 定制简历生成引擎**——专注产出"给人看的高质量求职材料"（评估报告 / 定制简历 PDF / 投递清单）。
> 自动化投递（采集→评分→打招呼→发送）由投递流水线承担（如 [BossHunter](https://github.com/powerycy/BossHunter)），二者互补，见下文「与投递流水线的分工」。

> **本项目基于开源项目二次开发**（诚实声明）：
> - 上游：`sunyet-01/ai-job-search-cn`（MIT）← `MadsLorentzen/ai-job-search`（MIT）
> - 本项目增量：**Windows 中文字体适配的重构渲染引擎 + LLM 简历生成闭环（上游缺失）+ skill 工作流封装**

---

## ✨ 功能

| 功能 | 说明 |
|------|------|
| 🎯 **7 维 JD 评估** | 技能/经验/文化/薪资/强度/稳定性/通勤加权评分 + Deal-breaker 强制降分（996/外包判不投） |
| 📄 **定制简历 PDF** | 画像 + JD → LLM 生成结构化简历 → reportlab 渲染一页中文 PDF（ATS 关键词命中） |
| 📋 **投递清单** | 官方渠道 + BOSS直聘/猎聘/智联搜索链接 + 0/5/12 天跟进话术 |
| 🔁 **可复用工作流** | 评估 → 草拟 → Reviewer 批评 → 修订 → 编译校验（SKILL.md 封装） |

---

## 💡 与投递流水线（BossHunter）的分工

本项目**不替代**投递自动化工具，而是补齐"投递流水线不产出"的部分——高质量求职材料：

| 环节 | BossHunter（投递流水线） | 本项目（评估+简历引擎） |
|------|--------------------------|------------------------|
| 岗位采集 | ✅ 关键词/城市自动翻页 + 去重 | —（接收已采岗位） |
| 匹配筛选 | ✅ AI 两阶段评分（快速预筛→深度评分） | ✅ **7 维评估报告**（分维表/亮点/风险/薪资对标/中国化专项） |
| 招呼语 | ✅ AI 定制个性化开场白 | — |
| 自动投递 | ✅ 人工确认 + 低频发送（防封号） | —（产出投递清单） |
| **定制简历** | ⚠️ xhtml2pdf 简单渲染 | ✅ **reportlab 中文 PDF**：照片/蓝色分区/Windows 字体/ATS 校验 |
| HR 回复监听 | ✅ 自动监测 + 建议回复 | — |

**推荐工作流**：BossHunter 海投筛选 → 对重点岗位用本项目产出**深度评估报告 + 定制简历 PDF** → 定向投递。
两个工具互补，覆盖求职全链路。

---

## 🚀 快速开始

```bash
# 1. 安装依赖
pip install reportlab

# 2. 填画像（先复制模板）
cp data/profile.template.json data/profile.json
# 编辑 profile.json：姓名/教育/经历/技能/求职偏好

# 3. 运行评估 + 生成简历
python tools/resume_render.py            # 简历渲染引擎（读取 profile.json + resume.json）
```

完整工作流见 [SKILL.md](SKILL.md)（AI agent 使用指引）与
[references/](references/)（评估框架 + 简历 JSON schema）。

---

## 📁 目录结构

```
job-apply-assistant/
├── SKILL.md                     # AI agent 工作流（评估→草拟→review→编译）
├── tools/
│   ├── resume_render.py         # 中文简历 PDF 渲染（reportlab，Windows 字体适配）
│   └── channel_list.py          # 投递渠道清单生成
├── references/
│   ├── evaluation-framework-cn.md  # 中国化 7 维评估框架
│   └── resume-json-schema.md       # 简历 JSON 数据 schema
├── data/
│   └── profile.template.json    # 用户画像模板（**不含真实个人信息**）
└── LICENSE
```

---

## 🔒 隐私声明

- **本仓库不含任何真实个人信息**：`data/profile.json`（真实画像）与照片被 `.gitignore` 排除，仅存本地
- 开源内容仅含：工作流文档、评估框架、渲染代码、空模板
- 你的求职数据（画像/简历/投递记录）**永不上传本仓库**

---

## 📜 License

MIT — 见 [LICENSE](LICENSE)（保留上游版权声明，符合 MIT 协议要求）。
