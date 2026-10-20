# -*- coding: utf-8 -*-
"""
BAKI MÜHƏNDİSLİK UNİVERSİTETİ (BMU)
Fənn: Maşın Öyrənməsinə Giriş — SDF 1 (Variant B)
Maksimum bal: 100 (10 tapşırıq: 4 nəzəri + 6 praktiki, hər biri 10 bal)

İSTİFADƏ QAYDASI
1. Nəzəri suallarda düzgün variantın hərfini (a, b, c və ya d) `cavab_T..` dəyişəninə yazın.
2. Kod tapşırıqlarında funksiyanı `with hell("T..."):` blokunun İÇİNDƏ yazın
   (blokun içindəki sətirlər 4 boşluq girintili olmalıdır). `pass` əvəzinə funksiyanın gövdəsini yazın.
3. Faylı işə salın:   python variant_B.py
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
# Tapşırıq T1. Kənar müşahidə və IQR qaydası (10 bal) — Nəzəri sual (yalnız 0 və ya 10 bal)
#
# IQR (interkvartil diapazon) qaydası ilə kənar müşahidə (outlier) hədləri necə müəyyən edilir?
#   a) IQR standart sapmanın kvadratıdır; hədlər 0 və 1 sabitləridir
#   b) IQR = maksimum − minimum; ortalamadan 1.5 IQR uzaq qiymətlər kənardır
#   c) IQR = Q3 − Q1; adətən Q1 − 1.5·IQR-dən aşağı və Q3 + 1.5·IQR-dən yuxarı qiymətlər kənar müşahidə sayılır
#   d) IQR = Q2 − Q1; yalnız medianın altındakı qiymətlər kənar sayılır
# ======================================================================

cavab_T1 = ""      # düzgün variantın hərfi: "a", "b", "c" və ya "d"


def test_t1():
    assert _h(cavab_T1) == "2e7d2c03a9507ae265ecf5b5356885a53393a2029d241394997265a1a25aefc6", "cavab düzgün deyil"
check("T1", 10, test_t1)


# ======================================================================
# Tapşırıq T2. Əyrilik (skewness) (10 bal) — Kod tapşırığı · EDA, statistika və preprocessing · yalnız 0 və ya 10 bal
#
# df[sutun] sütununun əyriliyini (skewness) hesablayıb qaytaran eyrilik(df, sutun) funksiyasını yazın (.skew()).
# ======================================================================

with hell("T2"):
    def eyrilik(df, sutun):
        # buranı yazın
        pass


def test_t2():
    df = pd.DataFrame({"x": [1, 2, 2, 3, 3, 3, 4, 20], "y": [5, 5, 5, 5, 5, 5, 5, 5.5]})
    for c in ("x", "y"):
        exp = df[c].skew()
        r = eyrilik(df, c)
        assert _eq(r, exp), f"{c} sütunu üçün {exp!r} gözlənilirdi, sizinki: {r!r}"
check("T2", 10, test_t2)


# ======================================================================
# Tapşırıq T3. Mətn təmizləmə (10 bal) — Kod tapşırığı · Pandas ilə seçim, filtrasiya və dəyişənlərin işlənməsi · qismən qiymətləndirmə (0–10 bal arası)
#
# Mətn sütununun (pd.Series) kənar boşluqlarını silin və kiçik hərflərə çevirin: temizle(seriya) funksiyası nəticəni qaytarsın (.str.strip().str.lower()).
# Nümunə: "  Baku " → "baku".
# ======================================================================

with hell("T3"):
    def temizle(seriya):
        # buranı yazın
        pass


def test_t3():
    s = pd.Series(["  Baku ", "GANJA", " Sumqayit"])
    r = temizle(s)
    return grade(
        (5, "kənar boşluqlar silinməlidir", lambda: [x.strip() for x in r] == list(r) and list(r)[0].startswith("b")),
        (5, "bütün hərflər kiçik olmalıdır", lambda: list(r) == ["baku", "ganja", "sumqayit"]),
    )
check("T3", 10, test_t3)


# ======================================================================
# Tapşırıq T4. Cüt ədədlər massivi (10 bal) — Kod tapşırığı · NumPy ilə massivlər və ədədi hesablamalar · qismən qiymətləndirmə (0–10 bal arası)
#
# 0-dan 10-a qədər (10 daxil) cüt ədədlərdən ibarət NumPy massivini (np.arange() ilə) qaytaran cut_ededler() funksiyasını yazın.
# Gözlənilən nəticə: [0, 2, 4, 6, 8, 10].
# ======================================================================

with hell("T4"):
    def cut_ededler():
        # buranı yazın
        pass


def test_t4():
    r = cut_ededler()
    return grade(
        (3, "nəticə NumPy massivi olmalıdır", lambda: isinstance(r, np.ndarray)),
        (7, "elementlər [0, 2, 4, 6, 8, 10] olmalıdır", lambda: _eq(r, [0, 2, 4, 6, 8, 10])),
    )
check("T4", 10, test_t4)


# ======================================================================
# Tapşırıq T5. Miqyasa həssaslıq (10 bal) — Nəzəri sual (yalnız 0 və ya 10 bal)
#
# Maşın öyrənməsi alqoritmləri verilənlərin miqyasına həssaslığına görə necə təsnif olunur?
#   a) Ağac əsaslı alqoritmlər miqyasa ən çox həssasdır, KNN isə heç həssas deyil
#   b) Bütün alqoritmlər miqyasa eyni dərəcədə həssasdır
#   c) Miqyasa həssaslıq yalnız klasterləşdirmə alqoritmlərinə aiddir
#   d) Məsafə və qradient əsaslı alqoritmlər (KNN, SVM, qradient enişi ilə xətti modellər, neyron şəbəkələr) miqyasa həssasdır; ağac əsaslı alqoritmlər (Decision Tree, Random Forest) əsasən həssas deyil
# ======================================================================

cavab_T5 = ""      # düzgün variantın hərfi: "a", "b", "c" və ya "d"


def test_t5():
    assert _h(cavab_T5) == "18ac3e7343f016890c510e93f935261169d9e3f565436429830faf0934f4f8e4", "cavab düzgün deyil"
check("T5", 10, test_t5)


# ======================================================================
# Tapşırıq T6. Sütun seçimi (Series və DataFrame) (10 bal) — Kod tapşırığı · Pandas ilə seçim, filtrasiya və dəyişənlərin işlənməsi · qismən qiymətləndirmə (0–10 bal arası)
#
# df-dən 'study_hours' sütununu Series kimi, ['study_hours', 'score'] sütunlarını isə DataFrame kimi seçib (seriya, cedvel) cütü şəklində qaytaran sutunlari_sec(df) funksiyasını yazın.
# ======================================================================

with hell("T6"):
    def sutunlari_sec(df):
        # buranı yazın
        pass


def test_t6():
    df = pd.DataFrame(
        {"study_hours": [5, 2, 8, 6, 4, 9], "score": [70, 40, 90, 75, 60, 95], "attendance": [85, 60, 95, 80, 70, 100]},
        index=["A01", "A02", "A03", "A04", "A05", "A06"],
    )
    r = sutunlari_sec(df)
    return grade(
        (2, "nəticə iki elementli olmalıdır", lambda: len(r) == 2),
        (4, "birinci nəticə Series olmalıdır (study_hours)", lambda: isinstance(r[0], pd.Series) and list(r[0]) == [5, 2, 8, 6, 4, 9]),
        (4, "ikinci nəticə iki sütunlu DataFrame olmalıdır", lambda: isinstance(r[1], pd.DataFrame) and list(r[1].columns) == ["study_hours", "score"]),
    )
check("T6", 10, test_t6)


# ======================================================================
# Tapşırıq T7. Determinasiya əmsalı (R²) (10 bal) — Nəzəri sual (yalnız 0 və ya 10 bal)
#
# Determinasiya əmsalı (R² score) modelin izah etmə qabiliyyətini necə xarakterizə edir?
#   a) R² xətaların orta mütləq qiymətidir və hədəflə eyni vahiddədir
#   b) R² həmişə 0 ilə 1 arasındadır və mənfi ola bilməz
#   c) R² = 0 modelin mükəmməl olduğunu göstərir
#   d) R² = 1 − SS_res / SS_tot: hədəfin dəyişkənliyinin modellə izah olunan hissəsini göstərir; 1-ə yaxın yaxşıdır, 0 orta qiymətlə proqnoza bərabərdir, mənfi də ola bilər
# ======================================================================

cavab_T7 = ""      # düzgün variantın hərfi: "a", "b", "c" və ya "d"


def test_t7():
    assert _h(cavab_T7) == "18ac3e7343f016890c510e93f935261169d9e3f565436429830faf0934f4f8e4", "cavab düzgün deyil"
check("T7", 10, test_t7)


# ======================================================================
# Tapşırıq T8. CSV oxumaq və ilk 5 sətir (10 bal) — Kod tapşırığı · Pandas ilə verilənlərin oxunması və ilkin baxış · qismən qiymətləndirmə (0–10 bal arası)
#
# Verilmiş fayl yolundakı CSV faylını Pandas ilə oxuyun (pd.read_csv()) və ilk 5 sətri (.head()) DataFrame kimi qaytaran ilk_bes(fayl) funksiyasını yazın.
# ======================================================================

with hell("T8"):
    def ilk_bes(fayl):
        # buranı yazın
        pass


def test_t8():
    import os, tempfile
    _p = os.path.join(tempfile.gettempdir(), "imtahan_students.csv")
    with open(_p, "w", encoding="utf-8") as _f:
        _f.write("id,study_hours,score\n" + "\n".join(f"{i},{i + 1},{50 + i}" for i in range(1, 9)) + "\n")
    r = ilk_bes(_p)
    return grade(
        (3, "nəticə DataFrame olmalıdır", lambda: isinstance(r, pd.DataFrame)),
        (4, "yalnız ilk 5 sətir qaytarılmalıdır", lambda: len(r) == 5),
        (3, "sütun adları faylla eyni olmalıdır", lambda: list(r.columns) == ["id", "study_hours", "score"]),
    )
check("T8", 10, test_t8)


# ======================================================================
# Tapşırıq T9. Reqressiya və klassifikasiya (10 bal) — Nəzəri sual (yalnız 0 və ya 10 bal)
#
# Reqressiya (regression) və klassifikasiya (classification) məsələlərinin əsas fərqi hansıdır?
#   a) Reqressiya diskret sinif, klassifikasiya isə kəsilməz ədədi qiymət proqnozlaşdırır
#   b) Reqressiya kəsilməz ədədi qiymət (məsələn, mənzilin qiyməti), klassifikasiya isə diskret sinif (məsələn, spam / spam deyil) proqnozlaşdırır
#   c) Fərq yoxdur: hər ikisi eyni hədəf tipinə malikdir və eyni metriklərlə qiymətləndirilir
#   d) Reqressiya yalnız xətti, klassifikasiya isə yalnız qeyri-xətti modellərlə həll olunur
# ======================================================================

cavab_T9 = ""      # düzgün variantın hərfi: "a", "b", "c" və ya "d"


def test_t9():
    assert _h(cavab_T9) == "3e23e8160039594a33894f6564e1b1348bbd7a0088d42c4acb73eeaed59c009d", "cavab düzgün deyil"
check("T9", 10, test_t9)


# ======================================================================
# Tapşırıq T10. RMSE hesablamaq (10 bal) — Kod tapşırığı · Scikit-Learn ilə xətti reqressiya və model qiymətləndirilməsi · qismən qiymətləndirmə (0–10 bal arası)
#
# MSE göstəricisindən np.sqrt() vasitəsilə RMSE dəyərini hesablayıb qaytaran rmse_hesabla(y_test, y_pred) funksiyasını yazın.
# ======================================================================

with hell("T10"):
    def rmse_hesabla(y_test, y_pred):
        # buranı yazın
        pass


def test_t10():
    return grade(
        (5, "[0, 0] və [3, 4] üçün RMSE = sqrt(12.5)", lambda: _eq(rmse_hesabla([0, 0], [3, 4]), math.sqrt(12.5))),
        (3, "[2, 4, 6] və [3, 3, 9] üçün RMSE = sqrt(11/3)", lambda: _eq(rmse_hesabla([2, 4, 6], [3, 3, 9]), math.sqrt(11 / 3))),
        (2, "mükəmməl proqnozda RMSE = 0", lambda: _eq(rmse_hesabla([1, 2], [1, 2]), 0.0)),
    )
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
