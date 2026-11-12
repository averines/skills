#!/usr/bin/env python3
"""Estimate work time from Git and explicit JSONL activity logs.

Agent-neutral input format: references/activity-format.md.
No automatic profile or log discovery. Standard library only.
Time between events does not establish attendance or focused work.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

# One explicit model for all events; no implicit calibration of earlier periods.
GAP_MIN = 180
CAP_MIN, LEAD_MIN, TAIL_MIN = 30, 10, 15


# --------------------------------------------------------------------------- data collection

def git_commits(repo: Path, author: str | None) -> tuple[list[dt.datetime], Counter]:
    """Commit timestamps in local time and counts by author.

    `--all` includes local branches whose work may not have reached main.
    """
    cmd = ['git', '-C', str(repo), 'log', '--all', '--date=iso-strict-local', '--fixed-strings',
           '--pretty=%ad%x09%an']
    if author:
        cmd.append(f'--author={author}')
    out = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    if out.returncode != 0:
        sys.exit(f'timespent: Git could not read history for {repo}:\n{out.stderr.strip()}')
    times, authors = [], Counter()
    for line in out.stdout.splitlines():
        if '\t' not in line:
            continue
        stamp, name = line.split('\t', 1)
        try:
            times.append(dt.datetime.fromisoformat(stamp).astimezone())
        except ValueError:
            continue
        authors[name] += 1
    return sorted(times), authors


def human_messages(files: list[Path]) -> list[tuple[dt.datetime, int]]:
    """Explicit JSONL inputs: id, timestamp with time zone, role, and text or chars.

    IDs are unique across inputs to deduplicate repeated exports.
    Text is used only to count characters and is omitted from reports.
    """
    seen: dict[str, tuple[dt.datetime, int]] = {}
    rows: list[tuple[dt.datetime, int]] = []
    for path in files:
        with path.expanduser().open(encoding='utf-8-sig') as handle:
            for line_no, line in enumerate(handle, 1):
                if not line.strip():
                    continue
                location = f'{path}:{line_no}'
                try:
                    rec = json.loads(line)
                except ValueError as exc:
                    raise ValueError(f'{location}: invalid JSON') from exc
                if not isinstance(rec, dict) or rec.get('role') not in ('user', 'assistant', 'system', 'tool'):
                    raise ValueError(f'{location}: expected an object with role=user/assistant/system/tool')
                if rec['role'] != 'user':
                    continue
                identity = rec.get('id')
                if not isinstance(identity, str) or not identity.strip():
                    raise ValueError(f'{location}: expected a nonempty id with a source prefix')
                stamp = _parse_stamp(rec.get('timestamp'))
                if stamp is None:
                    raise ValueError(f'{location}: timestamp must be ISO 8601 with a time zone')
                if 'text' in rec:
                    if not isinstance(rec['text'], str):
                        raise ValueError(f'{location}: text must be a string')
                    chars = len(rec['text'])
                    if 'chars' in rec and (type(rec['chars']) is not int or rec['chars'] != chars):
                        raise ValueError(f'{location}: chars does not match the length of text')
                else:
                    chars = rec.get('chars')
                    if type(chars) is not int or chars < 0:
                        raise ValueError(f'{location}: expected text or a nonnegative integer chars')
                row = (stamp, chars)
                if identity in seen:
                    if seen[identity] != row:
                        raise ValueError(f'{location}: conflicting duplicate id')
                    continue
                seen[identity] = row
                rows.append(row)
    rows.sort()
    return rows


def _parse_stamp(raw) -> dt.datetime | None:
    if not isinstance(raw, str):
        return None
    try:
        moment = dt.datetime.fromisoformat(raw.replace('Z', '+00:00'))
    except ValueError:
        return None
    if moment.tzinfo is None or moment.utcoffset() is None:
        return None
    return moment.astimezone()


# ------------------------------------------------------------------------ time model

def sessionize(times: list[dt.datetime], gap: int) -> list[list[dt.datetime]]:
    """Start a new session when the gap between events exceeds `gap` minutes."""
    if not times:
        return []
    sessions = [[times[0]]]
    for moment in times[1:]:
        if (moment - sessions[-1][-1]).total_seconds() / 60 > gap:
            sessions.append([moment])
        else:
            sessions[-1].append(moment)
    return sessions


def minutes_by_day(sessions, cap: int, lead: int, tail: int, weight: float = 1.0) -> Counter:
    """Merge overlapping intervals and split minutes across local calendar days."""
    daily: Counter = Counter()
    intervals = []
    for session in sessions:
        intervals.append((session[0] - dt.timedelta(minutes=lead), session[0]))
        for start, end in zip(session, session[1:]):
            intervals.append((start, min(end, start + dt.timedelta(minutes=cap))))
        intervals.append((session[-1], session[-1] + dt.timedelta(minutes=tail)))
    merged = []
    for start, end in sorted(intervals):
        if end <= start:
            continue
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    for start, end in merged:
        start, end = start.astimezone(), end.astimezone()
        while start < end:
            midnight = dt.datetime.combine(start.date() + dt.timedelta(days=1), dt.time()).astimezone()
            stop = min(end, midnight)
            daily[start.date()] += (stop - start).total_seconds() / 60 * weight
            start = stop.astimezone()
    return daily


def total_hours(sessions, cap: int, lead: int, tail: int) -> float:
    return sum(minutes_by_day(sessions, cap, lead, tail).values()) / 60


def build_report(commits, authors, messages, args) -> dict:
    msg_times = [t for t, _ in messages]
    report: dict = {
        'repo': str(args.repo),
        'commits': len(commits),
        'authors': authors.most_common(),
        'messages': len(messages),
        'chars': sum(c for _, c in messages),
        'msg_lengths': sorted(c for _, c in messages),
        'generated': dt.datetime.now().astimezone().isoformat(timespec='seconds'),
    }
    if not commits and not msg_times:
        raise ValueError('no commits or user activity events to estimate from')
    events = sorted(set(commits) | set(msg_times))
    sessions = sessionize(events, args.gap)
    daily = minutes_by_day(sessions, args.cap, args.lead, args.tail)
    hours = sum(daily.values()) / 60
    low = total_hours(sessions, args.cap // 2, args.lead // 2, args.tail // 2)
    high = total_hours(sessions, args.cap * 2, args.lead * 2, args.tail * 2)
    report.update(
        model={'gap': args.gap, 'cap': args.cap, 'lead': args.lead, 'tail': args.tail},
        activity_files=[str(path.expanduser().resolve()) for path in args.activity],
        activity_first=msg_times[0].isoformat() if msg_times else None,
        activity_last=msg_times[-1].isoformat() if msg_times else None,
        caveats=[
            'This event-based heuristic does not measure attendance or focused work.',
            'The range shows parameter sensitivity (0.5x / 2x), not statistical uncertainty.',
            'Missing events do not establish that no work occurred or that logs were deleted.',
        ],
    )
    if not msg_times:
        report['caveats'].append('No user activity supplied: Git-only estimate; message and character totals are unknown.')
    else:
        report['caveats'].append('Logs must belong to the selected project and person; --author filters Git only.')
    if len(authors) > 1:
        report['caveats'].append('Multiple Git authors: without --author, the estimate combines their events; it is not a sum of person-hours.')
    report.update(
        hours=hours,
        hours_low=low,
        hours_high=high,
        sessions=len(sessions),
        session_hours=sorted(total_hours([s], args.cap, args.lead, args.tail) for s in sessions),
        overnight=sum(1 for s in sessions if s[0].date() != s[-1].date()),
        first=events[0].isoformat(timespec='seconds'),
        last=events[-1].isoformat(timespec='seconds'),
        active_days=len({event.date() for event in events}),
        span_days=(events[-1].date() - events[0].date()).days + 1,
        by_day={d.isoformat(): round(m / 60, 3) for d, m in sorted(daily.items())},
        by_hour=[sum(1 for e in events if e.hour == h) for h in range(24)],
        commits_by_day=dict(Counter(c.date().isoformat() for c in commits)),
        chars_by_month=dict(Counter()),
    )
    months_chars, months_msgs = Counter(), Counter()
    for stamp, chars in messages:
        months_chars[stamp.strftime('%Y-%m')] += chars
        months_msgs[stamp.strftime('%Y-%m')] += 1
    report['chars_by_month'] = dict(sorted(months_chars.items()))
    report['msgs_by_month'] = dict(sorted(months_msgs.items()))
    hours_by_month: Counter = Counter()
    for iso, hours in report['by_day'].items():
        hours_by_month[iso[:7]] += hours
    report['hours_by_month'] = {m: round(h, 1) for m, h in sorted(hours_by_month.items())}
    return report


# ----------------------------------------------------------------------------- terminal

def _sessions_line(rep: dict) -> str:
    """Session durations calculated with the same model as the total."""
    spans = rep['session_hours']
    if not spans:
        return f'  sessions   {rep["sessions"]}'
    return (f'  sessions   {rep["sessions"]}   median {spans[len(spans) // 2]:.1f} h'
            f'   max {spans[-1]:.1f} h')


def render_terminal(rep: dict) -> str:
    lengths = rep['msg_lengths']
    lines = [
        '',
        f'  ESTIMATED PROJECT WORK TIME: {rep["hours"]:.2f} h   ({rep["hours"] / 8:.2f} eight-hour days)',
        f'  parameter sensitivity: {rep["hours_low"]:.2f}-{rep["hours_high"]:.2f} h',
        '',
        f'  period     {rep["first"][:10]} .. {rep["last"][:10]}'
        f'   ({rep["active_days"]} active days out of {rep["span_days"]})',
        _sessions_line(rep),
        f'  crossing midnight: {rep["overnight"]}',
        f'  commits    {rep["commits"]}',
    ]
    if len(rep['authors']) > 1:
        who = ', '.join(f'{name}: {n}' for name, n in rep['authors'])
        lines.append(f'  NOTE: multiple authors ({who}) — filter with --author')
    if rep['messages']:
        lines += [
            f'  messages   {rep["messages"]}   characters {rep["chars"]:,}'.replace(',', ' ')
            + f'   median {lengths[len(lengths) // 2]}   max {lengths[-1]}',
        ]
    else:
        lines.append('  messages   absent from supplied data; actual count unknown')
    lines.extend(f'  LIMITATION: {item}' for item in rep['caveats'])
    lines.append('')
    lines.append('  Hours by month:')
    peak = max(rep['hours_by_month'].values(), default=1) or 1
    for month, hours in rep['hours_by_month'].items():
        bar = '#' * max(1, round(hours / peak * 40))
        lines.append(f'    {month}  {hours:6.1f} h  {bar}')
    return '\n'.join(lines) + '\n'


# --------------------------------------------------------------------------------- SVG

PALETTE = ['var(--c1)', 'var(--c2)', 'var(--c3)', 'var(--c4)']


def _esc(text: str) -> str:
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def svg_heatmap(by_day: dict) -> str:
    """Calendar heatmap: columns are weeks, rows are weekdays, intensity is hours."""
    if not by_day:
        return ''
    days = {dt.date.fromisoformat(k): v for k, v in by_day.items()}
    first, last = min(days), max(days)
    start = first - dt.timedelta(days=first.weekday())
    weeks = (last - start).days // 7 + 1
    cell, pad = 13, 3
    width, height = weeks * (cell + pad) + 40, 7 * (cell + pad) + 34
    spread = sorted(v for v in days.values() if v > 0)

    def _step(hours: float) -> int:
        # Use the fraction of days below this value to adapt the scale to the
        # project rather than a single outlier.
        below = sum(1 for v in spread if v < hours)
        return min(3, int(below / len(spread) * 4))

    parts = [f'<svg viewBox="0 0 {width} {height}" width="{width}" height="{height}" '
             f'role="img" aria-label="Activity calendar">']
    for name, row in zip(('Mon', 'Wed', 'Fri'), (0, 2, 4)):
        y = 26 + row * (cell + pad) + cell - 3
        parts.append(f'<text class="ax" x="0" y="{y}">{name}</text>')
    seen_month = set()
    for w in range(weeks):
        for d in range(7):
            day = start + dt.timedelta(days=w * 7 + d)
            if day > last:
                continue
            x, y = 40 + w * (cell + pad), 26 + d * (cell + pad)
            hours = days.get(day, 0.0)
            if day.day <= 7 and day.strftime('%Y-%m') not in seen_month and day >= first:
                seen_month.add(day.strftime('%Y-%m'))
                label = ('Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split())[day.month - 1]
                parts.append(f'<text class="ax" x="{x}" y="16">{label}</text>')
            if hours <= 0:
                fill, title = 'var(--grid)', 'no activity'
            else:
                fill, title = PALETTE[_step(hours)], f'{hours:.1f} h'
            parts.append(
                f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" fill="{fill}">'
                f'<title>{day.isoformat()}: {title}</title></rect>')
    parts.append('</svg>')
    return ''.join(parts)


def svg_weekly(by_day: dict, commits_by_day: dict) -> str:
    """Weekly hours as bars and cumulative total as a line."""
    if not by_day:
        return ''
    weekly: Counter = Counter()
    weekly_commits: Counter = Counter()
    for iso, hours in by_day.items():
        day = dt.date.fromisoformat(iso)
        weekly[day - dt.timedelta(days=day.weekday())] += hours
    for iso, count in commits_by_day.items():
        day = dt.date.fromisoformat(iso)
        weekly_commits[day - dt.timedelta(days=day.weekday())] += count
    keys = sorted(weekly)
    width, height, top, bottom, left = 720, 260, 16, 40, 44
    bar_w = max(6, (width - left - 12) / max(1, len(keys)) - 6)
    peak = max(weekly.values()) or 1
    plot_h = height - top - bottom
    parts = [f'<svg viewBox="0 0 {width} {height}" role="img" '
             f'aria-label="Weekly hours and cumulative total">']
    for frac in (0, 0.5, 1):
        y = top + plot_h * (1 - frac)
        parts.append(f'<line class="grid" x1="{left}" y1="{y:.1f}" x2="{width - 12}" y2="{y:.1f}"/>')
        parts.append(f'<text class="ax" x="0" y="{y + 4:.1f}">{peak * frac:.0f} h</text>')
    running, points = 0.0, []
    total = sum(weekly.values()) or 1
    for i, key in enumerate(keys):
        x = left + i * ((width - left - 12) / max(1, len(keys)))
        h = weekly[key] / peak * plot_h
        parts.append(
            f'<rect class="bar" x="{x:.1f}" y="{top + plot_h - h:.1f}" width="{bar_w:.1f}" '
            f'height="{h:.1f}" rx="2"><title>week of {key.isoformat()}: '
            f'{weekly[key]:.1f} h, commits {weekly_commits.get(key, 0)}</title></rect>')
        running += weekly[key]
        points.append(f'{x + bar_w / 2:.1f},{top + plot_h * (1 - running / total):.1f}')
        if i % max(1, len(keys) // 8) == 0:
            parts.append(f'<text class="ax" x="{x:.1f}" y="{height - 20}">'
                         f'{key.strftime("%d.%m")}</text>')
    parts.append(f'<polyline class="cum" points="{" ".join(points)}"/>')
    parts.append(f'<text class="ax" x="{left}" y="{height - 4}">'
                 f'bars: weekly hours; line: cumulative total up to 100%</text>')
    parts.append('</svg>')
    return ''.join(parts)


def svg_clock(by_hour: list) -> str:
    """Event counts by hour of day."""
    width, height, top, bottom, left = 720, 190, 12, 34, 30
    peak = max(by_hour) or 1
    plot_h = height - top - bottom
    step = (width - left - 12) / 24
    parts = [f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="Activity by hour of day">']
    for hour, count in enumerate(by_hour):
        x = left + hour * step
        h = count / peak * plot_h
        night = hour < 7 or hour >= 22
        parts.append(
            f'<rect class="{"bar night" if night else "bar"}" x="{x:.1f}" '
            f'y="{top + plot_h - h:.1f}" width="{step - 4:.1f}" height="{h:.1f}" rx="2">'
            f'<title>{hour:02d}:00 — {count} events</title></rect>')
        if hour % 3 == 0:
            parts.append(f'<text class="ax" x="{x:.1f}" y="{height - 16}">{hour:02d}</text>')
    parts.append(f'<text class="ax" x="{left}" y="{height - 2}">'
                 f'gray: night hours (before 07:00 and from 22:00)</text>')
    parts.append('</svg>')
    return ''.join(parts)


def svg_months(hours_by_month: dict, chars_by_month: dict) -> str:
    """Monthly hours alongside message character counts."""
    if not hours_by_month:
        return ''
    keys = sorted(hours_by_month)
    width, height, top, bottom, left = 720, 210, 14, 46, 44
    plot_h = height - top - bottom
    peak = max(hours_by_month.values()) or 1
    peak_chars = max(chars_by_month.values(), default=0) or 1
    slot = (width - left - 12) / max(1, len(keys))
    parts = [f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="Monthly hours and message volume">']
    for i, key in enumerate(keys):
        x = left + i * slot
        h = hours_by_month[key] / peak * plot_h
        parts.append(f'<rect class="bar" x="{x:.1f}" y="{top + plot_h - h:.1f}" '
                     f'width="{slot * 0.42:.1f}" height="{h:.1f}" rx="2">'
                     f'<title>{key}: {hours_by_month[key]:.1f} h</title></rect>')
        chars = chars_by_month.get(key, 0)
        hc = chars / peak_chars * plot_h
        parts.append(f'<rect class="bar alt" x="{x + slot * 0.48:.1f}" '
                     f'y="{top + plot_h - hc:.1f}" width="{slot * 0.42:.1f}" height="{hc:.1f}" rx="2">'
                     f'<title>{key}: {chars} characters</title></rect>')
        parts.append(f'<text class="ax" x="{x:.1f}" y="{height - 26}">{key}</text>')
    parts.append(f'<text class="ax" x="{left}" y="{height - 8}">'
                 f'left: hours; right: message characters (independent scales)</text>')
    parts.append('</svg>')
    return ''.join(parts)


# --------------------------------------------------------------------------------- HTML

STYLE = """
:root{--bg:#fbfaf8;--fg:#1d1b19;--muted:#6f6a64;--card:#fff;--line:#e6e2dc;--grid:#eceae6;
--c1:#d8e6da;--c2:#8fc09b;--c3:#4a9c68;--c4:#1f6b41;--accent:#1f6b41;--alt:#b58a3e;
--night:#a9b3ba}
:root:not([data-theme=light]){}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){
--bg:#16181a;--fg:#e9e6e1;--muted:#9a948c;--card:#1e2124;--line:#2f3438;--grid:#272b2f;
--c1:#22402e;--c2:#2f6b45;--c3:#4a9c68;--c4:#7fd39a;--accent:#7fd39a;--alt:#d8ab5c;
--night:#6b7a83}}
:root[data-theme=dark]{--bg:#16181a;--fg:#e9e6e1;--muted:#9a948c;--card:#1e2124;--line:#2f3438;
--grid:#272b2f;--c1:#22402e;--c2:#2f6b45;--c3:#4a9c68;--c4:#7fd39a;--accent:#7fd39a;
--alt:#d8ab5c;--night:#6b7a83}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
font:16px/1.6 ui-sans-serif,system-ui,'Segoe UI',Roboto,Helvetica,Arial,sans-serif}
.wrap{max-width:840px;margin:0 auto;padding:40px 20px 64px}
h1{font-size:26px;margin:0 0 4px;letter-spacing:-.01em}
.sub{color:var(--muted);margin:0 0 28px;font-size:14px}
.hero{display:grid;grid-template-columns:repeat(auto-fit,minmax(132px,1fr));gap:12px;
margin-bottom:32px}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 18px;
flex:1 1 150px}
.kpi b{display:block;font-size:28px;line-height:1.15;letter-spacing:-.02em}
.kpi span{color:var(--muted);font-size:12.5px}
section{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px 20px;
margin-bottom:18px}
h2{font-size:15px;margin:0 0 2px;letter-spacing:.01em}
.note{color:var(--muted);font-size:13px;margin:0 0 14px}
.scroll{overflow-x:auto}
svg{display:block;max-width:100%;height:auto}
text.ax{fill:var(--muted);font-size:10.5px;font-family:inherit}
line.grid{stroke:var(--grid);stroke-width:1}
rect.bar{fill:var(--c3)}
rect.bar.night{fill:var(--night)}
rect.bar.alt{fill:var(--alt)}
polyline.cum{fill:none;stroke:var(--accent);stroke-width:2;stroke-dasharray:4 3}
table{width:100%;border-collapse:collapse;font-size:14px}
th,td{text-align:left;padding:7px 8px;border-bottom:1px solid var(--line)}
th{color:var(--muted);font-weight:500;font-size:12.5px}
td.num{text-align:right;font-variant-numeric:tabular-nums}
footer{color:var(--muted);font-size:12.5px;line-height:1.65;margin-top:26px}
"""


def render_html(rep: dict, standalone: bool) -> str:
    lengths = rep['msg_lengths']
    kpis = [
        (f'{rep["hours"]:.2f} h', f'estimate; sensitivity {rep["hours_low"]:.2f}-{rep["hours_high"]:.2f}'),
        (f'{rep["hours"] / 8:.0f}', 'eight-hour workdays'),
        (str(rep['commits']), 'commits'),
        (str(rep['sessions']), f'sessions, {rep["overnight"]} crossing midnight'),
    ]
    if rep['messages']:
        kpis.append((f'{rep["chars"]:,}'.replace(',', ' '), f'characters in {rep["messages"]} messages'))
    hero = ''.join(f'<div class="kpi"><b>{v}</b><span>{_esc(t)}</span></div>' for v, t in kpis)

    rows = ''.join(
        f'<tr><td>{m}</td><td class="num">{h:.1f} h</td>'
        f'<td class="num">{rep["msgs_by_month"].get(m, 0)}</td>'
        f'<td class="num">{rep["chars_by_month"].get(m, 0):,}</td></tr>'.replace(',', ' ')
        for m, h in rep['hours_by_month'].items())

    caveat = ''.join(f'<p class="note">{_esc(item)}</p>' for item in rep['caveats'])
    model = rep['model']

    body = f"""<div class="wrap">
