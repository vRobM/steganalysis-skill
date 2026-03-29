#!/usr/bin/env python3
"""
Steganography Batch Scanner

Scans directories for suspicious images and runs multiple detection methods.
"""

import argparse
import sys
from pathlib import Path
import os

try:
    import numpy as np
    from PIL import Image
except ImportError:
    print("Error: numpy and pillow required. Install: pip install numpy pillow")
    sys.exit(1)


# Extensions to scan
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif", ".gif"}


def scan_file(image_path: str) -> dict:
    """Scan a single image for steganography indicators."""
    result = {
        "file": image_path,
        "suspicion_score": 0.0,
        "findings": [],
    }

    try:
        img = Image.open(image_path)
        arr = np.array(img)
    except Exception as e:
        result["findings"].append(f"Error reading: {e}")
        return result

    # Check 1: File size anomaly
    file_size = Path(image_path).stat().st_size
    expected_size = arr.size * arr.dtype.itemsize
    if file_size < expected_size * 0.5:
        result["suspicion_score"] += 0.1
        result["findings"].append(
            "File size smaller than expected (possible compression or hidden data)"
        )

    # Check 2: LSB distribution
    lsb_bits = arr.flatten() & 1
    ones_ratio = np.mean(lsb_bits)

    # Clean images typically have ~0.5 ratio
    if abs(ones_ratio - 0.5) > 0.05:
        result["suspicion_score"] += 0.2
        result["findings"].append(
            f"LSB distribution anomaly: {ones_ratio:.4f} (expected ~0.5)"
        )

    # Check 3: Entropy
    hist, _ = np.histogram(arr.flatten(), bins=256, range=(0, 256))
    hist = hist[hist > 0]
    probs = hist / hist.sum()
    entropy = -np.sum(probs * np.log2(probs))

    # High entropy could indicate encrypted data
    if entropy > 7.9:
        result["suspicion_score"] += 0.15
        result["findings"].append(
            f"High entropy: {entropy:.4f} (possible encrypted payload)"
        )

    # Check 4: Unusual dimensions
    if arr.shape[0] % 8 != 0 or arr.shape[1] % 8 != 0:
        result["suspicion_score"] += 0.05
        result["findings"].append(
            "Dimensions not divisible by 8 (unusual for steganography)"
        )

    # Check 5: Chunk analysis (PNG)
    if image_path.lower().endswith(".png"):
        with open(image_path, "rb") as f:
            f.seek(-1024, 2)
            tail = f.read()
            if len(tail) > 16 and b"IEND" in tail:
                eof_pos = tail.index(b"IEND") + 4
                appended = tail[eof_len:]
                if len(appended) > 100:
                    result["suspicion_score"] += 0.3
                    result["findings"].append(
                        f"Data appended after IEND: {len(appended)} bytes"
                    )

    return result


def scan_directory(
    directory: str, recursive: bool = False, extensions: set = None
) -> list:
    """Scan a directory for suspicious images."""
    if extensions is None:
        extensions = IMAGE_EXTENSIONS

    dir_path = Path(directory)
    results = []

    # Find all images
    if recursive:
        patterns = [f"**/*{ext}" for ext in extensions]
        image_files = []
        for pattern in patterns:
            image_files.extend(dir_path.glob(pattern))
    else:
        image_files = [
            f
            for f in dir_path.iterdir()
            if f.is_file() and f.suffix.lower() in extensions
        ]

    print(f"Found {len(image_files)} images to scan")
    print("=" * 50)

    # Scan each file
    for i, image_file in enumerate(image_files, 1):
        print(f"[{i}/{len(image_files)}] Scanning: {image_file.name}...", end=" ")
        result = scan_file(str(image_file))

        if result["suspicion_score"] > 0:
            print(f"⚠️  Score: {result['suspicion_score']:.2f}")
        else:
            print("✓")

        results.append(result)

    return results


def summarize_results(results: list) -> None:
    """Print summary of scan results."""
    print()
    print("=" * 50)
    print("SCAN SUMMARY")
    print("=" * 50)

    total = len(results)
    suspicious = [r for r in results if r["suspicion_score"] > 0.2]
    high = [r for r in results if r["suspicion_score"] > 0.5]

    print(f"Total scanned: {total}")
    print(f"Suspicious (>0.2): {len(suspicious)}")
    print(f"High confidence (>0.5): {len(high)}")

    if high:
        print()
        print("HIGH CONFIDENCE FINDINGS:")
        for r in high:
            print(f"\n  {r['file']}:")
            print(f"    Score: {r['suspicion_score']:.2f}")
            for finding in r["findings"]:
                print(f"    - {finding}")

    if suspicious and not high:
        print()
        print("SUSPICIOUS FILES:")
        for r in suspicious:
            print(f"\n  {r['file']}:")
            print(f"    Score: {r['suspicion_score']:.2f}")
            for finding in r["findings"]:
                print(f"    - {finding}")


def main():
    parser = argparse.ArgumentParser(description="Batch steganography scanner")
    parser.add_argument("--dir", "-d", required=True, help="Directory to scan")
    parser.add_argument(
        "--recursive", "-r", action="store_true", help="Scan subdirectories"
    )
    parser.add_argument(
        "--extensions",
        "-e",
        default=".png,.jpg,.jpeg,.bmp",
        help="Comma-separated extensions (default: .png,.jpg,.jpeg,.bmp)",
    )
    parser.add_argument("--output", "-o", help="Output JSON file (optional)")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show all findings"
    )

    args = parser.parse_args()

    extensions = set(f".{ext.strip('.')}" for ext in args.extensions.split(","))

    if not Path(args.dir).exists():
        print(f"Error: {args.dir} not found", file=sys.stderr)
        sys.exit(1)

    print(f"Scanning: {args.dir}")
    print(f"Recursive: {args.recursive}")
    print(f"Extensions: {', '.join(sorted(extensions))}")
    print()

    # Scan
    results = scan_directory(args.dir, args.recursive, extensions)

    # Summary
    summarize_results(results)

    # Verbose output
    if args.verbose:
        print()
        print("=" * 50)
        print("ALL FINDINGS")
        print("=" * 50)
        for r in results:
            if r["findings"]:
                print(f"\n{r['file']}:")
                for finding in r["findings"]:
                    print(f"  - {finding}")


if __name__ == "__main__":
    main()
