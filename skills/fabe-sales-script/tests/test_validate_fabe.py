#!/usr/bin/env python3
"""FABE 校验器的自检测试 —— 证明闸门双向有效（正例放行、反例拦截）。

运行:
    python3 tests/test_validate_fabe.py
    python3 -m pytest tests/test_validate_fabe.py -v
"""

import subprocess
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "validate_fabe.py"


def run(text: str):
    """跑一次校验器，返回 (退出码, stdout)。"""
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".md", encoding="utf-8", delete=False) as f:
        f.write(text)
        path = f.name
    try:
        r = subprocess.run(
            [sys.executable, str(SCRIPT), path],
            capture_output=True, text=True, timeout=60,
        )
        return r.returncode, r.stdout
    finally:
        Path(path).unlink(missing_ok=True)


class TestPositive(unittest.TestCase):
    """合规话术必须放行。"""

    def test_washer_example(self):
        """用户提供的洗地机示例 —— 应当 PASS。"""
        rc, out = run("""- F：自带热风烘干滚刷
- A：洗完不会潮湿、不容易发霉异味
- B：你不用手动拆开晾晒滚刷，更省心，家里更卫生
- E：产品检测报告、买家实测视频
""")
        self.assertEqual(rc, 0, out)
        self.assertIn("PASS", out)

    def test_insurance_example(self):
        """用户提供的保险示例 —— 应当 PASS。"""
        rc, out = run("""- F：这是一款增额终身寿险，有固定递增
- A：比普通年金险更灵活，可以按需随时申请部分领取现金价值
- B：提前给孩子储备教育婚嫁资金，减轻未来经济压力
- E：保单现金价值表、合同条款、过往客户案例
""")
        self.assertEqual(rc, 0, out)

    def test_labeled_format_variants(self):
        """多种标签写法都要能识别。"""
        for fmt in [
            "F: 材质好\nA: 更耐用\nB: 你用得更久\nE: 检测报告",
            "F、材质好\nA、更耐用\nB、你用得更久\nE、检测报告",
            "**F** 材质好\n**A** 更耐用\n**B** 你用得更久\n**E** 检测报告",
        ]:
            with self.subTest(fmt=fmt):
                rc, out = run(fmt)
                self.assertEqual(rc, 0, out)

    def test_unlabeled_order_inference(self):
        """无标签时按 F,A,B,E 顺序推断。"""
        rc, out = run("""材质好
更耐用
你用得更久
检测报告
""")
        self.assertEqual(rc, 0, out)


class TestNegative(unittest.TestCase):
    """问题话术必须被拦住。"""

    def test_f_a_conflation(self):
        """A 复述 F —— 必须报错。"""
        rc, out = run("""- F：不锈钢材质，3000W大功率电机
- A：不锈钢材质，3000W大功率电机
- B：你不用操心性能，家里更干净
- E：检测报告
""")
        self.assertEqual(rc, 1)
        self.assertIn("复述", out)

    def test_missing_e(self):
        """缺 E 环节 —— 必须报错。"""
        rc, out = run("""- F：增额终身寿险，固定递增
- A：比普通年金险更灵活，可以按需申请部分领取
- B：提前给孩子储备教育资金，减轻未来经济压力
""")
        self.assertEqual(rc, 1)
        self.assertIn("缺少 E", out)

    def test_weak_evidence(self):
        """E 是空话 —— 必须报错。"""
        rc, out = run("""- F：材质好
- A：更耐用
- B：你用得更久
- E：品质保证，值得信赖，销量第一
""")
        self.assertEqual(rc, 1)
        self.assertIn("空话", out)

    def test_ai_cliche_benefit(self):
        """B 是 AI 空话 —— 必须报错。"""
        rc, out = run("""- F：材质好
- A：更耐用
- B：提升效率，降低成本，优化体验
- E：检测报告
""")
        self.assertEqual(rc, 1)
        self.assertIn("AI 空话", out)

    def test_vague_evidence(self):
        """E 只有“很多客户” —— 必须报错。"""
        rc, out = run("""- F：支持7天无理由退换
- A：买错了也能退，不承担损失
- B：你不用担心选错，试错成本很低
- E：很多客户都说不错
""")
        self.assertEqual(rc, 1)
        self.assertIn("可核验", out)

    def test_benefit_not_client_facing(self):
        """B 继续说产品而非客户 —— 必须报错。"""
        rc, out = run("""- F：材质好
- A：更耐用
- B：采用进口材料，工艺先进
- E：检测报告
""")
        self.assertEqual(rc, 1)
        self.assertIn("客户视角", out)


class TestMutualExclusion(unittest.TestCase):
    """校验器本身的可信度：改坏一条就该失败。"""

    def test_removing_e_line_breaks_pass(self):
        """把合规话术的 E 删掉，必须从 PASS 变 FAIL —— 证明闸门真的在起作用。"""
        good = """- F：自带热风烘干滚刷
- A：洗完不会潮湿、不容易发霉异味
- B：你不用手动拆开晾晒滚刷，更省心，家里更卫生
- E：产品检测报告、买家实测视频
"""
        bad = "\n".join(good.split("\n")[:-2]) + "\n"
        self.assertEqual(run(good)[0], 0)
        self.assertEqual(run(bad)[0], 1)

    def test_evidence_type_detection(self):
        """不同证据类型都要能识别。"""
        for evidence in ["检测报告", "客户案例", "保单条款", "现金价值表", "实测视频", "认证证书"]:
            with self.subTest(evidence=evidence):
                rc, out = run(f"""- F：材质好
- A：更耐用
- B：你用得更久
- E：{evidence}
""")
                self.assertEqual(rc, 0, out)


class TestCLI(unittest.TestCase):
    """命令行接口。"""

    def test_demo_mode(self):
        r = subprocess.run([sys.executable, str(SCRIPT), "--demo"], capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("PASS", r.stdout)

    def test_json_mode(self):
        import json
        r = subprocess.run([sys.executable, str(SCRIPT), "--demo", "--json"], capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stdout)
        data = json.loads(r.stdout)
        self.assertTrue(data["pass"])
        self.assertEqual(len(data["units"]), 4)
        self.assertEqual(len(data["checks"]), 5)

    def test_missing_file(self):
        r = subprocess.run([sys.executable, str(SCRIPT), "/nonexistent/x.md"], capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
