
import streamlit as st
import numpy as np
import joblib

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
    """)

# ---- Сайдбар для ввода данных ----------------------------------------
with st.sidebar:
    st.header("Данные пациента")

    age     = st.slider("Возраст", 18, 100, 45)
    sex     = st.selectbox("Пол", ["Мужчина", "Женщина"])
    cp      = st.selectbox("Тип боли в груди",
                           ["Бессимптомная (0)",
                            "Атипичная стенокардия (1)",
                            "Нестабильная стенокардия (2)",
                            "Типичная стенокардия (3)"])
    trestbps = st.slider("АРТ (мм рт. ст.)", 80, 200, 120,
                         help="Артериальное давление в покое")
    chol     = st.slider("Холестерин (mg/dl)", 100, 600, 200)
    fbs      = st.radio("Глюкоза натощак > 120 mg/dl", ["Нет", "Да"])
    restecg  = st.selectbox("ЭКГ в покое",
                            ["Нормальная (0)",
                             "ST‑T аномалия (1)",
                             "Гипертрофия ЛЖ (2)"])
    thalach  = st.slider("Максимальная ЧСС", 60, 220, 150)
    exang    = st.radio("Стенокардия при нагрузке", ["Нет", "Да"])
    oldpeak  = st.slider("Сдвиг ST", 0.0, 6.2, 1.0, step=0.1)
    slope    = st.selectbox("Наклон ST сегмента",
                            ["Вверх (0)", "Горизонтально (1)", "Вниз (2)"])
    ca       = st.selectbox("Количество крупных сосудов (0–4)", list(range(5)))
    thal     = st.selectbox("Таллий‑тест",
                            ["Нормальный (1)",
                             "Фиксированный дефект (2)",
                             "Обратимый дефект (3)"])

    predict_btn = st.button("Спрогнозировать")

# ---- Функция формирования признаков -----------------------------------
def build_features():
    gender      = 1 if sex == "Мужчина" else 0
    fbs_val     = 1 if fbs == "Да" else 0
    exang_val   = 1 if exang == "Да" else 0
    cp_val      = ["Бессимптомная (0)",
                   "Атипичная стенокардия (1)",
                   "Нестабильная стенокардия (2)",
                   "Типичная стенокардия (3)"].index(cp)
    restecg_val = ["Нормальная (0)",
                   "ST‑T аномалия (1)",
                   "Гипертрофия ЛЖ (2)"].index(restecg)
    slope_val   = ["Вверх (0)", "Горизонтально (1)", "Вниз (2)"].index(slope)
    thal_val    = ["Нормальный (1)",
                   "Фиксированный дефект (2)",
                   "Обратимый дефект (3)"].index(thal) + 1  # → 1–3

    return np.array([[age, gender, cp_val, trestbps, chol,
                      fbs_val, restecg_val, thalach, exang_val,
                      oldpeak, slope_val, ca, thal_val]])

# ---- Подгружаем модель один раз --------------------------------------
@st.cache_resource(show_spinner=False)
def load_model(path: str = "rs.pkl"):
    return joblib.load(path)

if predict_btn:
    X = build_features()
    model = load_model()
    prob = model.predict_proba(X)[0, 1] * 100

    st.subheader(f"🩺 Вероятность заболевания: **{prob:.1f}%**")
    st.progress(prob / 100)

    if prob >= 50:
        st.error("Повышенный риск — рекомендуем консультацию кардиолога.")
    else:
        st.success("Низкий риск по текущим данным.")
