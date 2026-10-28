# Agent Engineering Suite

[English](README.md)

把澄清决策、Spec 推进、History、架构深化、代码审查、文档维护、成熟度评分与 Roadmap 跟踪放在一个可复用的研发套件里。

**同一份核心源码，两种交付形式；Skill 与 Codex 插件都支持单模块和整套安装。** 单模块不依赖编排入口，不绑定私人账号。

## 安装 Codex 插件

以下固定版本的远端 Git 安装路径已在 Linux、Codex CLI **0.163.0** 实测。这是已观测版本，不代表最低版本或所有平台兼容。

```sh
codex plugin marketplace add https://github.com/hpoenixf/agent-engineering-suite.git --ref 3b515de2f30e25b1e0757243f3ce4d1be19b00b0
# 单模块：
codex plugin add agent-engineering-suite-history@agent-engineering-suite
# 或整套（二选一，不要重复安装）：
codex plugin add agent-engineering-suite@agent-engineering-suite
```

[单模块／整套独立 Skill 安装与本地构建](docs/installation.md) · [远端安装回执](docs/verification/native-remote-install.json)

先看英文首页的模块表、[安装方式](docs/installation.md)、[兼容与验证边界](docs/compatibility.md)和[来源记录](docs/provenance.md)。Node 26.11.1 下运行 `node scripts/build.mjs`、`node scripts/validate.mjs` 与 `node --test tests/*.test.mjs`。无需安装 npm 运行依赖。

原 Spec/History 工具保留；成熟度默认通用量表，另提供通用改编的 24/28/16 维度离线计算器（新量表，不与历史评分比较），但不携带私人评分。Roadmap 独立安装，不凭评分自动完成任务。验收/发布/交接暂为明确边界的模板，不冒充自动化执行器。

不自动推送 main、不发起付费模型、不永久删除未知文件、不改变账号权限。包校验通过不等于原生安装通过，更不等于真实产品验收。
