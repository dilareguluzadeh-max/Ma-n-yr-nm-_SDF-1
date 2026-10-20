# -*- coding: utf-8 -*-
"""
SDF 1 yoxlama mühərriki — həm brauzerdə (Pyodide, index.html), həm də müəllimin
kompüterində (yeniden_qiymetlendir.py) eyni kod işləyir.

HARNESS_SOURCE mətni tools/build_bank.py tərəfindən exam_data.js-ə yerləşdirilir.
"""

import types

HARNESS_SOURCE = r'''
import builtins
import contextlib
import hashlib
import io
import json
import math
import re
import sys
import time

import numpy as np
import pandas as pd

try:   # scikit-learn əvvəlcədən yüklənir (testlər zamanı izləmə yavaşlatmasın)
    import sklearn.linear_model, sklearn.metrics, sklearn.model_selection, sklearn.preprocessing  # noqa: F401
except Exception:
    pass

# Yalnız təhlükəsizlik üçün zəruri modullar bloklanır; digər standart kitabxanalar (itertools, collections, heapq, bisect, random, os, ...) sərbəstdir
_BLOCKED_MODULES = ("js", "pyodide", "pyodide_js", "_pyodide", "micropip", "subprocess", "socket")
_real_import = builtins.__import__


def _guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
    if name.split(".")[0] in _BLOCKED_MODULES:
        raise ImportError(f"'{name}' modulu imtahanda qadağandır")
    return _real_import(name, globals, locals, fromlist, level)


def _h(x):
    return hashlib.sha256(str(x).strip().lower().encode()).hexdigest()


def _plain(v):
    """numpy/tuple/set tiplərini adi Python siyahı-dəyərlərinə çevirir (tolerant müqayisə üçün)."""
    if hasattr(v, "tolist"):
        v = v.tolist()
    if isinstance(v, (list, tuple)):
        return [_plain(x) for x in v]
    if isinstance(v, dict):
        return {k: _plain(x) for k, x in v.items()}
    return v


def _eq(a, b):
    """Tolerant bərabərlik: list≈tuple≈ndarray, 1.0≈1, float-lar üçün kiçik xəta payı."""
    a, b = _plain(a), _plain(b)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(_eq(x, y) for x, y in zip(a, b))
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(_eq(a[k], b[k]) for k in a)
    if isinstance(a, float) or isinstance(b, float):
        try:
            return math.isclose(a, b, rel_tol=1e-6, abs_tol=1e-9)
        except TypeError:
            return False
    return a == b


OK_MSG = "✅ Tapşırıq {t}: DÜZGÜNDÜR (+{p} bal)"
PARTIAL_MSG = "🟡 Tapşırıq {t}: QİSMƏN DÜZGÜNDÜR (+{p} / {m} bal)"
FAIL_MSG = "❌ Tapşırıq {t}: XƏTA — Çıxış formatı və ya hesablanmış dəyər gözlənilən nəticəyə uyğun deyil!"


def grade(*items):
    """
    Qismən bal üçün: items = (çəki, "yoxlanılan hissə", çağırıla bilən) ...
    Hər hissə ayrıca yoxlanılır; ödənən hissələrin çəkisi toplanır.
    Qaytarır: (qazanılan_çəki, ümumi_çəki, [ödənməyən hissələrin təsviri]).
    """
    got = tot = 0
    failed = []
    for w, label, fn in items:
        tot += w
        try:
            r = fn()
            if isinstance(r, (bool, np.bool_)) and not r:
                raise AssertionError
            got += w
        except AssertionError:
            failed.append(label)
        except Exception as e:
            failed.append(f"{label} ({type(e).__name__}: {e})")
    return (got, tot, failed)


def _exec_limited(code, ns, budget, out):
    """Kodu vaxt limiti ilə icra edir (sonsuz dövrlər brauzeri dondurmasın)."""
    deadline = time.monotonic() + budget

    def tracer(frame, event, arg):
        if time.monotonic() > deadline:
            raise TimeoutError(f"icra {budget:g} saniyədən çox çəkdi (sonsuz dövr ola bilər)")
        return tracer

    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
        sys.settrace(tracer)
        try:
            exec(compile(code, "<kod>", "exec"), ns)
        finally:
            sys.settrace(None)


_QUOTES = {"\u201c": '"', "\u201d": '"', "\u201e": '"', "\u2018": "'", "\u2019": "'", "\u00a0": " ", "\u2009": " ",
           "\u200b": "", "\u200c": "", "\u200d": "", "\ufeff": "", "\u2013": "-", "\u2212": "-"}


def normalize_code(code):
    """
    Colab/Jupyter-dən gələn kodu tolerant şəkildə qəbul edir:
    CRLF, sətir başındakı Tab (4 boşluq), görünməz/qeyri-standart simvollar (NBSP, \u200b), "ağıllı" dırnaqlar,
    ümumi artıq girinti (kod xanası içəridən kopyalananda) və Jupyter sehrli sətirləri (%magic, !əmr) düzəldilir.
    """
    import textwrap
    code = str(code).replace("\r\n", "\n").replace("\r", "\n")
    code = "".join(_QUOTES.get(c, c) for c in code)
    lines = []
    for ln in code.split("\n"):
        stripped = ln.lstrip(" \t")
        lead = ln[:len(ln) - len(stripped)].replace("\t", "    ")
        if stripped.startswith(("%", "!")) and not stripped.startswith("!="):
            continue                      # Jupyter: %matplotlib inline, !pip install ...
        lines.append((lead + stripped).rstrip())
    return textwrap.dedent("\n".join(lines)).strip("\n") + "\n"


def _describe(exc):
    if "'___'" in str(exc):
        return "`___` boşluqları hələ doldurulmayıb"
    if isinstance(exc, IndentationError):
        return f"Girinti xətası (sətir {exc.lineno}): {exc.msg}. Bloklardan sonra (:) 4 boşluq girinti qoyun."
    if isinstance(exc, SyntaxError):
        return f"Sintaksis xətası (sətir {exc.lineno}): {exc.msg}"
    return f"{type(exc).__name__}: {exc}"


def _coerce(value):
    if value is None:
        return None
    s = str(value).strip()
    if s == "":
        return None
    if re.fullmatch(r"[+-]?\d+", s):
        return int(s)
    return s


def run_variant(steps, answers, upto=None, budget=10.0):
    """
    steps   : exam_data.js-dəki addımlar (tapşırıq ardıcıllığı ilə)
    answers : {"A1": "<kod>", "C1": "24", "E1": "b", ...}
    upto    : yalnız bu tapşırığın testinə qədər icra et ("Test Et" düyməsi üçün)
    Nəticə  : {"results": {id: {ok, pts, max, msg, detail}}, "output": {id: stdout}}
    """
    answers = answers or {}
    ns = {
        "__name__": "__main__",
        "__builtins__": dict(vars(builtins), __import__=_guarded_import),
        "np": np, "pd": pd, "math": math, "hashlib": hashlib, "_h": _h, "_eq": _eq, "grade": grade,
    }
    errors, results, output = {}, {}, {}
    defined_by = {}   # dəyişən/funksiya adı -> onu yaradan əvvəlki tapşırıq (məs. y_pred -> F1)

    def check(task_id, points, test):
        t = task_id.split("_")[0]
        try:
            res = test()
            if isinstance(res, tuple) and len(res) == 3:
                got, tot, failed = res
                pts = int(points * got / tot + 0.5) if tot else 0
                if pts >= points:
                    results[t] = {"ok": True, "pts": points, "max": points, "partial": False,
                                  "msg": OK_MSG.format(t=t, p=points), "detail": ""}
                    return
                detail = "Ödənməyən hissələr: " + "; ".join(failed)
                if pts > 0:
                    results[t] = {"ok": False, "pts": pts, "max": points, "partial": True,
                                  "msg": PARTIAL_MSG.format(t=t, p=pts, m=points), "detail": detail}
                    return
                if t in errors:
                    detail = errors[t] if errors[t].startswith("`") else "kodunuz icra olunarkən xəta baş verdi → " + errors[t]
                results[t] = {"ok": False, "pts": 0, "max": points, "partial": False,
                              "msg": FAIL_MSG.format(t=t), "detail": detail}
                return
            results[t] = {"ok": True, "pts": points, "max": points, "partial": False,
                          "msg": OK_MSG.format(t=t, p=points), "detail": ""}
            return
        except AssertionError as e:
            detail = str(e) or "test şərti ödənmədi"
        except NameError as e:
            detail = f"tələb olunan dəyişən/funksiya təyin edilməyib ({e})"
        except BaseException as e:
            detail = _describe(e)
        if t in errors:
            detail = errors[t] if errors[t].startswith("`") else "kodunuz icra olunarkən xəta baş verdi → " + errors[t]
        results[t] = {"ok": False, "pts": 0, "max": points, "partial": False,
                      "msg": FAIL_MSG.format(t=t), "detail": detail}

    ns["check"] = check

    for st in steps:
        kind = st["k"]
        if kind == "var":
            ns[st["var"]] = _coerce(answers.get(st["task"]))
            continue
        label = st.get("task")
        code = st["code"]
        if kind == "code" and label in answers and answers[label] is not None:
            code = normalize_code(answers[label])
        out = io.StringIO()
        try:
            _exec_limited(code, ns, budget, out)
        except BaseException as e:
            if label:
                errors[label] = _describe(e)
                # Əvvəlki tapşırığın nəticəsi yoxdursa (məs. F2 üçün F1-in y_pred-i), bunu aydın deyək
                missing = getattr(e, "name", None) if isinstance(e, NameError) else None
                if missing in defined_by and defined_by[missing] != label:
                    src = defined_by[missing]
                    errors[label] = (f"`{missing}` {src} tapşırığında hesablanır, lakin {src} hələ tamamlanmayıb "
                                     f"və ya xəta verir. Əvvəlcə {src}-i düzgün tamamlayın.")
        if kind == "code" and label:
            names = re.findall(r"^\s*([A-Za-z_]\w*)\s*=(?!=)", st["code"], re.M)
            names += re.findall(r"^\s*def\s+([A-Za-z_]\w*)", st["code"], re.M)
            for name in names:
                defined_by.setdefault(name, label)
        if label:
            output[label] = out.getvalue()[-2000:]
        elif kind == "test" and out.getvalue():
            # test zamanı tələbə funksiyasının çap etdikləri
            output[st["ids"][0]] = (output.get(st["ids"][0], "") + out.getvalue())[-2000:]
        if kind == "test" and upto and upto in st["ids"]:
            break

    if upto:
        results = {k: v for k, v in results.items() if k == upto}
        output = {k: v for k, v in output.items() if k == upto}
    return {"results": results, "output": output}


def run_json(payload):
    """Pyodide körpüsü: JSON mətn daxil olur, JSON mətn qayıdır."""
    p = json.loads(payload)
    return json.dumps(run_variant(p["steps"], p.get("answers"), p.get("upto"), p.get("budget", 10.0)),
                      ensure_ascii=False)
'''


def load_harness():
    """HARNESS_SOURCE-u adi Python modulu kimi yükləyir (CPython-da istifadə üçün)."""
    mod = types.ModuleType("sdf1_harness")
    exec(compile(HARNESS_SOURCE, "sdf1_harness", "exec"), mod.__dict__)
    return mod
