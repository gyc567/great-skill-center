"""abogus 签名与评论解析的离线测试。

不访问网络，可在任何环境运行：

    python3 -m unittest discover -s tests -v
"""

import os
import sys
import unittest

sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"
    ),
)

import abogus  # noqa: E402
from douyin_client import Comment, to_csv_rows, to_json  # noqa: E402


class TestSM3(unittest.TestCase):
    """GB/T 32905-2016 标准测试向量。"""

    def test_abc(self):
        self.assertEqual(
            abogus.sm3_hex(b"abc"),
            "66c7f0f462eeedd9d1f2d46bdc10e4e24167c4875cf2f7a2297da02b8f4ba8e0",
        )

    def test_abcdefghijklmnopqrstuvwxyz(self):
        self.assertEqual(
            abogus.sm3_hex(b"abcdefghijklmnopqrstuvwxyz"),
            "b80fe97a4da24afc277564f66a359ef440462ad28dcc6d63adb24d5c20a61595",
        )

    def test_empty(self):
        self.assertEqual(
            abogus.sm3_hex(b""),
            "1ab21d8355cfa17f8e61194831e81a8f22bec8c728fefb747ed035eb5082aa2b",
        )

    def test_long_input(self):
        self.assertEqual(
            abogus.sm3_hex(b"a" * 1000),
            "f4bedca973227d45c5b822551d2e762d4cfb0e9af70b241452545727b5fb046f",
        )


class TestRC4(unittest.TestCase):
    """RC4 标准测试向量（Wikipedia / 经典教材向量）。"""

    def test_key_plaintext(self):
        # Key="Key", Plaintext="Plaintext" -> BBF316E8D940AF0AD3
        self.assertEqual(
            abogus.rc4(b"Plaintext", b"Key").hex().upper(),
            "BBF316E8D940AF0AD3",
        )

    def test_wiki_pedia(self):
        self.assertEqual(
            abogus.rc4(b"Wiki", b"pedia").hex().upper(), "F9CCEEC3"
        )

    def test_secret_attack(self):
        self.assertEqual(
            abogus.rc4(b"Secret", b"Attack").hex().upper(), "63DE7D7BEA6D"
        )

    def test_roundtrip(self):
        data = b"hello douyin signing world"
        key = b"y"
        self.assertEqual(abogus.rc4(abogus.rc4(data, key), key), data)

    def test_empty_key_raises(self):
        with self.assertRaises(ValueError):
            abogus.rc4(b"data", b"")


class TestCustomB64(unittest.TestCase):
    def test_length_follows_js_float_bound(self):
        # JS: for (i = 0; i < len/3*4; i++) —— 上界是浮点数
        # 输出长度 = ceil(len * 4 / 3)
        #   108 -> 144.0  -> 144
        #   109 -> 145.33 -> 146
        #   110 -> 146.67 -> 147
        #   111 -> 148.0  -> 148
        self.assertEqual(len(abogus.custom_b64(b"\x00" * 108)), 144)
        self.assertEqual(len(abogus.custom_b64(b"\x00" * 109)), 146)
        self.assertEqual(len(abogus.custom_b64(b"\x00" * 110)), 147)
        self.assertEqual(len(abogus.custom_b64(b"\x00" * 111)), 148)

    def test_alphabet_only(self):
        out = abogus.custom_b64(b"\xff" * 60, "s4")
        allowed = set(abogus._B64_ALPHABET["s4"])
        self.assertTrue(set(out) <= allowed)

    def test_unknown_variant_raises(self):
        with self.assertRaises(ValueError):
            abogus.custom_b64(b"abc", "s99")


