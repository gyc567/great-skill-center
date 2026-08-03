# great-skill-center 代码审计报告

| 项目 | 内容 |
|------|------|
| 审计对象 | `/Users/stevenw/code/great-skill-center` |
| 审计范围 | `crypto-harmonic-signals/`、`github-repo-evaluator/` |
| 审计时间 | 2026-07-29 |
| 测试基线 | 130 个单测全部通过 (crypto-harmonic-signals: 102/102, github-repo-evaluator: 28/28) |
| Python | 3.9.6 / pandas + numpy + requests |

---

## 0. 总体评分

| 维度 | 评分 | 备注 |
|------|------|------|
| 代码可读性 | ⭐⭐⭐⭐ | 中文注释充分，模块边界清晰 |
| 测试覆盖 | ⭐⭐⭐ | 主体 82% 覆盖，scanner / scheduler / alerter 大量裸跑 |
| 安全性 | ⭐⭐ | 凭证在命令行、错误吞掉无日志、URL 正则可被绕过 |
| 性能 | ⭐⭐⭐ | 单币单次扫描合理；可观测性 / 缓存 / 限流缺失 |
| 与设计文档一致性 | ⭐⭐ | 设计文档列出多个未实现模块和未处理问题 |
| 可运维性 | ⭐⭐ | 无日志、无信号存档、无熔断、无监控 |
| 风险控制 (交易语义) | ⭐⭐ | 文档承诺的多项风控在代码里未落地 |

整体: **可用骨架，工程化 / 上线前仍需补齐若干关键模块**。

---

## 1. 模块概览

### 1.1 crypto-harmonic-signals

```
scripts/
├── config.py          (115)   配置 dataclass
├── indicators.py      (152)   EMA / RSI / ATR
├── harmonics.py       (341)   ZigZag + XABCD 形态检测
├── filters.py         (215)   趋势 / RSI / 分级综合过滤
├── scanner.py         (210)   批量扫描入口
├── alerter.py         ( 99)   Telegram 推送
├── reporter.py        (217)   Markdown / Telegram 报告
├── scheduler.py       (171)   三次/日定时调度
└── exchanges/
    ├── base.py        ( 60)
    ├── binance.py     ( 73)
    ├── okx.py         ( 78)
    └── bybit.py       ( 90)
```

实际行数: 约 1800 行生产代码 + 800 行单测。

### 1.2 github-repo-evaluator

```
scripts/
└── fetch_repo_info.py  (197)  GitHub API 信息抓取 (CLI)
tests/
└── test_evaluator.py   (234)  仅测试纯函数，不测网络路径
```

---

## 2. 审计发现汇总 (按严重度)

