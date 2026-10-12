"""Training-only structured clinical preprocessing for a binary detection baseline."""
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def clinical_baseline(numeric_features: list[str], categorical_features: list[str]) -> Pipeline:
    if not numeric_features and not categorical_features:
        raise ValueError("At least one clinical feature is required")
    numeric = Pipeline([("impute", SimpleImputer(strategy="median", add_indicator=True)),
                        ("scale", StandardScaler())])
    categorical = Pipeline([("impute", SimpleImputer(strategy="most_frequent")),
                            ("onehot", OneHotEncoder(handle_unknown="ignore"))])
    numeric_columns = list(range(len(numeric_features)))
    categorical_columns = list(range(len(numeric_features), len(numeric_features) + len(categorical_features)))
    preprocessing = ColumnTransformer([("numeric", numeric, numeric_columns),
                                       ("categorical", categorical, categorical_columns)])
    return Pipeline([("preprocess", preprocessing),
                     ("model", LogisticRegression(C=1.0, max_iter=1000, random_state=2026))])
