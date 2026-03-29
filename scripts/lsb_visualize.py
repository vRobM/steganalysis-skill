#!/usr/bin/env python3
"""
LSB Plane Visualizer - Visualize least significant bits in images

Generates visualizations of LSB planes to help detect steganography.
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


def extract_lsb_plane(image_path: str, bit: int = 0) -> np.ndarray:
    """Extract a specific LSB plane from an image."""
    img = Image.open(image_path).convert("RGB")
    arr = np.array(img)

    # Extract bit plane
    plane = (arr >> bit) & 1
    return (plane * 255).astype(np.uint8)


def visualize_all_planes(image_path: str, output_dir: str = ".") -> list:
    """Visualize all LSB planes (1-8 bits per channel)."""
    img = Image.open(image_path).convert("RGB")
    arr = np.array(img)

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    base_name = Path(image_path).stem
    channels = ["R", "G", "B"]

    # For each bit position (1-8)
    for bit in range(1, 9):
        # Check if embedding would exceed capacity
        if bit > int(np.log2(255)):
            break

        mask = 1 << (bit - 1)
        plane = (arr >> (bit - 1)) & 1
        plane_visual = (plane * 255).astype(np.uint8)

        # Save as grayscale
        output_file = output_path / f"{base_name}_lsb{bit}.png"
        Image.fromarray(plane_visual).save(output_file)
        print(f"Saved: {output_file}")

    # Combined RGB view (bit 1)
    combined = ((arr >> 0) & 1) * 255
    output_file = output_path / f"{base_name}_lsb_combined.png"
    Image.fromarray(combined).save(output_file)
    print(f"Saved: {output_file}")

    return []


def analyze_lsb_distribution(image_path: str) -> dict:
    """Analyze LSB bit distribution."""
    img = Image.open(image_path).convert("RGB")
    arr = np.array(img)

    results = {}

    for ch, name in enumerate(["R", "G", "B"]):
        channel = arr[:, :, ch]
        lsb = channel & 1

        zero_count = np.sum(lsb == 0)
        one_count = np.sum(lsb == 1)
        total = zero_count + one_count

        results[name] = {
            "zeros": int(zero_count),
            "ones": int(one_count),
            "ratio": float(one_count / total) if total > 0 else 0.0,
        }

    return results


def entropy_per_channel(image_path: str) -> dict:
    """Calculate Shannon entropy per channel."""
    from math import log2

    img = Image.open(image_path).convert("RGB")
    arr = np.array(img)

    results = {}

    for ch, name in enumerate(["R", "G", "B"]):
        channel = arr[:, :, ch].flatten()
        # Calculate histogram
        hist, _ = np.histogram(channel, bins=256, range=(0, 256))
        hist = hist[hist > 0]  # Remove zero counts

        # Shannon entropy
        probs = hist / hist.sum()
        entropy = -np.sum(probs * np.log2(probs))

        results[name] = float(entropy)

    return results


def main():
    parser = argparse.ArgumentParser(description="LSB plane visualization")
    parser.add_argument("--input", "-i", required=True, help="Input image")
    parser.add_argument(
        "--channel",
        "-c",
        choices=["R", "G", "B", "all"],
        default="all",
        help="Channel to visualize (default: all)",
    )
    parser.add_argument(
        "--bit", "-b", type=int, default=1, help="Bit position (default: 1)"
    )
    parser.add_argument(
        "--output", "-o", default=".", help="Output directory (default: current)"
    )
    parser.add_argument(
        "--analyze", "-a", action="store_true", help="Run statistical analysis"
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: {args.input} not found", file=sys.stderr)
        sys.exit(1)

    print(f"Processing: {args.input}")
    print()

    # Visualization
    if args.channel == "all":
        visualize_all_planes(args.input, args.output)
    else:
        plane = extract_lsb_plane(args.input, args.bit)
        output_path = (
            Path(args.output) / f"{input_path.stem}_lsb{args.bit}_{args.channel}.png"
        )
        Image.fromarray(plane).save(output_path)
        print(f"Saved: {output_path}")

    print()

    # Analysis
    if args.analyze:
        print("=== LSB Distribution Analysis ===")
        dist = analyze_lsb_distribution(args.input)
        for ch, data in dist.items():
            print(
                f"{ch} channel: 0s={data['zeros']:,}, 1s={data['ones']:,}, ratio={data['ratio']:.4f}"
            )

        print()
        print("=== Channel Entropy ===")
        ent = entropy_per_channel(args.input)
        for ch, val in ent.items():
            print(f"{ch}: {val:.4f}")


if __name__ == "__main__":
    main()
