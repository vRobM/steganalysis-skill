#!/usr/bin/env python3
"""
Steganalysis Detection Engine
Multi-method detection pipeline for steganographic content in images.
"""

import os
import sys
import math
import struct
import argparse
from collections import Counter
from PIL import Image
import numpy as np
from scipy.fft import dctn


def chi_square_lsb(image_path):
    """Chi-square test on LSB plane — detects LSB Replacement."""
    img = Image.open(image_path).convert("RGB")
    arr = np.array(img)
    results = {}

    for ci, cn in enumerate(["R", "G", "B"]):
        ch = arr[:, :, ci]
        flat = ch.flatten()
        int_c = flat.astype(int)

        chi_parts = []
        for v in range(255):
            c_v = np.sum(int_c == v)
            c_v1 = np.sum(int_c == v + 1)
            if c_v + c_v1 > 5:
                exp = (c_v + c_v1) / 2
                chi = ((c_v - exp) ** 2 + (c_v1 - exp) ** 2) / exp
                chi_parts.append(chi)

        avg_chi = np.mean(chi_parts) if chi_parts else 0
        results[cn] = {
            "chi_square": round(avg_chi, 4),
            "suspicious": avg_chi > 3.84,
            "confidence": "high"
            if avg_chi > 100
            else "medium"
            if avg_chi > 6
            else "low",
        }

    return results


def lsb_ratio_analysis(image_path):
    """Analyze LSB ratios — skewed ratios indicate payload."""
    img = Image.open(image_path).convert("RGB")
    arr = np.array(img)
    results = {}

    for ci, cn in enumerate(["R", "G", "B"]):
        ch = arr[:, :, ci]
        lsb = ch & 1
        ratio = lsb.mean()
        deviation = abs(ratio - 0.5)

        results[cn] = {
            "lsb_ratio": round(ratio, 4),
            "deviation": round(deviation, 4),
            "suspicious": deviation > 0.02,
            "interpretation": "skewed toward 1s"
            if ratio > 0.52
            else "skewed toward 0s"
            if ratio < 0.48
            else "balanced",
        }

    return results


def bit_plane_entropy(image_path):
    """Shannon entropy per bit plane — encrypted data shows max entropy."""
    img = Image.open(image_path).convert("RGB")
    arr = np.array(img)
    results = {}

    for ci, cn in enumerate(["R", "G", "B"]):
        ch = arr[:, :, ci]
        plane_entropies = []

        for bit in range(8):
            plane = (ch >> bit) & 1
            flat = plane.flatten()
            counts = Counter(flat)
            total = len(flat)
            ent = 0
            for c in counts.values():
                p = c / total
                if p > 0:
                    ent -= p * math.log2(p)
            plane_entropies.append(round(ent, 4))

        results[cn] = {
            "entropies": plane_entropies,
            "lsb_entropy": plane_entropies[0],
            "suspicious": plane_entropies[0] > 0.99,
            "interpretation": "near-maximum (encrypted/random)"
            if plane_entropies[0] > 0.99
            else "normal"
            if plane_entropies[0] > 0.9
            else "structured",
        }

    return results


def spatial_autocorrelation(image_path):
    """LSB spatial autocorrelation — stego breaks natural correlation."""
    img = Image.open(image_path).convert("RGB")
    arr = np.array(img)
    results = {}

    for ci, cn in enumerate(["R", "G", "B"]):
        ch = arr[:, :, ci]
        lsb = ch & 1

        h_corr = float(np.mean(lsb[:, :-1] == lsb[:, 1:]))
        v_corr = float(np.mean(lsb[:-1, :] == lsb[1:, :]))
        d_corr = float(np.mean(lsb[:-1, :-1] == lsb[1:, 1:]))

        results[cn] = {
            "horizontal": round(h_corr, 4),
            "vertical": round(v_corr, 4),
            "diagonal": round(d_corr, 4),
            "suspicious": h_corr < 0.505 and v_corr < 0.505,
            "interpretation": "below natural correlation — possible stego"
            if h_corr < 0.505
            else "natural image correlation",
        }

    return results


