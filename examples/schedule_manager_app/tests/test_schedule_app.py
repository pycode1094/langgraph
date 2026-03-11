from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from schedule_app import ScheduleManager


def test_add_and_list(tmp_path: Path) -> None:
    db = tmp_path / "db.json"
    manager = ScheduleManager(str(db))

    manager.add("회의", "2026-03-10", "09:00", "일일 스탠드업")
    items = manager.list()

    assert len(items) == 1
    assert items[0].title == "회의"
    assert items[0].done is False


def test_complete_filters_from_default_list(tmp_path: Path) -> None:
    db = tmp_path / "db.json"
    manager = ScheduleManager(str(db))

    item = manager.add("운동", "2026-03-10", "20:00")
    manager.complete(item.id)

    assert manager.list() == []
    assert len(manager.list(show_all=True)) == 1


def test_update_and_remove(tmp_path: Path) -> None:
    db = tmp_path / "db.json"
    manager = ScheduleManager(str(db))

    item = manager.add("장보기", "2026-03-11", "18:00")
    manager.update(item.id, time="19:00", description="우유, 계란")

    updated = manager.list(show_all=True)[0]
    assert updated.time == "19:00"
    assert updated.description == "우유, 계란"

    manager.remove(item.id)
    assert manager.list(show_all=True) == []
