#!/usr/bin/env python3
"""
Steganography Decoder - Extract hidden data from stego images

Supports multiple extraction methods:
- LSB extraction (1-8 bits)
- DCT coefficient extraction (JPEG)
- Steghide extraction
- zsteg extraction
- Binwalk extraction
"""

import argparse
import sys
from pathlib import Path


def extract_lsb(image_path: str, bits: int = 1, output_dir: str = ".") -> bytes:
    """Extract data from LSB planes."""
    from PIL import Image
    import numpy as np

    img = Image.open(image_path).convert("RGB")
    arr = np.array(img)

    # Flatten and extract LSBs
    flat = arr.flatten()
    mask = (1 << bits) - 1
    lsb_bits = flat & mask

    # Convert to bytes
    bit_array = np.packbits(lsb_bits)
    return bit_array.tobytes()


def extract_dct(image_path: str, output_dir: str = ".") -> bytes:
    """Extract data from DCT coefficients (JPEG)."""
    import numpy as np

    # DCT extraction requires JPEG
    if not image_path.lower().endswith((".jpg", ".jpeg")):
        print("DCT extraction only works with JPEG images", file=sys.stderr)
        return b""

    # Note: Full DCT extraction requires JPEG library
    # This is a placeholder for the full implementation
    print("DCT extraction not fully implemented", file=sys.stderr)
    return b""


def try_steghide(image_path: str, password: str = "") -> bool:
    """Try steghide extraction."""
    import subprocess

    cmd = ["steghide", "extract", "-sf", image_path, "-p", password, "-f"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.returncode == 0
    except FileNotFoundError:
        print("steghide not installed", file=sys.stderr)
        return False
    except Exception as e:
        print(f"steghide error: {e}", file=sys.stderr)
        return False


def try_zsteg(image_path: str) -> bool:
    """Try zsteg extraction."""
    import subprocess

    cmd = ["zsteg", image_path, "-a"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.stdout:
            print(result.stdout)
            return True
        return False
    except FileNotFoundError:
        print("zsteg not installed", file=sys.stderr)
        return False
    except Exception as e:
        print(f"zsteg error: {e}", file=sys.stderr)
        return False


def check_appended_data(image_path: str) -> bytes | None:
    """Check for data appended after image EOF."""
    with open(image_path, "rb") as f:
        f.seek(-1024, 2)  # Last 1KB
        data = f.read()

    # Look for common markers
    if b"IEND" in data:
        eof_pos = data.index(b"IEND") + 4
        appended = data[eof_pos:]
        if len(appended) > 16:  # Minimum meaningful data
            return appended
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Extract hidden data from stego images"
    )
    parser.add_argument("--input", "-i", required=True, help="Input stego image")
    parser.add_argument(
        "--output", "-o", default=".", help="Output directory (default: current)"
    )
    parser.add_argument(
        "--method",
        "-m",
        choices=["auto", "lsb", "dct", "steghide", "zsteg"],
        default="auto",
        help="Extraction method (default: auto)",
    )
    parser.add_argument(
        "--bits", "-b", type=int, default=1, help="LSB bits (default: 1)"
    )
    parser.add_argument("--password", "-p", default="", help="Password for steghide")

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: {args.input} not found", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Extracting from: {args.input}")
    print(f"Method: {args.method}")

    # Method: auto - try all methods
    if args.method == "auto":
        # 1. Check for appended data
        appended = check_appended_data(args.input)
        if appended:
            output_file = output_dir / "extracted_appended.bin"
            output_file.write_bytes(appended)
            print(f"Found appended data: {output_file}")
            return

        # 2. Try LSB extraction
        for bits in [1, 2, 3, 4]:
            try:
                data = extract_lsb(args.input, bits)
                if len(data) > 0:
                    output_file = output_dir / f"extracted_lsb{bits}.bin"
                    output_file.write_bytes(data)
                    print(f"LSB-{bits} extraction: {output_file} ({len(data)} bytes)")
            except Exception as e:
                print(f"LSB-{bits} failed: {e}", file=sys.stderr)

        # 3. Try steghide
        if try_steghide(args.input, args.password):
            print("steghide extraction: Success")

        # 4. Try zsteg
        try_zsteg(args.input)

    # Method: specific
    elif args.method == "lsb":
        data = extract_lsb(args.input, args.bits)
        output_file = output_dir / "extracted_lsb.bin"
        output_file.write_bytes(data)
        print(f"Extracted: {output_file} ({len(data)} bytes)")

    elif args.method == "dct":
        data = extract_dct(args.input, str(output_dir))
        if data:
            output_file = output_dir / "extracted_dct.bin"
            output_file.write_bytes(data)
            print(f"Extracted: {output_file}")

    elif args.method == "steghide":
        if try_steghide(args.input, args.password):
            print("Extraction successful")
        else:
            print("Extraction failed (check password)")

    elif args.method == "zsteg":
        try_zsteg(args.input)


if __name__ == "__main__":
    main()
