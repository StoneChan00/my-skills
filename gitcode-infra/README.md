# gitcode-infra — GitCode 协作 Skill 集

从 [cann/cannbot-skills](https://gitcode.com/cann/cannbot-skills) `infra/` 目录整理发布的 GitCode 协作类 skill 镜像。

- **上游源仓**：`https://gitcode.com/cann/cannbot-skills`（`infra/` 目录）
- **同步基线**：commit `e7af33a264fe6d139d6298b4da6e3ac3602f8d81`（2026-10 快照）
- **许可**：CANN Open Software License 2.0（各文件版权头保留，详见文件头与上游 LICENSE）

## Skill 清单

| Skill | 说明 |
|-------|------|
| `gitcode-toolkit` | 共享基础库（**内部参考，不直接触发**）：GitCode API / Token / URL 解析 / 日志规范 / git 克隆检出 / diff 等参考文档 + 确定性脚本。其余 3 个 skill 均引用它 |
| `gitcode-issue-handler` | GitCode Issue 批量处理：分诊、首响答疑、责任人转交、复现修复、PR 交付与报告，含完整 Python 脚本流水线 |
| `gitcode-pr-handler` | 根据 PR 代码变更重新生成约定式提交标题 + 仓库模板描述，API 写回 PR |
| `gitcode-issue-gen` | 两条路径创建 Issue：PR → Issue 自动关联；手动交互式提单（模板/查重/草稿/确认） |

## ⚠️ 平级依赖约束

**4 个 skill 目录必须保持同级、不可拆散**：

```
gitcode-infra/
├── gitcode-toolkit/        ← 被下面 3 个引用
├── gitcode-issue-handler/
├── gitcode-pr-handler/
└── gitcode-issue-gen/
```

- 各 SKILL.md 通过 `../gitcode-toolkit/references/...` 相对链接引用共享文档
- `gitcode-issue-handler/scripts/` 下 8 个脚本通过 `../../gitcode-toolkit/scripts` 相对路径导入共享模块（`gitcode_client.py` 等）

单独拷走任何一个消费方 skill 都会导致引用断链。

## 与上游的差异（同步时需重放）

拷贝时对 4 处**仓库根相对路径**做了适配，其余文件与上游逐字节一致：

| 文件 | 差异 |
|------|------|
| `gitcode-toolkit/tests/test_preflight_contract.py` | `REPO_ROOT / "infra" / ...` 与 `read("infra/...")` 中的前缀 `infra` → `gitcode-infra` |
| `gitcode-issue-handler/tests/test_issue_handler_contract.py` | ① 新增 `import pytest`；② `test_repository_exposes_only_the_handler_public_name` 在仓库级注册文件（`marketplace.json` / `skill-registry.ts`，仅存在于上游源仓）缺失时 `pytest.skip`；③ `test_gitcode_issue_workflow_uses_pr_terminology` 对仓库级文档路径按存在性过滤 |
| `gitcode-toolkit/SKILL.md` | 「验证」章节命令路径 `infra/gitcode-toolkit/...` → `gitcode-infra/gitcode-toolkit/...`，并注明 skill 校验器在上游源仓 |
| `gitcode-issue-handler/SKILL.md` | 「修改验证」章节同上适配 |
| `gitcode-issue-handler/docs/installation-guide.md` | 两个指向上游仓库根 `docs/` 的相对链接改为上游绝对 URL |

注：`gitcode-issue-handler/README.md` 与 `docs/installation-guide.md` 中的安装命令（Plugin Marketplace / install-helper）指向上游源仓，保留原文未改。

## 从上游同步更新

```powershell
# 在 StoneChan00 工作区执行（PowerShell）
$src = "D:\2_Projects\github\StoneChan00\cannbot-skills\infra"
$dst = "D:\2_Projects\github\StoneChan00\my-skills\gitcode-infra"
foreach ($skill in @('gitcode-toolkit','gitcode-issue-handler','gitcode-pr-handler','gitcode-issue-gen')) {
    robocopy "$src\$skill" "$dst\$skill" /MIR /XD __pycache__ /NFL /NDL /NJH /NJS
}
# 然后按上表重放 4 处补丁，并更新本 README 的「同步基线」commit
```

同步后验证（my-skills 仓库根）：

```bash
python3 -m pytest -q gitcode-infra/gitcode-toolkit/tests gitcode-infra/gitcode-issue-handler/tests
```

## 运行依赖

- `gitcode-issue-handler` 确定性脚本：`pip install requests PyYAML`（见其 `requirements.txt`）
- Token：环境变量 `GITCODE_TOKEN`（各 skill 的 preflight 会检查）
- 平台：仅适用于 GitCode（gitcode.com）
