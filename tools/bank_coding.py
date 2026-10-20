# -*- coding: utf-8 -*-
"""imtahan_suallari-v3.docx, Hissə 2: 40 kod yazma tapşırığı (5 kateqoriya).

Hər tapşırıq funksiya yazmaq formasındadır (avtomatik yoxlanılır).
`partial=True` olan tapşırıqlar 0–10 arası qismən balla, `partial=False` olanlar 0 və ya 10 bal ilə qiymətləndirilir.
Test gövdəsi `def test_...():` daxilinə yerləşdirilir; qismən testlər `return grade((çəki, "hissə", lambda: ...), ...)` ilə bitir.
Hissə çəkilərinin cəmi həmişə 10-dur.
"""
import textwrap

CATEGORIES = {
    1: "NumPy ilə massivlər və ədədi hesablamalar",
    2: "Pandas ilə verilənlərin oxunması və ilkin baxış",
    3: "Pandas ilə seçim, filtrasiya və dəyişənlərin işlənməsi",
    4: "EDA, statistika və preprocessing",
    5: "Scikit-Learn ilə xətti reqressiya və model qiymətləndirilməsi",
}
CAT_SHORT = {1: "NumPy", 2: "Pandas · oxu", 3: "Pandas · seçim", 4: "EDA · preprocessing", 5: "Scikit-Learn"}

CODING = {}


def _unalign(text):
    """Mənbə faylında vizual hizalama üçün qoyulan 1 əlavə boşluğu (ilk sətirdən sonrakı sətirlərdə) silir."""
    lines = text.strip("\n").split("\n")
    rest = lines[1:]
    if rest and all(l.startswith(" ") for l in rest if l.strip()):
        rest = [l[1:] if l.strip() else l for l in rest]
    return "\n".join([lines[0]] + rest)


def task(num, cat, title, desc, starter, solution, test, partial=True):
    CODING[num] = dict(num=num, cat=cat, title=title, desc=_unalign(desc).strip(),
                       starter=_unalign(starter), solution=_unalign(solution),
                       test=textwrap.dedent(test).strip("\n"), partial=partial)


# ===================== Kateqoriya 1: NumPy =====================
task(1, 1, "Massivin orta qiyməti",
 """`scores` NumPy massivinin orta qiymətini `np.mean()` ilə hesablayıb **qaytaran** `ortalama_hesabla(scores)` funksiyasını yazın.
 Nümunə: `np.array([70, 80, 90])` → `80.0`.""",
 """def ortalama_hesabla(scores):
     # buranı yazın
     pass""",
 """def ortalama_hesabla(scores):
     return np.mean(scores)""",
 """return grade(
    (4, "tam ədədlərdən massiv", lambda: _eq(ortalama_hesabla(np.array([70, 80, 90])), 80.0)),
    (3, "mənfi və kəsr qiymətli massiv", lambda: _eq(ortalama_hesabla(np.array([-2.5, 4.0, 1.5, 9.0])), 3.0)),
    (3, "nəticə tək ədəd olmalıdır (massiv yox)", lambda: isinstance(ortalama_hesabla(np.array([1, 2, 3])), (int, float, np.number))),
)""")

task(2, 1, "Matrisin ölçü xassələri",
 """Verilmiş NumPy matrisi `m` üçün `(m.shape, m.ndim, m.size)` üçlüyünü **qaytaran** `matris_xasseleri(m)` funksiyasını yazın.
 Nümunə: `3x3` matris üçün `((3, 3), 2, 9)`.""",
 """def matris_xasseleri(m):
     # buranı yazın
     pass""",
 """def matris_xasseleri(m):
     return m.shape, m.ndim, m.size""",
 """m = np.arange(12).reshape(3, 4)
r = matris_xasseleri(m)
return grade(
    (3, "nəticə 3 elementli olmalıdır", lambda: len(r) == 3),
    (3, "shape düzgün deyil", lambda: tuple(r[0]) == (3, 4)),
    (2, "ndim düzgün deyil", lambda: r[1] == 2),
    (2, "size düzgün deyil", lambda: r[2] == 12),
)""")

task(3, 1, "Cüt ədədlər massivi",
 """0-dan 10-a qədər (10 daxil) cüt ədədlərdən ibarət NumPy massivini (`np.arange()` ilə) **qaytaran** `cut_ededler()` funksiyasını yazın.
 Gözlənilən nəticə: `[0, 2, 4, 6, 8, 10]`.""",
 """def cut_ededler():
     # buranı yazın
     pass""",
 """def cut_ededler():
     return np.arange(0, 11, 2)""",
 """r = cut_ededler()
return grade(
    (3, "nəticə NumPy massivi olmalıdır", lambda: isinstance(r, np.ndarray)),
    (7, "elementlər [0, 2, 4, 6, 8, 10] olmalıdır", lambda: _eq(r, [0, 2, 4, 6, 8, 10])),
)""")

task(4, 1, "Sıfırlardan ibarət massiv",
 """Bütün elementləri sıfır olan `2x3` ölçülü NumPy massivini (`np.zeros()` ilə) **qaytaran** `sifir_massiv()` funksiyasını yazın.""",
 """def sifir_massiv():
     # buranı yazın
     pass""",
 """def sifir_massiv():
     return np.zeros((2, 3))""",
 """r = sifir_massiv()
assert isinstance(r, np.ndarray), "nəticə NumPy massivi olmalıdır"
assert r.shape == (2, 3), f"shape (2, 3) olmalıdır, sizinki: {r.shape}"
assert (r == 0).all(), "bütün elementlər 0 olmalıdır"
""", partial=False)

