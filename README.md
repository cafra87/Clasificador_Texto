# Identificación y Generación Automatizada de Resúmenes de Lenguaje Sencillo para el Caso de Salud

Este repositorio contiene el código fuente, los experimentos y los recursos asociados al trabajo: **"Identificación y Generación Automatizada de Resúmenes de Lenguaje Sencillo para el Caso de Salud"**.

[cite_start]El proyecto aborda la barrera de la alfabetización en salud mediante el desarrollo de herramientas de Inteligencia Artificial capaces de clasificar textos médicos y generar resúmenes en lenguaje sencillo (Plain Language Summaries - PLS) a partir de literatura biomédica técnica[cite: 1, 5, 6].

## 📖 Descripción General

La complejidad del lenguaje en textos biomédicos afecta la comprensión de diagnósticos y tratamientos por parte de los pacientes. [cite_start]Este proyecto propone una solución dividida en dos componentes principales[cite: 6, 71]:

1.  **Clasificación:** Identificación automática de textos médicos como "técnico" o "lenguaje sencillo".
2.  **Generación:** Transformación de abstracts técnicos en resúmenes accesibles utilizando Modelos Grandes de Lenguaje (LLMs) ajustados.

[cite_start]La metodología sigue el estándar **CRISP-ML** para garantizar un ciclo de vida robusto desde la preparación de datos hasta el despliegue[cite: 53].

## 📂 Conjunto de Datos (Dataset)

[cite_start]Se utilizó la colección **Cochrane**, específicamente pares de *Abstracts* (técnicos) y *Plain Language Summaries* (sencillos)[cite: 57].

* [cite_start]**Entrenamiento:** 3,563 parejas de textos[cite: 66].
* [cite_start]**Preprocesamiento:** Limpieza, normalización (minúsculas, eliminación de signos de puntuación) y emparejamiento basado en códigos DOI/CD[cite: 65, 67].

## 🛠️ Arquitectura y Modelos

### 1. Modelos de Clasificación
[cite_start]Se entrenaron clasificadores binarios utilizando representaciones vectoriales (TF-IDF) y Embeddings contextuales (BERT)[cite: 73, 80]:
* [cite_start]**Algoritmos:** Regresión Logística, Naive Bayes, Gaussian Naive Bayes, Multi-Layer Perceptron (MLP)[cite: 84, 85].
* [cite_start]**Embeddings Contextuales:** `microsoft/BiomedNLP-BiomedBERT-base-uncased-abstract-fulltext`[cite: 80].

### 2. Modelos Generativos (Fine-Tuning)
[cite_start]Se realizó un ajuste fino (Fine-tuning) utilizando la técnica **LoRA (Low-Rank Adaptation)** sobre modelos *decoder-only* (< 3B parámetros) para optimizar recursos computacionales[cite: 72, 126]:
* [cite_start]**Gemma 3 1B** [cite: 88]
* [cite_start]**Llama 3.2 1B** (con estrategia de chunking para ventanas de contexto de 2048 tokens)[cite: 88, 138].
* [cite_start]**Qwen3-0.6B-Base** y **Qwen3-1.7B-Base**[cite: 89].

### 3. Infraestructura de Despliegue
[cite_start]La solución está desplegada en la nube (**AWS**) utilizando una arquitectura de microservicios[cite: 171, 172]:
* **Orquestación:** Amazon ECS en modo Fargate.
* **Contenedores:** Docker (imágenes almacenadas en Amazon ECR).
* [cite_start]**Servicios:** Interfaz de Usuario, Microservicio de Clasificación y Microservicio de Generación PLS[cite: 173].

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
python train_lora.py --model_name "Qwen/Qwen2.5-1.5B" --data_path "./data/cochrane_train.csv"```

## 📊 Evaluación y Métricas

[cite_start]El desempeño de los modelos se evaluó utilizando un conjunto de métricas cuantitativas divididas en dos categorías principales para asegurar tanto la simplicidad como la fidelidad del contenido[cite: 9, 39].

### 1. Métricas de Legibilidad
[cite_start]Estas métricas estiman la dificultad cognitiva y el nivel educativo necesario para comprender el texto generado, basándose en la longitud de palabras, sílabas y oraciones[cite: 168, 169]:
* [cite_start]**Flesch Reading Ease:** Mide la facilidad de lectura (0-100)[cite: 209].
* [cite_start]**Gunning Fog Index:** Estima los años de educación formal requeridos[cite: 209].
* [cite_start]**SMOG Index:** Evalúa la complejidad basada en polisílabos[cite: 209].
* [cite_start]**Coleman-Liau Index, Kincaid Grade Level y Dale-Chall Index**[cite: 209].

### 2. Métricas de Preservación Semántica y Factualidad
* [cite_start]**BERTScore (Relevancia):** Utiliza embeddings contextuales para comparar la similitud semántica entre el texto generado y la referencia, evaluando la preservación del significado[cite: 160, 161].
* **AlignScore (Factualidad):** Cuantifica qué tan alineada está la información generada con el texto original. [cite_start]Divide el contexto en "chunks" para verificar que cada afirmación (claim) esté justificada por la fuente, ayudando a medir alucinaciones o inconsistencias[cite: 165, 166].

## 👥 Autores

[cite_start]Este proyecto fue desarrollado por estudiantes de la Maestría en Inteligencia Artificial de la **Universidad de los Andes**, Bogotá - Colombia[cite: 13]:

* **J. [cite_start]Blanco** - [jr.blanco@uniandes.edu.co](mailto:jr.blanco@uniandes.edu.co) [cite: 13]
* **C. [cite_start]Castellanos** - [ci.castellanos@uniandes.edu.co](mailto:ci.castellanos@uniandes.edu.co) [cite: 13]
* **C. [cite_start]Franco** - [ca.franco48@uniandes.edu.co](mailto:ca.franco48@uniandes.edu.co) [cite: 13]
* **F. [cite_start]Guzmán** - [f.guzmanc@uniandes.edu.co](mailto:f.guzmanc@uniandes.edu.co) [cite: 13]

## 🔮 Trabajo Futuro

Las líneas de investigación propuestas para extender este trabajo incluyen:
* [cite_start]**Integración RAG (Retrieval Augmented Generation):** Implementar un sistema donde los textos técnicos sean codificados (ej. con BiomedNLP-PubMedBERT) e indexados (FAISS) para recuperar ejemplos sencillos similares y guiar la generación[cite: 252, 253].
* [cite_start]**Optimización Multiobjetivo:** Desarrollar estrategias de entrenamiento que incluyan las métricas de legibilidad y factualidad directamente en la función de pérdida[cite: 251, 256].
* [cite_start]**Evaluación Humana:** Realizar pruebas cualitativas con pacientes y expertos para medir dimensiones como empatía, claridad percibida y utilidad clínica real[cite: 270, 272].

## 📄 Referencia

> Blanco, J., Castellanos, C., Franco, C., & Guzmán, F. (2025). *Identificación y Generación Automatizada de Resúmenes de Lenguaje Sencillo para el Caso de Salud*. [cite_start]Universidad de los Andes[cite: 1, 13].


