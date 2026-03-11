from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import List, Optional
from uuid import uuid4


@dataclass
class ScheduleItem:
    id: str
    title: str
    day: str
    time: str
    description: str
    done: bool = False


class ScheduleManager:
    def __init__(self, db_path: str = "schedule_db.json") -> None:
        self.db_path = Path(db_path)
        self.items: List[ScheduleItem] = []
        self._load()

    def _load(self) -> None:
        if not self.db_path.exists():
            self.items = []
            return

        data = json.loads(self.db_path.read_text(encoding="utf-8"))
        self.items = [ScheduleItem(**item) for item in data]

    def _save(self) -> None:
        payload = [asdict(item) for item in self.items]
        self.db_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def add(self, title: str, day: str, time: str, description: str = "") -> ScheduleItem:
        _validate_date(day)
        item = ScheduleItem(
            id=str(uuid4())[:8],
            title=title,
            day=day,
            time=time,
            description=description,
        )
        self.items.append(item)
        self.items.sort(key=lambda x: (x.day, x.time, x.title))
        self._save()
        return item

    def list(self, day: Optional[str] = None, show_all: bool = False) -> List[ScheduleItem]:
        filtered = self.items
        if day:
            _validate_date(day)
            filtered = [item for item in filtered if item.day == day]
        if not show_all:
            filtered = [item for item in filtered if not item.done]
        return filtered

    def complete(self, item_id: str) -> ScheduleItem:
        item = self._find(item_id)
        item.done = True
        self._save()
        return item

    def remove(self, item_id: str) -> ScheduleItem:
        item = self._find(item_id)
        self.items = [entry for entry in self.items if entry.id != item_id]
        self._save()
        return item

    def update(
        self,
        item_id: str,
        title: Optional[str] = None,
        day: Optional[str] = None,
        time: Optional[str] = None,
        description: Optional[str] = None,
    ) -> ScheduleItem:
        item = self._find(item_id)
        if title is not None:
            item.title = title
        if day is not None:
            _validate_date(day)
            item.day = day
        if time is not None:
            item.time = time
        if description is not None:
            item.description = description
        self.items.sort(key=lambda x: (x.day, x.time, x.title))
        self._save()
        return item

    def _find(self, item_id: str) -> ScheduleItem:
        for item in self.items:
            if item.id == item_id:
                return item
        raise ValueError(f"일정을 찾을 수 없습니다: {item_id}")


def _validate_date(day_text: str) -> None:
    try:
        date.fromisoformat(day_text)
    except ValueError as exc:
        raise ValueError("날짜 형식은 YYYY-MM-DD 이어야 합니다.") from exc


def _format_row(item: ScheduleItem) -> str:
    status = "완료" if item.done else "예정"
    return (
        f"[{item.id}] {item.day} {item.time} | {item.title} | {status}"
        + (f" | {item.description}" if item.description else "")
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="스케줄 관리 앱")
    parser.add_argument("--db", default="schedule_db.json", help="데이터 저장 파일 경로")
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="일정 추가")
    add.add_argument("title")
    add.add_argument("day", help="YYYY-MM-DD")
    add.add_argument("time", help="HH:MM")
    add.add_argument("--description", default="")

    list_cmd = sub.add_parser("list", help="일정 조회")
    list_cmd.add_argument("--day")
    list_cmd.add_argument("--all", action="store_true", help="완료 포함")

    done = sub.add_parser("done", help="일정 완료 처리")
    done.add_argument("id")

    remove = sub.add_parser("remove", help="일정 삭제")
    remove.add_argument("id")

    update = sub.add_parser("update", help="일정 수정")
    update.add_argument("id")
    update.add_argument("--title")
    update.add_argument("--day")
    update.add_argument("--time")
    update.add_argument("--description")

    return parser


def main() -> None:
    args = build_parser().parse_args()
    manager = ScheduleManager(args.db)

    try:
        if args.command == "add":
            item = manager.add(args.title, args.day, args.time, args.description)
            print("일정이 추가되었습니다.")
            print(_format_row(item))
        elif args.command == "list":
            rows = manager.list(day=args.day, show_all=args.all)
            if not rows:
                print("조회된 일정이 없습니다.")
            else:
                for row in rows:
                    print(_format_row(row))
        elif args.command == "done":
            item = manager.complete(args.id)
            print("완료 처리되었습니다.")
            print(_format_row(item))
        elif args.command == "remove":
            item = manager.remove(args.id)
            print("삭제되었습니다.")
            print(_format_row(item))
        elif args.command == "update":
            item = manager.update(
                args.id,
                title=args.title,
                day=args.day,
                time=args.time,
                description=args.description,
            )
            print("수정되었습니다.")
            print(_format_row(item))
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    main()
