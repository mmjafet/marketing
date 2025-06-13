from flask import Flask, request, jsonify, send_file, Response
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns
import io
import os

app = Flask(__name__)

DATA_FILE = 'data/sales_data_sample.csv'
df_global = None

# --- Funciones de procesamiento ---

def load_data(filepath):
    try:
        # Try different encodings
        for encoding in ['latin1', 'iso-8859-1', 'cp1252']:
            try:
                df = pd.read_csv(filepath, encoding=encoding)
                print(f"Successfully loaded file with encoding: {encoding}")
                return df
            except UnicodeDecodeError:
                continue
        
        # If all encodings fail, try with error handling
        df = pd.read_csv(filepath, encoding='utf-8', encoding_errors='replace')
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
    grouped = df.groupby('ORDERDATE', as_index=False)['SALES'].sum()
    grouped['ORDERDATE'] = grouped['ORDERDATE'].dt.strftime('%Y-%m-%d')
    return grouped

def get_correlation_matrix(df):
    corr = df.select_dtypes(include=['number']).corr()
    return corr

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

    return pca_df, result

# --- Funciones para generar imágenes en memoria ---

def plot_grouped_sales(df):
    grouped = group_sales_by_date(df)
    plt.figure(figsize=(10,5))
    plt.plot(grouped['ORDERDATE'], grouped['SALES'], marker='o')
    plt.xticks(rotation=45)
    plt.title('Ventas agrupadas por fecha')
    plt.xlabel('Fecha')
    plt.ylabel('Ventas')
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return buf

def plot_correlation_heatmap(df):
    corr = get_correlation_matrix(df)
    plt.figure(figsize=(8,6))
    sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f")
    plt.title('Matriz de correlación')
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return buf

def plot_sales_distribution(df, column='SALES'):
    if column not in df.columns:
        return None
    plt.figure(figsize=(8,5))
    sns.histplot(df[column].dropna(), bins=30, kde=True)
    plt.title(f'Distribución de {column}')
    plt.xlabel(column)
    plt.ylabel('Frecuencia')
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return buf

def plot_pca_clusters(df, n_components=3, n_clusters=3):
    pca_df, _ = perform_pca_analysis(df, n_components=n_components, apply_clustering=True, n_clusters=n_clusters)
    plt.figure(figsize=(8,6))

    if n_components >= 3:
        ax = plt.axes(projection='3d')
        scatter = ax.scatter(pca_df['PC1'], pca_df['PC2'], pca_df['PC3'], c=pca_df['cluster'], cmap='viridis', s=50)
        ax.set_xlabel('PC1')
        ax.set_ylabel('PC2')
        ax.set_zlabel('PC3')
        plt.title('PCA con clustering (3 componentes)')
        plt.colorbar(scatter)
    else:
        sns.scatterplot(data=pca_df, x='PC1', y='PC2', hue='cluster', palette='viridis')
        plt.title('PCA con clustering')

    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return buf

# --- Rutas API ---

def check_data_loaded():
    global df_global
    if df_global is None:
        return False, jsonify({"error": "No hay datos cargados."}), 400
    return True, None, None

@app.route('/')
def home():
    return jsonify({"message": "API activa. Usa los endpoints GET para consultar datos o imágenes."})

@app.route('/summary')
def summary():
    ok, resp, code = check_data_loaded()
    if not ok:
        return resp, code
    return jsonify(get_sales_summary(df_global))

@app.route('/grouped')
def grouped():
    ok, resp, code = check_data_loaded()
    if not ok:
        return resp, code
    return jsonify(group_sales_by_date(df_global).to_dict(orient='records'))

@app.route('/correlation')
def correlation():
    ok, resp, code = check_data_loaded()
    if not ok:
        return resp, code
    return jsonify(get_correlation_matrix(df_global))

@app.route('/distribution')
def distribution():
    ok, resp, code = check_data_loaded()
    if not ok:
        return resp, code
    dist = get_sales_distribution(df_global)
    if dist is None:
        return jsonify({"error": "Columna SALES no encontrada"}), 400
    return jsonify(dist)

@app.route('/pca')
def pca():
    ok, resp, code = check_data_loaded()
    if not ok:
        return resp, code
    _, result = perform_pca_analysis(df_global)
    if 'error' in result:
        return jsonify(result), 400
    return jsonify(result)

# Endpoints que regresan imágenes PNG:

@app.route('/plot/grouped')
def plot_grouped():
    ok, resp, code = check_data_loaded()
    if not ok:
        return resp, code
    img = plot_grouped_sales(df_global)
    return Response(img.getvalue(), mimetype='image/png')

@app.route('/plot/correlation')
def plot_corr():
    ok, resp, code = check_data_loaded()
    if not ok:
        return resp, code
    img = plot_correlation_heatmap(df_global)
    return Response(img.getvalue(), mimetype='image/png')

@app.route('/plot/distribution')
def plot_dist():
    ok, resp, code = check_data_loaded()
    if not ok:
        return resp, code
    img = plot_sales_distribution(df_global)
    if img is None:
        return jsonify({"error": "Columna SALES no encontrada"}), 400
    return Response(img.getvalue(), mimetype='image/png')

@app.route('/plot/pca')
def plot_pca():
    ok, resp, code = check_data_loaded()
    if not ok:
        return resp, code
    img = plot_pca_clusters(df_global)
    return Response(img.getvalue(), mimetype='image/png')

if __name__ == '__main__':
    if os.path.exists(DATA_FILE):
        df_global = load_data(DATA_FILE)
        if isinstance(df_global, pd.DataFrame):
            df_global = preprocess_data(df_global)
        else:
            print(f"Error cargando {DATA_FILE}: {df_global}")
    else:
        print(f"Archivo {DATA_FILE} no encontrado. Carga un archivo con POST /upload para usar la API.")

    app.run(host='0.0.0.0', port=8000, debug=True)
