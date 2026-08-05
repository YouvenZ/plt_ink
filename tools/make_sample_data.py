#!/usr/bin/env python3
"""Regenerate every bundled example dataset under ``sample_data/``.

The research templates in ``plt_ink_scripts/`` fall back to these files when
the user has not selected a data file, so each template previews and inserts
with zero configuration. Everything here is synthetic but shaped like the real
thing: imbalanced classes, censored survival times, heteroscedastic residuals,
proportional measurement bias, and so on — figures drawn from flat, well-
behaved noise look wrong to anyone who reads papers.

Deterministic: one master seed drives every dataset, so regenerating produces
byte-identical files. Requires numpy, pandas and matplotlib only.

    python tools/make_sample_data.py [--out DIR]
"""

import argparse
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

SEED = 20260728
HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUT = os.path.join(os.path.dirname(HERE), 'sample_data')

_written = []


def write(df, out_dir, name, **kwargs):
    """Write a CSV with stable formatting and record it for the summary."""
    path = os.path.join(out_dir, name)
    df.to_csv(path, index=False, lineterminator='\n', **kwargs)
    _written.append((name, df.shape))
    return path


def logistic(x):
    return 1.0 / (1.0 + np.exp(-x))


# ---------------------------------------------------------------------------
# Model evaluation
# ---------------------------------------------------------------------------

def make_training_runs(rng, out_dir):
    """Multi-seed training histories: loss, accuracy and LR per epoch."""
    models = [
        # name, final val acc, overfit strength, noise
        ('ResNet-50',   0.918, 0.030, 0.006),
        ('ViT-B/16',    0.936, 0.052, 0.009),
        ('ConvNeXt-T',  0.944, 0.021, 0.005),
    ]
    epochs = np.arange(1, 61)
    # Step schedule, decayed at epochs 25 / 40 / 52.
    lr = np.select([epochs < 25, epochs < 40, epochs < 52],
                   [1e-3, 3e-4, 1e-4], default=3e-5)

    rows = []
    for name, final, overfit, noise in models:
        for seed in range(5):
            offset = rng.normal(0, 0.006)          # per-seed skill
            speed = 13.0 * np.exp(rng.normal(0, 0.12))
            # Validation accuracy: exponential approach to the asymptote, plus
            # the small step-ups that follow each LR decay. The step-ups are
            # subtracted from the asymptote so the final value still lands on
            # `final` rather than overshooting it.
            target = final + offset - 0.015
            base = target - (target - 0.42) * np.exp(-epochs / speed)
            base += 0.010 * (epochs >= 25) + 0.005 * (epochs >= 40)
            val_acc = np.clip(base + rng.normal(0, noise, epochs.size), 0, 0.999)
            # Training accuracy pulls ahead and saturates -> generalisation gap.
            train_acc = np.clip(
                val_acc + overfit * (1 - np.exp(-epochs / 20.0))
                + rng.normal(0, noise * 0.6, epochs.size), 0, 0.9995)
            train_loss = 2.30 * np.exp(-epochs / (speed * 0.85)) + 0.05 \
                + rng.normal(0, 0.012, epochs.size)
            val_loss = 2.30 * np.exp(-epochs / speed) + 0.11 \
                + 0.9 * overfit * (1 - np.exp(-epochs / 18.0)) \
                + rng.normal(0, 0.020, epochs.size)
            for split, acc, loss in (('train', train_acc, train_loss),
                                     ('val', val_acc, val_loss)):
                rows.append(pd.DataFrame({
                    'model': name,
                    'seed': seed,
                    'epoch': epochs,
                    'split': split,
                    'loss': np.round(np.maximum(loss, 1e-3), 5),
                    'accuracy': np.round(acc, 5),
                    'lr': lr,
                }))
    write(pd.concat(rows, ignore_index=True), out_dir, 'training_runs.csv')


def make_predictions_binary(rng, out_dir):
    """Held-out scores for a screening task: 22 % prevalence, 3 models.

    Each model is built to hit a target AUC exactly: latent scores are normal
    with a separation d = sqrt(2)*Phi^-1(AUC), then converted to probabilities
    through the Bayes-optimal log-odds, which yields *calibrated* scores. The
    ``sharpness`` factor then inflates the log-odds, so ViT comes out
    over-confident and the reliability diagram has something real to show.
    """
    n = 900
    prevalence = 0.22
    y_true = (rng.random(n) < prevalence).astype(int)
    models = [
        # name, target AUC, sharpness (1.0 = calibrated, >1 = over-confident)
        ('Logistic Regression', 0.780, 1.00),
        ('Gradient Boosting',   0.868, 1.12),
        ('ViT-B/16',            0.918, 1.75),
    ]
    prior_odds = np.log(prevalence / (1 - prevalence))
    frames = []
    for name, auc, sharpness in models:
        d = np.sqrt(2.0) * _norm_ppf(auc)
        latent = rng.normal(0, 1, n) + d * y_true
        # Bayes-optimal log-odds for two unit-variance normals separated by d.
        logit = prior_odds + d * latent - 0.5 * d ** 2
        score = logistic(logit * sharpness)
        frames.append(pd.DataFrame({
            'model': name,
            'sample_id': np.arange(n),
            'y_true': y_true,
            'y_score': np.round(np.clip(score, 1e-5, 1 - 1e-5), 6),
        }))
    write(pd.concat(frames, ignore_index=True), out_dir,
          'predictions_binary.csv')


