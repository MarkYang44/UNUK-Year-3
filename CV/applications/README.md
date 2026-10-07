# COMP2002 项目申请材料

当前推荐：`shared/Yang_Qixuan_CV_Group_Projects.pdf`，一份同时用于 Pacman、AI Game Player 和 Crisis Reporting App 的个人英文 CV。其 LaTeX 源码及讲义要求对应说明位于 `shared/`。此前三份项目定制版保留供参考。AI Game Player 已有带留白标注的 EOI 草稿：`ai_game_player/Team26_UoN_AiGamePlayer_EoI_Draft.docx`；其他 EOI 尚未编写。未提交 Moodle 或联系项目方。

每份 CV 均为独立 LaTeX 源文件，使用相同的单栏 A4 模板。分别打开 `.tex` 即可在 Codex 内置 LaTeX 编辑器中修改和预览；最终 PDF 由 LaTeX 编译导出。课程允许最多两面 A4，本次优先保持一页。

| 项目 | 文件夹 | 内容重点 |
|---|---|---|
| 三项目共用（推荐） | `shared/` | 软件逻辑与测试、AI 实验与状态管理、API/数据处理、沟通与交付 |
| UoN Pacman | `pacman/` | 确定性逻辑、边界测试、UI/核心分离、可重复运行 |
| UoN AI Game Player | `ai_game_player/` | AI 实验与评估、状态管理、通用语言、测试与设计交接 |
| CGI Crisis Reporting App | `crisis_app/` | Java API、数据模型、隐患报告、审计追溯、失败处理 |

完整解释见 `Project_Fit_Analysis.md`；CareerSet 实测与反馈取舍见 `assessment/CareerSet_Review.md`。

## 事实来源与界限

- 个人经历：`../2026_summer_internship_summary.md`、`../Yang_Qixuan_CV_2026.tex`，以及用户确认的 2+2 学制信息。
- 项目要求：`../pdf/UoN-Pacman (Graham Hutton).pdf`、`../pdf/UoN-AIGamePlayer (Kristian Spoerer).pdf`、`../pdf/CGI-CrisisApp.pdf`。
- CV 格式：`../../Y3_Autumn/COMP2002_GRP/lecture2CVs.pdf` 与 `projectHandbook2.0.15.pdf`。
- 11 项医疗后端测试属于本地结果；Fabric 验收属于本地重建环境。没有据此声称生产部署。
- 没有把 LangGraph 智能体写成 MCTS，也没有声称已有 JavaFX、游戏引擎、移动端、QR/GPS 或生产 RBAC 实现经验。
- 新项目的可能实现方案只出现在分析文件中，明确标为建议；不作为 CV 已完成经历。

## PDF 导出

优先使用 Codex 内置编译器检查独立 `.tex`。本机已具备的 Tectonic 可用于导出 PDF，无须安装新的 TeX 环境：

```sh
TECTONIC_CACHE_DIR=/private/tmp/cv-tectonic-cache \
/Applications/ChatGPT.app/Contents/Resources/tectonic/tectonic \
  --untrusted --only-cached --outdir CV/applications/pacman \
  CV/applications/pacman/Yang_Qixuan_CV_Pacman.tex
```

其他两份替换输入路径和输出目录即可。字体按 TeX 字体文件名加载，不依赖 Windows 字体；每个源文件均不依赖外部 `\input` 文件。
