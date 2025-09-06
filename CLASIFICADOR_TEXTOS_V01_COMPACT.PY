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

#VARIABLES PARA EMBEDDINGS:
COCHRANE_PATH = Path("/home/ubuntu/Cochrane")
EMBED_DIR = Path("/home/ubuntu")
EMBED_DIR.mkdir(parents=True, exist_ok=True)

BATCH_SIZE = 16       # Esto se puede modificar dependiendo de la memoria
CHUNK_WORDS = 250     # tamaño de chunk en palabras
MAX_LENGTH = 512      # tokens max al tokenizar



device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

#Tokenizador y modelo BERT especializado en los datos
#tokenizer = AutoTokenizer.from_pretrained("microsoft/BiomedNLP-BiomedBERT-base-uncased-abstract-fulltext")
#model = AutoModel.from_pretrained("microsoft/BiomedNLP-BiomedBERT-base-uncased-abstract-fulltext")
model_dir = "./biomedbert"  # carpeta con el modelo
tokenizer = AutoTokenizer.from_pretrained(model_dir, local_files_only=True)
model     = AutoModel.from_pretrained(model_dir, local_files_only=True)
#tokenizer = AutoTokenizer.from_pretrained("microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract")
#model = AutoModel.from_pretrained("microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract")

# colocamos el modelo en modo evaluación para generar los embeddings
model.eval()
model.to(device)

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
# FUNCIONES AUXILIARES EMBEDDINGS
# ----------------------------------------------------------

# función para Dividir textos largos en fragmentos de hasta N palabras para que puedan 
#ser procesados eficientemente por los modelos de representación de texto con embeddings, (BERT).

def chunk_text(text, max_words=CHUNK_WORDS):
    words = text.split()
    if len(words) <= max_words:
        return [text]
    return [' '.join(words[i:i+max_words]) for i in range(0, len(words), max_words)]


def embed_batch_cls(texts, tokenizer, model, device, max_length=512, batch_size=16):
    """Devuelve np.array (N, D) con embedding CLS (last_hidden_state[:,0,:])"""
    model.eval()
    embs = []
    with torch.no_grad():
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            enc = tokenizer(batch, padding=True, truncation=True, max_length=max_length, return_tensors='pt').to(device)
            out = model(**enc)
            cls = out.last_hidden_state[:, 0, :].cpu()  # (B, D)
            cls = F.normalize(cls, p=2, dim=1)         # L2 normalize
            embs.append(cls.numpy())
    return np.vstack(embs)

def embed_batch_mean(texts, tokenizer, model, device, max_length=512, batch_size=16):
    """Devuelve np.array (N, D) con mean pooling (usando attention_mask)"""
    model.eval()
    embs = []
    with torch.no_grad():
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            enc = tokenizer(batch, padding=True, truncation=True, max_length=max_length, return_tensors='pt').to(device)
            out = model(**enc)
            att_mask = enc['attention_mask']
            mean = (out.last_hidden_state * att_mask.unsqueeze(-1)).sum(dim=1) / torch.clamp(att_mask.unsqueeze(-1).sum(dim=1), min=1e-9)
            mean = F.normalize(mean, p=2, dim=1)
            embs.append(mean.cpu().numpy())
    return np.vstack(embs)

def embed_documents(texts, tokenizer, model, device, batch_size=16, chunk_words=250, max_length=512, use="mean"):
    """
    texts: list[str]
    use: "mean" (pooling sobre tokens) o "cls"
    Devuelve: np.array (N_docs, D)
    """
    all_doc_embs = []
    with torch.no_grad():
        for doc in tqdm(texts, desc="Embedding docs"):
            chunks = chunk_text(doc, max_words=chunk_words)  # utilizamos chunk text
            chunk_embs = []
            # procesar los chunks en lotes
            for i in range(0, len(chunks), batch_size):
                batch_chunks = chunks[i:i+batch_size]
                if use == "mean":
                    emb = embed_batch_mean(batch_chunks, tokenizer, model, device,
                                           max_length=max_length, batch_size=len(batch_chunks))
                else:
                    emb = embed_batch_cls(batch_chunks, tokenizer, model, device,
                                          max_length=max_length, batch_size=len(batch_chunks))
                chunk_embs.append(emb)  # (b, D)
            chunk_embs = np.vstack(chunk_embs)   # (n_chunks, D)
            doc_emb = chunk_embs.mean(axis=0)    # promedio de chunks → (D,)
            all_doc_embs.append(doc_emb)
    return np.vstack(all_doc_embs)               # (N_docs, D)


"""Las siguientes funciones sirven para separar correctamente los datos en train (para entrenar/validar) y test (para la evaluación final). 
Cargan solo un split (train o test). A partir del train, se hace un split estratificado en train y val 
(porque la carpeta test ya está reservada para la evaluación final).

Se crean los embeddings y se guardan según el conjunto de datos que se esá utilizando 
(cochrane_train_embeddings.npz y cochrane_test_embeddings.npz) para no recalcular.
"""