def _norm_ppf(p):
    """Inverse standard normal CDF (Acklam's rational approximation)."""
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00]
    p_low, p_high = 0.02425, 1 - 0.02425
    if p < p_low:
        q = np.sqrt(-2 * np.log(p))
        return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
               ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    if p > p_high:
        return -_norm_ppf(1 - p)
    q = p - 0.5
    r = q * q
    return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / \
           (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)


def make_predictions_multiclass(rng, out_dir):
    """Chest-radiograph style 6-class predictions with a realistic confusion
    structure (Nodule <-> Atelectasis and Effusion <-> Atelectasis mix up)."""
    classes = ['Normal', 'Pneumonia', 'Effusion', 'Nodule',
               'Atelectasis', 'Cardiomegaly']
    k = len(classes)
    prior = np.array([0.34, 0.14, 0.14, 0.12, 0.16, 0.10])
    # Row = true class, column = predicted class.
    conf = np.full((k, k), 0.012)
    np.fill_diagonal(conf, 0.0)
    conf[3, 4] = conf[4, 3] = 0.13          # nodule <-> atelectasis
    conf[2, 4] = conf[4, 2] = 0.10          # effusion <-> atelectasis
    conf[1, 2] = 0.07                       # pneumonia -> effusion
    conf[0, 1] = 0.04
    conf[5, 0] = 0.06
    for i in range(k):
        conf[i, i] = 1.0 - conf[i].sum()

    n = 1400
    y_true = rng.choice(k, size=n, p=prior)
    rows = []
    for i, t in enumerate(y_true):
        # Draw the prediction from the confusion row, then shape a softmax
        # vector whose argmax is that prediction — otherwise the argmax of a
        # Dirichlet centred on the diagonal is always correct and the
        # confusion matrix comes out perfectly diagonal.
        pred = int(rng.choice(k, p=conf[t]))
        probs = rng.dirichlet(conf[t] * 18 + 0.3)
        top = int(np.argmax(probs))
        probs[top], probs[pred] = probs[pred], probs[top]
        rows.append((i, classes[t], classes[pred]) + tuple(np.round(probs, 5)))
    cols = ['sample_id', 'y_true', 'y_pred'] + [f'p_{c}' for c in classes]
    write(pd.DataFrame(rows, columns=cols), out_dir,
          'predictions_multiclass.csv')


def make_benchmark_seeds(rng, out_dir):
    """Per-seed scores for 5 methods on 3 datasets — the input to a bar chart
    with significance brackets. Effect sizes are small on purpose."""
    methods = [('Baseline CNN', 0.0), ('+ Augmentation', 0.021),
               ('+ Self-supervised', 0.034), ('+ Ensemble', 0.041),
               ('Ours (full)', 0.052)]
    datasets = [('CIFAR-100', 0.742, 0.011), ('Tiny-ImageNet', 0.615, 0.014),
                ('CheXpert', 0.838, 0.008)]
    rows = []
    for ds, base, sd in datasets:
        for name, gain in methods:
            for seed in range(10):
                score = base + gain + rng.normal(0, sd)
                rows.append({
                    'dataset': ds, 'model': name, 'seed': seed,
                    'score': round(float(np.clip(score, 0, 1)), 5),
                    'f1': round(float(np.clip(score - 0.018 +
                                              rng.normal(0, sd * 0.6), 0, 1)), 5),
                })
    write(pd.DataFrame(rows), out_dir, 'benchmark_seeds.csv')


# ---------------------------------------------------------------------------
# Model analysis
# ---------------------------------------------------------------------------

def make_hparam_sweep(rng, out_dir):
    """Learning-rate x batch-size x weight-decay grid with a single optimum."""
    lrs = np.array([1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 3e-2])
    batches = np.array([16, 32, 64, 128, 256])
    wds = np.array([0.0, 1e-4, 1e-2])
    rows = []
    for lr in lrs:
        for bs in batches:
            for wd in wds:
                # Quadratic ridge in log-space around lr=1e-3, bs=64.
                d = ((np.log10(lr) + 3.0) / 1.05) ** 2 \
                    + ((np.log2(bs) - 6.0) / 2.6) ** 2
                penalty = 0.0 if wd == 1e-4 else (0.004 if wd == 0.0 else 0.011)
                val = 0.913 - 0.052 * d - penalty + rng.normal(0, 0.0035)
                if lr >= 3e-2:               # divergence at the top of the range
                    val = min(val, 0.32 + rng.normal(0, 0.02))
                rows.append({
                    'lr': lr, 'batch_size': int(bs), 'weight_decay': wd,
                    'val_score': round(float(np.clip(val, 0, 1)), 5),
                    'train_score': round(float(np.clip(val + 0.035 +
                                                       rng.normal(0, 0.004), 0, 1)), 5),
                })
    write(pd.DataFrame(rows), out_dir, 'hparam_sweep.csv')


