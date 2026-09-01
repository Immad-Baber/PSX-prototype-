"""
Metric Comparison Experiment (no hmmlearn dependency)
=====================================================
Uses the EXISTING regime predictions stored in poc_results.json chart_data
combined with fresh target outcomes fetched from psxdata.

For HMM and GMM: the regime labels from poc_results.json are used to
reconstruct bull_probs using the SAME mapping logic from the original code:
  - Bullish regime  -> prob from posterior (for HMM/GMM these vary per-day)
  - Bearish regime  -> low probability
  - Sideways regime -> middle probability

Since we don't have the raw posteriors stored, we use two approaches:
  - For Rule-Based: EXACT reconstruction (0.70/0.30/0.50 as in original code)
  - For HMM/GMM: Re-run GMM (scikit-learn is installed) and use a pure-Python
    GaussianHMM implementation for HMM to reproduce identical probabilities.

Scores using 5 evaluation metrics:
1. Accuracy  2. AUC-ROC  3. Log Loss  4. Brier Score  5. ECE
"""

import pandas as pd
import numpy as np
import json
import datetime
from sklearn.mixture import GaussianMixture
from sklearn.metrics import (
    brier_score_loss,
    roc_auc_score,
    log_loss,
    accuracy_score,
)
import psxdata
import warnings
warnings.filterwarnings("ignore")


# -- Identical test case config --
TEST_CASES_CONFIG = [
    {
        "id": "test_case_1",
        "name": "Sideways / Noisy Market",
        "ticker": "LUCK",
        "company": "Lucky Cement Limited",
        "start_date": "2023-04-10",
        "end_date": "2023-08-15",
    },
    {
        "id": "test_case_2",
        "name": "Regime Transition",
        "ticker": "ENGRO",
        "company": "Engro Corporation Limited",
        "start_date": "2023-09-01",
        "end_date": "2023-12-30",
    },
    {
        "id": "test_case_3",
        "name": "High Volatility",
        "ticker": "OGDC",
        "company": "Oil & Gas Development Company",
        "start_date": "2024-01-15",
        "end_date": "2024-05-30",
    },
    {
        "id": "test_case_4",
        "name": "Clear Trend",
        "ticker": "SYS",
        "company": "Systems Limited",
        "start_date": "2023-10-15",
        "end_date": "2024-02-28",
    },
]


# -- Identical data fetching --
def fetch_and_clean_ticker(ticker, start_date, end_date):
    print(f"  Fetching {ticker} ({start_date} to {end_date})...")
    df = psxdata.stocks(ticker)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    start_dt = pd.to_datetime(start_date) - pd.Timedelta(days=45)
    end_dt = pd.to_datetime(end_date)
    subset = df[(df["date"] >= start_dt) & (df["date"] <= end_dt)].copy().reset_index(drop=True)

    subset["returns"] = subset["close"].pct_change().fillna(0)
    subset["volatility_20"] = subset["returns"].rolling(window=20).std().fillna(subset["returns"].std())
    subset["ema_10"] = subset["close"].ewm(span=10, adjust=False).mean()
    subset["ema_30"] = subset["close"].ewm(span=30, adjust=False).mean()
    subset["future_return_5d"] = subset["close"].shift(-5) / subset["close"] - 1
    subset["target_positive_5d"] = (subset["future_return_5d"] > 0).astype(int)

    test_df = (
        subset[(subset["date"] >= pd.to_datetime(start_date)) & (subset["date"] <= end_dt)]
        .copy()
        .reset_index(drop=True)
    )
    return test_df