task(5, 1, "Şərti filtrasiya (50-dən böyük)",
 """`arr` NumPy massivindən yalnız **50-dən böyük** (`> 50`) elementləri seçib **qaytaran** `boyuk_elementler(arr)` funksiyasını yazın (`arr[arr > 50]`).""",
 """def boyuk_elementler(arr):
     # buranı yazın
     pass""",
 """def boyuk_elementler(arr):
     return arr[arr > 50]""",
 """return grade(
    (4, "adi hal", lambda: _eq(boyuk_elementler(np.array([10, 60, 30, 80, 55])), [60, 80, 55])),
    (3, "50-nin özü daxil edilməməlidir (sərt >)", lambda: _eq(boyuk_elementler(np.array([50, 51, 49, 50])), [51])),
    (3, "uyğun element yoxdursa boş massiv qaytarılmalıdır", lambda: len(boyuk_elementler(np.array([1, 2, 50]))) == 0),
)""")

task(6, 1, "1D massivi 2x3 matrisə çevirmək",
 """6 elementli 1D `arr` massivini `2x3` ölçülü 2D matrisə çevirib **qaytaran** `matrise_cevir(arr)` funksiyasını yazın (`.reshape(2, 3)`).""",
 """def matrise_cevir(arr):
     # buranı yazın
     pass""",
 """def matrise_cevir(arr):
     return arr.reshape(2, 3)""",
 """r = matrise_cevir(np.array([1, 2, 3, 4, 5, 6]))
return grade(
    (5, "shape (2, 3) olmalıdır", lambda: tuple(r.shape) == (2, 3)),
    (5, "elementlərin sırası saxlanmalıdır", lambda: _eq(r, [[1, 2, 3], [4, 5, 6]])),
)""")

task(7, 1, "Minimum və maksimum",
 """NumPy massivinin minimum və maksimum qiymətlərini `(minimum, maksimum)` cütü kimi **qaytaran** `min_maks(arr)` funksiyasını yazın (`np.min()`, `np.max()`).
 Nümunə: `[4, 9, 1, 7]` → `(1, 9)`.""",
 """def min_maks(arr):
     # buranı yazın
     pass""",
 """def min_maks(arr):
     return np.min(arr), np.max(arr)""",
 """r = min_maks(np.array([4, 9, 1, 7]))
return grade(
    (2, "nəticə iki elementli olmalıdır", lambda: len(r) == 2),
    (4, "minimum düzgün deyil", lambda: r[0] == 1),
    (4, "maksimum düzgün deyil", lambda: r[1] == 9),
)""")

task(8, 1, "Elementbəelement vurma",
 """İki 1D NumPy massivini elementbəelement vuran (vektorlaşdırılmış, dövrsüz) `vur(arr1, arr2)` funksiyasını yazın və nəticəni **qaytarın**.
 Nümunə: `[1, 2, 3]` və `[4, 5, 6]` → `[4, 10, 18]`.""",
 """def vur(arr1, arr2):
     # buranı yazın
     pass""",
 """def vur(arr1, arr2):
     return arr1 * arr2""",
 """r = vur(np.array([1, 2, 3]), np.array([4, 5, 6]))
assert _eq(r, [4, 10, 18]), f"[4, 10, 18] gözlənilirdi, sizinki: {r!r}"
r2 = vur(np.array([0.5, -2.0]), np.array([4.0, 3.0]))
assert _eq(r2, [2.0, -6.0]), f"[2.0, -6.0] gözlənilirdi, sizinki: {r2!r}"
""", partial=False)

# ===================== Kateqoriya 2: Pandas oxu =====================
task(9, 2, "CSV oxumaq və ilk 5 sətir",
 """Verilmiş `fayl` yolundakı CSV faylını Pandas ilə oxuyun (`pd.read_csv()`) və **ilk 5 sətri** (`.head()`) DataFrame kimi **qaytaran** `ilk_bes(fayl)` funksiyasını yazın.""",
 """def ilk_bes(fayl):
     # buranı yazın
     pass""",
 """def ilk_bes(fayl):
     return pd.read_csv(fayl).head()""",
 """import os, tempfile
_p = os.path.join(tempfile.gettempdir(), "imtahan_students.csv")
with open(_p, "w", encoding="utf-8") as _f:
    _f.write("id,study_hours,score\\n" + "\\n".join(f"{i},{i + 1},{50 + i}" for i in range(1, 9)) + "\\n")
r = ilk_bes(_p)
return grade(
    (3, "nəticə DataFrame olmalıdır", lambda: isinstance(r, pd.DataFrame)),
    (4, "yalnız ilk 5 sətir qaytarılmalıdır", lambda: len(r) == 5),
    (3, "sütun adları faylla eyni olmalıdır", lambda: list(r.columns) == ["id", "study_hours", "score"]),
)""")

