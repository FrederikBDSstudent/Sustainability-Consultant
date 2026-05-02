import json
import re
from pathlib import Path


SNAPSHOT_SPECS = {
    "summary": {
        "source_dir": Path("data/weekly_summary"),
        "filename_pattern": re.compile(r"sustainability_summary_(\d{4}-\d{2}-\d{2})\.json"),
        "target_path": Path("docs/_data/current_summary.json"),
    },
    "consultation": {
        "source_dir": Path("data/weekly_consultation"),
        "filename_pattern": re.compile(r"business_consultation_(\d{4}-\d{2}-\d{2})\.json"),
        "target_path": Path("docs/_data/current_consultation.json"),
    },
    "attribution": {
        "source_dir": Path("data/attribution"),
        "filename_pattern": re.compile(r"attribution_(\d{4}-\d{2}-\d{2})\.json"),
        "target_path": Path("docs/_data/current_attribution.json"),
    },
}


def _collect_snapshot_dates():
    dated_snapshots = {}
    for key, spec in SNAPSHOT_SPECS.items():
        per_date = {}
        for path in spec["source_dir"].glob("*.json"):
            match = spec["filename_pattern"].fullmatch(path.name)
            if match:
                per_date[match.group(1)] = path
        dated_snapshots[key] = per_date
    return dated_snapshots


def find_latest_complete_snapshot_date():
    dated_snapshots = _collect_snapshot_dates()
    common_dates = None
    for per_date in dated_snapshots.values():
        snapshot_dates = set(per_date)
        common_dates = snapshot_dates if common_dates is None else common_dates & snapshot_dates

    if not common_dates:
        return None

    return max(common_dates)


def publish_snapshot(snapshot_date=None):
    dated_snapshots = _collect_snapshot_dates()
    if snapshot_date is None:
        snapshot_date = find_latest_complete_snapshot_date()

    if snapshot_date is None:
        raise FileNotFoundError("No complete archived snapshot was found.")

    for key, spec in SNAPSHOT_SPECS.items():
        source_path = dated_snapshots[key].get(snapshot_date)
        if source_path is None:
            raise FileNotFoundError(
                f"Archived snapshot for '{key}' on {snapshot_date} was not found."
            )

        spec["target_path"].parent.mkdir(parents=True, exist_ok=True)
        with source_path.open("r", encoding="utf-8") as source_file:
            payload = json.load(source_file)
        with spec["target_path"].open("w", encoding="utf-8") as target_file:
            json.dump(payload, target_file, indent=2)

    return snapshot_date


if __name__ == "__main__":
    published_date = publish_snapshot()
    print(f"Published archived snapshot for {published_date}")
