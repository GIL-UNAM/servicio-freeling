import json
from typing import List, Dict, Any


def format_tagged_html(data: List[List[Dict[str, str]]]) -> str:
    """Format tagged output as HTML tables."""
    html = ""
    for sentence in data:
        html += "<table><tr><th>Token</th><th>Lemma</th><th>Tag</th><th>Prob.</th></tr>"
        for word in sentence:
            html += "<tr>"
            html += f"<td>{word['token']}</td>"
            html += f"<td>{word['lemma']}</td>"
            html += f"<td>{word['tag']}</td>"
            html += f"<td>{word['prob']}</td>"
            html += "</tr>"
        html += "</table><hr/>"
    return html


def format_tree_html(data: List[List[Dict[str, Any]]]) -> str:
    """Format parsed/dep output as HTML."""
    # Convert brackets to divs for tree visualization
    text = json.dumps(data, ensure_ascii=False)
    text = text.replace("\n", "<br/>")
    text = text.replace(" ", "&nbsp;")
    return text


def format_json(data: Any) -> str:
    """Format data as JSON string."""
    return json.dumps(data, ensure_ascii=False)


def format_response(data: Any, output_format: str, analysis_type: str) -> tuple:
    """
    Format the analysis data according to the requested format.

    Returns a tuple of (content, content_type).
    """
    if output_format == "plain":
        # Plain format is handled by the analyzer directly
        return data, "text/plain; charset=utf-8"

    elif output_format == "json":
        return format_json(data), "application/json; charset=utf-8"

    elif output_format == "html":
        if analysis_type == "tagged":
            html_content = format_tagged_html(data)
        else:
            html_content = format_tree_html(data)

        full_html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Result</title>
    <link href="estilo_arbol.css" rel="stylesheet" type="text/css">
    <meta http-equiv="content-type" content="text/html; charset=utf-8"/>
    <style>
        body {{ font-family: sans-serif; margin: 20px; }}
        table {{ border-collapse: collapse; margin-bottom: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""
        return full_html, "text/html; charset=utf-8"

    else:
        raise ValueError(f"Unknown format: {output_format}")
