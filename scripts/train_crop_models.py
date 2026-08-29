import os
import json
import pickle
import numpy as np
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, GradientBoostingClassifier
from xgboost import XGBClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

def generate_crop_dataset(n_samples_per_crop=500, random_state=42):
    np.random.seed(random_state)
    
    crop_profiles = {
        'Rice': ([80, 100], [35, 60], [35, 45], [20, 27], [80, 90], [5.0, 7.0], [180, 300]),
        'Maize': ([60, 100], [35, 60], [15, 25], [18, 27], [55, 75], [5.5, 7.0], [60, 110]),
        'Chickpea': ([20, 50], [55, 80], [75, 85], [17, 22], [14, 20], [6.0, 8.5], [65, 95]),
        'Kidneybeans': ([15, 40], [55, 80], [15, 25], [15, 24], [18, 25], [5.5, 6.0], [60, 150]),
        'Pigeonpeas': ([15, 40], [55, 80], [18, 25], [27, 38], [30, 65], [4.5, 7.5], [90, 190]),
        'Mothbeans': ([15, 40], [35, 60], [15, 25], [24, 32], [40, 65], [3.5, 10.0], [30, 75]),
        'Mungbean': ([15, 40], [35, 60], [15, 25], [27, 30], [80, 90], [6.2, 7.2], [35, 60]),
        'Blackgram': ([35, 60], [55, 80], [15, 25], [25, 35], [60, 75], [6.5, 7.5], [60, 75]),
        'Lentil': ([15, 40], [55, 80], [15, 25], [18, 30], [60, 70], [5.9, 7.8], [35, 55]),
        'Pomegranate': ([15, 40], [10, 30], [35, 45], [18, 25], [85, 95], [5.5, 7.2], [100, 115]),
        'Banana': ([90, 120], [70, 95], [45, 55], [25, 30], [75, 85], [5.5, 6.5], [90, 120]),
        'Mango': ([15, 40], [15, 40], [25, 35], [27, 36], [45, 55], [4.5, 7.0], [85, 105]),
        'Grapes': ([15, 40], [120, 145], [195, 205], [8, 40], [80, 90], [5.5, 6.5], [60, 75]),
        'Watermelon': ([80, 120], [5, 30], [45, 55], [24, 27], [80, 90], [6.0, 7.0], [40, 60]),
        'Muskmelon': ([80, 120], [5, 30], [45, 55], [27, 30], [90, 95], [6.0, 6.8], [20, 30]),
        'Apple': ([15, 40], [120, 145], [195, 205], [21, 24], [90, 95], [5.5, 6.5], [100, 125]),
        'Orange': ([15, 40], [10, 30], [5, 15], [10, 35], [90, 95], [6.0, 7.5], [100, 120]),
        'Papaya': ([35, 70], [45, 70], [45, 55], [23, 44], [90, 95], [6.5, 7.0], [40, 250]),
        'Coconut': ([15, 40], [10, 30], [25, 35], [25, 28], [90, 98], [5.5, 6.5], [130, 220]),
        'Cotton': ([110, 140], [35, 60], [15, 25], [22, 26], [75, 85], [5.8, 8.0], [60, 90]),
        'Jute': ([60, 90], [35, 60], [35, 45], [23, 26], [70, 90], [6.0, 7.4], [150, 200]),
        'Coffee': ([80, 120], [15, 40], [25, 35], [23, 28], [50, 70], [6.0, 7.2], [115, 190])
    }
    
    x_list = []
    y_list = []
    for crop, prof in crop_profiles.items():
        n_low, n_high = prof[0]
        p_low, p_high = prof[1]
        k_low, k_high = prof[2]
        t_low, t_high = prof[3]
        h_low, h_high = prof[4]
        ph_low, ph_high = prof[5]
        r_low, r_high = prof[6]
        
        N = np.random.uniform(n_low, n_high, n_samples_per_crop) + np.random.normal(0, 1.0, n_samples_per_crop)
        P = np.random.uniform(p_low, p_high, n_samples_per_crop) + np.random.normal(0, 1.0, n_samples_per_crop)
        K = np.random.uniform(k_low, k_high, n_samples_per_crop) + np.random.normal(0, 1.0, n_samples_per_crop)
        Temp = np.random.uniform(t_low, t_high, n_samples_per_crop) + np.random.normal(0, 0.3, n_samples_per_crop)
        Hum = np.random.uniform(h_low, h_high, n_samples_per_crop) + np.random.normal(0, 0.5, n_samples_per_crop)
        pH = np.random.uniform(ph_low, ph_high, n_samples_per_crop) + np.random.normal(0, 0.05, n_samples_per_crop)
        Rain = np.random.uniform(r_low, r_high, n_samples_per_crop) + np.random.normal(0, 1.5, n_samples_per_crop)
        
        for i in range(n_samples_per_crop):
            feat = [
                max(0, N[i]), max(0, P[i]), max(0, K[i]),
                max(0, Temp[i]), max(0, min(100, Hum[i])),
                max(0, min(14, pH[i])), max(0, Rain[i])
            ]
            x_list.append(feat)
            y_list.append(crop)
            
    return np.array(x_list), np.array(y_list)

def train_and_evaluate_crop_models():
    print("=== Step 1: Training & Evaluating Crop Recommendation Models ===")
    X, y_raw = generate_crop_dataset(n_samples_per_crop=500)
    
    feature_cols = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
    
    encoder = LabelEncoder()
    y = encoder.fit_transform(y_raw)
    
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
        
        # 5-fold CV
        cv_scores = cross_val_score(model, X_train, y_train, cv=skf, scoring='accuracy')
        cv_mean = cv_scores.mean()
        cv_std = cv_scores.std()
        
        # Fit on train split
        model.fit(X_train, y_train)
        
        # Predictions
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
            
    print(f"\n[BEST] Best Crop Model Selected: {best_model_name} (F1: {best_f1:.4f})")
    
    # Save artifacts
    out_dir = os.path.join('ml_models', 'crop')
    os.makedirs(out_dir, exist_ok=True)
    
    model_path = os.path.join(out_dir, 'crop_recommendation_model.pkl')
    encoder_path = os.path.join(out_dir, 'crop_encoder.pkl')
    
    with open(model_path, 'wb') as f:
        pickle.dump(best_model_obj, f)
        
    with open(encoder_path, 'wb') as f:
        pickle.dump(encoder, f)
        
    metrics_summary = {
        'best_model': best_model_name,
        'candidates': results,
        'features': feature_cols,
        'classes': encoder.classes_.tolist()
    }
    
    with open(os.path.join(out_dir, 'crop_evaluation_metrics.json'), 'w') as f:
        json.dump(metrics_summary, f, indent=2)
        
    print(f"Saved crop model to {model_path}")
    print(f"Saved crop encoder to {encoder_path}")
    return metrics_summary

if __name__ == '__main__':
    train_and_evaluate_crop_models()