def dct_coefficient_analysis(image_path):
    """DCT coefficient analysis for JPEG — detects F5, JSteg, OutGuess."""
    if not image_path.lower().endswith((".jpg", ".jpeg")):
        return {"skipped": "not a JPEG"}

    img = Image.open(image_path).convert("L")
    arr = np.array(img, dtype=np.float64)
    h, w = arr.shape

    ph = (8 - h % 8) % 8
    pw = (8 - w % 8) % 8
    if ph or pw:
        arr = np.pad(arr, ((0, ph), (0, pw)), mode="edge")

    # Mid-frequency mask
    mid_mask = np.zeros((8, 8), dtype=bool)
    mid_mask[0, 3] = mid_mask[1, 2] = mid_mask[2, 1] = mid_mask[3, 0] = True
    mid_mask[0, 4] = mid_mask[1, 3] = mid_mask[2, 2] = mid_mask[3, 1] = mid_mask[
        4, 0
    ] = True
    mid_mask[0, 5] = mid_mask[1, 4] = mid_mask[2, 3] = mid_mask[3, 2] = mid_mask[
        4, 1
    ] = mid_mask[5, 0] = True
    mid_mask[0, 6] = mid_mask[1, 5] = mid_mask[2, 4] = mid_mask[3, 3] = mid_mask[
        4, 2
    ] = mid_mask[5, 1] = mid_mask[6, 0] = True

    mid_coeffs = []
    for by in range(0, arr.shape[0], 8):
        for bx in range(0, arr.shape[1], 8):
            block = arr[by : by + 8, bx : bx + 8]
            if block.shape != (8, 8):
                continue
            dct_block = dctn(block, type=2, norm="ortho")
            mid_coeffs.extend(dct_block[mid_mask].tolist())

    coeffs = np.array(mid_coeffs)
    int_c = np.round(coeffs).astype(int)

    # Zero rate
    zero_rate = np.sum(int_c == 0) / len(int_c)

    # +1/-1 ratio
    plus1 = np.sum(int_c == 1)
    minus1 = np.sum(int_c == -1)
    ratio = plus1 / (plus1 + minus1) if (plus1 + minus1) > 0 else 0.5

    # Chi-square pair balance
    chi_parts = []
    for v in range(-8, 8):
        c_v = np.sum(int_c == v)
        c_v1 = np.sum(int_c == v + 1)
        if c_v + c_v1 > 5:
            exp = (c_v + c_v1) / 2
            chi = ((c_v - exp) ** 2 + (c_v1 - exp) ** 2) / exp
            chi_parts.append(chi)

    avg_chi = np.mean(chi_parts) if chi_parts else 0

    return {
        "zero_rate": round(zero_rate, 4),
        "plus1_minus1_ratio": round(ratio, 4),
        "chi_square": round(avg_chi, 2),
        "f5_suspicious": abs(ratio - 0.5) < 0.03 and zero_rate < 0.8,
        "jsteg_suspicious": abs(ratio - 0.5) > 0.05,
        "interpretation": "Possible F5 matrix encoding"
        if abs(ratio - 0.5) < 0.03
        else "Possible JSteg"
        if abs(ratio - 0.5) > 0.05
        else "Natural JPEG",
    }


def appended_data_check(image_path):
    """Check for data appended after image markers."""
    with open(image_path, "rb") as f:
        data = f.read()

    results = {"has_appended": False}

    if image_path.lower().endswith(".png"):
        iend = data.find(b"IEND")
        if iend >= 0:
            trail = data[iend + 12 :]
            if trail:
                results["has_appended"] = True
                results["appended_bytes"] = len(trail)
                results["hex_preview"] = trail[:100].hex()
                try:
                    results["text_preview"] = trail[:500].decode(
                        "utf-8", errors="replace"
                    )
                except:
                    pass

    elif image_path.lower().endswith((".jpg", ".jpeg")):
        eoi = data.rfind(b"\xff\xd9")
        if eoi >= 0:
            trail = data[eoi + 2 :]
            if trail:
                results["has_appended"] = True
                results["appended_bytes"] = len(trail)
                results["hex_preview"] = trail[:100].hex()

    return results


def idat_chunk_analysis(image_path):
    """Analyze PNG IDAT chunk uniformity."""
    if not image_path.lower().endswith(".png"):
        return {"skipped": "not a PNG"}

    with open(image_path, "rb") as f:
        data = f.read()

    pos = 8
    chunks = []
    while pos < len(data) - 12:
        length = struct.unpack(">I", data[pos : pos + 4])[0]
        ctype = data[pos + 4 : pos + 8].decode("ascii", errors="replace")
        chunks.append((ctype, length))
        pos += 12 + length

    idats = [c for c in chunks if c[0] == "IDAT"]
    sizes = [c[1] for c in idats]

    return {
        "chunk_count": len(idats),
        "sizes": sizes[:10],
        "all_same_size": len(set(sizes)) == 1,
        "suspicious": len(set(sizes)) == 1 and len(idats) > 3,
        "interpretation": "Uniform chunk sizes — possible custom stego"
        if len(set(sizes)) == 1 and len(idats) > 3
        else "Normal PNG compression",
    }


