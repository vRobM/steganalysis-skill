# Steganography Methods Reference

## Spatial Domain Methods

### LSB Replacement
- **Year:** ~1990s
- **Mechanism:** Replace least significant bit(s) of pixel channels with message bits
- **Capacity:** width × height × channels × bits bytes
- **Robustness:** None — any compression destroys data
- **Detection:** Easy — chi-square test on ±1 pairs
- **Tools:** OpenStego, StegHide, S-Tools

### LSB Matching
- **Year:** ~2000s
- **Mechanism:** Randomly +1 or -1 to make LSB match message bit
- **Capacity:** Same as LSB Replacement
- **Robustness:** None — any compression destroys data
- **Detection:** Medium — requires SPA or SRM analysis
- **Tools:** HIDEAGEM (GEMMA_RANDOM)

### Pixel Value Differencing (PVD)
- **Mechanism:** Embed more bits in high-contrast areas (edge pixels)
- **Capacity:** Variable — higher in textured regions
- **Detection:** Histogram analysis of difference values

### Adaptive LSB
- **Mechanism:** Use Human Visual System model to embed more in noisy areas
- **Capacity:** Higher than fixed LSB for same visual quality
- **Detection:** Harder — adapts to image content

## Frequency Domain Methods

### DCT Coefficient Modification

#### JSteg (1993-1997)
- **Mechanism:** Embed in quantized DCT coefficients (skip zeros and ones)
- **Capacity:** Medium
- **Robustness:** Survives JPEG recompression at same quality
- **Detection:** Chi-square on DCT coefficient pairs

#### F5 (2001)
- **Mechanism:** Decrement coefficient magnitudes, encode via sign
- **Capacity:** Medium
- **Robustness:** Survives JPEG recompression
- **Detection:** Histogram hollow effect, calibration

#### OutGuess (2001)
- **Mechanism:** Embed in DCT while preserving first-order statistics
- **Capacity:** Lower (correction overhead)
- **Robustness:** Survives JPEG recompression
- **Detection:** Very difficult

#### nsF5 (2007)
- **Mechanism:** F5 with wet paper codes
- **Capacity:** Higher than F5
- **Robustness:** Survives JPEG recompression
- **Detection:** Calibration only

### Spread Spectrum

#### Cox et al. (1997)
- **Mechanism:** Modulate watermark onto pseudo-random sequence in perceptually significant DCT components
- **Capacity:** Low (10-100 bits)
- **Robustness:** Very high — survives filtering, compression, D/A conversion
- **Detection:** Requires original image
- **Used by:** Digimarc, commercial systems

#### SSIS (1999)
- **Mechanism:** Spread Spectrum Image Steganography — higher capacity than Cox
- **Capacity:** Medium
- **Robustness:** High
- **Detection:** Difficult

## Transform Domain Methods

### DWT (Discrete Wavelet Transform)
- **Mechanism:** Embed in wavelet coefficients
- **Capacity:** Medium
- **Robustness:** Good against compression
- **Detection:** Wavelet coefficient analysis

### DFT (Discrete Fourier Transform)
- **Mechanism:** Embed in phase or magnitude of Fourier coefficients
- **Capacity:** Low-medium
- **Robustness:** Phase coding survives compression well
- **Detection:** Phase analysis

## Audio Steganography

### LSB Audio
- **Mechanism:** Replace LSBs of audio samples
- **Capacity:** High
- **Robustness:** None — MP3/AAC destroys
- **Detection:** Same as image LSB

### Echo Hiding
- **Mechanism:** Add micro-echoes with specific delays encoding bits
- **Capacity:** Low
- **Robustness:** Survives lossy compression
- **Detection:** Autocorrelation analysis

### Phase Coding
- **Mechanism:** Modify phase spectrum to encode data
- **Capacity:** Medium
- **Robustness:** Good — phase is preserved in compression
- **Detection:** Phase analysis

### Spread Spectrum Audio
- **Mechanism:** Modulate data onto pseudo-random sequence in audio spectrum
- **Capacity:** Low
- **Robustness:** High
- **Detection:** Difficult

### Sine-Wave Speech
- **Mechanism:** Encode speech as sine waves, requires primer to decode
- **Capacity:** Variable
- **Robustness:** Survives compression if frequencies preserved
- **Detection:** Spectral analysis

## Modern Encrypted Steganography

### HIDEAGEM (2019+)
- **Algorithm:** GEMMA_RANDOM — LSB Matching with 512-bit Cycle Key
- **Encryption:** XChaCha20-Poly1305
- **Key derivation:** Argon2id (INTERACTIVE params)
- **Capacity:** 1-24 bits per pixel
- **Format:** PNG/TIFF only
- **Detection:** SPA/SRM at ~11KB/MP
- **Source:** https://github.com/CYBERGEM777/HIDEAGEM

### DeepStego (AI-based)
- **Mechanism:** Neural network encodes data in learned features
- **Capacity:** Variable
- **Robustness:** Can be trained for compression resistance
- **Detection:** Adversarial detection models
- **Note:** Emerging threat — no reliable detection methods yet
