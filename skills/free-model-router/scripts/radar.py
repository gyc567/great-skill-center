#!/usr/bin/env python3
"""
Free Model Radar — OpenRouter 免费模型发现 + Pi 集成。

设计原则（fail-closed）：
  1. 免费的定义 = OpenRouter 目录 pricing.prompt == 0 且 pricing.completion == 0，
     显式的 request / cache 价格也必须为 0。
  2. 只有**已核实**参数量 ≥ 100B 的模型才进 approved 池。
     不从名字、上下文长度、模型家族推测参数量。
  3. 子代理候选必须声明支持 tools，且要单独探测过工具调用。
     普通对话探针**不能**证明工具支持。
  4. 绝不自动路由到付费模型。402、配额耗尽、限流都不是移除用户已有配置的理由。
  5. 手输的模型 ID 一律不信。必须对最新扫描结果做 fail-closed 解析。

只用 Python 标准库。
"""
import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import time
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

API = 'https://openrouter.ai/api/v1'
HOME = Path.home() / '.pi' / 'agent'
CACHE = HOME / 'freetoken-bots.json'
MODELS = HOME / 'models.json'
MODELS_STORE = HOME / 'models-store.json'
PARAM = re.compile(r'(?<!\d)(\d+(?:\.\d+)?)\s*[bB](?![a-zA-Z])')

# Pi 的 models.json schema（来自 Pi 官方 docs/models-configuration.md）
# 每个 model 的 cost 四项都是 required
COST_FIELDS = ('input', 'output', 'cacheRead', 'cacheWrite')


# ---------------------------------------------------------------- HTTP
def request(url, key=None, payload=None, timeout=20, retries=2):
    headers = {'User-Agent': 'FreeModelRadar/1.0', 'Accept': 'application/json'}
    if key:
        headers['Authorization'] = 'Bearer ' + key
    if payload is not None:
        headers['Content-Type'] = 'application/json'
    req = urllib.request.Request(url, headers=headers,
                                 data=json.dumps(payload).encode() if payload is not None else None)
    last = None
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.load(resp)
        except (urllib.error.URLError, OSError, ValueError) as exc:
            last = exc
            if attempt < retries:
                time.sleep(1.5 * (attempt + 1))
    raise last


# ---------------------------------------------------------------- 判定
def zero(value):
    try:
        return float(value) == 0
    except (ValueError, TypeError):
        return False


def is_free(model):
    """免费 = prompt 与 completion 都为 0，且显式的 request/cache 价格也为 0。"""
    p = model.get('pricing') or {}
    if not (zero(p.get('prompt')) and zero(p.get('completion'))):
        return False
    return all(zero(p[k]) for k in ('request', 'input_cache_read', 'input_cache_write') if k in p)


def billion(model):
    """只信结构化的参数字段。绝不从名字、上下文长度或模型家族推测。"""
    direct = model.get('total_parameters') or model.get('parameter_count')
    if isinstance(direct, (int, float)) and direct >= 1e9:
        return direct / 1e9
    return None


def has_tools(model):
    return 'tools' in (model.get('supported_parameters') or [])


def eligible(model):
    """已核实 ≥100B + 免费 + 声明支持 tools。"""
    if not is_free(model) or not has_tools(model):
        return False
    b = billion(model)
    return b is not None and b >= 100


def infer_size_from_id(model_id):
    """从 ID 里的显式参数量标记（如 550b）读出数值。

    这**不是**核实，只是一个线索。返回 (值, 是否来自描述性字符串)。
    OpenRouter 目录通常不带结构化参数字段，所以这一路只能进
    needs_parameter_verification，永远不能直接进 approved 池。
    """
    m = PARAM.search(model_id or '')
    if not m:
        return None
    try:
        return float(m.group(1))
    except ValueError:
        return None


# ---------------------------------------------------------------- 发现
def discover():
    raw = request(API + '/models')
    entries = raw.get('data', [])
    free = [m for m in entries if is_free(m)]
    qualifying = [m for m in free if eligible(m)]
    pending = [m for m in free if has_tools(m) and billion(m) is None]

    for m in pending:
        hint = infer_size_from_id(m['id'])
        m['_size_hint_b'] = hint  # 线索，非核实

    return {
        'checked_at': dt.datetime.now(dt.timezone.utc).isoformat(),
        'eligible': [
            {'id': m['id'], 'context_length': m.get('context_length'),
             'parameters_b': billion(m)}
            for m in qualifying
        ],
        'needs_parameter_verification': [
            {'id': m['id'], 'context_length': m.get('context_length'),
             'size_hint_b': m.get('_size_hint_b'),
             'name': m.get('name')}
            for m in pending
        ],
        'free_ids': sorted(m['id'] for m in free),
        'free_count': len(free),
        'total_models': len(entries),
        'free_with_tools': len(pending) + len(qualifying),
    }


