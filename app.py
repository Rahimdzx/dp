
# ---------------------------------------------------------------
import streamlit as st
from pathlib import Path
import numpy as np
import pandas as pd
import joblib

# ---------- Общие настройки страницы ---------------------------
st.set_page_config(
    page_title="Прогноз риска сердечных заболеваний",
    page_icon="❤️",
    layout="centered",
)

# ---------- Заголовок/описание ---------------------------------
st.title("❤️‍🩹 Прогноз риска сердечно-сосудистых заболеваний")

st.markdown(
    """
В левой панели укажите данные пациента и нажмите **«Спрогнозировать»**.
Алгоритм вернёт вероятность наличия/развития сердечных заболеваний.
""",
    unsafe_allow_html=True,
)

# ---------- Сайдбар: ввод признаков ----------------------------
with st.sidebar:
    st.header("🔎 Данные пациента")

    age       = st.slider("Возраст (лет)", 18, 100, 45)
    sex       = st.selectbox("Пол", ["Мужчина", "Женщина"])
    cp        = st.selectbox(
        "Тип боли в груди",
        [
            "Бессимптомная (0)",
            "Атипичная стенокардия (1)",
            "Нестабильная стенокардия (2)",
            "Типичная стенокардия (3)",
        ],
    )
    trestbps  = st.slider("АД в покое (мм рт. ст.)", 80, 200, 120)
    chol      = st.slider("Холестерин (mg/dl)", 100, 600, 200)
    fbs       = st.radio("Глюкоза натощак > 120 mg/dl", ["Нет", "Да"])
    restecg   = st.selectbox(
        "ЭКГ-покоя",
        ["Нормальная (0)", "ST-T аномалия (1)", "Гипертрофия ЛЖ (2)"],
    )
    thalach   = st.slider("Макс. ЧСС", 60, 220, 150)
    exang     = st.radio("Стенокардия при нагрузке", ["Нет", "Да"])
    oldpeak   = st.slider("Сдвиг ST (мм)", 0.0, 6.2, 1.0, step=0.1)
    slope     = st.selectbox(
        "Наклон ST-сегмента", ["Вверх (0)", "Горизонтально (1)", "Вниз (2)"]
    )
    ca        = st.selectbox("Крупные сосуды (0-4)", list(range(5)))
    thal      = st.selectbox(
        "Таллий-тест",
        ["Нормальный (1)", "Фиксированный дефект (2)", "Обратимый дефект (3)"],
    )

    predict_btn = st.button("💡 Спрогнозировать", use_container_width=True)

# ---------- Кэш-загрузка модели --------------------------------
@st.cache_resource(show_spinner=False)
def load_model(model_path: str = "rs2.pkl"):
    return joblib.load(Path(__file__).parent / model_path)

# ---------- Формирование признаков -----------------------------
def build_features_df(model):
    """Формируем DataFrame c точно теми колонками, которые модель «ждёт»."""
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
                 "Обратимый дефект (3)"].index(thal) + 1,
    }

    df = pd.DataFrame([raw])

    # One-hot для категориальных
    cat_cols = ["cp", "restecg", "slope"]
    df = pd.get_dummies(df, columns=cat_cols, prefix=cat_cols)

    # Выравниваем под ожидаемый порядок
    feat_cols = model.feature_names_in_
    df = df.reindex(columns=feat_cols, fill_value=0)

    return df

# ---------- Прогноз --------------------------------------------
if predict_btn:
    model = load_model()
    X_df  = build_features_df(model)
    proba_vec = model.predict_proba(X_df.values)[0]

    # «Болезнь» считается меткой 1, если таковая есть в classes_,
    # иначе 0 (на случай инверсии меток)
    disease_label = 1 if 1 in model.classes_ else 0
    disease_idx   = list(model.classes_).index(disease_label)
    prob = proba_vec[disease_idx] * 100  # %

    st.markdown("---")
    st.subheader(f"🩺 Вероятность заболевания: **{prob:.3f}%**")
    st.progress(min(prob, 100) / 100)

    if prob >= 50:
        st.error(
            "‼️ Повышенный риск — настоятельно рекомендуем консультацию кардиолога.",
            icon="⚠️",
        )
    elif prob >= 20:
        st.warning(
            "Возможен риск. Рекомендуется дополнительное обследование.",
            icon="🔍",
        )
    else:
        st.success("Низкий риск по текущим данным.", icon="✅")

# ---------- Футер ----------------------------------------------
st.markdown(
    """
    <div style='text-align:center; margin-top:2em; font-size:0.85em; color:gray;'>
      Сделано с любовью ❤️Mouissat Rabah  · Модель&nbsp;SVM&nbsp;+&nbsp;StandardScaler
    </div>
    """,
    unsafe_allow_html=True,
)
