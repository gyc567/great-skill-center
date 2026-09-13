# Python 环境搭建与离线依赖包教程

> 本 skill（office-file-process）的 Python 依赖都是轻依赖：`openpyxl`、`pandas`、`defusedxml`、`lxml`、`Pillow`、`markitdown[pptx,xlsx]`。
>
> 本文档教你三件事：**① 在新机器装 Python → ② 在有网的机器打包依赖 wheels → ③ 在无网机器离线安装**。
>
> 适用 Windows。

---

## 1. 安装 Python

### 1.1 下载

官方地址：https://www.python.org/downloads/windows/

选 **Python 3.13+ 的 Windows installer (64-bit)**，例如 `python-3.13.x-amd64.exe`。

> 版本务必与"打包依赖"那台机器一致（第 2 步），否则含二进制扩展的包（pandas/lxml/Pillow）离线装不上。都用 3.13 64 位最省心。

### 1.2 安装

1. 双击安装包，第一个界面**务必勾选 "Add python.exe to PATH"**（最底部的复选框），再点 "Install Now"；
   - 不勾的话装完 `python` 命令找不到，后面所有步骤都得写全路径 `C:\Users\<你>\AppData\Local\Programs\Python\Python313\python.exe`
2. 装完不点 "Disable path length limit" 也可以，但建议点一下（避免深目录路径超长问题）。

### 1.3 验证

打开**新的** cmd 或 PowerShell（PATH 要新开窗口才生效），执行：

```powershell
python --version          # 应输出 Python 3.13.x
python -m pip --version   # 应输出 pip 版本和 python 路径
```

两个都有正常输出即安装成功。

---

## 2. 打包依赖（在有网的机器上做）

在有网、且装了**相同版本 Python** 的机器上执行：

### 2.1 建一个打包目录

```powershell
mkdir D:\skill-py-deps
cd D:\skill-py-deps
```

### 2.2 下载全部 wheels

在 powershell 里粘贴执行：

```powershell
python -m pip download -d wheels --only-binary :all: defusedxml lxml openpyxl pandas Pillow "markitdown[pptx,xlsx]"
```

- `--only-binary :all:` 强制只下 wheel（预编译二进制），不源码编译——离线安装时无需编译器
- 下载完 `wheels\` 目录约 **34 个文件、65MB**，连同下面两个文件一起拷贝给目标机器

### 2.3 生成依赖清单（供离线安装）

**不要用 `pip freeze`**——它列出的是打包机全局 Python 里装的*所有*包，和 wheels 里下载的这套对不上，离线安装时会报缺包。

清单直接**从 wheels 目录生成**（wheel 文件名就是 `包名-版本-平台.whl`，取前两段即 `包名==版本`）：

```powershell
Get-ChildItem wheels -Filter *.whl | ForEach-Object { ($_.BaseName -split '-')[0..1] -join '==' } | Set-Content requirements.txt
```

生成的 requirements.txt 正好 34 行、与 wheels 一一对应（markitdown 的 extras 如 `markitdown==0.1.7` 写法照用即可，pptx/xlsx 的附加依赖已在 wheels 里）。

### 2.4 最终交给目标机器的目录

```
skill-py-deps/
├── wheels/           # 34 个 .whl 文件（约 65MB）
└── requirements.txt  # 依赖清单（从 wheels 生成，一一对应）
```

整个目录用 U 盘 / 内网共享 / 压缩包传给目标机器即可。

---

## 3. 离线安装（在无网的目标机器上）

### 3.1 前提

- 已按第 1 节装好 Python（版本与打包机一致）
- 拿到了第 2 节的 `skill-py-deps` 目录，拷到目标机任意位置（如 `D:\skill-py-deps`）

### 3.2 装到默认环境（不推荐）

```powershell
cd D:\skill-py-deps
python -m pip install --no-index --find-links wheels -r requirements.txt
```

- `--no-index` 不访问 PyPI，完全离线
- `--find-links wheels` 从本地 wheels 目录找包
- requirements.txt 由 wheels 生成、一一对应，不会报缺包

### 3.3 装到虚拟环境（推荐）

不污染全局 Python，多个项目互不干扰：

```powershell
cd D:\skill-py-deps
python -m venv D:\path\skill-py-venv
D:\path\skill-py-venv\Scripts\python.exe -m pip install --no-index --find-links wheels -r requirements.txt
```

直接丢给 AI：

```Plain
python我已装好，请帮我离线安装 skill-py-deps 目录下的依赖到虚拟环境（D:\path\skill-py-venv）
```

### 3.4 验证

激活环境（powershell）：

```
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
D:\path\skill-py-venv\Scripts\Activate.ps1
```

验证：

```powershell
pip list
# 或者下面的
python -c "import defusedxml, lxml, openpyxl, pandas, PIL, markitdown; print('ALL OK')"
```

输出 `ALL OK` 即装齐。再抽查 skill 实际用到的入口：

```powershell
python -c "from markitdown import MarkItDown; print('markitdown OK')"
```

---

## 常见问题

| 现象 | 原因与解决 |
|---|---|
| 离线安装报 `ERROR: Could not find a version...` | wheels 与目标机 Python 版本/位数不一致（如打包机 3.13、目标机 3.12）。回第 1 节对齐版本，或用目标机版本重新执行第 2 步 |
| `python` 命令找不到 | 安装时没勾 "Add python.exe to PATH"。重跑安装包勾上，或所有命令改用 python.exe 全路径 |
| pip 提示版本旧、离线装失败 | 先离线升级 pip：把 `pip-xxx.whl` 一并放进 wheels（在有网机器 `pip download pip`），先装它再装其余 |
| markitdown 安装项报错解析 `markitdown[pptx,xlsx]` | 仅手动直接安装时遇到：PowerShell 下加引号 `python -m pip install ... "markitdown[pptx,xlsx]"`；用 requirements.txt 文件方式（第 2.3 节）则无此问题 |
| 装完 import 报 DLL 缺失 | 目标机缺 VC++ 运行库（pandas/lxml 依赖）。装 [Microsoft VC++ Redistributable 2015-2022 x64](https://aka.ms/vs/17/release/vc_redist.x64.exe)（可下载后离线传过去装） |
