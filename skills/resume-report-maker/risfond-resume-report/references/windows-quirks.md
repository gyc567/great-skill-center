# Windows 环境生成脚本注意事项

## 1. python-docx 文件锁定
生成 .docx 后 Word 会锁定文件。如需重新生成（修改后覆盖），必须先关闭 Word 或杀掉进程：
```powershell
Get-Process WINWORD -ErrorAction SilentlyContinue | Stop-Process -Force
```
或直接换用新文件名（如加上版本号）避免冲突。

## 2. hermes.bat 路径含空格
桌面版安装路径 `D:\Hermes Agent CN Desktop\` 含空格，直接执行不行。
**正确方式**（PowerShell）：
```powershell
& "D:\Hermes Agent CN Desktop\data\desktop-bin\hermes.bat" <command>
```
**错误方式**（不要用）：
```powershell
cmd /c "D:\Hermes Agent CN Desktop\...\hermes.bat"   # 空格被截断
D:\Hermes Agent CN Desktop\...\hermes.bat            # 空格被截断
```

## 3. 旧版 .doc 读取 RPC 错误
Word COM 读取 .doc 文件时可能报 `0x800706BE`（远程过程调用失败）。
- 重启：杀掉所有 WINWORD 进程再试
- 换文件：某些 .doc 文件本身有损坏

## 4. TreatControlCAsInput 警告
PowerShell 每次执行 python 脚本都输出：
```
设置"TreatControlCAsInput"时发生异常:"句柄无效。"
```
**无害**，可忽略。这是 Hermes TUI 环境下的终端兼容问题。