def make_model_efficiency(rng, out_dir):
    """Accuracy / latency / size for a model zoo — the Pareto-front input."""
    zoo = [
        # name, family, params_M, accuracy, latency_ms
        ('MobileNetV3-S', 'CNN',        2.5, 0.674,  3.1),
        ('MobileNetV3-L', 'CNN',        5.4, 0.752,  5.4),
        ('EfficientNet-B0', 'CNN',      5.3, 0.771,  8.2),
        ('EfficientNet-B3', 'CNN',     12.0, 0.816, 21.4),
        ('ResNet-18',     'CNN',       11.7, 0.698,  6.3),
        ('ResNet-50',     'CNN',       25.6, 0.761, 14.8),
        ('ResNet-152',    'CNN',       60.2, 0.784, 38.9),
        ('ConvNeXt-T',    'CNN',       28.6, 0.821, 18.7),
        ('ConvNeXt-B',    'CNN',       88.6, 0.839, 46.2),
        ('DeiT-S',        'Transformer', 22.1, 0.798, 16.2),
        ('ViT-B/16',      'Transformer', 86.6, 0.812, 44.1),
        ('ViT-L/16',      'Transformer', 304.3, 0.828, 132.0),
        ('Swin-T',        'Transformer', 28.3, 0.813, 22.6),
        ('Swin-B',        'Transformer', 87.8, 0.835, 52.4),
        ('MLP-Mixer-B',   'MLP',        59.9, 0.766, 31.5),
        ('DistilBERT-ish','MLP',        22.4, 0.731, 12.9),
    ]
    rows = []
    for name, fam, params, acc, lat in zoo:
        rows.append({
            'model': name, 'family': fam, 'params_m': params,
            'accuracy': round(acc + rng.normal(0, 0.002), 5),
            'latency_ms': round(lat * float(np.exp(rng.normal(0, 0.03))), 3),
            'flops_g': round(params * 0.34 * float(np.exp(rng.normal(0, 0.15))), 3),
        })
    write(pd.DataFrame(rows), out_dir, 'model_efficiency.csv')


def make_learning_curve(rng, out_dir):
    """Score vs training-set size — a power law that saturates."""
    sizes = np.array([100, 250, 500, 1000, 2500, 5000, 12500, 25000, 50000])
    models = [('Scratch CNN', 0.902, 0.34, 0.62),
              ('ImageNet pre-trained', 0.928, 0.52, 0.45),
              ('Self-supervised pre-trained', 0.941, 0.63, 0.39)]
    rows = []
    for name, ceiling, floor, decay in models:
        for size in sizes:
            for seed in range(5):
                # score = ceiling - a * n^-decay
                score = ceiling - (ceiling - floor) * (size / 100.0) ** (-decay)
                score += rng.normal(0, 0.010 + 0.35 / np.sqrt(size))
                rows.append({'model': name, 'train_size': int(size),
                             'seed': seed,
                             'score': round(float(np.clip(score, 0, 1)), 5)})
    write(pd.DataFrame(rows), out_dir, 'learning_curve.csv')


def make_feature_importance(rng, out_dir):
    """Per-sample SHAP-style attributions for a clinical risk model."""
    features = [
        # name, importance, direction (sign of correlation with the outcome)
        ('Age',                  1.00,  1),
        ('NT-proBNP',            0.86,  1),
        ('Ejection fraction',    0.74, -1),
        ('Creatinine',           0.61,  1),
        ('Systolic BP',          0.48, -1),
        ('Diabetes',             0.41,  1),
        ('Haemoglobin',          0.35, -1),
        ('BMI',                  0.29, -1),
        ('Heart rate',           0.24,  1),
        ('Sodium',               0.20, -1),
        ('Smoking',              0.17,  1),
        ('Sex (male)',           0.14,  1),
        ('Albumin',              0.11, -1),
        ('Platelets',            0.07, -1),
        ('WBC count',            0.05,  1),
    ]
    n = 250
    rows = []
    for name, imp, sign in features:
        value = rng.normal(0, 1, n)              # standardised feature value
        # Attribution grows with the feature value, with saturation + noise.
        shap = sign * imp * np.tanh(value * 1.1) * 0.9 \
            + rng.normal(0, imp * 0.18 + 0.01, n)
        rows.append(pd.DataFrame({
            'feature': name,
            'sample_id': np.arange(n),
            'shap_value': np.round(shap, 5),
            'feature_value': np.round(value, 5),
        }))
    write(pd.concat(rows, ignore_index=True), out_dir,
          'feature_importance.csv')


def make_embedding_2d(rng, out_dir):
    """A t-SNE-like 2-D projection: 8 classes, two of which overlap."""
    classes = ['T-cell', 'B-cell', 'NK', 'Monocyte', 'Neutrophil',
               'Dendritic', 'Erythrocyte', 'Platelet']
    counts = [420, 330, 180, 300, 260, 140, 220, 150]
    # Cluster centres on a ring, with the two lymphoid classes placed close.
    angles = np.linspace(0, 2 * np.pi, len(classes), endpoint=False)
    centres = np.stack([14 * np.cos(angles), 14 * np.sin(angles)], axis=1)
    centres[1] = centres[0] + np.array([4.4, 2.1])      # B-cell near T-cell
    centres[2] = centres[0] + np.array([2.0, -5.2])     # NK near T-cell
    rows = []
    for i, (name, n) in enumerate(zip(classes, counts)):
        spread = 2.4 if i not in (0, 1, 2) else 3.1
        pts = centres[i] + rng.normal(0, spread, (n, 2))
        # Elongate each blob along a random axis, as t-SNE tends to.
        theta = rng.uniform(0, np.pi)
        rot = np.array([[np.cos(theta), -np.sin(theta)],
                        [np.sin(theta), np.cos(theta)]])
        pts = (pts - centres[i]) @ rot @ np.diag([1.5, 0.7]) @ rot.T + centres[i]
        # Misclassification: mostly among the three overlapping lymphoid types.
        err_p = 0.12 if i in (0, 1, 2) else 0.03
        pred = np.array([name] * n, dtype=object)
        flip = rng.random(n) < err_p
        neighbours = [0, 1, 2] if i in (0, 1, 2) else list(range(len(classes)))
        for j in np.flatnonzero(flip):
            choices = [c for c in neighbours if c != i]
            pred[j] = classes[int(rng.choice(choices))]
        rows.append(pd.DataFrame({
            'x': np.round(pts[:, 0], 4),
            'y': np.round(pts[:, 1], 4),
            'label': name,
            'pred': pred,
            'split': rng.choice(['train', 'test'], n, p=[0.7, 0.3]),
        }))
    df = pd.concat(rows, ignore_index=True).sample(frac=1, random_state=1)
    write(df.reset_index(drop=True), out_dir, 'embedding_2d.csv')


