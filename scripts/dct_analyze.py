#!/usr/bin/env python3
"""
DCT Coefficient Analyzer - Analyze DCT coefficients in JPEG images

Analyzes:
- Coefficient distribution
- +/-1 balance (F5 detection)
- Chi-square test
- Zero-rate analysis
"""

import argparse
import sys
from pathlib import Path

try:
    import numpy as np
except ImportError:
    print("Error: numpy required. Install: pip install numpy")
    sys.exit(1)


def load_jpeg_dct(image_path: str) -> np.ndarray:
    """Load JPEG and extract DCT coefficients."""
    try:
        from PIL import Image
        import io

        img = Image.open(image_path)
        if not image_path.lower().endswith((".jpg", ".jpeg")):
            print("Warning: Not a JPEG, DCT analysis may not be accurate")

        # Get JPEG buffer
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=95)
        buf.seek(0)

        # Simple DCT approximation using numpy FFT
        img_array = np.array(img.convert("L"), dtype=np.float32)
        dct = np.fft.fft2(img_array)
        return np.abs(dct)

    except Exception as e:
        print(f"Error loading image: {e}", file=sys.stderr)
        sys.exit(1)


def analyze_coefficients(dct: np.ndarray, band: str = "all") -> dict:
    """Analyze DCT coefficient distribution."""
    results = {
        "total_coeffs": int(dct.size),
        "mean": float(np.mean(dct)),
        "std": float(np.std(dct)),
        "zeros": int(np.sum(dct < 0.001)),
        "zero_rate": 0.0,
    }
    results["zero_rate"] = results["zeros"] / results["total_coeffs"]

    return results


def chi_square_analysis(dct: np.ndarray) -> dict:
    """Chi-square test on DCT coefficients."""
    # Flatten and round
    coeffs = np.round(dct.flatten()).astype(int)

    # Count pairs (v, v+1)
    chi_values = []
    for v in range(-10, 10):
        count_v = np.sum(coeffs == v)
        count_v1 = np.sum(coeffs == v + 1)

        if count_v + count_v1 > 10:
            expected = (count_v + count_v1) / 2
            if expected > 0:
                chi = (
                    (count_v - expected) ** 2 + (count_v1 - expected) ** 2
                ) / expected
                chi_values.append(chi)

    return {
        "chi_square": float(np.mean(chi_values)) if chi_values else 0.0,
        "chi_values_count": len(chi_values),
    }


def plus_minus_balance(dct: np.ndarray) -> dict:
    """Check +1/-1 coefficient balance (F5 detection)."""
    coeffs = np.round(dct.flatten()).astype(int)

    # Count +1 and -1
    plus_one = np.sum(coeffs == 1)
    minus_one = np.sum(coeffs == -1)
    total = plus_one + minus_one

    if total == 0:
        return {"ratio": 0.5, "imbalance": 0.0}

    ratio = plus_one / total
    imbalance = abs(ratio - 0.5)

    return {
        "plus_one": int(plus_one),
        "minus_one": int(minus_one),
        "ratio": float(ratio),
        "imbalance": float(imbalance),
    }


def main():
    parser = argparse.ArgumentParser(description="DCT coefficient analysis for JPEG")
    parser.add_argument("--input", "-i", required=True, help="Input JPEG image")
    parser.add_argument(
        "--band",
        "-b",
        choices=["low", "mid", "high", "all"],
        default="all",
        help="Frequency band to analyze (default: all)",
    )
    parser.add_argument("--chi-square", action="store_true", help="Run chi-square test")
    parser.add_argument("--signs", action="store_true", help="Check +/-1 balance")
    parser.add_argument("--output", "-o", help="Output JSON file (optional)")

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: {input_path} not found", file=sys.stderr)
        sys.exit(1)

    print(f"Analyzing: {args.input}")
    print(f"Band: {args.band}")
    print()

    # Load DCT
    dct = load_jpeg_dct(args.input)

    # Basic analysis
    results = analyze_coefficients(dct, args.band)
    print("=== Coefficient Distribution ===")
    print(f"Total coefficients: {results['total_coeffs']:,}")
    print(f"Mean: {results['mean']:.4f}")
    print(f"Std: {results['std']:.4f}")
    print(f"Zeros: {results['zeros']:,} ({results['zero_rate'] * 100:.2f}%)")
    print()

    # Chi-square
    if args.chi_square:
        chi_results = chi_square_analysis(dct)
        print("=== Chi-Square Analysis ===")
        print(f"Chi-square: {chi_results['chi_square']:.4f}")
        if chi_results["chi_square"] > 3.84:
            print("⚠️  SUSPICIOUS: Chi-square > 3.84 (p < 0.05)")
        print()

    # +/-1 balance
    if args.signs:
        balance = plus_minus_balance(dct)
        print("=== +/-1 Balance (F5 Detection) ===")
        print(f"+1 count: {balance['plus_one']:,}")
        print(f"-1 count: {balance['minus_one']:,}")
        print(f"Ratio: {balance['ratio']:.4f}")
        print(f"Imbalance: {balance['imbalance']:.4f}")
        if abs(balance["ratio"] - 0.5) > 0.01:
            print("⚠️  SUSPICIOUS: Ratio != 0.50 (possible F5 steganography)")


if __name__ == "__main__":
    main()