task(10, 2, "Shape və dtypes",
 """DataFrame-in ölçüsünü və sütun tiplərini `(df.shape, df.dtypes)` cütü kimi **qaytaran** `olcu_ve_tipler(df)` funksiyasını yazın.""",
 """def olcu_ve_tipler(df):
     # buranı yazın
     pass""",
 """def olcu_ve_tipler(df):
     return df.shape, df.dtypes""",
 """df = pd.DataFrame({"a": [1, 2, 3], "b": [1.5, 2.5, 3.5], "c": ["x", "y", "z"]})
r = olcu_ve_tipler(df)
return grade(
    (2, "nəticə iki elementli olmalıdır", lambda: len(r) == 2),
    (4, "shape (3, 3) olmalıdır", lambda: tuple(r[0]) == (3, 3)),
    (4, "sütun tipləri düzgün deyil", lambda: {k: str(v) for k, v in dict(r[1]).items()} in ({"a": "int64", "b": "float64", "c": "object"}, {"a": "int64", "b": "float64", "c": "str"}, {"a": "int64", "b": "float64", "c": "string"})),
)""")

task(11, 2, "DataFrame.info()",
 """DataFrame haqqında ümumi texniki xülasəni (sütun tipləri və boş olmayan dəyərlər) **ekrana çap edən** `xulase_cap(df)` funksiyasını yazın (`df.info()`).""",
 """def xulase_cap(df):
     # buranı yazın
     pass""",
 """def xulase_cap(df):
     df.info()""",
 """import io, contextlib
df = pd.DataFrame({"yas": [20, 21, None], "ad": ["A", "B", "C"]})
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    xulase_cap(df)
out = buf.getvalue()
return grade(
    (3, "heç nə çap edilməyib", lambda: len(out.strip()) > 0),
    (4, "sütun adları xülasədə olmalıdır", lambda: "yas" in out and "ad" in out),
    (3, "boş olmayan dəyərlərin sayı göstərilməlidir (info() çıxışı)", lambda: "Non-Null" in out),
)""")

task(12, 2, "Əsas statistik xülasə",
 """DataFrame-in **ədədi** sütunları üçün əsas statistik xülasəni (`count, mean, std, min, 25%, 50%, 75%, max`) hesablayıb **qaytaran** `statistika(df)` funksiyasını yazın (`.describe()`).""",
 """def statistika(df):
     # buranı yazın
     pass""",
 """def statistika(df):
     return df.describe()""",
 """df = pd.DataFrame({"a": [1, 2, 3, 4], "b": [10.0, 20.0, 30.0, 40.0], "c": list("wxyz")})
r = statistika(df)
return grade(
    (2, "nəticə DataFrame olmalıdır", lambda: isinstance(r, pd.DataFrame)),
    (4, "sətir adları describe() nəticəsi kimi olmalıdır", lambda: list(r.index) == ["count", "mean", "std", "min", "25%", "50%", "75%", "max"]),
    (4, "yalnız ədədi sütunlar olmalıdır", lambda: list(r.columns) == ["a", "b"]),
)""")

task(13, 2, "Hər sütunda çatışmayan qiymətlər",
 """DataFrame-in hər sütununda neçə çatışmayan (`NaN`) qiymət olduğunu **qaytaran** `catismayanlar(df)` funksiyasını yazın (`df.isna().sum()`).""",
 """def catismayanlar(df):
     # buranı yazın
     pass""",
 """def catismayanlar(df):
     return df.isna().sum()""",
 """df = pd.DataFrame({"a": [1, None, 3, None], "b": [None, 2, 3, 4], "c": [1, 2, 3, 4]})
r = catismayanlar(df)
assert dict(r) == {"a": 2, "b": 1, "c": 0}, f"hər sütun üçün NaN sayı {{'a': 2, 'b': 1, 'c': 0}} olmalıdır, sizinki: {dict(r)}"
""", partial=False)

task(14, 2, "Təkrarlanan sətirlərin sayı",
 """DataFrame-də təkrarlanan sətirlərin sayını tam ədəd kimi **qaytaran** `tekrar_sayi(df)` funksiyasını yazın (`df.duplicated().sum()`).""",
 """def tekrar_sayi(df):
     # buranı yazın
     pass""",
 """def tekrar_sayi(df):
     return df.duplicated().sum()""",
 """df = pd.DataFrame({"a": [1, 1, 2, 2, 2, 3], "b": ["x", "x", "y", "y", "y", "z"]})
r = tekrar_sayi(df)
assert r == 3, f"3 təkrarlanan sətir gözlənilirdi, sizinki: {r!r}"
assert tekrar_sayi(pd.DataFrame({"a": [1, 2, 3]})) == 0, "təkrar yoxdursa 0 qaytarılmalıdır"
""", partial=False)