# ---------------------------------------------------------------------------
# Clinical / biostatistics
# ---------------------------------------------------------------------------

def make_survival(rng, out_dir):
    """Two-arm trial with Weibull event times and administrative censoring."""
    arms = [('Control', 1.00), ('Treatment', 0.62)]   # hazard ratio 0.62
    shape = 1.35
    scale = 42.0                                      # months
    follow_up = 48.0                                  # administrative cutoff
    rows = []
    pid = 0
    for arm, hr in arms:
        for _ in range(210):
            age = float(np.clip(rng.normal(63, 10), 30, 90))
            sex = 'M' if rng.random() < 0.56 else 'F'
            stage = int(rng.choice([1, 2, 3], p=[0.32, 0.41, 0.27]))
            # Covariate effects folded into the hazard.
            lp = np.log(hr) + 0.021 * (age - 63) + 0.34 * (stage - 2)
            t_event = scale * np.exp(-lp / shape) * rng.weibull(shape)
            # Loss to follow-up plus administrative censoring at 48 months.
            t_censor = min(rng.exponential(70.0), follow_up)
            time = min(t_event, t_censor)
            rows.append({
                'patient_id': f'P{pid:04d}', 'group': arm,
                'time': round(float(time), 3),
                'event': int(t_event <= t_censor),
                'age': round(age, 1), 'sex': sex, 'stage': stage,
            })
            pid += 1
    write(pd.DataFrame(rows), out_dir, 'survival.csv')


def make_forest_studies(rng, out_dir):
    """Meta-analysis of 15 trials in 3 subgroups, reported as hazard ratios."""
    subgroups = [('Early stage', -0.36), ('Advanced stage', -0.14),
                 ('Recurrent', -0.05)]
    names = ['Alvarez 2016', 'Bianchi 2017', 'Chen 2018', 'Dubois 2018',
             'Eriksen 2019', 'Ferreira 2019', 'Gupta 2020', 'Haas 2020',
             'Ibrahim 2021', 'Jensen 2021', 'Kowalski 2022', 'Liu 2022',
             'Moreau 2023', 'Nakamura 2023', 'Okafor 2024']
    rows = []
    idx = 0
    for sub, mu in subgroups:
        for _ in range(5):
            n_t = int(rng.integers(45, 420))
            n_c = int(rng.integers(45, 420))
            se = float(np.sqrt(4.0 / min(n_t, n_c)) * rng.uniform(0.8, 1.3))
            log_hr = rng.normal(mu, 0.16)             # between-study heterogeneity
            rows.append({
                'study': names[idx], 'subgroup': sub,
                'estimate': round(float(np.exp(log_hr)), 4),
                'ci_low': round(float(np.exp(log_hr - 1.96 * se)), 4),
                'ci_high': round(float(np.exp(log_hr + 1.96 * se)), 4),
                'n_treatment': n_t, 'n_control': n_c,
                'weight': round(float(1.0 / se ** 2), 4),
            })
            idx += 1
    write(pd.DataFrame(rows), out_dir, 'forest_studies.csv')


def make_method_agreement(rng, out_dir):
    """Manual vs automated LV ejection fraction — fixed and proportional bias."""
    n = 140
    truth = rng.uniform(22, 72, n)
    manual = truth + rng.normal(0, 2.4, n)
    # The automated reader compresses the scale by 10 % — a proportional bias
    # that a plain paired t-test misses but Bland-Altman shows immediately.
    # Weaker than this and the measurement noise swamps it, leaving the
    # template's proportional-bias test with nothing to detect.
    automated = truth * 0.90 + 0.19 + rng.normal(0, 2.6, n)
    write(pd.DataFrame({
        'subject': [f'S{i:03d}' for i in range(n)],
        'method_a': np.round(manual, 3),
        'method_b': np.round(automated, 3),
        'reader': rng.choice(['Reader 1', 'Reader 2'], n),
    }), out_dir, 'method_agreement.csv')


