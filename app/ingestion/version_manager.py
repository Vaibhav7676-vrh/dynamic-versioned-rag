import json
from pathlib import Path


class VersionManager:
    def __init__(self, base_path: str = "storage"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        self.manifest = self.base_path / "versions.json"

        if not self.manifest.exists():
            self._write_manifest({"latest": 0, "versions": []})

    def _read_manifest(self):
        with open(self.manifest, "r") as f:
            return json.load(f)

    def _write_manifest(self, data):
        with open(self.manifest, "w") as f:
            json.dump(data, f, indent=2)

    def create_new_version(self) -> str:
        data = self._read_manifest()
        new_version = data["latest"] + 1

        version_name = f"v{new_version}"
        version_path = self.base_path / version_name
        version_path.mkdir(exist_ok=True)

        data["latest"] = new_version
        data["versions"].append(version_name)

        self._write_manifest(data)
        return version_name

    def get_latest_version(self) -> str:
        data = self._read_manifest()
        if data["latest"] == 0:
            raise ValueError("No versions exist yet")
        return f"v{data['latest']}"
