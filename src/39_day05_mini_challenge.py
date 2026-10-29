from pathlib import Path
from itertools import combinations
import csv
import json
import sys

import numpy as np

from day05_logo_features import (
    prepare_reference,
    measure_target,
)


# 기본은 samples/day05/mini_challenge 를 사용합니다.
# 다른 폴더로 시험할 때만: python src/39_day05_mini_challenge.py <폴더>
ROOT = Path(
    sys.argv[1] if len(sys.argv) > 1 else "samples/day05/mini_challenge"
)

REFERENCE_PATH = (
    ROOT
    / "reference/reference_label.jpg"
)

CALIBRATION_DIR = (
    ROOT
    / "calibration"
)

TEST_DIR = (
    ROOT
    / "test"
)

RESULT_DIR = (
    ROOT
    / "results"
)

# Rule에 사용할 수 있는 Feature (Position Error, Scale Ratio는 사용하지 않음)
FEATURES = [
    "template_score",
    "sift_good_matches",
    "inlier_ratio",
]


def list_images(folder):

    return sorted(
        p for p in folder.glob("*")
        if p.suffix.lower() in (".jpg", ".jpeg", ".png")
    )


def measure_folder(folder, actual, reference_data):

    rows = []

    for path in list_images(folder):

        result = measure_target(
            path,
            reference_data,
        )

        rows.append({
            "file": path.name,
            "actual": actual,
            "template_score": round(float(result["template_score"]), 6),
            "sift_good_matches": int(result["sift_good_matches"]),
            "homography_found": int(bool(result["homography_found"])),
            "homography_inliers": int(result["homography_inliers"]),
            "inlier_ratio": round(float(result["inlier_ratio"]), 6),
        })

    return rows


def predict(row, rule):

    # NG를 Positive로 봅니다. 하나라도 기준에 못 미치면 NG
    reasons = []

    if row["homography_found"] != 1:
        reasons.append("HOMOGRAPHY_NOT_FOUND")

    for feature, minimum in rule.items():
        if row[feature] < minimum:
            reasons.append(f"LOW_{feature.upper()}")

    return ("NG" if reasons else "OK"), ";".join(reasons)


def error_type(actual, predicted):

    if actual == "NG" and predicted == "NG":
        return "TP"
    if actual == "OK" and predicted == "OK":
        return "TN"
    if actual == "OK" and predicted == "NG":
        return "FP"
    return "FN"


def count_errors(rows, rule):

    counts = {"TP": 0, "TN": 0, "FP": 0, "FN": 0}

    for row in rows:
        predicted, _ = predict(row, rule)
        counts[error_type(row["actual"], predicted)] += 1

    return counts


def make_candidates(values, count=15, integer=False):

    # 35_day05_analyze_calibration.py 와 같은 방식:
    # 측정값의 최소값~최대값 사이를 15개로 나눕니다.
    low, high = min(values), max(values)

    if low == high:
        return [low]

    candidates = np.linspace(low, high, count)

    if integer:
        return sorted({int(round(v)) for v in candidates})

    return sorted({round(float(v), 4) for v in candidates})


def write_csv(path, rows):

    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


# --------------------------------------------------
# TODO 1
#
# Reference를 준비합니다.
#
# prepare_reference()를 사용합니다.
# --------------------------------------------------

reference_data = prepare_reference(
    REFERENCE_PATH
)

print("Reference:", REFERENCE_PATH)


# --------------------------------------------------
# TODO 2
#
# calibration/ok
# calibration/ng
#
# 이미지를 모두 읽어서 측정합니다.
# --------------------------------------------------

calibration_rows = (
    measure_folder(CALIBRATION_DIR / "ok", "OK", reference_data)
    + measure_folder(CALIBRATION_DIR / "ng", "NG", reference_data)
)

if not calibration_rows:
    raise RuntimeError(
        f"Calibration 이미지가 없습니다: {CALIBRATION_DIR}/ok, {CALIBRATION_DIR}/ng"
    )

print()
print("Calibration 측정값")
for row in calibration_rows:
    print(
        f"  {row['file']:16s} {row['actual']:2s}"
        f"  template {row['template_score']:.4f}"
        f"  sift {row['sift_good_matches']:4d}"
        f"  inlier {row['homography_inliers']:4d}"
        f"  ratio {row['inlier_ratio']:.4f}"
        f"  found {row['homography_found']}"
    )

write_csv(RESULT_DIR / "calibration_measurements.csv", calibration_rows)


# --------------------------------------------------
# TODO 3
#
# OK와 NG 측정값을 비교합니다.
#
# 어떤 Feature가 구분에 도움이 되는지 확인합니다.
# OK 최소값 > NG 최대값이면 두 분포가 겹치지 않습니다.
# --------------------------------------------------