task(15, 2, "Kateqorik sütunun nisbətləri",
 """`df[sutun]` kateqorik sütunundakı unikal dəyərlərin **nisbətlərini** (cəmi 1) **qaytaran** `nisbetler(df, sutun)` funksiyasını yazın (`value_counts(normalize=True)`).""",
 """def nisbetler(df, sutun):
     # buranı yazın
     pass""",
 """def nisbetler(df, sutun):
     return df[sutun].value_counts(normalize=True)""",
 """df = pd.DataFrame({"city": ["Baku", "Baku", "Ganja", "Baku", "Sumqayit", "Ganja", "Baku", "Baku"]})
r = nisbetler(df, "city")
return grade(
    (6, "nisbətlər düzgün deyil (Baku=0.625, Ganja=0.25, Sumqayit=0.125)", lambda: _eq(dict(r), {"Baku": 0.625, "Ganja": 0.25, "Sumqayit": 0.125})),
    (2, "nisbətlərin cəmi 1 olmalıdır", lambda: abs(float(sum(r)) - 1.0) < 1e-9),
    (2, "ən çox təkrarlanan dəyər birinci olmalıdır", lambda: r.index[0] == "Baku"),
)""")

task(16, 2, "DataFrame-i CSV-yə yazmaq",
 """DataFrame `df`-i `fayl` yoluna **indeksi saxlamadan** CSV kimi yazan `csv_yaz(df, fayl)` funksiyasını yazın (`df.to_csv(..., index=False)`).""",
 """def csv_yaz(df, fayl):
     # buranı yazın
     pass""",
 """def csv_yaz(df, fayl):
     df.to_csv(fayl, index=False)""",
 """import os, tempfile
_p = os.path.join(tempfile.gettempdir(), "imtahan_clean.csv")
if os.path.exists(_p):
    os.remove(_p)
df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
csv_yaz(df, _p)
def _lines():
    with open(_p, encoding="utf-8") as f:
        return f.read().strip().splitlines()
return grade(
    (3, "fayl yaradılmalıdır", lambda: os.path.exists(_p)),
    (4, "indeks sütunu yazılmamalıdır (başlıq 'a,b' olmalıdır)", lambda: _lines()[0].replace(" ", "") == "a,b"),
    (3, "bütün sətirlər yazılmalıdır", lambda: len(_lines()) == 4),
)""")

# ===================== Kateqoriya 3: Pandas seçim =====================
_DF3 = '''df = pd.DataFrame(
    {"study_hours": [5, 2, 8, 6, 4, 9], "score": [70, 40, 90, 75, 60, 95], "attendance": [85, 60, 95, 80, 70, 100]},
    index=["A01", "A02", "A03", "A04", "A05", "A06"],
)
'''

task(17, 3, "Sütun seçimi (Series və DataFrame)",
 """`df`-dən `'study_hours'` sütununu **Series** kimi, `['study_hours', 'score']` sütunlarını isə **DataFrame** kimi seçib `(seriya, cedvel)` cütü şəklində **qaytaran** `sutunlari_sec(df)` funksiyasını yazın.""",
 """def sutunlari_sec(df):
     # buranı yazın
     pass""",
 """def sutunlari_sec(df):
     return df['study_hours'], df[['study_hours', 'score']]""",
 _DF3 + """r = sutunlari_sec(df)
return grade(
    (2, "nəticə iki elementli olmalıdır", lambda: len(r) == 2),
    (4, "birinci nəticə Series olmalıdır (study_hours)", lambda: isinstance(r[0], pd.Series) and list(r[0]) == [5, 2, 8, 6, 4, 9]),
    (4, "ikinci nəticə iki sütunlu DataFrame olmalıdır", lambda: isinstance(r[1], pd.DataFrame) and list(r[1].columns) == ["study_hours", "score"]),
)""")

task(18, 3, "loc ilə seçim",
 """`df.loc` vasitəsilə `'A02'` sətir indeksi və `'attendance'` sütun adına görə tək dəyəri **qaytaran** `loc_ile(df)` funksiyasını yazın.""",
 """def loc_ile(df):
     # buranı yazın
     pass""",
 """def loc_ile(df):
     return df.loc['A02', 'attendance']""",
 _DF3 + """r = loc_ile(df)
assert r == 60, f"60 gözlənilirdi, sizinki: {r!r}"
assert not isinstance(r, (pd.Series, pd.DataFrame)), "nəticə tək dəyər olmalıdır (Series/DataFrame yox)"
""", partial=False)

task(19, 3, "iloc ilə seçim",
 """`df.iloc` vasitəsilə DataFrame-in **ilk 3 sətrini** və **ilk 2 sütununu** seçib **qaytaran** `iloc_ile(df)` funksiyasını yazın.""",
 """def iloc_ile(df):
     # buranı yazın
     pass""",
 """def iloc_ile(df):
     return df.iloc[0:3, 0:2]""",
 _DF3 + """r = iloc_ile(df)
return grade(
    (4, "ölçü (3, 2) olmalıdır", lambda: tuple(r.shape) == (3, 2)),
    (3, "sütunlar ilk iki sütun olmalıdır", lambda: list(r.columns) == ["study_hours", "score"]),
    (3, "sətirlər ilk üç sətir olmalıdır", lambda: list(r.index) == ["A01", "A02", "A03"]),
)""")

task(20, 3, "Bir şərtlə filtr",
 """`'attendance'` sütunu **80 və ondan böyük** (`>= 80`) olan sətirləri seçib **qaytaran** `davamiyyet_filtr(df)` funksiyasını yazın.""",
 """def davamiyyet_filtr(df):
     # buranı yazın
     pass""",
 """def davamiyyet_filtr(df):
     return df[df['attendance'] >= 80]""",
 _DF3 + """r = davamiyyet_filtr(df)
return grade(
    (5, "sətirlərin sayı düzgün deyil (4 sətir gözlənilir)", lambda: len(r) == 4),
    (3, "seçilən sətirlər düzgün deyil", lambda: list(r.index) == ["A01", "A03", "A04", "A06"]),
    (2, "bütün sütunlar saxlanmalıdır", lambda: list(r.columns) == list(df.columns)),
)""")

