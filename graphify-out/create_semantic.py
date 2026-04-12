import json
from pathlib import Path

nodes = [
    {"id": "prd_sisyphus", "label": "Product Requirements Document", "file_type": "document", "source_file": "PRD.md", "source_location": None, "source_url": None, "captured_at": None, "author": None, "contributor": None},
    {"id": "sisyphus_app", "label": "Sisyphus Controller App", "file_type": "document", "source_file": "PRD.md"},
    {"id": "mode_idle", "label": "Idle Mode", "file_type": "document", "source_file": "PRD.md"},
    {"id": "mode_custom", "label": "Custom Mode", "file_type": "document", "source_file": "PRD.md"},
    {"id": "mode_simulation", "label": "Simulation Mode", "file_type": "document", "source_file": "PRD.md"},
    {"id": "mode_transform", "label": "Transform Mode", "file_type": "document", "source_file": "PRD.md"},
    {"id": "grbl_controller", "label": "GRBL Arduino Controller", "file_type": "document", "source_file": "PRD.md"},
    {"id": "readme_sisyphus", "label": "README", "file_type": "document", "source_file": "README.md"}
]

edges = [
    {"source": "prd_sisyphus", "target": "sisyphus_app", "relation": "conceptually_related_to", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "PRD.md", "weight": 1.0},
    {"source": "readme_sisyphus", "target": "sisyphus_app", "relation": "conceptually_related_to", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "README.md", "weight": 1.0},
    {"source": "sisyphus_app", "target": "mode_idle", "relation": "implements", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "PRD.md", "weight": 1.0},
    {"source": "sisyphus_app", "target": "mode_custom", "relation": "implements", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "PRD.md", "weight": 1.0},
    {"source": "sisyphus_app", "target": "mode_simulation", "relation": "implements", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "PRD.md", "weight": 1.0},
    {"source": "sisyphus_app", "target": "mode_transform", "relation": "implements", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "PRD.md", "weight": 1.0},
    {"source": "sisyphus_app", "target": "grbl_controller", "relation": "references", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "PRD.md", "weight": 1.0}
]

data = {
    "nodes": nodes,
    "edges": edges,
    "hyperedges": [],
    "input_tokens": 1000,
    "output_tokens": 500
}

Path('graphify-out/.graphify_semantic_new.json').write_text(json.dumps(data, indent=2), encoding='utf-8')
