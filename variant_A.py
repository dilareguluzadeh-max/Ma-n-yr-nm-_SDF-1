# -*- coding: utf-8 -*-
"""
BAKI MÜHƏNDİSLİK UNİVERSİTETİ (BMU)
Fənn: Maşın Öyrənməsinə Giriş — SDF 1 (Variant A)
Maksimum bal: 100 (10 tapşırıq: 4 nəzəri + 6 praktiki, hər biri 10 bal)

İSTİFADƏ QAYDASI
1. Nəzəri suallarda düzgün variantın hərfini (a, b, c və ya d) `cavab_T..` dəyişəninə yazın.
2. Kod tapşırıqlarında funksiyanı `with hell("T..."):` blokunun İÇİNDƏ yazın
   (blokun içindəki sətirlər 4 boşluq girintili olmalıdır). `pass` əvəzinə funksiyanın gövdəsini yazın.
3. Faylı işə salın:   python variant_A.py
4. Hər tapşırıq dərhal yoxlanır:
       ✅ Tapşırıq T3: DÜZGÜNDÜR (+10 bal)
       🟡 Tapşırıq T3: QİSMƏN DÜZGÜNDÜR (+6 / 10 bal)   (altında hansı hissənin ödənmədiyi göstərilir)
       ❌ Tapşırıq T3: XƏTA — ...
   Faylın sonunda yekun balınız çap olunur.

Qiymətləndirmə: bəzi kod tapşırıqları yalnız 0 və ya 10 bal, digərləri isə hissə-hissə (0–10 arası) qiymətləndirilir.
Hər tapşırığın başlığında bu qeyd olunub.

Qeyd: bir tapşırıqdakı icra xətası digər tapşırıqları dayandırmır.
SyntaxError (məs. mötərizə və ya girinti səhvi) isə bütün faylın işləməsinə mane olur —
Python xətanın sətrini göstərəcək, onu düzəldib yenidən işlədin.
Funksiyaların adlarını və arqumentlərini dəyişməyin.

Bu fayl tools/build_bank.py ilə yaradılıb.
"""

import hashlib
import math
import sys

import numpy as np
import pandas as pd

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

results = {}
_errors = {}


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


class hell:
    """Tapşırıq blokunu qoruyur: blokdakı xəta yadda saxlanır, fayl isə işləməyə davam edir."""

    def __init__(self, task_id):
        self.task_id = task_id

    def __enter__(self):
        _errors.pop(self.task_id, None)
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type is None:
            return False
        _errors[self.task_id] = f"kodunuz icra olunarkən xəta baş verdi → {exc_type.__name__}: {exc}"
        return True


def check(task_id, points, test):
    """Testi işlədir, nəticəni `results`-də saxlayır və ekrana rəy çıxarır (tam və ya qismən bal)."""
    tid = task_id.split("_")[0]
    reason = ""
    try:
        res = test()
        if isinstance(res, tuple) and len(res) == 3:
            got, tot, failed = res
            pts = int(points * got / tot + 0.5) if tot else 0
            results[task_id] = pts
            if pts >= points:
                print(f"✅ Tapşırıq {tid}: DÜZGÜNDÜR (+{points} bal)")
                return
            reason = "Ödənməyən hissələr: " + "; ".join(failed)
            if pts > 0:
                print(f"🟡 Tapşırıq {tid}: QİSMƏN DÜZGÜNDÜR (+{pts} / {points} bal)")
                print(f"   ↳ {reason}")
                return
        else:
            results[task_id] = points
            print(f"✅ Tapşırıq {tid}: DÜZGÜNDÜR (+{points} bal)")
            return
    except AssertionError as e:
        reason = str(e) or "test şərti ödənmədi"
    except NameError as e:
        reason = f"tələb olunan dəyişən/funksiya təyin edilməyib ({e})"
    except Exception as e:
        reason = f"{type(e).__name__}: {e}"
    results[task_id] = 0
    if tid in _errors:
        reason = _errors[tid]
    print(f"❌ Tapşırıq {tid}: XƏTA — Çıxış formatı və ya hesablanmış dəyər gözlənilən nəticəyə uyğun deyil!")
    print(f"   ↳ Səbəb: {reason}")


