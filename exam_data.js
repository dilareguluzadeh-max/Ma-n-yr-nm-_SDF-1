// AVTOMATİK YARADILIB: python tools/build_bank.py — əl ilə redaktə etməyin.
window.EXAM_DATA = {
 "version": 3,
 "harness": "\nimport builtins\nimport contextlib\nimport hashlib\nimport io\nimport json\nimport math\nimport re\nimport sys\nimport time\n\nimport numpy as np\nimport pandas as pd\n\ntry:   # scikit-learn əvvəlcədən yüklənir (testlər zamanı izləmə yavaşlatmasın)\n    import sklearn.linear_model, sklearn.metrics, sklearn.model_selection, sklearn.preprocessing  # noqa: F401\nexcept Exception:\n    pass\n\n# Yalnız təhlükəsizlik üçün zəruri modullar bloklanır; digər standart kitabxanalar (itertools, collections, heapq, bisect, random, os, ...) sərbəstdir\n_BLOCKED_MODULES = (\"js\", \"pyodide\", \"pyodide_js\", \"_pyodide\", \"micropip\", \"subprocess\", \"socket\")\n_real_import = builtins.__import__\n\n\ndef _guarded_import(name, globals=None, locals=None, fromlist=(), level=0):\n    if name.split(\".\")[0] in _BLOCKED_MODULES:\n        raise ImportError(f\"'{name}' modulu imtahanda qadağandır\")\n    return _real_import(name, globals, locals, fromlist, level)\n\n\ndef _h(x):\n    return hashlib.sha256(str(x).strip().lower().encode()).hexdigest()\n\n\ndef _plain(v):\n    \"\"\"numpy/tuple/set tiplərini adi Python siyahı-dəyərlərinə çevirir (tolerant müqayisə üçün).\"\"\"\n    if hasattr(v, \"tolist\"):\n        v = v.tolist()\n    if isinstance(v, (list, tuple)):\n        return [_plain(x) for x in v]\n    if isinstance(v, dict):\n        return {k: _plain(x) for k, x in v.items()}\n    return v\n\n\ndef _eq(a, b):\n    \"\"\"Tolerant bərabərlik: list≈tuple≈ndarray, 1.0≈1, float-lar üçün kiçik xəta payı.\"\"\"\n    a, b = _plain(a), _plain(b)\n    if isinstance(a, list) and isinstance(b, list):\n        return len(a) == len(b) and all(_eq(x, y) for x, y in zip(a, b))\n    if isinstance(a, dict) and isinstance(b, dict):\n        return a.keys() == b.keys() and all(_eq(a[k], b[k]) for k in a)\n    if isinstance(a, float) or isinstance(b, float):\n        try:\n            return math.isclose(a, b, rel_tol=1e-6, abs_tol=1e-9)\n        except TypeError:\n            return False\n    return a == b\n\n\nOK_MSG = \"✅ Tapşırıq {t}: DÜZGÜNDÜR (+{p} bal)\"\nPARTIAL_MSG = \"🟡 Tapşırıq {t}: QİSMƏN DÜZGÜNDÜR (+{p} / {m} bal)\"\nFAIL_MSG = \"❌ Tapşırıq {t}: XƏTA — Çıxış formatı və ya hesablanmış dəyər gözlənilən nəticəyə uyğun deyil!\"\n\n\ndef grade(*items):\n    \"\"\"\n    Qismən bal üçün: items = (çəki, \"yoxlanılan hissə\", çağırıla bilən) ...\n    Hər hissə ayrıca yoxlanılır; ödənən hissələrin çəkisi toplanır.\n    Qaytarır: (qazanılan_çəki, ümumi_çəki, [ödənməyən hissələrin təsviri]).\n    \"\"\"\n    got = tot = 0\n    failed = []\n    for w, label, fn in items:\n        tot += w\n        try:\n            r = fn()\n            if isinstance(r, (bool, np.bool_)) and not r:\n                raise AssertionError\n            got += w\n        except AssertionError:\n            failed.append(label)\n        except Exception as e:\n            failed.append(f\"{label} ({type(e).__name__}: {e})\")\n    return (got, tot, failed)\n\n\ndef _exec_limited(code, ns, budget, out):\n    \"\"\"Kodu vaxt limiti ilə icra edir (sonsuz dövrlər brauzeri dondurmasın).\"\"\"\n    deadline = time.monotonic() + budget\n\n    def tracer(frame, event, arg):\n        if time.monotonic() > deadline:\n            raise TimeoutError(f\"icra {budget:g} saniyədən çox çəkdi (sonsuz dövr ola bilər)\")\n        return tracer\n\n    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):\n        sys.settrace(tracer)\n        try:\n            exec(compile(code, \"<kod>\", \"exec\"), ns)\n        finally:\n            sys.settrace(None)\n\n\n_QUOTES = {\"\\u201c\": '\"', \"\\u201d\": '\"', \"\\u201e\": '\"', \"\\u2018\": \"'\", \"\\u2019\": \"'\", \"\\u00a0\": \" \", \"\\u2009\": \" \",\n           \"\\u200b\": \"\", \"\\u200c\": \"\", \"\\u200d\": \"\", \"\\ufeff\": \"\", \"\\u2013\": \"-\", \"\\u2212\": \"-\"}\n\n\ndef normalize_code(code):\n    \"\"\"\n    Colab/Jupyter-dən gələn kodu tolerant şəkildə qəbul edir:\n    CRLF, sətir başındakı Tab (4 boşluq), görünməz/qeyri-standart simvollar (NBSP, \\u200b), \"ağıllı\" dırnaqlar,\n    ümumi artıq girinti (kod xanası içəridən kopyalananda) və Jupyter sehrli sətirləri (%magic, !əmr) düzəldilir.\n    \"\"\"\n    import textwrap\n    code = str(code).replace(\"\\r\\n\", \"\\n\").replace(\"\\r\", \"\\n\")\n    code = \"\".join(_QUOTES.get(c, c) for c in code)\n    lines = []\n    for ln in code.split(\"\\n\"):\n        stripped = ln.lstrip(\" \\t\")\n        lead = ln[:len(ln) - len(stripped)].replace(\"\\t\", \"    \")\n        if stripped.startswith((\"%\", \"!\")) and not stripped.startswith(\"!=\"):\n            continue                      # Jupyter: %matplotlib inline, !pip install ...\n        lines.append((lead + stripped).rstrip())\n    return textwrap.dedent(\"\\n\".join(lines)).strip(\"\\n\") + \"\\n\"\n\n\ndef _describe(exc):\n    if \"'___'\" in str(exc):\n        return \"`___` boşluqları hələ doldurulmayıb\"\n    if isinstance(exc, IndentationError):\n        return f\"Girinti xətası (sətir {exc.lineno}): {exc.msg}. Bloklardan sonra (:) 4 boşluq girinti qoyun.\"\n    if isinstance(exc, SyntaxError):\n        return f\"Sintaksis xətası (sətir {exc.lineno}): {exc.msg}\"\n    return f\"{type(exc).__name__}: {exc}\"\n\n\ndef _coerce(value):\n    if value is None:\n        return None\n    s = str(value).strip()\n    if s == \"\":\n        return None\n    if re.fullmatch(r\"[+-]?\\d+\", s):\n        return int(s)\n    return s\n\n\ndef run_variant(steps, answers, upto=None, budget=10.0):\n    \"\"\"\n    steps   : exam_data.js-dəki addımlar (tapşırıq ardıcıllığı ilə)\n    answers : {\"A1\": \"<kod>\", \"C1\": \"24\", \"E1\": \"b\", ...}\n    upto    : yalnız bu tapşırığın testinə qədər icra et (\"Test Et\" düyməsi üçün)\n    Nəticə  : {\"results\": {id: {ok, pts, max, msg, detail}}, \"output\": {id: stdout}}\n    \"\"\"\n    answers = answers or {}\n    ns = {\n        \"__name__\": \"__main__\",\n        \"__builtins__\": dict(vars(builtins), __import__=_guarded_import),\n        \"np\": np, \"pd\": pd, \"math\": math, \"hashlib\": hashlib, \"_h\": _h, \"_eq\": _eq, \"grade\": grade,\n    }\n    errors, results, output = {}, {}, {}\n    defined_by = {}   # dəyişən/funksiya adı -> onu yaradan əvvəlki tapşırıq (məs. y_pred -> F1)\n\n    def check(task_id, points, test):\n        t = task_id.split(\"_\")[0]\n        try:\n            res = test()\n            if isinstance(res, tuple) and len(res) == 3:\n                got, tot, failed = res\n                pts = int(points * got / tot + 0.5) if tot else 0\n                if pts >= points:\n                    results[t] = {\"ok\": True, \"pts\": points, \"max\": points, \"partial\": False,\n                                  \"msg\": OK_MSG.format(t=t, p=points), \"detail\": \"\"}\n                    return\n                detail = \"Ödənməyən hissələr: \" + \"; \".join(failed)\n                if pts > 0:\n                    results[t] = {\"ok\": False, \"pts\": pts, \"max\": points, \"partial\": True,\n                                  \"msg\": PARTIAL_MSG.format(t=t, p=pts, m=points), \"detail\": detail}\n                    return\n                if t in errors:\n                    detail = errors[t] if errors[t].startswith(\"`\") else \"kodunuz icra olunarkən xəta baş verdi → \" + errors[t]\n                results[t] = {\"ok\": False, \"pts\": 0, \"max\": points, \"partial\": False,\n                              \"msg\": FAIL_MSG.format(t=t), \"detail\": detail}\n                return\n            results[t] = {\"ok\": True, \"pts\": points, \"max\": points, \"partial\": False,\n                          \"msg\": OK_MSG.format(t=t, p=points), \"detail\": \"\"}\n            return\n        except AssertionError as e:\n            detail = str(e) or \"test şərti ödənmədi\"\n        except NameError as e:\n            detail = f\"tələb olunan dəyişən/funksiya təyin edilməyib ({e})\"\n        except BaseException as e:\n            detail = _describe(e)\n        if t in errors:\n            detail = errors[t] if errors[t].startswith(\"`\") else \"kodunuz icra olunarkən xəta baş verdi → \" + errors[t]\n        results[t] = {\"ok\": False, \"pts\": 0, \"max\": points, \"partial\": False,\n                      \"msg\": FAIL_MSG.format(t=t), \"detail\": detail}\n\n    ns[\"check\"] = check\n\n    for st in steps:\n        kind = st[\"k\"]\n        if kind == \"var\":\n            ns[st[\"var\"]] = _coerce(answers.get(st[\"task\"]))\n            continue\n        label = st.get(\"task\")\n        code = st[\"code\"]\n        if kind == \"code\" and label in answers and answers[label] is not None:\n            code = normalize_code(answers[label])\n        out = io.StringIO()\n        try:\n            _exec_limited(code, ns, budget, out)\n        except BaseException as e:\n            if label:\n                errors[label] = _describe(e)\n                # Əvvəlki tapşırığın nəticəsi yoxdursa (məs. F2 üçün F1-in y_pred-i), bunu aydın deyək\n                missing = getattr(e, \"name\", None) if isinstance(e, NameError) else None\n                if missing in defined_by and defined_by[missing] != label:\n                    src = defined_by[missing]\n                    errors[label] = (f\"`{missing}` {src} tapşırığında hesablanır, lakin {src} hələ tamamlanmayıb \"\n                                     f\"və ya xəta verir. Əvvəlcə {src}-i düzgün tamamlayın.\")\n        if kind == \"code\" and label:\n            names = re.findall(r\"^\\s*([A-Za-z_]\\w*)\\s*=(?!=)\", st[\"code\"], re.M)\n            names += re.findall(r\"^\\s*def\\s+([A-Za-z_]\\w*)\", st[\"code\"], re.M)\n            for name in names:\n                defined_by.setdefault(name, label)\n        if label:\n            output[label] = out.getvalue()[-2000:]\n        elif kind == \"test\" and out.getvalue():\n            # test zamanı tələbə funksiyasının çap etdikləri\n            output[st[\"ids\"][0]] = (output.get(st[\"ids\"][0], \"\") + out.getvalue())[-2000:]\n        if kind == \"test\" and upto and upto in st[\"ids\"]:\n            break\n\n    if upto:\n        results = {k: v for k, v in results.items() if k == upto}\n        output = {k: v for k, v in output.items() if k == upto}\n    return {\"results\": results, \"output\": output}\n\n\ndef run_json(payload):\n    \"\"\"Pyodide körpüsü: JSON mətn daxil olur, JSON mətn qayıdır.\"\"\"\n    p = json.loads(payload)\n    return json.dumps(run_variant(p[\"steps\"], p.get(\"answers\"), p.get(\"upto\"), p.get(\"budget\", 10.0)),\n                      ensure_ascii=False)\n",
 "variants": {
  "A": {
   "name": "Variant A",
   "max_score": 100,
   "items": [
    {
     "type": "task",
     "id": "T1"
    },
    {
     "type": "task",
     "id": "T2"
    },
    {
     "type": "task",
     "id": "T3"
    },
    {
     "type": "task",
     "id": "T4"
    },
    {
     "type": "task",
     "id": "T5"
    },
    {
     "type": "task",
     "id": "T6"
    },
    {
     "type": "task",
     "id": "T7"
    },
    {
     "type": "task",
     "id": "T8"
    },
    {
     "type": "task",
     "id": "T9"
    },
    {
     "type": "task",
     "id": "T10"
    }
   ],
   "tasks": [
    {
     "id": "T1",
     "title": "Tapşırıq T1. Log-transformasiya (log1p) (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T1. Log-transformasiya (log1p) (10 bal)</h4>\n<p><i>Kod tapşırığı · EDA, statistika və preprocessing · qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)</i></p>\n<p><code>np.log1p()</code> ilə <code>'price'</code> sütununun log-transformasiyasını aparın, nəticəni <code>'log_price'</code> adlı yeni sütuna yazın və DataFrame-i <b>qaytarın</b>: <code>log_cevir(df)</code>.</p>",
     "starter": "def log_cevir(df):\n    # buranı yazın\n    pass"
    },
    {
     "id": "T2",
     "title": "Tapşırıq T2. Xətti reqressiyada w və b (10 bal)",
     "pts": 10,
     "kind": "choice",
     "html": "<h4>Tapşırıq T2. Xətti reqressiyada w və b (10 bal)</h4>\n<p><i>Nəzəri sual · Nəzəri anlayış və mövzu · düzgün variantı seçin (yalnız 0 və ya 10 bal)</i></p>\n<p>Sadə Xətti Reqressiya tənliyində <code>y = w * x + b</code> çəki <code>w</code> və kəsişmə <code>b</code> parametrlərinin həndəsi mənası nədir?</p>",
     "options": {
      "a": "<code>w</code> təlim nümunələrinin sayı, <code>b</code> isə sütunların sayıdır",
      "b": "<code>w</code> xəttin <code>y</code> oxunu kəsdiyi nöqtə, <code>b</code> isə yamacdır",
      "c": "<code>w</code> düz xəttin yamacıdır (<code>x</code> 1 vahid artanda <code>y</code>-in dəyişməsi), <code>b</code> isə xəttin <code>y</code> oxunu kəsdiyi nöqtədir (<code>x = 0</code> olduqda <code>y</code>)",
      "d": "<code>w</code> və <code>b</code> verilənlərin ortası və medianıdır"
     }
    },
    {
     "id": "T3",
     "title": "Tapşırıq T3. R² balı (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T3. R² balı (10 bal)</h4>\n<p><i>Kod tapşırığı · Scikit-Learn ilə xətti reqressiya və model qiymətləndirilməsi · qiymətləndirmə: yalnız 0 və ya 10 bal</i></p>\n<p><code>r2_score</code> funksiyası ilə modelin <b>R² balını</b> hesablayıb <b>qaytaran</b> <code>r2_hesabla(y_test, y_pred)</code> funksiyasını yazın.</p>",
     "starter": "def r2_hesabla(y_test, y_pred):\n    # buranı yazın\n    pass"
    },
    {
     "id": "T4",
     "title": "Tapşırıq T4. Əsas statistik xülasə (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T4. Əsas statistik xülasə (10 bal)</h4>\n<p><i>Kod tapşırığı · Pandas ilə verilənlərin oxunması və ilkin baxış · qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)</i></p>\n<p>DataFrame-in <b>ədədi</b> sütunları üçün əsas statistik xülasəni (<code>count, mean, std, min, 25%, 50%, 75%, max</code>) hesablayıb <b>qaytaran</b> <code>statistika(df)</code> funksiyasını yazın (<code>.describe()</code>).</p>",
     "starter": "def statistika(df):\n    # buranı yazın\n    pass"
    },
    {
     "id": "T5",
     "title": "Tapşırıq T5. Modeli öyrətmək (fit) (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T5. Modeli öyrətmək (fit) (10 bal)</h4>\n<p><i>Kod tapşırığı · Scikit-Learn ilə xətti reqressiya və model qiymətləndirilməsi · qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)</i></p>\n<p>Xətti reqressiya modelini <code>(X_train, y_train)</code> üzərində öyrədib <b>öyrədilmiş modeli qaytaran</b> <code>oyret(X_train, y_train)</code> funksiyasını yazın (<code>model.fit(X_train, y_train)</code>).</p>",
     "starter": "def oyret(X_train, y_train):\n    # buranı yazın\n    pass"
    },
    {
     "id": "T6",
     "title": "Tapşırıq T6. Sağa əyilmiş paylanmada mean və median (10 bal)",
     "pts": 10,
     "kind": "choice",
     "html": "<h4>Tapşırıq T6. Sağa əyilmiş paylanmada mean və median (10 bal)</h4>\n<p><i>Nəzəri sual · Nəzəri anlayış və mövzu · düzgün variantı seçin (yalnız 0 və ya 10 bal)</i></p>\n<p>Sağa əyilmiş (right-skewed) paylanmada orta qiymət (mean) və median arasında necə nisbət olur?</p>",
     "options": {
      "a": "Median həmişə meandan böyükdür, çünki kənar qiymətlər medianı yuxarı çəkir",
      "b": "Mean və median həmişə bir-birinə bərabərdir",
      "c": "Mean medianından kiçik olur, çünki sol quyruq uzundur",
      "d": "Mean medianından böyük olur, çünki uzun sağ quyruqdakı böyük qiymətlər ortanı yuxarı çəkir"
     }
    },
    {
     "id": "T7",
     "title": "Tapşırıq T7. Minimum və maksimum (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T7. Minimum və maksimum (10 bal)</h4>\n<p><i>Kod tapşırığı · NumPy ilə massivlər və ədədi hesablamalar · qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)</i></p>\n<p>NumPy massivinin minimum və maksimum qiymətlərini <code>(minimum, maksimum)</code> cütü kimi <b>qaytaran</b> <code>min_maks(arr)</code> funksiyasını yazın (<code>np.min()</code>, <code>np.max()</code>).<br>Nümunə: <code>[4, 9, 1, 7]</code> → <code>(1, 9)</code>.</p>",
     "starter": "def min_maks(arr):\n    # buranı yazın\n    pass"
    },
    {
     "id": "T8",
     "title": "Tapşırıq T8. Normal tənlik və qradient enişi (10 bal)",
     "pts": 10,
     "kind": "choice",
     "html": "<h4>Tapşırıq T8. Normal tənlik və qradient enişi (10 bal)</h4>\n<p><i>Nəzəri sual · Nəzəri anlayış və mövzu · düzgün variantı seçin (yalnız 0 və ya 10 bal)</i></p>\n<p>Xətti reqressiyada analitik həll (Normal Equation / OLS) ilə qradient enişi necə müqayisə olunur?</p>",
     "options": {
      "a": "Qradient enişi həmişə bir addımda həll verir, normal tənlik isə iterativdir",
      "b": "Normal tənlik də <code>alpha</code> və iterasiya sayı tələb edir",
      "c": "İkisi həmişə eyni sayda iterasiya və eyni hesablama xərci tələb edir",
      "d": "Normal tənlik parametrləri bir addımda dəqiq verir və <code>alpha</code> tələb etmir, lakin çox xüsusiyyət olduqda matrisin tərsi bahalıdır; qradient enişi iterativdir, <code>alpha</code> seçilməlidir, böyük verilənlərdə daha əlverişlidir"
     }
    },
    {
     "id": "T9",
     "title": "Tapşırıq T9. Törəmə sütun (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T9. Törəmə sütun (10 bal)</h4>\n<p><i>Kod tapşırığı · Pandas ilə seçim, filtrasiya və dəyişənlərin işlənməsi · qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)</i></p>\n<p><code>'price'</code> və <code>'area'</code> sütunlarından istifadə edərək <code>'price_per_sqm'</code> (<code>price / area</code>) adlı yeni sütun yaradın və DataFrame-i <b>qaytarın</b>: <code>tirem_sutun(df)</code>.</p>",
     "starter": "def tirem_sutun(df):\n    # buranı yazın\n    pass"
    },
    {
     "id": "T10",
     "title": "Tapşırıq T10. Kəşfiyyat xarakterli verilənlər təhlili (EDA) (10 bal)",
     "pts": 10,
     "kind": "choice",
     "html": "<h4>Tapşırıq T10. Kəşfiyyat xarakterli verilənlər təhlili (EDA) (10 bal)</h4>\n<p><i>Nəzəri sual · Nəzəri anlayış və mövzu · düzgün variantı seçin (yalnız 0 və ya 10 bal)</i></p>\n<p>Kəşfiyyat xarakterli verilənlər təhlili (EDA) mərhələsində əsasən hansı sualların cavabı axtarılır?</p>",
     "options": {
      "a": "Sətir və sütun sayı, sütun tipləri, çatışmayan qiymətlər, təkrarlanan sətirlər, paylanmalar və kənar müşahidələr kimi verilənlərin quruluşu ilə bağlı suallar",
      "b": "Modelin hiperparametrlərinin hansı qiymətlərdə ən yaxşı olduğu",
      "c": "Verilənlərin hansı hissəsinin bazadan həmişəlik silinməli olduğu",
      "d": "Yalnız modelin test verilənlərindəki dəqiqliyinin neçə faiz olduğu"
     }
    }
   ],
   "steps": [
    {
     "k": "code",
     "task": "T1",
     "code": "def log_cevir(df):\n    # buranı yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T1"
     ],
     "code": "def test_t1():\n    df = pd.DataFrame({\"price\": [0, 9, 99, 999]})\n    r = log_cevir(df)\n    return grade(\n        (3, \"'log_price' sütunu yaradılmalıdır\", lambda: \"log_price\" in r.columns),\n        (5, \"dəyərlər log(1 + price) olmalıdır\", lambda: _eq(list(r[\"log_price\"]), [0.0, math.log(10), math.log(100), math.log(1000)])),\n        (2, \"'price' sütunu dəyişməməlidir\", lambda: list(r[\"price\"]) == [0, 9, 99, 999]),\n    )\ncheck(\"T1\", 10, test_t1)"
    },
    {
     "k": "var",
     "task": "T2",
     "var": "cavab_T2"
    },
    {
     "k": "test",
     "ids": [
      "T2"
     ],
     "code": "def test_t2():\n    assert _h(cavab_T2) == \"2e7d2c03a9507ae265ecf5b5356885a53393a2029d241394997265a1a25aefc6\", \"cavab düzgün deyil\"\ncheck(\"T2\", 10, test_t2)"
    },
    {
     "k": "code",
     "task": "T3",
     "code": "def r2_hesabla(y_test, y_pred):\n    # buranı yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T3"
     ],
     "code": "def test_t3():\n    assert _eq(r2_hesabla([1, 2, 3, 4], [1, 2, 3, 4]), 1.0), \"mükəmməl proqnozda R² = 1 olmalıdır\"\n    assert _eq(r2_hesabla([1, 2, 3, 4], [2.5, 2.5, 2.5, 2.5]), 0.0), \"orta ilə proqnozda R² = 0 olmalıdır\"\n    assert _eq(r2_hesabla([3, -0.5, 2, 7], [2.5, 0.0, 2, 8]), 0.9486081370449679), \"R² = 0.9486... olmalıdır\"\ncheck(\"T3\", 10, test_t3)"
    },
    {
     "k": "code",
     "task": "T4",
     "code": "def statistika(df):\n    # buranı yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T4"
     ],
     "code": "def test_t4():\n    df = pd.DataFrame({\"a\": [1, 2, 3, 4], \"b\": [10.0, 20.0, 30.0, 40.0], \"c\": list(\"wxyz\")})\n    r = statistika(df)\n    return grade(\n        (2, \"nəticə DataFrame olmalıdır\", lambda: isinstance(r, pd.DataFrame)),\n        (4, \"sətir adları describe() nəticəsi kimi olmalıdır\", lambda: list(r.index) == [\"count\", \"mean\", \"std\", \"min\", \"25%\", \"50%\", \"75%\", \"max\"]),\n        (4, \"yalnız ədədi sütunlar olmalıdır\", lambda: list(r.columns) == [\"a\", \"b\"]),\n    )\ncheck(\"T4\", 10, test_t4)"
    },
    {
     "k": "code",
     "task": "T5",
     "code": "def oyret(X_train, y_train):\n    # buranı yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T5"
     ],
     "code": "def test_t5():\n    rs = np.random.RandomState(0)\n    X_train = rs.rand(40, 2) * 10\n    y_train = 3 * X_train[:, 0] - 2 * X_train[:, 1] + 5\n    X_test = rs.rand(10, 2) * 10\n    m = oyret(X_train, y_train)\n    return grade(\n        (3, \"LinearRegression modeli qaytarılmalıdır\", lambda: type(m).__name__ == \"LinearRegression\"),\n        (3, \"model öyrədilməlidir (fit çağırılmalıdır)\", lambda: hasattr(m, \"coef_\")),\n        (4, \"öyrənilən çəkilər düzgün olmalıdır (3 və -2)\", lambda: np.allclose(m.coef_, [3, -2], atol=1e-6)),\n    )\ncheck(\"T5\", 10, test_t5)"
    },
    {
     "k": "var",
     "task": "T6",
     "var": "cavab_T6"
    },
    {
     "k": "test",
     "ids": [
      "T6"
     ],
     "code": "def test_t6():\n    assert _h(cavab_T6) == \"18ac3e7343f016890c510e93f935261169d9e3f565436429830faf0934f4f8e4\", \"cavab düzgün deyil\"\ncheck(\"T6\", 10, test_t6)"
    },
    {
     "k": "code",
     "task": "T7",
     "code": "def min_maks(arr):\n    # buranı yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T7"
     ],
     "code": "def test_t7():\n    r = min_maks(np.array([4, 9, 1, 7]))\n    return grade(\n        (2, \"nəticə iki elementli olmalıdır\", lambda: len(r) == 2),\n        (4, \"minimum düzgün deyil\", lambda: r[0] == 1),\n        (4, \"maksimum düzgün deyil\", lambda: r[1] == 9),\n    )\ncheck(\"T7\", 10, test_t7)"
    },
    {
     "k": "var",
     "task": "T8",
     "var": "cavab_T8"
    },
    {
     "k": "test",
     "ids": [
      "T8"
     ],
     "code": "def test_t8():\n    assert _h(cavab_T8) == \"18ac3e7343f016890c510e93f935261169d9e3f565436429830faf0934f4f8e4\", \"cavab düzgün deyil\"\ncheck(\"T8\", 10, test_t8)"
    },
    {
     "k": "code",
     "task": "T9",
     "code": "def tirem_sutun(df):\n    # buranı yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T9"
     ],
     "code": "def test_t9():\n    df = pd.DataFrame({\"price\": [100000, 150000, 90000], \"area\": [50, 75, 60]})\n    r = tirem_sutun(df)\n    return grade(\n        (3, \"nəticə DataFrame olmalıdır\", lambda: isinstance(r, pd.DataFrame)),\n        (3, \"'price_per_sqm' sütunu yaradılmalıdır\", lambda: \"price_per_sqm\" in r.columns),\n        (4, \"dəyərlər price / area olmalıdır\", lambda: _eq(list(r[\"price_per_sqm\"]), [2000.0, 2000.0, 1500.0])),\n    )\ncheck(\"T9\", 10, test_t9)"
    },
    {
     "k": "var",
     "task": "T10",
     "var": "cavab_T10"
    },
    {
     "k": "test",
     "ids": [
      "T10"
     ],
     "code": "def test_t10():\n    assert _h(cavab_T10) == \"ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb\", \"cavab düzgün deyil\"\ncheck(\"T10\", 10, test_t10)"
    }
   ]
  },
  "B": {
   "name": "Variant B",
   "max_score": 100,
   "items": [
    {
     "type": "task",
     "id": "T1"
    },
    {
     "type": "task",
     "id": "T2"
    },
    {
     "type": "task",
     "id": "T3"
    },
    {
     "type": "task",
     "id": "T4"
    },
    {
     "type": "task",
     "id": "T5"
    },
    {
     "type": "task",
     "id": "T6"
    },
    {
     "type": "task",
     "id": "T7"
    },
    {
     "type": "task",
     "id": "T8"
    },
    {
     "type": "task",
     "id": "T9"
    },
    {
     "type": "task",
     "id": "T10"
    }
   ],
   "tasks": [
    {
     "id": "T1",
     "title": "Tapşırıq T1. Kənar müşahidə və IQR qaydası (10 bal)",
     "pts": 10,
     "kind": "choice",
     "html": "<h4>Tapşırıq T1. Kənar müşahidə və IQR qaydası (10 bal)</h4>\n<p><i>Nəzəri sual · Nəzəri anlayış və mövzu · düzgün variantı seçin (yalnız 0 və ya 10 bal)</i></p>\n<p>IQR (interkvartil diapazon) qaydası ilə kənar müşahidə (outlier) hədləri necə müəyyən edilir?</p>",
     "options": {
      "a": "<code>IQR</code> standart sapmanın kvadratıdır; hədlər 0 və 1 sabitləridir",
      "b": "<code>IQR = maksimum − minimum</code>; ortalamadan 1.5 IQR uzaq qiymətlər kənardır",
      "c": "<code>IQR = Q3 − Q1</code>; adətən <code>Q1 − 1.5·IQR</code>-dən aşağı və <code>Q3 + 1.5·IQR</code>-dən yuxarı qiymətlər kənar müşahidə sayılır",
      "d": "<code>IQR = Q2 − Q1</code>; yalnız medianın altındakı qiymətlər kənar sayılır"
     }
    },
    {
     "id": "T2",
     "title": "Tapşırıq T2. Əyrilik (skewness) (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T2. Əyrilik (skewness) (10 bal)</h4>\n<p><i>Kod tapşırığı · EDA, statistika və preprocessing · qiymətləndirmə: yalnız 0 və ya 10 bal</i></p>\n<p><code>df[sutun]</code> sütununun <b>əyriliyini</b> (skewness) hesablayıb <b>qaytaran</b> <code>eyrilik(df, sutun)</code> funksiyasını yazın (<code>.skew()</code>).</p>",
     "starter": "def eyrilik(df, sutun):\n    # buranı yazın\n    pass"
    },
    {
     "id": "T3",
     "title": "Tapşırıq T3. Mətn təmizləmə (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T3. Mətn təmizləmə (10 bal)</h4>\n<p><i>Kod tapşırığı · Pandas ilə seçim, filtrasiya və dəyişənlərin işlənməsi · qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)</i></p>\n<p>Mətn sütununun (<code>pd.Series</code>) kənar boşluqlarını silin və kiçik hərflərə çevirin: <code>temizle(seriya)</code> funksiyası nəticəni <b>qaytarsın</b> (<code>.str.strip().str.lower()</code>).<br>Nümunə: <code>\"  Baku \"</code> → <code>\"baku\"</code>.</p>",
     "starter": "def temizle(seriya):\n    # buranı yazın\n    pass"
    },
    {
     "id": "T4",
     "title": "Tapşırıq T4. Cüt ədədlər massivi (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T4. Cüt ədədlər massivi (10 bal)</h4>\n<p><i>Kod tapşırığı · NumPy ilə massivlər və ədədi hesablamalar · qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)</i></p>\n<p>0-dan 10-a qədər (10 daxil) cüt ədədlərdən ibarət NumPy massivini (<code>np.arange()</code> ilə) <b>qaytaran</b> <code>cut_ededler()</code> funksiyasını yazın.<br>Gözlənilən nəticə: <code>[0, 2, 4, 6, 8, 10]</code>.</p>",
     "starter": "def cut_ededler():\n    # buranı yazın\n    pass"
    },
    {
     "id": "T5",
     "title": "Tapşırıq T5. Miqyasa həssaslıq (10 bal)",
     "pts": 10,
     "kind": "choice",
     "html": "<h4>Tapşırıq T5. Miqyasa həssaslıq (10 bal)</h4>\n<p><i>Nəzəri sual · Nəzəri anlayış və mövzu · düzgün variantı seçin (yalnız 0 və ya 10 bal)</i></p>\n<p>Maşın öyrənməsi alqoritmləri verilənlərin miqyasına həssaslığına görə necə təsnif olunur?</p>",
     "options": {
      "a": "Ağac əsaslı alqoritmlər miqyasa ən çox həssasdır, KNN isə heç həssas deyil",
      "b": "Bütün alqoritmlər miqyasa eyni dərəcədə həssasdır",
      "c": "Miqyasa həssaslıq yalnız klasterləşdirmə alqoritmlərinə aiddir",
      "d": "Məsafə və qradient əsaslı alqoritmlər (KNN, SVM, qradient enişi ilə xətti modellər, neyron şəbəkələr) miqyasa həssasdır; ağac əsaslı alqoritmlər (Decision Tree, Random Forest) əsasən həssas deyil"
     }
    },
    {
     "id": "T6",
     "title": "Tapşırıq T6. Sütun seçimi (Series və DataFrame) (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T6. Sütun seçimi (Series və DataFrame) (10 bal)</h4>\n<p><i>Kod tapşırığı · Pandas ilə seçim, filtrasiya və dəyişənlərin işlənməsi · qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)</i></p>\n<p><code>df</code>-dən <code>'study_hours'</code> sütununu <b>Series</b> kimi, <code>['study_hours', 'score']</code> sütunlarını isə <b>DataFrame</b> kimi seçib <code>(seriya, cedvel)</code> cütü şəklində <b>qaytaran</b> <code>sutunlari_sec(df)</code> funksiyasını yazın.</p>",
     "starter": "def sutunlari_sec(df):\n    # buranı yazın\n    pass"
    },
    {
     "id": "T7",
     "title": "Tapşırıq T7. Determinasiya əmsalı (R²) (10 bal)",
     "pts": 10,
     "kind": "choice",
     "html": "<h4>Tapşırıq T7. Determinasiya əmsalı (R²) (10 bal)</h4>\n<p><i>Nəzəri sual · Nəzəri anlayış və mövzu · düzgün variantı seçin (yalnız 0 və ya 10 bal)</i></p>\n<p>Determinasiya əmsalı (R² score) modelin izah etmə qabiliyyətini necə xarakterizə edir?</p>",
     "options": {
      "a": "R² xətaların orta mütləq qiymətidir və hədəflə eyni vahiddədir",
      "b": "R² həmişə 0 ilə 1 arasındadır və mənfi ola bilməz",
      "c": "R² = 0 modelin mükəmməl olduğunu göstərir",
      "d": "<code>R² = 1 − SS_res / SS_tot</code>: hədəfin dəyişkənliyinin modellə izah olunan hissəsini göstərir; 1-ə yaxın yaxşıdır, 0 orta qiymətlə proqnoza bərabərdir, mənfi də ola bilər"
     }
    },
    {
     "id": "T8",
     "title": "Tapşırıq T8. CSV oxumaq və ilk 5 sətir (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T8. CSV oxumaq və ilk 5 sətir (10 bal)</h4>\n<p><i>Kod tapşırığı · Pandas ilə verilənlərin oxunması və ilkin baxış · qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)</i></p>\n<p>Verilmiş <code>fayl</code> yolundakı CSV faylını Pandas ilə oxuyun (<code>pd.read_csv()</code>) və <b>ilk 5 sətri</b> (<code>.head()</code>) DataFrame kimi <b>qaytaran</b> <code>ilk_bes(fayl)</code> funksiyasını yazın.</p>",
     "starter": "def ilk_bes(fayl):\n    # buranı yazın\n    pass"
    },
    {
     "id": "T9",
     "title": "Tapşırıq T9. Reqressiya və klassifikasiya (10 bal)",
     "pts": 10,
     "kind": "choice",
     "html": "<h4>Tapşırıq T9. Reqressiya və klassifikasiya (10 bal)</h4>\n<p><i>Nəzəri sual · Nəzəri anlayış və mövzu · düzgün variantı seçin (yalnız 0 və ya 10 bal)</i></p>\n<p>Reqressiya (regression) və klassifikasiya (classification) məsələlərinin əsas fərqi hansıdır?</p>",
     "options": {
      "a": "Reqressiya diskret sinif, klassifikasiya isə kəsilməz ədədi qiymət proqnozlaşdırır",
      "b": "Reqressiya kəsilməz ədədi qiymət (məsələn, mənzilin qiyməti), klassifikasiya isə diskret sinif (məsələn, spam / spam deyil) proqnozlaşdırır",
      "c": "Fərq yoxdur: hər ikisi eyni hədəf tipinə malikdir və eyni metriklərlə qiymətləndirilir",
      "d": "Reqressiya yalnız xətti, klassifikasiya isə yalnız qeyri-xətti modellərlə həll olunur"
     }
    },
    {
     "id": "T10",
     "title": "Tapşırıq T10. RMSE hesablamaq (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T10. RMSE hesablamaq (10 bal)</h4>\n<p><i>Kod tapşırığı · Scikit-Learn ilə xətti reqressiya və model qiymətləndirilməsi · qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)</i></p>\n<p>MSE göstəricisindən <code>np.sqrt()</code> vasitəsilə <b>RMSE</b> dəyərini hesablayıb <b>qaytaran</b> <code>rmse_hesabla(y_test, y_pred)</code> funksiyasını yazın.</p>",
     "starter": "def rmse_hesabla(y_test, y_pred):\n    # buranı yazın\n    pass"
    }
   ],
   "steps": [
    {
     "k": "var",
     "task": "T1",
     "var": "cavab_T1"
    },
    {
     "k": "test",
     "ids": [
      "T1"
     ],
     "code": "def test_t1():\n    assert _h(cavab_T1) == \"2e7d2c03a9507ae265ecf5b5356885a53393a2029d241394997265a1a25aefc6\", \"cavab düzgün deyil\"\ncheck(\"T1\", 10, test_t1)"
    },
    {
     "k": "code",
     "task": "T2",
     "code": "def eyrilik(df, sutun):\n    # buranı yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T2"
     ],
     "code": "def test_t2():\n    df = pd.DataFrame({\"x\": [1, 2, 2, 3, 3, 3, 4, 20], \"y\": [5, 5, 5, 5, 5, 5, 5, 5.5]})\n    for c in (\"x\", \"y\"):\n        exp = df[c].skew()\n        r = eyrilik(df, c)\n        assert _eq(r, exp), f\"{c} sütunu üçün {exp!r} gözlənilirdi, sizinki: {r!r}\"\ncheck(\"T2\", 10, test_t2)"
    },
    {
     "k": "code",
     "task": "T3",
     "code": "def temizle(seriya):\n    # buranı yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T3"
     ],
     "code": "def test_t3():\n    s = pd.Series([\"  Baku \", \"GANJA\", \" Sumqayit\"])\n    r = temizle(s)\n    return grade(\n        (5, \"kənar boşluqlar silinməlidir\", lambda: [x.strip() for x in r] == list(r) and list(r)[0].startswith(\"b\")),\n        (5, \"bütün hərflər kiçik olmalıdır\", lambda: list(r) == [\"baku\", \"ganja\", \"sumqayit\"]),\n    )\ncheck(\"T3\", 10, test_t3)"
    },
    {
     "k": "code",
     "task": "T4",
     "code": "def cut_ededler():\n    # buranı yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T4"
     ],
     "code": "def test_t4():\n    r = cut_ededler()\n    return grade(\n        (3, \"nəticə NumPy massivi olmalıdır\", lambda: isinstance(r, np.ndarray)),\n        (7, \"elementlər [0, 2, 4, 6, 8, 10] olmalıdır\", lambda: _eq(r, [0, 2, 4, 6, 8, 10])),\n    )\ncheck(\"T4\", 10, test_t4)"
    },
    {
     "k": "var",
     "task": "T5",
     "var": "cavab_T5"
    },
    {
     "k": "test",
     "ids": [
      "T5"
     ],
     "code": "def test_t5():\n    assert _h(cavab_T5) == \"18ac3e7343f016890c510e93f935261169d9e3f565436429830faf0934f4f8e4\", \"cavab düzgün deyil\"\ncheck(\"T5\", 10, test_t5)"
    },
    {
     "k": "code",
     "task": "T6",
     "code": "def sutunlari_sec(df):\n    # buranı yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T6"
     ],
     "code": "def test_t6():\n    df = pd.DataFrame(\n        {\"study_hours\": [5, 2, 8, 6, 4, 9], \"score\": [70, 40, 90, 75, 60, 95], \"attendance\": [85, 60, 95, 80, 70, 100]},\n        index=[\"A01\", \"A02\", \"A03\", \"A04\", \"A05\", \"A06\"],\n    )\n    r = sutunlari_sec(df)\n    return grade(\n        (2, \"nəticə iki elementli olmalıdır\", lambda: len(r) == 2),\n        (4, \"birinci nəticə Series olmalıdır (study_hours)\", lambda: isinstance(r[0], pd.Series) and list(r[0]) == [5, 2, 8, 6, 4, 9]),\n        (4, \"ikinci nəticə iki sütunlu DataFrame olmalıdır\", lambda: isinstance(r[1], pd.DataFrame) and list(r[1].columns) == [\"study_hours\", \"score\"]),\n    )\ncheck(\"T6\", 10, test_t6)"
    },
    {
     "k": "var",
     "task": "T7",
     "var": "cavab_T7"
    },
    {
     "k": "test",
     "ids": [
      "T7"
     ],
     "code": "def test_t7():\n    assert _h(cavab_T7) == \"18ac3e7343f016890c510e93f935261169d9e3f565436429830faf0934f4f8e4\", \"cavab düzgün deyil\"\ncheck(\"T7\", 10, test_t7)"
    },
    {
     "k": "code",
     "task": "T8",
     "code": "def ilk_bes(fayl):\n    # buranı yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T8"
     ],
     "code": "def test_t8():\n    import os, tempfile\n    _p = os.path.join(tempfile.gettempdir(), \"imtahan_students.csv\")\n    with open(_p, \"w\", encoding=\"utf-8\") as _f:\n        _f.write(\"id,study_hours,score\\n\" + \"\\n\".join(f\"{i},{i + 1},{50 + i}\" for i in range(1, 9)) + \"\\n\")\n    r = ilk_bes(_p)\n    return grade(\n        (3, \"nəticə DataFrame olmalıdır\", lambda: isinstance(r, pd.DataFrame)),\n        (4, \"yalnız ilk 5 sətir qaytarılmalıdır\", lambda: len(r) == 5),\n        (3, \"sütun adları faylla eyni olmalıdır\", lambda: list(r.columns) == [\"id\", \"study_hours\", \"score\"]),\n    )\ncheck(\"T8\", 10, test_t8)"
    },
    {
     "k": "var",
     "task": "T9",
     "var": "cavab_T9"
    },
    {
     "k": "test",
     "ids": [
      "T9"
     ],
     "code": "def test_t9():\n    assert _h(cavab_T9) == \"3e23e8160039594a33894f6564e1b1348bbd7a0088d42c4acb73eeaed59c009d\", \"cavab düzgün deyil\"\ncheck(\"T9\", 10, test_t9)"
    },
    {
     "k": "code",
     "task": "T10",
     "code": "def rmse_hesabla(y_test, y_pred):\n    # buranı yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T10"
     ],
     "code": "def test_t10():\n    return grade(\n        (5, \"[0, 0] və [3, 4] üçün RMSE = sqrt(12.5)\", lambda: _eq(rmse_hesabla([0, 0], [3, 4]), math.sqrt(12.5))),\n        (3, \"[2, 4, 6] və [3, 3, 9] üçün RMSE = sqrt(11/3)\", lambda: _eq(rmse_hesabla([2, 4, 6], [3, 3, 9]), math.sqrt(11 / 3))),\n        (2, \"mükəmməl proqnozda RMSE = 0\", lambda: _eq(rmse_hesabla([1, 2], [1, 2]), 0.0)),\n    )\ncheck(\"T10\", 10, test_t10)"
    }
   ]
  },
  "C": {
   "name": "Variant C",
   "max_score": 100,
   "items": [
    {
     "type": "task",
     "id": "T1"
    },
    {
     "type": "task",
     "id": "T2"
    },
    {
     "type": "task",
     "id": "T3"
    },
    {
     "type": "task",
     "id": "T4"
    },
    {
     "type": "task",
     "id": "T5"
    },
    {
     "type": "task",
     "id": "T6"
    },
    {
     "type": "task",
     "id": "T7"
    },
    {
     "type": "task",
     "id": "T8"
    },
    {
     "type": "task",
     "id": "T9"
    },
    {
     "type": "task",
     "id": "T10"
    }
   ],
   "tasks": [
    {
     "id": "T1",
     "title": "Tapşırıq T1. 1D massivi 2x3 matrisə çevirmək (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T1. 1D massivi 2x3 matrisə çevirmək (10 bal)</h4>\n<p><i>Kod tapşırığı · NumPy ilə massivlər və ədədi hesablamalar · qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)</i></p>\n<p>6 elementli 1D <code>arr</code> massivini <code>2x3</code> ölçülü 2D matrisə çevirib <b>qaytaran</b> <code>matrise_cevir(arr)</code> funksiyasını yazın (<code>.reshape(2, 3)</code>).</p>",
     "starter": "def matrise_cevir(arr):\n    # buranı yazın\n    pass"
    },
    {
     "id": "T2",
     "title": "Tapşırıq T2. Medianla doldurmaq (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T2. Medianla doldurmaq (10 bal)</h4>\n<p><i>Kod tapşırığı · EDA, statistika və preprocessing · qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)</i></p>\n<p><code>df[sutun]</code> sütunundakı çatışmayan (<code>NaN</code>) qiymətləri həmin sütunun <b>medianı</b> ilə doldurub nəticəni (<code>Series</code>) <b>qaytaran</b> <code>median_ile_doldur(df, sutun)</code> funksiyasını yazın (<code>fillna(df[sutun].median())</code>).</p>",
     "starter": "def median_ile_doldur(df, sutun):\n    # buranı yazın\n    pass"
    },
    {
     "id": "T3",
     "title": "Tapşırıq T3. İki şərtlə filtr (&) (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T3. İki şərtlə filtr (&amp;) (10 bal)</h4>\n<p><i>Kod tapşırığı · Pandas ilə seçim, filtrasiya və dəyişənlərin işlənməsi · qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)</i></p>\n<p><code>'attendance' &gt;= 80</code> <b>VƏ</b> <code>'study_hours' &gt;= 5</code> şərtlərini eyni vaxtda ödəyən sətirləri <code>&amp;</code> operatoru ilə seçib <b>qaytaran</b> <code>iki_sert_filtr(df)</code> funksiyasını yazın.</p>",
     "starter": "def iki_sert_filtr(df):\n    # buranı yazın\n    pass"
    },
    {
     "id": "T4",
     "title": "Tapşırıq T4. Bazis (baseline) model (10 bal)",
     "pts": 10,
     "kind": "choice",
     "html": "<h4>Tapşırıq T4. Bazis (baseline) model (10 bal)</h4>\n<p><i>Nəzəri sual · Nəzəri anlayış və mövzu · düzgün variantı seçin (yalnız 0 və ya 10 bal)</i></p>\n<p>Bazis (baseline) model anlayışı və mürəkkəb modellərdən əvvəl tətbiqinin əhəmiyyəti nədir?</p>",
     "options": {
      "a": "Bazis model təlim verilənləri olmadan yalnız test verilənləri üzərində qurulur",
      "b": "Bazis model yalnız dərin neyron şəbəkələr üçün istifadə olunur",
      "c": "Bazis model ən yaxşı mümkün modeldir və ondan sonra başqa model sınamağa ehtiyac qalmır",
      "d": "Bazis model sadə referans modeldir (məsələn, hədəfin ortası və ya medianı); mürəkkəb modelin həqiqətən fayda verdiyini müqayisə etmək üçün minimum standart rolunu oynayır"
     }
    },
    {
     "id": "T5",
     "title": "Tapşırıq T5. Shape və dtypes (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T5. Shape və dtypes (10 bal)</h4>\n<p><i>Kod tapşırığı · Pandas ilə verilənlərin oxunması və ilkin baxış · qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)</i></p>\n<p>DataFrame-in ölçüsünü və sütun tiplərini <code>(df.shape, df.dtypes)</code> cütü kimi <b>qaytaran</b> <code>olcu_ve_tipler(df)</code> funksiyasını yazın.</p>",
     "starter": "def olcu_ve_tipler(df):\n    # buranı yazın\n    pass"
    },
    {
     "id": "T6",
     "title": "Tapşırıq T6. Multikolinearlıq (10 bal)",
     "pts": 10,
     "kind": "choice",
     "html": "<h4>Tapşırıq T6. Multikolinearlıq (10 bal)</h4>\n<p><i>Nəzəri sual · Nəzəri anlayış və mövzu · düzgün variantı seçin (yalnız 0 və ya 10 bal)</i></p>\n<p>Multikolinearlıq (multicollinearity) problemi Xətti Reqressiya modelinin çəkilərinə necə təsir edir?</p>",
     "options": {
      "a": "Hədəflə xüsusiyyətlər arasında korrelyasiya olmadıqda yaranır və bütün çəkiləri sıfır edir",
      "b": "Yalnız çatışmayan qiymətlər olduqda yaranır və çəkilərə təsir etmir",
      "c": "Müstəqil dəyişənlər bir-biri ilə yüksək korrelyasiyalı olduqda çəkilər qeyri-sabit olur, verilənlərdəki kiçik dəyişiklikdən kəskin dəyişir və şərh etmək çətinləşir",
      "d": "Çəkilər daha sabit olur, çünki modelə əlavə eyni məlumat verilir"
     }
    },
    {
     "id": "T7",
     "title": "Tapşırıq T7. Test üçün proqnoz (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T7. Test üçün proqnoz (10 bal)</h4>\n<p><i>Kod tapşırığı · Scikit-Learn ilə xətti reqressiya və model qiymətləndirilməsi · qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)</i></p>\n<p>Öyrədilmiş <code>model</code> vasitəsilə <code>X_test</code> üçün proqnozları (<code>y_pred</code>) hesablayıb <b>qaytaran</b> <code>proqnoz_ver(model, X_test)</code> funksiyasını yazın (<code>model.predict(X_test)</code>).</p>",
     "starter": "def proqnoz_ver(model, X_test):\n    # buranı yazın\n    pass"
    },
    {
     "id": "T8",
     "title": "Tapşırıq T8. Log-transformasiya (np.log1p) (10 bal)",
     "pts": 10,
     "kind": "choice",
     "html": "<h4>Tapşırıq T8. Log-transformasiya (np.log1p) (10 bal)</h4>\n<p><i>Nəzəri sual · Nəzəri anlayış və mövzu · düzgün variantı seçin (yalnız 0 və ya 10 bal)</i></p>\n<p><code>np.log1p(x)</code> əməliyyatının mahiyyəti və xətti modellərə təsiri haqqında hansı ifadə düzgündür?</p>",
     "options": {
      "a": "Yalnız mənfi ədədlərə tətbiq oluna bilər və qiymətləri 0–1 intervalına salır",
      "b": "<code>log(1 + x)</code> hesablayır: böyük qiymətləri sıxaraq sağ əyriliyi azaldır, <code>x = 0</code> üçün də təyin olunub və xətti modelin işini yaxşılaşdıra bilər",
      "c": "Verilənlərin paylanmasına heç bir təsir göstərmir, yalnız sütunun adını dəyişir",
      "d": "Paylanmanı daha da sağa əyir və kənar qiymətlərin təsirini artırır"
     }
    },
    {
     "id": "T9",
     "title": "Tapşırıq T9. Hər sütunda çatışmayan qiymətlər (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T9. Hər sütunda çatışmayan qiymətlər (10 bal)</h4>\n<p><i>Kod tapşırığı · Pandas ilə verilənlərin oxunması və ilkin baxış · qiymətləndirmə: yalnız 0 və ya 10 bal</i></p>\n<p>DataFrame-in hər sütununda neçə çatışmayan (<code>NaN</code>) qiymət olduğunu <b>qaytaran</b> <code>catismayanlar(df)</code> funksiyasını yazın (<code>df.isna().sum()</code>).</p>",
     "starter": "def catismayanlar(df):\n    # buranı yazın\n    pass"
    },
    {
     "id": "T10",
     "title": "Tapşırıq T10. MAE və RMSE fərqi (10 bal)",
     "pts": 10,
     "kind": "choice",
     "html": "<h4>Tapşırıq T10. MAE və RMSE fərqi (10 bal)</h4>\n<p><i>Nəzəri sual · Nəzəri anlayış və mövzu · düzgün variantı seçin (yalnız 0 və ya 10 bal)</i></p>\n<p>Reqressiya metrikləri MAE və RMSE arasındakı əsas fərq nədir?</p>",
     "options": {
      "a": "RMSE kənar qiymətlərə MAE-dən daha az həssasdır",
      "b": "MAE mütləq xətaların ortasıdır və hədəflə eyni vahiddədir; RMSE xətaları kvadrata yüksəldir, ona görə böyük xətalara (kənar qiymətlərə) daha həssasdır",
      "c": "RMSE həmişə MAE-dən kiçik olur",
      "d": "MAE xətaların kvadratına, RMSE isə mütləq qiymətinə əsaslanır"
     }
    }
   ],
   "steps": [
    {
     "k": "code",
     "task": "T1",
     "code": "def matrise_cevir(arr):\n    # buranı yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T1"
     ],
     "code": "def test_t1():\n    r = matrise_cevir(np.array([1, 2, 3, 4, 5, 6]))\n    return grade(\n        (5, \"shape (2, 3) olmalıdır\", lambda: tuple(r.shape) == (2, 3)),\n        (5, \"elementlərin sırası saxlanmalıdır\", lambda: _eq(r, [[1, 2, 3], [4, 5, 6]])),\n    )\ncheck(\"T1\", 10, test_t1)"
    },
    {
     "k": "code",
     "task": "T2",
     "code": "def median_ile_doldur(df, sutun):\n    # buranı yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T2"
     ],
     "code": "def test_t2():\n    df = pd.DataFrame({\"x\": [1.0, None, 3.0, 100.0, None]})\n    r = median_ile_doldur(df, \"x\")\n    return grade(\n        (4, \"çatışmayan qiymət qalmamalıdır\", lambda: int(pd.isna(r).sum()) == 0),\n        (4, \"boşluqlar medianla (3.0) doldurulmalıdır, orta ilə yox\", lambda: _eq(list(r), [1.0, 3.0, 3.0, 100.0, 3.0])),\n        (2, \"mövcud qiymətlər dəyişməməlidir\", lambda: list(r)[0] == 1.0 and list(r)[3] == 100.0),\n    )\ncheck(\"T2\", 10, test_t2)"
    },
    {
     "k": "code",
     "task": "T3",
     "code": "def iki_sert_filtr(df):\n    # buranı yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T3"
     ],
     "code": "def test_t3():\n    df = pd.DataFrame(\n        {\"study_hours\": [5, 2, 8, 6, 4, 9], \"score\": [70, 40, 90, 75, 60, 95], \"attendance\": [85, 60, 95, 80, 70, 100]},\n        index=[\"A01\", \"A02\", \"A03\", \"A04\", \"A05\", \"A06\"],\n    )\n    r = iki_sert_filtr(df)\n    return grade(\n        (5, \"sətirlərin sayı düzgün deyil (4 sətir gözlənilir)\", lambda: len(r) == 4),\n        (5, \"seçilən sətirlər düzgün deyil\", lambda: list(r.index) == [\"A01\", \"A03\", \"A04\", \"A06\"]),\n    )\ncheck(\"T3\", 10, test_t3)"
    },
    {
     "k": "var",
     "task": "T4",
     "var": "cavab_T4"
    },
    {
     "k": "test",
     "ids": [
      "T4"
     ],
     "code": "def test_t4():\n    assert _h(cavab_T4) == \"18ac3e7343f016890c510e93f935261169d9e3f565436429830faf0934f4f8e4\", \"cavab düzgün deyil\"\ncheck(\"T4\", 10, test_t4)"
    },
    {
     "k": "code",
     "task": "T5",
     "code": "def olcu_ve_tipler(df):\n    # buranı yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T5"
     ],
     "code": "def test_t5():\n    df = pd.DataFrame({\"a\": [1, 2, 3], \"b\": [1.5, 2.5, 3.5], \"c\": [\"x\", \"y\", \"z\"]})\n    r = olcu_ve_tipler(df)\n    return grade(\n        (2, \"nəticə iki elementli olmalıdır\", lambda: len(r) == 2),\n        (4, \"shape (3, 3) olmalıdır\", lambda: tuple(r[0]) == (3, 3)),\n        (4, \"sütun tipləri düzgün deyil\", lambda: {k: str(v) for k, v in dict(r[1]).items()} in ({\"a\": \"int64\", \"b\": \"float64\", \"c\": \"object\"}, {\"a\": \"int64\", \"b\": \"float64\", \"c\": \"str\"}, {\"a\": \"int64\", \"b\": \"float64\", \"c\": \"string\"})),\n    )\ncheck(\"T5\", 10, test_t5)"
    },
    {
     "k": "var",
     "task": "T6",
     "var": "cavab_T6"
    },
    {
     "k": "test",
     "ids": [
      "T6"
     ],
     "code": "def test_t6():\n    assert _h(cavab_T6) == \"2e7d2c03a9507ae265ecf5b5356885a53393a2029d241394997265a1a25aefc6\", \"cavab düzgün deyil\"\ncheck(\"T6\", 10, test_t6)"
    },
    {
     "k": "code",
     "task": "T7",
     "code": "def proqnoz_ver(model, X_test):\n    # buranı yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T7"
     ],
     "code": "def test_t7():\n    rs = np.random.RandomState(0)\n    X_train = rs.rand(40, 2) * 10\n    y_train = 3 * X_train[:, 0] - 2 * X_train[:, 1] + 5\n    X_test = rs.rand(10, 2) * 10\n    from sklearn.linear_model import LinearRegression\n    model = LinearRegression().fit(X_train, y_train)\n    r = proqnoz_ver(model, X_test)\n    return grade(\n        (3, \"hər test nümunəsi üçün bir proqnoz olmalıdır (10 ədəd)\", lambda: len(r) == 10),\n        (7, \"proqnoz dəyərləri düzgün deyil\", lambda: np.allclose(r, model.predict(X_test))),\n    )\ncheck(\"T7\", 10, test_t7)"
    },
    {
     "k": "var",
     "task": "T8",
     "var": "cavab_T8"
    },
    {
     "k": "test",
     "ids": [
      "T8"
     ],
     "code": "def test_t8():\n    assert _h(cavab_T8) == \"3e23e8160039594a33894f6564e1b1348bbd7a0088d42c4acb73eeaed59c009d\", \"cavab düzgün deyil\"\ncheck(\"T8\", 10, test_t8)"
    },
    {
     "k": "code",
     "task": "T9",
     "code": "def catismayanlar(df):\n    # buranı yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T9"
     ],
     "code": "def test_t9():\n    df = pd.DataFrame({\"a\": [1, None, 3, None], \"b\": [None, 2, 3, 4], \"c\": [1, 2, 3, 4]})\n    r = catismayanlar(df)\n    assert dict(r) == {\"a\": 2, \"b\": 1, \"c\": 0}, f\"hər sütun üçün NaN sayı {{'a': 2, 'b': 1, 'c': 0}} olmalıdır, sizinki: {dict(r)}\"\ncheck(\"T9\", 10, test_t9)"
    },
    {
     "k": "var",
     "task": "T10",
     "var": "cavab_T10"
    },
    {
     "k": "test",
     "ids": [
      "T10"
     ],
     "code": "def test_t10():\n    assert _h(cavab_T10) == \"3e23e8160039594a33894f6564e1b1348bbd7a0088d42c4acb73eeaed59c009d\", \"cavab düzgün deyil\"\ncheck(\"T10\", 10, test_t10)"
    }
   ]
  },
  "D": {
   "name": "Variant D",
   "max_score": 100,
   "items": [
    {
     "type": "task",
     "id": "T1"
    },
    {
     "type": "task",
     "id": "T2"
    },
    {
     "type": "task",
     "id": "T3"
    },
    {
     "type": "task",
     "id": "T4"
    },
    {
     "type": "task",
     "id": "T5"
    },
    {
     "type": "task",
     "id": "T6"
    },
    {
     "type": "task",
     "id": "T7"
    },
    {
     "type": "task",
     "id": "T8"
    },
    {
     "type": "task",
     "id": "T9"
    },
    {
     "type": "task",
     "id": "T10"
    }
   ],
   "tasks": [
    {
     "id": "T1",
     "title": "Tapşırıq T1. Verilənlər sızması (data leakage) (10 bal)",
     "pts": 10,
     "kind": "choice",
     "html": "<h4>Tapşırıq T1. Verilənlər sızması (data leakage) (10 bal)</h4>\n<p><i>Nəzəri sual · Nəzəri anlayış və mövzu · düzgün variantı seçin (yalnız 0 və ya 10 bal)</i></p>\n<p>Verilənlər sızması (data leakage) nədir və train/test bölgüsü necə aparılmalıdır?</p>",
     "options": {
      "a": "Test verilənlərindən məlumatın təlim prosesinə keçməsidir (məsələn, bölgüdən əvvəl bütün verilənlərə scaler fit etmək); düzgün yol əvvəl bölmək, ön emalı yalnız train-də fit etmək, test-ə yalnız transform tətbiq etməkdir",
      "b": "Test verilənlərini də təlimdə istifadə etmək dəqiqliyi artırdığı üçün düzgün və tövsiyə olunan yoldur",
      "c": "Yalnız hədəf sütunun adı dəyişdikdə baş verir və bölgüyə aid deyil",
      "d": "Verilənlərin bir hissəsinin itməsidir; bölgüdən əvvəl bütün verilənlərə scaler fit etmək məsləhət görülür"
     }
    },
    {
     "id": "T2",
     "title": "Tapşırıq T2. Kateqorik sütunun nisbətləri (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T2. Kateqorik sütunun nisbətləri (10 bal)</h4>\n<p><i>Kod tapşırığı · Pandas ilə verilənlərin oxunması və ilkin baxış · qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)</i></p>\n<p><code>df[sutun]</code> kateqorik sütunundakı unikal dəyərlərin <b>nisbətlərini</b> (cəmi 1) <b>qaytaran</b> <code>nisbetler(df, sutun)</code> funksiyasını yazın (<code>value_counts(normalize=True)</code>).</p>",
     "starter": "def nisbetler(df, sutun):\n    # buranı yazın\n    pass"
    },
    {
     "id": "T3",
     "title": "Tapşırıq T3. Massivin orta qiyməti (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T3. Massivin orta qiyməti (10 bal)</h4>\n<p><i>Kod tapşırığı · NumPy ilə massivlər və ədədi hesablamalar · qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)</i></p>\n<p><code>scores</code> NumPy massivinin orta qiymətini <code>np.mean()</code> ilə hesablayıb <b>qaytaran</b> <code>ortalama_hesabla(scores)</code> funksiyasını yazın.<br>Nümunə: <code>np.array([70, 80, 90])</code> → <code>80.0</code>.</p>",
     "starter": "def ortalama_hesabla(scores):\n    # buranı yazın\n    pass"
    },
    {
     "id": "T4",
     "title": "Tapşırıq T4. Maşın öyrənməsi və nəzarətli öyrənmənin qolları (10 bal)",
     "pts": 10,
     "kind": "choice",
     "html": "<h4>Tapşırıq T4. Maşın öyrənməsi və nəzarətli öyrənmənin qolları (10 bal)</h4>\n<p><i>Nəzəri sual · Nəzəri anlayış və mövzu · düzgün variantı seçin (yalnız 0 və ya 10 bal)</i></p>\n<p>Maşın öyrənməsi (Machine Learning) anlayışı və nəzarətli öyrənmənin (supervised learning) əsas qolları haqqında hansı ifadə düzgündür?</p>",
     "options": {
      "a": "Nəzarətli öyrənmə etiketsiz verilənlərlə işləyir və yalnız qruplaşdırma aparır",
      "b": "Maşın öyrənməsi alqoritmin qanunauyğunluqları açıq qaydalar yazılmadan verilənlərdən öyrənməsidir; nəzarətli öyrənmənin əsas qolları reqressiya və klassifikasiyadır",
      "c": "Nəzarətli öyrənmə yalnız şəkil tanıma məsələlərinə aiddir, reqressiya buraya daxil deyil",
      "d": "Maşın öyrənməsi bütün qaydaların proqramçı tərəfindən əl ilə yazılmasıdır; nəzarətli öyrənmənin qolları klasterləşdirmə və ölçü azaldılmasıdır"
     }
    },
    {
     "id": "T5",
     "title": "Tapşırıq T5. Sıfırlardan ibarət massiv (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T5. Sıfırlardan ibarət massiv (10 bal)</h4>\n<p><i>Kod tapşırığı · NumPy ilə massivlər və ədədi hesablamalar · qiymətləndirmə: yalnız 0 və ya 10 bal</i></p>\n<p>Bütün elementləri sıfır olan <code>2x3</code> ölçülü NumPy massivini (<code>np.zeros()</code> ilə) <b>qaytaran</b> <code>sifir_massiv()</code> funksiyasını yazın.</p>",
     "starter": "def sifir_massiv():\n    # buranı yazın\n    pass"
    },
    {
     "id": "T6",
     "title": "Tapşırıq T6. MSE-də kvadratik xəta (10 bal)",
     "pts": 10,
     "kind": "choice",
     "html": "<h4>Tapşırıq T6. MSE-də kvadratik xəta (10 bal)</h4>\n<p><i>Nəzəri sual · Nəzəri anlayış və mövzu · düzgün variantı seçin (yalnız 0 və ya 10 bal)</i></p>\n<p>Orta Kvadratik Xəta (MSE) məsrəf funksiyasında xətanın kvadratının alınmasının riyazi üstünlüyü nədir?</p>",
     "options": {
      "a": "Xətanı kiçildir və nəticəni hədəflə eyni ölçü vahidində saxlayır",
      "b": "Mütləq dəyər kimi hər nöqtədə diferensiallanır və kənar qiymətlərə qətiyyən həssas deyil",
      "c": "Yalnız mənfi xətaları müsbətə çevirir, böyük xətaların təsiri dəyişmir",
      "d": "Xətanın işarəsini aradan qaldırır, böyük xətaları daha çox cəzalandırır və hamar, diferensiallanan funksiya verdiyi üçün qradient eniş üçün əlverişlidir"
     }
    },
    {
     "id": "T7",
     "title": "Tapşırıq T7. iloc ilə seçim (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T7. iloc ilə seçim (10 bal)</h4>\n<p><i>Kod tapşırığı · Pandas ilə seçim, filtrasiya və dəyişənlərin işlənməsi · qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)</i></p>\n<p><code>df.iloc</code> vasitəsilə DataFrame-in <b>ilk 3 sətrini</b> və <b>ilk 2 sütununu</b> seçib <b>qaytaran</b> <code>iloc_ile(df)</code> funksiyasını yazın.</p>",
     "starter": "def iloc_ile(df):\n    # buranı yazın\n    pass"
    },
    {
     "id": "T8",
     "title": "Tapşırıq T8. Pirson korrelyasiyası (r = 0) (10 bal)",
     "pts": 10,
     "kind": "choice",
     "html": "<h4>Tapşırıq T8. Pirson korrelyasiyası (r = 0) (10 bal)</h4>\n<p><i>Nəzəri sual · Nəzəri anlayış və mövzu · düzgün variantı seçin (yalnız 0 və ya 10 bal)</i></p>\n<p>İki dəyişən arasında Pirson korrelyasiya əmsalı <code>r = 0</code> olarsa, nə demək olar?</p>",
     "options": {
      "a": "Hər iki dəyişən mütləq sabit qiymətlərdir",
      "b": "Dəyişənlər tam müstəqildir, heç bir asılılıq ola bilməz",
      "c": "Aralarında xətti asılılıq yoxdur, lakin qeyri-xətti asılılıq (məsələn, parabolik) hələ də mövcud ola bilər",
      "d": "Dəyişənlər arasında mükəmməl mənfi xətti asılılıq var"
     }
    },
    {
     "id": "T9",
     "title": "Tapşırıq T9. LinearRegression obyekti (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T9. LinearRegression obyekti (10 bal)</h4>\n<p><i>Kod tapşırığı · Scikit-Learn ilə xətti reqressiya və model qiymətləndirilməsi · qiymətləndirmə: yalnız 0 və ya 10 bal</i></p>\n<p><code>sklearn.linear_model</code> modulundan <code>LinearRegression</code> modelini idxal edin və yeni (təlim olunmamış) model obyektini <b>qaytaran</b> <code>model_yarat()</code> funksiyasını yazın.</p>",
     "starter": "def model_yarat():\n    # buranı yazın\n    pass"
    },
    {
     "id": "T10",
     "title": "Tapşırıq T10. Stratify ilə bölgü (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T10. Stratify ilə bölgü (10 bal)</h4>\n<p><i>Kod tapşırığı · EDA, statistika və preprocessing · qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)</i></p>\n<p>Klassifikasiya məsələsində sinif balansını qorumaq üçün <code>X</code> və <code>y</code>-ni <code>stratify=y</code> parametri ilə <code>test_size=0.2</code> nisbətində bölün və <code>X_train, X_test, y_train, y_test</code> <b>qaytaran</b> <code>strat_bol(X, y)</code> funksiyasını yazın.</p>",
     "starter": "def strat_bol(X, y):\n    # buranı yazın\n    pass"
    }
   ],
   "steps": [
    {
     "k": "var",
     "task": "T1",
     "var": "cavab_T1"
    },
    {
     "k": "test",
     "ids": [
      "T1"
     ],
     "code": "def test_t1():\n    assert _h(cavab_T1) == \"ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb\", \"cavab düzgün deyil\"\ncheck(\"T1\", 10, test_t1)"
    },
    {
     "k": "code",
     "task": "T2",
     "code": "def nisbetler(df, sutun):\n    # buranı yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T2"
     ],
     "code": "def test_t2():\n    df = pd.DataFrame({\"city\": [\"Baku\", \"Baku\", \"Ganja\", \"Baku\", \"Sumqayit\", \"Ganja\", \"Baku\", \"Baku\"]})\n    r = nisbetler(df, \"city\")\n    return grade(\n        (6, \"nisbətlər düzgün deyil (Baku=0.625, Ganja=0.25, Sumqayit=0.125)\", lambda: _eq(dict(r), {\"Baku\": 0.625, \"Ganja\": 0.25, \"Sumqayit\": 0.125})),\n        (2, \"nisbətlərin cəmi 1 olmalıdır\", lambda: abs(float(sum(r)) - 1.0) < 1e-9),\n        (2, \"ən çox təkrarlanan dəyər birinci olmalıdır\", lambda: r.index[0] == \"Baku\"),\n    )\ncheck(\"T2\", 10, test_t2)"
    },
    {
     "k": "code",
     "task": "T3",
     "code": "def ortalama_hesabla(scores):\n    # buranı yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T3"
     ],
     "code": "def test_t3():\n    return grade(\n        (4, \"tam ədədlərdən massiv\", lambda: _eq(ortalama_hesabla(np.array([70, 80, 90])), 80.0)),\n        (3, \"mənfi və kəsr qiymətli massiv\", lambda: _eq(ortalama_hesabla(np.array([-2.5, 4.0, 1.5, 9.0])), 3.0)),\n        (3, \"nəticə tək ədəd olmalıdır (massiv yox)\", lambda: isinstance(ortalama_hesabla(np.array([1, 2, 3])), (int, float, np.number))),\n    )\ncheck(\"T3\", 10, test_t3)"
    },
    {
     "k": "var",
     "task": "T4",
     "var": "cavab_T4"
    },
    {
     "k": "test",
     "ids": [
      "T4"
     ],
     "code": "def test_t4():\n    assert _h(cavab_T4) == \"3e23e8160039594a33894f6564e1b1348bbd7a0088d42c4acb73eeaed59c009d\", \"cavab düzgün deyil\"\ncheck(\"T4\", 10, test_t4)"
    },
    {
     "k": "code",
     "task": "T5",
     "code": "def sifir_massiv():\n    # buranı yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T5"
     ],
     "code": "def test_t5():\n    r = sifir_massiv()\n    assert isinstance(r, np.ndarray), \"nəticə NumPy massivi olmalıdır\"\n    assert r.shape == (2, 3), f\"shape (2, 3) olmalıdır, sizinki: {r.shape}\"\n    assert (r == 0).all(), \"bütün elementlər 0 olmalıdır\"\ncheck(\"T5\", 10, test_t5)"
    },
    {
     "k": "var",
     "task": "T6",
     "var": "cavab_T6"
    },
    {
     "k": "test",
     "ids": [
      "T6"
     ],
     "code": "def test_t6():\n    assert _h(cavab_T6) == \"18ac3e7343f016890c510e93f935261169d9e3f565436429830faf0934f4f8e4\", \"cavab düzgün deyil\"\ncheck(\"T6\", 10, test_t6)"
    },
    {
     "k": "code",
     "task": "T7",
     "code": "def iloc_ile(df):\n    # buranı yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T7"
     ],
     "code": "def test_t7():\n    df = pd.DataFrame(\n        {\"study_hours\": [5, 2, 8, 6, 4, 9], \"score\": [70, 40, 90, 75, 60, 95], \"attendance\": [85, 60, 95, 80, 70, 100]},\n        index=[\"A01\", \"A02\", \"A03\", \"A04\", \"A05\", \"A06\"],\n    )\n    r = iloc_ile(df)\n    return grade(\n        (4, \"ölçü (3, 2) olmalıdır\", lambda: tuple(r.shape) == (3, 2)),\n        (3, \"sütunlar ilk iki sütun olmalıdır\", lambda: list(r.columns) == [\"study_hours\", \"score\"]),\n        (3, \"sətirlər ilk üç sətir olmalıdır\", lambda: list(r.index) == [\"A01\", \"A02\", \"A03\"]),\n    )\ncheck(\"T7\", 10, test_t7)"
    },
    {
     "k": "var",
     "task": "T8",
     "var": "cavab_T8"
    },
    {
     "k": "test",
     "ids": [
      "T8"
     ],
     "code": "def test_t8():\n    assert _h(cavab_T8) == \"2e7d2c03a9507ae265ecf5b5356885a53393a2029d241394997265a1a25aefc6\", \"cavab düzgün deyil\"\ncheck(\"T8\", 10, test_t8)"
    },
    {
     "k": "code",
     "task": "T9",
     "code": "def model_yarat():\n    # buranı yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T9"
     ],
     "code": "def test_t9():\n    from sklearn.linear_model import LinearRegression\n    m = model_yarat()\n    assert isinstance(m, LinearRegression), f\"LinearRegression obyekti gözlənilirdi, sizinki: {type(m).__name__}\"\n    assert not hasattr(m, \"coef_\"), \"model hələ təlim olunmamalıdır (fit çağırmayın)\"\ncheck(\"T9\", 10, test_t9)"
    },
    {
     "k": "code",
     "task": "T10",
     "code": "def strat_bol(X, y):\n    # buranı yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T10"
     ],
     "code": "def test_t10():\n    def _data(n_pos, seed):\n        y = np.array([1] * n_pos + [0] * (200 - n_pos))\n        X = np.random.RandomState(seed).rand(200, 2)\n        return X, y\n    def _pos_test(n_pos, seed):\n        X, y = _data(n_pos, seed)\n        r = strat_bol(X, y)\n        return int(np.sum(r[3] == 1))\n    return grade(\n        (3, \"test hissəsi 40 nümunə olmalıdır\", lambda: len(strat_bol(*_data(20, 0))[1]) == 40),\n        (2, \"10 müsbət nümunə: testdə 2 olmalıdır (5%)\", lambda: _pos_test(10, 0) == 2),\n        (2, \"20 müsbət nümunə: testdə 4 olmalıdır (10%)\", lambda: _pos_test(20, 1) == 4),\n        (3, \"30 müsbət nümunə: testdə 6 olmalıdır (15%)\", lambda: _pos_test(30, 2) == 6),\n    )\ncheck(\"T10\", 10, test_t10)"
    }
   ]
  },
  "E": {
   "name": "Variant E",
   "max_score": 100,
   "items": [
    {
     "type": "task",
     "id": "T1"
    },
    {
     "type": "task",
     "id": "T2"
    },
    {
     "type": "task",
     "id": "T3"
    },
    {
     "type": "task",
     "id": "T4"
    },
    {
     "type": "task",
     "id": "T5"
    },
    {
     "type": "task",
     "id": "T6"
    },
    {
     "type": "task",
     "id": "T7"
    },
    {
     "type": "task",
     "id": "T8"
    },
    {
     "type": "task",
     "id": "T9"
    },
    {
     "type": "task",
     "id": "T10"
    }
   ],
   "tasks": [
    {
     "id": "T1",
     "title": "Tapşırıq T1. StandardScaler ilə standartlaşdırma (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T1. StandardScaler ilə standartlaşdırma (10 bal)</h4>\n<p><i>Kod tapşırığı · EDA, statistika və preprocessing · qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)</i></p>\n<p><code>StandardScaler</code> obyektini yaradın və <code>X_train</code>-ə <code>fit_transform()</code> tətbiq edin. Funksiya <code>(scaler, X_scaled)</code> cütünü <b>qaytarmalıdır</b>: <code>standartlas(X_train)</code>.<br>İdxal: <code>from sklearn.preprocessing import StandardScaler</code>.</p>",
     "starter": "def standartlas(X_train):\n    # buranı yazın\n    pass"
    },
    {
     "id": "T2",
     "title": "Tapşırıq T2. Miqyaslama və StandardScaler (10 bal)",
     "pts": 10,
     "kind": "choice",
     "html": "<h4>Tapşırıq T2. Miqyaslama və StandardScaler (10 bal)</h4>\n<p><i>Nəzəri sual · Nəzəri anlayış və mövzu · düzgün variantı seçin (yalnız 0 və ya 10 bal)</i></p>\n<p><code>StandardScaler</code> vasitəsilə standartlaşdırma necə işləyir?</p>",
     "options": {
      "a": "<code>(x − min) / (max − min)</code> hesablanır və qiymətlər [0, 1] intervalına düşür",
      "b": "Qiymətlər sıralanır və hər birinə yalnız sıra nömrəsi verilir",
      "c": "Hər qiymət sütunun maksimumuna bölünür və orta qiymət dəyişmir",
      "d": "Hər xüsusiyyət üçün <code>z = (x − μ) / σ</code> hesablanır; nəticədə orta 0, standart sapma 1 olur, μ və σ təlim hissəsindən tapılır"
     }
    },
    {
     "id": "T3",
     "title": "Tapşırıq T3. MSE hesablamaq (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T3. MSE hesablamaq (10 bal)</h4>\n<p><i>Kod tapşırığı · Scikit-Learn ilə xətti reqressiya və model qiymətləndirilməsi · qiymətləndirmə: yalnız 0 və ya 10 bal</i></p>\n<p>Həqiqi <code>y_test</code> və proqnoz <code>y_pred</code> arasında <b>MSE</b> (orta kvadratik xəta) göstəricisini hesablayıb <b>qaytaran</b> <code>mse_hesabla(y_test, y_pred)</code> funksiyasını yazın (<code>mean_squared_error</code>).</p>",
     "starter": "def mse_hesabla(y_test, y_pred):\n    # buranı yazın\n    pass"
    },
    {
     "id": "T4",
     "title": "Tapşırıq T4. Kənar qiymətləri kəsmək (clip) (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T4. Kənar qiymətləri kəsmək (clip) (10 bal)</h4>\n<p><i>Kod tapşırığı · EDA, statistika və preprocessing · qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)</i></p>\n<p><code>seriya</code> sütunundakı qiymətləri <code>low</code> və <code>high</code> hədlərinə <b>kəsən</b> (<code>clip</code>) <code>kenar_kes(seriya, low, high)</code> funksiyasını yazın və nəticəni <b>qaytarın</b>.<br>Nümunə: <code>[1, 50, 200]</code>, <code>low=10</code>, <code>high=100</code> → <code>[10, 50, 100]</code>.</p>",
     "starter": "def kenar_kes(seriya, low, high):\n    # buranı yazın\n    pass"
    },
    {
     "id": "T5",
     "title": "Tapşırıq T5. Qradient enişində öyrənmə sürəti (10 bal)",
     "pts": 10,
     "kind": "choice",
     "html": "<h4>Tapşırıq T5. Qradient enişində öyrənmə sürəti (10 bal)</h4>\n<p><i>Nəzəri sual · Nəzəri anlayış və mövzu · düzgün variantı seçin (yalnız 0 və ya 10 bal)</i></p>\n<p>Qradient Enişində (Gradient Descent) öyrənmə sürəti <code>alpha</code> parametrinin rolu və seçimi haqqında hansı ifadə düzgündür?</p>",
     "options": {
      "a": "<code>alpha</code> hər addımda parametrlərin yenilənmə ölçüsünü təyin edir: çox böyük olarsa minimum ətrafında salınma və ya diverqensiya, çox kiçik olarsa çox yavaş yaxınlaşma baş verir",
      "b": "<code>alpha</code> çox kiçik olarsa alqoritm diverqensiyaya uğrayır",
      "c": "<code>alpha</code> nə qədər böyük olsa, alqoritm həmişə daha sürətli və daha dəqiq yaxınlaşır",
      "d": "<code>alpha</code> təlim verilənlərindəki nümunələrin sayıdır"
     }
    },
    {
     "id": "T6",
     "title": "Tapşırıq T6. Matrisin ölçü xassələri (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T6. Matrisin ölçü xassələri (10 bal)</h4>\n<p><i>Kod tapşırığı · NumPy ilə massivlər və ədədi hesablamalar · qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)</i></p>\n<p>Verilmiş NumPy matrisi <code>m</code> üçün <code>(m.shape, m.ndim, m.size)</code> üçlüyünü <b>qaytaran</b> <code>matris_xasseleri(m)</code> funksiyasını yazın.<br>Nümunə: <code>3x3</code> matris üçün <code>((3, 3), 2, 9)</code>.</p>",
     "starter": "def matris_xasseleri(m):\n    # buranı yazın\n    pass"
    },
    {
     "id": "T7",
     "title": "Tapşırıq T7. X və y ayırmaq (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T7. X və y ayırmaq (10 bal)</h4>\n<p><i>Kod tapşırığı · Pandas ilə seçim, filtrasiya və dəyişənlərin işlənməsi · qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)</i></p>\n<p><code>'target'</code> sütununu <code>y</code> dəyişəninə, qalan sütunları <code>X</code> dəyişəninə mənimsədib <code>(X, y)</code> cütü kimi <b>qaytaran</b> <code>x_y_ayir(df)</code> funksiyasını yazın (<code>df.drop(columns=['target'])</code>).</p>",
     "starter": "def x_y_ayir(df):\n    # buranı yazın\n    pass"
    },
    {
     "id": "T8",
     "title": "Tapşırıq T8. Çatışmayan qiymət mexanizmləri (10 bal)",
     "pts": 10,
     "kind": "choice",
     "html": "<h4>Tapşırıq T8. Çatışmayan qiymət mexanizmləri (10 bal)</h4>\n<p><i>Nəzəri sual · Nəzəri anlayış və mövzu · düzgün variantı seçin (yalnız 0 və ya 10 bal)</i></p>\n<p>Çatışmayan qiymətlərin MCAR, MAR və MNAR mexanizmləri necə fərqlənir?</p>",
     "options": {
      "a": "MCAR: çatışma qiymətin özündən asılıdır; MAR: tam təsadüfidir; MNAR: digər dəyişənlərdən asılıdır",
      "b": "MCAR yalnız ədədi, MAR yalnız mətn, MNAR yalnız tarix sütunlarında yaranır",
      "c": "Üçü də eyni mənanı verir və yalnız kateqorik sütunlara aiddir",
      "d": "MCAR: çatışma tam təsadüfidir; MAR: çatışma digər müşahidə olunan dəyişənlərdən asılıdır; MNAR: çatışma çatışan qiymətin özündən asılıdır"
     }
    },
    {
     "id": "T9",
     "title": "Tapşırıq T9. DataFrame.info() (10 bal)",
     "pts": 10,
     "kind": "code",
     "html": "<h4>Tapşırıq T9. DataFrame.info() (10 bal)</h4>\n<p><i>Kod tapşırığı · Pandas ilə verilənlərin oxunması və ilkin baxış · qismən qiymətləndirmə: 0–10 bal arası (hər düzgün hissə üçün ayrıca bal)</i></p>\n<p>DataFrame haqqında ümumi texniki xülasəni (sütun tipləri və boş olmayan dəyərlər) <b>ekrana çap edən</b> <code>xulase_cap(df)</code> funksiyasını yazın (<code>df.info()</code>).</p>",
     "starter": "def xulase_cap(df):\n    # buranı yazın\n    pass"
    },
    {
     "id": "T10",
     "title": "Tapşırıq T10. EDA və ön emal fərqi (10 bal)",
     "pts": 10,
     "kind": "choice",
     "html": "<h4>Tapşırıq T10. EDA və ön emal fərqi (10 bal)</h4>\n<p><i>Nəzəri sual · Nəzəri anlayış və mövzu · düzgün variantı seçin (yalnız 0 və ya 10 bal)</i></p>\n<p>EDA (kəşfiyyat təhlili) ilə verilənlərin ön emalı (data preprocessing) mərhələləri necə fərqlənir?</p>",
     "options": {
      "a": "EDA verilənləri dəyişir, ön emal isə yalnız onlara baxır",
      "b": "İki mərhələ eynidir və adlar fərqli yazılır",
      "c": "EDA yalnız test verilənlərinə, ön emal isə yalnız nəticələrə tətbiq olunur",
      "d": "EDA verilənləri anlamaq və araşdırmaq üçündür (statistika, qrafiklər); ön emal isə modelə verməzdən əvvəl verilənləri dəyişən addımlardır (doldurma, kodlaşdırma, miqyaslama)"
     }
    }
   ],
   "steps": [
    {
     "k": "code",
     "task": "T1",
     "code": "def standartlas(X_train):\n    # buranı yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T1"
     ],
     "code": "def test_t1():\n    X = np.array([[1.0, 100.0], [2.0, 200.0], [3.0, 300.0], [4.0, 400.0]])\n    r = standartlas(X)\n    return grade(\n        (2, \"nəticə (scaler, X_scaled) cütü olmalıdır\", lambda: len(r) == 2 and hasattr(r[0], \"mean_\")),\n        (4, \"hər sütunun ortası 0 olmalıdır\", lambda: np.allclose(np.asarray(r[1]).mean(axis=0), 0)),\n        (4, \"hər sütunun standart sapması 1 olmalıdır\", lambda: np.allclose(np.asarray(r[1]).std(axis=0), 1)),\n    )\ncheck(\"T1\", 10, test_t1)"
    },
    {
     "k": "var",
     "task": "T2",
     "var": "cavab_T2"
    },
    {
     "k": "test",
     "ids": [
      "T2"
     ],
     "code": "def test_t2():\n    assert _h(cavab_T2) == \"18ac3e7343f016890c510e93f935261169d9e3f565436429830faf0934f4f8e4\", \"cavab düzgün deyil\"\ncheck(\"T2\", 10, test_t2)"
    },
    {
     "k": "code",
     "task": "T3",
     "code": "def mse_hesabla(y_test, y_pred):\n    # buranı yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T3"
     ],
     "code": "def test_t3():\n    assert _eq(mse_hesabla([3, 5, 2], [2, 5, 4]), 5 / 3), f\"[3, 5, 2] və [2, 5, 4] üçün MSE = 5/3 olmalıdır, sizinki: {mse_hesabla([3, 5, 2], [2, 5, 4])!r}\"\n    assert _eq(mse_hesabla([10, 20], [7, 26]), 22.5), \"[10, 20] və [7, 26] üçün MSE = 22.5 olmalıdır\"\ncheck(\"T3\", 10, test_t3)"
    },
    {
     "k": "code",
     "task": "T4",
     "code": "def kenar_kes(seriya, low, high):\n    # buranı yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T4"
     ],
     "code": "def test_t4():\n    s = pd.Series([1, 50, 200, 10, 100])\n    r = kenar_kes(s, 10, 100)\n    return grade(\n        (4, \"aşağı hədd (10) tətbiq olunmalıdır\", lambda: list(r)[0] == 10),\n        (4, \"yuxarı hədd (100) tətbiq olunmalıdır\", lambda: list(r)[2] == 100),\n        (2, \"hədlər daxilindəki qiymətlər dəyişməməlidir\", lambda: list(r)[1] == 50 and list(r)[3] == 10 and list(r)[4] == 100),\n    )\ncheck(\"T4\", 10, test_t4)"
    },
    {
     "k": "var",
     "task": "T5",
     "var": "cavab_T5"
    },
    {
     "k": "test",
     "ids": [
      "T5"
     ],
     "code": "def test_t5():\n    assert _h(cavab_T5) == \"ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb\", \"cavab düzgün deyil\"\ncheck(\"T5\", 10, test_t5)"
    },
    {
     "k": "code",
     "task": "T6",
     "code": "def matris_xasseleri(m):\n    # buranı yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T6"
     ],
     "code": "def test_t6():\n    m = np.arange(12).reshape(3, 4)\n    r = matris_xasseleri(m)\n    return grade(\n        (3, \"nəticə 3 elementli olmalıdır\", lambda: len(r) == 3),\n        (3, \"shape düzgün deyil\", lambda: tuple(r[0]) == (3, 4)),\n        (2, \"ndim düzgün deyil\", lambda: r[1] == 2),\n        (2, \"size düzgün deyil\", lambda: r[2] == 12),\n    )\ncheck(\"T6\", 10, test_t6)"
    },
    {
     "k": "code",
     "task": "T7",
     "code": "def x_y_ayir(df):\n    # buranı yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T7"
     ],
     "code": "def test_t7():\n    df = pd.DataFrame({\"f1\": [1, 2, 3], \"f2\": [4, 5, 6], \"target\": [0, 1, 0]})\n    r = x_y_ayir(df)\n    return grade(\n        (2, \"nəticə iki elementli olmalıdır\", lambda: len(r) == 2),\n        (4, \"X-də 'target' olmamalı, yalnız f1 və f2 olmalıdır\", lambda: list(r[0].columns) == [\"f1\", \"f2\"]),\n        (4, \"y 'target' sütunu olmalıdır\", lambda: list(r[1]) == [0, 1, 0]),\n    )\ncheck(\"T7\", 10, test_t7)"
    },
    {
     "k": "var",
     "task": "T8",
     "var": "cavab_T8"
    },
    {
     "k": "test",
     "ids": [
      "T8"
     ],
     "code": "def test_t8():\n    assert _h(cavab_T8) == \"18ac3e7343f016890c510e93f935261169d9e3f565436429830faf0934f4f8e4\", \"cavab düzgün deyil\"\ncheck(\"T8\", 10, test_t8)"
    },
    {
     "k": "code",
     "task": "T9",
     "code": "def xulase_cap(df):\n    # buranı yazın\n    pass"
    },
    {
     "k": "test",
     "ids": [
      "T9"
     ],
     "code": "def test_t9():\n    import io, contextlib\n    df = pd.DataFrame({\"yas\": [20, 21, None], \"ad\": [\"A\", \"B\", \"C\"]})\n    buf = io.StringIO()\n    with contextlib.redirect_stdout(buf):\n        xulase_cap(df)\n    out = buf.getvalue()\n    return grade(\n        (3, \"heç nə çap edilməyib\", lambda: len(out.strip()) > 0),\n        (4, \"sütun adları xülasədə olmalıdır\", lambda: \"yas\" in out and \"ad\" in out),\n        (3, \"boş olmayan dəyərlərin sayı göstərilməlidir (info() çıxışı)\", lambda: \"Non-Null\" in out),\n    )\ncheck(\"T9\", 10, test_t9)"
    },
    {
     "k": "var",
     "task": "T10",
     "var": "cavab_T10"
    },
    {
     "k": "test",
     "ids": [
      "T10"
     ],
     "code": "def test_t10():\n    assert _h(cavab_T10) == \"18ac3e7343f016890c510e93f935261169d9e3f565436429830faf0934f4f8e4\", \"cavab düzgün deyil\"\ncheck(\"T10\", 10, test_t10)"
    }
   ]
  }
 }
};
