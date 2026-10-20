# -*- coding: utf-8 -*-
"""Qismən bal sınağı: bilərəkdən natamam həllər və onların gözlənilən balı (build_bank.py --verify istifadə edir)."""

PROBES = {
    2: ("def matris_xasseleri(m):\n    return m.shape, m.ndim", 5),
    5: ("def boyuk_elementler(arr):\n    return arr[arr >= 50]", 4),
    12: ("def statistika(df):\n    return df.describe(include='all')", 2),
    16: ("def csv_yaz(df, fayl):\n    df.to_csv(fayl)", 6),
    25: ("def median_ile_doldur(df, sutun):\n    return df[sutun].fillna(df[sutun].mean())", 6),
    29: ("def kenar_kes(seriya, low, high):\n    return seriya.clip(upper=high)", 6),
    34: ("def oyret(X_train, y_train):\n    from sklearn.linear_model import LinearRegression\n    return LinearRegression()", 3),
    37: ("def mae_hesabla(y_test, y_pred):\n    from sklearn.metrics import mean_squared_error\n    return mean_squared_error(y_test, y_pred)", 2),
    32: ("def standartlas(X_train):\n    from sklearn.preprocessing import MinMaxScaler\n    s = MinMaxScaler()\n    return s, s.fit_transform(X_train)", 0),
}
