import spacy
from typing import List, Dict, Any
from .base import BaseAnalyzer


class SpacyAnalyzer(BaseAnalyzer):
    """Analyzer that uses spaCy for non-Spanish text analysis."""

    def __init__(self, lang: str, model_name: str):
        self.lang = lang
        self.model_name = model_name
        self._nlp = None

    @property
    def nlp(self):
        """Lazy load the spaCy model."""
        if self._nlp is None:
            self._nlp = spacy.load(self.model_name)
        return self._nlp

    def tagged(self, text: str) -> List[List[Dict[str, str]]]:
        """Perform POS tagging and return structured data matching FreeLing format."""
        doc = self.nlp(text)
        data = []

        for sent in doc.sents:
            sentence = []
            for token in sent:
                sentence.append({
                    "token": token.text,
                    "lemma": token.lemma_,
                    "tag": token.tag_,
                    "prob": "1.0"  # spaCy doesn't provide tag probability the same way
                })
            data.append(sentence)

        return data

    def parsed(self, text: str) -> List[List[Dict[str, Any]]]:
        """
        Constituency parsing is not supported for non-Spanish languages.
        Raises an error directing users to use Spanish or other analysis types.
        """
        raise NotImplementedError(
            "Constituency parsing (parsed) is only available for Spanish. "
            "Use 'tagged' or 'dep' for other languages."
        )

    def dep(self, text: str) -> List[List[Dict[str, Any]]]:
        """
        Perform dependency parsing and return tree structure matching FreeLing format.
        """
        doc = self.nlp(text)
        trees = []

        for sent in doc.sents:
            # Build a tree from the dependency structure
            tree = self._build_dep_tree(sent)
            trees.append(tree)

        return trees

    def _build_dep_tree(self, sent) -> List[Dict[str, Any]]:
        """Build a dependency tree from a spaCy sentence."""
        # Find root(s) of the sentence
        roots = [token for token in sent if token.head == token]

        def build_node(token) -> Dict[str, Any]:
            node = {
                "type": token.dep_.upper(),
                "subtype": token.dep_.lower(),
                "content": {
                    "token": token.text,
                    "lemma": token.lemma_,
                    "tag": token.tag_
                }
            }

            # Add children recursively
            children = [child for child in token.children]
            if children:
                node["children"] = [build_node(child) for child in children]

            return node

        return [build_node(root) for root in roots]

    def tagged_plain(self, text: str) -> str:
        """Return tagged output as plain text in CoNLL-like format."""
        doc = self.nlp(text)
        lines = []

        for sent in doc.sents:
            for token in sent:
                lines.append(f"{token.text} {token.lemma_} {token.tag_} 1.0")
            lines.append("")  # Empty line between sentences

        return "\n".join(lines)

    def parsed_plain(self, text: str) -> str:
        """
        Constituency parsing is not supported for non-Spanish languages.
        """
        raise NotImplementedError(
            "Constituency parsing (parsed) is only available for Spanish. "
            "Use 'tagged' or 'dep' for other languages."
        )

    def dep_plain(self, text: str) -> str:
        """Return dependency output as plain text in CoNLL-like format."""
        doc = self.nlp(text)
        lines = []

        for sent in doc.sents:
            for token in sent:
                head_idx = token.head.i - sent.start + 1 if token.head != token else 0
                lines.append(
                    f"{token.i - sent.start + 1}\t{token.text}\t{token.lemma_}\t"
                    f"{token.pos_}\t{token.tag_}\t_\t{head_idx}\t{token.dep_}\t_\t_"
                )
            lines.append("")  # Empty line between sentences

        return "\n".join(lines)
