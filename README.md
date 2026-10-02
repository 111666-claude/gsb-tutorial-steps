# tutorial-steps

新手引导：前置依赖、跳过条件、请求幂等与步骤顺序，只用 Python 标准库。

```
python3 -m tutorial.cli --sample require
python3 -m tutorial.cli --sample skip
python3 -m tutorial.cli --sample dup
python3 -m tutorial.cli --sample order
python3 -m tutorial.cli --sample scan
python3 -m unittest discover -s tests -v
```

## 口径（README 为准）

- **前置依赖**：`requires` 里的每个步骤都已完成或已跳过后，这一步才能触发；
  否则返回 False 并把该步骤记入 `pending`。
- **跳过**：`skip_flag` 为真的步骤在触发时直接记为跳过，不再计入完成；
  已跳过的步骤同样算满足后续依赖。
- **幂等**：同一个 `req_id` 只生效一次，重复调用返回 False 且不改状态。
- **顺序**：`progress` 按步骤定义顺序返回已完成与已跳过的步骤。
- **不变量**：已完成的步骤与已跳过的步骤不相交；同一步骤不会被完成两次。
- **查询代价**：触发一步不许遍历全部步骤，`scanned_count` 不随步骤数线性增长。
- **规模**：1 万个步骤、每秒 10 万次触发，单次摊还 O(1)。

## 输出契约（不改格式）

```
ok=..
skipped=..
second=..
progress=..
scanned=..
```

## 目录

```
tutorial/core.py   依赖、跳过、幂等与顺序
tutorial/cli.py    命令行入口
tests/             unittest 用例
```
