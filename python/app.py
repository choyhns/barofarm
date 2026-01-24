from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from sqlalchemy import create_engine
import joblib
import logging
import numpy as np

# ------------------------
# 로깅 설정
# ------------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ------------------------
# Flask 설정
# ------------------------
app = Flask(__name__)
CORS(app)  # 모든 도메인 허용 (임시, 테스트용)

# ------------------------
# DB 연결
# ------------------------
try:
    engine = create_engine("oracle+cx_oracle://barofarm:a123@localhost:1521/xe")
    logging.info("DB 연결 성공")
except Exception as e:
    logging.error(f"DB 연결 실패: {e}")
    raise

# ------------------------
# 모델/라벨 인코더 불러오기
# ------------------------
model_names = ["RandomForest","LinearRegression","XGBoost","LightGBM"]
models = {name: joblib.load(f"models/{name}_daily_price_model.pkl") for name in model_names}

label_cols = ['categoryCode','itemName','kindName','productClsCode','rank','regionName']
label_encoders = {col: joblib.load(f"models/{col}_labelencoder.pkl") for col in label_cols}

n_days = 5  # lag feature 개수
lag_cols = [f'dpr1_lag_{i}' for i in range(1, n_days+1)]

# ------------------------
# 예측 API
# ------------------------
@app.post("/predict")
def predict():
    try:
        data = request.get_json()
        model_name = data.get("model", "RandomForest")

        if model_name not in models:
            return jsonify({"error": "지원하지 않는 모델입니다."}), 400
        model = models[model_name]

        # 라벨 인코딩
        encoded_input = {}
        for col in label_cols:
            val = data.get(col)
            if val is None:
                return jsonify({"error": f"{col} 값이 없습니다."}), 400
            le = label_encoders[col]
            # le.classes_는 numpy array; 비교를 문자열로 통일해야 할 경우도 있으므로 안전하게 처리
            if val not in le.classes_:
                return jsonify({"error": f"{col} 값 '{val}' 은(는) 학습되지 않은 값입니다."}), 400
            encoded_input[col] = int(le.transform([val])[0])

        # ------------------------
        # DB에서 최근 n일 가격 가져오기 (Oracle 호환)
        # ------------------------
        query = """
        SELECT * FROM (
            SELECT dpr1
            FROM DAILY_PRICE
            WHERE category_code = :category_code
              AND item_name = :item_name
              AND kind_name = :kind_name
              AND region_name = :region_name
              AND product_cls_code = :product_cls_code
            ORDER BY regday DESC
        ) WHERE ROWNUM <= :n_days
        """

        df_recent = pd.read_sql(query, engine, params={
            "category_code": data['categoryCode'],
            "item_name": data['itemName'],
            "kind_name": data['kindName'],
            "region_name": data['regionName'],
            "product_cls_code": data['productClsCode'],
            "n_days": n_days
        })

        if df_recent.empty:
            return jsonify({"error": "DB에 최근 가격 데이터가 존재하지 않습니다."}), 400

        # 안전한 복사 및 숫자 변환
        df_recent = df_recent.copy()
        df_recent['dpr1'] = pd.to_numeric(df_recent['dpr1'], errors='coerce')

        # 직전 값으로 채우기 (ffill 사용), 첫 값은 평균으로
        mean_price = df_recent['dpr1'].mean(skipna=True)
        # ffill을 사용한 후에도 NaN이 있을 수 있어서 fillna(mean)
        df_recent['dpr1'] = df_recent['dpr1'].ffill().fillna(mean_price if not np.isnan(mean_price) else 0)

        past_prices = df_recent['dpr1'].values  # 내림차순(가장 최신이 인덱스 0)

        # ------------------------
        # lag feature 생성
        # ------------------------
        # 학습시 사용했던 lag naming과 동일하게 생성 (dpr1_lag_1 ... dpr1_lag_n)
        for i in range(1, n_days+1):
            if i <= len(past_prices):
                # 과거 n일 데이터가 내림차순이므로 가장 최신을 lag_1로 사용
                encoded_input[f'dpr1_lag_{i}'] = float(past_prices[i-1])
            else:
                encoded_input[f'dpr1_lag_{i}'] = float(past_prices.mean()) if len(past_prices) > 0 else 0.0

        # ------------------------
        # 예측: 모델이 기대하는 컬럼 순서/이름으로 재정렬 (안정성 확보)
        # ------------------------
        X_input = pd.DataFrame([encoded_input])

        # 모델이 feature names 정보를 가지고 있으면 그것을 우선 사용
        if hasattr(model, "feature_names_in_"):
            expected_cols = list(model.feature_names_in_)
        else:
            # fallback: label_cols + lag_cols (학습 스크립트의 순서)
            expected_cols = label_cols + lag_cols

        # reindex로 부족한 컬럼은 0으로 채우고, 순서도 맞춤
        X_input = X_input.reindex(columns=expected_cols, fill_value=0)

        # 타입 안정화: float로 변경 (모델에 따라선 int도 괜찮지만 안전을 위해 float)
        X_input = X_input.astype(float)

        # 예측 수행
        pred = model.predict(X_input)[0]

        return jsonify({
            "predicted_price": float(pred),
            "past_prices": past_prices.tolist(),
            "model": model_name
        })

    except Exception as e:
        logging.exception("예측 중 에러:")
        return jsonify({"error": str(e)}), 500

# ------------------------
# Flask 실행
# ------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
