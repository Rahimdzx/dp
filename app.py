# app.py  — Streamlit-приложение (русская версия)
# -----------------------------------------------
import streamlit as st
import numpy as np
import pandas as pd          # ← новее: для one-hot
import joblib
from pathlib import Path

# ───── Настройки страницы ──────────────────────────────────────────────
st.set_page_config(
    page_title="Прогноз риска сердечных заболеваний",
    page_icon="❤️",
    layout="centered",
)

st.title("🔬 Прогнозирование риска сердечных заболеваний")

st.markdown(
    """
Введите параметры пациента в левой панели и нажмите **«Спрогнозировать»**,
чтобы получить вероятность наличия или развития сердечных заболеваний.
"""
)

# ───── Сайдбар: ввод данных ────────────────────────────────────────────
with st.sidebar:
    st.header("Данные пациента")

    age       = st.slider("Возраст", 18, 100, 45)
    sex       = st.selectbox("Пол", ["Мужчина", "Женщина"])
    cp        = st.selectbox(
        "Тип боли в груди",
        ["Бессимптомная (0)",
         "Атипичная стенокардия (1)",
         "Нестабильная стенокардия (2)",
         "Типичная стенокардия (3)"],
    )
    trestbps  = st.slider("АРТ (мм рт. ст.)", 80, 200, 120,
                          help="Артериальное давление в покое")
    chol      = st.slider("Холестерин (mg/dl)", 100, 600, 200)
    fbs       = st.radio("Глюкоза натощак > 120 mg/dl", ["Нет", "Да"])
    restecg   = st.selectbox(
        "ЭКГ в покое",
        ["Нормальная (0)", "ST-T аномалия (1)", "Гипертрофия ЛЖ (2)"],
    )
    thalach   = st.slider("Максимальная ЧСС", 60, 220, 150)
    exang     = st.radio("Стенокардия при нагрузке", ["Нет", "Да"])
    oldpeak   = st.slider("Сдвиг ST", 0.0, 6.2, 1.0, step=0.1)
    slope     = st.selectbox(
        "Наклон ST сегмента", ["Вверх (0)", "Горизонтально (1)", "Вниз (2)"]
    )
    ca        = st.selectbox("Количество крупных сосудов (0–4)", list(range(5)))
    thal      = st.selectbox(
        "Таллий-тест",
        ["Нормальный (1)", "Фиксированный дефект (2)", "Обратимый дефект (3)"],
    )

    predict_btn = st.button("Спрогнозировать")

# ───── Загрузка модели (кэшируется) ────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_model(path: str = "rs1.pkl"):
    return joblib.load(Path(__file__).parent / path)

# ───── Формирование признаков под 18-колоночную модель ────────────────
def build_features_df(model):
    """Возвращает DataFrame с колонками ровно в том порядке, в каком
    модель обучалась (model.feature_names_in_)."""

    raw = {
        "age": age,
        "sex": 1 if sex == "Мужчина" else 0,
        "trestbps": trestbps,
        "chol": chol,
        "fbs": 1 if fbs == "Да" else 0,
        "thalach": thalach,
        "exang": 1 if exang == "Да" else 0,
        "oldpeak": oldpeak,
        "ca": ca,
        "cp": ["Бессимптомная (0)",
               "Атипичная стенокардия (1)",
               "Нестабильная стенокардия (2)",
               "Типичная стенокардия (3)"].index(cp),
        "restecg": ["Нормальная (0)",
                    "ST-T аномалия (1)",
                    "Гипертрофия ЛЖ (2)"].index(restecg),
        "slope": ["Вверх (0)", "Горизонтально (1)", "Вниз (2)"].index(slope),
        "thal": ["Нормальный (1)",
                 "Фиксированный дефект (2)",
                 "Обратимый дефект (3)"].index(thal) + 1,   # 1–3
    }

    df = pd.DataFrame([raw])

    # One-hot для трёх категориальных признаков — как в ноутбуке
    cat_cols = ["cp", "restecg", "slope"]
    df = pd.get_dummies(df, columns=cat_cols, prefix=cat_cols)

    # Добавляем недостающие dummy-колонки (fill_value=0) и упорядочиваем
    feature_cols = model.feature_names_in_
    df = df.reindex(columns=feature_cols, fill_value=0)

    return df

# ───── Прогноз по нажатию кнопки ───────────────────────────────────────
if predict_btn:
    model = load_model()
    X = build_features_df(model).values      # shape (1, 18)
    prob = model.predict_proba(X)[0, 1] * 100

    st.subheader(f"🩺 Вероятность заболевания: **{prob:.1f}%**")
    st.progress(prob / 100)

    if prob >= 50:
        st.error("Повышенный риск — рекомендуем консультацию кардиолога.")
    else:
        st.success("Низкий риск по текущим данным.")
