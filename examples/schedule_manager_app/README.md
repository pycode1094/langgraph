# 스케줄 관리 앱 (CLI)

간단한 커맨드라인 기반 스케줄 관리 앱입니다.

## 기능

- 일정 추가
- 일정 조회 (날짜 필터)
- 일정 수정
- 일정 완료 처리
- 일정 삭제
- JSON 파일로 데이터 영속화

## 실행 방법

```bash
python schedule_app.py --db my_schedule.json add "팀 회의" 2026-03-12 10:00 --description "분기 계획"
python schedule_app.py --db my_schedule.json list
python schedule_app.py --db my_schedule.json done <일정ID>
python schedule_app.py --db my_schedule.json update <일정ID> --time 11:00
python schedule_app.py --db my_schedule.json remove <일정ID>
```

> `--db`를 생략하면 기본 파일은 `schedule_db.json` 입니다.