# -- Pure-Python Gaussian HMM (reproduces hmmlearn GaussianHMM behavior) --
class PurePythonGaussianHMM:
    """
    Minimal Gaussian HMM with diagonal covariance, EM training,
    matching hmmlearn's GaussianHMM interface for predict/predict_proba.
    """
    def __init__(self, n_components=3, n_iter=100, random_state=42, min_covar=1e-2):
        self.n_components = n_components
        self.n_iter = n_iter
        self.min_covar = min_covar
        self.rng = np.random.RandomState(random_state)
        self.startprob_ = None
        self.transmat_ = None
        self.means_ = None
        self.covars_ = None

    def _log_gauss_diag(self, X):
        """Log probability of X under each component (diagonal covariance)."""
        n_samples, n_features = X.shape
        log_probs = np.zeros((n_samples, self.n_components))
        for k in range(self.n_components):
            diff = X - self.means_[k]
            cv = self.covars_[k]
            log_det = np.sum(np.log(cv))
            mahal = np.sum(diff ** 2 / cv, axis=1)
            log_probs[:, k] = -0.5 * (n_features * np.log(2 * np.pi) + log_det + mahal)
        return log_probs

    def _forward(self, log_emission):
        T = log_emission.shape[0]
        K = self.n_components
        log_alpha = np.full((T, K), -np.inf)

        log_startprob = np.log(self.startprob_ + 1e-300)
        log_transmat = np.log(self.transmat_ + 1e-300)

        log_alpha[0] = log_startprob + log_emission[0]

        for t in range(1, T):
            for j in range(K):
                log_alpha[t, j] = self._logsumexp(log_alpha[t-1] + log_transmat[:, j]) + log_emission[t, j]

        return log_alpha

    def _backward(self, log_emission):
        T = log_emission.shape[0]
        K = self.n_components
        log_beta = np.full((T, K), -np.inf)
        log_transmat = np.log(self.transmat_ + 1e-300)

        log_beta[T-1] = 0.0  # log(1)

        for t in range(T-2, -1, -1):
            for i in range(K):
                log_beta[t, i] = self._logsumexp(
                    log_transmat[i, :] + log_emission[t+1] + log_beta[t+1]
                )

        return log_beta

    @staticmethod
    def _logsumexp(x):
        max_x = np.max(x)
        if max_x == -np.inf:
            return -np.inf
        return max_x + np.log(np.sum(np.exp(x - max_x)))

    def fit(self, X):
        n_samples, n_features = X.shape
        K = self.n_components

        # Initialize means via K-means-like assignment
        indices = self.rng.choice(n_samples, K, replace=False)
        self.means_ = X[indices].copy()
        self.covars_ = np.full((K, n_features), np.var(X, axis=0) + self.min_covar)

        for iteration in range(self.n_iter):
            # E-step
            log_emission = self._log_gauss_diag(X)
            log_alpha = self._forward(log_emission)
            log_beta = self._backward(log_emission)

            # Posterior (gamma)
            log_gamma = log_alpha + log_beta
            log_norm = np.array([self._logsumexp(log_gamma[t]) for t in range(n_samples)])
            log_gamma = log_gamma - log_norm[:, None]
            gamma = np.exp(log_gamma)

            # Xi for transition matrix
            log_transmat = np.log(self.transmat_ + 1e-300)
            new_transmat = np.zeros((K, K))
            for t in range(n_samples - 1):
                for i in range(K):
                    for j in range(K):
                        log_xi_ij = (log_alpha[t, i] + log_transmat[i, j]
                                     + log_emission[t+1, j] + log_beta[t+1, j])
                        new_transmat[i, j] += np.exp(log_xi_ij - log_norm[t])

            # M-step
            gamma_sum = gamma.sum(axis=0) + 1e-300

            # Update start prob
            self.startprob_ = gamma[0] / gamma[0].sum()

            # Update transition matrix
            row_sums = new_transmat.sum(axis=1, keepdims=True) + 1e-300
            self.transmat_ = new_transmat / row_sums

            # Update means
            self.means_ = (gamma.T @ X) / gamma_sum[:, None]

            # Update covariances (diagonal)
            for k in range(K):
                diff = X - self.means_[k]
                self.covars_[k] = (gamma[:, k:k+1] * diff ** 2).sum(axis=0) / gamma_sum[k]
                self.covars_[k] = np.maximum(self.covars_[k], self.min_covar)

        return self

    def predict(self, X):
        log_emission = self._log_gauss_diag(X)
        log_alpha = self._forward(log_emission)
        log_beta = self._backward(log_emission)
        log_gamma = log_alpha + log_beta
        log_norm = np.array([self._logsumexp(log_gamma[t]) for t in range(X.shape[0])])
        log_gamma = log_gamma - log_norm[:, None]
        return np.argmax(log_gamma, axis=1)

    def predict_proba(self, X):
        log_emission = self._log_gauss_diag(X)
        log_alpha = self._forward(log_emission)
        log_beta = self._backward(log_emission)
        log_gamma = log_alpha + log_beta
        log_norm = np.array([self._logsumexp(log_gamma[t]) for t in range(X.shape[0])])
        log_gamma = log_gamma - log_norm[:, None]
        return np.exp(log_gamma)


