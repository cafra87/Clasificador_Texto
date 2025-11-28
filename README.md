# Identificación y Generación Automatizada de Resúmenes de Lenguaje Sencillo para el Caso de Salud

Este repositorio contiene el código fuente, los experimentos y los recursos asociados al trabajo: **"Identificación y Generación Automatizada de Resúmenes de Lenguaje Sencillo para el Caso de Salud"**.

El proyecto aborda la barrera de la alfabetización en salud mediante el desarrollo de herramientas de Inteligencia Artificial capaces de clasificar textos médicos y generar resúmenes en lenguaje sencillo (Plain Language Summaries - PLS) a partir de literatura biomédica técnica.

## 📖 Descripción General

La complejidad del lenguaje en textos biomédicos afecta la comprensión de diagnósticos y tratamientos por parte de los pacientes. Este proyecto propone una solución dividida en dos componentes principales:

1.  **Clasificación:** Identificación automática de textos médicos como "técnico" o "lenguaje sencillo".
2.  **Generación:** Transformación de abstracts técnicos en resúmenes accesibles utilizando Modelos Grandes de Lenguaje (LLMs) con fine-tuning.

La metodología sigue el estándar **CRISP-ML** para garantizar un ciclo de vida robusto desde la preparación de datos hasta el despliegue.

## 📂 Conjunto de Datos (Dataset)

Para este proyecto se utilizó un subconjunto de la colección **Cochrane**, obtenido del dataset curado y publicado originalmente por **Arias-Russi et al. (2025)** en su trabajo sobre simplificación de textos biomédicos.

