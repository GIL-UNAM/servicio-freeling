#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for the v2 migration: spaCy for non-Spanish, FreeLing for Spanish.

Run with: python test_v2.py
"""

import io
import json
from unittest.mock import patch, MagicMock

from app import app

FRENCH_TEXT = (
    "Le président de la République a prononcé un discours "
    "devant l'Assemblée nationale. Les députés ont longuement applaudi."
)


def make_file(text):
    """Create an in-memory file upload for the Flask test client."""
    return (io.BytesIO(text.encode("utf-8")), "input.txt")


def section(title):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


# ------------------------------------------------------------------ #
#  1. French document → spaCy  (real end-to-end through Flask)       #
# ------------------------------------------------------------------ #

def test_french_tagged_json():
    section("French tagged (JSON) — real spaCy analysis")

    with app.test_client() as c:
        resp = c.post(
            "/analyze?outf=tagged&format=json&lang=fr",
            data={"file": make_file(FRENCH_TEXT)},
            content_type="multipart/form-data",
        )

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.data}"
    data = json.loads(resp.data)

    print(f"Status: {resp.status_code}")
    print(f"Sentences returned: {len(data)}")
    for i, sent in enumerate(data):
        print(f"\n  Sentence {i + 1} ({len(sent)} tokens):")
        for tok in sent:
            print(f"    {tok['token']:20s}  lemma={tok['lemma']:20s}  tag={tok['tag']}")

    # Basic structural checks
    assert isinstance(data, list) and len(data) > 0, "Should return at least one sentence"
    for sent in data:
        for tok in sent:
            assert set(tok.keys()) == {"token", "lemma", "tag", "prob"}, (
                f"Token keys mismatch: {tok.keys()}"
            )

    print("\n  ✓ PASSED")


def test_french_dep_json():
    section("French dep (JSON) — real spaCy analysis")

    with app.test_client() as c:
        resp = c.post(
            "/analyze?outf=dep&format=json&lang=fr",
            data={"file": make_file(FRENCH_TEXT)},
            content_type="multipart/form-data",
        )

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.data}"
    data = json.loads(resp.data)

    print(f"Status: {resp.status_code}")
    print(f"Dependency trees returned: {len(data)}")
    print(json.dumps(data, ensure_ascii=False, indent=2)[:2000])

    assert isinstance(data, list) and len(data) > 0
    # Each tree should have at least a root node with content
    for tree in data:
        assert len(tree) > 0, "Tree should have at least one root"
        root = tree[0]
        assert "type" in root and "content" in root, f"Root node missing keys: {root.keys()}"

    print("\n  ✓ PASSED")


def test_french_tagged_plain():
    section("French tagged (plain) — real spaCy analysis")

    with app.test_client() as c:
        resp = c.post(
            "/analyze?outf=tagged&format=plain&lang=fr",
            data={"file": make_file(FRENCH_TEXT)},
            content_type="multipart/form-data",
        )

    assert resp.status_code == 200
    text = resp.data.decode("utf-8")

    print(f"Status: {resp.status_code}")
    print(f"Plain output:\n{text}")

    assert len(text.strip()) > 0, "Plain output should not be empty"

    print("\n  ✓ PASSED")


def test_french_parsed_rejected():
    section("French parsed → should be rejected (constituency only for Spanish)")

    with app.test_client() as c:
        resp = c.post(
            "/analyze?outf=parsed&format=json&lang=fr",
            data={"file": make_file(FRENCH_TEXT)},
            content_type="multipart/form-data",
        )

    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}"
    data = json.loads(resp.data)
    print(f"Status: {resp.status_code}")
    print(f"Error: {data['error']}")
    assert "only available for Spanish" in data["error"]

    print("\n  ✓ PASSED")


# ------------------------------------------------------------------ #
#  2. Spanish → FreeLing: verify the exact analyzer_client command    #
# ------------------------------------------------------------------ #

SPANISH_TEXT = "El gato se sentó en la alfombra."

FAKE_TAGGED_OUTPUT = (
    "El el DA0MS0 1\n"
    "gato gato NCMS000 1\n"
    "se se P0000000 0.432955\n"
    "sentó sentar VMIS3S0 1\n"
    "en en SPS00 1\n"
    "la el DA0FS0 0.972006\n"
    "alfombra alfombra NCFS000 1\n"
    ". . Fp 1\n"
)


def test_spanish_tagged_calls_analyzer_client():
    section("Spanish tagged — verify analyzer_client command")

    captured_commands = []

    original_popen = MagicMock()

    def fake_popen(command, shell, stdin, stdout, stderr):
        captured_commands.append(command)
        mock_proc = MagicMock()
        mock_proc.communicate.return_value = (
            FAKE_TAGGED_OUTPUT.encode("utf-8"),
            b"",
        )
        return mock_proc

    with patch("analyzers.freeling.subprocess.Popen", side_effect=fake_popen):
        with app.test_client() as c:
            resp = c.post(
                "/analyze?outf=tagged&format=json&lang=es",
                data={"file": make_file(SPANISH_TEXT)},
                content_type="multipart/form-data",
            )

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.data}"
    data = json.loads(resp.data)

    assert len(captured_commands) == 1, f"Expected 1 call, got {len(captured_commands)}"
    cmd = captured_commands[0]

    print(f"Status: {resp.status_code}")
    print(f"Captured command: {cmd}")
    print(f"  → binary:  /usr/bin/analyzer_client")
    print(f"  → target:  localhost:9999  (port 9999 = tagged)")
    print(f"  → stdin:   <the uploaded text>")
    print()
    print(f"JSON response from mocked FreeLing output:")
    print(json.dumps(data, ensure_ascii=False, indent=2))

    assert cmd == "/usr/bin/analyzer_client localhost:9999", f"Unexpected command: {cmd}"

    print("\n  ✓ PASSED — if /usr/bin/analyzer_client were available, "
          "this is exactly the command that would run.")


def test_spanish_dep_calls_analyzer_client():
    section("Spanish dep — verify analyzer_client command (port 9997)")

    captured = []

    def fake_popen(command, shell, stdin, stdout, stderr):
        captured.append(command)
        mock_proc = MagicMock()
        # Return minimal valid dep output (empty is fine for command verification)
        mock_proc.communicate.return_value = (b"", b"")
        return mock_proc

    with patch("analyzers.freeling.subprocess.Popen", side_effect=fake_popen):
        with app.test_client() as c:
            resp = c.post(
                "/analyze?outf=dep&format=json&lang=es",
                data={"file": make_file(SPANISH_TEXT)},
                content_type="multipart/form-data",
            )

    assert resp.status_code == 200
    cmd = captured[0]

    print(f"Captured command: {cmd}")
    assert cmd == "/usr/bin/analyzer_client localhost:9997", f"Unexpected command: {cmd}"

    print("\n  ✓ PASSED — dep uses port 9997")


def test_spanish_parsed_calls_analyzer_client():
    section("Spanish parsed — verify analyzer_client command (port 9998)")

    captured = []

    def fake_popen(command, shell, stdin, stdout, stderr):
        captured.append(command)
        mock_proc = MagicMock()
        mock_proc.communicate.return_value = (b"", b"")
        return mock_proc

    with patch("analyzers.freeling.subprocess.Popen", side_effect=fake_popen):
        with app.test_client() as c:
            resp = c.post(
                "/analyze?outf=parsed&format=json&lang=es",
                data={"file": make_file(SPANISH_TEXT)},
                content_type="multipart/form-data",
            )

    assert resp.status_code == 200
    cmd = captured[0]

    print(f"Captured command: {cmd}")
    assert cmd == "/usr/bin/analyzer_client localhost:9998", f"Unexpected command: {cmd}"

    print("\n  ✓ PASSED — parsed uses port 9998")


# ------------------------------------------------------------------ #
#  Run all tests                                                      #
# ------------------------------------------------------------------ #

if __name__ == "__main__":
    tests = [
        test_french_tagged_json,
        test_french_dep_json,
        test_french_tagged_plain,
        test_french_parsed_rejected,
        test_spanish_tagged_calls_analyzer_client,
        test_spanish_dep_calls_analyzer_client,
        test_spanish_parsed_calls_analyzer_client,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"\n  ✗ FAILED: {e}")

    section("SUMMARY")
    print(f"  {passed} passed, {failed} failed, {passed + failed} total")
    if failed:
        exit(1)
    else:
        print("\n  All tests passed!")
