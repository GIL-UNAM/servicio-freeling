#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FreeLing + spaCy Text Analysis Service

A Flask-based web service for POS tagging, parsing, and dependency analysis.
- Spanish: Uses FreeLing
- Other languages: Uses spaCy
"""

import os
import tempfile
from flask import Flask, request, jsonify, render_template, Response

import langid

from analyzers import get_analyzer, SUPPORTED_LANGUAGES, SPACY_MODELS
from formatters import format_response

app = Flask(__name__)

# Configuration
ALLOWED_ANALYSIS_TYPES = ['tagged', 'parsed', 'dep']
ALLOWED_FORMATS = ['plain', 'json', 'html']


def detect_language(text: str) -> str:
    """Detect the language of the text using langid."""
    lang, _ = langid.classify(text)
    return lang


def http_error(status_code: int, message: str):
    """Return a JSON error response."""
    response = jsonify({"error": message})
    response.status_code = status_code
    return response


@app.route('/')
def index():
    """Render the main web interface."""
    return render_template('index.html',
                           endpoint=request.url_root + 'analyze',
                           languages=SUPPORTED_LANGUAGES,
                           spacy_languages=list(SPACY_MODELS.keys()))


@app.route('/analyze', methods=['POST'])
@app.route('/analyze.php', methods=['POST'])  # Backward compatibility
def analyze():
    """
    Main analysis endpoint.

    Parameters (query string or form):
        - outf: Analysis type (tagged, parsed, dep) [required]
        - format: Output format (plain, json, html) [required]
        - lang: Language code (es, en, fr, de, it, pt, auto) [default: es]

    File (multipart form):
        - file: Text file to analyze (UTF-8 encoded)
    """
    # Check for required file
    if 'file' not in request.files:
        return http_error(400, "No text file sent")

    file = request.files['file']
    if file.filename == '':
        return http_error(400, "No file selected")

    # Read file content
    try:
        text = file.read().decode('utf-8')
    except UnicodeDecodeError:
        return http_error(400, "File must be UTF-8 encoded")

    if not text.strip():
        return http_error(400, "File is empty")

    # Get parameters (support both query string and form data)
    outf = request.args.get('outf') or request.form.get('outf')
    output_format = request.args.get('format') or request.form.get('format')
    lang = request.args.get('lang') or request.form.get('lang') or 'es'

    # Validate required parameters
    if not outf:
        return http_error(400, "No analysis type specified (outf parameter)")

    if outf not in ALLOWED_ANALYSIS_TYPES:
        return http_error(400, f"'{outf}' not a recognized option. Use: {', '.join(ALLOWED_ANALYSIS_TYPES)}")

    if not output_format:
        return http_error(400, "No format specified")

    if output_format not in ALLOWED_FORMATS:
        return http_error(400, f"'{output_format}' not a recognized format. Use: {', '.join(ALLOWED_FORMATS)}")

    # Handle automatic language detection
    if lang == 'auto':
        lang = detect_language(text)

    # Validate language
    if lang not in SUPPORTED_LANGUAGES:
        return http_error(400, f"Unsupported language: {lang}. Supported: {', '.join(SUPPORTED_LANGUAGES)}")

    # Check if parsed is requested for non-Spanish
    if outf == 'parsed' and lang != 'es':
        return http_error(400,
            "Constituency parsing (parsed) is only available for Spanish. "
            "Use 'tagged' or 'dep' for other languages.")

    # Get the appropriate analyzer
    try:
        analyzer = get_analyzer(lang)
    except ValueError as e:
        return http_error(400, str(e))

    # Perform the analysis
    try:
        if output_format == 'plain':
            # For plain format, use the plain text methods
            if outf == 'tagged':
                result = analyzer.tagged_plain(text)
            elif outf == 'parsed':
                result = analyzer.parsed_plain(text)
            elif outf == 'dep':
                result = analyzer.dep_plain(text)
            content_type = "text/plain; charset=utf-8"
        else:
            # For JSON and HTML, get structured data
            if outf == 'tagged':
                data = analyzer.tagged(text)
            elif outf == 'parsed':
                data = analyzer.parsed(text)
            elif outf == 'dep':
                data = analyzer.dep(text)

            result, content_type = format_response(data, output_format, outf)

    except NotImplementedError as e:
        return http_error(400, str(e))
    except Exception as e:
        return http_error(500, f"Analysis error: {str(e)}")

    return Response(result, content_type=content_type)


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "languages": SUPPORTED_LANGUAGES})


if __name__ == '__main__':
    # Development server
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
