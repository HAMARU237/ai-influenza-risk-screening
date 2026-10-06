import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report
)


# ==========================================
# 1. Load cleaned dataset
# ==========================================

df = pd.read_csv("influenza_clean.csv")

print("Dataset shape:", df.shape)


# ==========================================
# 2. Define Features and Target
# ==========================================

features = [
    "Age",
    "Gender",
    "Sec3_Fever",
    "Sec3_Cough",
    "Sec3_Sore",
    "Sec3_Headache",
    "Sec3_Malaise",
    "Sec3_Runny",
    "Sec3_Generalized",
    "Sec3_Chill"
]

target = "Flu_final_posneg"


X = df[features]
y = df[target]


# ==========================================
# 3. Split Training / Testing
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


print("\nTraining samples:", len(X_train))
print("Testing samples:", len(X_test))


# ==========================================
# 4. Create Models
# ==========================================

models = {

    "Logistic Regression":
        LogisticRegression(max_iter=1000),

    "Decision Tree":
        DecisionTreeClassifier(
            max_depth=5,
            random_state=42
        ),

    "Random Forest":
        RandomForestClassifier(
            n_estimators=200,
            random_state=42,
            n_jobs=-1
        )
}


# ==========================================
# 5. Train and Evaluate
# ==========================================

results = {}

for name, model in models.items():

    print("\n================================")
    print(name)
    print("================================")

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    precision = precision_score(
        y_test,
        predictions
    )

    recall = recall_score(
        y_test,
        predictions
    )

    f1 = f1_score(
        y_test,
        predictions
    )

    results[name] = {
        "model": model,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1
    }

    print(
        f"Accuracy : {accuracy:.4f}"
    )

    print(
        f"Precision: {precision:.4f}"
    )

    print(
        f"Recall   : {recall:.4f}"
    )

    print(
        f"F1-score : {f1:.4f}"
    )

    print("\nClassification Report:")
    print(
        classification_report(
            y_test,
            predictions
        )
    )


# ==========================================
# 6. Select Best Model
# ==========================================

best_name = max(
    results,
    key=lambda name: results[name]["f1"]
)

best_model = results[best_name]["model"]


print("\n================================")
print("BEST MODEL")
print("================================")

print("Model:", best_name)

print(
    f"Accuracy: "
    f"{results[best_name]['accuracy']:.4f}"
)

print(
    f"F1-score: "
    f"{results[best_name]['f1']:.4f}"
)


# ==========================================
# 7. Save Model
# ==========================================

joblib.dump(
    best_model,
    "model.pkl"
)

print("\nModel saved as: model.pkl")


# ==========================================
# 8. Save Feature List
# ==========================================

joblib.dump(
    features,
    "features.pkl"
)

print("Features saved as: features.pkl")