# Dreamie Design 项目协作

本目录是独立Git仓库，技能入口只有根目录 `SKILL.md`。不要在父目录初始化Git，也不要把参考专题重新变成多个自动发现的技能。

## 更新知识

- 先读 `CONTRIBUTING.md` 与相关专题的 `guide.md`、`methods.md`、`sources.md`；按需读取，避免默认展开全部专题。
- 新材料明确实际阅读页码、图版、来源层次、使用条件、反例与验证；不把目录/OCR处理完成等同全文图像精读，不抄录整书或成套素材。
- 书内经验、现代执行补充与本次综合分别标记。保留来源冲突、失效页及未验证项；有证据再升级结论。
- 修改与反馈有关的最小范围；不把一个作品、一次偏好或某个平台参数变成所有设计的硬规则。

## 本地验证与提交

```sh
python scripts/check_skill.py
python -m unittest discover -s tests -v
python scripts/check_skill.py --package dist/dreamie-design.zip
git diff --check
git status --short
git diff
```

文档方法的实质变化再做相关应用情境；视觉成品实际渲染和查看。小步修改、验证、看差异、提交；不覆盖已有未提交工作。推送、公开仓库、发布版本与其他外部变更依本次用户授权，不由本文件自动授权。

## 发布文件

不提交个人路径、私人邮箱、密钥、真实环境配置、PDF、扫描图、全量OCR和不具备分发条件的素材。公开书目作者姓名作为必要署名保留。生成包放 `dist/` 并保持忽略，打包脚本只包含技能运行所需文档。

自动检查覆盖有限模式；发布前仍检查差异、暂存文件与ZIP清单，核对素材权限、引用和未解决项。
