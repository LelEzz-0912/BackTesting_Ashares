import datetime as _dt
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union

import backtrader as bt
import pandas as pd


_OP_MAP = {
    ">": lambda a, b: a > b,
    "<": lambda a, b: a < b,
    ">=": lambda a, b: a >= b,
    "<=": lambda a, b: a <= b,
    "=": lambda a, b: a == b,
    "==": lambda a, b: a == b,
    "≠": lambda a, b: a != b,
    "!=": lambda a, b: a != b,
}


def _parse_consecutive(text: str) -> int:
    """
    返回连续天数要求：
    - '首次' -> 1（并且触发逻辑为"从 False 到 True 的首次触发"）
    - '连续2天'/'连续3天'/'连续5天' -> 对应 N
    """
    if not text or text.strip() == "":
        return 1
    text = text.strip()
    if text == "首次":
        return 1
    if text.startswith("连续") and text.endswith("天"):
        mid = text.replace("连续", "").replace("天", "").strip()
        try:
            return int(mid)
        except Exception:
            return 1
    return 1


def _ensure_datetime_index(df: pd.DataFrame, date_col: str = "date") -> pd.DataFrame:
    if df is None or df.empty:
        raise ValueError("历史数据为空，无法回测。")
    if date_col not in df.columns:
        raise ValueError(f"历史数据缺少 `{date_col}` 列，无法回测。")
    out = df.copy()
    out[date_col] = pd.to_datetime(out[date_col])
    out = out.sort_values(date_col).set_index(date_col)
    return out


def _coerce_rhs(df: pd.DataFrame, rhs_value: str, rhs_var: Optional[str]) -> Union[pd.Series, float, int]:
    """
    GUI 里右侧可以是：手填数值（Entry）或选择变量（Combobox）。
    - 如果 rhs_var 有值：用 df[rhs_var]
    - 否则尝试把 rhs_value 解析成 float
    """
    if rhs_var and rhs_var.strip():
        if rhs_var not in df.columns:
            raise ValueError(f"策略变量不存在：{rhs_var}")
        return df[rhs_var]

    if rhs_value is None:
        raise ValueError("策略右侧值为空。")
    s = str(rhs_value).strip()
    if s == "":
        raise ValueError("策略右侧值为空。")
    try:
        if "." in s:
            return float(s)
        return int(s)
    except Exception:
        # 最后尝试按表达式解析（允许用户写类似 close*0.98）
        safe_locals = {c: df[c] for c in df.columns}
        try:
            val = eval(s, {"__builtins__": {}}, safe_locals)
        except Exception as e:
            raise ValueError(f"无法解析右侧表达式：{s}，错误：{e}") from e
        return val


def build_signals(
    his_df: pd.DataFrame,
    buy: Dict[str, Any],
    sell: Dict[str, Any],
    buy_col: str = "bt_buy",
    sell_col: str = "bt_sell",
) -> pd.DataFrame:
    """
    基于 GUI 的"简单策略"输入，在 pandas 里生成买卖信号列。
    """
    df = his_df.copy()
    if df.empty:
        raise ValueError("历史数据为空，无法生成信号。")

    def _one_side(side: Dict[str, Any]) -> pd.Series:
        left = side.get("left")
        if not left:
            raise ValueError("策略条件缺少左侧变量。")
        if left not in df.columns:
            raise ValueError(f"策略变量不存在：{left}")
        op = side.get("op")
        if op not in _OP_MAP:
            raise ValueError(f"不支持的比较符号：{op}")

        rhs = _coerce_rhs(df, side.get("rhs_value"), side.get("rhs_var"))
        raw = _OP_MAP[op](df[left], rhs)
        raw = raw.fillna(False).astype(bool)

        consec_text = side.get("consecutive", "首次")
        n = _parse_consecutive(consec_text)

        if consec_text == "首次":
            trig = raw & (~raw.shift(1).fillna(False))
            return trig.astype(bool)

        if n <= 1:
            trig = raw & (~raw.shift(1).fillna(False))
            return trig.astype(bool)

        streak = raw.rolling(n).sum() == n
        trig = streak & (~streak.shift(1).fillna(False))
        return trig.fillna(False).astype(bool)

    df[buy_col] = _one_side(buy)
    df[sell_col] = _one_side(sell)
    return df


