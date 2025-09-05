import os
from pathlib import Path
import numpy as np
import pandas as pd
import joblib
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel

from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import pickle
from tqdm import tqdm

from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer, TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.model_selection import GridSearchCV

from sklearn.naive_bayes import MultinomialNB
import mlflow
import mlflow.sklearn
import json
import matplotlib.pyplot as plt

# Preprocesamiento de texto
import nltk
nltk.download('stopwords')
from nltk import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer


# Configurar semillas para facilitar la reproducibilidad de los resultados
seed = 99
torch.manual_seed(seed)
np.random.seed(seed)


# ----------------------------------------------------------
# Funciones auxiliares TFIDF
# ----------------------------------------------------------
def lectura_datos(base_path):
    non_pls_path = base_path / "non_pls"
    pls_path = base_path / "pls"

    def cargar_textos(path, label_num):
        data = []
        for archivo in path.glob("*.txt"):
            with open(archivo, "r", encoding="utf-8", errors="ignore") as f:
                contenido = f.read().strip()
                data.append({"texto": contenido, "target": label_num})
        return data

    data_non_pls = cargar_textos(non_pls_path, 0)
    data_pls = cargar_textos(pls_path, 1)

    return pd.DataFrame(data_non_pls + data_pls)

def text_preprocess(text):
    tokenizer = RegexpTokenizer(r'\w+')
    stemmer = PorterStemmer()
    tokens = tokenizer.tokenize(text.lower())
    tokens = [word for word in tokens if word not in stopwords.words('english')]
    tokens = [stemmer.stem(word) for word in tokens]
    return ' '.join(tokens)

def plot_and_save_confusion(y_true, y_pred, title, out_png):
    cm = confusion_matrix(y_true, y_pred)
    fig, ax = plt.subplots(figsize=(4,4))
    im = ax.imshow(cm, interpolation='nearest')
    ax.figure.colorbar(im, ax=ax)
    ax.set(xticks=[0,1], yticks=[0,1], xticklabels=['non_pls','pls'], yticklabels=['non_pls','pls'],
           title=title, ylabel='True label', xlabel='Predicted label')
    # etiquetas
    thresh = cm.max() / 2.
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, format(cm[i, j], 'd'),
                    ha="center", va="center",
                    color="white" if cm[i, j] > thresh else "black")
    fig.tight_layout()
    plt.savefig(out_png, bbox_inches='tight')
    plt.close(fig)



