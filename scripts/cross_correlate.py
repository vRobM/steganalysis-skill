#!/usr/bin/env python3
"""
Cross-Image Correlation Analyzer

Compares multiple images to detect:
- Similar encoding patterns
- KL divergence between distributions
- Statistical anomalies suggesting same steganographic tool
"""

import argparse
import sys
from pathlib import Path

try:
    import numpy as np
    from PIL import Image
except ImportError:
    print("Error: numpy and pillow required. Install: pip install numpy pillow")
    sys.exit(1)


def extract_features(image_path: str) -> dict:
    """Extract statistical features from an image."""
    img = Image.open(image_path).convert("RGB")
    arr = np.array(img)

    features = {}

    # LSB distribution
    lsb_bits = arr & 1
    features["lsb_ratio"] = float(np.mean(lsb_bits))

    # Channel means
    for i, ch in enumerate(["R", "G", "B"]):
        features[f"{ch}_mean"] = float(np.mean(arr[:, :, i]))

    # Channel stds
    for i, ch in enumerate(["R", "G", "B"]):
        features[f"{ch}_std"] = float(np.std(arr[:, :, i]))

    # DCT-like features (using FFT approximation)
    gray = np.mean(arr, axis=2)
    fft = np.abs(np.fft.fft2(gray))
    features["fft_mean"] = float(np.mean(fft))
    features["fft_std"] = float(np.std(fft))

    return features


def kl_divergence(p: np.ndarray, q: np.ndarray) -> float:
    """Calculate KL divergence between two distributions."""
    # Add small epsilon to avoid log(0)
    p = p + 1e-10
    q = q + 1e-10

    # Normalize
    p = p / p.sum()
    q = q / q.sum()

    return float(np.sum(p * np.log(p / q)))


def compare_distributions(img1: str, img2: str) -> dict:
    """Compare LSB distributions between two images."""
    img1_data = Image.open(img1).convert("RGB")
    img2_data = Image.open(img2).convert("RGB")

    arr1 = np.array(img1_data)
    arr2 = np.array(img2_data)

    # Histogram comparison
    hist1_r, _ = np.histogram(arr1[:, :, 0].flatten(), bins=256, range=(0, 256))
    hist2_r, _ = np.histogram(arr2[:, :, 0].flatten(), bins=256, range=(0, 256))

    # KL divergence
    kl_r = kl_divergence(hist1_r.astype(float), hist2_r.astype(float))

    return {"kl_divergence": kl_r}


def correlation_matrix(image_paths: list) -> np.ndarray:
    """Build correlation matrix for multiple images."""
    n = len(image_paths)
    features = []

    for path in image_paths:
        feat = extract_features(path)
        features.append(list(feat.values()))

    features = np.array(features)

    # Correlation matrix
    corr = np.corrcoef(features)
    return corr


def main():
    parser = argparse.ArgumentParser(description="Cross-image correlation analysis")
    parser.add_argument("--images", "-i", nargs="+", required=True, help="Input images")
    parser.add_argument("--output", "-o", help="Output JSON file (optional)")
    parser.add_argument(
        "--matrix", "-m", action="store_true", help="Show correlation matrix"
    )

    args = parser.parse_args()

    if len(args.images) < 2:
        print("Error: Need at least 2 images for comparison", file=sys.stderr)
        sys.exit(1)

    print(f"Comparing {len(args.images)} images:")
    for img in args.images:
        print(f"  - {img}")
    print()

    # Extract features
    print("=== Feature Extraction ===")
    all_features = {}
    for img in args.images:
        features = extract_features(img)
        all_features[img] = features
        print(f"\n{Path(img).name}:")
        for k, v in features.items():
            print(f"  {k}: {v:.4f}")

    print()

    # Pairwise comparison
    print("=== Pairwise KL Divergence ===")
    for i, img1 in enumerate(args.images):
        for img2 in args.images[i + 1 :]:
            result = compare_distributions(img1, img2)
            print(
                f"{Path(img1).name} vs {Path(img2).name}: {result['kl_divergence']:.6f}"
            )
            if result["kl_divergence"] < 0.05:
                print("  ⚠️  LOW DIVERGENCE: Similar encoding detected!")

    # Correlation matrix
    if args.matrix and len(args.images) <= 10:
        print()
        print("=== Correlation Matrix ===")
        corr = correlation_matrix(args.images)

        # Header
        print("         ", end="")
        for img in args.images:
            print(f"{Path(img).stem[:8]:>8}", end=" ")
        print()

        # Rows
        for i, img in enumerate(args.images):
            print(f"{Path(img).stem[:8]:>8}", end=" ")
            for j in range(len(args.images)):
                print(f"{corr[i, j]:8.4f}", end=" ")
            print()


if __name__ == "__main__":
    main()
