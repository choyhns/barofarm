import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import joblib
import cx_Oracle
from sqlalchemy import create_engine

# 1. 오라클에서 데이터 가져오기
engine = create_engine("oracle+cx_oracle://barofarm:a123@loaclhost:1521/xe")
df = pd.read_sql("SELECT * FROM DAILY_PRICE", engine)

print(df.columns)
df.rename(columns={
    'CATEGORY_CODE': 'categoryCode',
    'ITEM_CODE': 'itemCode',
    'KIND_CODE': 'kindCode',
    'PRODUCT_CLS_CODE': 'productClsCode',
    'RANK_CODE': 'rankCode',
    'REGION_NAME': 'regionName'
}, inplace=True)

# 2. 범주형 변수 숫자 변환
label_cols = ['categoryCode', 'itemCode', 'kindCode', 'productClsCode', 'rankCode', 'regionName']
for col in label_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])

# 3. 특징(X)과 목표(Y) 정의
X_cols = ['dpr1','dpr2','dpr3','dpr4','dpr5','dpr6','dpr7','categoryCode','itemCode','kindCode','productClsCode','rankCode','regionName']
X = df[X_cols]
y = df['dpr1'].shift(-1)  # 다음날 가격 예측
X = X[:-1]
y = y[:-1]

# 4. 학습/테스트 분리
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 5. 모델 학습
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 6. 모델 저장
joblib.dump(model, 'price_model.pkl')