def make_differential_expression(rng, out_dir):
    """RNA-seq style results: 4000 genes, ~3 % genuinely differential."""
    n = 4000
    base_mean = np.exp(rng.normal(4.2, 1.9, n))
    is_de = rng.random(n) < 0.032
    log2fc = np.where(
        is_de,
        rng.normal(0, 1.9, n) + np.sign(rng.normal(0, 1, n)) * 1.1,
        rng.normal(0, 0.28, n),
    )
    # Larger counts -> more power, so p-values track |fc| and expression. The
    # divisor is tuned so the strongest hits land near -log10(p) ~ 40, the
    # range a real RNA-seq volcano spans; any tighter and p underflows to the
    # 1e-300 floor and the whole top of the plot flattens into one line.
    stat = np.abs(log2fc) * np.sqrt(np.log1p(base_mean)) / 1.15
    # Soft-saturate rather than hard-clip: a hard cap would stack the top hits
    # into a visible horizontal line across the volcano.
    stat = 13.0 * np.tanh(stat / 13.0)
    pvalue = np.clip(2 * _norm_sf(stat) * rng.uniform(0.4, 1.6, n),
                     1e-300, 1.0)
    order = np.argsort(pvalue)
    ranks = np.empty(n, dtype=int)
    ranks[order] = np.arange(1, n + 1)
    padj = np.clip(pvalue * n / ranks, 0, 1)          # Benjamini-Hochberg
    padj = np.minimum.accumulate(padj[order][::-1])[::-1][np.argsort(order)]

    prefixes = ['ACTB', 'BRCA', 'CDK', 'EGFR', 'FOX', 'GATA', 'HIF', 'IL',
                'JAK', 'KRAS', 'LDH', 'MYC', 'NFK', 'PTEN', 'RAS', 'STAT',
                'TP', 'VEGF', 'WNT', 'ZEB']
    genes = [f'{prefixes[i % len(prefixes)]}{i // len(prefixes) + 1}'
             for i in range(n)]
    write(pd.DataFrame({
        'gene': genes,
        'base_mean': np.round(base_mean, 3),
        'log2fc': np.round(log2fc, 5),
        'pvalue': pvalue,
        'padj': padj,
    }), out_dir, 'differential_expression.csv')


def _norm_cdf(x):
    """Standard normal CDF via the error function (no scipy dependency)."""
    return 0.5 * (1.0 + np.vectorize(_erf)(x / np.sqrt(2.0)))


def _norm_sf(z):
    """Upper tail P(Z > z), usable far into the tail.

    The Abramowitz & Stegun erf approximation is only accurate to ~1e-7, so
    ``1 - cdf`` collapses to exactly zero beyond z ~ 5.5 — which would push
    every strong hit to the 1e-300 floor. Past that point switch to the
    asymptotic expansion, which stays accurate down to ~1e-40.
    """
    z = np.asarray(z, float)
    near = 1.0 - _norm_cdf(z)
    with np.errstate(over='ignore', divide='ignore', invalid='ignore'):
        density = np.exp(-0.5 * z ** 2) / np.sqrt(2 * np.pi)
        far = density / np.where(z > 0, z, 1.0) * (
            1 - 1 / z ** 2 + 3 / z ** 4)
    return np.where(z > 5.0, far, near)


def _erf(x):
    """Abramowitz & Stegun 7.1.26 — plenty accurate for synthetic data."""
    sign = 1.0 if x >= 0 else -1.0
    x = abs(x)
    t = 1.0 / (1.0 + 0.3275911 * x)
    y = 1.0 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t
                - 0.284496736) * t + 0.254829592) * t * np.exp(-x * x)
    return sign * y


def make_dose_response(rng, out_dir):
    """Three compounds, 8 doses, 3 replicates — a 4PL curve each."""
    compounds = [('Compound A', 0.42, 1.35), ('Compound B', 3.80, 1.05),
                 ('Compound C', 24.0, 1.90)]     # (name, EC50 uM, Hill slope)
    doses = np.array([0.003, 0.01, 0.03, 0.1, 0.32, 1.0, 3.2, 10.0, 32.0, 100.0])
    rows = []
    for name, ec50, hill in compounds:
        for dose in doses:
            for rep in range(1, 4):
                resp = 4.0 + (98.0 - 4.0) / (1.0 + (ec50 / dose) ** hill)
                # Noise grows with the response (typical of plate assays).
                resp += rng.normal(0, 1.8 + 0.035 * resp)
                rows.append({'compound': name, 'dose': dose, 'replicate': rep,
                             'response': round(float(resp), 3)})
    write(pd.DataFrame(rows), out_dir, 'dose_response.csv')


# ---------------------------------------------------------------------------
# Distributions & general statistics
# ---------------------------------------------------------------------------

def make_group_measurements(rng, out_dir):
    """Four dose groups with a monotone effect and unequal variance."""
    groups = [('Vehicle', 42.0, 6.0, 34), ('Low dose', 45.5, 6.4, 31),
              ('Mid dose', 51.5, 8.1, 33), ('High dose', 58.0, 11.0, 29)]
    rows = []
    for name, mu, sd, n in groups:
        vals = rng.normal(mu, sd, n)
        # A couple of genuine outliers in the top group.
        if name == 'High dose':
            vals[:2] += rng.uniform(18, 26, 2)
        for i, v in enumerate(vals):
            rows.append({'group': name, 'subject': f'{name[:1]}{i:02d}',
                         'value': round(float(v), 3),
                         'sex': 'M' if rng.random() < 0.5 else 'F'})
    write(pd.DataFrame(rows), out_dir, 'group_measurements.csv')


