"""Lead propensity score: probability a lead activates, using only what is
known when the lead is created (no stage dates, follow-up calls or cost -
those leak the outcome). Logistic regression keeps it explainable for the
sales team: each lead shows its top reasons.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

DATA = Path(__file__).resolve().parent.parent / "data"
CAT = ["segment", "lead_source", "preferred_language", "has_gstin", "has_udyam", "current_internet",
       "current_provider", "annual_turnover_band", "contact_role"]
NUM = ["city_tier", "log_employees", "num_sites", "log_spend", "n_interest"]


def features(df: pd.DataFrame) -> pd.DataFrame:
    X = df[CAT + ["city_tier", "num_sites"]].copy()
    X["log_employees"] = np.log1p(df["employee_count"])
    X["log_spend"] = np.log1p(df["monthly_telecom_spend_inr"])
    X["n_interest"] = df["products_of_interest"].fillna("").str.count(";") + 1
    return X


def _pipe() -> Pipeline:
    pre = ColumnTransformer([("cat", OneHotEncoder(handle_unknown="ignore"), CAT), ("num", StandardScaler(), NUM)])
    return Pipeline([("pre", pre), ("lr", LogisticRegression(max_iter=2000, C=0.5, class_weight="balanced"))])


@lru_cache(maxsize=1)
def model():
    df = pd.read_csv(DATA / "smb_leads.csv")
    y = (df["outcome"] == "Activated").astype(int).values
    X = features(df)
    oof = cross_val_predict(_pipe(), X, y, cv=StratifiedKFold(5, shuffle=True, random_state=7), method="predict_proba")[:, 1]
    auc = roc_auc_score(y, oof)
    pipe = _pipe().fit(X, y)
    # lift: activation rate in top decile vs average
    dec = pd.qcut(pd.Series(oof).rank(method="first"), 10, labels=False)
    lift = pd.Series(y).groupby(dec).mean()
    top3 = pd.Series(y)[dec >= 7]
    stats = {"cv_auc": round(float(auc), 3), "base_rate": round(float(y.mean()), 4),
             "top_decile_rate": round(float(lift.iloc[-1]), 4), "bottom_decile_rate": round(float(lift.iloc[0]), 4),
             "top30_share_of_activations": round(float(top3.sum() / y.sum()), 3),
             "decile_rates": [round(float(v), 4) for v in lift.values]}
    return pipe, stats, oof


def explain(pipe: Pipeline, row: pd.DataFrame, k: int = 3) -> list[str]:
    pre, lr = pipe.named_steps["pre"], pipe.named_steps["lr"]
    x = pre.transform(row)
    x = x.toarray()[0] if hasattr(x, "toarray") else x[0]
    contrib = x * lr.coef_[0]
    names = pre.get_feature_names_out()
    order = np.argsort(-np.abs(contrib))[:k]
    out = []
    for i in order:
        n = names[i].replace("cat__", "").replace("num__", "")
        out.append(("+ " if contrib[i] > 0 else "- ") + n.replace("_", " "))
    return out


def score_leads(df: pd.DataFrame) -> pd.DataFrame:
    pipe, _, _ = model()
    X = features(df)
    df = df.copy()
    df["propensity"] = pipe.predict_proba(X)[:, 1]
    return df


if __name__ == "__main__":
    _, s, _ = model()
    print(json.dumps(s, indent=1))
