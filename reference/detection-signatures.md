# Detection Signatures — Known Patterns

## Aletheia Detection Reference

### SPA (Sample Pair Analysis)
**Best for:** LSB Matching (HIDEAGEM, LSBM)
**Output:** Payload ratio per channel (0.0 = clean, >0.05 = detected)
**Interpretation:**
- Values > 0.05: hidden data present
- Equal values across R/G/B: systematic embedding (suspicious)
- Higher values: more payload
- `No hidden data found`: below threshold or clean

**Verified results (Brian Roemmele archive):**
- 2019 PNG (claimed stego): R=0.052, G=0.077, B=0.092 — DETECTED
- 2018 JPEG: R=0.151, G=0.151, B=0.151 — DETECTED (uniform)
- 2024 JPEG: R=0.099, G=0.099, B=0.099 — DETECTED (uniform)

### RS (Regular-Singular)
**Best for:** LSB Replacement
**Output:** Payload ratio per channel
**Limitation:** Cannot detect LSB Matching (HIDEAGEM-style)
**Verified:** Detected 2018 and 2019 JPEGs but NOT the 2019 PNG (LSB Matching)

### Calibration (F5)
**Best for:** F5, nsF5 JPEG steganography
**Needs:** Octave + JPEG Toolbox
**Mechanism:** Decompress → crop → recompress → compare DCT distributions

### SRM (Spatial Rich Models)
**Best for:** All spatial-domain methods (most sensitive)
**Needs:** External resources download (first run)
**Output:** 34,671 features for ML classification
**Note:** Requires trained classifier for prediction

## LSB Replacement Detection

**Method:** Chi-square test on pixel value pairs
**Signature:** Values v and v+1 should have similar frequencies in natural images. LSB replacement makes them equal, creating a detectable imbalance.
**Threshold:** Chi-square > 3.84 (p < 0.05) = suspicious; > 100 = confirmed
**Tools:** StegExpose, Aletheia, custom scripts

## LSB Matching Detection

**Method:** Sample Pair Analysis (SPA), SPA2, Spatial Rich Models (SRM)
**Signature:** No ±1 asymmetry (unlike replacement). Detected by analyzing correlations between pixel pairs and their residuals.
**Threshold:** SPA ratio deviation from 0.5; SRM ensemble classifier score
**Tools:** Aletheia (SPA, SRM), StegExpose (multiple features)
**Note:** HIDEAGEM uses LSB Matching — harder to detect than LSB Replacement

## F5 Detection

**Method:** Histogram analysis, calibration
**Signature:** "Hollow" effect — reduced number of ±1 coefficients compared to natural JPEG. The histogram shows a dip near zero.
**Calibration:** Decompress → crop 4 pixels → recompress → compare DCT distributions
**Tools:** Aletheia (calibration), custom DCT analysis

## JSteg Detection

**Method:** Chi-square test on DCT coefficient pairs
**Signature:** Same as LSB Replacement but in DCT domain — ±1 coefficient pair imbalance
**Threshold:** Chi-square > 3.84 in mid-frequency DCT coefficients
**Tools:** Stegdetect, Aletheia

## OutGuess Detection

**Method:** Very difficult — preserves first-order statistics
**Signature:** Second-order statistics (block correlations) may show anomalies
**Approach:** Calibration + comparison with double-compressed version
**Tools:** Aletheia (advanced), custom analysis

## Spread Spectrum Detection

**Method:** Requires original image for comparison
**Signature:** Energy distribution in perceptually significant components differs from original
**Approach:** Correlation with known watermark patterns
**Note:** Commercial systems (Digimarc) are designed to be undetectable without the key

## Appended Data Detection

**Method:** File structure analysis
**Signature:** Data after image end markers (IEND for PNG, EOI `\xff\xd9` for JPEG)
**Tools:** binwalk, foremost, hexdump, custom scripts
**Note:** Trivially detectable — not true steganography

## HIDEAGEM Detection

**Method:** SPA/SRM at high payload ratios
**Signature:** LSB Matching with encrypted payload — near-random LSB distribution
**Threshold:** ~11KB per megapixel in 1-bit mode triggers Aletheia
**Approach:**
1. Chi-square: ineffective (LSB Matching)
2. RS analysis: partially effective at high payload ratios
3. SPA: most effective method
4. SRM: best detection rates
5. No metadata markers — header encrypted
6. Fragility test: re-encode as JPEG — if data was present, it's now destroyed