def make_paired_prepost(rng, out_dir):
    """Pre/post measurements per subject in two arms — the slope-plot input."""
    rows = []
    for arm, effect in (('Placebo', 1.2), ('Active', 9.4)):
        for i in range(26):
            baseline = rng.normal(58, 9)
            post = baseline + effect + rng.normal(0, 5.2)
            sid = f'{arm[:3].upper()}{i:02d}'
            rows.append({'subject': sid, 'group': arm, 'timepoint': 'Pre',
                         'value': round(float(baseline), 3)})
            rows.append({'subject': sid, 'group': arm, 'timepoint': 'Post',
                         'value': round(float(post), 3)})
    write(pd.DataFrame(rows), out_dir, 'paired_prepost.csv')


def make_regression_xy(rng, out_dir):
    """Biomarker vs age in two cohorts — different slopes, mild spread."""
    rows = []
    for group, intercept, slope, sd in (('Healthy', 12.0, 0.084, 1.5),
                                        ('Disease', 15.5, 0.191, 2.4)):
        n = 160
        age = np.clip(rng.normal(55, 14, n), 20, 89)
        y = intercept + slope * age + rng.normal(0, sd, n)
        rows.append(pd.DataFrame({
            'x': np.round(age, 2), 'y': np.round(y, 4), 'group': group,
        }))
    write(pd.concat(rows, ignore_index=True), out_dir, 'regression_xy.csv')


def make_pred_vs_measured(rng, out_dir):
    """Regression model outputs with heteroscedastic, slightly biased error."""
    rows = []
    for split, n, noise in (('train', 340, 0.55), ('val', 120, 0.78),
                            ('test', 120, 0.86)):
        y = rng.uniform(2.0, 42.0, n)
        # Shrinkage toward the mean plus error growing with magnitude.
        pred = 1.6 + 0.94 * y + rng.normal(0, noise + 0.045 * y, n)
        rows.append(pd.DataFrame({
            'sample': [f'{split[:2]}{i:04d}' for i in range(n)],
            'y_true': np.round(y, 4), 'y_pred': np.round(pred, 4),
            'split': split,
        }))
    write(pd.concat(rows, ignore_index=True), out_dir, 'pred_vs_measured.csv')


def make_omics_matrix(rng, out_dir):
    """Wide numeric matrix with three correlated blocks — clustermap input."""
    blocks = {
        'Inflammation': ['IL6', 'TNFa', 'CRP', 'IL1B', 'IL10', 'IFNg'],
        'Metabolic': ['Glucose', 'Insulin', 'HbA1c', 'Triglycerides',
                      'HDL', 'LDL', 'BMI'],
        'Cardiac': ['Troponin', 'NTproBNP', 'CK_MB', 'LVEF', 'LVMass'],
        'Renal': ['Creatinine', 'eGFR', 'Urea', 'Cystatin_C'],
    }
    n = 150
    data = {}
    for block, names in blocks.items():
        latent = rng.normal(0, 1, n)
        for i, name in enumerate(names):
            loading = rng.uniform(0.55, 0.92)
            # A few members load negatively (HDL, LVEF, eGFR are protective).
            if name in ('HDL', 'LVEF', 'eGFR', 'IL10'):
                loading = -loading
            data[name] = np.round(
                loading * latent + np.sqrt(1 - loading ** 2) * rng.normal(0, 1, n), 5)
    df = pd.DataFrame(data)
    df.insert(0, 'sample_id', [f'S{i:03d}' for i in range(n)])
    df.insert(1, 'group', rng.choice(['Case', 'Control'], n, p=[0.45, 0.55]))
    write(df, out_dir, 'omics_matrix.csv')


# ---------------------------------------------------------------------------
# Imaging & signals
# ---------------------------------------------------------------------------

CASES = ['case01', 'case02', 'case03', 'case04']
STRUCTURES = ['Liver', 'Spleen', 'Kidney L', 'Kidney R', 'Tumour']


def make_segmentation_metrics(rng, out_dir):
    """Per-case, per-structure overlap metrics for 3 segmentation models."""
    models = [('U-Net', 0.0), ('Attention U-Net', 0.021), ('nnU-Net', 0.043)]
    # Large organs segment well; the tumour is the hard, high-variance class.
    structures = [('Liver', 0.931, 0.021, 4.1), ('Spleen', 0.912, 0.028, 5.0),
                  ('Kidney L', 0.895, 0.034, 6.2), ('Kidney R', 0.889, 0.036, 6.6),
                  ('Tumour', 0.702, 0.098, 17.5)]
    rows = []
    for case in range(40):
        difficulty = rng.normal(0, 0.022)      # a shared per-case offset
        for model, gain in models:
            for struct, base, sd, hd in structures:
                dice = np.clip(base + gain - difficulty + rng.normal(0, sd), 0, 0.999)
                hd95 = max(0.6, hd * (1.6 - dice) * float(np.exp(rng.normal(0, 0.25))))
                rows.append({
                    'case_id': f'CT{case:03d}', 'model': model,
                    'structure': struct,
                    'dice': round(float(dice), 5),
                    'hd95': round(float(hd95), 4),
                    'assd': round(float(hd95 / 4.2 * np.exp(rng.normal(0, 0.15))), 4),
                })
    write(pd.DataFrame(rows), out_dir, 'segmentation_metrics.csv')


