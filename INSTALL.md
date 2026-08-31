# 安装与升级

当前公开版本为 `v0.5.0-preview`，Skill 技术名称为 `research-decision-skill`。

## 让 Codex 安装

直接发送：

```text
请从 https://github.com/Odyphus/research-decision-skill 安装这个 Skill。
```

## 手动安装

把仓库克隆到当前 Codex 的 Skills 目录：

```powershell
$skillRoot = if ($env:CODEX_HOME) { Join-Path $env:CODEX_HOME 'skills' } else { Join-Path $HOME '.codex\skills' }
git clone https://github.com/Odyphus/research-decision-skill.git (Join-Path $skillRoot 'research-decision-skill')
```

安装完成后开启一个新任务，再显式调用：

```text
$research-decision-skill 帮我判断当前最关键的科研决定。
```

## 从旧版 Preview 升级

- 不要让 `research-exploration` 与 `research-decision-skill` 两个 Skill 同时处于活动 Skills 目录，否则可能重复触发。
- 先备份旧 Skill，再安装新目录；确认新版本可用后再停用旧目录。
- 新项目默认把记录写入 `.research-decision/`。
- 如果研究项目中只有旧版 `.research-exploration/`，新版本会继续原地使用，不会自动改名或迁移。
- 如果两个状态目录同时存在，新版本会停止写入并要求人工确认，避免覆盖历史。

## 卸载

关闭正在使用该 Skill 的任务后，移除 Skills 目录中的 `research-decision-skill` 文件夹即可。研究项目里的 `.research-decision/` 是项目记录，不会随 Skill 一起自动删除。

