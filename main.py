import os

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import KNNImputer
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

esg_scores = pd.read_csv('data/SP500ESGRiskRatings.csv')
fin_data = pd.read_csv('data/financial data sp500 companies.csv')

df = pd.merge(esg_scores, fin_data.rename(columns={'Ticker': 'Symbol'}), on='Symbol', how='inner')
df.dropna(subset=['Environment Risk Score', 'Social Risk Score', 'Governance Risk Score'], inplace=True)
df = df[~df.duplicated(
    subset=['Symbol', 'Environment Risk Score', 'Governance Risk Score', 'Social Risk Score'],
    keep='first')]
data = df.drop(columns=['Total ESG Risk score', 'Controversy Score', 'Controversy Level', 'Description',
                        'Research Development', 'Research Development', 'date', 'Description', 'Name', 'Symbol',
                        'Address', 'Industry', 'ESG Risk Level', 'ESG Risk Percentile', 'Unnamed: 0', 'firm',
                        'Full Time Employees'])

# data['Full Time Employees'] = data['Full Time Employees'].str.replace(',', '').astype(float)
X = data.drop(columns=['Environment Risk Score', 'Governance Risk Score', 'Social Risk Score'])
# Create a mapping dictionary
sector_mapping = {
    'Consumer Cyclical': 'Consumer',
    'Consumer Defensive': 'Consumer'
}

# Replace values based on the mapping
X['Sector'] = X['Sector'].replace(sector_mapping)

# found its sector by manual searching
X['Sector'].fillna('Industrials', inplace=True)

le_sector = LabelEncoder()
le_sector.fit(['Healthcare', 'Industrials', 'Consumer', 'Technology', 'Utilities', 'Financial Services',
               'Basic Materials', 'Real Estate', 'Energy', 'Communication Services'])
X['Sector'] = le_sector.transform(X['Sector'].dropna())
print(X)
data['Environment Risk Score'] = np.log1p(data['Environment Risk Score'])
data['Social Risk Score'] = np.log1p(data['Social Risk Score'])
data['Governance Risk Score'] = np.log1p(data['Governance Risk Score'])
y1 = data['Environment Risk Score']
y2 = data['Social Risk Score']
y3 = data['Governance Risk Score']
imputer = KNNImputer()
X_imputed = pd.DataFrame(imputer.fit_transform(X), columns=X.columns)
X_train1, X_test1, y_train1, y_test1 = train_test_split(X_imputed, y1, test_size=0.2, random_state=42)

rf_model1 = RandomForestRegressor(n_estimators=100, random_state=42)
rf_model1.fit(X_train1, y_train1)

y_pred1 = rf_model1.predict(X_test1)

mse1 = mean_squared_error(y_test1, y_pred1)
r2_score1 = r2_score(y_test1, y_pred1)

print(f'Metrics for Environment Risk Score\nMSE: {mse1}\nRMSE: {np.sqrt(mse1)}\nR-squared Score: {r2_score1}')

X_train2, X_test2, y_train2, y_test2 = train_test_split(X_imputed, y2, test_size=0.2, random_state=42)

rf_model2 = RandomForestRegressor(n_estimators=100, random_state=42)
rf_model2.fit(X_train2, y_train2)

y_pred2 = rf_model2.predict(X_test2)

mse2 = mean_squared_error(y_test2, y_pred2)
r2_score2 = r2_score(y_test2, y_pred2)

# print(f'Metrics for Social Risk Score\nMSE: {mse2}\nRMSE: {np.sqrt(mse2)}\nR-squared Score: {r2_score2}')

X_train3, X_test3, y_train3, y_test3 = train_test_split(X_imputed, y3, test_size=0.2, random_state=42)
rf_model3 = RandomForestRegressor(n_estimators=100, random_state=42)
rf_model3.fit(X_train3, y_train3)

y_pred3 = rf_model3.predict(X_test3)

mse3 = mean_squared_error(y_test3, y_pred3)
r2_score3 = r2_score(y_test3, y_pred3)

print(f'Metrics for Governance Risk Score\nMSE: {mse3}\nRMSE: {np.sqrt(mse3)}\nR-squared Score: {r2_score3}')

# Directory paths
sk_models_folder = 'models/model_v2/sk_models/'
ct_models_folder = 'models/model_v2/ct_models/'

# Check if the folders exist, and create them if not
if not os.path.exists(sk_models_folder):
    os.makedirs(sk_models_folder)


# Assume rf_model1, rf_model2, and rf_model3 are your scikit-learn models
joblib.dump(rf_model1, os.path.join(sk_models_folder, 'env_model.pkl'))
joblib.dump(rf_model2, os.path.join(sk_models_folder, 'soc_model.pkl'))
joblib.dump(rf_model3, os.path.join(sk_models_folder, 'gov_model.pkl'))

print(X_train1.shape)

