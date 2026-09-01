# pct-split

把一个总量按百分比拆成各分项，输出可直接粘贴进飞书的纯文本算式。

典型场景：截一张 AI token 用量看板（总数 + Claude/Codex/WorkBuddy 各自占比），需要把每项的绝对值算出来发给同事。

## 输出

```
Claude：2,572,165,448*72.59%=1,867,134,899
Codex：2,572,165,448*15.49%=398,428,428
WorkBuddy：2,572,165,448*11.91%=306,344,905
```

## 用法

```bash
python3 scripts/split_by_pct.py --total 2572165448 "Claude=72.59" "Codex=15.49" "WorkBuddy=11.91"
```

- `--decimals 0`（默认）：token、人次等计数类
- `--decimals 2`：金额类
- 总数可带千分位逗号、`$`、`%`，脚本自动清洗
- 占比合计不等于 100%（截图四舍五入）时，差额从 stderr 单独提示，不混进正文

详见 [SKILL.md](SKILL.md)。