print()
print("Feature 비교 (OK 최소 / NG 최대 → 겹치지 않으면 구분 가능)")

for feature in FEATURES:

    ok_values = [r[feature] for r in calibration_rows if r["actual"] == "OK"]
    ng_values = [r[feature] for r in calibration_rows if r["actual"] == "NG"]

    if not ok_values or not ng_values:
        continue

    gap = min(ok_values) - max(ng_values)

    print(
        f"  {feature:18s} OK {min(ok_values):.4f}~{max(ok_values):.4f}"
        f"  NG {min(ng_values):.4f}~{max(ng_values):.4f}"
        f"  → {'겹치지 않음' if gap > 0 else '겹침'} (gap {gap:+.4f})"
    )


# --------------------------------------------------
# TODO 4
#
# Calibration 결과를 보고 Threshold를 결정합니다.
#
# Feature 2개 조합마다 Threshold 후보를 시험하고
# FN(놓친 불량) → 전체 오류 → FP → 작은 기준값 순으로 고릅니다.
# (35_day05_analyze_calibration.py 와 같은 정렬 기준)
#
# 숫자를 임의로 정하지 않습니다.
# --------------------------------------------------

best = None

for pair in combinations(FEATURES, 2):

    candidate_lists = [
        make_candidates(
            [r[f] for r in calibration_rows],
            integer=(f == "sift_good_matches"),
        )
        for f in pair
    ]

    for a in candidate_lists[0]:
        for b in candidate_lists[1]:

            rule = {pair[0]: a, pair[1]: b}
            counts = count_errors(calibration_rows, rule)
            key = (counts["FN"], counts["FP"] + counts["FN"], counts["FP"], a, b)

            if best is None or key < best[0]:
                best = (key, rule, counts)

_, final_rule, calibration_counts = best

print()
print("선택한 Rule:", " AND ".join(f"{k} >= {v}" for k, v in final_rule.items()))
print("Calibration:", calibration_counts)


# --------------------------------------------------
# TODO 5
#
# 결정한 Rule을 고정합니다.
#
# Test를 시작한 뒤에는 Threshold를 수정하지 않습니다.
# --------------------------------------------------

frozen = {
    "baseline_version": "day05-mini-challenge-v1.0",
    "positive_class": "NG",
    "reference": str(REFERENCE_PATH),
    "required_rules": {
        "homography_found": True,
        **{f"{k}_min": v for k, v in final_rule.items()},
    },
    "calibration_result": calibration_counts,
}

RESULT_DIR.mkdir(parents=True, exist_ok=True)

with open(RESULT_DIR / "mini_challenge_rule.json", "w", encoding="utf-8") as f:
    json.dump(frozen, f, ensure_ascii=False, indent=2)

print("Rule 저장:", RESULT_DIR / "mini_challenge_rule.json")


# --------------------------------------------------
# TODO 6
#
# test/ok
# test/ng
#
# 이미지에 같은 Rule을 적용합니다.
# --------------------------------------------------

test_rows = (
    measure_folder(TEST_DIR / "ok", "OK", reference_data)
    + measure_folder(TEST_DIR / "ng", "NG", reference_data)
)

if not test_rows:
    raise RuntimeError(
        f"Test 이미지가 없습니다: {TEST_DIR}/ok, {TEST_DIR}/ng"
    )


# --------------------------------------------------
# TODO 7
#
# Actual과 Predicted를 비교합니다.
#
# TP / TN / FP / FN 을 확인합니다.
# --------------------------------------------------

test_counts = {"TP": 0, "TN": 0, "FP": 0, "FN": 0}

print()
print("Test 결과")

for row in test_rows:

    predicted, reason = predict(row, final_rule)
    kind = error_type(row["actual"], predicted)
    test_counts[kind] += 1

    row["predicted"] = predicted
    row["error_type"] = kind
    row["ng_reason"] = reason

    print(
        f"  {row['file']:16s} actual {row['actual']:2s} → {predicted:2s}  {kind}"
        f"  sift {row['sift_good_matches']:4d}  ratio {row['inlier_ratio']:.4f}"
        f"  template {row['template_score']:.4f}  {reason}"
    )

write_csv(RESULT_DIR / "test_results.csv", test_rows)

total = sum(test_counts.values())
accuracy = (test_counts["TP"] + test_counts["TN"]) / total

print()
print("TP:", test_counts["TP"], " TN:", test_counts["TN"],
      " FP:", test_counts["FP"], " FN:", test_counts["FN"])
print(f"Accuracy: {accuracy:.4f}")
print("결과 폴더:", RESULT_DIR)