ad_soyad = "..."      # Bura ad və soyadınızı yazın
qrup = "1203A"        # Qrup nömrəniz


# ======================================================================
# Tapşırıq T1. Log-transformasiya (log1p) (10 bal) — Kod tapşırığı · EDA, statistika və preprocessing · qismən qiymətləndirmə (0–10 bal arası)
#
# np.log1p() ilə 'price' sütununun log-transformasiyasını aparın, nəticəni 'log_price' adlı yeni sütuna yazın və DataFrame-i qaytarın: log_cevir(df).
# ======================================================================

with hell("T1"):
    def log_cevir(df):
        # buranı yazın
        pass


def test_t1():
    df = pd.DataFrame({"price": [0, 9, 99, 999]})
    r = log_cevir(df)
    return grade(
        (3, "'log_price' sütunu yaradılmalıdır", lambda: "log_price" in r.columns),
        (5, "dəyərlər log(1 + price) olmalıdır", lambda: _eq(list(r["log_price"]), [0.0, math.log(10), math.log(100), math.log(1000)])),
        (2, "'price' sütunu dəyişməməlidir", lambda: list(r["price"]) == [0, 9, 99, 999]),
    )
check("T1", 10, test_t1)


# ======================================================================
# Tapşırıq T2. Xətti reqressiyada w və b (10 bal) — Nəzəri sual (yalnız 0 və ya 10 bal)
#
# Sadə Xətti Reqressiya tənliyində y = w * x + b çəki w və kəsişmə b parametrlərinin həndəsi mənası nədir?
#   a) w təlim nümunələrinin sayı, b isə sütunların sayıdır
#   b) w xəttin y oxunu kəsdiyi nöqtə, b isə yamacdır
#   c) w düz xəttin yamacıdır (x 1 vahid artanda y-in dəyişməsi), b isə xəttin y oxunu kəsdiyi nöqtədir (x = 0 olduqda y)
#   d) w və b verilənlərin ortası və medianıdır
# ======================================================================

cavab_T2 = ""      # düzgün variantın hərfi: "a", "b", "c" və ya "d"


def test_t2():
    assert _h(cavab_T2) == "2e7d2c03a9507ae265ecf5b5356885a53393a2029d241394997265a1a25aefc6", "cavab düzgün deyil"
check("T2", 10, test_t2)


# ======================================================================
# Tapşırıq T3. R² balı (10 bal) — Kod tapşırığı · Scikit-Learn ilə xətti reqressiya və model qiymətləndirilməsi · yalnız 0 və ya 10 bal
#
# r2_score funksiyası ilə modelin R² balını hesablayıb qaytaran r2_hesabla(y_test, y_pred) funksiyasını yazın.
# ======================================================================

with hell("T3"):
    def r2_hesabla(y_test, y_pred):
        # buranı yazın
        pass


def test_t3():
    assert _eq(r2_hesabla([1, 2, 3, 4], [1, 2, 3, 4]), 1.0), "mükəmməl proqnozda R² = 1 olmalıdır"
    assert _eq(r2_hesabla([1, 2, 3, 4], [2.5, 2.5, 2.5, 2.5]), 0.0), "orta ilə proqnozda R² = 0 olmalıdır"
    assert _eq(r2_hesabla([3, -0.5, 2, 7], [2.5, 0.0, 2, 8]), 0.9486081370449679), "R² = 0.9486... olmalıdır"
check("T3", 10, test_t3)


# ======================================================================
# Tapşırıq T4. Əsas statistik xülasə (10 bal) — Kod tapşırığı · Pandas ilə verilənlərin oxunması və ilkin baxış · qismən qiymətləndirmə (0–10 bal arası)
#
# DataFrame-in ədədi sütunları üçün əsas statistik xülasəni (count, mean, std, min, 25%, 50%, 75%, max) hesablayıb qaytaran statistika(df) funksiyasını yazın (.describe()).
# ======================================================================

with hell("T4"):
    def statistika(df):
        # buranı yazın
        pass


