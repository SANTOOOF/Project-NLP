from flask import Flask, request, jsonify, render_template, send_from_directory
import joblib
import os
import re
import numpy as np
import pandas as pd
from datetime import datetime
from collections import deque
import nltk

app = Flask(__name__)

# --- Configuration ---
BASE_DIR = os.path.dirname(__file__)
ARTIFACT_DIR = os.path.join(BASE_DIR, "saved_models")
LOGO_PATH = os.path.join(BASE_DIR, "logo.png")

# --- Class Definitions (Required for unpickling) ---
class WordCache:
    """
    Implements the word cache feature.
    Tracks if a word has appeared previously in the text.
    """
    def __init__(self):
        self.cache = set()
    
    def add(self, word):
        self.cache.add(word.lower())
    
    def contains(self, word):
        return word.lower() in self.cache
    
    def reset(self):
        self.cache.clear()

class UnsupervisedHMM:
    """
    Implements unsupervised HMM to generate features for rare words.
    """
    def __init__(self, n_states=10):
        self.n_states = n_states
        self.word_to_state = {}
        self.state_transitions = None
        
    def fit(self, sentences, min_freq=5):
        pass
    
    def get_state(self, word):
        word_lower = word.lower()
        return self.word_to_state.get(word_lower, 0)

# --- Global State ---
MODEL_CACHE = {}
SHARED_ARTIFACTS = {}

def load_shared_artifacts():
    """Loads vectorizer, label encoder, and HMM."""
    try:
        vec_path = os.path.join(ARTIFACT_DIR, "vectorizer.joblib")
        hmm_path = os.path.join(ARTIFACT_DIR, "hmm_model.joblib")
        le_path = os.path.join(ARTIFACT_DIR, "label_encoder.joblib")
        
        if os.path.exists(vec_path):
            SHARED_ARTIFACTS['vectorizer'] = joblib.load(vec_path)
        if os.path.exists(hmm_path):
            SHARED_ARTIFACTS['hmm'] = joblib.load(hmm_path)
        if os.path.exists(le_path):
            SHARED_ARTIFACTS['le'] = joblib.load(le_path)
            
        print(f"✓ Shared artifacts loaded: {list(SHARED_ARTIFACTS.keys())}")
    except Exception as e:
        print(f"⚠️ Error loading shared artifacts: {e}")

load_shared_artifacts()

def get_available_models():
    """Scans the saved_models directory for .joblib model files."""
    models = []
    if os.path.exists(ARTIFACT_DIR):
        for f in os.listdir(ARTIFACT_DIR):
            if f.endswith(".joblib") and f not in ["vectorizer.joblib", "label_encoder.joblib", "hmm_model.joblib"]:
                models.append(f)
    return sorted(models)

def get_model(model_name):
    """Loads a specific model from disk or cache."""
    if model_name in MODEL_CACHE:
        return MODEL_CACHE[model_name]
    
    path = os.path.join(ARTIFACT_DIR, model_name)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Model {model_name} not found.")
    
    print(f"Loading model from disk: {model_name}...")
    model = joblib.load(path)
    MODEL_CACHE[model_name] = model
    return model

def sentence_to_features_single(tokens, pos_tags, hmm=None, word_cache=None):
    """
    Extracts features for a single sentence.
    Matches notebook logic.
    """
    doc_features = []
    window = 2
    
    for i in range(len(tokens)):
        word = tokens[i]
        
        features = {
            'bias': 1.0,
            'word.lower()': word.lower(),
            'word.isupper()': word.isupper(),
            'word.istitle()': word.istitle(),
            'word.isdigit()': word.isdigit(),
            'pos': pos_tags[i],
            'prefix-2': word[:2],
            'prefix-3': word[:3],
            'suffix-2': word[-2:],
            'suffix-3': word[-3:],
        }
        
        # Window context
        for w in range(1, window + 1):
            if i - w >= 0:
                features[f'-{w}:word.lower()'] = tokens[i-w].lower()
                features[f'-{w}:pos'] = pos_tags[i-w]
            else:
                features[f'-{w}:word.lower()'] = 'BOS'

            if i + w < len(tokens):
                features[f'+{w}:word.lower()'] = tokens[i+w].lower()
                features[f'+{w}:pos'] = pos_tags[i+w]
            else:
                features[f'+{w}:word.lower()'] = 'EOS'
        
        # Word Cache
        if word_cache is not None:
            features['in_cache'] = word_cache.contains(word)
            word_cache.add(word)

        # HMM features
        if hmm is not None:
            features['hmm_state'] = hmm.get_state(word)
            if i - 1 >= 0:
                features['hmm_state-1'] = hmm.get_state(tokens[i-1])
            if i + 1 < len(tokens):
                features['hmm_state+1'] = hmm.get_state(tokens[i+1])
        
        doc_features.append(features)
    return doc_features