class PandasSignalData(bt.feeds.PandasData):
    lines = ("bt_buy", "bt_sell")
    params = (
        ("datetime", None),
        ("open", "open"),
        ("high", "high"),
        ("low", "low"),
        ("close", "close"),
        ("volume", "vol"),
        ("openinterest", -1),
        ("bt_buy", "bt_buy"),
        ("bt_sell", "bt_sell"),
    )


# ------------------------------------------------------------------
# 增强版 SignalStrategy：支持三种下单模式 + 止损止盈
# ------------------------------------------------------------------
# stake_mode:
#   "all"   -> 全仓（95% 现金下单，等效原行为）
#   "fixed" -> 固定手数（fixed_size 指定）
#   "pct"   -> 按资金百分比（stake_pct 指定，如 0.5 表示 50%）
#
# stop_loss / take_profit:  0 表示不启用，否则为百分比（如 0.05 表示 5%）
# ------------------------------------------------------------------
class SignalStrategy(bt.Strategy):
    params = dict(
        stake_mode="all",      # "all" | "fixed" | "pct"
        fixed_size=100,        # 固定手数（stake_mode == "fixed" 时生效）
        stake_pct=0.95,        # 资金百分比（stake_mode == "pct" 时生效）
        stop_loss=0.0,         # 止损幅度（如 0.05 → 5%）
        take_profit=0.0,       # 止盈幅度（如 0.10 → 10%）
    )

    def __init__(self):
        self._order: Optional[bt.Order] = None
        self.trades: List[Dict[str, Any]] = []
        self._entry_price: float = 0.0
        self._entry_size: float = 0.0
        self._win_trades = 0
        self._lose_trades = 0

    # ---- helpers ----
    def _calc_size(self) -> int:
        mode = self.p.stake_mode
        price = float(self.data.close[0])
        if price <= 0:
            return 0
        if mode == "all":
            cash = self.broker.getcash()
            size = int((cash * 0.95) / price)   # 留 5% 防精度问题
        elif mode == "fixed":
            size = int(self.p.fixed_size)
        else:   # pct
            cash = self.broker.getcash()
            size = int((cash * float(self.p.stake_pct)) / price)
        return max(0, size)

    def _place_buy(self):
        size = self._calc_size()
        if size <= 0:
            return
        self._order = self.buy(size=size)

    def _place_sell(self):
        if self.position.size <= 0:
            return
        self._order = self.sell(size=self.position.size)

    # ---- stop loss / take profit per bar ----
    def next(self):
        if self._order:
            return

        # 持仓中：检查止损止盈
        if self.position:
            p = float(self.data.close[0])
            entry = self._entry_price
            if self.p.stop_loss > 0 and entry > 0:
                if p <= entry * (1 - float(self.p.stop_loss)):
                    self._order = self.sell(size=self.position.size)
                    return
            if self.p.take_profit > 0 and entry > 0:
                if p >= entry * (1 + float(self.p.take_profit)):
                    self._order = self.sell(size=self.position.size)
                    return

        buy_sig = bool(getattr(self.data, "bt_buy")[0])
        sell_sig = bool(getattr(self.data, "bt_sell")[0])

        if not self.position:
            if buy_sig:
                self._place_buy()
        else:
            if sell_sig:
                self._place_sell()

    # ---- order callback ----
    def notify_order(self, order):
        if order.status in (order.Submitted, order.Accepted):
            return
        if order.status == order.Completed:
            dt = bt.num2date(order.executed.dt)
            date_str = dt.strftime("%Y-%m-%d")
            trade = {
                "date": date_str,
                "type": "BUY" if order.isbuy() else "SELL",
                "price": float(order.executed.price),
                "size": float(order.executed.size),
                "value": float(order.executed.value),
                "comm": float(order.executed.comm),
            }
            self.trades.append(trade)
            if order.isbuy():
                self._entry_price = float(order.executed.price)
                self._entry_size = float(order.executed.size)
            else:
                # 平仓了，统计胜率
                prev = self.trades[-2] if len(self.trades) >= 2 else None
                if prev and prev["type"] == "BUY":
                    pnl = (trade["price"] - prev["price"]) * trade["size"] - trade["comm"] - prev["comm"]
                    if pnl > 0:
                        self._win_trades += 1
                    else:
                        self._lose_trades += 1
                self._entry_price = 0.0
                self._entry_size = 0.0
        self._order = None


