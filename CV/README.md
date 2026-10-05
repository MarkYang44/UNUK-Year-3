# CV 文件说明

- `Yang_Qixuan_CV_2026.tex`：润色后的 LaTeX 源文件，英文一页、中文一页。
- `Yang_Qixuan_CV_2026.pdf`：由同一源文件编译导出的 PDF。
- `draft_backup/`：修改前的 LaTeX 初稿和 PDF，保留原始内容。
- `2026_summer_internship_summary.md`：本次实习内容润色的依据；原有 DOCX 和 PDF 总结材料未修改。

本版面向通用技术岗位，突出工厂安全 AI 助手、医疗健康专区后端、Hyperledger Fabric 平台三项主线；将工程收获体现为来源追溯、检索降级、兼容性审计、自动化验收、回归测试和账本兼容。智能体、合规验收及安全沙箱作为补充经历。

项目数字沿用实习总结记录。医疗项目的 11 项测试属于本地单元测试；Fabric 的四组织、12 个页面和四 Peer 交易结论属于本地验收；智能体为原型，沙箱为离线交付脚本，不代表生产环境部署已完成。图像分类项目、成绩、联系方式和奖学金信息沿用初稿。

教育经历按本人补充信息更新：宁波诺丁汉大学 2024–2026；英国诺丁汉大学 Jubilee 校区自 2026 年 9 月开始，预计 2028 年 6 月毕业。GPA 和专业排名标注在宁诺阶段。

## 后续编译

在 Codex 内置 LaTeX 编辑器中打开 `.tex` 文件即可继续编辑、预览和编译。也可使用现有 XeLaTeX 或 Tectonic：

```sh
xelatex Yang_Qixuan_CV_2026.tex
# 或
tectonic --keep-logs Yang_Qixuan_CV_2026.tex
```

源文件使用 TeX Gyre Heros 与 FandolHei 字体文件，避免依赖 Windows 的 Microsoft YaHei。字体随标准 TeX 发行版提供，Tectonic 可自动获取依赖。