def predict_ner_dynamic(text, model_name):
    """
    Predicts entities using the selected model.
    """
    if 'vectorizer' not in SHARED_ARTIFACTS:
        raise ValueError("Vectorizer not loaded. Cannot process text.")
        
    # 1. Tokenize
    tokens = nltk.word_tokenize(text)
    if not tokens:
        return []
        
    # 2. POS Tagging
    pos_tags = [tag for word, tag in nltk.pos_tag(tokens)]
    
    # 3. Feature Extraction
    hmm = SHARED_ARTIFACTS.get('hmm')
    # Create a fresh cache for this prediction request
    word_cache = WordCache()
    
    features = sentence_to_features_single(tokens, pos_tags, hmm, word_cache)
    
    # 4. Vectorize
    X = SHARED_ARTIFACTS['vectorizer'].transform(features)
    
    # 5. Load Model & Predict
    clf = get_model(model_name)
    predictions = clf.predict(X)
    
    # 6. Handle Numeric Labels (e.g. XGBoost)
    if len(predictions) > 0 and (isinstance(predictions[0], (int, np.integer)) or isinstance(predictions[0], float)):
        if 'le' in SHARED_ARTIFACTS:
            predictions = SHARED_ARTIFACTS['le'].inverse_transform(predictions.astype(int))
        else:
            # Fallback if LE is missing but model returns ints
            predictions = [str(p) for p in predictions]

    # 7. Format Result
    results = []
    for token, label in zip(tokens, predictions):
        simple_label = label
        if isinstance(label, str) and label.startswith("O-"):
            simple_label = "O"
        results.append({"token": token, "label": simple_label})
        
    return results

# Ensure NLTK data is downloaded
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')

@app.route("/")
def index():
    models = get_available_models()
    return render_template("index.html", models=models)

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json(force=True)
        text = data.get("text", "").strip()
        model_name = data.get("model_name")
        
        if not text:
            return jsonify({"error": "Le texte est vide."}), 400
        if len(text) > 5000:
            return jsonify({"error": "Texte trop long (max 5000 caractères)."}), 400
        if not model_name:
            return jsonify({"error": "Aucun modèle sélectionné."}), 400

        # Perform prediction
        predictions = predict_ner_dynamic(text, model_name)
        
        # Extract entities for summary
        entities = []
        current_ent = []
        current_type = None
        
        for item in predictions:
            lbl = item['label']
            if lbl.startswith("B-"):
                if current_ent:
                    entities.append({"text": " ".join(current_ent), "type": current_type})
                current_ent = [item['token']]
                current_type = lbl[2:]
            elif lbl.startswith("I-") and current_ent:
                current_ent.append(item['token'])
            else:
                if current_ent:
                    entities.append({"text": " ".join(current_ent), "type": current_type})
                current_ent = []
                current_type = None
        if current_ent:
             entities.append({"text": " ".join(current_ent), "type": current_type})

        return jsonify({
            "ok": True,
            "predictions": predictions,
            "entities": entities,
            "model_used": model_name
        })

    except FileNotFoundError:
        return jsonify({"error": "Modèle introuvable sur le serveur."}), 404
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/logo.png")
def logo():
    return send_from_directory(os.path.dirname(LOGO_PATH), "logo.png")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
