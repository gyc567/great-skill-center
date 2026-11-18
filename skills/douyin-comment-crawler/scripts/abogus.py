"""抖音 web 接口 a_bogus 签名 —— 纯 Python 实现。

算法由公开标准算法组合而成：
  * RC4 流密码（RFC 6229 / 经典 KSA-PRGA）
  * SM3 密码杂凑（GB/T 32905-2016）
  * 自定义 Base64 变体 + 字节级打包

不依赖 Node.js / execjs / PyExecJS，纯标准库实现。
"""

from __future__ import annotations

import random
import struct
import time

# --------------------------------------------------------------------------
# SM3 密码杂凑（GB/T 32905-2016）
# --------------------------------------------------------------------------

_SM3_IV = [
    0x7380166F, 0x4914B2B9, 0x172442D7, 0xDA8A0600,
    0xA96F30BC, 0x163138AA, 0xE38DEE4D, 0xB0FB0E4E,
]

_T = [0x79CC4519] + [0x7A879D8A] * 15


def _rotl(x: int, n: int) -> int:
    n &= 31
    return ((x << n) | (x >> (32 - n))) & 0xFFFFFFFF


def _p0(x: int) -> int:
    return x ^ _rotl(x, 9) ^ _rotl(x, 17)


def _p1(x: int) -> int:
    return x ^ _rotl(x, 15) ^ _rotl(x, 23)


def _ff_j(x: int, y: int, z: int, j: int) -> int:
    if j < 16:
        return x ^ y ^ z
    return (x & y) | (x & z) | (y & z)


def _gg_j(x: int, y: int, z: int, j: int) -> int:
    if j < 16:
        return x ^ y ^ z
    return (x & y) | ((~x & 0xFFFFFFFF) & z)


def sm3(data: bytes) -> bytes:
    """返回 32 字节的 SM3 摘要。"""
    bit_len = len(data) * 8
    data = data + b"\x80"
    while len(data) % 64 != 56:
        data += b"\x00"
    data += struct.pack(">Q", bit_len)

    v = list(_SM3_IV)

    for off in range(0, len(data), 64):
        block = data[off:off + 64]
        w = list(struct.unpack(">16I", block))
        for j in range(16, 68):
            w.append(_p1(w[j - 16] ^ w[j - 9] ^ _rotl(w[j - 3], 15))
                     ^ _rotl(w[j - 13], 7) ^ w[j - 6])
        w1 = [w[j] ^ w[j + 4] for j in range(64)]

        a, b, c, d, e, f, g, h = v
        for j in range(64):
            t = 0x79CC4519 if j < 16 else 0x7A879D8A
            ss1 = _rotl((_rotl(a, 12) + e + _rotl(t, j % 32)) & 0xFFFFFFFF, 7)
            ss2 = ss1 ^ _rotl(a, 12)
            # 注意：TT1 使用 W1[j]，TT2 使用 W[j]（GB/T 32905-2016）
            tt1 = (_ff_j(a, b, c, j) + d + ss2 + w1[j]) & 0xFFFFFFFF
            tt2 = (_gg_j(e, f, g, j) + h + ss1 + w[j]) & 0xFFFFFFFF
            d = c
            c = _rotl(b, 9)
            b = a
            a = tt1
            h = g
            g = _rotl(f, 19)
            f = e
            e = _p0(tt2)
        v = [x ^ y for x, y in zip(v, [a, b, c, d, e, f, g, h])]

    return struct.pack(">8I", *v)


def sm3_hex(data: bytes) -> str:
    return sm3(data).hex()


# --------------------------------------------------------------------------
# RC4 流密码
# --------------------------------------------------------------------------

def rc4(data: bytes, key: bytes) -> bytes:
    s = list(range(256))
    j = 0
    klen = len(key)
    if klen == 0:
        raise ValueError("RC4 key must not be empty")
    for i in range(256):
        j = (j + s[i] + key[i % klen]) & 0xFF
        s[i], s[j] = s[j], s[i]

    out = bytearray(len(data))
    i = j = 0
    for k, byte in enumerate(data):
        i = (i + 1) & 0xFF
        j = (j + s[i]) & 0xFF
        s[i], s[j] = s[j], s[i]
        out[k] = s[(s[i] + s[j]) & 0xFF] ^ byte
    return bytes(out)


# --------------------------------------------------------------------------
# 自定义 Base64 变体
# --------------------------------------------------------------------------

