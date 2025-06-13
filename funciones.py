import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

def load_data(filepath):
    try:
        df = pd.read_csv(filepath)
        return df
    except Exception as e:
        return str(e)

def preprocess_data(df):
    if 'ORDERDATE' in df.columns:
        df['ORDERDATE'] = pd.to_datetime(df['ORDERDATE'], errors='coerce')
        df = df.dropna(subset=['ORDERDATE'])
        df = df.sort_values('ORDERDATE')
    return df

def get_sales_summary(df):
    return {
        "total_sales": float(df['SALES'].sum()),
        "average_sales": float(df['SALES'].mean()),
        "max_sales": float(df['SALES'].max()),
        "min_sales": float(df['SALES'].min()),
        "total_orders": int(df.shape[0])
    }

def group_sales_by_date(df):
    return df.groupby('ORDERDATE', as_index=False)['SALES'].sum()

def get_correlation_matrix(df):
    return df.select_dtypes(include=['number']).corr()

def get_sales_distribution(df, column='SALES'):
    if column not in df.columns:
        return None
    return {
        "mean": float(df[column].mean()),
        "std": float(df[column].std()),
        "min": float(df[column].min()),
        "max": float(df[column].max()),
        "25%": float(df[column].quantile(0.25)),
        "50%": float(df[column].median()),
        "75%": float(df[column].quantile(0.75))
    }

def perform_pca_analysis(df, n_components=3, apply_clustering=True, n_clusters=3):
    df_num = df.select_dtypes(include=['number']).dropna()
    
    if df_num.shape[0] == 0 or df_num.shape[1] < n_components:
        return {"error": "No hay suficientes datos numéricos para realizar PCA"}

    scaler = StandardScaler()
    df_scaled = scaler.fit_transform(df_num)

    pca = PCA(n_components=n_components)
    pca_result = pca.fit_transform(df_scaled)

    pca_df = pd.DataFrame(pca_result, columns=[f'PC{i+1}' for i in range(n_components)])

    result = {
        "explained_variance_ratio": pca.explained_variance_ratio_.tolist(),
        "components": pca_df.to_dict(orient='records')
    }

    if apply_clustering:
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(pca_df)
        pca_df['cluster'] = clusters
        result["components"] = pca_df.to_dict(orient='records')

    return result
