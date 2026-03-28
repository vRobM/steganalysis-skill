# Steganalysis Report — [SUBJECT]

**Date:** YYYY-MM-DD
**Analyst:** [NAME]
**Subject:** [DESCRIPTION]
**Samples:** [COUNT] images, [COUNT] audio files

---

## 1. Executive Summary

[2-3 sentence summary of findings]

## 2. Sample Inventory

| File | Format | Dimensions | Size | Source |
|------|--------|------------|------|--------|
| file1.png | PNG | WxH | XX KB | [source] |

## 3. Analysis Methods Applied

- [ ] Appended data check
- [ ] Metadata extraction
- [ ] LSB ratio analysis
- [ ] Chi-square test
- [ ] Bit-plane entropy
- [ ] Spatial autocorrelation
- [ ] DCT coefficient analysis (JPEG)
- [ ] Sample Pair Analysis
- [ ] RS Analysis
- [ ] Cross-image correlation
- [ ] Tool-based extraction (steghide, zsteg, binwalk)

## 4. Results

### 4.1 [Sample Name]

**Detection Summary:**
- Suspicious indicators: [N]
- Assessment: [CLEAN / LOW / MODERATE / HIGH]

**Detailed Findings:**

| Test | Result | Threshold | Verdict |
|------|--------|-----------|---------|
| LSB ratio (R) | 0.XXXX | 0.50 ± 0.02 | PASS/FAIL |
| Chi-square | X.XX | < 3.84 | PASS/FAIL |
| LSB entropy | 0.XXXX | < 0.99 | PASS/FAIL |
| Autocorrelation | 0.XXXX | > 0.505 | PASS/FAIL |
| DCT +1/-1 ratio | 0.XXXX | 0.45-0.55 | PASS/FAIL |

**Interpretation:**
[What the results mean in context]

## 5. Cross-Image Analysis

[If multiple samples: KL divergence matrix, shared encoder detection]

## 6. Conclusions

1. [Finding 1]
2. [Finding 2]
3. [Finding 3]

## 7. Limitations

- Encrypted steganography cannot be definitively ruled out by statistical tests
- Detection thresholds vary by image content
- [Method-specific limitations]

## 8. Recommendations

[Next steps, additional analyses, expert consultation needed]
