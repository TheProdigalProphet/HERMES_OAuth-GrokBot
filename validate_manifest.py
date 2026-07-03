import json
from pathlib import Path

import jsonschema


def load_manifest() -> dict:
    manifest_path = Path(__file__).resolve().parent / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError("manifest.json not found")
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def build_schema() -> dict:
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "description": {"type": "string"},
            "agent": {"type": "string"},
            "input_form": {"type": "string"},
            "model": {"type": "string"},
            "version": {"type": "string"},
            "schema_version": {"type": "string"},
            "tools": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "actions": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "method": {"type": "string"},
                                    "path": {"type": "string"},
                                    "description": {"type": "string"},
                                    "request_schema": {"type": "object"},
                                    "response_schema": {"type": "object"}
                                },
                                "required": ["name", "method", "path", "description"],
                                "additionalProperties": False
                            }
                        }
                    },
                    "required": ["name", "description", "actions"],
                    "additionalProperties": False
                }
            },
            "schemas": {"type": "object"}
        },
        "required": ["name", "description", "agent", "input_form", "model", "version", "schema_version", "tools", "schemas"],
        "additionalProperties": False
    }


def validate_manifest(manifest: dict, schema: dict) -> None:
    jsonschema.validate(manifest, schema)


if __name__ == "__main__":
    manifest = load_manifest()
    schema = build_schema()
    validate_manifest(manifest, schema)
    print("manifest.json is valid.")