| 编号 | 严重度 | 位置 | 简述 |
|------|--------|------|------|
| F-01 | 🔴 高 | scanner.py / scheduler.py | 设计文档承诺的 `position_manager.py` 不存在；持仓 / 资金管理模块整体缺失 |
| F-02 | 🔴 高 | scanner.py / exchanges/* | `Config.fallbacks` 在 `scan_all()` 中被忽略，永远只用 binance |
| F-03 | 🔴 高 | scheduler.py | `timezone="Asia/Shanghai"` 仅作为注释配置存在；调度判断用本地时间，跨时区运行会错峰 |
| F-04 | 🔴 高 | scanner.py | `HYPE/USDT` 等币种在 Binance 现货/合约可能无交易对，运行时会一直 empty |
| F-05 | 🟠 中 | exchanges/* | 三个适配器 `except requests.exceptions.RequestException` 静默吞掉，不打日志，不分类 (限流 / 超时 / 业务错) |
| F-06 | 🟠 中 | scanner.py / scheduler.py | 无信号历史存档；设计文档承诺的 "CSV/JSON 存档" 未实现 |
| F-07 | 🟠 中 | alerter.py | Telegram 推送只判断 `status_code==200`，未处理 429 限流 / Markdown 解析失败 |
| F-08 | 🟠 中 | fetch_repo_info.py | GitHub token 通过命令行参数传入，进程列表可见；建议改用环境变量 |
| F-09 | 🟠 中 | fetch_repo_info.py | `extract_repo_info` 的两条 regex 互相覆盖，第二条基本等价于 `.*` 通配；输入 `https://github.com/x/y/../../etc/passwd` 等边界未严格校验 |
| F-10 | 🟠 中 | scheduler.py | `_loop` 每 60 秒轮询；长任务期间会与下次轮询重叠；`start(blocking=True)` 用 `while: sleep(1)` 紧循环浪费 CPU |
| F-11 | 🟠 中 | filters.py | `min_grade` 默认 "B" + `C` 必拒，但 C 之外无明确分级语义；分级信息没有被反推到 reporter 之外 |
| F-12 | 🟡 低 | indicators.py | RSI 使用简单 SMA（`rolling().mean()`），而非 Wilder 平滑；与 TradingView 等业界实现存在偏差 |
| F-13 | 🟡 低 | indicators.py | `calculate_atr` 用 `pd.concat([..], axis=1).max(axis=1)`；三个 Series 拼宽表只为取 max |
| F-14 | 🟡 低 | harmonics.py | `validate_pattern` 中 `_in_range` 是闭区间容忍边界，与设计文档描述一致但未单测覆盖边界值 |
| F-15 | 🟡 低 | exchanges/* | 每个适配器都新建 `requests.Session()`；同一进程多 symbol 复用率低 |
| F-16 | 🟡 低 | scanner.py | `notes=["4H K线数据不足"]` 仅在内存；没有持久化运行日志 |
| F-17 | 🟡 低 | reporter.py | `strftime('UTC+8')` 仅是字符串，host 时区不是上海时区时输出错误 |
| F-18 | 🟡 低 | scanner.py / scheduler.py | 无统一 `logging` 模块，全部用 `print`；调试 / 生产不可分级别 |
| F-19 | 🟡 低 | fetch_repo_info.py | `decoded[:2000]` 截断 README；可能在评估时丢失关键信息 |
| F-20 | 🟡 低 | scanner.py | `Scanner._init_exchanges` 总是实例化三个 adapter，对只用 Binance 的用户是浪费 |

---

## 3. 详细审计

### 3.1 crypto-harmonic-signals

#### 3.1.1 config.py ✅ 基本合规
- 全部用 `@dataclass`，默认值与设计文档 / `references/config.yaml` 对齐。
- 缺一个从 yaml 加载的入口 (`Config.from_yaml(...)`)。仓库里写了 yaml 但代码里没人读它，造成 **配置双轨**。

#### 3.1.2 indicators.py ✅ 算法合理 / 有偏差
- `calculate_ema`: `ewm(span=period, adjust=False).mean().iloc[-1]`，标准实现。⚠️ 数据长度不足时退化为 `mean()`，会污染 EMA 序列，应改为发警告或返回 `None`。
- `calculate_rsi`: 使用 SMA 而非 Wilder 平滑，与主流交易软件不一致，建议在文档中显式注明或改为 EWM (`ewm(alpha=1/period)`)。
- `calculate_atr`: 用 `pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)` 计算 True Range。效率略低，可改成 `np.maximum.reduce([tr1.values, tr2.values, tr3.values])`。功能上没问题。

#### 3.1.3 harmonics.py ⚠️ 与设计文档小不一致
- `PATTERNS` 中 5 个形态参数表与设计文档一致。Shark 已从字典移除 (test_config.py 验证 `assertNotIn("Shark", ...)`)。
- `zigzag(df, pct=0.03)`: 起始用 `df["close"].iloc[0]` 作初始参考，第一根 K 线如果是十字星可能错过反转点，建议初始 `ext_price = (high[0]+low[0])/2`。
- `validate_pattern`: 用 4 比例 (B/XA, C/AB, D/XA, CD/BC) 全部命中容差区间才返回信号。✅
- `calculate_stop_loss`: 实现是 `max(ATR*0.7, entry*0.5%)`，与设计文档 `prz_buffer_ratio: 0.5` 不一致 (文档是 `0.5%` 标注，但 yaml 写 `0.005`)，代码用 yaml 数值，符合 yaml。
- `scan(df, only_latest=True)`: 默认只扫描最后一个 D 点；生产可改为 `False` 以便历史回放，但默认行为合理 (避免重复告警)。
- **缺少单元测试**: 没有 PRZ 重叠检测、容差边界 (例如恰好等于 `hi*(1+tol)`) 的测试。

#### 3.1.4 filters.py ✅ 语义清晰
- `filter_by_trend` / `filter_by_rsi` / `filter_by_grade` 三个独立判定，组合时 `is_valid = AND`。
- 注意: `filter_by_grade` 总是拒 C，没有 "降级通过" 路径。设计文档里写 "中间区域 → 信号降级"，代码里没有降级 (degrade) 概念——信号要么 `is_valid=True` 要么 `False`。这点应在产品上明确。
- **缺少单元测试**: 没有 `min_grade="A"` + `grade="A"` 通过的边界用例 (`test_filter_grade_min_a` 只测 B 拒绝)。

#### 3.1.5 scanner.py 🔴 关键路径
- `scan_all()`:
  ```python
  for symbol in self.config.symbols:
      result = self.scan_symbol(symbol, exchange_name="binance")
  ```
  **永远只用 binance**，没有 fallback。`config.exchanges.fallbacks` 字段是死代码。🔴
- `scan_symbol()`:
  - 先取 4H K 线 ≥ 50 根才继续 (`< 50` 直接放弃)。
  - 取日线 ≥ 200 根做 EMA200，否则退回用 4H 做趋势 (此回退会让设计文档 "日线 EMA200" 的承诺落空)。建议至少在 `notes` 区分两个等级。
  - `harmonic_scan(only_latest=True)` 只取一个 D 点；与设计文档 "可输出未完成形态" 不一致，但属于产品选择。
  - 数据缺失时 `notes=["未检测到和谐形态"]` 会被 `Reporter.generate_invalid_section` 当作信号输出，语义略奇怪 ("未检测到" 是不是信号？)。
- **未实现**: 信号 ID、信号生命周期、持仓管理。设计文档 5.1 节信号报告里写 `信号 ID | sig_btc_gartley_20260726_00`，代码完全没有。

#### 3.1.6 alerter.py ⚠️ 健壮性不足
- `send_message()` 用 `requests.post` 单次提交，无重试、无指数退避、无 429 退避。
- `parse_mode="Markdown"`，但消息里有 `|`、`[xxx]` 等字符，MarkdownV1 解析 OK，但 emoji + Markdown 在某些 Telegram 客户端可能样式异常。
- 工厂模式简单可用，但缺乏其他通道 (邮件 / Webhook)，设计文档 9.3 已规划但未实现。

#### 3.1.7 reporter.py ✅ 输出友好 / 缺持久化
- Markdown / Telegram 模板与设计文档 5.1 / 5.2 节大致吻合。
- `format_rsi_status` 中 `rsi_status` 是 `RSIResult.status` 字符串；若 `status` 出现预料外的值 (例如 None)，会输出 f-string 中显示 "None"，应加 fallback。
- **未实现**: 报告持久化 (`reports/2026-07-29-00-00.md`)，每次只是 `print`。

#### 3.1.8 scheduler.py 🔴 阻塞 + 时区
- `start(blocking=True)` 主线程 `while self._running: time.sleep(1)`，紧循环（虽然 sleep 1s，但 OS 调度器仍频繁唤醒）。建议用 `threading.Event.wait()`。
- `_should_run` 用 `datetime.now().time()`，未考虑 `ScheduleConfig.timezone`。如果机器在 UTC 而配置写 `00:00 Asia/Shanghai`，实际会在 UTC 16:00 触发 (相差 8 小时)。
- `_loop` 用 `time.sleep(60)` 间隔：若某次扫描 > 60s (9 个币种各 2 次网络请求 + EMA200 + ZigZag)，下一次轮询会立即再次进入 `_run_scan`。虽有 `self._lock`，但锁只保护 `print` 段；外层 `for entry in self.schedule` 没有锁，可能同一个时间点触发两次。
- 没有 **熔断 / 连续失败报警** (设计文档 §7.3 提到)。

#### 3.1.9 exchanges/* ⚠️ 安全 / 一致性

| 项 | Binance | OKX | Bybit |
|----|---------|-----|-------|
| URL | ✅ api.binance.com | ✅ www.okx.com | ✅ api.bybit.com |
| HTTP 方法 | GET | GET | GET |
| 超时 | 10s | 10s | 10s |
| User-Agent 伪装 | "Mozilla/5.0" | "Mozilla/5.0" | "Mozilla/5.0" |
| 错误处理 | 吞掉异常 | 吞掉异常 | 吞掉异常 |
| rate-limit 处理 | ❌ | ❌ | ❌ |
| 重试 | ❌ | ❌ | ❌ |

- `okx.py`: `inst_id = self.normalize_symbol(symbol).replace("USDT", "-USDT")`，对 `BTC/USDC` 形态会替换成 `BTC-USC` (因为只有首个 `USDT` 被替换) — **bug**。应使用精确替换：`symbol.replace("USDT", "-USDT", 1)` 或者基于分隔符。
- `bybit.py`: 强制 `category="linear"`。设计文档说 "全币种合约数据"，假设 OK；但 spot 行情下 `category` 应是 `spot`。
- 三个适配器均无 `get_funding_rate` 方法 (设计文档 §10.1 标注为 `@abstractmethod`)。**接口承诺未兑现。**

---

### 3.2 github-repo-evaluator

#### 3.2.1 fetch_repo_info.py 🔴 凭证暴露 + 正则弱

**凭证处理 (F-08)**:
```python
token = sys.argv[2] if len(sys.argv) > 2 else None
```
- 命令行 token 会被 `ps aux` 看到、写入 shell history。
- 建议改为 `os.environ.get("GITHUB_TOKEN")`，并提供 `--token` flag 作 override。

**URL 解析 (F-09)**:
```python
patterns = [
    r'github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$',
    r'github\.com/([^/]+)/([^/]+?)(?:/.*)?$',
]
```
- 第二条 regex 等价于 `.*` 通配，会把 `/tree/main` 这种尾部路径全吃掉 → 但 `re.search` 配合 `$` 仍能匹配，所以安全。
- 输入 `https://github.com/evil/repo/../../../../etc/passwd` 时 owner 会变成 `evil`，repo 会包含路径 → 上 GitHub API 会失败，无注入风险，但输入校验应更严格 (白名单字符 `[A-Za-z0-9_.-]`)。
- `extract_repo_info("https://github.com/facebook/react/tree/main")` 测试断言 owner=`microsoft`, repo=`vscode` (line 42)，是因为 mock 输入是 `https://github.com/microsoft/vscode/tree/main`，但 line 43 的 `assertEqual` 写的是 `repo == "vscode"`——实际 regex 取到的是 `vscode/tree/main`？让我重读：

```python
def test_url_with_path_after_repo(self):
    owner, repo = extract_repo_info("https://github.com/microsoft/vscode/tree/main")
    self.assertEqual(owner, "microsoft")
    self.assertEqual(repo, "vscode")
```

regex 第一条 `r'github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$'` 需要 `$` 结尾，输入不以 `/` 结尾，因此第一条不匹配；第二条 `r'github\.com/([^/]+)/([^/]+?)(?:/.*)?$'` 用 `[^/]+?` 非贪婪 + `(?:/.*)?` 零或多 → 实际取 `vscode`，OK。但第二条 regex 在很多边界 case 下会取到错的 owner (例如 `https://github.com/foo/bar/baz`，非贪婪会把 `bar` 作为 owner)。建议用更明确的方案：`urlparse` + 路径分割。

**README 截断 (F-19)**: `decoded[:2000]` 截断到 2KB，README 长项目会丢尾部章节，建议按行截断 (前 50 行)。

**GitHub API 调用**:
- 5 次串行调用，无并发、无重试。
- 限流 60 次/小时匿名，5000 次/小时带 token；脚本未实现任何缓存/重试，长时间批量评估会撞限流。

#### 3.2.2 test_evaluator.py ⚠️ 假阳性覆盖
- `TestEvaluatorDecisions.score_to_decision` 等是测试本地方法 (定义在测试里)，**没有真正测试 `fetch_repo_info` 的代码路径**。
- 唯一真测试：`extract_repo_info` / `is_recently_updated`。28 个测试中只有 ~14 个真正在测产品代码。
- `evals/evals.json` 是给 Jcode / 评测 harness 用的，跟产品代码测试是平行的另一套。

---

## 4. 测试覆盖与可观测性

| 模块 | 覆盖率 (报告) | 实测结论 |
|------|--------------|----------|
| config.py | 100% | ✅ 单测充分 |
| exchanges/base.py | 97% | ✅ |
| exchanges/binance.py | 92% | ⚠️ 真实网络请求 |
| indicators.py | 94% | ✅ |
| harmonics.py | 95% | ⚠️ 缺边界用例 |
| filters.py | 91% | ⚠️ 缺 `min_grade=A` 通过路径 |
| reporter.py | 85% | ✅ |
| scanner.py | 43% | 🔴 主路径未测 |
| scheduler.py | 0% | 🔴 完全没测 |
| alerter.py | 62% | ⚠️ Telegram 真实推送未 mock |

测试**全部通过**，但覆盖率分布严重失衡：**核心交易路径 (scanner) 与时间调度 (scheduler) 几乎裸跑**。

---

## 5. 设计文档 vs 代码 一致性

| 设计文档承诺 | 代码实现 | 状态 |
|--------------|----------|------|
| `position_manager.py` | ❌ 不存在 | 高优先级缺口 |
| `get_funding_rate` 抽象方法 | ❌ base.py 未声明 | 接口承诺未兑现 |
| `Config.from_yaml()` | ❌ 无 | 配置双轨 |
| 信号 ID (`sig_xxx`) | ❌ 无 | 可观测性缺口 |
| 持仓跟踪 / 熔断 / 信号生命周期 | ❌ 无 | 设计文档 §7 / §7.3 未落地 |
| RSI 背离检测 | ❌ 无 | 设计文档 §9.1 A 未实现 |
| 成交量确认 | ❌ 无 | 设计文档 §9.1 B 未实现 |
| 动态 PRZ 分级阈值 | ❌ 写死 0.02 / 0.04 | 设计文档 §9.1 C 未实现 |
| 多交易所 fallback | ❌ 只用 binance | 设计文档 §6 错误处理策略未实现 |
| 时区 (Asia/Shanghai) | ⚠️ 配置存在，代码未用 | 时区漂移 bug |
| CSV / JSON 信号存档 | ❌ 无 | 设计文档 §2 / §5.3 未实现 |

> **结论**: 设计文档 ≥ 60% 的功能点未在代码中落地，文档描述的产品成熟度与代码实际成熟度有 **显著差距**。

---

## 6. 建议优先级

### P0 (上线前必须)

1. **F-02**: 实现 `scan_all()` 中的 fallback 链 (try primary → fallbacks → cache)。
2. **F-03**: `scheduler` 引入 `pytz` / `zoneinfo`，按 `ScheduleConfig.timezone` 计算下一次触发时间。
3. **F-05**: 所有 `except` 改用 `logging` + 分类异常 (Timeout / RateLimit / ServerError)。
4. **F-08**: `fetch_repo_info` token 改用环境变量 (`GITHUB_TOKEN`)。
5. **scanner.py / scheduler.py** 补单测：mock exchange API + 模拟时间触发。
6. **F-06**: 加 SQLite (or JSON Lines) 信号存档，至少记录 (timestamp, symbol, pattern, direction, grade, RR)。

### P1 (生产稳定性)

7. **F-01**: 实现 `position_manager.py` 最小版 (持仓上限、风险敞口)，即使只是占位 + 测试。
8. **F-07**: Telegram alerter 加 429 退避 + Markdown 解析失败 fallback 到纯文本。
9. **F-10**: `_loop` 改 `threading.Event.wait(timeout=60)`，长任务期间不重叠。
10. **indicators.calculate_rsi** 改 Wilder 平滑 (或文档注明与 TV 差异)。
11. `Config.from_yaml()` 把 `references/config.yaml` 真接上 (避免双轨)。

### P2 (完善)

12. **F-12/F-13**: ATR 用 `np.maximum.reduce`，EMAs 用 float64 dtype。
13. **F-15**: 单例 Session，按 exchange 复用连接。
14. **F-17**: `reporter` 时区感知 (`datetime.now(ZoneInfo("Asia/Shanghai"))`)。
15. **F-19**: README 截断改成按行截断。
16. **设计文档 9.x**: 增量实现 RSI 背离、VOL 确认、动态 PRZ 阈值。

### P3 (长期)

17. 把 `github-repo-evaluator` 从纯 CLI 脚本升级成 Python package，加 `__main__.py`。
18. 加 CI (GitHub Actions): ruff + mypy + pytest + coverage gate (≥ 85%)。
19. 把 "Jcode Skill" 风格封装成 Anthropic Skill YAML frontmatter，目前 `crypto-harmonic-signals/SKILL.md` 已合规。

---

## 7. 风险点 (业务侧)

1. **HYPE/USDT** 在 Binance 不一定有交易对，扫描会一直返回空 → 用户感受 "扫描不工作"。建议在启动时校验所有 `Config.symbols` 至少能从一个交易所拉到 K 线。
2. **`Scheduler._should_run`** 没有去重 (同一个 schedule 时间点轮询到 N 次会触发 N 次 — 不过锁保护了 `_run_scan`，所以实际只跑一次)。但 `entry.last_run` 被立即赋值，后续轮询会跳过，所以行为正确；只是不利于调试。
3. **Telegram 单条消息内容** MarkdownV1 对 `(` `)` `*` `_` 等敏感字符需要转义；当前消息里有 `(RR 1:1.8)` 是安全的，但 emoji 大量使用偶尔触发 Telegram 端解析失败，建议开 `parse_mode=None` 或用 HTML。
4. **fetch_repo_info** 5 次串行请求在 GFW 下会偶发失败，建议加 retry + jitter。

---

## 8. 快速 win (一天内能改完)

```python
# scheduler.py 时区感知 (P0)
from zoneinfo import ZoneInfo  # py3.9+
TZ = ZoneInfo(self.config.schedule.timezone or "Asia/Shanghai")
now = datetime.now(TZ)

# scanner.py fallback (P0)
def scan_all(self):
    results = []
    order = [self.config.exchanges] + self.config.fallbacks
    for symbol in self.config.symbols:
        for ex_name in order:
            try:
                r = self.scan_symbol(symbol, exchange_name=ex_name)
                if r.signal:  # 拿到信号就跳出
                    results.append(r); break
            except Exception as e:
                log.warning("scan failed %s@%s: %s", symbol, ex_name, e)
                continue
    return results

# fetch_repo_info.py token from env (P0)
import os
token = sys.argv[2] if len(sys.argv) > 2 else os.environ.get("GITHUB_TOKEN")
```

---

## 9. 总结

仓库目前是 **"原型 + 单测" 阶段**：核心算法 (ZigZag / 形态验证 / 过滤 / 报告) 写得好且单测覆盖，但 **生产化能力 (时区 / fallback / 凭证 / 持久化 / 调度闭环) 严重欠缺**。设计文档本身已经把差距写出来了，但代码侧只实现了一半。

建议分两阶段:
- **阶段 A (1 周)**: P0 全部修复，把 HYPE 类空数据、时区漂移、fallback 缺失修掉。
- **阶段 B (2 周)**: P1 + 设计文档里承诺但未落地的核心模块 (position_manager、信号存档、熔断)。

完成后再对外宣称 "可用于交易决策"。

---

*审计完成于 2026-07-29, 测试基线 130/130 PASS。*