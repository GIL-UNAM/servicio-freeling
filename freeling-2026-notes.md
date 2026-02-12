# FreeLing Installation Notes (2026)

## Current Status

**Latest version:** FreeLing 4.2.1 (released September 2020)

**Project status:** Essentially unmaintained - no releases in 5+ years. The [GitHub releases page](https://github.com/TALP-UPC/FreeLing/releases) shows no activity since 2020.

## Interface Compatibility

The `analyzer` binary interface remains unchanged and is compatible with this project:

- `analyzer --server -p PORT --outlv <level>` for server mode ✓
- `analyzer_client localhost:PORT` for client communication ✓
- Output format (space-separated: `token lemma tag prob`) unchanged ✓

### Output Levels
- `--outlv tagged` - POS tagging
- `--outlv parsed` - Constituency parsing
- `--outlv dep` - Dependency parsing

## README.md Issues

The current README.md has outdated instructions:

| Component | README Version | Issue |
|-----------|---------------|-------|
| FreeLing .deb | 4.2 for Ubuntu Focal | Built for libboost 1.71.0, won't install on Ubuntu 22.04+ |
| PHP | 7.4 | EOL November 2022 (irrelevant for v2 Python migration) |
| Apache | Required for PHP | Not needed for v2 Flask/Gunicorn |

## Installation Options

### Option 1: Docker (Recommended for local testing)

Docker image available: [lcriadof/freeling:4.2](https://hub.docker.com/r/lcriadof/freeling) (last updated March 2023)

```bash
docker pull lcriadof/freeling:4.2

# Run FreeLing server for Spanish tagged analysis
docker run -d --name freeling-tagged -p 9999:9999 lcriadof/freeling:4.2 \
  analyzer --server -p 9999 --outlv tagged -f /usr/share/freeling/config/es.cfg

# Run FreeLing server for Spanish dependency parsing
docker run -d --name freeling-dep -p 9997:9997 lcriadof/freeling:4.2 \
  analyzer --server -p 9997 --outlv dep -f /usr/share/freeling/config/es.cfg

# Run FreeLing server for Spanish constituency parsing
docker run -d --name freeling-parsed -p 9998:9998 lcriadof/freeling:4.2 \
  analyzer --server -p 9998 --outlv parsed -f /usr/share/freeling/config/es.cfg
```

**Pros:** Works on any system, no library conflicts
**Cons:** Image is 2+ years old, requires Docker

### Option 2: Build from Source

```bash
# Install dependencies
sudo apt-get install build-essential automake autoconf libtool
sudo apt-get install libboost-dev libboost-regex-dev libboost-system-dev \
  libboost-program-options-dev libboost-thread-dev libboost-filesystem-dev \
  libicu-dev zlib1g-dev

# Clone and build
git clone https://github.com/TALP-UPC/FreeLing.git
cd FreeLing
mkdir build && cd build
cmake ..
make -j$(nproc)
sudo make install
```

**Pros:** Latest patches, works on any distro
**Cons:** Complex build process, ~30min compile time

### Option 3: Ubuntu 20.04 Container/VM

Use the official .deb packages inside an Ubuntu Focal environment:

```bash
# In Ubuntu 20.04 environment
wget https://github.com/TALP-UPC/FreeLing/releases/download/4.2/freeling-4.2-focal-amd64.deb
wget https://github.com/TALP-UPC/FreeLing/releases/download/4.2/freeling-langs-4.2.deb
sudo dpkg -i freeling-4.2-focal-amd64.deb freeling-langs-4.2.deb
```

**Pros:** Uses official packages, known working setup
**Cons:** Running outdated Ubuntu version

### Option 4: Skip FreeLing for Testing

Since the v2 migration routes non-Spanish languages to spaCy, you can test most functionality without FreeLing:

```bash
./install.sh  # Installs Flask + spaCy models
python app.py
# Test with lang=en, lang=fr, lang=de, lang=it, lang=pt
```

Spanish requests will fail, but all other languages work via spaCy.

**Pros:** Fastest setup, no FreeLing needed
**Cons:** Can't test Spanish analysis

## Port Configuration

Current `start.sh` port mapping:

| Language | Tagged | Parsed | Dep |
|----------|--------|--------|-----|
| Spanish (es) | 9999 | 9998 | 9997 |
| English (en) | 9995 | 9993 | 9996 |
| French (fr) | 9994 | 9992 | 9991 |

Note: The v2 migration only uses FreeLing for Spanish. English and French now use spaCy.

## References

- [FreeLing GitHub](https://github.com/TALP-UPC/FreeLing)
- [FreeLing Releases](https://github.com/TALP-UPC/FreeLing/releases)
- [FreeLing User Manual](https://freeling-user-manual.readthedocs.io/)
- [Docker Image: lcriadof/freeling](https://hub.docker.com/r/lcriadof/freeling)
- [Alternative Docker: hfoffani/docker-freeling](https://github.com/hfoffani/docker-freeling)