# ----------------------------------------------------------
# Entrenamiento con MLflow
# ----------------------------------------------------------
def clase_principal():
    # Configuración de MLflow
    EXPERIMENT_NAME = "Clasificador_texto_normal_vs_texto_tecnico"
    #mlflow.set_tracking_uri("http://localhost:5000")
    # para utilizar en pruebas locales:
    mlflow.set_tracking_uri("file:///home/ubuntu/mlruns")

    experiment = mlflow.set_experiment(EXPERIMENT_NAME)

    # --- Lectura de train ---
    base_train = Path("/home/ubuntu/Cochrane/train")
    data_train = lectura_datos(base_train).drop_duplicates().dropna()
    X_train, y_train = data_train["texto"], data_train["target"]

    # Split estratificado (train/val) SOLO a partir de la carpeta train
    X_train_txt, X_val_txt, y_train, y_val = train_test_split(
        X_train, y_train, test_size=0.2, stratify=y_train, random_state=seed
    )
    print("Train size:", len(X_train_txt), "Val size:", len(X_val_txt))

    # --- Lectura de test ---
    #base_test  = Path("/home/ubuntu/Cochrane/test")
    #data_test = lectura_datos(base_test).drop_duplicates().dropna()
    #test_texts  = data_test["texto"].tolist()
    #test_labels = data_test["target"].to_numpy()
 


    # ----------------------------------------------------------
    # PRIMER MODELO: COUNT-VECTORIZER_TFIDF_REGRESIÓN_LOGÍSTICA
    # ----------------------------------------------------------

    # Parámetros del modelo
    n_components = 100
    max_iter = 500

    with mlflow.start_run(run_name="COUNT-VECTORIZER-TFIDF_REGRESIÓN_LOGÍSTICA"):
        # Definir pipeline
        steps = [
            ("vectorizer", CountVectorizer(preprocessor=text_preprocess)),
            ("tfidf", TfidfTransformer()),
            ("svd", TruncatedSVD(n_components=n_components, random_state=seed)),
            ("model", LogisticRegression(max_iter=max_iter)),
        ]
        pipeline = Pipeline(steps)

        # Entrenar modelo
        pipeline.fit(X_train_txt, y_train)

        joblib.dump(pipeline, EMBED_DIR / "count_tfidf_lr.joblib")

        
        # Evaluación
        y_pred = pipeline.predict(X_val_txt)
        acc = accuracy_score(y_val, y_pred)
        f1 = f1_score(y_val, y_pred, average='macro')

        #Matriz de confusión como PNG y subirla
        cm_png = "cm_COUNT-VECTORIZER-tfidf_lr_val.png"
        plot_and_save_confusion(y_val, y_pred, "COUNT-VECTORIZERTFIDF+LR (validación)", cm_png)

        print("\n📌 Reporte de Clasificación (VAL):")
        print(classification_report(y_val, y_pred))
        print("\n📊 Matriz de confusión:")
        print(confusion_matrix(y_val, y_pred))

        # --- Loguear parámetros y métricas en MLflow ---
        mlflow.log_param("n_components", n_components)
        mlflow.log_param("max_iter", max_iter)

        mlflow.log_metric("Val accuracy", acc)
        mlflow.log_metric("Val f1_score", f1)

        mlflow.log_artifact(cm_png, artifact_path="figures")
        os.remove(cm_png)

        # Guardar el modelo
        mlflow.sklearn.log_model(pipeline, "Modelo-COUNT-VECTORIZER-TFIDF_REGRESIÓN_LOGÍSTICA")

        print(f"\n✅ Accuracy: {acc:.4f}, F1: {f1:.4f}")

    # ----------------------------------------------------------
    # SEGUNDO MODELO: TFIDF_REGRESIÓN_LOGÍSTICA
    # ----------------------------------------------------------

    tfidf = TfidfVectorizer(stop_words='english', lowercase=True,
                            max_features=20000, ngram_range=(1,2))

    pipe_lr = Pipeline([
        ("tfidf", tfidf),
        ('svd', TruncatedSVD(n_components=100)),
        ("model", LogisticRegression(max_iter=1000, class_weight="balanced", random_state=seed))
    ])

    param_grid_lr = {
        "tfidf__max_features": [20000],
        "tfidf__ngram_range": [(1,2)],
        "model__C": [0.5, 1.0, 2.0],
    }

    grid_lr = GridSearchCV(pipe_lr, param_grid_lr, scoring="f1_macro", cv=2, n_jobs=1, verbose=1)
    grid_lr.fit(X_train_txt, y_train)
    y_pred_lr = grid_lr.predict(X_val_txt)

    print("=== TF-IDF + LR ===")
    print("Best params:", grid_lr.best_params_)
    print("Val accuracy:", accuracy_score(y_val, y_pred_lr))
    print("Val F1-macro:", f1_score(y_val, y_pred_lr, average='macro'))
    print(classification_report(y_val, y_pred_lr, digits=4))

    joblib.dump(grid_lr.best_estimator_, EMBED_DIR / "tfidf_lr_best.joblib")

    with mlflow.start_run(run_name="TFIDF_REGRESIÓN_LOGÍSTICA"):

        #Matriz de confusión como PNG y subirla
        cm_png = "cm_tfidf_lr_val.png"
        plot_and_save_confusion(y_val, y_pred_lr, "TFIDF+LR (validación)", cm_png)

        #Dfinimos las métricas a registrar
        acc = accuracy_score(y_val, y_pred_lr)
        f1m = f1_score(y_val, y_pred_lr, average='macro')

        #Se registran los mejores hiperparámetros en mlflow:
        for param, value in grid_lr.best_params_.items():
            mlflow.log_param(param, value)

        #Registramos los parámetros y las métricas
        mlflow.log_metric("val_accuracy", acc)
        mlflow.log_metric("val_f1_macro", f1m)

        mlflow.log_artifact(cm_png, artifact_path="figures")
        os.remove(cm_png)

        #Guardamos en MLFlow el mejor modelo:
        mlflow.sklearn.log_model(grid_lr.best_estimator_, name="Modelo_tfidf_regresion_logistica")

    # ----------------------------------------------------------
    # TERCER MODELO: TFIDF_Naive Bayes (MultinomialNB)
    # ----------------------------------------------------------

    param_grid_nb = {
        "tfidf__max_features": [20000],
        "tfidf__ngram_range": [(1,2)],
        "model__alpha": [0.5, 1.0, 2.0]
    }

    pipe_nb = Pipeline([
        ("tfidf", TfidfVectorizer(stop_words='english', lowercase=True)),
        ("model", MultinomialNB())
    ])

    grid_nb = GridSearchCV(pipe_nb, param_grid_nb, scoring="f1_macro", cv=2, n_jobs=1, verbose=1)
    grid_nb.fit(X_train_txt, y_train)
    y_pred_nb = grid_nb.predict(X_val_txt)

    print("=== TF-IDF + MultinomialNB ===")
    print("Val accuracy:", accuracy_score(y_val, y_pred_nb))
    print("Val F1-macro:", f1_score(y_val, y_pred_nb, average='macro'))
    print(classification_report(y_val, y_pred_nb, digits=4))

    joblib.dump(grid_nb.best_estimator_, EMBED_DIR / "tfidf_nb_best.joblib")


    with mlflow.start_run(run_name="TFIDF_MEJOR NAIVE BAYES"):

        #Matriz de confusión como PNG y subirla
        cm_png = "cm_tfidf_nb_val.png"
        plot_and_save_confusion(y_val, y_pred_nb, "TFIDF+NB (validación)", cm_png)

        #Dfinimos las métricas a registrar
        acc = accuracy_score(y_val, y_pred_nb)
        f1m = f1_score(y_val, y_pred_nb, average='macro')

        #Se registran los mejores hiperparámetros en mlflow:
        for param, value in grid_nb.best_params_.items():
            mlflow.log_param(param, value)

        #Registramos los parámetros y las métricas
        mlflow.log_metric("val_accuracy", acc)
        mlflow.log_metric("val_f1_macro", f1m)

        mlflow.log_artifact(cm_png, artifact_path="figures")
        os.remove(cm_png)

        #Guardamos en MLFlow el mejor modelo:
        mlflow.sklearn.log_model(grid_nb.best_estimator_, name="Mejor_modelo_tfidf_Naive_Bayes")


    # ----------------------------------------------------------
    # CUARTO MODELO: TFIDF_MLP
    # ----------------------------------------------------------

    param_grid_mlp = {
        "tfidf__max_features": [20000],
        "tfidf__ngram_range": [(1,2)],
        "svd__n_components": [100],
        "model__hidden_layer_sizes": [(128,),(128,64)],
        "model__max_iter": [100],
    }

    pipe_mlp = Pipeline([
        ("tfidf", TfidfVectorizer(stop_words='english', lowercase=True,)),
        ('svd', TruncatedSVD(random_state=seed)),
        ("model", MLPClassifier(random_state=seed))
    ])


    grid_mlp = GridSearchCV(pipe_mlp, param_grid_mlp, scoring="f1_macro", cv=2, n_jobs=1, verbose=1)
    grid_mlp.fit(X_train_txt, y_train)
    y_pred_mlp = grid_mlp.predict(X_val_txt)

    print("=== TF-IDF + MLP ===")
    print("Best params:", grid_mlp.best_params_)
    print("Val accuracy:", accuracy_score(y_val, y_pred_mlp))
    print("Val F1-macro:", f1_score(y_val, y_pred_mlp, average='macro'))
    print(classification_report(y_val, y_pred_mlp, digits=4))

    joblib.dump(grid_mlp.best_estimator_, EMBED_DIR / "tfidf_mlp_best.joblib")

    #Enviamos a mlflow
    with mlflow.start_run(run_name="TFIDF_MEJOR_MLP"):

        #Matriz de confusión como PNG y subirla
        cm_png = "cm_tfidf_mlp_val.png"
        plot_and_save_confusion(y_val, y_pred_mlp, "TFIDF+MLP (validación)", cm_png)

        #Dfinimos las métricas a registrar
        acc = accuracy_score(y_val, y_pred_mlp)
        f1m = f1_score(y_val, y_pred_mlp, average='macro')
        #Se registran los mejores hiperparámetros en mlflow:
        for param, value in grid_mlp.best_params_.items():
            mlflow.log_param(param, value)

        #Registramos los parámetros y las métricas
        mlflow.log_metric("val_accuracy", acc)
        mlflow.log_metric("val_f1_macro", f1m)

        #Guardamos en MLFlow el mejor modelo:
        mlflow.sklearn.log_model(grid_mlp.best_estimator_, name="Mejor_modelo_tfidf_mlp")

if __name__ == "__main__":
    clase_principal()
