from .config import plugin_config
from .api import TencentTranslator, BaiduTranslator, BaiduPublicTranslator

SIGN_GENERATE_JS = """
    function a(r) {
        if (Array.isArray(r)) {
            for (var o = 0, t = Array(r.length); o < r.length; o++)
                t[o] = r[o];
            return t
        }
        return Array.from(r)
    }
    function n(r, o) {
        for (var t = 0; t < o.length - 2; t += 3) {
            var a = o.charAt(t + 2);
            a = a >= "a" ? a.charCodeAt(0) - 87 : Number(a),
            a = "+" === o.charAt(t + 1) ? r >>> a : r << a,
            r = "+" === o.charAt(t) ? r + a & 4294967295 : r ^ a
        }
        return r
    }
    var i = null;
    function e(r) {
        var t = r.length;
        t > 30 && (r = "" + r.substr(0, 10) + r.substr(Math.floor(t / 2) - 5, 10) + r.substr(-10, 10))

        var u = void 0, l = "" + String.fromCharCode(103) + String.fromCharCode(116) + String.fromCharCode(107);

        u = null !== i ? i : (i = '320305.131321201' || "") || "";
        for (var d = u.split("."), m = Number(d[0]) || 0, s = Number(d[1]) || 0, S = [], c = 0, v = 0; v < r.length; v++) {
            var A = r.charCodeAt(v);
            128 > A ? S[c++] = A : (2048 > A ? S[c++] = A >> 6 | 192 : (55296 === (64512 & A) && v + 1 < r.length && 56320 === (64512 & r.charCodeAt(v + 1)) ? (A = 65536 + ((1023 & A) << 10) + (1023 & r.charCodeAt(++v)),
            S[c++] = A >> 18 | 240,
            S[c++] = A >> 12 & 63 | 128) : S[c++] = A >> 12 | 224,
            S[c++] = A >> 6 & 63 | 128),
            S[c++] = 63 & A | 128)
        }
        for (var p = m, F = "" + String.fromCharCode(43) + String.fromCharCode(45) + String.fromCharCode(97) + ("" + String.fromCharCode(94) + String.fromCharCode(43) + String.fromCharCode(54)), D = "" + String.fromCharCode(43) + String.fromCharCode(45) + String.fromCharCode(51) + ("" + String.fromCharCode(94) + String.fromCharCode(43) + String.fromCharCode(98)) + ("" + String.fromCharCode(43) + String.fromCharCode(45) + String.fromCharCode(102)), b = 0; b < S.length; b++)
            p += S[b],
            p = n(p, F);
        return p = n(p, D),
        p ^= s,
        0 > p && (p = (2147483647 & p) + 2147483648),
        p %= 1e6,
        p.toString() + "." + (p ^ m)
    }
"""

ACS_TOKEN = "1688283182512_1688283209905_ecbXIUvn6YJy8rQDY3g1" \
            "ReOmwlzbUjp9EDQphE5judocmJEXSyKeztLo99iRZNQzbMR2OmM" \
            "RYHYTGiU584eYyFlXzFbWqWYOXFZFAfxEIKaaGrUDRRFxBwEzS1Y" \
            "iJPgyEd8pi0hiyaljYE68JOR4Z3bfycm69mYgL9Uzb9sLA5X4VXN5" \
            "MJt2K/oVpjn5TU55wGSE0OnbgKoGNUeZ1eI1EkxiAyj4OoFvNN9u8" \
            "Uvc+uEoWYChMF6ZWHnJDMZl+jPNofmkbQtO6Wvsf/RiNZMI9Davkz" \
            "wVS1Th3Ioc18d8rZ5zhasoRNIeGq244zyl5QFFIxjsNgXPMQ4AXeV" \
            "hrpV9lKha6TiPHDR1+0DZ3+wwxfvzRvzWDbR5Sl5VvALmCFSGyoRfm" \
            "IRVklnl3a2J9k+8bx3AzGCYuyDfHCOZo2I0c0+c/y0Lhdsl56CR9SV" \
            "lczw+YDpUJBCXnRoCWO+chIyiVKWD7PAvmUVrX9Z32Hviuis="