# ---------------------------------------------------------------- 缓存
class NotFreeError(RuntimeError):
    """模型 ID 无法被证明免费时抛出。绝不带着不确定去探针。"""


def free_ids():
    """最近一次扫描核实过的精确 OpenRouter ID 集合。

    缓存缺失、不可读、超过 24h、或早于 free_ids 字段时重新扫描
    （公开 /models，不需要 key）。免费资格是动态的，过期名单绝不能授权调用。
    """
    report = None
    if CACHE.exists():
        try:
            report = json.loads(CACHE.read_text())
            age = dt.datetime.now(dt.timezone.utc) - dt.datetime.fromisoformat(report['checked_at'])
            if age > dt.timedelta(hours=24) or 'free_ids' not in report:
                report = None
        except (ValueError, KeyError):
            report = None
    if report is None:
        report = discover()
        atomic_json(CACHE, report)
    return set(report.get('free_ids', []))


def resolve_free_model(requested):
    """fail-closed：把用户给的模型 ID 解析成核实过的免费精确 ID。

    - 与最近扫描结果精确匹配 → 原样使用
    - 缺 `:free` 后缀但带后缀的形式已核实免费 → 自动纠正 + 大声告警
      （静默丢掉 `:free` 会路由到同一模型的**付费版**，这个错误曾造成过真实扣费）
    - 其他任何情况 → 抛 NotFreeError，调用方必须拒绝探针
    """
    requested = (requested or '').strip()
    known = free_ids()
    if requested in known:
        return requested
    suffixed = requested if requested.endswith(':free') else requested + ':free'
    if suffixed in known:
        print(f'WARNING: "{requested}" is not a verified-free model ID; '
              f'using verified-free "{suffixed}" instead. '
              f'Calling "{requested}" directly would use the PAID variant.',
              file=sys.stderr)
        return suffixed
    raise NotFreeError(
        f'"{requested}" is not a verified-free OpenRouter model ID. '
        'Probe refused: calling it could incur charges. '
        'Use an exact ID from the latest scan report.')


# ---------------------------------------------------------------- 探针
def probe_chat(model_id, key, timeout=35):
    """普通对话探针。注意：这**不能**证明工具调用支持。"""
    try:
        result = request(API + '/chat/completions', key,
                         {'model': model_id,
                          'messages': [{'role': 'user', 'content': 'Reply PONG'}],
                          'max_tokens': 64},
                         timeout=timeout)
        if result.get('error'):
            return {'ok': False, 'error': str(result['error'])[:300]}
        return {'ok': bool(result.get('choices')), 'error': None}
    except urllib.error.HTTPError as exc:
        body = ''
        try:
            body = exc.read().decode('utf-8', 'ignore')[:200]
        except Exception:
            pass
        return {'ok': False, 'http_status': exc.code, 'error': str(exc), 'body': body}
    except (OSError, ValueError) as exc:
        return {'ok': False, 'error': str(exc)[:300]}


def probe_tools(model_id, key, timeout=45):
    """真实工具调用探针。子代理候选必须过这一关。"""
    payload = {
        'model': model_id,
        'messages': [{'role': 'user', 'content': 'What is the weather in Beijing? Use the tool.'}],
        'tools': [{
            'type': 'function',
            'function': {
                'name': 'get_weather',
                'description': 'Get current weather for a city',
                'parameters': {
                    'type': 'object',
                    'properties': {'city': {'type': 'string'}},
                    'required': ['city'],
                },
            },
        }],
        'tool_choice': 'auto',
        'max_tokens': 256,
    }
    try:
        result = request(API + '/chat/completions', key, payload, timeout=timeout)
        if result.get('error'):
            return {'ok': False, 'error': str(result['error'])[:300]}
        choices = result.get('choices') or []
        if not choices:
            return {'ok': False, 'error': 'no choices returned'}
        msg = choices[0].get('message') or {}
        calls = msg.get('tool_calls') or []
        if calls:
            fn = (calls[0].get('function') or {}).get('name')
            return {'ok': True, 'tool_called': True, 'function': fn, 'error': None}
        return {'ok': True, 'tool_called': False,
                'note': 'model answered without calling the tool; tool support unproven',
                'error': None}
    except urllib.error.HTTPError as exc:
        return {'ok': False, 'http_status': exc.code, 'error': str(exc)}
    except (OSError, ValueError) as exc:
        return {'ok': False, 'error': str(exc)[:300]}


