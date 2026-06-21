# Steganalysis Skill

Encode, decode, detect, and analyze steganographic content in images. A comprehensive toolkit for steganography and steganalysis, built as an [aidevops](https://github.com/marcusquinn/aidevops) skill.

Covers spatial-domain, frequency-domain, and modern encrypted steganography including HIDEAGEM, F5, JSteg, spread spectrum, and LSB matching techniques.

## Installation

### 1. Clone the repo

```bash
git clone https://github.com/vRobM/steganalysis-skill.git
cd steganalysis-skill
```

### 2. Install Python dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Register as an agent skill

Install into whichever runtime(s) you use:

#### OpenCode

```bash
ln -s "$(pwd)" ~/.config/opencode/skills/steganalysis
```

#### Claude Code

```bash
ln -s "$(pwd)" ~/.claude/skills/steganalysis
```

#### Codex

```bash
ln -s "$(pwd)" ~/.codex/skills/steganalysis
```

#### Hermes Agent

```bash
ln -s "$(pwd)" ~/.hermes/skills/steganalysis
```

After linking, restart your agent session. The skill activates automatically when you mention steganography, steganalysis, hiding data in images, or detecting hidden content.

### Dependencies

- **numpy**, **pillow**, **scipy** — core image processing
- **opencv-python**, **scikit-image**, **pandas** — enhanced analysis (optional)
- **aletheia** — steganalysis framework integration

## Usage

### Encode (Hide Data)

```bash
# LSB Replacement — simple, detectable
python3 scripts/steg_encode.py --cover image.png --payload secret.txt --output stego.png

# LSB Matching — harder to detect
python3 scripts/steg_encode.py --cover image.png --payload secret.txt --output stego.png --method lsb_matching

# DCT embedding — frequency domain
python3 scripts/steg_encode.py --cover image.jpg --payload secret.txt --output stego.jpg --method dct
```

### Decode (Extract Data)

```bash
python3 scripts/steg_decode.py --input stego.png --output extracted/
```

### Detect Steganography

```bash
# Single image — runs all detection methods
python3 scripts/steg_detect.py --input suspicious.png

# Specific method
python3 scripts/steg_detect.py --input image.png --method chi_square
python3 scripts/steg_detect.py --input image.png --method rs
python3 scripts/steg_detect.py --input image.png --method spa
python3 scripts/steg_detect.py --input image.png --method weighted
python3 scripts/steg_detect.py --input image.jpg --method calibration

# DCT LSB Bias (primary test for JPEGs)
python3 scripts/dct_lsb_bias.py image.jpg
```

### Batch Scan

```bash
python3 scripts/steg_scan.py --directory ./images/ --recursive
```

### Analysis Tools

```bash
# DCT coefficient analysis
python3 scripts/dct_analyze.py image.jpg

# LSB plane visualization
python3 scripts/lsb_visualize.py --input image.png --channel all

# Cross-image correlation (detect common payloads)
python3 scripts/cross_correlate.py --images *.jpg
```

### Aletheia Integration

```bash
# Auto-detect all methods
aletheia auto images/

# RS analysis
aletheia rs image.png

# SPA analysis
aletheia spa image.png
```

## Detection Methods

| Method | Targets | Format |
|--------|---------|--------|
| Chi-Square | LSB Replacement | Any |
| RS Analysis | LSB Replacement | PNG |
| SPA | LSB Matching | PNG |
| Weighted Stego | LSB Replacement/Matching | PNG |
| F5 Calibration | F5 embedding | JPEG |
| DCT LSB Bias | DCT-domain steganography | JPEG |

## Project Structure

```
steganalysis-skill/
├── SKILL.md                 # Full skill documentation (aidevops)
├── README.md                # This file
├── requirements.txt         # Python dependencies
├── scripts/
│   ├── steg_encode.py       # Encode/hide data in images
│   ├── steg_decode.py       # Decode/extract hidden data
│   ├── steg_detect.py       # Multi-method detection engine
│   ├── steg_scan.py         # Batch directory scanner
│   ├── dct_analyze.py       # DCT coefficient analysis
│   ├── dct_lsb_bias.py      # DCT LSB bias detection (JPEGs)
│   ├── lsb_visualize.py     # LSB plane visualization
│   └── cross_correlate.py   # Cross-image correlation
├── reference/
│   ├── methods.md           # Steganographic method reference
│   ├── hideagem.md          # HIDEAGEM technical deep-dive
│   ├── compression-resistant.md  # Compression-resistant techniques
│   └── detection-signatures.md   # Known detection signatures
└── templates/
    ├── report-template.md   # Analysis report template
    └── expert-questions.md  # Expert review question template
```

## Supported Techniques

**Encoding:**
- LSB Replacement (1-4 bits per channel)
- LSB Matching (±1 modification, harder to detect)
- DCT coefficient embedding (JPEG domain)

**Detection:**
- Chi-square statistical test
- Regular-Singular (RS) analysis
- Sample Pair Analysis (SPA)
- Weighted Stego analysis
- F5 calibration attack
- DCT LSB bias detection

## License

MIT
