import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    'radar', Path(__file__).resolve().parents[1] / 'scripts' / 'radar.py')
radar = importlib.util.module_from_spec(spec)
spec.loader.exec_module(radar)


class ModelTests(unittest.TestCase):
    """上游 v0.1.x 原有测试，保持行为兼容。"""

    def test_price(self):
        self.assertTrue(radar.is_free({'pricing': {'prompt': '0', 'completion': '0'}}))
        self.assertFalse(radar.is_free({'pricing': {'prompt': '0', 'completion': '0.00001'}}))

    def test_unknown_parameters_fail_closed(self):
        self.assertFalse(radar.eligible(
            {'id': 'some/550b:free', 'pricing': {'prompt': '0', 'completion': '0'},
             'supported_parameters': ['tools']}))

    def test_verified_parameters(self):
        self.assertTrue(radar.eligible(
            {'id': 'any', 'total_parameters': 120000000000,
             'pricing': {'prompt': '0', 'completion': '0'},
             'supported_parameters': ['tools']}))


class ResolveTests(unittest.TestCase):
    """v0.1.1 fail-closed 模型解析：绝不信任手输的 ID。"""

    def setUp(self):
        self._orig = radar.free_ids
        radar.free_ids = lambda: {'a/model:free', 'openrouter/free'}

    def tearDown(self):
        radar.free_ids = self._orig

    def test_exact_id_used_asis(self):
        self.assertEqual(radar.resolve_free_model('a/model:free'), 'a/model:free')

    def test_missing_free_suffix_autocorrects(self):
        self.assertEqual(radar.resolve_free_model('a/model'), 'a/model:free')

    def test_unknown_id_refused(self):
        with self.assertRaises(radar.NotFreeError):
            radar.resolve_free_model('x/paid-model')

    def test_blank_id_refused(self):
        with self.assertRaises(radar.NotFreeError):
            radar.resolve_free_model('   ')


