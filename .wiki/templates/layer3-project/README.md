# 项目 wiki 接入包（Layer: projects）

把本目录内容复制到**项目仓**，让项目内的 Agent 既能用项目知识，又能向上查团队 wiki。

## 接入步骤

1. 复制 `docs/wiki/` 到项目仓（路径保持一致，Agent 好找）；
2. 把 `AGENTS-snippet.md` 的内容合并进项目根的 `AGENTS.md` / `CLAUDE.md`；
3. 修改 snippet 中的 `WIKI_ROOT` 为团队 wiki 仓库在本机的路径（推荐固定克隆位置或 git submodule）；
4. 项目条目编号 `<项目缩写>-<序号>`（如 `TKB-001`），frontmatter 格式与团队库一致。

## 与团队 wiki 的分工

| 内容 | 放哪 |
|---|---|
| 只对本项目有意义（本项目部署参数、已知问题、接口约定） | 项目仓 `docs/wiki/` |
| 跨项目/换环境仍有用 | 团队 wiki 的 `通用/` 或 `基础设施/<子域>`：
  `python <WIKI_ROOT>/.wiki/scripts/wiki.py promote --file <项目仓条目> --to 通用 --keep-source`（源处留 stub） |
| 项目全貌（仓库/负责人/依赖） | 团队 wiki `项目/<项目名>/README.md` |
