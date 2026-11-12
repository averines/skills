# User activity format

UTF-8 JSONL: one JSON object per line, no header. Pass each file with `--activity`.
All files must belong to the selected project and person. Convert raw agent
logs to this format before use.

```jsonl
{"id":"source:session-1:message-1","timestamp":"2026-11-12T10:00:00+03:00","role":"user","chars":42}
{"id":"source:session-1:message-2","timestamp":"2026-11-12T10:20:00+03:00","role":"user","text":"Verify the result"}
```

- `id`: nonempty string that identifies one message across all inputs. Use a
  source prefix and stable message ID so repeated exports retain the same ID.
- `timestamp`: ISO 8601 with an explicit UTC offset or `Z`. Timestamps without
  a time zone are rejected rather than interpreted by guesswork.
- `role`: `user`, `assistant`, `system`, or `tool`. Only `user` events count;
  other roles are ignored after role validation. Converters must exclude
  automatic summaries, tool results, notifications, and other service records
  even if their source labels them as user messages.
- `chars`: nonnegative integer counting Unicode code points. Prefer this to
  copying private message text.
- Alternatively, supply `text`: a string whose length is computed with Python
  `len`. If both fields exist, `chars` must equal `len(text)`. The report
  does not store the text.

User events require `id`, `timestamp`, and either `chars` or `text`.

Repeated IDs with identical timestamps and lengths count once. Conflicting
metadata causes an error with the file and line number, without printing text.
The script does not compare the contents of equal-length texts or determine
the intended project and person. Check project and person when preparing inputs.

Do not synthesize messages to fill gaps. Without logs, use Git only and disclose
the limitation. With activity alone, use `--no-git --activity /path/to/activity.jsonl`.
