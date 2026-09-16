# GIT 持久化手册（跨平台终极形态）

目标：框架"唯一正本"住在私有 git 仓库；任何新环境一条命令还原生产线。

## 一、一次性建库推送（在有推送权限的环境执行，例如本工作区或你的电脑）

1. 在 GitHub / Gitee / GitLab 新建**私有**仓库（Private），取得 URL（形如
   `https://github.com/<you>/codex-pet-framework.git`）。
2. 在本工作区执行（token 走环境变量，**不要粘贴进聊天/命令行明文**）：

   ```bash
   cd /home/user
   git init -b main
   git add -A                      # .gitignore 已排除 uploads/ 与缓存
   git commit -m "Codex Pet sprite framework v1 (engine + pets + specs + docs)"
   git remote add origin <仓库URL>
   git push -u origin main         # 凭据用 credential helper 或环境变量注入
   git tag v1-spec && git push --tags   # 可选：给官方 v1 规格打标签
   ```

   凭据安全建议：`git config credential.helper store` 仅限私有受信机器；
   或每次用 `https://<user>:$GIT_TOKEN@...` 形式且 token 存 `~/.config/env` 等受权限保护文件。

## 二、任何新环境初始化（30 秒）

**种子 vs 初始化器**：`init_workspace.sh` 住在仓库/zip 内，空白环境先落"种子"（一条外部命令或一次 zip 附件），脚本现身后接管其余步骤。

| 环境能力 | 种子命令 | 接管命令 |
|---|---|---|
| 有 git + 网络 | `git clone --depth 1 <url> && cd <目录>` | `bash init_workspace.sh --here` |
| 仅网络 | `curl -L -H "Authorization: Bearer $GIT_TOKEN" https://codeload.github.com/<you>/<repo>/zip/refs/heads/main -o fw.zip && unzip fw.zip && cd <解压目录>` | `bash init_workspace.sh --here` |
| 无网络 | 首会话附件 `codex_pet_framework.zip` | `bash init_workspace.sh --zip <zip>` |
| 有 git 想一步到位 | — | `bash init_workspace.sh <url>`（内部=clone+接管） |

接管步骤（自动）：`sha256sum -c MANIFEST.sha256` → 依赖检查（缺则 pip install）
→ 冒烟构建 blob_demo 并确认 `VALIDATION OK` → 打印 READY。
随后按 `BOOTSTRAP.md` §1–§4 生产新宠物。

## 三、日常同步与升级

- 框架在任何环境改进后：`git add -A && git commit -m "..." && git push`；
- 其他环境开工前先 `git pull --ff-only`（把 BOOTSTRAP §0 自检换成 pull + 自检）；
- 大规格变更打新 tag（如 `v2-spec`），spec JSON 与 tag 对应，保证历史产物可复现。

## 四、边界与回退

| 环境类型 | 方案 |
|---|---|
| 有 shell + 网络 | `init_workspace.sh <url>`（本手册主路径） |
| 有 shell 无网络 | `init_workspace.sh --zip <zip>`（zip 随人身/云盘携带） |
| 无 shell（纯聊天 API） | system prompt 内嵌 `BOOTSTRAP.md`（~2k token）+ 附件 `pets/blob_template.py`（~3k） |
| 同账号工作区持久 | 无需 git：BOOTSTRAP §0 自检后直接开工 |

## 五、为什么这是"终极形态"

- **平台无关**：正本不依赖任何沙箱/账号存续；沙箱被回收也不丢；
- **零附件成本**：clone 26KB ≈ 0.2k token 命令输出，对比每次上传 zip/重读框架；
- **版本化**：历史、回滚、tag 与 spec 对应，"字节级可复现"从单环境承诺升级为跨环境承诺；
- **多点同步**：框架升级 push 一次，所有环境 pull 即齐。