class TestSign(unittest.TestCase):
    UA = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    )

    def test_shape(self):
        sig = abogus.sign("aweme_id=123&cursor=0", self.UA, (0, 1, 8))
        self.assertTrue(sig.endswith("="))
        # 签名长度固定：ceil((12 + 110) * 4 / 3) + 1 = 164
        self.assertEqual(len(sig), 164)
        allowed = set(abogus._B64_ALPHABET["s4"])
        self.assertTrue(set(sig[:-1]) <= allowed)

    def test_structure_stable_across_calls(self):
        # 签名含随机前缀与毫秒时间戳，不会逐字符相同；
        # 但中后段的固定结构必须稳定。
        a = abogus.sign("aweme_id=1", self.UA, (0, 1, 8))
        b = abogus.sign("aweme_id=1", self.UA, (0, 1, 8))
        marker = "25gsDSkKl12so0j53inCLf/E0iE5hsAtFH8svr4iKi8owICSYyhldAJ5kIlO62-zo0/"
        self.assertIn(marker, a)
        self.assertIn(marker, b)

    def test_different_args_differ(self):
        a = abogus.sign("aweme_id=1", self.UA, (0, 1, 8))
        b = abogus.sign("aweme_id=1", self.UA, (0, 1, 14))
        self.assertNotEqual(a[-40:], b[-40:])

    def test_different_query_differs(self):
        a = abogus.sign("aweme_id=1", self.UA, (0, 1, 8))
        b = abogus.sign("aweme_id=2", self.UA, (0, 1, 8))
        self.assertNotEqual(a[-40:], b[-40:])

    def test_helpers(self):
        q = "aweme_id=1"
        self.assertEqual(
            len(abogus.sign_detail(q, self.UA)),
            len(abogus.sign_reply(q, self.UA)),
        )


class TestCommentParsing(unittest.TestCase):
    RAW = {
        "cid": "7434412221676372763",
        "aweme_id": "7633646113853104116",
        "text": "测试评论内容",
        "digg_count": 35,
        "create_time": 1730958992,
        "reply_comment_total": 7,
        "reply_id": "0",
        "ip_label": "重庆",
        "image_list": [
            {"origin_url": {"url_list": ["https://example.com/a.jpg"]}}
        ],
        "user": {
            "nickname": "测试用户",
            "sec_uid": "MS4wLjABAAAA",
            "unique_id": "test_user",
        },
    }

    def test_from_raw(self):
        c = Comment.from_raw(self.RAW, "7633646113853104116", level=1)
        self.assertEqual(c.cid, "7434412221676372763")
        self.assertEqual(c.text, "测试评论内容")
        self.assertEqual(c.digg_count, 35)
        self.assertEqual(c.nickname, "测试用户")
        self.assertEqual(c.ip_label, "重庆")
        self.assertEqual(c.level, 1)
        self.assertEqual(c.images, ["https://example.com/a.jpg"])

    def test_missing_fields_are_safe(self):
        c = Comment.from_raw({"cid": "1"}, "2")
        self.assertEqual(c.text, "")
        self.assertEqual(c.digg_count, 0)
        self.assertEqual(c.nickname, "")
        self.assertEqual(c.images, [])

    def test_csv_rows(self):
        c = Comment.from_raw(self.RAW, "7633646113853104116", level=1)
        rows = to_csv_rows([c])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["评论内容"], "测试评论内容")
        self.assertEqual(rows[0]["层级"], "一级评论")
        self.assertIn("用户主页", rows[0])

    def test_json_output(self):
        c = Comment.from_raw(self.RAW, "7633646113853104116", level=2)
        out = to_json([c])
        self.assertIn("测试评论内容", out)
        self.assertIn("二级评论", to_csv_rows([c])[0]["层级"])


class TestNoRandomMsToken(unittest.TestCase):
    """回归测试：随机 msToken 会污染签名导致空响应。

    上游 common.py 的 get_ms_token() 返回随机字符串并注入签名参数，
    实测会导致抖音返回 HTTP 200 但响应体为空。本 Skill 绝不复现该行为。
    """

    def test_client_params_have_no_mstoken(self):
        from douyin_client import WEB_PARAMS

        self.assertNotIn("msToken", WEB_PARAMS)
        self.assertNotIn("webid", WEB_PARAMS)

    def test_query_builder_uses_quoted_values(self):
        from douyin_client import _build_query

        q = _build_query({"a": "1", "b": "x y"})
        self.assertEqual(q, "a=1&b=x%20y")


if __name__ == "__main__":
    unittest.main()
