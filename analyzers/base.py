from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseAnalyzer(ABC):
    """Base class for text analyzers."""

    @abstractmethod
    def tagged(self, text: str) -> List[List[Dict[str, str]]]:
        """
        Perform POS tagging on the text.

        Returns a list of sentences, where each sentence is a list of tokens.
        Each token is a dict with keys: token, lemma, tag, prob
        """
        pass

    @abstractmethod
    def parsed(self, text: str) -> List[List[Dict[str, Any]]]:
        """
        Perform constituency parsing on the text.

        Returns a list of parse trees.
        """
        pass

    @abstractmethod
    def dep(self, text: str) -> List[List[Dict[str, Any]]]:
        """
        Perform dependency parsing on the text.

        Returns a list of dependency trees.
        """
        pass

    @abstractmethod
    def tagged_plain(self, text: str) -> str:
        """Return tagged output as plain text."""
        pass

    @abstractmethod
    def parsed_plain(self, text: str) -> str:
        """Return parsed output as plain text."""
        pass

    @abstractmethod
    def dep_plain(self, text: str) -> str:
        """Return dependency output as plain text."""
        pass
