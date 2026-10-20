# -*- coding: utf-8 -*-
"""
BAKI MÜHƏNDİSLİK UNİVERSİTETİ (BMU)
Fənn: Maşın Öyrənməsinə Giriş — SDF 1 (Variant D)
Maksimum bal: 100 (10 tapşırıq: 4 nəzəri + 6 praktiki, hər biri 10 bal)

İSTİFADƏ QAYDASI
1. Nəzəri suallarda düzgün variantın hərfini (a, b, c və ya d) `cavab_T..` dəyişəninə yazın.
2. Kod tapşırıqlarında funksiyanı `with hell("T..."):` blokunun İÇİNDƏ yazın
   (blokun içindəki sətirlər 4 boşluq girintili olmalıdır). `pass` əvəzinə funksiyanın gövdəsini yazın.
3. Faylı işə salın:   python variant_D.py
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
# Tapşırıq T1. Verilənlər sızması (data leakage) (10 bal) — Nəzəri sual (yalnız 0 və ya 10 bal)
#
# Verilənlər sızması (data leakage) nədir və train/test bölgüsü necə aparılmalıdır?
#   a) Test verilənlərindən məlumatın təlim prosesinə keçməsidir (məsələn, bölgüdən əvvəl bütün verilənlərə scaler fit etmək); düzgün yol əvvəl bölmək, ön emalı yalnız train-də fit etmək, test-ə yalnız transform tətbiq etməkdir
#   b) Test verilənlərini də təlimdə istifadə etmək dəqiqliyi artırdığı üçün düzgün və tövsiyə olunan yoldur
#   c) Yalnız hədəf sütunun adı dəyişdikdə baş verir və bölgüyə aid deyil
#   d) Verilənlərin bir hissəsinin itməsidir; bölgüdən əvvəl bütün verilənlərə scaler fit etmək məsləhət görülür
# ======================================================================

cavab_T1 = ""      # düzgün variantın hərfi: "a", "b", "c" və ya "d"


def test_t1():
    assert _h(cavab_T1) == "ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb", "cavab düzgün deyil"
check("T1", 10, test_t1)


# ======================================================================
# Tapşırıq T2. Kateqorik sütunun nisbətləri (10 bal) — Kod tapşırığı · Pandas ilə verilənlərin oxunması və ilkin baxış · qismən qiymətləndirmə (0–10 bal arası)
#
# df[sutun] kateqorik sütunundakı unikal dəyərlərin nisbətlərini (cəmi 1) qaytaran nisbetler(df, sutun) funksiyasını yazın (value_counts(normalize=True)).
# ======================================================================

with hell("T2"):
    def nisbetler(df, sutun):
        # buranı yazın
        pass


def test_t2():
    df = pd.DataFrame({"city": ["Baku", "Baku", "Ganja", "Baku", "Sumqayit", "Ganja", "Baku", "Baku"]})
    r = nisbetler(df, "city")
    return grade(
        (6, "nisbətlər düzgün deyil (Baku=0.625, Ganja=0.25, Sumqayit=0.125)", lambda: _eq(dict(r), {"Baku": 0.625, "Ganja": 0.25, "Sumqayit": 0.125})),
        (2, "nisbətlərin cəmi 1 olmalıdır", lambda: abs(float(sum(r)) - 1.0) < 1e-9),
        (2, "ən çox təkrarlanan dəyər birinci olmalıdır", lambda: r.index[0] == "Baku"),
    )
check("T2", 10, test_t2)


# ======================================================================
# Tapşırıq T3. Massivin orta qiyməti (10 bal) — Kod tapşırığı · NumPy ilə massivlər və ədədi hesablamalar · qismən qiymətləndirmə (0–10 bal arası)
#
# scores NumPy massivinin orta qiymətini np.mean() ilə hesablayıb qaytaran ortalama_hesabla(scores) funksiyasını yazın.
# Nümunə: np.array([70, 80, 90]) → 80.0.
# ======================================================================

with hell("T3"):
    def ortalama_hesabla(scores):
        # buranı yazın
        pass


def test_t3():
    return grade(
        (4, "tam ədədlərdən massiv", lambda: _eq(ortalama_hesabla(np.array([70, 80, 90])), 80.0)),
        (3, "mənfi və kəsr qiymətli massiv", lambda: _eq(ortalama_hesabla(np.array([-2.5, 4.0, 1.5, 9.0])), 3.0)),
        (3, "nəticə tək ədəd olmalıdır (massiv yox)", lambda: isinstance(ortalama_hesabla(np.array([1, 2, 3])), (int, float, np.number))),
    )
check("T3", 10, test_t3)


# ======================================================================
# Tapşırıq T4. Maşın öyrənməsi və nəzarətli öyrənmənin qolları (10 bal) — Nəzəri sual (yalnız 0 və ya 10 bal)
#
# Maşın öyrənməsi (Machine Learning) anlayışı və nəzarətli öyrənmənin (supervised learning) əsas qolları haqqında hansı ifadə düzgündür?
#   a) Nəzarətli öyrənmə etiketsiz verilənlərlə işləyir və yalnız qruplaşdırma aparır
#   b) Maşın öyrənməsi alqoritmin qanunauyğunluqları açıq qaydalar yazılmadan verilənlərdən öyrənməsidir; nəzarətli öyrənmənin əsas qolları reqressiya və klassifikasiyadır
#   c) Nəzarətli öyrənmə yalnız şəkil tanıma məsələlərinə aiddir, reqressiya buraya daxil deyil
#   d) Maşın öyrənməsi bütün qaydaların proqramçı tərəfindən əl ilə yazılmasıdır; nəzarətli öyrənmənin qolları klasterləşdirmə və ölçü azaldılmasıdır
# ======================================================================

cavab_T4 = ""      # düzgün variantın hərfi: "a", "b", "c" və ya "d"


def test_t4():
    assert _h(cavab_T4) == "3e23e8160039594a33894f6564e1b1348bbd7a0088d42c4acb73eeaed59c009d", "cavab düzgün deyil"
check("T4", 10, test_t4)


# ======================================================================
# Tapşırıq T5. Sıfırlardan ibarət massiv (10 bal) — Kod tapşırığı · NumPy ilə massivlər və ədədi hesablamalar · yalnız 0 və ya 10 bal
#
# Bütün elementləri sıfır olan 2x3 ölçülü NumPy massivini (np.zeros() ilə) qaytaran sifir_massiv() funksiyasını yazın.
# ======================================================================

with hell("T5"):
    def sifir_massiv():
        # buranı yazın
        pass


def test_t5():
    r = sifir_massiv()
    assert isinstance(r, np.ndarray), "nəticə NumPy massivi olmalıdır"
    assert r.shape == (2, 3), f"shape (2, 3) olmalıdır, sizinki: {r.shape}"
    assert (r == 0).all(), "bütün elementlər 0 olmalıdır"
check("T5", 10, test_t5)


# ======================================================================
# Tapşırıq T6. MSE-də kvadratik xəta (10 bal) — Nəzəri sual (yalnız 0 və ya 10 bal)
#
# Orta Kvadratik Xəta (MSE) məsrəf funksiyasında xətanın kvadratının alınmasının riyazi üstünlüyü nədir?
#   a) Xətanı kiçildir və nəticəni hədəflə eyni ölçü vahidində saxlayır
#   b) Mütləq dəyər kimi hər nöqtədə diferensiallanır və kənar qiymətlərə qətiyyən həssas deyil
#   c) Yalnız mənfi xətaları müsbətə çevirir, böyük xətaların təsiri dəyişmir
#   d) Xətanın işarəsini aradan qaldırır, böyük xətaları daha çox cəzalandırır və hamar, diferensiallanan funksiya verdiyi üçün qradient eniş üçün əlverişlidir
# ======================================================================

cavab_T6 = ""      # düzgün variantın hərfi: "a", "b", "c" və ya "d"


def test_t6():
    assert _h(cavab_T6) == "18ac3e7343f016890c510e93f935261169d9e3f565436429830faf0934f4f8e4", "cavab düzgün deyil"
check("T6", 10, test_t6)


# ======================================================================
# Tapşırıq T7. iloc ilə seçim (10 bal) — Kod tapşırığı · Pandas ilə seçim, filtrasiya və dəyişənlərin işlənməsi · qismən qiymətləndirmə (0–10 bal arası)
#
# df.iloc vasitəsilə DataFrame-in ilk 3 sətrini və ilk 2 sütununu seçib qaytaran iloc_ile(df) funksiyasını yazın.
# ======================================================================

with hell("T7"):
    def iloc_ile(df):
        # buranı yazın
        pass


def test_t7():
    df = pd.DataFrame(
        {"study_hours": [5, 2, 8, 6, 4, 9], "score": [70, 40, 90, 75, 60, 95], "attendance": [85, 60, 95, 80, 70, 100]},
        index=["A01", "A02", "A03", "A04", "A05", "A06"],
    )
    r = iloc_ile(df)
    return grade(
        (4, "ölçü (3, 2) olmalıdır", lambda: tuple(r.shape) == (3, 2)),
        (3, "sütunlar ilk iki sütun olmalıdır", lambda: list(r.columns) == ["study_hours", "score"]),
        (3, "sətirlər ilk üç sətir olmalıdır", lambda: list(r.index) == ["A01", "A02", "A03"]),
    )
check("T7", 10, test_t7)


# ======================================================================
# Tapşırıq T8. Pirson korrelyasiyası (r = 0) (10 bal) — Nəzəri sual (yalnız 0 və ya 10 bal)
#
# İki dəyişən arasında Pirson korrelyasiya əmsalı r = 0 olarsa, nə demək olar?
#   a) Hər iki dəyişən mütləq sabit qiymətlərdir
#   b) Dəyişənlər tam müstəqildir, heç bir asılılıq ola bilməz
#   c) Aralarında xətti asılılıq yoxdur, lakin qeyri-xətti asılılıq (məsələn, parabolik) hələ də mövcud ola bilər
#   d) Dəyişənlər arasında mükəmməl mənfi xətti asılılıq var
# ======================================================================

cavab_T8 = ""      # düzgün variantın hərfi: "a", "b", "c" və ya "d"


def test_t8():
    assert _h(cavab_T8) == "2e7d2c03a9507ae265ecf5b5356885a53393a2029d241394997265a1a25aefc6", "cavab düzgün deyil"
check("T8", 10, test_t8)


# ======================================================================
# Tapşırıq T9. LinearRegression obyekti (10 bal) — Kod tapşırığı · Scikit-Learn ilə xətti reqressiya və model qiymətləndirilməsi · yalnız 0 və ya 10 bal
#
# sklearn.linear_model modulundan LinearRegression modelini idxal edin və yeni (təlim olunmamış) model obyektini qaytaran model_yarat() funksiyasını yazın.
# ======================================================================

with hell("T9"):
    def model_yarat():
        # buranı yazın
        pass


def test_t9():
    from sklearn.linear_model import LinearRegression
    m = model_yarat()
    assert isinstance(m, LinearRegression), f"LinearRegression obyekti gözlənilirdi, sizinki: {type(m).__name__}"
    assert not hasattr(m, "coef_"), "model hələ təlim olunmamalıdır (fit çağırmayın)"
check("T9", 10, test_t9)


# ======================================================================
# Tapşırıq T10. Stratify ilə bölgü (10 bal) — Kod tapşırığı · EDA, statistika və preprocessing · qismən qiymətləndirmə (0–10 bal arası)
#
# Klassifikasiya məsələsində sinif balansını qorumaq üçün X və y-ni stratify=y parametri ilə test_size=0.2 nisbətində bölün və X_train, X_test, y_train, y_test qaytaran strat_bol(X, y) funksiyasını yazın.
# ======================================================================

with hell("T10"):
    def strat_bol(X, y):
        # buranı yazın
        pass


def test_t10():
    def _data(n_pos, seed):
        y = np.array([1] * n_pos + [0] * (200 - n_pos))
        X = np.random.RandomState(seed).rand(200, 2)
        return X, y
    def _pos_test(n_pos, seed):
        X, y = _data(n_pos, seed)
        r = strat_bol(X, y)
        return int(np.sum(r[3] == 1))
    return grade(
        (3, "test hissəsi 40 nümunə olmalıdır", lambda: len(strat_bol(*_data(20, 0))[1]) == 40),
        (2, "10 müsbət nümunə: testdə 2 olmalıdır (5%)", lambda: _pos_test(10, 0) == 2),
        (2, "20 müsbət nümunə: testdə 4 olmalıdır (10%)", lambda: _pos_test(20, 1) == 4),
        (3, "30 müsbət nümunə: testdə 6 olmalıdır (15%)", lambda: _pos_test(30, 2) == 6),
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
