import os
import json
import pickle
import numpy as np
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, GradientBoostingClassifier
from xgboost import XGBClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

def generate_fertilizer_dataset(n_samples_per_rule=500, random_state=42):
    np.random.seed(random_state)
    
    soil_types = ['Acidic', 'Alkaline', 'Loamy', 'Neutral', 'Peaty', 'Sandy', 'Clayey']
    soil_encoder = LabelEncoder()
    soil_encoder.fit(soil_types)
    
    rules = [
        # (N_range, P_range, K_range, soil_type, target_fertilizer)
        ([10, 45], [40, 80], [40, 80], 'Acidic', 'Lime'),
        ([10, 45], [40, 80], [40, 80], 'Loamy', 'Urea'),
        ([10, 45], [40, 80], [40, 80], 'Sandy', 'Urea'),
        ([40, 90], [10, 35], [40, 80], 'Neutral', 'DAP'),
        ([40, 90], [10, 35], [40, 80], 'Clayey', 'DAP'),
        ([40, 90], [40, 80], [10, 35], 'Alkaline', 'Muriate of Potash'),
        ([40, 90], [40, 80], [10, 35], 'Loamy', 'Muriate of Potash'),
        ([10, 40], [10, 40], [10, 40], 'Peaty', 'Compost'),
        ([10, 40], [10, 40], [10, 40], 'Acidic', 'Organic Fertilizer'),
        ([60, 100], [60, 100], [60, 100], 'Neutral', 'Balanced NPK Fertilizer'),
        ([60, 100], [60, 100], [60, 100], 'Loamy', 'Balanced NPK Fertilizer'),
        ([10, 45], [70, 110], [20, 50], 'Alkaline', '14-35-14'),
        ([50, 90], [50, 90], [50, 90], 'Sandy', '17-17-17'),
        ([20, 50], [20, 50], [60, 100], 'Clayey', 'Gypsum')
    ]
    
    x_list = []
    y_list = []
    
    for n_r, p_r, k_r, stype, fert in rules:
        s_idx = soil_encoder.transform([stype])[0]
        N = np.random.uniform(n_r[0], n_r[1], n_samples_per_rule) + np.random.normal(0, 1.0, n_samples_per_rule)
        P = np.random.uniform(p_r[0], p_r[1], n_samples_per_rule) + np.random.normal(0, 1.0, n_samples_per_rule)
        K = np.random.uniform(k_r[0], k_r[1], n_samples_per_rule) + np.random.normal(0, 1.0, n_samples_per_rule)
        
        for i in range(n_samples_per_rule):
            feat = [max(0, N[i]), max(0, P[i]), max(0, K[i]), float(s_idx)]
            x_list.append(feat)
            y_list.append(fert)
            
    return np.array(x_list), np.array(y_list), soil_encoder

def train_and_evaluate_fertilizer_models():
    print("=== Step 2: Training & Evaluating Fertilizer Recommendation Models ===")
    X, y_raw, soil_encoder = generate_fertilizer_dataset(n_samples_per_rule=500)
    
    fert_encoder = LabelEncoder()
    y = fert_encoder.fit_transform(y_raw)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    candidates = {
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
        'XGBoost': XGBClassifier(n_estimators=100, random_state=42, eval_metric='mlogloss'),
        'Extra Trees': ExtraTreesClassifier(n_estimators=100, random_state=42),
        'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42)
    }
    
    results = {}
    best_model_name = None
    best_f1 = -1.0
    best_model_obj = None
    
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    for name, model in candidates.items():
        print(f"\nTraining candidate: {name}...")
        
        cv_scores = cross_val_score(model, X_train, y_train, cv=skf, scoring='accuracy')
        cv_mean = cv_scores.mean()
        cv_std = cv_scores.std()
        
        model.fit(X_train, y_train)
        
        y_train_pred = model.predict(X_train)
        y_test_pred = model.predict(X_test)
        
        train_acc = accuracy_score(y_train, y_train_pred)
        test_acc = accuracy_score(y_test, y_test_pred)
        
        prec, rec, f1, _ = precision_recall_fscore_support(y_test, y_test_pred, average='weighted')
        
        results[name] = {
            'Accuracy': float(test_acc),
            'Precision': float(prec),
            'Recall': float(rec),
            'F1-Score': float(f1),
            'CV Score Mean': float(cv_mean),
            'CV Score Std': float(cv_std),
            'Train Accuracy': float(train_acc),
            'Overfit Diff': float(train_acc - test_acc)
        }
        
        print(f" -> Test Acc: {test_acc:.4f} | F1: {f1:.4f} | CV Mean: {cv_mean:.4f} | Train Acc: {train_acc:.4f}")
        
        if f1 > best_f1:
            best_f1 = f1
            best_model_name = name
            best_model_obj = model
            
    print(f"\n[BEST] Best Fertilizer Model Selected: {best_model_name} (F1: {best_f1:.4f})")
    
    out_dir = os.path.join('ml_models', 'fertilizer')
    os.makedirs(out_dir, exist_ok=True)
    
    model_path = os.path.join(out_dir, 'fertilizer_recommendation_model.pkl')
    fert_encoder_path = os.path.join(out_dir, 'fertilizer_encoder.pkl')
    soil_encoder_path = os.path.join(out_dir, 'soil_encoder.pkl')
    
    with open(model_path, 'wb') as f:
        pickle.dump(best_model_obj, f)
        
    with open(fert_encoder_path, 'wb') as f:
        pickle.dump(fert_encoder, f)
        
    with open(soil_encoder_path, 'wb') as f:
        pickle.dump(soil_encoder, f)
        
    metrics_summary = {
        'best_model': best_model_name,
        'candidates': results,
        'features': ['N', 'P', 'K', 'soil_type'],
        'fertilizers': fert_encoder.classes_.tolist(),
        'soil_types': soil_encoder.classes_.tolist()
    }
    
    with open(os.path.join(out_dir, 'fertilizer_evaluation_metrics.json'), 'w') as f:
        json.dump(metrics_summary, f, indent=2)
        
    print(f"Saved fertilizer model to {model_path}")
    print(f"Saved fertilizer encoder to {fert_encoder_path}")
    print(f"Saved soil encoder to {soil_encoder_path}")
    return metrics_summary

if __name__ == '__main__':
    train_and_evaluate_fertilizer_models()