<h1>{_esc(Path(rep['repo']).name)} — project work time</h1>
<p class="sub">{rep['first'][:10]} — {rep['last'][:10]} &middot; {rep['active_days']} active days
out of {rep['span_days']} &middot; generated {rep['generated'][:16].replace('T', ' ')}</p>
<div class="hero">{hero}</div>
{caveat}
<section><h2>Activity calendar</h2>
<p class="note">Cell intensity represents estimated hours per day, showing activity patterns and gaps.</p>
<div class="scroll">{svg_heatmap(rep['by_day'])}</div></section>
<section><h2>Weekly activity</h2>
<p class="note">Bars show estimated weekly hours; the dashed line shows the cumulative share of the total estimate.</p>
<div class="scroll">{svg_weekly(rep['by_day'], rep['commits_by_day'])}</div></section>
<section><h2>Time of day</h2>
<p class="note">Distribution of unique commit and message timestamps.</p>
<div class="scroll">{svg_clock(rep['by_hour'])}</div></section>
<section><h2>Monthly totals</h2>
<div class="scroll">{svg_months(rep['hours_by_month'], rep['chars_by_month'])}</div>
<table><thead><tr><th>month</th><th class="num">hours</th><th class="num">messages</th>
<th class="num">characters</th></tr></thead><tbody>{rows}</tbody></table></section>
<footer>
Event-based estimate, not measured work time.<br>
A session groups events with no gap longer than {model['gap']} min;
count up to {model['cap']} min between events. Add {model['lead']} min before and {model['tail']} min
after each session; count overlapping intervals once.
{f'Median message length: {lengths[len(lengths) // 2]} characters; maximum: {lengths[-1]}.' if lengths else ''}
</footer>
</div>"""
    if not standalone:
        return f'<title>Project work time: {_esc(Path(rep["repo"]).name)}</title>\n<style>{STYLE}</style>\n{body}'
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>Project work time: {_esc(Path(rep["repo"]).name)}</title>'
            f'<style>{STYLE}</style></head><body>{body}</body></html>')


# --------------------------------------------------------------------------------- entry point

def main() -> int:
    ap = argparse.ArgumentParser(
        description='Estimate work time from Git and explicit JSONL user activity logs')
    ap.add_argument('--repo', type=Path, default=Path.cwd(), help='project directory (default: current directory)')
    ap.add_argument('--author', help='filter Git commits by literal author name/email substring')
    ap.add_argument('--activity', type=Path, action='append', default=[],
                    help='JSONL log for this project and person; repeat for multiple files')
    ap.add_argument('--no-git', action='store_true', help='use only --activity inputs; do not invoke Git')
    ap.add_argument('--html', type=Path, help='write a standalone HTML report with charts')
    ap.add_argument('--fragment', type=Path, help='write an HTML fragment without the document wrapper')
    ap.add_argument('--json', type=Path, help='write report data as JSON')
    ap.add_argument('--gap', type=int, default=GAP_MIN, help=f'session gap in minutes ({GAP_MIN})')
    ap.add_argument('--cap', type=int, default=CAP_MIN, help=f'interval cap in minutes ({CAP_MIN})')
    ap.add_argument('--lead', type=int, default=LEAD_MIN, help=f'minutes before the first event ({LEAD_MIN})')
    ap.add_argument('--tail', type=int, default=TAIL_MIN, help=f'minutes after the last event ({TAIL_MIN})')
    args = ap.parse_args()
    if args.gap <= 0 or min(args.cap, args.lead, args.tail) < 0:
        ap.error('--gap must be positive; --cap/--lead/--tail must be nonnegative')

    repo = args.repo.expanduser().resolve()
    if not repo.is_dir():
        ap.error('--repo must point to an existing directory')
    if not args.no_git:
        top = subprocess.run(['git', '-C', str(repo), 'rev-parse', '--show-toplevel'],
                             capture_output=True, text=True, encoding='utf-8')
        if top.returncode != 0:
            ap.error(f'Git could not verify the repository {repo}: {top.stderr.strip()}')
        repo = Path(top.stdout.strip())
    args.repo = repo

    commits, authors = ([], Counter()) if args.no_git else git_commits(repo, args.author)
    messages = human_messages(args.activity)
    report = build_report(commits, authors, messages, args)

    print(render_terminal(report))
    for path, payload in (
        (args.html, lambda: render_html(report, standalone=True)),
        (args.fragment, lambda: render_html(report, standalone=False)),
        (args.json, lambda: json.dumps(report, ensure_ascii=False, indent=2, default=str)),
    ):
        if path:
            with path.expanduser().open('x', encoding='utf-8') as output:
                output.write(payload())
            print(f'  written: {path}')
    if args.html or args.fragment or args.json:
        print()
    return 0


if __name__ == '__main__':
    # Agent tools and redirected files use UTF-8 even when Windows Python defaults
    # to a legacy code page. Keep the native console behavior for interactive use.
    for stream in (sys.stdout, sys.stderr):
        if not stream.isatty() and hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    try:
        sys.exit(main())
    except (OSError, ValueError) as exc:
        sys.exit(f'timespent: {exc}')
