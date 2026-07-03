import json
from datetime import datetime
import uuid
from pathlib import Path

data_dir = Path("data/background")
for json_file in data_dir.glob("*.json"):
    data = json.loads(json_file.read_text(encoding="utf-8"))
    if "id" not in data:
        data["id"] = str(uuid.uuid4())
    if "created_at" not in data:
        data["created_at"] = datetime.utcnow().isoformat() + "Z"
    json_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Fixed {json_file.name} with id={data['id'][:8]}...")

print("Background documents fixed and ready for profile update.")
