#!/usr/bin/env python3
"""
DCT LSB Bias Analyzer — Primary Test for JPEG Steganography

Analyzes the least-significant-bit (parity) of quantized DCT coefficients
extracted directly from JPEG files via jpegio.

Usage:
    python3 scripts/dct_lsb_bias.py image.jpg
    python3 scripts/dct_lsb_bias.py image1.jpg image2.jpg ...

Thresholds:
    LSB=1 ratio > 0.60 or deviation > 0.10 = STRONG evidence
    Odd ratio > 0.70 (|coef| <= 10) = STRONG evidence
    |1| concentration > 50% = stego fingerprint

Requires: pip install jpegio numpy Pillow
"""

import argparse
import os
import sys

try:
    import jpegio

    HAS_JPEGIO = True
except ImportError:
    HAS_JPEGIO = False

import numpy as np


def analyze_dct_lsb(path: str) -> dict:
    """Analyze LSB patterns of quantized DCT coefficients."""
    if not HAS_JPEGIO:
        print("ERROR: jpegio not installed. Install with: pip install jpegio")
        return {"verdict": "SKIPPED", "reason": "jpegio not installed"}

    if not os.path.exists(path):
        print(f"ERROR: file not found: {path}")
        return {"verdict": "ERROR", "reason": "file not found"}

    fname = os.path.basename(path)
    results = {}

    try:
        j = jpegio.read(path)
    except Exception as e:
        print(f"ERROR reading {fname}: {e}")
        return {"verdict": "ERROR", "reason": str(e)}

    for channel in range(3):
        if channel >= j.image_components:
            continue

        coeffs = j.coef_arrays[channel].astype(int)
        nonzero = coeffs[coeffs != 0]
        total_nz = len(nonzero)

        if total_nz == 0:
            print(f"  Channel {channel}: all zero coefficients")
            continue

        # LSB of non-zero coefficients
        lsb = nonzero & 1
        n_0 = int(np.sum(lsb == 0))
        n_1 = int(np.sum(lsb == 1))
        total = n_0 + n_1
        lsb_ratio = n_1 / total if total > 0 else 0.5
        deviation = abs(lsb_ratio - 0.5)

        # Small magnitude coefficients (|coef| <= 10) — where payload concentrates
        small = nonzero[np.abs(nonzero) <= 10]
        odd_small = int(np.sum(np.abs(small) & 1))
        total_small = len(small)
        odd_ratio = odd_small / total_small if total_small > 0 else 0.5
        odd_deviation = abs(odd_ratio - 0.5)

        # Magnitude concentration
        mag_hist = {}
        for v in range(1, 11):
            mag_hist[v] = int(np.sum(np.abs(nonzero) == v))
        total_small_mag = sum(mag_hist.values())
        dominant_mag = max(mag_hist, key=mag_hist.get)
        dominant_pct = (
            mag_hist[dominant_mag] / total_small_mag * 100 if total_small_mag > 0 else 0
        )

        # Verdict
        if deviation > 0.10:
            lsb_verdict = "STRONG"
        elif deviation > 0.05:
            lsb_verdict = "SUSPICIOUS"
        elif deviation > 0.02:
            lsb_verdict = "MARGINAL"
        else:
            lsb_verdict = "CLEAN"

        if odd_deviation > 0.10:
            odd_verdict = "STRONG"
        elif odd_deviation > 0.05:
            odd_verdict = "SUSPICIOUS"
        elif odd_deviation > 0.02:
            odd_verdict = "MARGINAL"
        else:
            odd_verdict = "CLEAN"

        print(
            f"  Ch{channel}: LSB=1={lsb_ratio:.3f} (dev={deviation:.3f}) [{lsb_verdict}]"
        )
        print(
            f"         odd(|coef|<=10)={odd_ratio:.3f} (dev={odd_deviation:.3f}) [{odd_verdict}]"
        )
        print(f"         |1| concentration: {dominant_pct:.1f}%")

        results[channel] = {
            "lsb_ratio": float(lsb_ratio),
            "lsb_deviation": float(deviation),
            "odd_ratio": float(odd_ratio),
            "odd_deviation": float(odd_deviation),
            "dominant_mag": dominant_mag,
            "dominant_pct": float(dominant_pct),
            "lsb_verdict": lsb_verdict,
            "odd_verdict": odd_verdict,
        }

    # Overall verdict
    if results:
        max_lsb_dev = max(r.get("lsb_deviation", 0) for r in results.values())
        max_odd_dev = max(r.get("odd_deviation", 0) for r in results.values())
        if max_lsb_dev > 0.10 or max_odd_dev > 0.10:
            overall = "STRONGLY SUSPICIOUS"
        elif max_lsb_dev > 0.05 or max_odd_dev > 0.05:
            overall = "SUSPICIOUS"
        elif max_lsb_dev > 0.02 or max_odd_dev > 0.02:
            overall = "MARGINAL"
        else:
            overall = "CLEAN"
        print(f"  Overall: {overall}")
        results["_overall"] = overall
        results["max_lsb_dev"] = float(max_lsb_dev)
        results["max_odd_dev"] = float(max_odd_dev)

    return results


def main():
    parser = argparse.ArgumentParser(
        description="DCT LSB Bias Analyzer — Primary test for JPEG steganography"
    )
    parser.add_argument("images", nargs="+", help="JPEG image(s) to analyze")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args()

    all_results = {}
    for path in args.images:
        print(f"\n{'=' * 60}")
        print(f"Analyzing: {os.path.basename(path)}")
        print(f"{'=' * 60}")
        result = analyze_dct_lsb(path)
        all_results[path] = result

    if args.json:
        import json

        print(json.dumps(all_results, indent=2))


if __name__ == "__main__":
    main()