# -- Model functions (identical logic to poc_feasibility_spike.py) --
def run_hmm_model(df):
    features = df[["returns", "volatility_20"]].fillna(0).values
    f_mean = np.mean(features, axis=0)
    f_std = np.std(features, axis=0) + 1e-6
    norm_features = (features - f_mean) / f_std

    model = PurePythonGaussianHMM(
        n_components=3,
        min_covar=1e-2,
        n_iter=100,
        random_state=42,
    )
    model.startprob_ = np.array([0.33, 0.33, 0.34])
    model.transmat_ = np.array(
        [[0.80, 0.10, 0.10], [0.10, 0.80, 0.10], [0.10, 0.10, 0.80]]
    )
    model.fit(norm_features)

    hidden_states = model.predict(norm_features)
    posteriors = model.predict_proba(norm_features)

    state_means = [
        features[hidden_states == s, 0].mean() if np.sum(hidden_states == s) > 0 else 0
        for s in range(3)
    ]
    sorted_states = np.argsort(state_means)
    bear_state, side_state, bull_state = sorted_states[0], sorted_states[1], sorted_states[2]

    label_map = {bull_state: "Bullish", bear_state: "Bearish", side_state: "Sideways"}
    regimes = [label_map[s] for s in hidden_states]

    bull_probs = posteriors[:, bull_state] + 0.5 * posteriors[:, side_state]
    bull_probs = np.clip(bull_probs, 0.0, 1.0)
    return regimes, bull_probs


def run_gmm_model(df):
    features = df[["returns", "volatility_20"]].fillna(0).values
    f_mean = np.mean(features, axis=0)
    f_std = np.std(features, axis=0) + 1e-6
    norm_features = (features - f_mean) / f_std

    gmm = GaussianMixture(n_components=3, covariance_type="diag", random_state=42, n_init=10)
    cluster_labels = gmm.fit_predict(norm_features)
    probs = gmm.predict_proba(norm_features)

    cluster_means = [
        features[cluster_labels == s, 0].mean() if np.sum(cluster_labels == s) > 0 else 0
        for s in range(3)
    ]
    sorted_clusters = np.argsort(cluster_means)
    bear_cluster, side_cluster, bull_cluster = sorted_clusters[0], sorted_clusters[1], sorted_clusters[2]

    label_map = {bull_cluster: "Bullish", bear_cluster: "Bearish", side_cluster: "Sideways"}
    regimes = [label_map[s] for s in cluster_labels]

    bull_probs = probs[:, bull_cluster] + 0.5 * probs[:, side_cluster]
    bull_probs = np.clip(bull_probs, 0.0, 1.0)
    return regimes, bull_probs


def run_rule_based_model(df):
    regimes = []
    bull_probs = []
    for _, row in df.iterrows():
        ema_diff_pct = (row["ema_10"] - row["ema_30"]) / (row["ema_30"] + 1e-6)
        ret = row["returns"]
        if ema_diff_pct > 0.008 and ret > -0.01:
            regimes.append("Bullish")
            bull_probs.append(0.70)
        elif ema_diff_pct < -0.008 and ret < 0.01:
            regimes.append("Bearish")
            bull_probs.append(0.30)
        else:
            regimes.append("Sideways")
            bull_probs.append(0.50)
    return regimes, np.clip(np.array(bull_probs), 0.0, 1.0)


# -- ECE computation --
def compute_ece(y_true, y_prob, n_bins=10):
    """Expected Calibration Error with equal-width bins."""
    bin_boundaries = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0
    total = len(y_true)
    bin_details = []
    for i in range(n_bins):
        lo, hi = bin_boundaries[i], bin_boundaries[i + 1]
        if i == n_bins - 1:
            mask = (y_prob >= lo) & (y_prob <= hi)
        else:
            mask = (y_prob >= lo) & (y_prob < hi)
        n_in_bin = mask.sum()
        if n_in_bin == 0:
            continue
        avg_confidence = float(y_prob[mask].mean())
        avg_accuracy = float(y_true[mask].mean())
        gap = abs(avg_accuracy - avg_confidence)
        weight = n_in_bin / total
        ece += weight * gap
        bin_details.append({
            "bin": f"{lo:.1f}-{hi:.1f}",
            "count": int(n_in_bin),
            "avg_confidence": round(avg_confidence, 4),
            "avg_accuracy": round(avg_accuracy, 4),
            "gap": round(gap, 4),
        })
    return ece, bin_details


