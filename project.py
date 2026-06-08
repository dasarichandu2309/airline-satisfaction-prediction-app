import numpy as np
import pandas as pd
import mlflow
import mlflow.sklearn
import optuna

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
from sklearn.impute import SimpleImputer

import joblib
import time
import os
import warnings

warnings.filterwarnings("ignore")
os.environ["LOKY_MAX_CPU_COUNT"] = "4"

# ---------------- LOAD DATA ----------------
data = pd.read_csv(r"C:\Users\dasar\OneDrive\Desktop\ML_Project\airline_passenger_satisfaction.csv")

data['Gender'] = data['Gender'].map({'Male': 1, 'Female': 0})

# Encode categorical
for col in data.columns:
    if data[col].dtype == 'object':
        le = LabelEncoder()
        data[col] = le.fit_transform(data[col])

data = data.drop_duplicates()

X = data.drop(["Satisfaction", "ID"], axis=1)
y = data["Satisfaction"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, stratify=y, random_state=42
)

# ---------------- PIPELINE ----------------
pipeline = Pipeline([
    ('Imputer', SimpleImputer(strategy='most_frequent')),
    ('Scaler', StandardScaler()),
    ('Model', KNeighborsClassifier())
])

# ---------------- OBJECTIVES ----------------
def objective_knn(trial):
    scaler_type = trial.suggest_categorical('scaler_type', ['standard', 'minmax'])

    pipeline.set_params(
        Scaler=StandardScaler() if scaler_type == 'standard' else MinMaxScaler(),
        Model=KNeighborsClassifier(
            n_neighbors=trial.suggest_int('n_neighbors', 3, 21, step=2),
            weights=trial.suggest_categorical('weights', ['uniform', 'distance']),
            p=trial.suggest_int('p', 1, 3)
        )
    )

    skf = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)

    return cross_val_score(pipeline, X_train, y_train, cv=skf, n_jobs=1).mean()


def objective_dt(trial):
    scaler_type = trial.suggest_categorical('scaler_type', ['standard', 'minmax'])

    pipeline.set_params(
        Scaler=StandardScaler() if scaler_type == 'standard' else MinMaxScaler(),
        Model=DecisionTreeClassifier(
            max_depth=trial.suggest_int('max_depth', 2, 20),
            random_state=42
        )
    )

    skf = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)

    return cross_val_score(pipeline, X_train, y_train, cv=skf, n_jobs=1).mean()


def objective_svm(trial):
    scaler_type = trial.suggest_categorical('scaler_type', ['standard', 'minmax'])
    kernel = trial.suggest_categorical('kernel', ['linear', 'rbf'])

    params = {
        "C": trial.suggest_float("C", 1e-3, 10, log=True),
        "kernel": kernel
    }

    if kernel == "rbf":
        params["gamma"] = trial.suggest_float("gamma", 1e-4, 1e-2, log=True)

    pipeline.set_params(
        Scaler=StandardScaler() if scaler_type == 'standard' else MinMaxScaler(),
        Model=SVC(**params)
    )

    skf = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)

    return cross_val_score(pipeline, X_train, y_train, cv=skf, n_jobs=1).mean()


def objective_rf(trial):
    scaler_type = trial.suggest_categorical('scaler_type', ['standard', 'minmax'])

    pipeline.set_params(
        Scaler=StandardScaler() if scaler_type == 'standard' else MinMaxScaler(),
        Model=RandomForestClassifier(
            n_estimators=trial.suggest_int('n_estimators', 100, 200, step=50),
            max_depth=trial.suggest_int('max_depth', 5, 20),
            random_state=42,
            n_jobs=-1
        )
    )

    skf = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)

    return cross_val_score(pipeline, X_train, y_train, cv=skf, n_jobs=1).mean()


def objective_gb(trial):
    scaler_type = trial.suggest_categorical('scaler_type', ['standard', 'minmax'])

    pipeline.set_params(
        Scaler=StandardScaler() if scaler_type == 'standard' else MinMaxScaler(),
        Model=GradientBoostingClassifier(
            n_estimators=trial.suggest_int('n_estimators', 100, 200, step=50),
            learning_rate=trial.suggest_float('learning_rate', 0.01, 0.1),
            random_state=42
        )
    )

    skf = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)

    return cross_val_score(pipeline, X_train, y_train, cv=skf, n_jobs=1).mean()


objectives = {
    "KNN": objective_knn,
    "DecisionTree": objective_dt,
    "SVM": objective_svm,
    "RandomForest": objective_rf,
    "GradientBoosting": objective_gb
}

mlflow.set_experiment("FINAL_RUN")

results = {}

# ---------------- TRAIN LOOP ----------------
for model_name, obj_fn in objectives.items():
    print(f"\n--- Optimizing {model_name} ---")

    with mlflow.start_run(run_name=model_name):

        study = optuna.create_study(direction="maximize")

        start = time.time()
        study.optimize(obj_fn, n_trials=3)   # 🔥 REDUCED
        fit_time = time.time() - start

        best_params = study.best_params
        scaler_type = best_params["scaler_type"]

        # simple final model (no heavy tuning again)
        if model_name == "KNN":
            model = KNeighborsClassifier(n_neighbors=best_params["n_neighbors"])

        elif model_name == "DecisionTree":
            model = DecisionTreeClassifier(max_depth=best_params["max_depth"])

        elif model_name == "SVM":
            model = SVC(C=best_params["C"], kernel=best_params["kernel"])

        elif model_name == "RandomForest":
            model = RandomForestClassifier(n_estimators=best_params["n_estimators"], n_jobs=-1)

        elif model_name == "GradientBoosting":
            model = GradientBoostingClassifier(n_estimators=best_params["n_estimators"])

        pipeline.set_params(
            Scaler=StandardScaler() if scaler_type == 'standard' else MinMaxScaler(),
            Model=model
        )

        pipeline.fit(X_train, y_train)

        y_pred = pipeline.predict(X_test)

        train_acc = pipeline.score(X_train, y_train)
        test_acc = accuracy_score(y_test, y_pred)

        # Save model
        model_path = f"{model_name}.pkl"
        joblib.dump(X.columns.tolist(), "features.pkl")
        joblib.dump(pipeline, model_path)
        model_size = os.path.getsize(model_path)

        # MLflow logging
        mlflow.log_metric("train_acc", train_acc)
        mlflow.log_metric("test_acc", test_acc)
        mlflow.log_metric("fit_time", fit_time)
        mlflow.log_metric("model_size", model_size)

        mlflow.sklearn.log_model(pipeline, model_name)

        os.remove(model_path)

        results[model_name] = {
            "train": train_acc,
            "test": test_acc,
            "time": fit_time,
            "size": model_size
        }

# ---------------- FINAL SUMMARY ----------------
print("\n--- FINAL SUMMARY ---")
for name, res in results.items():
    print(
        f"{name} -> Train: {res['train']:.4f}, "
        f"Test: {res['test']:.4f}, "
        f"Time: {res['time']:.2f}s, "
        f"Size: {res['size']} bytes"
    )