def load_cochrane_split(base_path: Path, split: str):
    """
    Carga SOLO un split: 'train' o 'test'
    Devuelve (files, texts, labels) en orden determinístico.
    """
    assert split in ("train", "test")
    base_split = base_path / split

    df = lectura_datos(base_split).dropna().drop_duplicates()
    # rutas “falsas” si no quieres depender del path real
    files = [f"{split}/{i}.txt" for i in range(len(df))]
    texts = df["texto"].tolist()
    labels = np.array(df["target"].tolist(), dtype=int)
    return files, texts, labels

def embed_or_load_split(split_name: str, texts: list):
    save_path = EMBED_DIR / f"cochrane_{split_name}_embeddings.npz"
    print("Ruta esperada de embeddings:", save_path.resolve())
    if save_path.exists():
        print(f"Cargando embeddings de {split_name}:", save_path)
        d = np.load(save_path, allow_pickle=True)
        return d["embeddings"]
    else:
        print(f"Generando embeddings ({split_name})…")
        embs = embed_documents(
            texts, tokenizer, model, device,
            batch_size=BATCH_SIZE, chunk_words=CHUNK_WORDS,
            max_length=MAX_LENGTH, use="mean"
        )
        np.savez_compressed(save_path, embeddings=embs)
        print("Guardado:", save_path)
        return embs

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

    """Objetivo (B): entrenar con embeddings BERT (densos) y probar tres clasificadores:

    LogisticRegression con pequeña búsqueda en C

    GaussianNB (adecuado para densos)

    MLP (scikit-learn) encima de embeddings


    """


    _, train_texts, train_labels = load_cochrane_split(COCHRANE_PATH, "train")
    

    # Embeddings BERT para todo el split train (cache)
    # así evitamos recalcular; luego partimos en train/val por índices
    train_emb_all = embed_or_load_split("train", train_texts)
    print("Embeddings (train) shape:", train_emb_all.shape)

    # Mapear embeddings al split train/val (misma posición que train_texts)
    # Creamos índices basados en la posición
    idx_all = np.arange(len(train_texts))
    X_train_idx, X_val_idx, _, _ = train_test_split(
        idx_all, train_labels, test_size=0.2, stratify=train_labels, random_state=seed
    )
    X_train_emb = train_emb_all[X_train_idx]
    X_val_emb   = train_emb_all[X_val_idx]

    # Etiquetas alineadas con los indices
    y_train_emb = train_labels[X_train_idx]
    y_val_emb   = train_labels[X_val_idx]


    scaler_bert = StandardScaler()
    X_train_emb_s = scaler_bert.fit_transform(X_train_emb)
    X_val_emb_s   = scaler_bert.transform(X_val_emb)

    # ----------------------------------------------------------
    # QUINTO MODELO: BERT EMBEDDINGS + REGRESIÓN LOGÍSTICA
    # ----------------------------------------------------------

    param_C = [0.5, 1.0, 2.0]
    best_lr = None
    best_f1 = -1
    for C in param_C:
        clf = LogisticRegression(max_iter=1000, class_weight="balanced", C=C)
        clf.fit(X_train_emb_s, y_train_emb)
        pred = clf.predict(X_val_emb_s)
        f1m = f1_score(y_val_emb, pred, average='macro')
        if f1m > best_f1:
            best_f1 = f1m
            best_lr = clf
    print("=== BERT emb + LR ===")
    print("Best C:", best_lr.C, "Val F1-macro:", best_f1)
    print(classification_report(y_val_emb, best_lr.predict(X_val_emb_s), digits=4))
    joblib.dump({"scaler": scaler_bert, "clf": best_lr}, EMBED_DIR / "bert_lr_best.joblib")


    with mlflow.start_run(run_name="BERT_LR_BusquedaSimple"):

        #Matriz de confusión como PNG y subirla
        cm_png = "cm_bert_lr_val.png"
        plot_and_save_confusion(y_val_emb, best_lr.predict(X_val_emb_s), "BERT+LR (validación)", cm_png)

        # log params
        mlflow.log_param("param_grid_C", param_C)
        mlflow.log_param("best_C", best_lr.C)

        # metrics
        acc = accuracy_score(y_val_emb, best_lr.predict(X_val_emb_s))
        f1m = f1_score(y_val_emb, best_lr.predict(X_val_emb_s), average='macro')
        mlflow.log_metric("val_accuracy", acc)
        mlflow.log_metric("val_f1_macro", f1m)

        mlflow.log_artifact(cm_png, artifact_path="figures")
        os.remove(cm_png)

        # guardar modelo (scaler + clf)
        mlflow.sklearn.log_model(best_lr, name="bert_lr_model")

      # ----------------------------------------------------------
    # SEXTO MODELO: BERT EMBEDDINGS + NAIVE BAYES GAUSIANO
    # ----------------------------------------------------------
    gnb = GaussianNB()
    gnb.fit(X_train_emb_s, y_train_emb)

    pred_gnb = gnb.predict(X_val_emb_s)
    acc = accuracy_score(y_val_emb, pred_gnb)
    f1m = f1_score(y_val_emb, pred_gnb, average='macro')

    print("=== BERT emb + GaussianNB ===")
    print("Val accuracy:", acc)
    print("Val F1-macro:", f1m)
    print(classification_report(y_val_emb, pred_gnb, digits=4))


    joblib.dump({"scaler": scaler_bert, "gnb": gnb}, EMBED_DIR / "bert_gnb_best.joblib")


    with mlflow.start_run(run_name="BERT_NAIVE_BAYES"):

        #Matriz de confusión como PNG y subirla
        cm_png = "cm_bert_gnb_val.png"
        plot_and_save_confusion(y_val_emb, pred_gnb, "BERT+GNB (validación)", cm_png)

        #parámetros
        mlflow.log_param("model", "GaussianNB")
        mlflow.log_param("var_smoothing", gnb.var_smoothing)
        mlflow.log_param("encoder_model", "BiomedBERT")
        mlflow.log_param("pooling", "mean")
        mlflow.log_param("chunk_words", CHUNK_WORDS)
        mlflow.log_param("max_length", MAX_LENGTH)


        # metrics
        mlflow.log_metric("val_accuracy", acc)
        mlflow.log_metric("val_f1_macro", f1m)

        # guardar modelo (scaler + clf)
        mlflow.sklearn.log_model(gnb, artifact_path="bert_gnb_model")
        joblib.dump(scaler_bert, "scaler_bert.joblib")
        mlflow.log_artifact("scaler_bert.joblib", artifact_path="preproc")
        os.remove("scaler_bert.joblib")

    # ----------------------------------------------------------
    # SEPTIMO MODELO: BERT EMBEDDINGS + MLP
    # ----------------------------------------------------------

    param_grid_mlp_emb = {
        "hidden_layer_sizes": [(128,), (128,64)],
        "alpha": [1e-3],               # L2 regularization
        "learning_rate_init": [5e-4],
        "max_iter": [100],
    }

    mlp_base = MLPClassifier(
        random_state=seed,
        early_stopping=True,     # para terminar antes si no mejora
        n_iter_no_change=5,
        validation_fraction=0.1,
    )

    grid_mlp_emb = GridSearchCV(
        mlp_base,
        param_grid_mlp_emb,
        scoring="f1_macro",
        cv=3,
        n_jobs=-1,
        verbose=1
    )

    #entrenamiento
    grid_mlp_emb.fit(X_train_emb_s, y_train_emb)

    # Evaluar en tu split de validación externo
    pred_mlp_emb = grid_mlp_emb.predict(X_val_emb_s)
    acc = accuracy_score(y_val_emb, pred_mlp_emb)
    f1m = f1_score(y_val_emb, pred_mlp_emb, average='macro')


    print("=== BERT emb + MLP (Grid) ===")
    print("Best params:", grid_mlp_emb.best_params_)
    print("Val accuracy:", acc)
    print("Val F1-macro:", f1m)
    print(classification_report(y_val_emb, pred_mlp_emb, digits=4))


    joblib.dump({"scaler": scaler_bert, "mlp": grid_mlp_emb.best_estimator_}, EMBED_DIR / "bert_mlp_best.joblib")

    # ====== MLflow logging ======
    with mlflow.start_run(run_name="BERTemb_MEJOR_MLP"):

        #Matriz de confusión como PNG y subirla
        cm_png = "cm_bert_mlp_val.png"
        plot_and_save_confusion(y_val_emb, pred_mlp_emb, "BERT+MLP (validación)", cm_png)

        # hiperparámetros ganadores
        for p, v in grid_mlp_emb.best_params_.items():
            mlflow.log_param(p, v)

        # metadatos del encoder
        mlflow.log_param("encoder_model", "BiomedBERT")
        mlflow.log_param("pooling", "mean")
        mlflow.log_param("chunk_words", CHUNK_WORDS)
        mlflow.log_param("max_length", MAX_LENGTH)

        # métricas
        mlflow.log_metric("val_accuracy", acc)
        mlflow.log_metric("val_f1_macro", f1m)

        # subir solo el clasificador (recuerda escalar antes de usarlo)
        mlflow.sklearn.log_model(grid_mlp_emb.best_estimator_, name="bert_mlp_model")

        # subir el scaler como artefacto
        joblib.dump(scaler_bert, "scaler_bert.joblib")
        mlflow.log_artifact("scaler_bert.joblib", artifact_path="preproc")
        os.remove("scaler_bert.joblib")


if __name__ == "__main__":
    clase_principal()