def run_detection(image_path, methods="all"):
    """Run full detection pipeline on an image."""
    print(f"\n{'=' * 60}")
    print(f"STEGANALYSIS: {os.path.basename(image_path)}")
    print(f"{'=' * 60}")

    img = Image.open(image_path)
    print(f"  Format: {img.format}, Mode: {img.mode}, Size: {img.size}")

    results = {}

    # 1. Appended data
    print(f"\n  [1/7] Appended data check...")
    results["appended"] = appended_data_check(image_path)
    if results["appended"]["has_appended"]:
        print(f"    ** APPENDED DATA: {results['appended']['appended_bytes']} bytes")

    # 2. IDAT chunk analysis (PNG)
    print(f"  [2/7] Chunk analysis...")
    results["chunks"] = idat_chunk_analysis(image_path)
    if results["chunks"].get("suspicious"):
        print(f"    ** UNIFORM IDAT CHUNKS")

    # 3. LSB ratio
    print(f"  [3/7] LSB ratio analysis...")
    results["lsb_ratio"] = lsb_ratio_analysis(image_path)
    for ch, r in results["lsb_ratio"].items():
        flag = " **" if r["suspicious"] else ""
        print(f"    {ch}: ratio={r['lsb_ratio']}{flag}")

    # 4. Chi-square
    print(f"  [4/7] Chi-square test...")
    results["chi_square"] = chi_square_lsb(image_path)
    for ch, r in results["chi_square"].items():
        flag = " **" if r["suspicious"] else ""
        print(f"    {ch}: chi={r['chi_square']}{flag}")

    # 5. Bit-plane entropy
    print(f"  [5/7] Bit-plane entropy...")
    results["entropy"] = bit_plane_entropy(image_path)
    for ch, r in results["entropy"].items():
        flag = " **" if r["suspicious"] else ""
        print(f"    {ch}: LSB entropy={r['lsb_entropy']}{flag}")

    # 6. Spatial autocorrelation
    print(f"  [6/7] Spatial autocorrelation...")
    results["autocorr"] = spatial_autocorrelation(image_path)
    for ch, r in results["autocorr"].items():
        flag = " **" if r["suspicious"] else ""
        print(
            f"    {ch}: H={r['horizontal']} V={r['vertical']} D={r['diagonal']}{flag}"
        )

    # 7. DCT analysis (JPEG)
    print(f"  [7/7] DCT coefficient analysis...")
    results["dct"] = dct_coefficient_analysis(image_path)
    if "skipped" not in results["dct"]:
        flag = (
            " **"
            if results["dct"]["f5_suspicious"] or results["dct"]["jsteg_suspicious"]
            else ""
        )
        print(f"    +1/-1 ratio: {results['dct']['plus1_minus1_ratio']}{flag}")
        print(f"    Zero rate: {results['dct']['zero_rate']}")
        print(f"    {results['dct']['interpretation']}")

    # Overall assessment
    suspicious_count = 0
    findings = []

    if results["appended"]["has_appended"]:
        suspicious_count += 1
        findings.append("Appended data after image marker")
    if results["chunks"].get("suspicious"):
        suspicious_count += 1
        findings.append("Uniform IDAT chunk sizes")
    for ch, r in results["lsb_ratio"].items():
        if r["suspicious"]:
            suspicious_count += 1
            findings.append(f"Channel {ch} LSB ratio skewed ({r['lsb_ratio']})")
            break
    for ch, r in results["entropy"].items():
        if r["suspicious"]:
            suspicious_count += 1
            findings.append(
                f"Channel {ch} LSB entropy near maximum ({r['lsb_entropy']})"
            )
            break
    if results["dct"].get("f5_suspicious"):
        suspicious_count += 1
        findings.append("Possible F5 matrix encoding in DCT coefficients")
    if results["dct"].get("jsteg_suspicious"):
        suspicious_count += 1
        findings.append("Possible JSteg embedding in DCT coefficients")

    print(f"\n  {'=' * 40}")
    print(f"  OVERALL: {suspicious_count} suspicious indicators")
    if suspicious_count == 0:
        print(f"  Assessment: CLEAN — no steganographic indicators detected")
        print(
            f"  Note: Encrypted steganography (HIDEAGEM, OutGuess) may evade detection"
        )
    elif suspicious_count <= 2:
        print(f"  Assessment: LOW SUSPICION — minor anomalies detected")
    elif suspicious_count <= 4:
        print(f"  Assessment: MODERATE SUSPICION — multiple indicators present")
    else:
        print(f"  Assessment: HIGH SUSPICION — strong steganographic indicators")

    for f in findings:
        print(f"    - {f}")

    return results


def main():
    parser = argparse.ArgumentParser(description="Steganalysis Detection Engine")
    parser.add_argument("--input", "-i", required=True, help="Image file or directory")
    parser.add_argument(
        "--recursive", "-r", action="store_true", help="Scan directory recursively"
    )
    parser.add_argument(
        "--method", "-m", default="all", help="Detection method (all, lsb, dct, chi)"
    )
    args = parser.parse_args()

    if os.path.isdir(args.input):
        exts = (".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif")
        files = []
        if args.recursive:
            for root, _, fnames in os.walk(args.input):
                for f in fnames:
                    if f.lower().endswith(exts):
                        files.append(os.path.join(root, f))
        else:
            files = [
                os.path.join(args.input, f)
                for f in os.listdir(args.input)
                if f.lower().endswith(exts)
            ]

        print(f"Scanning {len(files)} images...")
        for f in sorted(files):
            try:
                run_detection(f, args.method)
            except Exception as e:
                print(f"\n  ERROR: {f}: {e}")
    else:
        run_detection(args.input, args.method)


if __name__ == "__main__":
    main()
