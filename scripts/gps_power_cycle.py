#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GPS Power Cycle — CMD TTCMD 指令產生器

從 All report 找到最近一次已執行的 GOHOME Activity，
加上 1 分鐘，輸出 GPS power cycle 指令對。

用法：
    python scripts/gps_power_cycle.py input/all_report.txt
    python scripts/gps_power_cycle.py input/all_report.txt --utc "2026 046 14 30 00"
"""

import argparse
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# 比對 GOHOME Activity 行，同時捕捉行首的時間戳
# 支援格式：yyyy ddd hh mm ss  CMD CNMGOHOME SRC=TTQ  # GOHOME Activity
GOHOME_LINE_RE = re.compile(
    r"(\d{4})\s+(\d{3})\s+(\d{2})\s+(\d{2})\s+(\d{2})"  # timestamp: yyyy ddd hh mm ss
    r".*?CMD\s+CNMGOHOME\s+SRC=TTQ",
    re.IGNORECASE,
)

# 備用：timestamp 在不同行，只找 GOHOME 行，再往上找時間戳
GOHOME_BARE_RE = re.compile(r"CMD\s+CNMGOHOME\s+SRC=TTQ", re.IGNORECASE)
TIMESTAMP_RE = re.compile(r"(\d{4})\s+(\d{3})\s+(\d{2})\s+(\d{2})\s+(\d{2})")


def doy_to_dt(year: int, doy: int, hh: int, mm: int, ss: int) -> datetime:
    return datetime(year, 1, 1, hh, mm, ss, tzinfo=timezone.utc) + timedelta(days=doy - 1)


def dt_to_cmd(dt: datetime) -> str:
    doy = dt.timetuple().tm_yday
    return (
        f"CMD TTCMD {dt.year} {doy:03d} {dt.hour:02d} {dt.minute:02d} 00 0 {{CGPFSWIOF}}\n"
        f"CMD TTCMD {dt.year} {doy:03d} {dt.hour:02d} {dt.minute:02d} 10 0 {{CGPFSWION}}"
    )


def parse_utc_arg(s: str) -> datetime:
    """接受 'yyyy ddd hh mm ss' 或 'yyyy-dddThh:mm:ss'。"""
    m = re.fullmatch(r"(\d{4})\s+(\d{3})\s+(\d{2})\s+(\d{2})\s+(\d{2})", s.strip())
    if m:
        return doy_to_dt(*map(int, m.groups()))
    m = re.fullmatch(r"(\d{4})-(\d{3})T(\d{2}):(\d{2}):(\d{2})", s.strip())
    if m:
        return doy_to_dt(*map(int, m.groups()))
    raise ValueError(f"無法解析 UTC 時間：{s!r}，請用格式 'yyyy ddd hh mm ss'")


def extract_gohome_times(text: str) -> list[datetime]:
    """從 All report 文字中抽出所有 GOHOME Activity 的時間戳。"""
    times = []

    # 策略一：timestamp 與 GOHOME 在同一行
    for m in GOHOME_LINE_RE.finditer(text):
        try:
            times.append(doy_to_dt(*map(int, m.groups())))
        except Exception:
            pass

    if times:
        return times

    # 策略二：逐行找 GOHOME，再往上找最近的 timestamp
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if not GOHOME_BARE_RE.search(line):
            continue
        # 往上掃最多 5 行找時間戳
        for j in range(i, max(i - 6, -1), -1):
            m = TIMESTAMP_RE.search(lines[j])
            if m:
                try:
                    times.append(doy_to_dt(*map(int, m.groups())))
                except Exception:
                    pass
                break

    return times


def main() -> None:
    parser = argparse.ArgumentParser(description="GPS Power Cycle 指令產生器")
    parser.add_argument("report", help="All report 檔案路徑")
    parser.add_argument(
        "--utc",
        default=None,
        help="目前 UTC 時間（格式：'yyyy ddd hh mm ss'），預設用系統時間",
    )
    args = parser.parse_args()

    report_path = Path(args.report)
    if not report_path.exists():
        sys.exit(f"找不到檔案：{report_path}")

    text = report_path.read_text(encoding="utf-8", errors="ignore")

    now_utc = parse_utc_arg(args.utc) if args.utc else datetime.now(timezone.utc).replace(microsecond=0)

    gohome_times = extract_gohome_times(text)
    if not gohome_times:
        sys.exit("❌ 在 All report 中找不到任何 GOHOME Activity 記錄。")

    # 只保留已過去的時間（<= now）
    past_times = [t for t in gohome_times if t <= now_utc]
    if not past_times:
        sys.exit(
            f"❌ 找不到早於目前 UTC 時間 {now_utc.strftime('%Y %j %H %M %S')} 的 GOHOME 記錄。\n"
            f"   All report 中的 GOHOME 時間：{sorted(gohome_times)}"
        )

    # 最接近現在（但已過去）的 GOHOME 時間
    ref_time = max(past_times)
    target_time = ref_time + timedelta(minutes=1)

    doy_ref = ref_time.timetuple().tm_yday
    print(f"參考 GOHOME 時間 : {ref_time.year} {doy_ref:03d} {ref_time.hour:02d} {ref_time.minute:02d} {ref_time.second:02d} UTC")
    print(f"目前 UTC         : {now_utc.year} {now_utc.timetuple().tm_yday:03d} {now_utc.hour:02d} {now_utc.minute:02d} {now_utc.second:02d} UTC")
    print(f"目標時間 (+1min) : {target_time.year} {target_time.timetuple().tm_yday:03d} {target_time.hour:02d} {target_time.minute:02d} 00 UTC")
    print()
    print("=== GPS Power Cycle 指令 ===")
    print(dt_to_cmd(target_time))


if __name__ == "__main__":
    main()
