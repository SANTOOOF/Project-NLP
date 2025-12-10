# 🧬 Biomedical Named Entity Recognition (Bio-NER) on the GENIA Corpus

## 📜 Description du Projet

Ce projet a pour objectif de concevoir un système capable d'identifier et de classifier automatiquement les entités biologiques (Protéines, ADN, ARN, etc.) dans les résumés d'articles scientifiques[cite: 28]. [cite_start]Nous avons implémenté un pipeline robuste en Python, combinant des techniques de Machine Learning classiques avec un *Feature Engineering* avancé et le décodage de Viterbi pour garantir la cohérence des prédictions[cite: 29, 31].

---

## 🎯 Objectif Principal

Développement d'un système de Bio-NER sur le corpus GENIA (Version 3.02), la référence standard pour l'extraction d'informations dans le domaine biomédical[cite: 28, 35].

## 📊 Jeu de Données et Classes Cibles

* **Corpus utilisé** : GENIA Corpus (Version 3.02), issu d'extraits d'articles de la base de données MEDLINE[cite: 35, 37].
* **Volume** : Environ 23,793 entités nommées annotées manuellement[cite: 38].
* **Format** : XML, nécessitant un parsing précis[cite: 39].
* **5 Classes Cibles** (simplifiées à partir de 36 classes fines)[cite: 41]:
    1.  **Protein** [cite: 42]
    2.  **DNA** [cite: 43]
    3.  **RNA** [cite: 44]
    4.  **Cell Line** [cite: 45]
    5.  **Cell Type** [cite: 46]

---

## 🛠️ Méthodologie et Implémentation

### 1. Pré-traitement et Encodage [cite: 50]

* **Encodage** : Schéma standard **BIO** (Begin, Inside, Outside)[cite: 52].
* **Class Splitting** : Division de la classe majoritaire "O" (Outside) en sous-classes basées sur les tags Part-of-Speech (e.g., O-NN, O-VB) pour améliorer la distinction du contexte linguistique[cite: 53, 54].

### 2. Feature Engineering [cite: 55]

Un vecteur de caractéristiques a été généré pour chaque mot, incluant :

* **Contexte Morphologique** : Le mot, ses préfixes (2 et 3 lettres), suffixes, présence de majuscules ou de chiffres[cite: 57].
* **Fenêtre Glissante (Sliding Window)** : Caractéristiques des 2 mots précédents et suivants[cite: 58].
* **Word Cache** : Indication binaire si le mot a déjà été vu comme une entité[cite: 59].
* **HMM States** : États d'un Modèle de Markov Caché (HMM) non supervisé pour capturer des structures latentes[cite: 60].

### 3. Modèles et Post-traitement [cite: 61]

* **Modèles Entraînés** : Random Forest, SVM, XGBoost[cite: 62].
* **Post-traitement Crucial** : Implémentation de l'**algorithme de Viterbi**[cite: 63].
    * **Rôle** : Utilise une matrice de transition pour corriger les erreurs de séquence illégales (e.g., un tag `I-Protein` isolé) et garantir la validité des séquences BIO[cite: 63, 166].

---

## 🚀 Résultats Clés

### 1. Comparaison des Modèles

Les modèles linéaires ont dominé le classement, suggérant l'efficacité du *feature engineering* à rendre le problème linéairement séparable dans un espace de haute dimension[cite: 71].

| Modèle | Rang | Précision (Accuracy) | F1-Score (Pondéré) |
| :--- | :---: | :---: | :---: |
| **Linear SVM** | **1** | [cite_start]**88.40%** [cite: 70] | [cite_start]**0.88** [cite: 70] |
| Logistic Regression | 2 | [cite_start]88.20% [cite: 70] | [cite_start]0.88 [cite: 70] |
| SVM (RBF Kernel) | 3 | [cite_start]85.97% [cite: 70] | [cite_start]0.85 [cite: 70] |
| Random Forest | 4 | [cite_start]85.22% [cite: 70] | [cite_start]0.84 [cite: 70] |

* **Meilleure Performance** : Le **Linear SVM** a atteint une précision de $\mathbf{88.40\%}$ et un F1-Score pondéré de **0.88**[cite: 70].

<img width="1189" height="590" alt="output" src="https://github.com/user-attachments/assets/5042d500-cd31-424b-a7e4-276945aebdb4" />


<img width="797" height="701" alt="output1" src="https://github.com/user-attachments/assets/aa01e3f8-3f93-4de0-a5db-12574791f7dd" />

### 2. Analyse des Erreurs

* Les classes **Protein** et **Cell Type** sont les mieux détectées[cite: 91].
* La classe **DNA** est souvent confondue avec les protéines en raison de contextes syntaxiques similaires[cite: 91].

### 3. Impact Qualitatif de Viterbi

L'algorithme de Viterbi s'est avéré crucial pour la cohérence structurelle[cite: 171].

> **Exemple de correction** : Le modèle Standard Random Forest a prédit un tag `I-protein` isolé pour le mot "5-lipoxygenase". [cite_start]Le décodeur de Viterbi, en appliquant les règles de transition BIO, a corrigé cette erreur en forçant le tag `B-protein` (Début d'entité)[cite: 165, 166].

---

## 💡 Conclusion et Perspectives

Ce projet a validé l'efficacité d'une approche hybride combinant des connaissances linguistiques (POS tagging, *Class Splitting*) et des techniques statistiques de Machine Learning pour le Bio-NER[cite: 169].

L'importance du **Feature Engineering** (Word Cache, HMM) et du **décodage de Viterbi** est confirmée pour garantir la fiabilité des informations extraites[cite: 170, 171].

### Prochaines Étapes

Le travail pourrait être étendu en utilisant des modèles de *Deep Learning* contextuels comme **BioBERT** afin de mieux capturer les dépendances à plus longue portée[cite: 172].

---
## 🧑‍💻 Auteurs du Projet

* Youssef RAHLI [cite: 14]
* Zouitni SALAH EDDINE [cite: 15]
* Yassir CHERGUI [cite: 16]

**Supervision** : Pr. ED-DRISSIYA EL-ALLALY [cite: 18, 19]

**Année Académique** : 2025-2026 [cite: 17]
**Module** : NLP (Natural Language Processing) [cite: 93, 103]
