from .base import BaseAnalyzer
from .freeling import FreelingAnalyzer
from .spacy_analyzer import SpacyAnalyzer

SPACY_MODELS = {
    'en': 'en_core_web_sm',
    'fr': 'fr_core_news_sm',
    'de': 'de_core_news_sm',
    'it': 'it_core_news_sm',
    'pt': 'pt_core_news_sm',
}

SUPPORTED_LANGUAGES = ['es'] + list(SPACY_MODELS.keys())

def get_analyzer(lang: str) -> BaseAnalyzer:
    """Get the appropriate analyzer for the given language."""
    if lang == 'es':
        return FreelingAnalyzer()
    elif lang in SPACY_MODELS:
        return SpacyAnalyzer(lang, SPACY_MODELS[lang])
    else:
        raise ValueError(f"Unsupported language: {lang}")