# ------------------------------------------------------------------
# 旧版（保留别名，防止已有代码报错）
# ------------------------------------------------------------------
SimpleSignalStrategy = SignalStrategy


@dataclass
class BacktestResult:
    ok: bool
    error: Optional[str]
    start_value: float
    end_value: float
    pnl: float
    pnl_pct: float
    sharpe: Optional[float]
    max_drawdown_pct: Optional[float]
    trade_count: int
    trades: List[Dict[str, Any]]
    analyzers: Dict[str, Any]
    cerebro: Optional[bt.Cerebro] = None
    strategy: Optional[bt.Strategy] = None
    data_colmap: Optional[Dict[str, str]] = None
    # 策略参数（简单策略用）
    params_used: Optional[Dict[str, Any]] = field(default_factory=dict)


def run_simple_backtest(
    his_df: pd.DataFrame,
    buy: Dict[str, Any],
    sell: Dict[str, Any],
    cash: float = 100000.0,
    commission: float = 0.001,
    slippage_perc: float = 0.0,
    # ---- 新参数 ----
    stake_mode: str = "all",
    fixed_size: int = 100,
    stake_pct: float = 0.95,
    stop_loss: float = 0.0,
    take_profit: float = 0.0,
) -> BacktestResult:
    """
    简单策略回测：
      stake_mode : "all"(全仓) | "fixed"(固定手数) | "pct"(按资金百分比)
      fixed_size : 固定手数
      stake_pct  : 资金百分比（0~1）
      stop_loss  : 止损幅度（如 0.05 → 5%），0 表示不启用
      take_profit: 止盈幅度（如 0.10 → 10%），0 表示不启用
    """
    params_used = dict(
        stake_mode=stake_mode,
        fixed_size=fixed_size,
        stake_pct=stake_pct,
        stop_loss=stop_loss,
        take_profit=take_profit,
    )
    try:
        df = build_signals(his_df, buy=buy, sell=sell)
        df = _ensure_datetime_index(df, date_col="date")
        cerebro = bt.Cerebro(stdstats=False)
        cerebro.broker.setcash(float(cash))
        cerebro.broker.setcommission(commission=float(commission))
        if slippage_perc and slippage_perc > 0:
            cerebro.broker.set_slippage_perc(slippage_perc)

        data = PandasSignalData(dataname=df)
        cerebro.adddata(data)

        cerebro.addstrategy(
            SignalStrategy,
            stake_mode=stake_mode,
            fixed_size=fixed_size,
            stake_pct=stake_pct,
            stop_loss=stop_loss,
            take_profit=take_profit,
        )
        cerebro.addobserver(bt.observers.Broker)
        cerebro.addobserver(bt.observers.Trades)
        cerebro.addobserver(bt.observers.BuySell)

        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name="sharpe", timeframe=bt.TimeFrame.Days)
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="trades")
        cerebro.addanalyzer(bt.analyzers.TimeReturn, _name="timereturn")

        start_value = float(cerebro.broker.getvalue())
        strategies = cerebro.run()
        strat = strategies[0]
        end_value = float(cerebro.broker.getvalue())

        analyzers = {
            "sharpe": strat.analyzers.sharpe.get_analysis(),
            "drawdown": strat.analyzers.drawdown.get_analysis(),
            "trades": strat.analyzers.trades.get_analysis(),
            "timereturn": strat.analyzers.timereturn.get_analysis(),
        }

        sharpe = None
        try:
            sharpe = float(analyzers["sharpe"].get("sharperatio"))
        except Exception:
            sharpe = None

        max_dd = None
        try:
            max_dd = float(analyzers["drawdown"]["max"]["drawdown"])
        except Exception:
            max_dd = None

        pnl = end_value - start_value
        pnl_pct = (pnl / start_value) * 100 if start_value else 0.0
        all_trades = getattr(strat, "trades", [])

        return BacktestResult(
            ok=True,
            error=None,
            start_value=start_value,
            end_value=end_value,
            pnl=pnl,
            pnl_pct=pnl_pct,
            sharpe=sharpe,
            max_drawdown_pct=max_dd,
            trade_count=len(all_trades),
            trades=all_trades,
            analyzers=analyzers,
            cerebro=cerebro,
            strategy=strat,
            data_colmap={"bt_buy": "bt_buy", "bt_sell": "bt_sell"},
            params_used=params_used,
        )
    except Exception as e:
        return BacktestResult(
            ok=False,
            error=str(e),
            start_value=float(cash),
            end_value=float(cash),
            pnl=0.0,
            pnl_pct=0.0,
            sharpe=None,
            max_drawdown_pct=None,
            trade_count=0,
            trades=[],
            analyzers={},
            cerebro=None,
            strategy=None,
            data_colmap=None,
            params_used=params_used,
        )


