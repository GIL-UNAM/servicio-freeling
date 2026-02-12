import subprocess
import re
from typing import List, Dict, Any
from .base import BaseAnalyzer


class FreelingAnalyzer(BaseAnalyzer):
    """Analyzer that uses FreeLing for Spanish text analysis."""

    CLIENT_PATH = "/usr/bin/analyzer_client"
    PORTS = {
        "tagged": "9999",
        "parsed": "9998",
        "dep": "9997",
    }

    def _execute(self, analysis_type: str, text: str) -> str:
        """Execute FreeLing analyzer_client with the given text."""
        port = self.PORTS[analysis_type]
        command = f"{self.CLIENT_PATH} localhost:{port}"

        process = subprocess.Popen(
            command,
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate(input=text.encode('utf-8'))
        return stdout.decode('utf-8')

    def tagged(self, text: str) -> List[List[Dict[str, str]]]:
        """Perform POS tagging and return structured data."""
        raw_output = self._execute("tagged", text)
        return self._parse_tagged_output(raw_output)

    def _parse_tagged_output(self, output: str) -> List[List[Dict[str, str]]]:
        """Parse FreeLing tagged output into structured format."""
        data = []
        sentence = []

        for line in output.split("\n"):
            fields = line.split(" ")
            if len(fields) == 4:
                sentence.append({
                    "token": fields[0],
                    "lemma": fields[1],
                    "tag": fields[2],
                    "prob": fields[3]
                })
            elif sentence:
                data.append(sentence)
                sentence = []

        return data

    def parsed(self, text: str) -> List[List[Dict[str, Any]]]:
        """Perform constituency parsing and return tree structure."""
        raw_output = self._execute("parsed", text)
        return self._parse_tree_output(raw_output, "parsed")

    def dep(self, text: str) -> List[List[Dict[str, Any]]]:
        """Perform dependency parsing and return tree structure."""
        raw_output = self._execute("dep", text)
        return self._parse_tree_output(raw_output, "dep")

    def _parse_tree_output(self, output: str, format_type: str) -> List[List[Dict[str, Any]]]:
        """
        Parse FreeLing tree output into JSON structure.
        Ported from tree2json.py
        """
        trees = []
        nodes = []
        contents = []
        depths = []

        def new_node(name):
            if isinstance(name, tuple):
                return {'type': name[0], 'subtype': name[1]}
            else:
                return {'type': name}

        def get_content(line):
            match = re.search(r"\+?\((.*?) (.*?) (.*?) -\)", line)
            if match:
                return {
                    'token': match.group(1),
                    'lemma': match.group(2),
                    'tag': match.group(3),
                }
            return None

        def build_tree(names, depths_list, contents_list):
            root = []
            last_seen_parent = {x: None for x in set(depths_list)}

            for name, depth in zip(names, depths_list):
                node = new_node(name)
                if name == 'leaf' or format_type == 'dep':
                    if contents_list:
                        node["content"] = contents_list.pop(0)
                last_seen_parent[depth] = node
                if depth > 0 and last_seen_parent.get(depth - 1):
                    last_seen_parent[depth - 1].setdefault('children', []).append(node)
                else:
                    root.append(node)
            return root

        for line in output.split('\n'):
            if line.strip() == ']':
                continue
            line = line.rstrip()
            m = re.match(r"(\s*)[A-Za-z+_0-9()]", line)

            if not m:
                tree = build_tree(nodes, depths, contents)
                if tree:
                    trees.append(tree)
                nodes = []
                depths = []
                contents = []
                continue

            if format_type == "parsed":
                if line.endswith("_["):
                    ntype = line.strip()[:-2]
                    node_name = ntype
                else:
                    leaf = get_content(line)
                    if leaf is not None:
                        contents.append(leaf)
                        node_name = "leaf"
                    else:
                        continue
            elif format_type == "dep":
                parts = line.strip().split("/")
                if len(parts) >= 3:
                    ntype, nsubtype, content = parts[0], parts[1], "/".join(parts[2:])
                    node_name = (ntype, nsubtype)
                    leaf = get_content(content)
                    if leaf:
                        contents.append(leaf)
                else:
                    continue

            depth = len(m.group(1)) // 2
            nodes.append(node_name)
            depths.append(depth)

        # Handle last tree if any
        if nodes:
            tree = build_tree(nodes, depths, contents)
            if tree:
                trees.append(tree)

        return trees

    def tagged_plain(self, text: str) -> str:
        """Return tagged output as plain text."""
        return self._execute("tagged", text)

    def parsed_plain(self, text: str) -> str:
        """Return parsed output as plain text."""
        return self._execute("parsed", text)

    def dep_plain(self, text: str) -> str:
        """Return dependency output as plain text."""
        return self._execute("dep", text)