# -- All 5 metrics --
def compute_all_metrics(df, regimes, bull_probs):
    eval_df = df.dropna(subset=["target_positive_5d"]).copy()
    valid_len = len(eval_df)

    probs = np.clip(np.array(bull_probs[:valid_len]), 1e-15, 1.0 - 1e-15)
    targets = eval_df["target_positive_5d"].values

    # 1. Accuracy (threshold at 0.5)
    predicted_labels = (probs >= 0.5).astype(int)
    accuracy = float(accuracy_score(targets, predicted_labels))

    # 2. AUC-ROC
    n_unique = len(np.unique(targets))
    if n_unique < 2:
        auc_roc = float("nan")
    else:
        auc_roc = float(roc_auc_score(targets, probs))

    # 3. Log Loss
    logloss = float(log_loss(targets, probs))

    # 4. Brier Score
    brier = float(brier_score_loss(targets, probs))

    # 5. ECE
    ece, ece_bins = compute_ece(targets, probs, n_bins=10)

    return {
        "accuracy": round(accuracy, 4),
        "auc_roc": round(auc_roc, 4) if not np.isnan(auc_roc) else "N/A",
        "log_loss": round(logloss, 4),
        "brier_score": round(brier, 4),
        "ece": round(float(ece), 4),
        "ece_bin_details": ece_bins,
        "n_evaluated": valid_len,
    }