def _sanitize_bt_line_name(name: str) -> str:
    if name is None:
        return "x"
    s = str(name).strip()
    if s == "":
        return "x"
    for ch in [" ", "-", ".", "(", ")", "[", "]", "{", "}", "%", "+", "*", "/", "\\", ":", "，", "。", "（", "）"]:
        s = s.replace(ch, "_")
    s = s.replace("__", "_")
    s2 = []
    for ch in s:
        if ch.isalnum() or ch == "_":
            s2.append(ch)
    s = "".join(s2)
    if s == "":
        s = "x"
    if s[0].isdigit():
        s = f"v_{s}"
    return s


def _build_dynamic_pandasdata(df: pd.DataFrame) -> Tuple[type, Dict[str, str], pd.DataFrame]:
    reserved = {"open", "high", "low", "close", "vol", "volume", "openinterest"}
    base_cols = {"open", "high", "low", "close", "vol"}
    missing = [c for c in base_cols if c not in df.columns]
    if missing:
        raise ValueError(f"历史数据缺少列：{missing}，无法用于自定义回测。")

    extra_cols = [c for c in df.columns if c not in reserved]
    colmap: Dict[str, str] = {}
    used: Dict[str, int] = {}
    for c in extra_cols:
        safe = _sanitize_bt_line_name(c)
        if safe in reserved:
            safe = f"x_{safe}"
        if safe in used:
            used[safe] += 1
            safe = f"{safe}_{used[safe]}"
        else:
            used[safe] = 1
        colmap[c] = safe

    renamed_df = df.rename(columns=colmap)
    lines = tuple(colmap.values())
    params = tuple((ln, ln) for ln in lines)

    DataCls = type(
        "CustomPandasData",
        (bt.feeds.PandasData,),
        {
            "lines": lines,
            "params": (
                ("datetime", None),
                ("open", "open"),
                ("high", "high"),
                ("low", "low"),
                ("close", "close"),
                ("volume", "vol"),
                ("openinterest", -1),
            )
            + params,
        },
    )
    return DataCls, colmap, renamed_df


