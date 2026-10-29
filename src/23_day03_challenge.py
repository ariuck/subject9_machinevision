from pathlib import Path
import csv

import cv2


# ============================================================
# Day 03 Mini Challenge — 빨간 병뚜껑 존재 여부 검사 (C. 색상 객체 검사)
#
# 검사 대상 : 콜라병 입구의 빨간 병뚜껑
# 정상(OK)  : 병 입구에 빨간 병뚜껑이 있음
# 불량(NG)  : 병뚜껑을 딴 상태(빨간 뚜껑 없음)
# 눈으로 보이는 차이 : 병 입구의 선명한 빨간색 영역이 있는가 / 없는가
#
# 이미지 : samples/sample.mp4(1일차 영상)에서 Frame을 저장해 사용
#   ok_01(#75)  / ng_01(#210) → Feature 비교와 Rule 결정
#   ok_02(#105) / ng_02(#225) → 확인용
#   ok_03(#150) / ng_03(#195) → 확인용 (ok_03은 병따개가 뚜껑을 일부 가림)
# ============================================================

input_dir = Path(
    "samples/day03/challenge"
)

output_dir = Path(
    "outputs/day03/challenge"
)

report_path = Path(
    "reports/day03_challenge_results.csv"
)

output_dir.mkdir(
    parents=True,
    exist_ok=True,
)

REFERENCE_OK = "ok_01.jpg"
REFERENCE_NG = "ng_01.jpg"
TEST_IMAGES = [
    ("ok_02.jpg", "OK"),
    ("ng_02.jpg", "NG"),
    ("ok_03.jpg", "OK"),
    ("ng_03.jpg", "NG"),
]

# 전체 이미지 면적의 0.05%보다 작은 빨간 조각은 Noise로 보고 개수에서 제외
MIN_CONTOUR_AREA_RATIO = 0.0005


# ------------------------------------------
# TODO 1
# 검사 문제에 맞는 전처리를 선택합니다.
#
# 색상이 검사 기준이므로 Gray가 아니라 HSV를 사용합니다.
#
# 먼저 측정한 객체별 H·S·V(중앙값):
#   빨간 뚜껑 : H 0~3, S 약 135, V 약 175
#   손(피부)  : H 7~8, S 약 105~115, V 약 190~205
#   콜라      : H 4,   S 약 222, V 약 80 (어두움)
#
# → H를 0~4(+170~180)로 좁혀 피부를 빼고,
#   V를 120 이상으로 정해 어두운 콜라를 뺍니다.
# ------------------------------------------

def red_mask(image):

    hsv = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2HSV,
    )

    lower_red = cv2.inRange(
        hsv,
        (0, 90, 120),
        (4, 255, 255),
    )

    upper_red = cv2.inRange(
        hsv,
        (170, 90, 120),
        (180, 255, 255),
    )

    return cv2.bitwise_or(
        lower_red,
        upper_red,
    )


# ------------------------------------------
# TODO 2
# 필요한 경우 Morphology를 적용합니다.
#
# 마스크에 손 가장자리 등 작은 빨간 점이 남으므로
# Opening(작은 점 제거) → Closing(뚜껑 안의 작은 틈 메우기)을 적용합니다.
# ------------------------------------------

kernel = cv2.getStructuringElement(
    cv2.MORPH_ELLIPSE,
    (5, 5),
)


def clean_mask(mask):

    opened = cv2.morphologyEx(
        mask,
        cv2.MORPH_OPEN,
        kernel,
    )

    return cv2.morphologyEx(
        opened,
        cv2.MORPH_CLOSE,
        kernel,
    )


# ------------------------------------------
# TODO 3
# Contour를 찾고 필요한 Feature를 계산합니다.
#
# largest_red_area_ratio : 가장 큰 빨간 객체 면적 / 전체 이미지 면적
# valid_count            : Noise 기준보다 큰 빨간 객체 수
# center                 : 가장 큰 빨간 객체의 중심(정규화 좌표)
# ------------------------------------------

def measure(image_path):

    image = cv2.imread(
        str(image_path)
    )

    if image is None:
        raise FileNotFoundError(
            image_path
        )

    height, width = image.shape[:2]
    image_area = height * width

    mask = red_mask(image)
    cleaned = clean_mask(mask)

    contours, _ = cv2.findContours(
        cleaned,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE,
    )

    valid = [
        c for c in contours
        if cv2.contourArea(c) >= MIN_CONTOUR_AREA_RATIO * image_area
    ]

    feature = {
        "image": image,
        "cleaned": cleaned,
        "largest": None,
        "largest_red_area_ratio": 0.0,
        "valid_count": len(valid),
        "center": None,
    }

    if contours:

        largest = max(
            contours,
            key=cv2.contourArea,
        )

        feature["largest"] = largest
        feature["largest_red_area_ratio"] = (
            cv2.contourArea(largest) / image_area
        )

        moments = cv2.moments(largest)

        if moments["m00"] != 0:
            feature["center"] = (
                moments["m10"] / moments["m00"] / width,
                moments["m01"] / moments["m00"] / height,
            )

    return feature


