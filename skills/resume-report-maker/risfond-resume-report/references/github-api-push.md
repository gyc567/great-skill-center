# GitHub API 推送（git 直连超时环境下的替代方案）

当 git 直连 github.com 超时（如某些网络环境），可通过 GitHub REST API 推送文件更新。

## 推送单个文件

```python
import requests, base64

token = "ghp_xxx"  # Personal Access Token，从 https://github.com/settings/tokens 创建
headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}

# 1. 获取当前文件信息（获取 SHA）
url = "https://api.github.com/repos/{owner}/{repo}/contents/{path}"
r = requests.get(url, headers=headers)
sha = r.json()["sha"] if r.status_code == 200 else None

# 2. 读取本地文件内容
with open("本地文件.md", "r", encoding="utf-8") as f:
    content = f.read()

# 3. 推送更新
body = {
    "message": "Update message",
    "content": base64.b64encode(content.encode("utf-8")).decode("utf-8"),
    "sha": sha,          # 更新文件需要传旧SHA
    "branch": "main"
}
r = requests.put(url, headers=headers, json=body)
```

## 关键要点

- **Token 权限**：至少需要 `repo` scope（私有仓库）或 `public_repo` scope（公开仓库）
- **文件路径**：如果是子目录下文件，路径要包含目录名，如 `risfond-resume-report/SKILL.md`
- **内容编码**：必须用 base64 编码
- **SHA 必须传**：更新已有文件时必须传 sha，新增文件不传
- **分支**：指定 `branch: "main"`，不传则默认主分支

## 错误处理

| HTTP状态 | 含义 | 处理 |
|---------|------|------|
| 404 | 文件不存在（路径错误或仓库不存在） | 检查路径，去掉 sha 用 PUT 新增 |
| 409 | SHA 冲突（文件已被他人更新） | 重新 GET 获取最新 SHA |
| 422 | 内容验证失败 | 检查 base64 编码是否正确 |
| 429 | 请求过频 | 等待后重试 |

## 获取仓库文件列表

```python
r = requests.get("https://api.github.com/repos/{owner}/{repo}/contents/", headers=headers)
items = r.json()
for item in items:
    print(f"{'[DIR]' if item['type']=='dir' else '[FILE]'} {item['name']}")
```

## 读取文件内容（无需下载）

```python
r = requests.get("https://api.github.com/repos/{owner}/{repo}/contents/{path}", headers=headers)
data = r.json()
content = base64.b64decode(data["content"]).decode("utf-8")
```
