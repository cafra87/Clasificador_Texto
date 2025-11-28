# Identificación y Generación Automatizada de Resúmenes de Lenguaje Sencillo para el Caso de Salud

Este repositorio contiene el código fuente, los experimentos y los recursos asociados al trabajo: **"Identificación y Generación Automatizada de Resúmenes de Lenguaje Sencillo para el Caso de Salud"**.

El proyecto aborda la barrera de la alfabetización en salud mediante el desarrollo de herramientas de Inteligencia Artificial capaces de clasificar textos médicos y generar resúmenes en lenguaje sencillo (Plain Language Summaries - PLS) a partir de literatura biomédica técnica.

## 📖 Descripción General

La complejidad del lenguaje en textos biomédicos afecta la comprensión de diagnósticos y tratamientos por parte de los pacientes. Este proyecto propone una solución dividida en dos componentes principales:

1.  **Clasificación:** Identificación automática de textos médicos como "técnico" o "lenguaje sencillo".
2.  **Generación:** Transformación de abstracts técnicos en resúmenes accesibles utilizando Modelos Grandes de Lenguaje (LLMs) ajustados.

La metodología sigue el estándar **CRISP-ML** para garantizar un ciclo de vida robusto desde la preparación de datos hasta el despliegue.

## 📂 Conjunto de Datos (Dataset)

Se utilizó la colección **Cochrane**, específicamente pares de *Abstracts* (técnicos) y *Plain Language Summaries* (sencillos).

* **Entrenamiento:** 3,563 parejas de textos.
* **Preprocesamiento:** Limpieza, normalización (minúsculas, eliminación de signos de puntuación) y emparejamiento basado en códigos DOI/CD.

## 🛠️ Arquitectura y Modelos

### 1. Modelos de Clasificación
Se entrenaron clasificadores binarios utilizando representaciones vectoriales (TF-IDF) y Embeddings contextuales (BERT):
* **Algoritmos:** Regresión Logística, Naive Bayes, Gaussian Naive Bayes, Multi-Layer Perceptron (MLP).
* **Embeddings Contextuales:** `microsoft/BiomedNLP-BiomedBERT-base-uncased-abstract-fulltext`.

### 2. Modelos Generativos (Fine-Tuning)
Se realizó un ajuste fino (Fine-tuning) utilizando la técnica **LoRA (Low-Rank Adaptation)** sobre modelos *decoder-only* (< 3B parámetros) para optimizar recursos computacionales:
* **Gemma 3 1B**
* **Llama 3.2 1B** (con estrategia de chunking para ventanas de contexto de 2048 tokens).
* **Qwen3-0.6B-Base** y **Qwen3-1.7B-Base**.

### 3. Infraestructura de Despliegue
La solución está desplegada en la nube (**AWS**) utilizando una arquitectura de microservicios:
* **Orquestación:** Amazon ECS en modo Fargate.
* **Contenedores:** Docker (imágenes almacenadas en Amazon ECR).
* **Servicios:** Interfaz de Usuario, Microservicio de Clasificación y Microservicio de Generación PLS.

## 🚀 Instalación y Uso

### Prerrequisitos
* Python 3.10+
* Cuenta de AWS (para despliegue)
* Bibliotecas principales: `transformers`, `scikit-learn`, `peft`, `torch`.

### Configuración del Entorno

1.  Clonar el repositorio:
    ```bash
    git clone [https://github.com/tu-usuario/nombre-del-repo.git](https://github.com/tu-usuario/nombre-del-repo.git)
    cd nombre-del-repo
    ```

2.  Instalar dependencias:
    ```bash
    pip install -r requirements.txt
    ```

### Entrenamiento (Ejemplo con LoRA)

Para reproducir el fine-tuning de los modelos (ej. Qwen o Llama) con adaptadores LoRA:

```python
# Ejemplo genérico de ejecución
python train_lora.py --model_name "Qwen/Qwen2.5-1.5B" --data_path "./data/cochrane_train.csv"
```

## 📊 Evaluación y Métricas

El desempeño de los modelos se evaluó utilizando un conjunto de métricas cuantitativas divididas en dos categorías principales para asegurar tanto la simplicidad como la fidelidad del contenido.

### 1. Métricas de Legibilidad
Estas métricas estiman la dificultad cognitiva y el nivel educativo necesario para comprender el texto generado, basándose en la longitud de palabras, sílabas y oraciones:
* **Flesch Reading Ease:** Mide la facilidad de lectura (0-100).
* **Gunning Fog Index:** Estima los años de educación formal requeridos.
* **SMOG Index:** Evalúa la complejidad basada en polisílabos.
* **Coleman-Liau Index, Kincaid Grade Level y Dale-Chall Index**.

### 2. Métricas de Preservación Semántica y Factualidad
* **BERTScore (Relevancia):** Utiliza embeddings contextuales para comparar la similitud semántica entre el texto generado y la referencia, evaluando la preservación del significado.
* **AlignScore (Factualidad):** Cuantifica qué tan alineada está la información generada con el texto original. Divide el contexto en "chunks" para verificar que cada afirmación (claim) esté justificada por la fuente, ayudando a medir alucinaciones o inconsistencias.

## 👥 Autores

Este proyecto fue desarrollado por estudiantes de la Maestría en Inteligencia Artificial de la **Universidad de los Andes**, Bogotá - Colombia:

* **J. Blanco** - [jr.blanco@uniandes.edu.co](mailto:jr.blanco@uniandes.edu.co)
* **C. Castellanos** - [ci.castellanos@uniandes.edu.co](mailto:ci.castellanos@uniandes.edu.co)
* **C. Franco** - [ca.franco48@uniandes.edu.co](mailto:ca.franco48@uniandes.edu.co)
* **F. Guzmán** - [f.guzmanc@uniandes.edu.co](mailto:f.guzmanc@uniandes.edu.co)

## 🔮 Trabajo Futuro

Las líneas de investigación propuestas para extender este trabajo incluyen:
* **Integración RAG (Retrieval Augmented Generation):** Implementar un sistema donde los textos técnicos sean codificados (ej. con BiomedNLP-PubMedBERT) e indexados (FAISS) para recuperar ejemplos sencillos similares y guiar la generación.
* **Optimización Multiobjetivo:** Desarrollar estrategias de entrenamiento que incluyan las métricas de legibilidad y factualidad directamente en la función de pérdida.
* **Evaluación Humana:** Realizar pruebas cualitativas con pacientes y expertos para medir dimensiones como empatía, claridad percibida y utilidad clínica real.

## 📄 Referencia

> Blanco, J., Castellanos, C., Franco, C., & Guzmán, F. (2025). *Identificación y Generación Automatizada de Resúmenes de Lenguaje Sencillo para el Caso de Salud*. Universidad de los Andes.