def test_t4():
    df = pd.DataFrame({"a": [1, 2, 3, 4], "b": [10.0, 20.0, 30.0, 40.0], "c": list("wxyz")})
    r = statistika(df)
    return grade(
        (2, "nəticə DataFrame olmalıdır", lambda: isinstance(r, pd.DataFrame)),
        (4, "sətir adları describe() nəticəsi kimi olmalıdır", lambda: list(r.index) == ["count", "mean", "std", "min", "25%", "50%", "75%", "max"]),
        (4, "yalnız ədədi sütunlar olmalıdır", lambda: list(r.columns) == ["a", "b"]),
    )
check("T4", 10, test_t4)


# ======================================================================
# Tapşırıq T5. Modeli öyrətmək (fit) (10 bal) — Kod tapşırığı · Scikit-Learn ilə xətti reqressiya və model qiymətləndirilməsi · qismən qiymətləndirmə (0–10 bal arası)
#
# Xətti reqressiya modelini (X_train, y_train) üzərində öyrədib öyrədilmiş modeli qaytaran oyret(X_train, y_train) funksiyasını yazın (model.fit(X_train, y_train)).
# ======================================================================

with hell("T5"):
    def oyret(X_train, y_train):
        # buranı yazın
        pass


def test_t5():
    rs = np.random.RandomState(0)
    X_train = rs.rand(40, 2) * 10
    y_train = 3 * X_train[:, 0] - 2 * X_train[:, 1] + 5
    X_test = rs.rand(10, 2) * 10
    m = oyret(X_train, y_train)
    return grade(
        (3, "LinearRegression modeli qaytarılmalıdır", lambda: type(m).__name__ == "LinearRegression"),
        (3, "model öyrədilməlidir (fit çağırılmalıdır)", lambda: hasattr(m, "coef_")),
        (4, "öyrənilən çəkilər düzgün olmalıdır (3 və -2)", lambda: np.allclose(m.coef_, [3, -2], atol=1e-6)),
    )
check("T5", 10, test_t5)


# ======================================================================
# Tapşırıq T6. Sağa əyilmiş paylanmada mean və median (10 bal) — Nəzəri sual (yalnız 0 və ya 10 bal)
#
# Sağa əyilmiş (right-skewed) paylanmada orta qiymət (mean) və median arasında necə nisbət olur?
#   a) Median həmişə meandan böyükdür, çünki kənar qiymətlər medianı yuxarı çəkir
#   b) Mean və median həmişə bir-birinə bərabərdir
#   c) Mean medianından kiçik olur, çünki sol quyruq uzundur
#   d) Mean medianından böyük olur, çünki uzun sağ quyruqdakı böyük qiymətlər ortanı yuxarı çəkir
# ======================================================================

cavab_T6 = ""      # düzgün variantın hərfi: "a", "b", "c" və ya "d"


def test_t6():
    assert _h(cavab_T6) == "18ac3e7343f016890c510e93f935261169d9e3f565436429830faf0934f4f8e4", "cavab düzgün deyil"
check("T6", 10, test_t6)


# ======================================================================
# Tapşırıq T7. Minimum və maksimum (10 bal) — Kod tapşırığı · NumPy ilə massivlər və ədədi hesablamalar · qismən qiymətləndirmə (0–10 bal arası)
#
# NumPy massivinin minimum və maksimum qiymətlərini (minimum, maksimum) cütü kimi qaytaran min_maks(arr) funksiyasını yazın (np.min(), np.max()).
# Nümunə: [4, 9, 1, 7] → (1, 9).
# ======================================================================

with hell("T7"):
    def min_maks(arr):
        # buranı yazın
        pass


def test_t7():
    r = min_maks(np.array([4, 9, 1, 7]))
    return grade(
        (2, "nəticə iki elementli olmalıdır", lambda: len(r) == 2),
        (4, "minimum düzgün deyil", lambda: r[0] == 1),
        (4, "maksimum düzgün deyil", lambda: r[1] == 9),
    )
check("T7", 10, test_t7)