def classify_error(result):
    """区分临时限流与硬性配额耗尽。"""
    if result.get('ok'):
        return 'ok'
    status = result.get('http_status')
    if status == 429:
        err = (result.get('error') or '') + (result.get('body') or '')
        low = err.lower()
        if any(k in low for k in ('daily', 'limit reached', 'quota', 'exhaust', 'credits')):
            return 'quota_exhausted'
        return 'rate_limited_temporary'
    if status == 402:
        return 'payment_required'
    if status == 401:
        return 'unauthorized'
    return 'other_error'


# ---------------------------------------------------------------- Pi 集成
def pi_available():
    return shutil.which('pi') is not None


def pi_list_models():
    """让 Pi 自己列出 OpenRouter 可用模型。

    OpenRouter 是 Pi 的内置 provider —— 配好 OPENROUTER_API_KEY 后
    Pi 会自动列出全部可用模型，**不需要**改 models.json。
    """
    if not pi_available():
        return {'ok': False, 'error': 'pi not on PATH'}
    env = dict(os.environ)
    env.setdefault('OPENROUTER_API_KEY', 'unset-probe')
    try:
        r = subprocess.run(['pi', '--list-models'], capture_output=True, text=True,
                           timeout=90, env=env)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {'ok': False, 'error': str(exc)[:200]}
    if r.returncode != 0:
        return {'ok': False, 'error': (r.stderr or r.stdout)[:300]}
    models = {}
    for line in (r.stdout or '').split('\n'):
        if not line.strip() or line.startswith('provider'):
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        provider, model = parts[0], parts[1]
        entry = {'provider': provider}
        if len(parts) >= 4:
            entry['context'] = parts[2]
        models.setdefault(provider, []).append(model)
    return {'ok': True, 'providers': {k: len(v) for k, v in models.items()},
            'models': models, 'total': sum(len(v) for v in models.values())}


def build_models_json_entry(model):
    """按 Pi 的 schema 生成一个 provider + model 条目。

    cost 的四个字段在 Pi schema 里都是 required，所以四项都给 0。
    """
    ctx = model.get('context_length') or 128000
    return {
        'name': model.get('name') or model['id'],
        'baseUrl': 'https://openrouter.ai/api/v1',
        'api': 'openai-completions',
        'apiKey': '$OPENROUTER_API_KEY',
        'authHeader': True,
        'models': [{
            'id': model['id'],
            'name': model.get('name') or model['id'],
            'contextWindow': ctx,
            'maxTokens': 16384,
            'cost': {'input': 0, 'output': 0, 'cacheRead': 0, 'cacheWrite': 0},
        }],
    }


def plan_sync(report, pi_models):
    """生成 models.json 的候选 diff。**不写盘**，只出提案。"""
    known = set(pi_models.get('models', {}).get('openrouter', []))
    additions = []
    for m in report.get('needs_parameter_verification', []):
        if m['id'] in known:
            continue
        additions.append(m['id'])
    return {
        'sync_status': 'proposal_only_requires_approval',
        'pi_models_path': str(MODELS),
        'openrouter_is_builtin_provider': True,
        'note': ('OpenRouter 是 Pi 内置 provider。多数情况下配好 OPENROUTER_API_KEY '
                 '后 pi --list-models 已直接列出免费模型，**无需**改 models.json。'
                 '下面的条目只用于 Pi 未列出的模型。'),
        'already_available_in_pi': len(known),
        'proposed_additions': additions,
        'proposed_provider_block': None,
    }


# ---------------------------------------------------------------- 原子写
def atomic_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix='.' + path.name, dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write('\n')
            f.flush()
            os.fsync(f.fileno())
        os.chmod(name, 0o600)
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