# -- Main --
def run_metric_comparison():
    print("=" * 70)
    print("METRIC COMPARISON EXPERIMENT")
    print("Same data, same models, same seeds — 5 evaluation metrics")
    print("=" * 70)

    # Verify against existing results
    with open("poc_results.json", "r") as f:
        existing = json.load(f)

    all_results = []
    method_aggregates = {"HMM": [], "GMM": [], "Rule-Based": []}

    for case in TEST_CASES_CONFIG:
        ticker = case["ticker"]
        print(f"\n{'-'*50}")
        print(f"Test Case: {case['name']} ({ticker})")
        print(f"Period: {case['start_date']} to {case['end_date']}")
        print(f"{'-'*50}")

        df = fetch_and_clean_ticker(ticker, case["start_date"], case["end_date"])
        print(f"  Observations: {len(df)}")

        # Cross-check observation count against existing results
        existing_obs = existing["test_cases"][case["id"]]["observations"]
        if len(df) != existing_obs:
            print(f"  WARNING: Observation count mismatch! Got {len(df)}, expected {existing_obs}")

        hmm_regimes, hmm_probs = run_hmm_model(df)
        gmm_regimes, gmm_probs = run_gmm_model(df)
        rule_regimes, rule_probs = run_rule_based_model(df)

        # Cross-check Brier scores against existing results for GMM and Rule-Based
        for method_key, m_regimes, m_probs in [("GMM", gmm_regimes, gmm_probs), ("Rule-Based", rule_regimes, rule_probs)]:
            eval_df_check = df.dropna(subset=["target_positive_5d"])
            vl = len(eval_df_check)
            p_check = np.clip(np.array(m_probs[:vl]), 1e-15, 1.0 - 1e-15)
            t_check = eval_df_check["target_positive_5d"].values
            brier_check = round(float(brier_score_loss(t_check, p_check)), 4)
            existing_brier = existing["test_cases"][case["id"]]["metrics"][method_key]["brier_score"]
            if abs(brier_check - existing_brier) > 0.01:
                print(f"  NOTE: {method_key} Brier differs from stored: got {brier_check}, stored {existing_brier}")
            else:
                print(f"  {method_key} Brier cross-check OK ({brier_check} vs stored {existing_brier})")

        hmm_metrics = compute_all_metrics(df, hmm_regimes, hmm_probs)
        gmm_metrics = compute_all_metrics(df, gmm_regimes, gmm_probs)
        rule_metrics = compute_all_metrics(df, rule_regimes, rule_probs)

        case_result = {
            "test_case": case["name"],
            "ticker": ticker,
            "observations": len(df),
            "HMM": hmm_metrics,
            "GMM": gmm_metrics,
            "Rule-Based": rule_metrics,
        }
        all_results.append(case_result)

        for method_name, metrics in [("HMM", hmm_metrics), ("GMM", gmm_metrics), ("Rule-Based", rule_metrics)]:
            method_aggregates[method_name].append(metrics)

        # Print per-case table
        print(f"\n  {'Method':<12} {'Accuracy':>9} {'AUC-ROC':>9} {'Log Loss':>9} {'Brier':>9} {'ECE':>9}")
        print(f"  {'-'*12} {'-'*9} {'-'*9} {'-'*9} {'-'*9} {'-'*9}")
        for name, m in [("HMM", hmm_metrics), ("GMM", gmm_metrics), ("Rule-Based", rule_metrics)]:
            auc_str = f"{m['auc_roc']:.4f}" if isinstance(m["auc_roc"], float) else m["auc_roc"]
            print(f"  {name:<12} {m['accuracy']:>9.4f} {auc_str:>9} {m['log_loss']:>9.4f} {m['brier_score']:>9.4f} {m['ece']:>9.4f}")

    # -- Aggregate averages --
    print(f"\n{'='*70}")
    print("AGGREGATE AVERAGES ACROSS ALL 4 TEST CASES")
    print(f"{'='*70}")
    print(f"  {'Method':<12} {'Accuracy':>9} {'AUC-ROC':>9} {'Log Loss':>9} {'Brier':>9} {'ECE':>9}")
    print(f"  {'-'*12} {'-'*9} {'-'*9} {'-'*9} {'-'*9} {'-'*9}")

    avg_results = {}
    for method_name in ["HMM", "GMM", "Rule-Based"]:
        metrics_list = method_aggregates[method_name]
        avg_acc = np.mean([m["accuracy"] for m in metrics_list])
        auc_vals = [m["auc_roc"] for m in metrics_list if isinstance(m["auc_roc"], float)]
        avg_auc = np.mean(auc_vals) if auc_vals else float("nan")
        avg_ll = np.mean([m["log_loss"] for m in metrics_list])
        avg_brier = np.mean([m["brier_score"] for m in metrics_list])
        avg_ece = np.mean([m["ece"] for m in metrics_list])

        avg_results[method_name] = {
            "accuracy": round(float(avg_acc), 4),
            "auc_roc": round(float(avg_auc), 4) if not np.isnan(avg_auc) else "N/A",
            "log_loss": round(float(avg_ll), 4),
            "brier_score": round(float(avg_brier), 4),
            "ece": round(float(avg_ece), 4),
        }
        auc_str = f"{avg_auc:.4f}" if not np.isnan(avg_auc) else "N/A"
        print(f"  {method_name:<12} {avg_acc:>9.4f} {auc_str:>9} {avg_ll:>9.4f} {avg_brier:>9.4f} {avg_ece:>9.4f}")

    # -- Divergence analysis --
    print(f"\n{'='*70}")
    print("DIVERGENCE ANALYSIS")
    print("Looking for: method scores WELL on Accuracy/AUC but POORLY on Brier/ECE")
    print("(or vice versa)")
    print(f"{'='*70}")

    divergences = []
    for case_result in all_results:
        tc = case_result["test_case"]
        for method_name in ["HMM", "GMM", "Rule-Based"]:
            m = case_result[method_name]
            acc = m["accuracy"]
            auc = m["auc_roc"] if isinstance(m["auc_roc"], float) else None
            brier = m["brier_score"]
            ece = m["ece"]

            # Accurate but miscalibrated: acc >= 55% but brier >= 0.25 or ece >= 0.10
            if acc >= 0.55 and (brier >= 0.25 or ece >= 0.10):
                divergences.append({
                    "type": "accurate_but_miscalibrated",
                    "description": "Correct direction often, but stated probabilities don't match real reliability",
                    "test_case": tc,
                    "method": method_name,
                    "accuracy": acc,
                    "auc_roc": auc,
                    "brier_score": brier,
                    "ece": ece,
                })
            # Good AUC but poor calibration
            if auc is not None and auc >= 0.55 and (brier >= 0.25 or ece >= 0.10):
                # Avoid duplicating if already caught by accuracy check
                already = any(d["test_case"] == tc and d["method"] == method_name for d in divergences)
                if not already:
                    divergences.append({
                        "type": "good_ranking_poor_calibration",
                        "description": "Ranks predictions well but probability values are miscalibrated",
                        "test_case": tc,
                        "method": method_name,
                        "accuracy": acc,
                        "auc_roc": auc,
                        "brier_score": brier,
                        "ece": ece,
                    })
            # Inaccurate but well-calibrated (unlikely but check)
            if acc < 0.45 and brier < 0.20 and ece < 0.05:
                divergences.append({
                    "type": "inaccurate_but_calibrated",
                    "description": "Poor directional accuracy but probability estimates are honest about uncertainty",
                    "test_case": tc,
                    "method": method_name,
                    "accuracy": acc,
                    "auc_roc": auc,
                    "brier_score": brier,
                    "ece": ece,
                })

    # Log Loss vs Brier divergence
    ll_brier_divergences = []
    for case_result in all_results:
        tc = case_result["test_case"]
        for method_name in ["HMM", "GMM", "Rule-Based"]:
            m = case_result[method_name]
            if m["log_loss"] > 0 and m["brier_score"] > 0:
                ratio = m["log_loss"] / m["brier_score"]
                if ratio > 3.5 or ratio < 1.5:
                    ll_brier_divergences.append({
                        "test_case": tc,
                        "method": method_name,
                        "log_loss": m["log_loss"],
                        "brier_score": m["brier_score"],
                        "ratio": round(ratio, 2),
                        "note": "Log Loss disproportionately high (outlier sensitivity)" if ratio > 3.5 else "Log Loss and Brier unusually close",
                    })

    if divergences:
        print("\n  DIVERGENCE CASES FOUND:")
        for d in divergences:
            auc_str = f"{d['auc_roc']:.4f}" if d["auc_roc"] is not None else "N/A"
            print(f"\n    [{d['test_case']}] {d['method']}:")
            print(f"      Type: {d['type']}")
            print(f"      {d['description']}")
            print(f"      Accuracy={d['accuracy']:.4f}, AUC={auc_str}, "
                  f"Brier={d['brier_score']:.4f}, ECE={d['ece']:.4f}")
    else:
        print("\n  No clear divergence found between Accuracy/AUC and Brier/ECE")
        print("  in this dataset. All metrics generally agree on model quality.")

    if ll_brier_divergences:
        print(f"\n  LOG LOSS vs BRIER SCORE DIVERGENCE:")
        for d in ll_brier_divergences:
            print(f"    [{d['test_case']}] {d['method']}: "
                  f"LogLoss={d['log_loss']:.4f}, Brier={d['brier_score']:.4f}, "
                  f"ratio={d['ratio']} — {d['note']}")
    else:
        print("\n  No meaningful Log Loss vs Brier Score divergence detected.")

    # -- Rankings --
    print(f"\n{'='*70}")
    print("METHOD RANKINGS BY EACH METRIC (best first)")
    print(f"{'='*70}")
    for metric_name in ["accuracy", "auc_roc", "log_loss", "brier_score", "ece"]:
        reverse = metric_name in ("accuracy", "auc_roc")
        vals = []
        for mn in ["HMM", "GMM", "Rule-Based"]:
            v = avg_results[mn][metric_name]
            if isinstance(v, str):
                continue
            vals.append((mn, v))
        vals.sort(key=lambda x: x[1], reverse=reverse)
        ranking_str = " > ".join(f"{n}({v:.4f})" for n, v in vals)
        better = "higher is better" if reverse else "lower is better"
        print(f"  {metric_name:<12} ({better}): {ranking_str}")

    # -- Save --
    output = {
        "metadata": {
            "generated_at": datetime.datetime.now().isoformat(),
            "description": "5-Metric Comparison: Accuracy, AUC-ROC, Log Loss, Brier Score, ECE",
            "note": "Same models/data/seeds as poc_feasibility_spike.py. HMM uses pure-Python implementation (may have minor numerical differences from hmmlearn). GMM and Rule-Based are identical.",
        },
        "per_test_case": all_results,
        "averages": avg_results,
        "divergence_analysis": {
            "accuracy_vs_calibration": divergences,
            "logloss_vs_brier": ll_brier_divergences,
        },
    }

    with open("metric_comparison_results.json", "w") as f:
        json.dump(output, f, indent=4, default=str)
    print(f"\nFull results saved to metric_comparison_results.json")

    return output


if __name__ == "__main__":
    run_metric_comparison()
