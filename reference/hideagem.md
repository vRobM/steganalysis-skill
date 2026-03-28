# HIDEAGEM Technical Reference

## Overview

HIDEAGEM is an open-source experimental steganography platform by CYBERGEM (UltraTerm). Written in C++ with Python CLI, WASM browser, and ComfyUI integration.

- **Web:** https://hideagem.com
- **Source:** https://github.com/CYBERGEM777/HIDEAGEM
- **Manual:** https://cybergem.net/blog/2023/hideagem-v1/
- **License:** MAGIC AI License (permissive)

## Core Algorithm: GEMMA_RANDOM

Spatial domain LSB Matching algorithm that visits pixels in an unpredictable sequence determined by the encryption key.

### Embedding Process

1. Generate 512-bit key from password via Argon2id (64MB memory, INTERACTIVE params)
2. Split key into two 256-bit slices (Fire Keys)
3. Seed RNG with first Fire Key
4. For each bit of encrypted payload:
   - RNG emits random pixel index + random channel order
   - Read pixel, randomly +1 or -1 to match target LSB (LSB Matching)
   - Consume pixel bytes + RNG output into key (mutates Fire Key)
   - Cycle to next Fire Key slice
5. Append 192-bit nonce to end of encrypted stream (decryption impossible until full extraction)

### Key Properties

- **Same password + different image = different pixel set** (key consumes cover image bits)
- **Same password + same image + different payload = different pixel set** (key consumes payload bits)
- **Sequential extraction required** — can't skip pixels, can't parallelize
- **Full 512-bit key required** — can't brute-force individual 256-bit slices
- **Tamper-proof** — any pixel mutation in Gem pixels → extraction failure

## 512-bit Cycle Key

```
Password → Argon2id → 512-bit block
                      ├─ Slice A (256 bits)
                      └─ Slice B (256 bits)

Each cycle:
  Fire Key = current_slice XOR BLAKE2b(food_pile)
  RNG re-seeded with Fire Key
  Key slice order shuffled by RNG
```

### Key Mutation

The key consumes bits from its environment:
- Cover image pixel bytes (after embedding)
- RNG output bytes
- Arbitrary bytes via `consume()` function

All consumed bytes go to a "Food Pile" which is BLAKE2b-hashed into a 256-bit "Key Food" array. The Fire Key = current slice XOR Key Food.

## DragonRNG

XChaCha20 stream cipher-based CSPRNG:
- 256-bit seed + 192-bit nonce
- O(1) fast-forwarding via warp coordinates
- n-dimensional IV generation for parallel-safe streams
- All output consumed internally by the key

## Gem Stream Format

```
[Encrypted Gem Files] + [192-bit nonce at END]
```

Each Gem Shard:
```
[64-bit obfuscated length] + [XChaCha20-Poly1305 encrypted body] + [192-bit nonce]
```

The byte count is obfuscated so ANY random 64-bit integer reads as a valid count within remaining capacity. This prevents early-exit brute-force attacks.

## Time Trap (Brute-Force Resistance)

Probabilistic key stretching with levels 0-7:
- Correct password → normal speed at specified level
- Wrong password → 50% chance of slowest verification (level 7, minutes)

| Level | Wrong Password Slow Rate |
|-------|------------------------|
| 7 | 50% (1/2) |
| 6 | 25% (1/4) |
| 5 | 12.5% (1/8) |
| 4 | 6.25% (1/16) |
| 3 | 3.125% (1/32) |
| 2 | 1.5625% (1/64) |
| 1 | 0.78125% (1/128) |
| 0 | 0.39062% (1/256) |

**Critical:** The Time Trap level must remain secret — knowing it allows bypass.

## Detection Characteristics

| Property | Value |
|----------|-------|
| Algorithm | LSB Matching (not LSB Replacement) |
| Chi-square detectable | No |
| RS analysis | Partially effective at high payload |
| SPA detection | Most effective method |
| SRM detection threshold | ~11KB per megapixel (1-bit mode) |
| Metadata markers | None (header encrypted) |
| Format requirement | PNG/TIFF only (lossless) |
| Fragility | Complete — any re-encoding destroys data |

## CLI Usage

```bash
# Hide files
python HIDEAGEM.py hide --ocean cover.png --files secret.txt --output out/ --password "key"

# Find files
python HIDEAGEM.py find --ocean stego.png --output out/ --password "key"

# With Time Trap
python HIDEAGEM.py hide --ocean cover.png --files secret.txt --output out/ --password "key" --timetrap 3
python HIDEAGEM.py find --ocean stego.png --output out/ --password "key" --timetrap

# Demo / tests
python HIDEAGEM.py demo
python HIDEAGEM.py unit
```

## Dependencies

- **libsodium** — all crypto operations (Argon2id, XChaCha20-Poly1305, BLAKE2b)
- **utf8proc** — Unicode password normalization
- **miniz** — zlib compression before encryption