def run_custom_backtest(
    his_df: pd.DataFrame,
    code: str,
    cash: float = 100000.0,
    commission: float = 0.001,
    slippage_perc: float = 0.0,
    strategy_class_name: str = "CustomStrategy",
) -> BacktestResult:
    """
    自定义策略：用户在文本里写 Backtrader 的 Strategy 类（默认类名 CustomStrategy）。
    his_df 中除 OHLCV 外的列会被动态注入到 DataFeed 中，供策略直接访问。
    """
    try:
        df = _ensure_datetime_index(his_df, date_col="date")

        g: Dict[str, Any] = {
            "__builtins__": {
                "abs": abs,
                "min": min,
                "max": max,
                "sum": sum,
                "len": len,
                "range": range,
                "int": int,
                "float": float,
                "str": str,
                "bool": bool,
                "print": print,
                "datetime": _dt,
            },
            "bt": bt,
        }
        l: Dict[str, Any] = {}
        exec(code, g, l)

        StrategyCls = l.get(strategy_class_name) or g.get(strategy_class_name)
        if StrategyCls is None:
            raise ValueError(
                f"未找到策略类 `{strategy_class_name}`。"
                f"请确保代码里定义了 class {strategy_class_name}(bt.Strategy): ..."
            )

        DataCls, colmap, renamed_df = _build_dynamic_pandasdata(df)

        cerebro = bt.Cerebro(stdstats=False)
        cerebro.broker.setcash(float(cash))
        cerebro.broker.setcommission(commission=float(commission))
        if slippage_perc and slippage_perc > 0:
            cerebro.broker.set_slippage_perc(slippage_perc)

        data = DataCls(dataname=renamed_df)
        cerebro.adddata(data)
        cerebro.addstrategy(StrategyCls)
        cerebro.addobserver(bt.observers.Broker)
        cerebro.addobserver(bt.observers.Trades)
        cerebro.addobserver(bt.observers.BuySell)

        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name="sharpe", timeframe=bt.TimeFrame.Days)
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="trades")
        cerebro.addanalyzer(bt.analyzers.TimeReturn, _name="timereturn")

        start_value = float(cerebro.broker.getvalue())
        strategies = cerebro.run()
        strat = strategies[0]
        end_value = float(cerebro.broker.getvalue())

        analyzers = {
            "sharpe": strat.analyzers.sharpe.get_analysis(),
            "drawdown": strat.analyzers.drawdown.get_analysis(),
            "trades": strat.analyzers.trades.get_analysis(),
            "timereturn": strat.analyzers.timereturn.get_analysis(),
        }

        sharpe = None
        try:
            sharpe = float(analyzers["sharpe"].get("sharperatio"))
        except Exception:
            sharpe = None

        max_dd = None
        try:
            max_dd = float(analyzers["drawdown"]["max"]["drawdown"])
        except Exception:
            max_dd = None

        pnl = end_value - start_value
        pnl_pct = (pnl / start_value) * 100 if start_value else 0.0

        trades = getattr(strat, "trades", [])
        trade_count = len(trades) if isinstance(trades, list) else 0

        return BacktestResult(
            ok=True,
            error=None,
            start_value=start_value,
            end_value=end_value,
            pnl=pnl,
            pnl_pct=pnl_pct,
            sharpe=sharpe,
            max_drawdown_pct=max_dd,
            trade_count=trade_count,
            trades=trades if isinstance(trades, list) else [],
            analyzers=analyzers,
            cerebro=cerebro,
            strategy=strat,
            data_colmap=colmap,
        )
    except Exception as e:
        return BacktestResult(
            ok=False,
            error=str(e),
            start_value=float(cash),
            end_value=float(cash),
            pnl=0.0,
            pnl_pct=0.0,
            sharpe=None,
            max_drawdown_pct=None,
            trade_count=0,
            trades=[],
            analyzers={},
            cerebro=None,
            strategy=None,
            data_colmap=None,
        )


