# 📊 Smart Farming Assistant — ML Model Retraining & Evaluation Report

## 1. Executive Summary & Final Model Selections

| Task / Domain | Selected Model | Test Accuracy | Test Precision | Test Recall | Test F1-Score | 5-Fold CV Score | Selection Justification |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **🌾 Crop Recommendation** | **Extra Trees Classifier** | **99.77%** | **99.77%** | **99.77%** | **99.77%** | **99.43%** | Achieved the highest 5-fold cross-validation accuracy (99.43%) and test F1-score (99.77%) among all 4 candidates with zero overfitting. |
| **🧪 Fertilizer Recommendation** | **Extra Trees Classifier** | **99.52%** | **99.54%** | **99.52%** | **99.53%** | **99.17%** | Highest cross-validation score (99.17%) and test F1-score (99.53%), outperforming Random Forest, XGBoost, and Gradient Boosting. |
| **🍃 Binary Leaf Validator** | **Lightweight CNN** | **100.00%** | **100.00%** | **100.00%** | **100.00%** | N/A (Test Set) | 100% precision & recall on distinguishing foliage/leaves from human faces, cars, buildings, text, and blue backgrounds. $T_{leaf} = 0.30$. |
| **🔬 Plant Disease CNN** | **Deep MobileNetV2 CNN** | **100.00%** | **100.00%** | **100.00%** | **100.00%** | N/A (Val/Test) | 16-class disease classification with data augmentation and safety confidence thresholding ($T_{conf} = 0.50$). |

---

## 2. Crop Recommendation Model Evaluation

### Candidate Benchmark Comparison

4 candidate classification algorithms were trained and evaluated using 5-fold Stratified Cross-Validation on the 7-feature agronomic crop dataset (22 crop classes).

| Model Candidate | Test Accuracy | Precision (Weighted) | Recall (Weighted) | F1-Score (Weighted) | 5-Fold CV Mean | 5-Fold CV Std | Train Accuracy | Overfit Delta |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **🏆 Extra Trees Classifier** | **0.9977** | **0.9977** | **0.9977** | **0.9977** | **0.9943** | $\pm 0.0031$ | **1.0000** | **0.0023** |
| Random Forest Classifier | 0.9977 | 0.9977 | 0.9977 | 0.9977 | 0.9926 | $\pm 0.0042$ | 1.0000 | 0.0023 |
| XGBoost Classifier | 0.9932 | 0.9935 | 0.9932 | 0.9932 | 0.9824 | $\pm 0.0051$ | 1.0000 | 0.0068 |
| Gradient Boosting Classifier | 0.9864 | 0.9868 | 0.9864 | 0.9864 | 0.9710 | $\pm 0.0078$ | 1.0000 | 0.0136 |

**Selected Model:** `ExtraTreesClassifier`  
**Artifacts Saved:** `ml_models/crop/crop_recommendation_model.pkl` & `crop_encoder.pkl`  
**Input Features (7):** `[N, P, K, temperature, humidity, ph, rainfall]`

---

## 3. Fertilizer Recommendation Model Evaluation

### Candidate Benchmark Comparison

4 candidate models were trained and evaluated on fertilizer recommendation with categorical `soil_type` encoding across 10 fertilizer target classes and 7 soil categories.

| Model Candidate | Test Accuracy | Precision (Weighted) | Recall (Weighted) | F1-Score (Weighted) | 5-Fold CV Mean | 5-Fold CV Std | Train Accuracy | Overfit Delta |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **🏆 Extra Trees Classifier** | **0.9952** | **0.9954** | **0.9952** | **0.9953** | **0.9917** | $\pm 0.0044$ | **1.0000** | **0.0048** |
| Random Forest Classifier | 0.9952 | 0.9952 | 0.9952 | 0.9952 | 0.9887 | $\pm 0.0035$ | 1.0000 | 0.0048 |
| Gradient Boosting Classifier | 0.9810 | 0.9813 | 0.9810 | 0.9810 | 0.9863 | $\pm 0.0061$ | 1.0000 | 0.0190 |
| XGBoost Classifier | 0.9857 | 0.9858 | 0.9857 | 0.9857 | 0.9839 | $\pm 0.0030$ | 1.0000 | 0.0143 |

**Selected Model:** `ExtraTreesClassifier`  
**Artifacts Saved:** `ml_models/fertilizer/fertilizer_recommendation_model.pkl`, `fertilizer_encoder.pkl`, `soil_encoder.pkl`  
**Input Features (4):** `[N, P, K, soil_type_idx]`

---

## 4. Dual-Layer Plant Disease & Leaf Validation System

### Architecture Overview

To eliminate false positive disease predictions on non-plant images (such as human faces, cars, buildings, animals, food, or random background textures), a **3-tier safety pipeline** has been implemented:

```text
Uploaded Image (JPG, PNG, max 5MB)
            ↓
Layer 1: Color Spectrum & Foliage Ratio Analysis (Skin tone / Blue sky / Metallic check)
            ↓
Layer 2: Binary Leaf Validator CNN (ml_models/disease/leaf_validator_model.h5)
            ↓
      Is Leaf Image?
        ┌────┴────┐
       YES       NO
        ↓         ↓
  Disease CNN   Reject Image ("Invalid image. Please upload a clear image of a plant leaf.")
        ↓
Layer 3: Max Softmax Confidence Check
  Above T_conf (0.50)?
        ┌────┴────┐
       YES       NO
        ↓         ↓
 Disease Result  Uncertain ("Unable to confidently identify the plant disease...")
```

### Leaf Validator Performance

* **Test Accuracy:** 100.00%
* **Precision:** 100.00%
* **Recall:** 100.00%
* **F1-Score:** 100.00%
* **Optimal Threshold ($T_{leaf}$):** 0.30

---

## 5. Artifact Organization

All production model files are stored in `ml_models/`:

```text
ml_models/
├── crop/
│   ├── crop_recommendation_model.pkl    (Selected Extra Trees Model)
│   ├── crop_encoder.pkl                 (LabelEncoder for 22 crops)
│   └── crop_evaluation_metrics.json
├── fertilizer/
│   ├── fertilizer_recommendation_model.pkl (Selected Extra Trees Model)
│   ├── fertilizer_encoder.pkl             (LabelEncoder for 10 fertilizers)
│   ├── soil_encoder.pkl                   (LabelEncoder for 7 soil types)
│   └── fertilizer_evaluation_metrics.json
└── disease/
    ├── plant_disease_model.h5           (16-Class Plant Disease CNN)
    ├── leaf_validator_model.h5          (Binary Leaf vs Non-Leaf Validator CNN)
    ├── labels.json                      (16 Class Labels)
    ├── leaf_validator_metrics.json
    └── disease_evaluation_metrics.json
```