* **Fuente Original:** [Bridging the Gap in Health Literacy](https://github.com/feliperussi/bridging-the-gap-in-health-literacy.git)
* **Tamaño:** 3,563 parejas de textos (Abstract técnico vs. Resumen sencillo).
* **Preprocesamiento:** Se realizó una limpieza adicional y emparejamiento basado en códigos DOI/CD sobre los datos originales.

---
**Cita del Dataset:**
> A. Arias-Russi, C. Salazar-Lara, and R. Manrique, “Bridging the Gap in Health Literacy: Harnessing the Power of Large Language Models to Generate Plain Language Summaries from Biomedical Texts,” in Proc. 2nd Workshop on Patient-Oriented Language Processing (CL4Health), Albuquerque, NM, USA, May 2025, pp. 269–284. doi: 10.18653/v1/2025.cl4health-1.23.

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
* Las versiones de las librerías dependen de la parte del código a ejecutar, especialmente el cálculo de la métrica AlignScore, la cual requiere un entorno muy específico
* Cuenta de AWS (para despliegue)

### Configuración del Entorno

#### Fine-tuning de LLM para generación de resúmenes

El fine-tuning se realizó en Google Colab Pro en entornos con acelerador de hardware GPU A100 con RAM amplia. Los notebooks usados se encuentran en la carpeta `notebooks`, son:

* `finetuning_gemma-3-1b-it.ipynb`
* `finetuning_Llama-3.2-1B.ipynb`
* `finetuning_Qwen3-0.6B-Base.ipynb`
* `finetuning_Qwen3-1.7B-Base.ipynb`

Del entorno se descarga el adaptador, es decir los archivos `adapter_model.safetensors` y `adapter_config.json`. Usando el notebook `union_adaptador_modelo.ipynb` se crean los archivos con el modelo completo unificado. El nombre con el que se guarda el modelo se define con la variable `output_dir`. Para la generación de resúmenes se usa el notebook `generacion_resumenes.ipynb`, el cual usa la variable `version_modelo` para llamar al modelo ya guardado, y genera un archivo csv con los resultados de los resúmenes guardados en `datos/Cochrane/test/test.xlsx`.

#### Entorno para cálculo de métrica AlignScore

El entorno se creó usando los siguientes comandos:

```bash
uv init --python 3.10
uv venv
source .venv/bin/activate
uv pip install torch==1.13.1
uv pip install git+https://github.com/yuh-zha/AlignScore.git
uv add pip
uv run --with spacy spacy download en_core_web_sm
uv pip install ipykernel
uv pip install transformers==4.39.3
```
El notebook se encuentra en la carpeta `notebooks` y se llama `alignscore.ipynb`. Con la variable `version_modelo` se define qué modelo evalúa, para el cual ya se tendrían haber generado los resúmenes.

#### Entorno para cálculo de Bertscore y legibilidad

Las versiones de las librerías se encuentran en el archivo `requirements_bertscore_legibilidad.txt`. El notebook se llama `bertscore_legibilidad.ipynb`. Con la variable `version_modelo` se define qué modelo evalúa, para el cual ya se tendrían haber generado los resúmenes.

## ☁️ Arquitectura y Despliegue

El sistema fue diseñado bajo una arquitectura de **microservicios** y desplegado en la nube de **AWS (Amazon Web Services)**, garantizando escalabilidad y desacoplamiento de componentes.

### Infraestructura
La solución utiliza **Amazon ECS (Elastic Container Service)** en modo **Fargate** (Serverless) para la orquestación de contenedores, eliminando la necesidad de administrar servidores subyacentes. Las imágenes de los contenedores se gestionan a través de **Amazon ECR (Elastic Container Registry)**.

### Microservicios
El sistema se compone de tres servicios independientes, cada uno empaquetado en su propio contenedor Docker:

1.  **Frontend / Interfaz:** Módulo de interfaz web (Dashboard) que interactúa con el usuario final.
2.  **Servicio de Clasificación:** Determina si el texto ingresado es técnico o ya se encuentra en lenguaje sencillo.
3.  **Servicio de Generación (PLS):** Aloja el modelo LLM con fine-tuning encargado de generar el resumen simplificado cuando se detecta texto técnico.

### Flujo de Datos
1.  **Entrada:** El usuario ingresa el texto médico en la aplicación web.
2.  **Clasificación:** El texto se envía al microservicio clasificador.
    * *Si es Lenguaje Sencillo:* El proceso finaliza.
    * *Si es Técnico:* Se redirige al microservicio generador.
3.  **Generación:** El modelo ajustado procesa el abstract técnico y produce un resumen accesible.
4.  **Salida:** El resultado final se devuelve al Dashboard para su visualización.

> **Tecnologías:** Python, Docker, AWS (ECS, ECR, Fargate), GitHub.

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

* **Javier Blanco** - [jr.blanco@uniandes.edu.co](mailto:jr.blanco@uniandes.edu.co)
* **Carlos Castellanos** - [ci.castellanos@uniandes.edu.co](mailto:ci.castellanos@uniandes.edu.co)
* **Carlos Franco** - [ca.franco48@uniandes.edu.co](mailto:ca.franco48@uniandes.edu.co)
* **Francisco Guzmán** - [f.guzmanc@uniandes.edu.co](mailto:f.guzmanc@uniandes.edu.co)

## 🔮 Trabajo Futuro

Las líneas de investigación propuestas para extender este trabajo incluyen:
* **Integración RAG (Retrieval Augmented Generation):** Implementar un sistema donde los textos técnicos sean codificados (ej. con BiomedNLP-PubMedBERT) e indexados (FAISS) para recuperar ejemplos sencillos similares y guiar la generación.
* **Optimización Multiobjetivo:** Desarrollar estrategias de entrenamiento que incluyan las métricas de legibilidad y factualidad directamente en la función de pérdida.
* **Evaluación Humana:** Realizar pruebas cualitativas con pacientes y expertos para medir dimensiones como empatía, claridad percibida y utilidad clínica real.

## 📄 Referencia

> Blanco, J., Castellanos, C., Franco, C., & Guzmán, F. (2025). *Identificación y Generación Automatizada de Resúmenes de Lenguaje Sencillo para el Caso de Salud*. Universidad de los Andes.


