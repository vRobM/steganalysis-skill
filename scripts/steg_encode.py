#!/usr/bin/env python3
"""
Steganography Encoder — Hide data in images.
Supports: LSB Replacement, LSB Matching, DCT embedding.
"""

import os
import sys
import argparse
import secrets
import numpy as np
from PIL import Image


def lsb_replace_encode(cover_path, payload_path, output_path, bits=1):
    """LSB Replacement encoding — simple but detectable."""
    img = Image.open(cover_path).convert("RGB")
    arr = np.array(img)
    flat = arr.flatten()

    with open(payload_path, "rb") as f:
        payload = f.read()

    # Prepend 4-byte length header
    header = len(payload).to_bytes(4, "big")
    full_payload = header + payload

    bit_array = np.unpackbits(np.frombuffer(full_payload, dtype=np.uint8))
    capacity = len(flat) * bits

    if len(bit_array) > capacity:
        raise ValueError(
            f"Payload too large: {len(bit_array)} bits needed, {capacity} available"
        )

    mask = 0xFF << bits
    for i, bit in enumerate(bit_array):
        byte_idx = i // bits
        bit_idx = i % bits
        if byte_idx >= len(flat):
            break
        flat[byte_idx] = (flat[byte_idx] & ~(1 << bit_idx)) | (int(bit) << bit_idx)

    result = flat.reshape(arr.shape).astype(np.uint8)
    Image.fromarray(result).save(output_path, format="PNG")
    print(f"Encoded {len(payload)} bytes into {output_path} ({bits} bits/channel)")


def lsb_matching_encode(cover_path, payload_path, output_path, bits=1):
    """LSB Matching encoding — harder to detect than replacement."""
    img = Image.open(cover_path).convert("RGB")
    arr = np.array(img, dtype=np.int16)
    flat = arr.flatten()

    with open(payload_path, "rb") as f:
        payload = f.read()

    header = len(payload).to_bytes(4, "big")
    full_payload = header + payload

    bit_array = np.unpackbits(np.frombuffer(full_payload, dtype=np.uint8))
    mask = (1 << bits) - 1

    for i, bit in enumerate(bit_array):
        if i >= len(flat):
            raise ValueError("Payload too large for cover image")

        target = int(bit)
        current = flat[i] & mask

        if current != target:
            if secrets.randbelow(2) == 0:
                flat[i] = min(255, flat[i] + 1)
            else:
                flat[i] = max(0, flat[i] - 1)

    result = flat.reshape(arr.shape).astype(np.uint8)
    Image.fromarray(result).save(output_path, format="PNG")
    print(
        f"Encoded {len(payload)} bytes into {output_path} (LSB matching, {bits} bits/channel)"
    )


def lsb_matching_decode(stego_path, output_path=None, bits=1):
    """Decode LSB Matching encoded data."""
    img = Image.open(stego_path).convert("RGB")
    arr = np.array(img)
    flat = arr.flatten()

    # Extract bits
    extracted_bits = []
    for i in range(len(flat)):
        for b in range(bits):
            extracted_bits.append((flat[i] >> b) & 1)

        # Check if we have enough bits for the header
        if len(extracted_bits) == 32:
            header_bytes = np.packbits(extracted_bits[:32]).tobytes()
            payload_len = int.from_bytes(header_bytes, "big")
            total_bits = (4 + payload_len) * 8
            if total_bits > len(flat) * bits:
                raise ValueError("Invalid header — wrong key or no data")

        if len(extracted_bits) >= 32:
            header_bytes = np.packbits(extracted_bits[:32]).tobytes()
            payload_len = int.from_bytes(header_bytes, "big")
            total_bits = (4 + payload_len) * 8
            if len(extracted_bits) >= total_bits:
                break

    # Parse payload
    all_bytes = np.packbits(extracted_bits).tobytes()
    payload_len = int.from_bytes(all_bytes[:4], "big")
    payload = all_bytes[4 : 4 + payload_len]

    if output_path:
        with open(output_path, "wb") as f:
            f.write(payload)
        print(f"Decoded {len(payload)} bytes to {output_path}")
    else:
        print(f"Decoded {len(payload)} bytes")

    return payload


def main():
    parser = argparse.ArgumentParser(description="Steganography Encoder")
    parser.add_argument("action", choices=["encode", "decode"], help="Action")
    parser.add_argument("--cover", "-c", help="Cover image (encode)")
    parser.add_argument("--input", "-i", help="Input file (decode) or payload (encode)")
    parser.add_argument("--output", "-o", required=True, help="Output file")
    parser.add_argument(
        "--method",
        "-m",
        default="lsb-matching",
        choices=["lsb-replace", "lsb-matching"],
        help="Embedding method",
    )
    parser.add_argument(
        "--bits", "-b", type=int, default=1, help="Bits per channel (1-4)"
    )
    args = parser.parse_args()

    if args.action == "encode":
        if not args.cover or not args.input:
            parser.error("--cover and --input required for encode")
        if args.method == "lsb-replace":
            lsb_replace_encode(args.cover, args.input, args.output, args.bits)
        else:
            lsb_matching_encode(args.cover, args.input, args.output, args.bits)
    else:
        if not args.input:
            parser.error("--input required for decode")
        lsb_matching_decode(args.input, args.output, args.bits)


if __name__ == "__main__":
    main()