def make_signal_timeseries(rng, out_dir):
    """Three vibration channels: harmonics, a fault tone and 1/f noise."""
    fs = 1000.0
    n = 4096
    t = np.arange(n) / fs
    channels = [
        # name, base frequency, harmonics, fault tone, noise
        ('Bearing A', 50.0, (2, 3), None, 0.35),
        ('Bearing B', 50.0, (2, 3), 213.0, 0.35),
        ('Gearbox',   120.0, (2,), 372.0, 0.55),
    ]
    rows = []
    for name, f0, harmonics, fault, noise in channels:
        sig = 1.0 * np.sin(2 * np.pi * f0 * t + rng.uniform(0, 2 * np.pi))
        for h in harmonics:
            sig += (0.9 / h) * np.sin(2 * np.pi * f0 * h * t + rng.uniform(0, 2 * np.pi))
        if fault is not None:
            # The fault tone ramps in over the second half of the record.
            envelope = np.clip((t - t[-1] / 2) / (t[-1] / 2), 0, 1)
            sig += 0.55 * envelope * np.sin(2 * np.pi * fault * t)
        # 1/f noise: filtered white noise in the frequency domain.
        white = rng.normal(0, 1, n)
        spec = np.fft.rfft(white)
        freqs = np.fft.rfftfreq(n, 1 / fs)
        spec[1:] /= np.sqrt(freqs[1:])
        pink = np.fft.irfft(spec, n)
        pink = pink / np.std(pink) * noise
        rows.append(pd.DataFrame({
            'channel': name, 't': np.round(t, 6),
            'amplitude': np.round(sig + pink, 6),
        }))
    write(pd.concat(rows, ignore_index=True), out_dir, 'signal_timeseries.csv')


def _phantom(rng, size=192):
    """A CT-like abdominal slice: body ellipse, organs, texture, noise."""
    yy, xx = np.mgrid[0:size, 0:size]
    cx = cy = size / 2.0

    def ellipse(x0, y0, rx, ry, angle=0.0):
        a = np.deg2rad(angle)
        dx, dy = xx - x0, yy - y0
        u = dx * np.cos(a) + dy * np.sin(a)
        v = -dx * np.sin(a) + dy * np.cos(a)
        return (u / rx) ** 2 + (v / ry) ** 2 <= 1.0

    img = np.zeros((size, size), float)
    body = ellipse(cx, cy, size * 0.42, size * 0.33)
    img[body] = 0.34                                   # soft tissue
    fat = body & ~ellipse(cx, cy, size * 0.385, size * 0.295)
    img[fat] = 0.22
    liver = ellipse(cx - size * 0.15, cy - size * 0.05, size * 0.20, size * 0.16, 15)
    liver &= body
    img[liver] = 0.55
    spleen = ellipse(cx + size * 0.21, cy - size * 0.02, size * 0.09, size * 0.07, -20)
    spleen &= body
    img[spleen] = 0.50
    kid_l = ellipse(cx + size * 0.17, cy + size * 0.14, size * 0.062, size * 0.045, 25)
    kid_r = ellipse(cx - size * 0.17, cy + size * 0.14, size * 0.062, size * 0.045, -25)
    img[kid_l | kid_r] = 0.47
    spine = ellipse(cx, cy + size * 0.24, size * 0.055, size * 0.045)
    img[spine & body] = 0.95                            # bone

    # A tumour with a random position inside the liver.
    ty = cy - size * 0.05 + rng.uniform(-0.05, 0.05) * size
    tx = cx - size * 0.15 + rng.uniform(-0.06, 0.06) * size
    tr = size * rng.uniform(0.032, 0.055)
    tumour = ellipse(tx, ty, tr, tr * rng.uniform(0.75, 1.15),
                     rng.uniform(0, 180)) & liver
    img[tumour] = 0.68

    # Parenchymal texture, then acquisition noise.
    texture = rng.normal(0, 1, (size, size))
    k = np.array([[1, 2, 1], [2, 4, 2], [1, 2, 1]], float)
    k /= k.sum()
    for _ in range(3):                                  # cheap Gaussian blur
        texture = sum(
            np.roll(np.roll(texture, dy - 1, 0), dx - 1, 1) * k[dy, dx]
            for dy in range(3) for dx in range(3))
    img = img + texture * 0.035 * body
    img += rng.normal(0, 0.012, (size, size))
    return np.clip(img, 0, 1), liver.astype(np.uint8), tumour.astype(np.uint8)


