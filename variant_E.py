# -*- coding: utf-8 -*-
"""
BAKI MÜHƏNDİSLİK UNİVERSİTETİ (BMU)
Fənn: Maşın Öyrənməsinə Giriş — SDF 1 (Variant E)
Maksimum bal: 100 (10 tapşırıq: 4 nəzəri + 6 praktiki, hər biri 10 bal)

İSTİFADƏ QAYDASI
1. Nəzəri suallarda düzgün variantın hərfini (a, b, c və ya d) `cavab_T..` dəyişəninə yazın.
2. Kod tapşırıqlarında funksiyanı `with hell("T..."):` blokunun İÇİNDƏ yazın
   (blokun içindəki sətirlər 4 boşluq girintili olmalıdır). `pass` əvəzinə funksiyanın gövdəsini yazın.
3. Faylı işə salın:   python variant_E.py
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
# Tapşırıq T1. StandardScaler ilə standartlaşdırma (10 bal) — Kod tapşırığı · EDA, statistika və preprocessing · qismən qiymətləndirmə (0–10 bal arası)
#
# StandardScaler obyektini yaradın və X_train-ə fit_transform() tətbiq edin. Funksiya (scaler, X_scaled) cütünü qaytarmalıdır: standartlas(X_train).
# İdxal: from sklearn.preprocessing import StandardScaler.
# ======================================================================

with hell("T1"):
    def standartlas(X_train):
        # buranı yazın
        pass


def test_t1():
    X = np.array([[1.0, 100.0], [2.0, 200.0], [3.0, 300.0], [4.0, 400.0]])
    r = standartlas(X)
    return grade(
        (2, "nəticə (scaler, X_scaled) cütü olmalıdır", lambda: len(r) == 2 and hasattr(r[0], "mean_")),
        (4, "hər sütunun ortası 0 olmalıdır", lambda: np.allclose(np.asarray(r[1]).mean(axis=0), 0)),
        (4, "hər sütunun standart sapması 1 olmalıdır", lambda: np.allclose(np.asarray(r[1]).std(axis=0), 1)),
    )
check("T1", 10, test_t1)


# ======================================================================
# Tapşırıq T2. Miqyaslama və StandardScaler (10 bal) — Nəzəri sual (yalnız 0 və ya 10 bal)
#
# StandardScaler vasitəsilə standartlaşdırma necə işləyir?
#   a) (x − min) / (max − min) hesablanır və qiymətlər [0, 1] intervalına düşür
#   b) Qiymətlər sıralanır və hər birinə yalnız sıra nömrəsi verilir
#   c) Hər qiymət sütunun maksimumuna bölünür və orta qiymət dəyişmir
#   d) Hər xüsusiyyət üçün z = (x − μ) / σ hesablanır; nəticədə orta 0, standart sapma 1 olur, μ və σ təlim hissəsindən tapılır
# ======================================================================

cavab_T2 = ""      # düzgün variantın hərfi: "a", "b", "c" və ya "d"


def test_t2():
    assert _h(cavab_T2) == "18ac3e7343f016890c510e93f935261169d9e3f565436429830faf0934f4f8e4", "cavab düzgün deyil"
check("T2", 10, test_t2)


# ======================================================================
# Tapşırıq T3. MSE hesablamaq (10 bal) — Kod tapşırığı · Scikit-Learn ilə xətti reqressiya və model qiymətləndirilməsi · yalnız 0 və ya 10 bal
#
# Həqiqi y_test və proqnoz y_pred arasında MSE (orta kvadratik xəta) göstəricisini hesablayıb qaytaran mse_hesabla(y_test, y_pred) funksiyasını yazın (mean_squared_error).
# ======================================================================

with hell("T3"):
    def mse_hesabla(y_test, y_pred):
        # buranı yazın
        pass


def test_t3():
    assert _eq(mse_hesabla([3, 5, 2], [2, 5, 4]), 5 / 3), f"[3, 5, 2] və [2, 5, 4] üçün MSE = 5/3 olmalıdır, sizinki: {mse_hesabla([3, 5, 2], [2, 5, 4])!r}"
    assert _eq(mse_hesabla([10, 20], [7, 26]), 22.5), "[10, 20] və [7, 26] üçün MSE = 22.5 olmalıdır"
check("T3", 10, test_t3)


# ======================================================================
# Tapşırıq T4. Kənar qiymətləri kəsmək (clip) (10 bal) — Kod tapşırığı · EDA, statistika və preprocessing · qismən qiymətləndirmə (0–10 bal arası)
#
# seriya sütunundakı qiymətləri low və high hədlərinə kəsən (clip) kenar_kes(seriya, low, high) funksiyasını yazın və nəticəni qaytarın.
# Nümunə: [1, 50, 200], low=10, high=100 → [10, 50, 100].
# ======================================================================

with hell("T4"):
    def kenar_kes(seriya, low, high):
        # buranı yazın
        pass


def test_t4():
    s = pd.Series([1, 50, 200, 10, 100])
    r = kenar_kes(s, 10, 100)
    return grade(
        (4, "aşağı hədd (10) tətbiq olunmalıdır", lambda: list(r)[0] == 10),
        (4, "yuxarı hədd (100) tətbiq olunmalıdır", lambda: list(r)[2] == 100),
        (2, "hədlər daxilindəki qiymətlər dəyişməməlidir", lambda: list(r)[1] == 50 and list(r)[3] == 10 and list(r)[4] == 100),
    )
check("T4", 10, test_t4)


# ======================================================================
# Tapşırıq T5. Qradient enişində öyrənmə sürəti (10 bal) — Nəzəri sual (yalnız 0 və ya 10 bal)
#
# Qradient Enişində (Gradient Descent) öyrənmə sürəti alpha parametrinin rolu və seçimi haqqında hansı ifadə düzgündür?
#   a) alpha hər addımda parametrlərin yenilənmə ölçüsünü təyin edir: çox böyük olarsa minimum ətrafında salınma və ya diverqensiya, çox kiçik olarsa çox yavaş yaxınlaşma baş verir
#   b) alpha çox kiçik olarsa alqoritm diverqensiyaya uğrayır
#   c) alpha nə qədər böyük olsa, alqoritm həmişə daha sürətli və daha dəqiq yaxınlaşır
#   d) alpha təlim verilənlərindəki nümunələrin sayıdır
# ======================================================================

cavab_T5 = ""      # düzgün variantın hərfi: "a", "b", "c" və ya "d"


def test_t5():
    assert _h(cavab_T5) == "ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb", "cavab düzgün deyil"
check("T5", 10, test_t5)


# ======================================================================
# Tapşırıq T6. Matrisin ölçü xassələri (10 bal) — Kod tapşırığı · NumPy ilə massivlər və ədədi hesablamalar · qismən qiymətləndirmə (0–10 bal arası)
#
# Verilmiş NumPy matrisi m üçün (m.shape, m.ndim, m.size) üçlüyünü qaytaran matris_xasseleri(m) funksiyasını yazın.
# Nümunə: 3x3 matris üçün ((3, 3), 2, 9).
# ======================================================================

with hell("T6"):
    def matris_xasseleri(m):
        # buranı yazın
        pass


def test_t6():
    m = np.arange(12).reshape(3, 4)
    r = matris_xasseleri(m)
    return grade(
        (3, "nəticə 3 elementli olmalıdır", lambda: len(r) == 3),
        (3, "shape düzgün deyil", lambda: tuple(r[0]) == (3, 4)),
        (2, "ndim düzgün deyil", lambda: r[1] == 2),
        (2, "size düzgün deyil", lambda: r[2] == 12),
    )
check("T6", 10, test_t6)


# ======================================================================
# Tapşırıq T7. X və y ayırmaq (10 bal) — Kod tapşırığı · Pandas ilə seçim, filtrasiya və dəyişənlərin işlənməsi · qismən qiymətləndirmə (0–10 bal arası)
#
# 'target' sütununu y dəyişəninə, qalan sütunları X dəyişəninə mənimsədib (X, y) cütü kimi qaytaran x_y_ayir(df) funksiyasını yazın (df.drop(columns=['target'])).
# ======================================================================

with hell("T7"):
    def x_y_ayir(df):
        # buranı yazın
        pass


def test_t7():
    df = pd.DataFrame({"f1": [1, 2, 3], "f2": [4, 5, 6], "target": [0, 1, 0]})
    r = x_y_ayir(df)
    return grade(
        (2, "nəticə iki elementli olmalıdır", lambda: len(r) == 2),
        (4, "X-də 'target' olmamalı, yalnız f1 və f2 olmalıdır", lambda: list(r[0].columns) == ["f1", "f2"]),
        (4, "y 'target' sütunu olmalıdır", lambda: list(r[1]) == [0, 1, 0]),
    )
check("T7", 10, test_t7)


# ======================================================================
# Tapşırıq T8. Çatışmayan qiymət mexanizmləri (10 bal) — Nəzəri sual (yalnız 0 və ya 10 bal)
#
# Çatışmayan qiymətlərin MCAR, MAR və MNAR mexanizmləri necə fərqlənir?
#   a) MCAR: çatışma qiymətin özündən asılıdır; MAR: tam təsadüfidir; MNAR: digər dəyişənlərdən asılıdır
#   b) MCAR yalnız ədədi, MAR yalnız mətn, MNAR yalnız tarix sütunlarında yaranır
#   c) Üçü də eyni mənanı verir və yalnız kateqorik sütunlara aiddir
#   d) MCAR: çatışma tam təsadüfidir; MAR: çatışma digər müşahidə olunan dəyişənlərdən asılıdır; MNAR: çatışma çatışan qiymətin özündən asılıdır
# ======================================================================

cavab_T8 = ""      # düzgün variantın hərfi: "a", "b", "c" və ya "d"


def test_t8():
    assert _h(cavab_T8) == "18ac3e7343f016890c510e93f935261169d9e3f565436429830faf0934f4f8e4", "cavab düzgün deyil"
check("T8", 10, test_t8)


# ======================================================================
# Tapşırıq T9. DataFrame.info() (10 bal) — Kod tapşırığı · Pandas ilə verilənlərin oxunması və ilkin baxış · qismən qiymətləndirmə (0–10 bal arası)
#
# DataFrame haqqında ümumi texniki xülasəni (sütun tipləri və boş olmayan dəyərlər) ekrana çap edən xulase_cap(df) funksiyasını yazın (df.info()).
# ======================================================================

with hell("T9"):
    def xulase_cap(df):
        # buranı yazın
        pass


def test_t9():
    import io, contextlib
    df = pd.DataFrame({"yas": [20, 21, None], "ad": ["A", "B", "C"]})
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        xulase_cap(df)
    out = buf.getvalue()
    return grade(
        (3, "heç nə çap edilməyib", lambda: len(out.strip()) > 0),
        (4, "sütun adları xülasədə olmalıdır", lambda: "yas" in out and "ad" in out),
        (3, "boş olmayan dəyərlərin sayı göstərilməlidir (info() çıxışı)", lambda: "Non-Null" in out),
    )
check("T9", 10, test_t9)


# ======================================================================
# Tapşırıq T10. EDA və ön emal fərqi (10 bal) — Nəzəri sual (yalnız 0 və ya 10 bal)
#
# EDA (kəşfiyyat təhlili) ilə verilənlərin ön emalı (data preprocessing) mərhələləri necə fərqlənir?
#   a) EDA verilənləri dəyişir, ön emal isə yalnız onlara baxır
#   b) İki mərhələ eynidir və adlar fərqli yazılır
#   c) EDA yalnız test verilənlərinə, ön emal isə yalnız nəticələrə tətbiq olunur
#   d) EDA verilənləri anlamaq və araşdırmaq üçündür (statistika, qrafiklər); ön emal isə modelə verməzdən əvvəl verilənləri dəyişən addımlardır (doldurma, kodlaşdırma, miqyaslama)
# ======================================================================

cavab_T10 = ""      # düzgün variantın hərfi: "a", "b", "c" və ya "d"


def test_t10():
    assert _h(cavab_T10) == "18ac3e7343f016890c510e93f935261169d9e3f565436429830faf0934f4f8e4", "cavab düzgün deyil"
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