task(21, 3, "İki şərtlə filtr (&)",
 """`'attendance' >= 80` **VƏ** `'study_hours' >= 5` şərtlərini eyni vaxtda ödəyən sətirləri `&` operatoru ilə seçib **qaytaran** `iki_sert_filtr(df)` funksiyasını yazın.""",
 """def iki_sert_filtr(df):
     # buranı yazın
     pass""",
 """def iki_sert_filtr(df):
     return df[(df['attendance'] >= 80) & (df['study_hours'] >= 5)]""",
 _DF3 + """r = iki_sert_filtr(df)
return grade(
    (5, "sətirlərin sayı düzgün deyil (4 sətir gözlənilir)", lambda: len(r) == 4),
    (5, "seçilən sətirlər düzgün deyil", lambda: list(r.index) == ["A01", "A03", "A04", "A06"]),
)""")

task(22, 3, "Mətn təmizləmə",
 """Mətn sütununun (`pd.Series`) kənar boşluqlarını silin və kiçik hərflərə çevirin: `temizle(seriya)` funksiyası nəticəni **qaytarsın** (`.str.strip().str.lower()`).
 Nümunə: `"  Baku "` → `"baku"`.""",
 """def temizle(seriya):
     # buranı yazın
     pass""",
 """def temizle(seriya):
     return seriya.str.strip().str.lower()""",
 """s = pd.Series(["  Baku ", "GANJA", " Sumqayit"])
r = temizle(s)
return grade(
    (5, "kənar boşluqlar silinməlidir", lambda: [x.strip() for x in r] == list(r) and list(r)[0].startswith("b")),
    (5, "bütün hərflər kiçik olmalıdır", lambda: list(r) == ["baku", "ganja", "sumqayit"]),
)""")

task(23, 3, "Törəmə sütun",
 """`'price'` və `'area'` sütunlarından istifadə edərək `'price_per_sqm'` (`price / area`) adlı yeni sütun yaradın və DataFrame-i **qaytarın**: `tirem_sutun(df)`.""",
 """def tirem_sutun(df):
     # buranı yazın
     pass""",
 """def tirem_sutun(df):
     df['price_per_sqm'] = df['price'] / df['area']
     return df""",
 """df = pd.DataFrame({"price": [100000, 150000, 90000], "area": [50, 75, 60]})
r = tirem_sutun(df)
return grade(
    (3, "nəticə DataFrame olmalıdır", lambda: isinstance(r, pd.DataFrame)),
    (3, "'price_per_sqm' sütunu yaradılmalıdır", lambda: "price_per_sqm" in r.columns),
    (4, "dəyərlər price / area olmalıdır", lambda: _eq(list(r["price_per_sqm"]), [2000.0, 2000.0, 1500.0])),
)""")

task(24, 3, "X və y ayırmaq",
 """`'target'` sütununu `y` dəyişəninə, qalan sütunları `X` dəyişəninə mənimsədib `(X, y)` cütü kimi **qaytaran** `x_y_ayir(df)` funksiyasını yazın (`df.drop(columns=['target'])`).""",
 """def x_y_ayir(df):
     # buranı yazın
     pass""",
 """def x_y_ayir(df):
     X = df.drop(columns=['target'])
     y = df['target']
     return X, y""",
 """df = pd.DataFrame({"f1": [1, 2, 3], "f2": [4, 5, 6], "target": [0, 1, 0]})
r = x_y_ayir(df)
return grade(
    (2, "nəticə iki elementli olmalıdır", lambda: len(r) == 2),
    (4, "X-də 'target' olmamalı, yalnız f1 və f2 olmalıdır", lambda: list(r[0].columns) == ["f1", "f2"]),
    (4, "y 'target' sütunu olmalıdır", lambda: list(r[1]) == [0, 1, 0]),
)""")

# ===================== Kateqoriya 4: EDA və preprocessing =====================
task(25, 4, "Medianla doldurmaq",
 """`df[sutun]` sütunundakı çatışmayan (`NaN`) qiymətləri həmin sütunun **medianı** ilə doldurub nəticəni (`Series`) **qaytaran** `median_ile_doldur(df, sutun)` funksiyasını yazın (`fillna(df[sutun].median())`).""",
 """def median_ile_doldur(df, sutun):
     # buranı yazın
     pass""",
 """def median_ile_doldur(df, sutun):
     return df[sutun].fillna(df[sutun].median())""",
 """df = pd.DataFrame({"x": [1.0, None, 3.0, 100.0, None]})
r = median_ile_doldur(df, "x")
return grade(
    (4, "çatışmayan qiymət qalmamalıdır", lambda: int(pd.isna(r).sum()) == 0),
    (4, "boşluqlar medianla (3.0) doldurulmalıdır, orta ilə yox", lambda: _eq(list(r), [1.0, 3.0, 3.0, 100.0, 3.0])),
    (2, "mövcud qiymətlər dəyişməməlidir", lambda: list(r)[0] == 1.0 and list(r)[3] == 100.0),
)""")

