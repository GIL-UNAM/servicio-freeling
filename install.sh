#!/bin/bash
# Installation script for FreeLing + spaCy Text Analysis Service

set -e

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Downloading spaCy language models..."
python -m spacy download en_core_web_sm
python -m spacy download fr_core_news_sm
python -m spacy download de_core_news_sm
python -m spacy download it_core_news_sm
python -m spacy download pt_core_news_sm

echo ""
echo "Installation complete!"
echo ""
echo "To run the service:"
echo "  python app.py"
echo ""
echo "Note: For Spanish analysis, ensure the FreeLing daemon is running."
