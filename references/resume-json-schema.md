# 简历 JSON Schema 与 LLM 生成指引

> 用途：LLM 依据「用户画像 profile.json + JD 解析结果」生成结构化简历数据 resume.json，
> 再由 `tools/resume_render.py --data resume.json` 渲染 PDF。本文件是生成环节的唯一判定标准。

## 一、resume.json 结构

```json
{
  "name": "张小明",
  "title": "后端开发实习生",
  "email": "zhangxm@example.com",
  "phone": "138-0000-0000",
  "location": "上海",
  "github": "github.com/zhangxm",
  "summary": "一句话简介：身份 + 核心技能 + 最有区分度成果（≤50 字）",
  "skills": ["Python", "FastAPI", "SQL"],
  "sections": {
    "教育": [
      {"title": "XX大学 · 软件工程（本科）", "date": "2022-09 - 2026-06", "bullets": ["GPA / 主修课程 / 荣誉"]}
    ],
    "项目经历": [
      {"title": "项目名（可加一行技术栈）", "date": "2025-03 - 2025-06", "bullets": ["量化成果 1", "量化成果 2"]}
    ],
    "实习经历": [
      {"title": "公司 · 岗位", "date": "2024-06 - 2024-09", "bullets": ["职责与量化成果"]}
    ]
  }
}
```

### 约束

- `name/title/email/phone/location` 必填；`github/summary/skills/sections` 可选但鼓励填。
- 可选字段 `"photo": "照片路径"`（PNG 圆形最佳，渲染到右上角；也可用 `--photo` 参数传入）。
- `sections` 的 key 是中文节名（教育/项目经历/实习经历/奖项/技能补充…），顺序即 PDF 渲染顺序。
- 每个条目：`title`（必填）、`date`（用 ASCII 连字符：`2024-09` 或 `2024-09 - 2025-01`）、`bullets`（每行一个要点，≤2 行，避免超页）。
- `skills` 是数组；**用 JD 原文词**，不用同义改写（ATS 命中）。

## 二、profile.json（用户画像）→ resume.json 映射

| profile 字段 | resume 去向 | 处理规则 |
|---|---|---|
| identity.name/phone/email/... | name/phone/email/... | 直接映射 |
| target.job_titles | title | 取与 JD 匹配的那个 |
| education | sections.教育 | 全量保留（实习/校招简历教育必填） |
| experience | sections.实习经历 | **relevance-weighted cutting**：按相关度剪裁要点 |
| projects | sections.项目经历 | 挑与 JD 最相关的 2-3 个，其余丢弃 |
| skills[] | skills | 与 JD required/preferred 求交，缺的用"熟悉/了解"诚实标注，绝不虚构 |
| awards | sections.奖项 | 与岗位相关才放 |
| behavioral | summary 的语气参考 | 不直接输出 |

## 三、LLM 生成方法论

### 1. relevance-weighted cutting（简历剪裁）
对每一条经历要点打分：
- **相关度**（0-2）：与 JD 要求的技能/职责直接相关？
- **唯一性**（0-2）：这条经历是画像里独有的亮点？
- **narrative load**（0-2）：是否为整体叙事关键一环？
总分 < 3 的行优先剪掉；剪完后页数仍超预算继续从低分剪。
目标页数：**实习/校招 1 页**，社招 1-2 页。

### 2. ATS 关键词
- 技能、工具、框架名一律用 JD 原文词（JD 写 "FastAPI" 就不要写 "API 框架"）。
- 保留英文大小写（`RAG`、`Kubernetes`），不翻译。

### 3. 量化原则
- 每行要点尽量含数字：规模、时长、性能提升、覆盖率。
- 以动词开头：实现/设计/优化/搭建/负责（避免空洞形容词）。

### 4. 诚实红线
- profile 里没有的经历/技能/数据 → 不写，绝不编造。
- JD 要求但画像缺的技能 → 用「了解/自学中」诚实呈现（如确有其事），否则不写。
- 日期必须与 profile 一致，不模糊化造假。

### 5. 求职信（cover letter）何时写
评估报告建议为「Good（60-74）投 + 求职信补缺口」或用户要求时写：
200-300 字中文，结构：为什么对这个岗位感兴趣（1 句）→ 2-3 条与 JD 最相关的证据 → 一句谦虚的缺口说明（如有）。
与简历分开存放：`output/<岗位名>/04-求职信.md`。

## 四、生成与校验流程（LLM 执行）

1. 读 profile.json + JD 解析结果
2. 按映射规则 + cutting 方法论生成 resume.json
3. **自审**（第 4 步 Reviewer）：逐条检查贴 JD / 无编造 / ATS 原文词 / 量化 / 页数
4. 修订至无遗留问题
5. 渲染 PDF 后用 pymupdf（或 pdftotext）提取文本，抽查关键技能词与 JD 一致
