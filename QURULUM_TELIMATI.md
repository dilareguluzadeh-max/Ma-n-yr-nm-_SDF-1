# 🚀 SDF 1: Onlayn İmtahan Portalı (BMU — Maşın Öyrənmənin Əsasları)

Brauzerdə işləyən, köçürməyə qarşı qorunan imtahan sistemi. Tələbənin Python kodu brauzerdə **real Python** (Pyodide: NumPy, Pandas, scikit-learn) ilə bank testləri vasitəsilə yoxlanılır.

**İmtahan strukturu (hər variantda):** 10 tapşırıq = **4 nəzəri** (Hissə 1) + **6 praktiki** (Hissə 2, 5 kateqoriyanın hər birindən ən azı 1), hər biri 10 bal, cəmi 100 bal. Tapşırıqların sırası hər variantda qarışdırılıb, heç bir sual iki variantda təkrarlanmır. Bəzi kod tapşırıqları yalnız **0 və ya 10 bal**, digərləri isə **hissə-hissə (0–10 bal arası)** qiymətləndirilir. Bölgü cədvəli: `sual_banki_xeritesi.md`.

---

## 📁 Fayllar

| Fayl | Təyinatı |
|---|---|
| `index.html` | **Tələbə portalı** — giriş yalnız ad-soyad və sıra nömrəsi ilə; tam ekran, 3 xəbərdarlıq, Copy/Paste/DevTools bloku, «Kodu yoxla» düyməsi |
| `admin.html` | **Müəllim paneli** — müəllim şifrəsi ilə, canlı nəticələr, pozuntu jurnalı, Excel ixracı |
| `exam_data.js` | 5 variantın sualları, başlanğıc kodları və testləri (**avtomatik yaradılır**) |
| `sual_banki_xeritesi.md` | Hansı variantda hansı sualın olduğu, qiymətləndirmə növü (**avtomatik yaradılır**) |
| `variant_A.py` … `variant_E.py` | `python variant_X.py` ilə işləyən müstəqil imtahan faylları (**avtomatik yaradılır**) |
| `telebeler_20.py` | 20 tələbənin 5 varianta bərabər bölgüsü (hər varianta 4 nəfər) |
| `yeniden_qiymetlendir.py` | Bazadakı cavabların müəllim kompüterində müstəqil yenidən yoxlanması |
| `grader_core.py` | Yoxlama mühərriki (brauzer və `yeniden_qiymetlendir.py` eyni kodu işlədir) |
| `tools/build_bank.py` | Sual bankından `exam_data.js`, `variant_*.py` və xəritəni yaradan generator |
| `tools/bank_theory.py` | Hissə 1: 20 nəzəri mövzu (hər biri 1 düzgün + 3 səhv cavab) |
| `tools/bank_coding.py` | Hissə 2: 40 kod tapşırığı, etalon həllər və testlər (tam/qismən bal) |
| `tools/probes.py` | Qismən bal mexanizmini yoxlayan natamam həllər |
| `supabase_setup.sql` | Supabase cədvəli, RLS qaydaları və şifrəli oxuma funksiyası |

---

## ⚡ Quraşdırma

### 1. Supabase (bir dəfə, və ya bu versiyaya yenilədikdə mütləq)
Supabase Dashboard → **SQL Editor** → `supabase_setup.sql`-in məzmununu yapışdırın → **Run**.

Bu skript:
- tələbələrə yalnız nəticə **göndərmək** icazəsi verir (oxumaq yox);
- nəticələri yalnız müəllim şifrəsi ilə (serverdə yoxlanılan) `admin_list_submissions` funksiyası vasitəsilə oxumağa imkan verir.

> ⚠️ Skript işlədilməyibsə, müəllim paneli sarı xəbərdarlıq göstərəcək: köhnə qayda ilə anon açarı olan hər kəs nəticələri oxuya bilir.