class EnhancedTests(unittest.TestCase):
    """商品化版本新增能力的测试。"""

    def test_tools_required(self):
        m = {'id': 'x/y:free', 'pricing': {'prompt': '0', 'completion': '0'},
             'total_parameters': 200e9}
        self.assertFalse(radar.eligible(m))
        m['supported_parameters'] = ['tools']
        self.assertTrue(radar.eligible(m))

    def test_cache_prices_must_be_zero(self):
        m = {'id': 'x/y:free', 'pricing': {'prompt': '0', 'completion': '0',
                                          'input_cache_read': '0.5'},
             'total_parameters': 200e9, 'supported_parameters': ['tools']}
        self.assertFalse(radar.is_free(m))
        self.assertFalse(radar.eligible(m))

    def test_size_hint_is_only_a_hint(self):
        """ID 里的 550b 只是线索，不能进 approved 池。"""
        self.assertEqual(radar.infer_size_from_id('nvidia/nemotron-3-ultra-550b-a55b:free'), 550.0)
        # 关键：hint 不影响 eligible
        m = {'id': 'nvidia/x-550b:free', 'pricing': {'prompt': '0', 'completion': '0'},
             'supported_parameters': ['tools']}
        self.assertFalse(radar.eligible(m))

    def test_size_hint_absent(self):
        self.assertIsNone(radar.infer_size_from_id('openrouter/free'))
        self.assertIsNone(radar.infer_size_from_id(''))

    def test_error_classification(self):
        self.assertEqual(radar.classify_error({'ok': True}), 'ok')
        self.assertEqual(radar.classify_error({'ok': False, 'http_status': 429}), 'rate_limited_temporary')
        self.assertEqual(
            radar.classify_error({'ok': False, 'http_status': 429, 'error': 'daily limit reached'}),
            'quota_exhausted')
        self.assertEqual(radar.classify_error({'ok': False, 'http_status': 402}), 'payment_required')
        self.assertEqual(radar.classify_error({'ok': False, 'http_status': 401}), 'unauthorized')

    def test_atomic_json_writes_and_protects(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / 'sub' / 'data.json'
            radar.atomic_json(target, {'a': 1})
            self.assertTrue(target.exists())
            self.assertEqual(json.loads(target.read_text()), {'a': 1})
            mode = target.stat().st_mode & 0o777
            self.assertEqual(mode, 0o600, '报告文件必须是 0600')

    def test_atomic_json_leaves_no_temp_files(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / 'data.json'
            radar.atomic_json(target, {'x': 1})
            leftovers = [p.name for p in Path(td).iterdir() if p.name != 'data.json']
            self.assertEqual(leftovers, [], '原子写不能留下临时文件')

    def test_build_models_json_entry_matches_pi_schema(self):
        entry = radar.build_models_json_entry(
            {'id': 'x/y:free', 'name': 'Y Free', 'context_length': 262144})
        self.assertEqual(entry['baseUrl'], 'https://openrouter.ai/api/v1')
        self.assertEqual(entry['api'], 'openai-completions')
        self.assertEqual(entry['apiKey'], '$OPENROUTER_API_KEY')
        model = entry['models'][0]
        self.assertEqual(model['id'], 'x/y:free')
        self.assertEqual(model['contextWindow'], 262144)
        for f in radar.COST_FIELDS:
            self.assertIn(f, model['cost'], f'Pi schema 要求 cost.{f}')
            self.assertEqual(model['cost'][f], 0, '免费模型成本必须是 0')

    def test_build_models_json_entry_default_context(self):
        entry = radar.build_models_json_entry({'id': 'x/y:free'})
        self.assertEqual(entry['models'][0]['contextWindow'], 128000)

    def test_plan_sync_marks_builtin_provider(self):
        plan = radar.plan_sync(
            {'needs_parameter_verification': [{'id': 'a/b:free'}, {'id': 'c/d:free'}]},
            {'ok': True, 'models': {'openrouter': ['c/d:free']}})
        self.assertTrue(plan['openrouter_is_builtin_provider'])
        self.assertEqual(plan['proposed_additions'], ['a/b:free'])
        self.assertEqual(plan['already_available_in_pi'], 1)
        self.assertIn('无需', plan['note'])

    def test_discover_shape(self):
        """discover 的返回结构必须包含三个池子。"""
        fake = {'data': [
            {'id': 'free/tools/verified', 'pricing': {'prompt': '0', 'completion': '0'},
             'total_parameters': 200e9, 'supported_parameters': ['tools'],
             'context_length': 1000, 'name': 'V'},
            {'id': 'free/tools/unverified', 'pricing': {'prompt': '0', 'completion': '0'},
             'supported_parameters': ['tools'], 'context_length': 2000, 'name': 'U'},
            {'id': 'paid/one', 'pricing': {'prompt': '1', 'completion': '1'}},
            {'id': 'free/no-tools', 'pricing': {'prompt': '0', 'completion': '0'},
             'total_parameters': 200e9},
        ]}
        orig = radar.request
        radar.request = lambda url, *a, **k: fake
        try:
            rep = radar.discover()
        finally:
            radar.request = orig
        self.assertEqual(rep['free_count'], 3)
        self.assertEqual(len(rep['eligible']), 1)
        self.assertEqual(rep['eligible'][0]['id'], 'free/tools/verified')
        self.assertEqual(rep['eligible'][0]['parameters_b'], 200.0)
        self.assertEqual(len(rep['needs_parameter_verification']), 1)
        self.assertNotIn('paid/one', rep['free_ids'])
        # free_ids 是"所有免费模型"，含不支持 tools 的 —— 工具支持是另一道门
        self.assertIn('free/no-tools', rep['free_ids'])

    def test_free_ids_rescans_when_stale(self):
        """缓存超过 24h 必须重新扫描 —— 免费资格是动态的。"""
        old = {'checked_at': '2020-01-01T00:00:00+00:00', 'free_ids': ['x/y:free']}
        with tempfile.TemporaryDirectory() as td:
            cache = Path(td) / 'freetoken-bots.json'
            cache.write_text(json.dumps(old))
            orig_cache = radar.CACHE
            orig_req = radar.request
            radar.CACHE = cache
            radar.request = lambda url, *a, **k: {'data': [
                {'id': 'new/model:free', 'pricing': {'prompt': '0', 'completion': '0'},
                 'supported_parameters': ['tools']}]}
            try:
                ids = radar.free_ids()
            finally:
                radar.CACHE = orig_cache
                radar.request = orig_req
            self.assertIn('new/model:free', ids)
            self.assertNotIn('x/y:free', ids, '过期名单不能授权调用')


if __name__ == '__main__':
    unittest.main()
