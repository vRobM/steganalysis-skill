# Compression-Resistant Steganography Methods

## Overview

Most steganographic methods are destroyed by lossy compression (JPEG, MP3, AAC). Only frequency-domain techniques survive because they embed in the same transform coefficients that compression preserves.

## Methods That Survive JPEG Recompression

### 1. Jpeg-Jsteg (1993-1997)
- **Mechanism:** Embeds between the quantization step and Huffman coding in the JPEG pipeline
- **How:** Modifies quantized DCT coefficients directly — the hidden data IS part of the compressed representation
- **Capacity:** Medium (depends on image complexity)
- **Detection:** ±1 coefficient pair imbalance (chi-square test)
- **Limitation:** Only survives recompression at same or higher quality level

### 2. F5 (2001)
- **Mechanism:** Decrements coefficient magnitudes and encodes data via sign patterns
- **How:** Matrix encoding (n,k) minimizes the number of coefficient changes per embedded bit
- **Capacity:** Medium
- **Detection:** Histogram "hollow" effect around zero; calibration analysis
- **Advantage:** Maintains ±1 balance (harder to detect than JSteg)

### 3. Spread Spectrum (Cox et al., 1997)
- **Mechanism:** Embeds in the N most perceptually significant DCT coefficients
- **How:** Modulates watermark bits onto pseudo-random sequences (like CDMA radio)
- **Capacity:** Low (10-100 bits typically)
- **Detection:** Very difficult — requires original image for extraction
- **Robustness:** Survives filtering, compression, D/A conversion, cropping
- **Used by:** Digimarc, commercial watermarking systems

### 4. OutGuess (2001)
- **Mechanism:** Embeds in DCT coefficients while preserving first-order statistics
- **How:** Uses a pseudo-random number generator to select coefficients, then corrects statistical distribution
- **Capacity:** Medium (lower than JSteg due to correction overhead)
- **Detection:** Very difficult — preserves histogram shape
- **Advantage:** Defeats chi-square and histogram analysis

### 5. nsF5 (2007)
- **Mechanism:** Improved F5 using wet paper codes
- **How:** Some coefficients are marked as "non-modifiable" (wet) and the algorithm works around them
- **Capacity:** Higher than F5 for same detectability
- **Detection:** Calibration-based methods only

## Methods That Do NOT Survive Compression

| Method | Why It Fails |
|--------|-------------|
| LSB Replacement | Spatial domain — JPEG quantization destroys LSBs |
| LSB Matching | Same — pixel values change during compression |
| HIDEAGEM (GEMMA_RANDOM) | Spatial domain LSB Matching — PNG only |
| S-Tools | Spatial domain |
| StegHide | Spatial domain with PRNG pixel selection |

## Audio Compression Resistance

### Sine-Wave Speech Encoding
- Encode speech as sine waves at specific frequencies
- Survives MP3/AAC compression if frequencies are in the preserved band
- Requires a "primer" to decode (listener must know the encoding pattern)
- Brian Roemmele claims to use this method

### Echo Hiding
- Embed data as micro-echoes with specific delays
- Survives lossy compression because echoes are perceptually natural
- Capacity: Low
- Detection: Autocorrelation analysis

### Phase Coding
- Embed data in the phase spectrum of audio
- Survives compression better than amplitude modifications
- Capacity: Medium
- Detection: Phase analysis

## Choosing a Method

| Requirement | Best Method |
|-------------|-------------|
| Must survive JPEG | Spread Spectrum or F5 |
| High capacity | JSteg or nsF5 |
| Hard to detect | OutGuess or Spread Spectrum |
| Must survive any compression | Spread Spectrum (DCT) or Digimarc |
| Maximum capacity, lossless only | LSB Matching (HIDEAGEM) |
| Audio steganography | Echo hiding or phase coding |