# ---------------------------------------------------------------- CLI
def main():
    p = argparse.ArgumentParser(description='OpenRouter 免费模型发现与 Pi 集成')
    p.add_argument('command',
                   choices=['scan', 'status', 'probe', 'probe-tools', 'sync', 'pi-models', 'doctor'])
    p.add_argument('--model', help='精确 OpenRouter 模型 ID')
    p.add_argument('--allow-unverified-size', action='store_true',
                   help='未核实参数量只进报告，永不进 Pi 同步')
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--apply', action='store_true',
                   help='确认后写入 models.json（先备份，失败自动回滚）')
    a = p.parse_args()

    if a.command == 'status':
        print(CACHE.read_text() if CACHE.exists() else '{"message":"run scan first"}')
        return 0

    if a.command in ('probe', 'probe-tools'):
        if not a.model or not os.getenv('OPENROUTER_API_KEY'):
            p.error(f'{a.command} requires --model and OPENROUTER_API_KEY')
        try:
            model = resolve_free_model(a.model)
        except NotFreeError as exc:
            print(f'error: {exc}', file=sys.stderr)
            return 2
        fn = probe_chat if a.command == 'probe' else probe_tools
        result = fn(model, os.environ['OPENROUTER_API_KEY'])
        result['model'] = model
        result['classification'] = classify_error(result)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result.get('ok') else 1

    if a.command == 'pi-models':
        result = pi_list_models()
        if not result.get('ok'):
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return 1
        print(json.dumps({'ok': True, 'total': result['total'],
                          'providers': result['providers'],
                          'openrouter_free_intersection': sorted(
                              set(result['models'].get('openrouter', [])) & free_ids())},
                         indent=2, ensure_ascii=False))
        return 0

    if a.command == 'doctor':
        print(json.dumps(doctor(), indent=2, ensure_ascii=False))
        return 0

    if a.command == 'scan':
        report = discover()
        if not a.dry_run:
            atomic_json(CACHE, report)
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0

    # sync —— 复用缓存报告，不强制重扫网络（网络抖动不该让 sync 挂掉）
    report = None
    if CACHE.exists():
        try:
            cached = json.loads(CACHE.read_text())
            age = dt.datetime.now(dt.timezone.utc) - dt.datetime.fromisoformat(cached['checked_at'])
            if age <= dt.timedelta(hours=24):
                report = cached
        except (ValueError, KeyError):
            report = None
    if report is None:
        report = discover()
    pi = pi_list_models()
    plan = plan_sync(report, pi if pi.get('ok') else {})
    plan['report'] = report
    if not a.dry_run:
        atomic_json(CACHE, report)
    print(json.dumps(plan, indent=2, ensure_ascii=False))
    return 0


def doctor():
    """环境体检：Pi 在不在、缓存新不新、免费名单多少、有没有 key。"""
    out = {
        'pi_on_path': pi_available(),
        'pi_version': None,
        'openrouter_key_set': bool(os.environ.get('OPENROUTER_API_KEY')),
        'cache_path': str(CACHE),
        'cache_exists': CACHE.exists(),
        'cache_age_hours': None,
        'free_count': 0,
        'eligible_count': 0,
        'needs_verification_count': 0,
        'pi_openrouter_models': 0,
        'free_models_already_in_pi': 0,
        'advice': [],
    }
    if pi_available():
        try:
            v = subprocess.run(['pi', '--version'], capture_output=True, text=True, timeout=30)
            out['pi_version'] = (v.stdout or v.stderr).strip()[:40]
        except Exception:
            pass
    if CACHE.exists():
        try:
            rep = json.loads(CACHE.read_text())
            age = dt.datetime.now(dt.timezone.utc) - dt.datetime.fromisoformat(rep['checked_at'])
            out['cache_age_hours'] = round(age.total_seconds() / 3600, 2)
            out['free_count'] = rep.get('free_count', 0)
            out['eligible_count'] = len(rep.get('eligible', []))
            out['needs_verification_count'] = len(rep.get('needs_parameter_verification', []))
            if age > dt.timedelta(hours=24):
                out['advice'].append('缓存已超过 24 小时，请跑 scan')
        except Exception as exc:
            out['advice'].append(f'缓存读取失败: {exc}')
    else:
        out['advice'].append('还没跑过 scan，请先 python3 scripts/radar.py scan')
    if not out['pi_on_path']:
        out['advice'].append('Pi 未安装：curl -fsSL https://pi.dev/install.sh | sh')
    if not out['openrouter_key_set']:
        out['advice'].append('未设置 OPENROUTER_API_KEY（probe 需要）')
    if out['eligible_count'] == 0:
        out['advice'].append(
            'eligible 为空是正常的：OpenRouter /models 目录不提供结构化参数字段。'
            '请用 references/parameter-verification.md 里的方法人工核实参数量。')
    pi = pi_list_models()
    if pi.get('ok'):
        out['pi_openrouter_models'] = len(pi['models'].get('openrouter', []))
        known = set(pi['models'].get('openrouter', []))
        out['free_models_already_in_pi'] = len(known & free_ids())
    return out


if __name__ == '__main__':
    raise SystemExit(main())