task(26, 4, "Əyrilik (skewness)",
 """`df[sutun]` sütununun **əyriliyini** (skewness) hesablayıb **qaytaran** `eyrilik(df, sutun)` funksiyasını yazın (`.skew()`).""",
 """def eyrilik(df, sutun):
     # buranı yazın
     pass""",
 """def eyrilik(df, sutun):
     return df[sutun].skew()""",
 """df = pd.DataFrame({"x": [1, 2, 2, 3, 3, 3, 4, 20], "y": [5, 5, 5, 5, 5, 5, 5, 5.5]})
for c in ("x", "y"):
    exp = df[c].skew()
    r = eyrilik(df, c)
    assert _eq(r, exp), f"{c} sütunu üçün {exp!r} gözlənilirdi, sizinki: {r!r}"
""", partial=False)

task(27, 4, "Log-transformasiya (log1p)",
 """`np.log1p()` ilə `'price'` sütununun log-transformasiyasını aparın, nəticəni `'log_price'` adlı yeni sütuna yazın və DataFrame-i **qaytarın**: `log_cevir(df)`.""",
 """def log_cevir(df):
     # buranı yazın
     pass""",
 """def log_cevir(df):
     df['log_price'] = np.log1p(df['price'])
     return df""",
 """df = pd.DataFrame({"price": [0, 9, 99, 999]})
r = log_cevir(df)
return grade(
    (3, "'log_price' sütunu yaradılmalıdır", lambda: "log_price" in r.columns),
    (5, "dəyərlər log(1 + price) olmalıdır", lambda: _eq(list(r["log_price"]), [0.0, math.log(10), math.log(100), math.log(1000)])),
    (2, "'price' sütunu dəyişməməlidir", lambda: list(r["price"]) == [0, 9, 99, 999]),
)""")

task(28, 4, "Pirson korrelyasiyası",
 """`df[s1]` və `df[s2]` ədədi sütunları arasında **Pirson korrelyasiya əmsalını** hesablayıb **qaytaran** `korrelyasiya(df, s1, s2)` funksiyasını yazın (`.corr()`).""",
 """def korrelyasiya(df, s1, s2):
     # buranı yazın
     pass""",
 """def korrelyasiya(df, s1, s2):
     return df[s1].corr(df[s2])""",
 """df = pd.DataFrame({"a": [1, 2, 3, 4, 5], "b": [2, 4, 6, 8, 10], "c": [5, 4, 3, 2, 1], "d": [1, 3, 2, 5, 4]})
return grade(
    (3, "mükəmməl müsbət asılılıq (r = 1)", lambda: _eq(korrelyasiya(df, "a", "b"), 1.0)),
    (3, "mükəmməl mənfi asılılıq (r = -1)", lambda: _eq(korrelyasiya(df, "a", "c"), -1.0)),
    (4, "qismən asılılıq (r = 0.8)", lambda: _eq(korrelyasiya(df, "a", "d"), df["a"].corr(df["d"]))),
)""")

task(29, 4, "Kənar qiymətləri kəsmək (clip)",
 """`seriya` sütunundakı qiymətləri `low` və `high` hədlərinə **kəsən** (`clip`) `kenar_kes(seriya, low, high)` funksiyasını yazın və nəticəni **qaytarın**.
 Nümunə: `[1, 50, 200]`, `low=10`, `high=100` → `[10, 50, 100]`.""",
 """def kenar_kes(seriya, low, high):
     # buranı yazın
     pass""",
 """def kenar_kes(seriya, low, high):
     return seriya.clip(lower=low, upper=high)""",
 """s = pd.Series([1, 50, 200, 10, 100])
r = kenar_kes(s, 10, 100)
return grade(
    (4, "aşağı hədd (10) tətbiq olunmalıdır", lambda: list(r)[0] == 10),
    (4, "yuxarı hədd (100) tətbiq olunmalıdır", lambda: list(r)[2] == 100),
    (2, "hədlər daxilindəki qiymətlər dəyişməməlidir", lambda: list(r)[1] == 50 and list(r)[3] == 10 and list(r)[4] == 100),
)""")

task(30, 4, "Train/test bölgüsü (80/20)",
 """`X` və `y` verilənlərini `train_test_split` vasitəsilə **80% təlim və 20% test** hissələrinə bölün (`test_size=0.2`, `random_state=42`) və `X_train, X_test, y_train, y_test` ardıcıllığı ilə **qaytaran** `bol(X, y)` funksiyasını yazın.
 Lazım olan idxal funksiyanın içində edilə bilər: `from sklearn.model_selection import train_test_split`.""",
 """def bol(X, y):
     # buranı yazın
     pass""",
 """def bol(X, y):
     from sklearn.model_selection import train_test_split
     return train_test_split(X, y, test_size=0.2, random_state=42)""",
 """X = np.arange(200).reshape(100, 2)
y = np.arange(100)
r = bol(X, y)
return grade(
    (2, "4 nəticə qaytarılmalıdır (X_train, X_test, y_train, y_test)", lambda: len(r) == 4),
    (4, "təlim hissəsi 80, test hissəsi 20 nümunə olmalıdır", lambda: len(r[0]) == 80 and len(r[1]) == 20 and len(r[2]) == 80 and len(r[3]) == 20),
    (4, "X və y sətirləri uyğun qalmalıdır (qarışdırılsa da cütlər saxlanmalıdır)", lambda: all(int(a[0]) // 2 == int(b) for a, b in zip(r[0], r[2]))),
)""")

