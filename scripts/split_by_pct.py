#!/usr/bin/env python3
"""按占比拆分总量，输出可直接粘贴进飞书的算式。

用法：
    python3 split_by_pct.py --total 2572165448 "Claude=72.59" "Codex=15.49" "WorkBuddy=11.91"
    python3 split_by_pct.py --total 1165.89 --decimals 2 "Claude=72.59" "Codex=15.49"

总数和百分比都可以带千分位逗号、百分号、货币符号，脚本会自己清洗。
"""
import argparse
import sys
from decimal import Decimal, ROUND_HALF_UP


def clean_number(raw: str) -> Decimal:
    s = str(raw).strip().replace(",", "").replace("，", "").replace("%", "")
    s = s.lstrip("$￥¥€£").strip()
    if not s:
        raise ValueError("空数值")
    return Decimal(s)


def fmt(value: Decimal, decimals: int) -> str:
    q = Decimal(1).scaleb(-decimals) if decimals else Decimal(1)
    v = value.quantize(q, rounding=ROUND_HALF_UP)
    return f"{v:,.{decimals}f}"


def fmt_pct(value: Decimal) -> str:
    # 百分比原样回显，去掉无意义的尾零（72.59 -> 72.59，20.0 -> 20）
    s = format(value.normalize(), "f")
    return s


def main() -> int:
    ap = argparse.ArgumentParser(description="按占比拆分总量并输出算式")
    ap.add_argument("--total", required=True, help="总量，可带千分位逗号")
    ap.add_argument("--decimals", type=int, default=0,
                    help="每项结果保留几位小数：计数类（token/人次）用 0，金额用 2。默认 0")
    ap.add_argument("items", nargs="+", metavar="名称=百分比",
                    help='形如 "Claude=72.59"，百分比写数字，不用带 %%')
    args = ap.parse_args()

    try:
        total = clean_number(args.total)
    except Exception as e:
        print(f"总数解析失败：{args.total}（{e}）", file=sys.stderr)
        return 1

    rows = []
    for item in args.items:
        if "=" not in item:
            print(f'参数格式应为 "名称=百分比"，收到：{item}', file=sys.stderr)
            return 1
        name, raw_pct = item.split("=", 1)
        name = name.strip()
        try:
            pct = clean_number(raw_pct)
        except Exception as e:
            print(f"{name} 的百分比解析失败：{raw_pct}（{e}）", file=sys.stderr)
            return 1
        rows.append((name, pct, total * pct / Decimal(100)))

    total_str = fmt(total, args.decimals)
    for name, pct, value in rows:
        print(f"{name}：{total_str}*{fmt_pct(pct)}%={fmt(value, args.decimals)}")

    # 四舍五入核对：截图上的百分比通常已被舍入，合计未必正好 100%
    pct_sum = sum(p for _, p, _ in rows)
    q = Decimal(1).scaleb(-args.decimals) if args.decimals else Decimal(1)
    parts_sum = sum(v.quantize(q, rounding=ROUND_HALF_UP) for _, _, v in rows)
    gap = total.quantize(q, rounding=ROUND_HALF_UP) - parts_sum
    if pct_sum != Decimal(100) or gap != 0:
        print("", file=sys.stderr)
        print(f"[核对] 占比合计 {fmt_pct(pct_sum)}%，各项相加 {fmt(parts_sum, args.decimals)}，"
              f"与总数差 {fmt(gap, args.decimals)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
