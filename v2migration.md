# V2 Migration: PHP to Python with spaCy Support

## Overview
This document describes the migration from the PHP-based FreeLing service (v1) to a Python Flask-based service (v2) that incorporates spaCy for improved POS tagging in non-Spanish languages.

## Motivation
- FreeLing's POS tagging quality for non-Spanish languages (English, French) was not meeting stakeholder expectations
- spaCy provides better accuracy for these languages with actively maintained models

## Architecture Changes

### V1 (PHP)
```
Client → analyze.php → functions.php → analyzer_client → FreeLing daemon
```

### V2 (Python)
```
Client → Flask app.py → Language Router
                            ├── Spanish → FreeLing (via analyzer_client)
                            └── Other → spaCy (native Python)
```

## API Compatibility

### Endpoint
- **V1**: `POST /analyze.php`
- **V2**: `POST /analyze` (also supports `/analyze.php` for backward compatibility)

### Parameters (unchanged)
| Parameter | Values | Required |
|-----------|--------|----------|
| `file` | Text file (UTF-8) | Yes |
| `outf` | `tagged`, `parsed`, `dep` | Yes |
| `format` | `plain`, `json`, `html` | Yes |
| `lang` | `es`, `en`, `fr`, `de`, `it`, `pt`, `auto` | No (default: `es`) |

### JSON Output Format (unchanged)
The JSON output format remains identical for backward compatibility. See examples below.

#### Tagged output
```json
[
  [
    {"token": "Hello", "lemma": "hello", "tag": "UH", "prob": "1.0"},
    {"token": "world", "lemma": "world", "tag": "NN", "prob": "1.0"}
  ]
]
```

#### Dep output
```json
[
  [
    {
      "type": "ROOT",
      "subtype": "root",
      "content": {"token": "...", "lemma": "...", "tag": "..."},
      "children": [...]
    }
  ]
]
```

## Breaking Changes

### 1. Parsed analysis limited to Spanish
The `parsed` (constituency parsing) analysis type is only available for Spanish. Requests for `parsed` with non-Spanish languages will return:
```json
{"error": "Constituency parsing (parsed) is only available for Spanish. Use 'tagged' or 'dep' for other languages."}
```

### 2. POS Tag differences
Each language uses its native tagset:
- **Spanish (FreeLing)**: EAGLES tagset
- **English (spaCy)**: Penn Treebank tagset
- **French (spaCy)**: French UD tagset
- **German (spaCy)**: German UD tagset

## New Languages Supported
| Language | Code | Analysis Types |
|----------|------|----------------|
| Spanish | `es` | tagged, parsed, dep |
| English | `en` | tagged, dep |
| French | `fr` | tagged, dep |
| German | `de` | tagged, dep |
| Italian | `it` | tagged, dep |
| Portuguese | `pt` | tagged, dep |

## Deployment

### Dependencies
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python -m spacy download fr_core_news_sm
python -m spacy download de_core_news_sm
python -m spacy download it_core_news_sm
python -m spacy download pt_core_news_sm
```

### Running the service
```bash
# Development
python app.py

# Production (with gunicorn)
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### FreeLing daemon
The FreeLing daemon must still be running for Spanish analysis:
```bash
./start.sh  # Starts FreeLing on configured ports
```

## File Structure (V2)
```
servicio-freeling/
├── app.py                    # Flask application
├── analyzers/
│   ├── __init__.py
│   ├── base.py               # Base analyzer interface
│   ├── freeling.py           # FreeLing wrapper (Spanish)
│   └── spacy_analyzer.py     # spaCy wrapper (other languages)
├── formatters.py             # Output formatting
├── templates/
│   └── index.html            # Web UI
├── requirements.txt          # Python dependencies
├── v2migration.md            # This file
└── (legacy PHP files)        # Kept for reference
```

## Rollback
To rollback to V1, simply point the web server back to `analyze.php`. The PHP files are preserved and functional.