task(31, 4, "Stratify ilə bölgü",
 """Klassifikasiya məsələsində sinif balansını qorumaq üçün `X` və `y`-ni `stratify=y` parametri ilə `test_size=0.2` nisbətində bölün və `X_train, X_test, y_train, y_test` **qaytaran** `strat_bol(X, y)` funksiyasını yazın.""",
 """def strat_bol(X, y):
     # buranı yazın
     pass""",
 """def strat_bol(X, y):
     from sklearn.model_selection import train_test_split
     return train_test_split(X, y, test_size=0.2, stratify=y, random_state=1)""",
 """def _data(n_pos, seed):
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
)""")

task(32, 4, "StandardScaler ilə standartlaşdırma",
 """`StandardScaler` obyektini yaradın və `X_train`-ə `fit_transform()` tətbiq edin. Funksiya `(scaler, X_scaled)` cütünü **qaytarmalıdır**: `standartlas(X_train)`.
 İdxal: `from sklearn.preprocessing import StandardScaler`.""",
 """def standartlas(X_train):
     # buranı yazın
     pass""",
 """def standartlas(X_train):
     from sklearn.preprocessing import StandardScaler
     scaler = StandardScaler()
     X_scaled = scaler.fit_transform(X_train)
     return scaler, X_scaled""",
 """X = np.array([[1.0, 100.0], [2.0, 200.0], [3.0, 300.0], [4.0, 400.0]])
r = standartlas(X)
return grade(
    (2, "nəticə (scaler, X_scaled) cütü olmalıdır", lambda: len(r) == 2 and hasattr(r[0], "mean_")),
    (4, "hər sütunun ortası 0 olmalıdır", lambda: np.allclose(np.asarray(r[1]).mean(axis=0), 0)),
    (4, "hər sütunun standart sapması 1 olmalıdır", lambda: np.allclose(np.asarray(r[1]).std(axis=0), 1)),
)""")

# ===================== Kateqoriya 5: Scikit-Learn =====================
_REG = '''rs = np.random.RandomState(0)
X_train = rs.rand(40, 2) * 10
y_train = 3 * X_train[:, 0] - 2 * X_train[:, 1] + 5
X_test = rs.rand(10, 2) * 10
'''

task(33, 5, "LinearRegression obyekti",
 """`sklearn.linear_model` modulundan `LinearRegression` modelini idxal edin və yeni (təlim olunmamış) model obyektini **qaytaran** `model_yarat()` funksiyasını yazın.""",
 """def model_yarat():
     # buranı yazın
     pass""",
 """def model_yarat():
     from sklearn.linear_model import LinearRegression
     return LinearRegression()""",
 """from sklearn.linear_model import LinearRegression
m = model_yarat()
assert isinstance(m, LinearRegression), f"LinearRegression obyekti gözlənilirdi, sizinki: {type(m).__name__}"
assert not hasattr(m, "coef_"), "model hələ təlim olunmamalıdır (fit çağırmayın)"
""", partial=False)

task(34, 5, "Modeli öyrətmək (fit)",
 """Xətti reqressiya modelini `(X_train, y_train)` üzərində öyrədib **öyrədilmiş modeli qaytaran** `oyret(X_train, y_train)` funksiyasını yazın (`model.fit(X_train, y_train)`).""",
 """def oyret(X_train, y_train):
     # buranı yazın
     pass""",
 """def oyret(X_train, y_train):
     from sklearn.linear_model import LinearRegression
     model = LinearRegression()
     model.fit(X_train, y_train)
     return model""",
 _REG + """m = oyret(X_train, y_train)
return grade(
    (3, "LinearRegression modeli qaytarılmalıdır", lambda: type(m).__name__ == "LinearRegression"),
    (3, "model öyrədilməlidir (fit çağırılmalıdır)", lambda: hasattr(m, "coef_")),
    (4, "öyrənilən çəkilər düzgün olmalıdır (3 və -2)", lambda: np.allclose(m.coef_, [3, -2], atol=1e-6)),
)""")

task(35, 5, "Test üçün proqnoz",
 """Öyrədilmiş `model` vasitəsilə `X_test` üçün proqnozları (`y_pred`) hesablayıb **qaytaran** `proqnoz_ver(model, X_test)` funksiyasını yazın (`model.predict(X_test)`).""",
 """def proqnoz_ver(model, X_test):
     # buranı yazın
     pass""",
 """def proqnoz_ver(model, X_test):
     return model.predict(X_test)""",
 _REG + """from sklearn.linear_model import LinearRegression
model = LinearRegression().fit(X_train, y_train)
r = proqnoz_ver(model, X_test)
return grade(
    (3, "hər test nümunəsi üçün bir proqnoz olmalıdır (10 ədəd)", lambda: len(r) == 10),
    (7, "proqnoz dəyərləri düzgün deyil", lambda: np.allclose(r, model.predict(X_test))),
)""")