# ------------------------------------------
# TODO 4
# 실제 측정값을 확인한 뒤 Rule을 작성합니다.
#
# 기준 한 쌍(ok_01 / ng_01)을 먼저 측정하고,
# 두 값의 중간값을 Candidate Threshold로 정한 뒤 고정합니다.
# ------------------------------------------

ok_ref = measure(input_dir / REFERENCE_OK)
ng_ref = measure(input_dir / REFERENCE_NG)

ok_ratio = ok_ref["largest_red_area_ratio"]
ng_ratio = ng_ref["largest_red_area_ratio"]

if ok_ratio <= ng_ratio:
    raise RuntimeError(
        "정상 이미지의 빨간 면적이 불량보다 크지 않습니다. 마스크 조건을 다시 확인하세요."
    )

candidate_threshold = (ok_ratio + ng_ratio) / 2

print("ok_01 largest_red_area_ratio :", round(ok_ratio, 5))
print("ng_01 largest_red_area_ratio :", round(ng_ratio, 5))
print("candidate threshold          :", round(candidate_threshold, 5))
print()


def judge(feature):

    if feature["largest_red_area_ratio"] >= candidate_threshold:
        return "OK", ""

    return "NG", "NG_RED_CAP_MISSING"


# ------------------------------------------
# 결과 표시와 저장
# ------------------------------------------

def save_result(name, feature, decision, reason):

    image = feature["image"].copy()
    color = (0, 200, 0) if decision == "OK" else (0, 0, 255)

    if feature["largest"] is not None:

        cv2.drawContours(
            image,
            [feature["largest"]],
            -1,
            (0, 255, 0),
            3,
        )

        x, y, w, h = cv2.boundingRect(
            feature["largest"]
        )

        cv2.rectangle(
            image,
            (x, y),
            (x + w, y + h),
            (255, 0, 0),
            2,
        )

    text = f"{decision}  red ratio {feature['largest_red_area_ratio']:.4f}"

    if reason:
        text += f"  {reason}"

    cv2.putText(
        image,
        text,
        (20, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.0,
        color,
        2,
    )

    stem = Path(name).stem

    cv2.imwrite(
        str(output_dir / f"{stem}_mask.jpg"),
        feature["cleaned"],
    )

    cv2.imwrite(
        str(output_dir / f"{stem}_result.jpg"),
        image,
    )


rows = []
correct = 0

checks = [
    (REFERENCE_OK, "OK", "reference"),
    (REFERENCE_NG, "NG", "reference"),
] + [
    (name, expected, "test") for name, expected in TEST_IMAGES
]

for name, expected, role in checks:

    feature = measure(input_dir / name)
    decision, reason = judge(feature)
    save_result(name, feature, decision, reason)

    is_correct = decision == expected

    if role == "test" and is_correct:
        correct += 1

    center = feature["center"]

    rows.append({
        "file": name,
        "role": role,
        "expected": expected,
        "decision": decision,
        "correct": is_correct,
        "largest_red_area_ratio": round(feature["largest_red_area_ratio"], 6),
        "valid_count": feature["valid_count"],
        "center_x_norm": round(center[0], 3) if center else "",
        "center_y_norm": round(center[1], 3) if center else "",
        "reason": reason,
    })

    print(
        f"{name:10s} {role:9s} expected {expected:2s} → {decision:2s}"
        f"  ratio {feature['largest_red_area_ratio']:.5f}"
        f"  count {feature['valid_count']}"
        f"  {'O' if is_correct else 'X'}"
    )


report_path.parent.mkdir(
    parents=True,
    exist_ok=True,
)

with open(report_path, "w", encoding="utf-8-sig", newline="") as f:

    writer = csv.DictWriter(
        f,
        fieldnames=list(rows[0].keys()),
    )

    writer.writeheader()
    writer.writerows(rows)

print()
print("Test 이미지 :", len(TEST_IMAGES))
print("기준과 일치 :", correct)
print("결과 CSV    :", report_path)
print("결과 이미지 :", output_dir)
