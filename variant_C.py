# -*- coding: utf-8 -*-
"""
BAKI MÜHƏNDİSLİK UNİVERSİTETİ (BMU)
Fənn: Maşın Öyrənməsinə Giriş — SDF 1 (Variant C)
Maksimum bal: 100 (10 tapşırıq: 4 nəzəri + 6 praktiki, hər biri 10 bal)

İSTİFADƏ QAYDASI
1. Nəzəri suallarda düzgün variantın hərfini (a, b, c və ya d) `cavab_T..` dəyişəninə yazın.
2. Kod tapşırıqlarında funksiyanı `with hell("T..."):` blokunun İÇİNDƏ yazın
   (blokun içindəki sətirlər 4 boşluq girintili olmalıdır). `pass` əvəzinə funksiyanın gövdəsini yazın.
3. Faylı işə salın:   python variant_C.py
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
# Tapşırıq T1. 1D massivi 2x3 matrisə çevirmək (10 bal) — Kod tapşırığı · NumPy ilə massivlər və ədədi hesablamalar · qismən qiymətləndirmə (0–10 bal arası)
#
# 6 elementli 1D arr massivini 2x3 ölçülü 2D matrisə çevirib qaytaran matrise_cevir(arr) funksiyasını yazın (.reshape(2, 3)).
# ======================================================================

with hell("T1"):
    def matrise_cevir(arr):
        # buranı yazın
        pass


def test_t1():
    r = matrise_cevir(np.array([1, 2, 3, 4, 5, 6]))
    return grade(
        (5, "shape (2, 3) olmalıdır", lambda: tuple(r.shape) == (2, 3)),
        (5, "elementlərin sırası saxlanmalıdır", lambda: _eq(r, [[1, 2, 3], [4, 5, 6]])),
    )
check("T1", 10, test_t1)


# ======================================================================
# Tapşırıq T2. Medianla doldurmaq (10 bal) — Kod tapşırığı · EDA, statistika və preprocessing · qismən qiymətləndirmə (0–10 bal arası)
#
# df[sutun] sütunundakı çatışmayan (NaN) qiymətləri həmin sütunun medianı ilə doldurub nəticəni (Series) qaytaran median_ile_doldur(df, sutun) funksiyasını yazın (fillna(df[sutun].median())).
# ======================================================================

with hell("T2"):
    def median_ile_doldur(df, sutun):
        # buranı yazın
        pass


def test_t2():
    df = pd.DataFrame({"x": [1.0, None, 3.0, 100.0, None]})
    r = median_ile_doldur(df, "x")
    return grade(
        (4, "çatışmayan qiymət qalmamalıdır", lambda: int(pd.isna(r).sum()) == 0),
        (4, "boşluqlar medianla (3.0) doldurulmalıdır, orta ilə yox", lambda: _eq(list(r), [1.0, 3.0, 3.0, 100.0, 3.0])),
        (2, "mövcud qiymətlər dəyişməməlidir", lambda: list(r)[0] == 1.0 and list(r)[3] == 100.0),
    )
check("T2", 10, test_t2)


# ======================================================================
# Tapşırıq T3. İki şərtlə filtr (&) (10 bal) — Kod tapşırığı · Pandas ilə seçim, filtrasiya və dəyişənlərin işlənməsi · qismən qiymətləndirmə (0–10 bal arası)
#
# 'attendance' >= 80 VƏ 'study_hours' >= 5 şərtlərini eyni vaxtda ödəyən sətirləri & operatoru ilə seçib qaytaran iki_sert_filtr(df) funksiyasını yazın.
# ======================================================================

with hell("T3"):
    def iki_sert_filtr(df):
        # buranı yazın
        pass


def test_t3():
    df = pd.DataFrame(
        {"study_hours": [5, 2, 8, 6, 4, 9], "score": [70, 40, 90, 75, 60, 95], "attendance": [85, 60, 95, 80, 70, 100]},
        index=["A01", "A02", "A03", "A04", "A05", "A06"],
    )
    r = iki_sert_filtr(df)
    return grade(
        (5, "sətirlərin sayı düzgün deyil (4 sətir gözlənilir)", lambda: len(r) == 4),
        (5, "seçilən sətirlər düzgün deyil", lambda: list(r.index) == ["A01", "A03", "A04", "A06"]),
    )
check("T3", 10, test_t3)


# ======================================================================
# Tapşırıq T4. Bazis (baseline) model (10 bal) — Nəzəri sual (yalnız 0 və ya 10 bal)
#
# Bazis (baseline) model anlayışı və mürəkkəb modellərdən əvvəl tətbiqinin əhəmiyyəti nədir?
#   a) Bazis model təlim verilənləri olmadan yalnız test verilənləri üzərində qurulur
#   b) Bazis model yalnız dərin neyron şəbəkələr üçün istifadə olunur
#   c) Bazis model ən yaxşı mümkün modeldir və ondan sonra başqa model sınamağa ehtiyac qalmır
#   d) Bazis model sadə referans modeldir (məsələn, hədəfin ortası və ya medianı); mürəkkəb modelin həqiqətən fayda verdiyini müqayisə etmək üçün minimum standart rolunu oynayır
# ======================================================================

cavab_T4 = ""      # düzgün variantın hərfi: "a", "b", "c" və ya "d"


def test_t4():
    assert _h(cavab_T4) == "18ac3e7343f016890c510e93f935261169d9e3f565436429830faf0934f4f8e4", "cavab düzgün deyil"
check("T4", 10, test_t4)


# ======================================================================
# Tapşırıq T5. Shape və dtypes (10 bal) — Kod tapşırığı · Pandas ilə verilənlərin oxunması və ilkin baxış · qismən qiymətləndirmə (0–10 bal arası)
#
# DataFrame-in ölçüsünü və sütun tiplərini (df.shape, df.dtypes) cütü kimi qaytaran olcu_ve_tipler(df) funksiyasını yazın.
# ======================================================================

with hell("T5"):
    def olcu_ve_tipler(df):
        # buranı yazın
        pass


def test_t5():
    df = pd.DataFrame({"a": [1, 2, 3], "b": [1.5, 2.5, 3.5], "c": ["x", "y", "z"]})
    r = olcu_ve_tipler(df)
    return grade(
        (2, "nəticə iki elementli olmalıdır", lambda: len(r) == 2),
        (4, "shape (3, 3) olmalıdır", lambda: tuple(r[0]) == (3, 3)),
        (4, "sütun tipləri düzgün deyil", lambda: {k: str(v) for k, v in dict(r[1]).items()} in ({"a": "int64", "b": "float64", "c": "object"}, {"a": "int64", "b": "float64", "c": "str"}, {"a": "int64", "b": "float64", "c": "string"})),
    )
check("T5", 10, test_t5)


# ======================================================================
# Tapşırıq T6. Multikolinearlıq (10 bal) — Nəzəri sual (yalnız 0 və ya 10 bal)
#
# Multikolinearlıq (multicollinearity) problemi Xətti Reqressiya modelinin çəkilərinə necə təsir edir?
#   a) Hədəflə xüsusiyyətlər arasında korrelyasiya olmadıqda yaranır və bütün çəkiləri sıfır edir
#   b) Yalnız çatışmayan qiymətlər olduqda yaranır və çəkilərə təsir etmir
#   c) Müstəqil dəyişənlər bir-biri ilə yüksək korrelyasiyalı olduqda çəkilər qeyri-sabit olur, verilənlərdəki kiçik dəyişiklikdən kəskin dəyişir və şərh etmək çətinləşir
#   d) Çəkilər daha sabit olur, çünki modelə əlavə eyni məlumat verilir
# ======================================================================

cavab_T6 = ""      # düzgün variantın hərfi: "a", "b", "c" və ya "d"


def test_t6():
    assert _h(cavab_T6) == "2e7d2c03a9507ae265ecf5b5356885a53393a2029d241394997265a1a25aefc6", "cavab düzgün deyil"
check("T6", 10, test_t6)


# ======================================================================
# Tapşırıq T7. Test üçün proqnoz (10 bal) — Kod tapşırığı · Scikit-Learn ilə xətti reqressiya və model qiymətləndirilməsi · qismən qiymətləndirmə (0–10 bal arası)
#
# Öyrədilmiş model vasitəsilə X_test üçün proqnozları (y_pred) hesablayıb qaytaran proqnoz_ver(model, X_test) funksiyasını yazın (model.predict(X_test)).
# ======================================================================

with hell("T7"):
    def proqnoz_ver(model, X_test):
        # buranı yazın
        pass


def test_t7():
    rs = np.random.RandomState(0)
    X_train = rs.rand(40, 2) * 10
    y_train = 3 * X_train[:, 0] - 2 * X_train[:, 1] + 5
    X_test = rs.rand(10, 2) * 10
    from sklearn.linear_model import LinearRegression
    model = LinearRegression().fit(X_train, y_train)
    r = proqnoz_ver(model, X_test)
    return grade(
        (3, "hər test nümunəsi üçün bir proqnoz olmalıdır (10 ədəd)", lambda: len(r) == 10),
        (7, "proqnoz dəyərləri düzgün deyil", lambda: np.allclose(r, model.predict(X_test))),
    )
check("T7", 10, test_t7)


# ======================================================================
# Tapşırıq T8. Log-transformasiya (np.log1p) (10 bal) — Nəzəri sual (yalnız 0 və ya 10 bal)
#
# np.log1p(x) əməliyyatının mahiyyəti və xətti modellərə təsiri haqqında hansı ifadə düzgündür?
#   a) Yalnız mənfi ədədlərə tətbiq oluna bilər və qiymətləri 0–1 intervalına salır
#   b) log(1 + x) hesablayır: böyük qiymətləri sıxaraq sağ əyriliyi azaldır, x = 0 üçün də təyin olunub və xətti modelin işini yaxşılaşdıra bilər
#   c) Verilənlərin paylanmasına heç bir təsir göstərmir, yalnız sütunun adını dəyişir
#   d) Paylanmanı daha da sağa əyir və kənar qiymətlərin təsirini artırır
# ======================================================================

cavab_T8 = ""      # düzgün variantın hərfi: "a", "b", "c" və ya "d"


def test_t8():
    assert _h(cavab_T8) == "3e23e8160039594a33894f6564e1b1348bbd7a0088d42c4acb73eeaed59c009d", "cavab düzgün deyil"
check("T8", 10, test_t8)


# ======================================================================
# Tapşırıq T9. Hər sütunda çatışmayan qiymətlər (10 bal) — Kod tapşırığı · Pandas ilə verilənlərin oxunması və ilkin baxış · yalnız 0 və ya 10 bal
#
# DataFrame-in hər sütununda neçə çatışmayan (NaN) qiymət olduğunu qaytaran catismayanlar(df) funksiyasını yazın (df.isna().sum()).
# ======================================================================

with hell("T9"):
    def catismayanlar(df):
        # buranı yazın
        pass


def test_t9():
    df = pd.DataFrame({"a": [1, None, 3, None], "b": [None, 2, 3, 4], "c": [1, 2, 3, 4]})
    r = catismayanlar(df)
    assert dict(r) == {"a": 2, "b": 1, "c": 0}, f"hər sütun üçün NaN sayı {{'a': 2, 'b': 1, 'c': 0}} olmalıdır, sizinki: {dict(r)}"
check("T9", 10, test_t9)


# ======================================================================
# Tapşırıq T10. MAE və RMSE fərqi (10 bal) — Nəzəri sual (yalnız 0 və ya 10 bal)
#
# Reqressiya metrikləri MAE və RMSE arasındakı əsas fərq nədir?
#   a) RMSE kənar qiymətlərə MAE-dən daha az həssasdır
#   b) MAE mütləq xətaların ortasıdır və hədəflə eyni vahiddədir; RMSE xətaları kvadrata yüksəldir, ona görə böyük xətalara (kənar qiymətlərə) daha həssasdır
#   c) RMSE həmişə MAE-dən kiçik olur
#   d) MAE xətaların kvadratına, RMSE isə mütləq qiymətinə əsaslanır
# ======================================================================

cavab_T10 = ""      # düzgün variantın hərfi: "a", "b", "c" və ya "d"


def test_t10():
    assert _h(cavab_T10) == "3e23e8160039594a33894f6564e1b1348bbd7a0088d42c4acb73eeaed59c009d", "cavab düzgün deyil"
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
