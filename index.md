

# Guide d'indexation de la base de données (BM25)

Ce document décrit la procédure étape par étape pour indexer le codebase conformément aux exigences du sujet *RAG against the machine*.

---

## 📋 Prérequis & Contraintes du sujet

* **Temps maximal d'indexation** : ≤ 5 minutes pour l'ensemble du corpus.


* **Taille maximale des chunks** : Paramétrable via `--max_chunk_size` (défaut : 2000 caractères).


* **Format de sortie** : L'index doit être sauvegardé dans le dossier `data/processed/`.


* **Intégrité des métadonnées** : Conservation exacte des chemins relatifs (`file_path`) et des positions de caractères (`first_character_index`, `last_character_index`).



---

## 🛠️ Étapes de mise en œuvre

### Étape 1 : Préparation de l'environnement et des dossiers

1. Installe les dépendances nécessaires avec `uv` :
`uv add rank-bm25 pydantic tqdm fire`
2. Vérifie la présence de la base source dans `data/raw/` (ex: `data/raw/vllm-0.10.1/`).


3. Crée le dossier de destination : `mkdir -p data/processed`

---

### Étape 2 : Implémentation des stratégies de découpage (Chunking)

Le sujet impose deux stratégies distinctes selon l'extension du fichier :

#### 1. Fichiers Markdown et Texte (`.md`, `.txt`)

* Découpe le texte par paragraphes ou lignes.
* Veille à ne jamais dépasser la limite de `max_chunk_size`.



#### 2. Fichiers Python (`.py`)

* Utilise le module standard `ast` pour extraire les blocs logiques (fonctions, classes, méthodes).
* Si une fonction dépasse `max_chunk_size`, applique un sous-découpage par blocs de lignes.



---

### Étape 3 : Tokenisation du corpus

1. Normalise et nettoie le texte de chaque chunk :
* Passage en minuscules.
* Extraction des mots et identifiants Python à l'aide d'une expression régulière (`re.findall(r"\w+", text.lower())`).


2. Construis la liste globale des tokens (`corpus_tokens`).

---

### Étape 4 : Construction et sauvegarde de l'index BM25

1. Initialise le modèle BM25 avec `BM25Okapi(corpus_tokens)`.
2. Regroupe l'index et les métadonnées des chunks dans un dictionnaire.
3. Sauvegarde le tout sous `data/processed/bm25_index.pkl` via `pickle`.



---

### Étape 5 : Intégration à la CLI (Python Fire)

Expose la méthode `index` dans ta classe CLI pour permettre l'appel dynamique.

---

## 🚀 Exécution et Validation

Lance la commande d'indexation via `uv` :

`uv run python -m src index --max_chunk_size 2000`

### Vérifications à effectuer :

* Le processus s'exécute en **moins de 5 minutes**.


* Le fichier `data/processed/bm25_index.pkl` est bien créé.


* Aucun chunk enregistré ne dépasse 2000 caractères.



---

Veux-tu qu'on écrive directement le fichier de code Python `src/indexer.py` ?