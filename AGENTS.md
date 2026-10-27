# Dreamie Design 项目协作

本目录是独立 Git 仓库，技能入口只有根目录 `SKILL.md`。不要在父目录初始化 Git，也不要把参考专题重新变成多个自动发现的技能。

## 更新知识

- 先读 `CONTRIBUTING.md` 与相关专题的 `guide.md`、`methods.md`、`sources.md`；按任务读取。
- 新材料明确实际查看范围、证据层次、适用条件、反例与验证。非公开研究记录留在本机。
- 区分可见观察、分析解释、设计提议和待验证项；事实性主张须有证据。
- 修改与反馈有关的最小范围；不把一次偏好或某个平台参数变成通用硬规则。

## 本地验证与提交

```sh
python scripts/check_skill.py
python -m unittest discover -s tests -v
python scripts/check_skill.py --package dist/dreamie-design.zip
git diff --check
git status --short
git diff
```

方法的实质变化再做相关应用情境；视觉成品实际打开查看。小步修改、验证、看差异、提交；不覆盖已有未提交工作。推送、公开仓库、发布版本等依用户本次授权。

## 发布文件

不提交个人路径、私人邮箱、密钥、真实环境配置、未获准的源资料和成套素材。图像保留必要的素材说明与使用条件。生成包放 `dist/` 并保持忽略。

自动检查覆盖有限模式；发布前仍检查差异、暂存文件与 ZIP 清单，核对素材权限和未解决项。