task(36, 5, "Çəkilər və kəsişmə",
 """Öyrədilmiş modelin çəkilərini (`model.coef_`) və kəsişmə nöqtəsini (`model.intercept_`) `(cekiler, kesisme)` cütü kimi **qaytaran** `parametrler(model)` funksiyasını yazın.""",
 """def parametrler(model):
     # buranı yazın
     pass""",
 """def parametrler(model):
     return model.coef_, model.intercept_""",
 _REG + """from sklearn.linear_model import LinearRegression
model = LinearRegression().fit(X_train, y_train)
r = parametrler(model)
return grade(
    (2, "nəticə iki elementli olmalıdır", lambda: len(r) == 2),
    (4, "çəkilər [3, -2] olmalıdır", lambda: np.allclose(r[0], [3, -2], atol=1e-6)),
    (4, "kəsişmə 5 olmalıdır", lambda: abs(float(r[1]) - 5) < 1e-6),
)""")

task(37, 5, "MAE hesablamaq",
 """Həqiqi `y_test` və proqnoz `y_pred` arasında **MAE** (orta mütləq xəta) göstəricisini hesablayıb **qaytaran** `mae_hesabla(y_test, y_pred)` funksiyasını yazın (`mean_absolute_error`).""",
 """def mae_hesabla(y_test, y_pred):
     # buranı yazın
     pass""",
 """def mae_hesabla(y_test, y_pred):
     from sklearn.metrics import mean_absolute_error
     return mean_absolute_error(y_test, y_pred)""",
 """return grade(
    (5, "[3, 5, 2] və [2, 5, 4] üçün MAE = 1.0", lambda: _eq(mae_hesabla([3, 5, 2], [2, 5, 4]), 1.0)),
    (3, "mənfi fərqlər mütləq qiymətlə hesablanmalıdır", lambda: _eq(mae_hesabla([10, 20], [7, 26]), 4.5)),
    (2, "mükəmməl proqnozda MAE = 0", lambda: _eq(mae_hesabla([1, 2, 3], [1, 2, 3]), 0.0)),
)""")

task(38, 5, "MSE hesablamaq",
 """Həqiqi `y_test` və proqnoz `y_pred` arasında **MSE** (orta kvadratik xəta) göstəricisini hesablayıb **qaytaran** `mse_hesabla(y_test, y_pred)` funksiyasını yazın (`mean_squared_error`).""",
 """def mse_hesabla(y_test, y_pred):
     # buranı yazın
     pass""",
 """def mse_hesabla(y_test, y_pred):
     from sklearn.metrics import mean_squared_error
     return mean_squared_error(y_test, y_pred)""",
 """assert _eq(mse_hesabla([3, 5, 2], [2, 5, 4]), 5 / 3), f"[3, 5, 2] və [2, 5, 4] üçün MSE = 5/3 olmalıdır, sizinki: {mse_hesabla([3, 5, 2], [2, 5, 4])!r}"
assert _eq(mse_hesabla([10, 20], [7, 26]), 22.5), "[10, 20] və [7, 26] üçün MSE = 22.5 olmalıdır"
""", partial=False)

task(39, 5, "RMSE hesablamaq",
 """MSE göstəricisindən `np.sqrt()` vasitəsilə **RMSE** dəyərini hesablayıb **qaytaran** `rmse_hesabla(y_test, y_pred)` funksiyasını yazın.""",
 """def rmse_hesabla(y_test, y_pred):
     # buranı yazın
     pass""",
 """def rmse_hesabla(y_test, y_pred):
     from sklearn.metrics import mean_squared_error
     return np.sqrt(mean_squared_error(y_test, y_pred))""",
 """return grade(
    (5, "[0, 0] və [3, 4] üçün RMSE = sqrt(12.5)", lambda: _eq(rmse_hesabla([0, 0], [3, 4]), math.sqrt(12.5))),
    (3, "[2, 4, 6] və [3, 3, 9] üçün RMSE = sqrt(11/3)", lambda: _eq(rmse_hesabla([2, 4, 6], [3, 3, 9]), math.sqrt(11 / 3))),
    (2, "mükəmməl proqnozda RMSE = 0", lambda: _eq(rmse_hesabla([1, 2], [1, 2]), 0.0)),
)""")

task(40, 5, "R² balı",
 """`r2_score` funksiyası ilə modelin **R² balını** hesablayıb **qaytaran** `r2_hesabla(y_test, y_pred)` funksiyasını yazın.""",
 """def r2_hesabla(y_test, y_pred):
     # buranı yazın
     pass""",
 """def r2_hesabla(y_test, y_pred):
     from sklearn.metrics import r2_score
     return r2_score(y_test, y_pred)""",
 """assert _eq(r2_hesabla([1, 2, 3, 4], [1, 2, 3, 4]), 1.0), "mükəmməl proqnozda R² = 1 olmalıdır"
assert _eq(r2_hesabla([1, 2, 3, 4], [2.5, 2.5, 2.5, 2.5]), 0.0), "orta ilə proqnozda R² = 0 olmalıdır"
assert _eq(r2_hesabla([3, -0.5, 2, 7], [2.5, 0.0, 2, 8]), 0.9486081370449679), "R² = 0.9486... olmalıdır"
""", partial=False)