# ======================================================================
# Tapşırıq T8. Normal tənlik və qradient enişi (10 bal) — Nəzəri sual (yalnız 0 və ya 10 bal)
#
# Xətti reqressiyada analitik həll (Normal Equation / OLS) ilə qradient enişi necə müqayisə olunur?
#   a) Qradient enişi həmişə bir addımda həll verir, normal tənlik isə iterativdir
#   b) Normal tənlik də alpha və iterasiya sayı tələb edir
#   c) İkisi həmişə eyni sayda iterasiya və eyni hesablama xərci tələb edir
#   d) Normal tənlik parametrləri bir addımda dəqiq verir və alpha tələb etmir, lakin çox xüsusiyyət olduqda matrisin tərsi bahalıdır; qradient enişi iterativdir, alpha seçilməlidir, böyük verilənlərdə daha əlverişlidir
# ======================================================================

cavab_T8 = ""      # düzgün variantın hərfi: "a", "b", "c" və ya "d"


def test_t8():
    assert _h(cavab_T8) == "18ac3e7343f016890c510e93f935261169d9e3f565436429830faf0934f4f8e4", "cavab düzgün deyil"
check("T8", 10, test_t8)


# ======================================================================
# Tapşırıq T9. Törəmə sütun (10 bal) — Kod tapşırığı · Pandas ilə seçim, filtrasiya və dəyişənlərin işlənməsi · qismən qiymətləndirmə (0–10 bal arası)
#
# 'price' və 'area' sütunlarından istifadə edərək 'price_per_sqm' (price / area) adlı yeni sütun yaradın və DataFrame-i qaytarın: tirem_sutun(df).
# ======================================================================

with hell("T9"):
    def tirem_sutun(df):
        # buranı yazın
        pass


def test_t9():
    df = pd.DataFrame({"price": [100000, 150000, 90000], "area": [50, 75, 60]})
    r = tirem_sutun(df)
    return grade(
        (3, "nəticə DataFrame olmalıdır", lambda: isinstance(r, pd.DataFrame)),
        (3, "'price_per_sqm' sütunu yaradılmalıdır", lambda: "price_per_sqm" in r.columns),
        (4, "dəyərlər price / area olmalıdır", lambda: _eq(list(r["price_per_sqm"]), [2000.0, 2000.0, 1500.0])),
    )
check("T9", 10, test_t9)


# ======================================================================
# Tapşırıq T10. Kəşfiyyat xarakterli verilənlər təhlili (EDA) (10 bal) — Nəzəri sual (yalnız 0 və ya 10 bal)
#
# Kəşfiyyat xarakterli verilənlər təhlili (EDA) mərhələsində əsasən hansı sualların cavabı axtarılır?
#   a) Sətir və sütun sayı, sütun tipləri, çatışmayan qiymətlər, təkrarlanan sətirlər, paylanmalar və kənar müşahidələr kimi verilənlərin quruluşu ilə bağlı suallar
#   b) Modelin hiperparametrlərinin hansı qiymətlərdə ən yaxşı olduğu
#   c) Verilənlərin hansı hissəsinin bazadan həmişəlik silinməli olduğu
#   d) Yalnız modelin test verilənlərindəki dəqiqliyinin neçə faiz olduğu
# ======================================================================

cavab_T10 = ""      # düzgün variantın hərfi: "a", "b", "c" və ya "d"


def test_t10():
    assert _h(cavab_T10) == "ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb", "cavab düzgün deyil"
check("T10", 10, test_t10)



# ======================================================================
# YEKUN NƏTİCƏ
# ======================================================================
MAX_POINTS = {'T1': 10, 'T2': 10, 'T3': 10, 'T4': 10, 'T5': 10, 'T6': 10, 'T7': 10, 'T8': 10, 'T9': 10, 'T10': 10}

total = 0
print()
print(f"{'Tapşırıq':<12}{'Nəticə':<10}{'Bal':>6}")
print("-" * 30)
for k, p in MAX_POINTS.items():
    got = results.get(k)
    if got is None:
        status, earned = "—", 0
    elif got == p:
        status, earned = "✅", got
    elif got > 0:
        status, earned = "🟡", got
    else:
        status, earned = "❌", got
    total += earned
    print(f"{k:<12}{status:<10}{earned:>3}/{p}")

max_total = sum(MAX_POINTS.values())
print("-" * 30)
print(f"YEKUN İMTAHAN BALI: {total} / {max_total}  ({total / max_total * 100:.0f}%)")