### 2. Variant bölgüsü
```bash
python telebeler_20.py                 # şablon siyahı
python telebeler_20.py siyahi.txt      # hər sətirdə bir ad (20 sətir)
```
Hər tələbəyə **sıra nömrəsini (1–20)** bildirin. Tələbə girişdə yalnız ad-soyad və sıra nömrəsini yazır; qrup (1203A) `index.html`-də `GROUP_NAME` sabitindədir. Variant girişdə göstərilmir, yalnız imtahan başlayanda görünür. Portal variantı `(sıra − 1) % 5` qaydası ilə təyin edir:
`1,6,11,16 → A · 2,7,12,17 → B · 3,8,13,18 → C · 4,9,14,19 → D · 5,10,15,20 → E`.

### 3. Tələbələrə link
- **GitHub Pages / Vercel**: qovluğu yükləyin, linki paylaşın.
- **Laboratoriya şəbəkəsi**: müəllim kompüterində `python -m http.server 8000`, tələbələr `http://192.168.X.X:8000` açır.

İnternet tələb olunur: Python mühiti (Pyodide, ~25 MB) və Supabase CDN-dən yüklənir. Python yüklənməsə, nəzəri (test) suallar yenə də yoxlanır, kod tapşırıqları isə "qismən" kimi işarələnir — onları `yeniden_qiymetlendir.py` ilə yoxlayın.

---

## 🛡️ Anti-Cheat
1. Məcburi **tam ekran**; çıxdıqda xəbərdarlıq və tam ekrana qaytarma.
2. **3 xəbərdarlıq**: başqa taba/pəncərəyə keçmək (Alt+Tab daxil — brauzer Alt+Tab-ı bloklaya bilməz, amma dərhal aşkarlayır), brauzeri kiçiltmək, tam ekrandan çıxmaq, səhifəni yeniləmək → səsli siqnal + xəbərdarlıq. 3-cü dəfə imtahan kəsilir, bal **0**, status `KƏNARLAŞDIRILDI_3_HAQQ`.
3. Sağ klik, Copy/Cut/Paste, sürüklə-burax, `F12`, `Ctrl+Shift+I/J/C`, `Ctrl+U` bloklanır (bunlar haqq aparmır, amma jurnala yazılır).
4. Səhifə yenilənsə belə vaxt, haqlar və cavablar itmir (brauzer yaddaşında saxlanılır).
5. Eyni kompüterdə növbəti tələbə üçün: nəticə ekranında **"Müəllim: bu kompüteri sıfırla"** (müəllim şifrəsi ilə).

---

## 🔁 Nəticələrin yoxlanması
Bal tələbənin brauzerində hesablanır. Şübhəli və ya "qismən" nəticələr üçün:
```bash
python yeniden_qiymetlendir.py --password MÜƏLLİM_ŞİFRƏSİ --csv yeni_ballar.csv
```

## 🛠️ Sualları dəyişmək
Nəzəri sualları `tools/bank_theory.py`, kod tapşırıqlarını `tools/bank_coding.py` faylında redaktə edin, sonra:
```bash
python tools/build_bank.py --verify
```
Bu `exam_data.js`, `variant_A.py … variant_E.py` və `sual_banki_xeritesi.md`-ni yenidən yaradır, hər variantın etalon həllə 100/100, boş cavabla 0 verdiyini, `.py` fayllarının sintaksisini və qismən bal mexanizmini yoxlayır.

**Qismən bal necə işləyir?** Tapşırığın testi `return grade((çəki, "hissə", lambda: şərt), ...)` ilə bitirsə, hər ödənən hissənin çəkisi toplanır (çəkilərin cəmi 10-dur). Adi `assert` ilə yazılmış tapşırıqlar isə yalnız 0 və ya 10 bal verir. Bal tam ədədə yuvarlaqlaşdırılır (bazadakı `score INTEGER` sütunu ilə uyğundur).
