# Expert Review Questions — Steganalysis Case

Use this template when submitting analysis findings for expert review. Customize the questions based on the specific findings.

---

## Case Context

**Subject:** [description of subject/claim]
**Samples:** [N] images from [source, date range]
**Methods Applied:** [list of analysis methods]
**Overall Verdict:** [CONFIRMED / LIKELY / POSSIBLE / CLEAN]

---

## Questions for Expert Review

### 1. Statistical Method Validity

[Describe the specific test and the observed results]

Is [test name] a valid diagnostic for [suspected method]? What false-positive rate would you expect for natural images at the observed compression levels (quality [Q])?

**Observed:** [specific metric value]
**Expected (natural):** [expected value]
**Deviation:** [deviation]

---

### 2. Combined Evidence Interpretation

Multiple tests agree on [verdict], but the evidence strength varies:

| Test | Result | Interpretation |
|------|--------|----------------|
| [Test 1] | [result] | [how to interpret] |
| [Test 2] | [result] | [how to interpret] |
| [Test 3] | [result] | [how to interpret] |

How would you weight the combined evidence? Are there cases where these tests could all agree on a false positive?

---

### 3. Tool or Method Identification

Based on the observed signatures:

- [specific signature 1]
- [specific signature 2]
- [specific signature 3]

What steganographic tool or method is most consistent with these findings?

---

### 4. Compression Resilience

The images show signs of [observed characteristic]. Could this be explained by:
- [ ] Re-compression artifact (JPEG re-save)
- [ ] Camera/processing pipeline signature
- [ ] Natural image content characteristics
- [ ] Steganographic embedding

What analysis would distinguish between these?

---

### 5. Capacity Estimation

**Claimed:** [e.g., 500,000 characters per image]
**Image specs:** [dimensions, file size]

Is this capacity feasible? What embedding rate would be required?

---

### 6. Additional Analyses Recommended

What tests or techniques would you recommend to:
- [ ] Strengthen the evidence
- [ ] Rule out false positives
- [ ] Identify the specific tool/method
- [ ] Estimate payload size

---

### 7. Method-Specific Questions

[For specific methods, e.g., F5:]

**F5 Calibration:** Chi-square between original and cropped-reference was [value]. Is this consistent with F5 matrix encoding, or could it arise from [alternative explanation]?

**RS Analysis:** RS statistics of [values] were observed on already-compressed JPEG images. Can JPEG compression alone produce RS statistics this extreme?

---

### 8. Limitations Acknowledgment

The following limitations apply to this analysis:

- [limitation 1]
- [limitation 2]
- [limitation 3]

How do these limitations affect the confidence of our conclusions?

---

## Submission Instructions

1. Fill in the case context above with your specific findings
2. Customize questions 1-8 based on your analysis
3. Submit to [relevant forum/expert contact]
4. Document expert responses in the analysis report
5. Update conclusions based on expert feedback