COOKIE = 'PSTM=1687446622; BAIDUID=6A95AE36AE5FFA3B9E7C8C8046FD6D16:FG=1; ' \
         'BIDUPSID=60D8B4B73304337DA4730B854A771F7C; REALTIME_TRANS_SWITCH=1; ' \
         'FANYI_WORD_SWITCH=1; HISTORY_SWITCH=1; SOUND_SPD_SWITCH=1; SOUND_PREFER_SWITCH=1; ' \
         'BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; ZFY=FxAk7Ccy7Qam4jpD:Ae5z:AViOw6HfyYw:AeJAqPeN83DA:C; ' \
         'BAIDUID_BFESS=6A95AE36AE5FFA3B9E7C8C8046FD6D16:FG=1; BA_HECTOR=8h2h0484a08k01agak25a0a51ia215s1o; ' \
         'ariaDefaultTheme=undefined; RT="z=1&dm=baidu.com&si=2f5a0624-612c-4564-9bfe-c0a608b3d94b&ss=ljl0d9' \
         '5w&sl=1&tt=1fdi&bcn=https%3A%2F%2Ffclog.baidu.com%2Flog%2Fweirwood%3Ftype%3Dperf&nu=9y8m6cy&cl=vg0&ld=' \
         '1g45&ul=1opw&hd=1oqd"; H_PS_PSSID=36546_38859_38958_38954_38983_38962_38918_38972_38819_38636_38868_26350; ' \
         'delPer=0; PSINO=7; Hm_lvt_64ecd82404c51e03dc91cb9e8c025574=1687797786,1688198682,1688279872,1688282040; ' \
         'BCLID=7868282504594360327; BCLID_BFESS=7868282504594360327; BDSFRCVID=HyCOJexroG0tCGRfCHuFbo5NV2KKvV3TDYL' \
         'EOwXPsp3LGJLVF5UJEG0PtoaGdu_-ox8EogKK3gOTH4PF_2uxOjjg8UtVJeC6EG0Ptf8g0M5; ' \
         'BDSFRCVID_BFESS=HyCOJexroG0tCGRfCHuFbo5NV2KKvV3TDYLEOwXPsp3LGJLVF5UJEG0PtoaGdu_-ox8EogKK3gOTH4' \
         'PF_2uxOjjg8UtVJeC6EG0Ptf8g0M5; H_BDCLCKID_SF=tRAOoC_-tDvDqTrP-trf5DCShUFs0xQlB2Q-XPoO3KJADfOPbxb15qD_5h' \
         '5y0x7f5mkf3fbgy4op8P3y0bb2DUA1y4vp0toW3eTxoUJ2-KDVeh5Gqq-KXU4ebPRit4r9Qg-qahQ7tt5W8ncFbT7l5hKpbt-q0x-jL' \
         'TnhVn0MBCK0hD0wD5thj6PVKgTa54cbb4o2WbCQWtjM8pcN2b5oQT83LPJNKfJ7bR5aWK5kQDovOPQKDpOUWfAkXpJvQnJjt2JxaqRC3D' \
         '5lOl5jDh3MhP_1bhode4ROfgTy0hvctb3cShPm0MjrDRLbXU6BK5vPbNcZ0l8K3l02V-bIe-t2XjQhDHt8JT-tJJ3aQ5rtKRTffjrnhPF' \
         '3yUCPXP6-hnjy3bRJ5h345qO1fqjPhToF36DUypjpJh3RymJ42-39LPO2hpRjyxv4Q6LAy4oxJpOJaK6x0P57HR7Wbh5vbURvDP-g3-AJQ' \
         'U5dtjTO2bc_5KnlfMQ_bf--QfbQ0hOhqP-jBRIEoC0XtI0hMCvPKITD-tFO5eT22-us-2Kj2hcHMPoosIJmLUJCbxtn5Joa25QwQJria-QC' \
         'tMbUoqRHXnJi0btQDPvxBf7p3JTPaq5TtUJMDnjjbborqt4be-oyKMnitKv9-pP2LpQrh459XP68bTkA5bjZKxtq3mkjbPbDfn028DKuDjt' \
         'BD5b0jGRabK6aKC5bL6rJabC3O-TJXU6q2bDeQN3J3MbN5e77LlQtaK5FSCooynj4Dp0vWtv4WbbvLT7johRTWqR4sC5ayxonDh83hUQxKn' \
         'QdHCOOVp5O5hvvhn3O3MAM0MKmDloOW-TB5bbPLUQF5l8-sq0x0bOte-bQXH_E5bj2qR-fVC3P; H_BDCLCKID_SF_BFESS=tRAOoC_-tDvD' \
         'qTrP-trf5DCShUFs0xQlB2Q-XPoO3KJADfOPbxb15qD_5h5y0x7f5mkf3fbgy4op8P3y0bb2DUA1y4vp0toW3eTxoUJ2-KDVeh5Gqq-KXU4e' \
         'bPRit4r9Qg-qahQ7tt5W8ncFbT7l5hKpbt-q0x-jLTnhVn0MBCK0hD0wD5thj6PVKgTa54cbb4o2WbCQWtjM8pcN2b5oQT83LPJNKfJ7bR5a' \
         'WK5kQDovOPQKDpOUWfAkXpJvQnJjt2JxaqRC3D5lOl5jDh3MhP_1bhode4ROfgTy0hvctb3cShPm0MjrDRLbXU6BK5vPbNcZ0l8K3l02V-b' \
         'Ie-t2XjQhDHt8JT-tJJ3aQ5rtKRTffjrnhPF3yUCPXP6-hnjy3bRJ5h345qO1fqjPhToF36DUypjpJh3RymJ42-39LPO2hpRjyxv4Q6LAy4' \
         'oxJpOJaK6x0P57HR7Wbh5vbURvDP-g3-AJQU5dtjTO2bc_5KnlfMQ_bf--QfbQ0hOhqP-jBRIEoC0XtI0hMCvPKITD-tFO5eT22-us-2Kj' \
         '2hcHMPoosIJmLUJCbxtn5Joa25QwQJria-QCtMbUoqRHXnJi0btQDPvxBf7p3JTPaq5TtUJMDnjjbborqt4be-oyKMnitKv9-pP2LpQrh' \
         '459XP68bTkA5bjZKxtq3mkjbPbDfn028DKuDjtBD5b0jGRabK6aKC5bL6rJabC3O-TJXU6q2bDeQN3J3MbN5e77LlQtaK5FSCooynj4Dp' \
         '0vWtv4WbbvLT7johRTWqR4sC5ayxonDh83hUQxKnQdHCOOVp5O5hvvhn3O3MAM0MKmDloOW-TB5bbPLUQF5l8-sq0x0bOte-bQXH_E5b' \
         'j2qR-fVC3P; Hm_lpvt_64ecd82404c51e03dc91cb9e8c025574=1688285784; ab_sr=1.0.1_ZWJiYzk1MDU5YTQ2MWJkMzE1MTZ' \
         'mYmQ2Yjg3NGIzZGE4NjlmNmFjNjM4ZmRhNWY5NWY0NWJhNzZhMjBkMDAxMDQwMWNlNWM2ODFkZDg0YTgyNjFiYWFjMjNkM2RiMjczMm' \
         'U1NzgwMTA0NjQyZWM0NGU3ZjlmNTY3OWZkNTExNWFhOGQ1ZDExYTVkNDQ3NDc2YjM1YTM2NzlhNDM3ZGJiYw=='


# translator = TencentTranslator(
#     secret_id=plugin_config.tencent_bot_secret_id,
#     secret_key=plugin_config.tencent_bot_secret_key
# )
# translator = BaiduTranslator(
#     appid=plugin_config.baidu_appid,
#     secret_key=plugin_config.baidu_secret_key
# )
translator = BaiduPublicTranslator(
    sign_generate_js=SIGN_GENERATE_JS,
    acs_token=ACS_TOKEN,
    cookie=COOKIE
)
