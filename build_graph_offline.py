from __future__ import annotations

import json
from pathlib import Path

from graphify.analyze import god_nodes, suggest_questions, surprising_connections
from graphify.build import build_from_json
from graphify.cluster import cluster, score_all
from graphify.detect import detect
from graphify.export import to_html, to_json
from graphify.extract import extract, extract_markdown
from graphify.report import generate


ROOT = Path('.')
OUT = ROOT / 'graphify-out'
OUT.mkdir(exist_ok=True)


def load_detection() -> dict:
    result = detect(ROOT)
    (OUT / '.graphify_detect.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    return result


def extract_offline(detection: dict) -> dict:
    code_files = [Path(path) for path in detection.get('files', {}).get('code', [])]
    doc_files = [Path(path) for path in detection.get('files', {}).get('document', [])]

    code_result = {'nodes': [], 'edges': [], 'hyperedges': [], 'input_tokens': 0, 'output_tokens': 0}
    if code_files:
        code_result = extract(code_files, cache_root=ROOT, parallel=True)

    doc_nodes = []
    doc_edges = []
    doc_hyperedges = []
    for doc_path in doc_files:
        if doc_path.suffix.lower() in {'.md', '.markdown', '.txt'}:
            doc_result = extract_markdown(doc_path)
            doc_nodes.extend(doc_result.get('nodes', []))
            doc_edges.extend(doc_result.get('edges', []))
            doc_hyperedges.extend(doc_result.get('hyperedges', []))

    merged = {
        'nodes': code_result.get('nodes', []) + doc_nodes,
        'edges': code_result.get('edges', []) + doc_edges,
        'hyperedges': code_result.get('hyperedges', []) + doc_hyperedges,
        'input_tokens': 0,
        'output_tokens': 0,
    }
    (OUT / '.graphify_extract.json').write_text(json.dumps(merged, indent=2), encoding='utf-8')
    return merged


def label_communities(G, communities: dict[int, list[str]]) -> dict[int, str]:
    labels: dict[int, str] = {}
    for cid, members in communities.items():
        best_label = None
        best_degree = -1
        for node_id in members:
            if node_id not in G:
                continue
            degree = G.degree(node_id)
            node_label = G.nodes[node_id].get('label', node_id)
            if degree > best_degree and node_label:
                best_degree = degree
                best_label = node_label
        labels[cid] = best_label or f'Community {cid}'
    return labels


def main() -> None:
    detection = load_detection()
    extraction = extract_offline(detection)

    if not extraction['nodes']:
        raise SystemExit('No nodes were extracted.')

    G = build_from_json(extraction)
    communities = cluster(G)
    cohesion_scores = score_all(G, communities)
    labels = label_communities(G, communities)
    gods = god_nodes(G)
    surprises = surprising_connections(G, communities)
    questions = suggest_questions(G, communities, labels)
    tokens = {'input': extraction.get('input_tokens', 0), 'output': extraction.get('output_tokens', 0)}

    report = generate(
        G,
        communities,
        cohesion_scores,
        labels,
        gods,
        surprises,
        detection,
        tokens,
        str(ROOT),
        suggested_questions=questions,
    )
    (OUT / 'GRAPH_REPORT.md').write_text(report, encoding='utf-8')
    to_json(G, communities, str(OUT / 'graph.json'), force=True)

    if G.number_of_nodes() <= 5000:
        to_html(G, communities, str(OUT / 'graph.html'), community_labels=labels)

    analysis = {
        'communities': {str(k): v for k, v in communities.items()},
        'cohesion': {str(k): v for k, v in cohesion_scores.items()},
        'gods': gods,
        'surprises': surprises,
        'questions': questions,
        'labels': {str(k): v for k, v in labels.items()},
    }
    (OUT / '.graphify_analysis.json').write_text(json.dumps(analysis, indent=2), encoding='utf-8')

    print(f'Graph built: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges, {len(communities)} communities')
    print('Outputs: graphify-out/graph.json, graphify-out/GRAPH_REPORT.md, graphify-out/graph.html')


if __name__ == '__main__':
    main()