def _perturb_mask(rng, mask, dilate_bias=0.0, drop=0.0, jitter=0.55):
    """Produce a plausible predicted mask: boundary jitter + optional dropout.

    The jitter has to be strong enough that the false-positive/false-negative
    error map has something to show — a prediction at Dice 0.99 makes that
    panel look broken rather than impressive.
    """
    m = mask.astype(float)
    k = np.array([[0.5, 1, 0.5], [1, 2, 1], [0.5, 1, 0.5]])
    k /= k.sum()
    blurred = sum(np.roll(np.roll(m, dy - 1, 0), dx - 1, 1) * k[dy, dx]
                  for dy in range(3) for dx in range(3))
    for _ in range(3):
        blurred = sum(np.roll(np.roll(blurred, dy - 1, 0), dx - 1, 1) * k[dy, dx]
                      for dy in range(3) for dx in range(3))
    # Correlated noise: smooth blobs of error along the boundary, not speckle.
    noise = rng.normal(0, jitter, m.shape)
    for _ in range(4):
        noise = sum(np.roll(np.roll(noise, dy - 1, 0), dx - 1, 1) * k[dy, dx]
                    for dy in range(3) for dx in range(3))
    noise *= jitter / (noise.std() or 1.0)
    # Gate the noise to the blurred boundary band. Applied globally it flips
    # patches of background far from the object into false positives, which
    # collapses Dice and looks nothing like a real segmentation error.
    boundary = 4.0 * blurred * (1.0 - blurred)
    pred = (blurred + noise * boundary > 0.5 - dilate_bias).astype(np.uint8)
    if drop > 0 and pred.any():
        # Knock out a blob to create a realistic false-negative region.
        ys, xs = np.nonzero(pred)
        i = int(rng.integers(len(ys)))
        yy, xx = np.mgrid[0:m.shape[0], 0:m.shape[1]]
        r = np.sqrt(m.sum()) * drop
        pred[((yy - ys[i]) ** 2 + (xx - xs[i]) ** 2) <= r ** 2] = 0
    return pred


def _gradcam(rng, tumour, size):
    """A saliency map peaked on the lesion, with distractor activations."""
    yy, xx = np.mgrid[0:size, 0:size]
    cam = np.zeros((size, size), float)
    if tumour.any():
        ys, xs = np.nonzero(tumour)
        cy, cx = ys.mean(), xs.mean()
        sigma = max(6.0, np.sqrt(tumour.sum()) * 0.9)
        cam += np.exp(-((yy - cy) ** 2 + (xx - cx) ** 2) / (2 * sigma ** 2))
    for _ in range(3):                                   # spurious attention
        cy, cx = rng.uniform(size * 0.2, size * 0.8, 2)
        sigma = rng.uniform(8, 18)
        cam += rng.uniform(0.15, 0.4) * np.exp(
            -((yy - cy) ** 2 + (xx - cx) ** 2) / (2 * sigma ** 2))
    cam += rng.normal(0, 0.02, (size, size))
    cam -= cam.min()
    return cam / (cam.max() or 1.0)


def make_images(rng, out_dir):
    """Write the imaging assets: slice, ground truth, prediction, Grad-CAM."""
    img_dir = os.path.join(out_dir, 'images')
    os.makedirs(img_dir, exist_ok=True)
    size = 192
    rows = []
    for i, case in enumerate(CASES):
        img, liver, tumour = _phantom(rng, size)
        # Ground truth: 1 = liver, 2 = tumour (a small multi-label mask).
        gt = liver.copy()
        gt[tumour > 0] = 2
        # The liver is the easy class; the small tumour is where models fail,
        # so it gets stronger jitter and, in one case, a dropped region.
        pred_liver = _perturb_mask(rng, liver, dilate_bias=0.06, jitter=0.62)
        pred_tumour = _perturb_mask(rng, tumour, dilate_bias=-0.05,
                                    jitter=0.85,
                                    drop=0.45 if i == 2 else 0.0)
        pred = pred_liver.copy()
        pred[pred_tumour > 0] = 2
        cam = _gradcam(rng, tumour, size)

        plt.imsave(os.path.join(img_dir, f'{case}_image.png'), img,
                   cmap='gray', vmin=0, vmax=1)
        plt.imsave(os.path.join(img_dir, f'{case}_mask_gt.png'), gt,
                   cmap='gray', vmin=0, vmax=2)
        plt.imsave(os.path.join(img_dir, f'{case}_mask_pred.png'), pred,
                   cmap='gray', vmin=0, vmax=2)
        plt.imsave(os.path.join(img_dir, f'{case}_cam.png'), cam,
                   cmap='gray', vmin=0, vmax=1)
        _written.append((f'images/{case}_*.png', (size, size)))

        inter = float(((gt > 0) & (pred > 0)).sum())
        dice = 2 * inter / float((gt > 0).sum() + (pred > 0).sum())
        rows.append({'case_id': case, 'dice': round(dice, 4),
                     'lesion_px': int(tumour.sum()),
                     'label_1': 'Liver', 'label_2': 'Tumour'})
    # An index so templates can enumerate cases without globbing.
    write(pd.DataFrame(rows), out_dir, os.path.join('images', 'cases.csv'))


# ---------------------------------------------------------------------------

BUILDERS = [
    make_training_runs, make_predictions_binary, make_predictions_multiclass,
    make_benchmark_seeds, make_hparam_sweep, make_model_efficiency,
    make_learning_curve, make_feature_importance, make_embedding_2d,
    make_survival, make_forest_studies, make_method_agreement,
    make_differential_expression, make_dose_response, make_group_measurements,
    make_paired_prepost, make_regression_xy, make_pred_vs_measured,
    make_omics_matrix, make_segmentation_metrics, make_signal_timeseries,
    make_images,
]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', default=DEFAULT_OUT,
                    help='output directory (default: sample_data/)')
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    # One stream per builder, derived from the master seed, so adding a new
    # dataset does not change the contents of the existing ones.
    root = np.random.SeedSequence(SEED)
    for builder, child in zip(BUILDERS, root.spawn(len(BUILDERS))):
        builder(np.random.default_rng(child), args.out)

    print(f'Wrote {len(_written)} datasets to {args.out}')
    for name, shape in _written:
        print(f'  {name:<34} {shape}')


if __name__ == '__main__':
    main()