_B64_ALPHABET = {
    "s0": "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=",
    "s1": "Dkdpgh4ZKsQB80/Mfvw36XI1R25+WUAlEi7NLboqYTOPuzmFjJnryx9HVGcaStCe=",
    "s2": "Dkdpgh4ZKsQB80/Mfvw36XI1R25-WUAlEi7NLboqYTOPuzmFjJnryx9HVGcaStCe=",
    "s3": "ckdp1h4ZKsUB80/Mfvw36XIgR25+WQAlEi7NLboqYTOPuzmFjJnryx9HVGDaStCe",
    "s4": "Dkdpgh2ZmsQB80/MfvV36XI1R45-WUAlEixNLwoqYTOPuzKFjJnry79HbGcaStCe",
}


def _get_long_int(block_index: int, data: bytes) -> int:
    """把 3 字节块解成一个 24bit 整数（用于自定义 base64）。"""
    chunk = data[block_index * 3:block_index * 3 + 3]
    if len(chunk) < 3:
        chunk = chunk + b"\x00" * (3 - len(chunk))
    return (chunk[0] << 16) | (chunk[1] << 8) | chunk[2]


def custom_b64(data: bytes, variant: str = "s4") -> str:
    """抖音签名用的自定义 base64 变体。

    与标准 base64 相比有两处差异：
      1. 字母表被替换为抖音自定义表；
      2. 输出长度 = ceil(len(data) * 4 / 3) —— 原 JS 写作
         `for (i = 0; i < long_str.length / 3 * 4; i++)`，循环上界是浮点数，
         所以当长度不是 3 的倍数时，输出会比标准 base64 少 1 个 padding 位。

    例：110 字节 -> 110/3*4 = 146.67 -> 输出 147 个字符。
    """
    if variant not in _B64_ALPHABET:
        raise ValueError(f"unknown base64 variant: {variant}")
    alphabet = _B64_ALPHABET[variant]

    out = []
    block = 0
    # ceil(len / 3 * 4)，等价于 -(-len * 4 // 3)
    total = -(-len(data) * 4 // 3)
    for i in range(total):
        if i // 4 != block:
            block += 1
        value = _get_long_int(block, data)
        key = i % 4
        if key == 0:
            index = (value & 0x00FC0000) >> 18
        elif key == 1:
            index = (value & 0x0003F000) >> 12
        elif key == 2:
            index = (value & 0x00000FC0) >> 6
        else:
            index = value & 63
        out.append(alphabet[index])

    return "".join(out)


# --------------------------------------------------------------------------
# a_bogus 签名
# --------------------------------------------------------------------------

WINDOW_ENV = "1536|747|1536|834|0|30|0|0|1536|834|1536|864|1525|747|24|24|Win32"

# JS: String.fromCharCode.apply(null, [0.00390625, 1, Arguments[2]])
#     -> [0, 1, Arguments[2]]，因为 0.00390625 会被截断为 0
UA_RC4_KEY_PREFIX = bytes([0, 1])


def _gener_random(random_val: float, option: tuple[int, int]) -> list[int]:
    r = int(random_val) & 0xFFFF
    return [
        (r & 255 & 170) | option[0] & 85,
        (r & 255 & 85) | option[0] & 170,
        (r >> 8 & 255 & 170) | option[1] & 85,
        (r >> 8 & 255 & 85) | option[1] & 170,
    ]


def generate_random_str() -> bytes:
    parts = []
    parts += _gener_random(random.random() * 10000, (3, 45))
    parts += _gener_random(random.random() * 10000, (1, 0))
    parts += _gener_random(random.random() * 10000, (1, 5))
    return bytes(parts)


def _ua_digest(user_agent: str, arg2: int) -> bytes:
    """UA 处理链：rc4(ua, key) -> custom_b64(s3) -> sm3。"""
    key = UA_RC4_KEY_PREFIX + bytes([arg2 & 0xFF])
    encrypted = rc4(user_agent.encode("utf-8"), key)
    b64 = custom_b64(encrypted, "s3")
    return sm3(b64.encode("utf-8"))


def sign(url_search_params: str, user_agent: str, args: tuple[int, int, int] = (0, 1, 14)) -> str:
    """生成 a_bogus 签名值（不含 '=' 后缀之外的任何包装）。

    Args:
        url_search_params: 已 urlencode 的查询串（不含 a_bogus 本身）
        user_agent: 浏览器 UA，必须与请求头一致
        args: (arg0, arg1, arg2) —— 抖音不同接口使用不同组合，
              评论接口用 (0, 1, 8)，详情接口常用 (0, 1, 14)
    """
    arg0, arg1, arg2 = args
    start_ms = int(time.time() * 1000)

    params_hash = sm3(sm3((url_search_params + "cus").encode("utf-8")))
    suffix_hash = sm3(sm3(b"cus"))
    ua_hash = _ua_digest(user_agent, arg2)
    end_ms = int(time.time() * 1000)

    b: dict[int, int] = {}
    b[8] = 3
    b[10] = end_ms
    b[16] = start_ms
    b[18] = 44
    b[19] = 44

    b[20] = (b[16] >> 24) & 255
    b[21] = (b[16] >> 16) & 255
    b[22] = (b[16] >> 8) & 255
    b[23] = b[16] & 255
    # JS 原文用浮点除法 (x/256/256/256/256)>>0，不是移位
    b[24] = int(b[16] / 256 / 256 / 256 / 256) & 0xFF
    b[25] = int(b[16] / 256 / 256 / 256 / 256 / 256) & 0xFF

    b[26] = (arg0 >> 24) & 255
    b[27] = (arg0 >> 16) & 255
    b[28] = (arg0 >> 8) & 255
    b[29] = arg0 & 255
    b[30] = (arg1 >> 8) & 255
    b[31] = arg1 & 255
    b[32] = (arg1 >> 24) & 255
    b[33] = (arg1 >> 16) & 255
    b[34] = (arg2 >> 24) & 255
    b[35] = (arg2 >> 16) & 255
    b[36] = (arg2 >> 8) & 255
    b[37] = arg2 & 255

    b[38] = params_hash[21]
    b[39] = params_hash[22]
    b[40] = suffix_hash[21]
    b[41] = suffix_hash[22]
    b[42] = ua_hash[23]
    b[43] = ua_hash[24]

    b[44] = (b[10] >> 24) & 255
    b[45] = (b[10] >> 16) & 255
    b[46] = (b[10] >> 8) & 255
    b[47] = b[10] & 255
    b[48] = b[8]
    # 同上：JS 用浮点除法
    b[49] = int(b[10] / 256 / 256 / 256 / 256) & 0xFF
    b[50] = int(b[10] / 256 / 256 / 256 / 256 / 256) & 0xFF

    page_id = 6241
    aid = 6383
    b[51] = page_id
    b[52] = (page_id >> 24) & 255
    b[53] = (page_id >> 16) & 255
    b[54] = (page_id >> 8) & 255
    b[55] = page_id & 255
    b[56] = aid
    b[57] = aid & 255
    b[58] = (aid >> 8) & 255
    b[59] = (aid >> 16) & 255
    b[60] = (aid >> 24) & 255

    env = WINDOW_ENV.encode("utf-8")
    b[64] = len(env)
    b[65] = b[64] & 255
    b[66] = (b[64] >> 8) & 255
    b[69] = 0
    b[70] = 0
    b[71] = 0

    b[72] = (
        b[18] ^ b[20] ^ b[26] ^ b[30] ^ b[38] ^ b[40] ^ b[42] ^ b[21] ^ b[27]
        ^ b[31] ^ b[35] ^ b[39] ^ b[41] ^ b[43] ^ b[22] ^ b[28] ^ b[32] ^ b[36]
        ^ b[23] ^ b[29] ^ b[33] ^ b[37] ^ b[44] ^ b[45] ^ b[46] ^ b[47] ^ b[48]
        ^ b[49] ^ b[50] ^ b[24] ^ b[25] ^ b[52] ^ b[53] ^ b[54] ^ b[55] ^ b[57]
        ^ b[58] ^ b[59] ^ b[60] ^ b[65] ^ b[66] ^ b[70] ^ b[71]
    )

    order = [
        b[18], b[20], b[52], b[26], b[30], b[34], b[58], b[38], b[40], b[53],
        b[42], b[21], b[27], b[54], b[55], b[31], b[35], b[57], b[39], b[41],
        b[43], b[22], b[28], b[32], b[60], b[36], b[23], b[29], b[33], b[37],
        b[44], b[45], b[59], b[46], b[47], b[48], b[49], b[50], b[24], b[25],
        b[65], b[66], b[70], b[71],
    ]
    bb = bytes(order) + env + bytes([b[72] & 0xFF])

    # JS: result_encrypt(generate_random_str() + rc4(bb), "s4")
    # 随机前缀是 12 字节（3 次 gener_random，每次 4 字节）
    random_prefix = generate_random_str()
    return custom_b64(random_prefix + rc4(bb, b"y"), "s4") + "="


def sign_detail(url_search_params: str, user_agent: str) -> str:
    return sign(url_search_params, user_agent, (0, 1, 14))


def sign_reply(url_search_params: str, user_agent: str) -> str:
    return sign(url_search_params, user_agent, (0, 1, 8))
