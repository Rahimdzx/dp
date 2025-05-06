
# Streamlit‑приложение для прогноза сердечных заболеваний (RU)

## Запуск локально

```bash
pip install streamlit scikit-learn joblib numpy
streamlit run app.py
```

Убедитесь, что **rs2.pkl** (сохранённая модель SVM‑Pipeline)
находится в той же папке, что и `app.py`.

## Как обучить и сохранить модель

В Jupyter‑ноутбуке:

```python
best_model = best_svm          # или любая ваша лучшая модель‑пайплайн
import joblib
joblib.dump(best_model, "heart_disease_model.pkl")
```

После этого перезапустите `streamlit run app.py`.
