# Dreamie Design

一个持续积累的视觉设计 Skill：把版式、配色、中国传统色、纹样、艺术分析与 AI 风格设计组织在一个入口中，按任务读取相关方法。

## 使用

安装后以 `$dreamie-design` 调用，也可以直接说明设计目标、用途、真实内容和参考材料。

```text
用 $dreamie-design 改进这张文化展海报：保留品牌色，分别考虑手机和A3打印。
用 $dreamie-design 给茶罐设计传统色与连续纹样，说明来源和实物验证条件。
用 $dreamie-design 分析参考画面的构图，再迁移到我的读书活动。
用 $dreamie-design 将这本新书读到的部分补充到现有配色专题。
```

技能入口：[SKILL.md](SKILL.md)。它按任务路由到六类参考，主文件不要求一次加载所有专题，也不依赖原先分开的六个技能。

## 安装包与检查

仓库根目录就是一个名为 `dreamie-design` 的技能目录。把这个目录放到你的代理工具支持的个人技能目录，保留 `SKILL.md` 与 `references/` 的相对结构。具体加载方式服从所用工具。

用 Python 3.11 或更高版本在仓库根目录运行，无第三方Python依赖：

```sh
python scripts/check_skill.py
python -m unittest discover -s tests -v
python scripts/check_skill.py --package dist/dreamie-design.zip
```

ZIP 内为 `dreamie-design/` 单目录；包含技能及其所需文档，不含Git历史、测试缓存、私有路径、原书或OCR。

## 持续完善

每次新增书籍、设计案例或失败反馈，按 `CONTRIBUTING.md` 记录实际阅读范围、来源、决策变化与反例。维护只更新相关专题；显著的新能力通过真实任务验证后再进入技能。`CHANGELOG.md` 记录版本与验证状态，项目 `AGENTS.md` 为后续协作者保留约定。

初始版基于12本书的方法提炼，正文分段阅读、关键图版抽查。原书11处失效页、OCR限制与未验证项均在[阅读范围](references/reading-scope.md)中保留。此前六类方法的情境测试不等于任意成品已经通过视觉或生产验收。

## 来源与使用范围

仓库保存原创归纳、流程与书目定位；不随包分发图书、原图、扫描件、附赠素材和成套色卡。原书及第三方素材的权利归各自权利人。本仓库尚未指定开源许可证，不将公开可读与任意商业复制等同。
