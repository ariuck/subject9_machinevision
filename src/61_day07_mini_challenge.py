from day07_paths import reset_generated_directory
import json
import shutil
from pathlib import Path

import cv2

from day07_anomaly_core import (
    anomaly_score,
    create_backbone,
    extract_features,
    load_reference,
)


# --------------------------------------------------
# 1. 입력 / 출력 경로
# --------------------------------------------------
NORMAL_DIR = Path(
    "samples/day07/test/normal"
)

OUTPUT_ROOT = Path(
    "samples/day07/mini_challenge"
)

VARIANT_DIR = (
    OUTPUT_ROOT
    / "variants"
)

REFERENCE_PATH = Path(
    "artifacts/day07/normal_reference.npz"
)

RULE_PATH = Path(
    "configs/day07_anomaly_rules.json"
)


# --------------------------------------------------
# 2. 학생이 직접 바꿀 조건
# --------------------------------------------------
DARK_ALPHA = 0.70
BLUR_KERNEL = 9
ROTATION_ANGLE = 12.0


# --------------------------------------------------
# 3. 이전 결과 초기화
# --------------------------------------------------
if OUTPUT_ROOT.exists():
    reset_generated_directory(
        OUTPUT_ROOT
    )

VARIANT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# --------------------------------------------------
# 4. 앞 Challenge와 다른 정상 이미지 선택
# --------------------------------------------------
normal_files = sorted(
    NORMAL_DIR.glob("*.png")
)

if len(normal_files) < 2:
    raise RuntimeError(
        "Mini Challenge용 Normal 이미지가 부족합니다."
    )

source_path = normal_files[1]

image = cv2.imread(
    str(source_path)
)

if image is None:
    raise FileNotFoundError(
        source_path
    )

height, width = image.shape[:2]


# --------------------------------------------------
# 5. Dark
# --------------------------------------------------
variant = cv2.convertScaleAbs(
    image,
    alpha=DARK_ALPHA,
    beta=0,
)

cv2.imwrite(
    str(
        VARIANT_DIR
        / "mini_dark.png"
    ),
    variant,
)


# --------------------------------------------------
# 6. Blur
# --------------------------------------------------
variant = cv2.GaussianBlur(
    image,
    (
        BLUR_KERNEL,
        BLUR_KERNEL,
    ),
    0,
)

cv2.imwrite(
    str(
        VARIANT_DIR
        / "mini_blur.png"
    ),
    variant,
)


# --------------------------------------------------
# 7. Rotation
# --------------------------------------------------
center = (
    width // 2,
    height // 2,
)

matrix = cv2.getRotationMatrix2D(
    center,
    ROTATION_ANGLE,
    1.0,
)

variant = cv2.warpAffine(
    image,
    matrix,
    (width, height),
    borderMode=cv2.BORDER_REFLECT,
)

cv2.imwrite(
    str(
        VARIANT_DIR
        / "mini_rotation.png"
    ),
    variant,
)


# --------------------------------------------------
# 8. Frozen Rule 불러오기
# --------------------------------------------------
rules = json.loads(
    RULE_PATH.read_text(
        encoding="utf-8"
    )
)

threshold = float(
    rules["anomaly_threshold"]
)

reference_vector, _ = load_reference(
    REFERENCE_PATH
)

model = create_backbone()


# --------------------------------------------------
# 9. 세 이미지 검사
# --------------------------------------------------
print("=" * 70)
print("DAY07 MINI CHALLENGE")
print("=" * 70)

print(
    "Source   :",
    source_path,
)

print(
    "Threshold:",
    threshold,
)

print()


# Agent predictions recorded before scoring; these are not the student's answers.
predictions = {"mini_dark.png": "FP", "mini_blur.png": "PASS", "mini_rotation.png": "FP"}
values = {"mini_dark.png": DARK_ALPHA, "mini_blur.png": BLUR_KERNEL, "mini_rotation.png": ROTATION_ANGLE}
rows = []
report_path = Path("reports/day07_mini_challenge.md")
report_path.parent.mkdir(exist_ok=True)
report_path.write_text(
    "# Day07 Mini Challenge\n\n에이전트의 실행 전 예상 (학생 개인 예상 아님):\n"
    + "\n".join(f"- {name}: {prediction}" for name, prediction in predictions.items()), encoding="utf-8")

for image_path in sorted(
    VARIANT_DIR.glob("*.png")
):
    vector, _ = extract_features(
        model,
        image_path,
    )

    score = anomaly_score(
        vector,
        reference_vector,
    )

    predicted = (
        "Anomaly"
        if score > threshold
        else "Normal"
    )

    result = (
        "FP"
        if predicted == "Anomaly"
        else "PASS"
    )

    rows.append({"file": image_path.name, "value": values[image_path.name],
                 "prediction": predictions[image_path.name], "anomaly_score": score,
                 "threshold": threshold, "predicted": predicted, "result": result})
    print(
        image_path.name,
        "score=",
        round(score, 6),
        "predicted=",
        predicted,
        "result=",
        result,
    )

import csv
with Path("reports/day07_mini_challenge_results.csv").open("w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
highest = max(rows, key=lambda r: r["anomaly_score"])
different = [r["file"] for r in rows if r["prediction"] != r["result"]]
lines = ["# Day07 Mini Challenge", "", f"Source: {source_path.as_posix()}",
         f"Threshold: {threshold}", "", "에이전트가 실행 전에 기록한 예상과 실제 측정 결과이다. 학생 개인의 예상으로 간주하지 않는다.", "",
         "| 변형 | 설정값 | 에이전트 사전 예상 | 실제 Score | 결과 |",
         "|---|---:|---|---:|---|"]
for row in rows:
    lines.append(f"| {row['file']} | {row['value']} | {row['prediction']} | {row['anomaly_score']:.6f} | {row['result']} |")
lines += ["", f"가장 Score가 높았던 조건: {highest['file']}",
          f"예상과 달랐던 조건: {', '.join(different) or '없음'}", "",
          "한 줄 정리: 정상 이미지라도 조건 변화가 정상 평균과의 특징 거리를 키울 수 있다. 설정 강도와 Score 관계는 원본 이미지에 따라서도 달라진다.", "",
          "학생 개인 예상과 해석은 직접 작성한다. 위 예상은 에이전트가 Score 계산 전에 기록했다."]
report_path.write_text("\n".join(lines), encoding="utf-8")
