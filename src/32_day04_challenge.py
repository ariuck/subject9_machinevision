from pathlib import Path
from time import perf_counter
import csv

import cv2
import numpy as np


reference_path = Path(
    "samples/day04/reference/reference_label.jpg"
)

challenge_dir = Path(
    "samples/day04/challenge"
)

output_dir = Path(
    "outputs/day04/challenge"
)

report_path = Path(
    "reports/day04_challenge_results.csv"
)

output_dir.mkdir(
    parents=True,
    exist_ok=True,
)


challenge_files = [
    challenge_dir / "shift.jpg",
    challenge_dir / "rotate.jpg",
    challenge_dir / "distance.jpg",
    challenge_dir / "tilt_glare.jpg",
]


# --------------------------------------------------
# 1. 사용할 방법을 선택합니다.
#
# TEMPLATE
# ORB
# SIFT
# SIFT_HOMOGRAPHY
#
# [선택] SIFT_HOMOGRAPHY
# - 27~30번 비교에서 Template은 shift·rot15에서 다른 위치를 찾았고,
#   SIFT + Homography는 4개 Target 모두 로고 위치를 찾았다.
# - distance.jpg(387×157)는 Template(440×198)보다 작아
#   Template Matching을 적용할 수 없다.
# - 회전·거리 변화가 있는 실제 촬영에서 로고 위치까지 표시하기 위해 선택했다.
# --------------------------------------------------

selected_method = "SIFT_HOMOGRAPHY"


reference = cv2.imread(
    str(reference_path)
)

if reference is None:
    raise FileNotFoundError(
        reference_path
    )


# 30_homography.py와 같은 SIFT · Matcher · Ratio Test · RANSAC 설정
reference_gray = cv2.cvtColor(
    reference,
    cv2.COLOR_BGR2GRAY,
)

sift = cv2.SIFT_create()

reference_keypoints, reference_descriptors = sift.detectAndCompute(
    reference_gray,
    None,
)

matcher = cv2.BFMatcher(
    cv2.NORM_L2,
    crossCheck=False,
)

reference_h, reference_w = reference_gray.shape[:2]

reference_corners = np.float32([
    [0, 0],
    [reference_w - 1, 0],
    [reference_w - 1, reference_h - 1],
    [0, reference_h - 1],
]).reshape(-1, 1, 2)

print(
    "Reference Keypoints:",
    len(reference_keypoints),
)

rows = []


# --------------------------------------------------
# 2. Challenge 이미지를 하나씩 읽습니다.
# --------------------------------------------------

for target_path in challenge_files:

    target = cv2.imread(
        str(target_path)
    )

    if target is None:
        print(
            "읽기 실패:",
            target_path
        )
        continue


    # --------------------------------------------------
    # SIFT_HOMOGRAPHY
    # → Good Match + Inlier + 로고 위치
    # --------------------------------------------------

    target_gray = cv2.cvtColor(
        target,
        cv2.COLOR_BGR2GRAY,
    )

    start = perf_counter()

    target_keypoints, target_descriptors = sift.detectAndCompute(
        target_gray,
        None,
    )

    good_matches = []
    inlier_count = 0
    inlier_ratio = 0.0
    status = "NOT_FOUND"
    preview = target.copy()

    if target_descriptors is not None and len(target_keypoints) >= 2:

        for candidate in matcher.knnMatch(
            reference_descriptors,
            target_descriptors,
            k=2,
        ):

            if len(candidate) < 2:
                continue

            m, n = candidate

            if m.distance < 0.75 * n.distance:
                good_matches.append(m)

    if len(good_matches) >= 4:

        reference_points = np.float32([
            reference_keypoints[m.queryIdx].pt for m in good_matches
        ]).reshape(-1, 1, 2)

        target_points = np.float32([
            target_keypoints[m.trainIdx].pt for m in good_matches
        ]).reshape(-1, 1, 2)

        homography, inlier_mask = cv2.findHomography(
            reference_points,
            target_points,
            cv2.RANSAC,
            5.0,
        )

        if homography is not None and inlier_mask is not None:

            inlier_count = int(inlier_mask.ravel().sum())
            inlier_ratio = inlier_count / len(good_matches)

            projected_corners = cv2.perspectiveTransform(
                reference_corners,
                homography,
            )

            cv2.polylines(
                preview,
                [np.int32(projected_corners)],
                True,
                (0, 255, 0),
                3,
                cv2.LINE_AA,
            )

            status = "FOUND"

    elapsed_ms = (perf_counter() - start) * 1000

    cv2.putText(
        preview,
        f"good={len(good_matches)} inlier={inlier_count} ratio={inlier_ratio:.2f}",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2,
        cv2.LINE_AA,
    )

    cv2.imwrite(
        str(output_dir / f"{target_path.stem}_{selected_method.lower()}.jpg"),
        preview,
    )

    rows.append({
        "filename": target_path.name,
        "size": f"{target.shape[1]}x{target.shape[0]}",
        "method": selected_method,
        "target_keypoints": len(target_keypoints),
        "good_matches": len(good_matches),
        "inliers": inlier_count,
        "inlier_ratio": f"{inlier_ratio:.6f}",
        "status": status,
        "time_ms": f"{elapsed_ms:.3f}",
    })

    print(
        target_path.name,
        "method=",
        selected_method,
        f"good={len(good_matches)}",
        f"inlier={inlier_count}",
        f"ratio={inlier_ratio:.3f}",
        f"status={status}",
    )


with report_path.open("w", newline="", encoding="utf-8") as file:

    writer = csv.DictWriter(
        file,
        fieldnames=list(rows[0].keys()),
    )

    writer.writeheader()
    writer.writerows(rows)

print()
print("CSV 저장:", report_path)
print("결과 이미지:", output_dir)