def format_result_text(res: BacktestResult) -> str:
    if not res.ok:
        return f"回测失败：{res.error}"
    lines = []
    lines.append("━" * 25)
    lines.append("  回测完成")
    lines.append(f"  初始资金：{res.start_value:,.2f}")
    lines.append(f"  结束资金：{res.end_value:,.2f}")
    pnl_sign = "+" if res.pnl >= 0 else ""
    lines.append(f"  盈  亏：{pnl_sign}{res.pnl:,.2f} ({pnl_sign}{res.pnl_pct:.2f}%)")
    if res.sharpe is not None:
        lines.append(f"  Sharpe：{res.sharpe:.4f}")
    if res.max_drawdown_pct is not None:
        lines.append(f"  最大回撤：{res.max_drawdown_pct:.2f}%")
    lines.append(f"  交易次数：{res.trade_count}")

    # 策略参数（简单策略）
    if res.params_used:
        p = res.params_used
        mode_names = {"all": "全仓", "fixed": "固定手数", "pct": "按资金百分比"}
        mode_str = mode_names.get(p.get("stake_mode", ""), p.get("stake_mode", ""))
        lines.append(f"  下单模式：{mode_str}")
        if p.get("stake_mode") == "fixed":
            lines.append(f"  固定手数：{p.get('fixed_size', 0)}")
        elif p.get("stake_mode") == "pct":
            lines.append(f"  资金比例：{float(p.get('stake_pct', 0)) * 100:.0f}%")
        sl = p.get("stop_loss", 0)
        tp = p.get("take_profit", 0)
        lines.append(f"  止  损：{'无' if sl == 0 else f'{float(sl)*100:.1f}%'}")
        lines.append(f"  止  盈：{'无' if tp == 0 else f'{float(tp)*100:.1f}%'}")

    lines.append("━" * 25)

    if res.data_colmap:
        extras = [
            f"{k} -> {v}"
            for k, v in list(res.data_colmap.items())[:12]
            if k not in ("bt_buy", "bt_sell")
        ]
        if extras:
            lines.append("  自定义字段映射（原名 -> 策略中名）：")
            for x in extras:
                lines.append(f"    • {x}")

    return "\n".join(lines)


def result_to_trade_df(res: BacktestResult) -> pd.DataFrame:
    if not res.trades:
        return pd.DataFrame(columns=["开仓日", "平仓日", "买入价", "卖出价", "数量", "盈亏", "盈亏%"])
    df = pd.DataFrame(res.trades)
    if "date" in df.columns and len(df) >= 2:
        buys = df[df["type"] == "BUY"].reset_index(drop=True)
        sells = df[df["type"] == "SELL"].reset_index(drop=True)
        rows = []
        i_buy, i_sell = 0, 0
        in_pos = False
        cur_buy = {}
        for _, row in df.iterrows():
            if row["type"] == "BUY":
                in_pos = True
                cur_buy = row.to_dict()
            else:
                if in_pos and cur_buy:
                    pnl = (row["price"] - cur_buy["price"]) * row["size"] - row["comm"] - cur_buy["comm"]
                    # 盈亏显示：盈利为负数，亏损为正数（取负号）
                    pnl_display = -pnl
                    # 盈亏%：价格涨跌幅（不含手续费），并转换为显示格式
                    pnl_pct_price = ((row["price"] - cur_buy["price"]) / cur_buy["price"] * 100) if cur_buy["price"] else 0.0
                    rows.append({
                        "开仓日": cur_buy["date"],
                        "平仓日": row["date"],
                        "买入价": round(cur_buy["price"], 2),
                        "卖出价": round(row["price"], 2),
                        "数量": int(cur_buy["size"]),
                        "盈亏": round(pnl_display, 2),
                        "盈亏%": f"{pnl_pct_price:.2f}%",
                    })
                    in_pos = False
                    cur_buy = {}
                else:
                    rows.append({
                        "开仓日": "-",
                        "平仓日": row["date"],
                        "买入价": "-",
                        "卖出价": round(row["price"], 2),
                        "数量": int(row["size"]),
                        "盈亏": round(-row["comm"], 2),
                        "盈亏%": "N/A",
                    })
        if rows:
            return pd.DataFrame(rows)
    return pd.DataFrame(res.trades)
