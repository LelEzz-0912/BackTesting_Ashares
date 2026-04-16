import datetime
import sys
import io
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tushare as ts
import backtrader as bt
import mplfinance as mpf
import mplcursors
import ttkbootstrap as ttk
import tkinter as tk
import tkinter.filedialog
import prebasic as pb
import ai_module
import ide_editor as ide
import bt_module
from PIL import ImageTk, Image
from tkinter import messagebox
from pandastable.core import Table
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import config_manager

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei"]  # 设置字体
plt.rcParams["axes.unicode_minus"] = False  # 该语句解决图像中的“-”负号的乱码问题
# 加载配置
_cfg = config_manager.load_config()
_bt_cfg = _cfg.get("backtest", {})
_api_cfg = _cfg.get("api_keys", {})

tu_token = _api_cfg.get("tushare", "")
ai_api_key = _api_cfg.get("openai", "")
# root & frame
root = ttk.Window(themename="superhero")
style = ttk.Style()
root.wm_attributes("-alpha", 0.999)
root.geometry("1680x935")
root.title("BackTesting (A Share)")

tp_frame = tk.Frame(root)
main_frame = tk.Frame(root)
left_frame = tk.Frame(main_frame)
right_frame = tk.Frame(main_frame)
tp_frame.pack(side='top', fill='x',padx=4, pady=(5,0))
main_frame.pack(side='top', fill='x')
left_frame.pack(side='left', fill='y')
right_frame.pack(side='left', fill='y')

ai_module.set_ai_api_key(ai_api_key)

# 定义变量
setting_image = Image.open("./image/setting_image.png").resize((22,22))
setting_image = ImageTk.PhotoImage(setting_image)
dictionary_image = Image.open("./image/dictionary_image.png").resize((22,22))
dictionary_image = ImageTk.PhotoImage(dictionary_image)
display_image = Image.open("./image/display_image.png").resize((18,18))
display_image = ImageTk.PhotoImage(display_image)

adjust = tk.StringVar()
end_date = tk.StringVar()
period = tk.StringVar()
portfolio_name_list = []
portfolio_value_list = []
query_df = pd.DataFrame()
start_date = tk.StringVar()
stock_code = tk.StringVar()
stock_selected = pb.Stock(0,0,0,0,0)
s_path = tk.StringVar()
sf_path = tk.StringVar()
variables = []
last_bt_result = None
last_cerebro = None
trade_df_cache = pd.DataFrame(columns=["开仓日", "平仓日", "买入价", "卖出价", "数量", "盈亏", "盈亏%"])
trade_table_ref = None            # pandastable 实例引用（以便回测后刷新）

up = '#f34334'
down = '#21be87'
figure_color = '#888888'
ax_color = '#c9c9c9'
code_name_text = '股票代码:'
dictionary_df = pd.read_csv("./basic_data/dictionary.csv").drop(['symbol'], axis=1)
dictionary_df.columns = ['股票代码', '股票名称', '地域', '所属行业', '拼音缩写', '市场类型', '上市日期', '实控人名称', '实控人企业性质']
portfolio_value = 0
days = 0
price_date = '0000-00-00'
price_date_show = f'{days} days to {price_date}'
current_price = 0
flu_range = 0
flu_range_spot = 0
current_price_show = '{:.2f}'.format(current_price)
flu_range_show = str(' ' + '{:.2f}'.format(flu_range) + '%')
flu_range_spot_show = str(' (' + '{:.2f}'.format(flu_range_spot) + '%)')

hline = None
vline = None
annotation = None
x_min_global, x_max_global = 0,100
y_min_global, y_max_global = 0,100

root.iconbitmap( "./image/icon.ico")
root.wm_iconbitmap("./image/icon.ico")
# ========== 设置窗口相关变量 ==========
settings_win = None
bt_cash_var = None
bt_commission_var = None
bt_slippage_var = None
tu_token_var = None
openai_key_var = None

# 定义函数
def open_settings():
    """打开设置窗口"""
    global settings_win, bt_cash_var, bt_commission_var, bt_slippage_var, tu_token_var, openai_key_var

    if settings_win is not None and settings_win.winfo_exists():
        settings_win.lift()
        settings_win.focus_force()
        return

    cfg = config_manager.load_config()
    bt_cfg = cfg.get("backtest", {})
    api_cfg = cfg.get("api_keys", {})

    settings_win = tk.Toplevel(root)
    settings_win.title("设置")
    settings_win.geometry("480x300")
    settings_win.resizable(False, False)
    

    notebook = ttk.Notebook(settings_win)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)

    # ---- Tab 1：回测参数 ----
    tab_bt = ttk.Frame(notebook)
    notebook.add(tab_bt, text="回测参数")

    ttk.Label(tab_bt, text="初始资金:", font=("微软雅黑", 10)).grid(row=0, column=0, padx=10, pady=15, sticky="e")
    bt_cash_var = tk.StringVar(value=str(bt_cfg.get("cash", 100000.0)))
    ttk.Entry(tab_bt, textvariable=bt_cash_var, width=20).grid(row=0, column=1, padx=10, sticky="w")

    ttk.Label(tab_bt, text="佣金手续费:", font=("微软雅黑", 10)).grid(row=1, column=0, padx=10, pady=10, sticky="e")
    bt_commission_var = tk.StringVar(value=str(bt_cfg.get("commission", 0.001)))
    ttk.Entry(tab_bt, textvariable=bt_commission_var, width=20).grid(row=1, column=1, padx=10, sticky="w")

    ttk.Label(tab_bt, text="滑点百分比:", font=("微软雅黑", 10)).grid(row=2, column=0, padx=10, pady=10, sticky="e")
    bt_slippage_var = tk.StringVar(value=str(bt_cfg.get("slippage_perc", 0.0)))
    ttk.Entry(tab_bt, textvariable=bt_slippage_var, width=20).grid(row=2, column=1, padx=10, sticky="w")

    # ---- Tab 2：API Keys ----
    tab_api = ttk.Frame(notebook)
    notebook.add(tab_api, text="API Keys")

    ttk.Label(tab_api, text="Tushare Token:", font=("微软雅黑", 10)).grid(row=0, column=0, padx=10, pady=15, sticky="e")
    tu_token_var = tk.StringVar(value=api_cfg.get("tushare", ""))
    ttk.Entry(tab_api, textvariable=tu_token_var, width=28, show="*").grid(row=0, column=1, padx=10, sticky="w")

    ttk.Label(tab_api, text="OpenAI API Key:", font=("微软雅黑", 10)).grid(row=1, column=0, padx=10, pady=10, sticky="e")
    openai_key_var = tk.StringVar(value=api_cfg.get("openai", ""))
    ttk.Entry(tab_api, textvariable=openai_key_var, width=28, show="*").grid(row=1, column=1, padx=10, sticky="w")

    # ---- 按钮区 ----
    def save_and_close():
        new_cfg = {
            "backtest": {
                "cash": float(bt_cash_var.get()),
                "commission": float(bt_commission_var.get()),
                "slippage_perc": float(bt_slippage_var.get()),
            },
            "api_keys": {
                "tushare": tu_token_var.get().strip(),
                "openai": openai_key_var.get().strip(),
            }
        }
        if config_manager.save_config(new_cfg):
            messagebox.showinfo("提示", "设置已保存")
            settings_win.destroy()
        else:
            messagebox.showerror("错误", "保存失败，请检查文件权限")

    btn_frame = tk.Frame(settings_win)
    btn_frame.pack(side="bottom", pady=10)
    ttk.Button(btn_frame, text="保存", command=save_and_close, width=10).pack(side="left", padx=5)
    ttk.Button(btn_frame, text="取消", command=lambda: settings_win.destroy(), width=10).pack(side="left", padx=5)

    settings_win.protocol("WM_DELETE_WINDOW", lambda: settings_win.destroy())

def change_code_name():
    global code_name_text
    if code_name_text == "股票代码:":
        code_name_text = "股票简称:"
        code_or_name.config(text=code_name_text)
    else:
        code_name_text = "股票代码:"
        code_or_name.config(text=code_name_text)

def judge_frequency(event):
    if frequency_combobox.get() != '日数据':
        fq_combobox.config(state=tk.DISABLED)
    else:
        fq_combobox.config(state=tk.NORMAL)

def update_portfolio_name():
    v_listbox.delete(0, "end")
    for stock in portfolio_name_list:
        v_listbox.insert(tk.END, stock)

def get_stock_selected():
    global stock_selected
    order = v_listbox.curselection()[0]
    stock_selected = portfolio_value_list[order]

def plot_stock_selected():
    global stock_selected, hline, vline, annotation, x_min_global, x_max_global, y_min_global, y_max_global
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei"]  # 设置字体
    plt.rcParams["axes.unicode_minus"] = False  # 该语句解决图像中的“-”负号的乱码问题

    bt_ax.clear()
    hline = None
    vline = None
    annotation = None

    # 转换为 Matplotlib 数值
    date_nums = mdates.date2num(stock_selected.his_df['date'])
    x_min_global = date_nums.min() - 10  # 浮点数
    x_max_global = date_nums.max() + 10  # 浮点数

    # 价格数据（假设已经是数值）
    y_min_global = min(stock_selected.his_df['close'])
    y_max_global = max(stock_selected.his_df['close'])

    line = bt_ax.plot(stock_selected.his_df['date'], stock_selected.his_df['close'], label=f'收盘价（{stock_selected.name}）')
    mplcursors.cursor(line, annotation_kwargs={'bbox': {'boxstyle': 'round,pad=0.5', 'fc': 'white', 'alpha': 0.7},
                                               'arrowprops': {'arrowstyle': '->', 'color': 'black'}})
    bt_ax.patch.set_facecolor('#c9c9c9')
    bt_ax.tick_params(axis='x', labelrotation=45)
    bt_ax.grid(axis='y')
    bt_ax.legend()
    bt_canvas_draw.draw()

def info_stock_selected():
    global stock_selected, current_price, current_price_show, flu_range, flu_range_show, flu_range_spot, flu_range_spot_show
    global price_date, price_date_show, days, portfolio_value

    current_price = stock_selected.his_df['close'].iloc[-1]
    current_price_show = '{:.2f}'.format(current_price)
    price_show_label.config(text=current_price_show)

    flu_range = ((current_price - stock_selected.his_df['close'].iloc[0]) / stock_selected.his_df['close'].iloc[0]) * 100
    if flu_range >= 0:
        flu_range_show = str("+" + '{:.2f}'.format(flu_range) + '%')
        fg_h = up
        bg = up
    else:
        flu_range_show = str('{:.2f}'.format(flu_range) + '%')
        fg_h = down
        bg = down

    flu_range_spot = stock_selected.his_df['pct_chg'].iloc[-1]
    if flu_range_spot >= 0:
        flu_range_spot_show = str("(+" + '{:.2f}'.format(flu_range_spot) + '%)')
        fg_s = up
    else:
        flu_range_spot_show = str('(' + '{:.2f}'.format(flu_range_spot) + '%)')
        fg_s = down

    flu_range_spot_label.config(text=flu_range_spot_show, fg=fg_s)
    flu_range_label.config(text=flu_range_show, fg=fg_h)
    up_down_label.config(bg=bg)

    price_date = stock_selected.his_df['date'].dt.strftime('%Y-%m-%d').iloc[-1]
    days = stock_selected.his_df.shape[0]
    price_date_show = f'{days} days to {price_date}'
    date_label.config(text=price_date_show)

    port_weight_bar.config(maximum=portfolio_value, value=current_price)

def update_variables():
    global variables, stock_selected
    variables = stock_selected.his_df.columns.values.tolist()
    for combobox in [buy_con_a_c, buy_con_d_c, sell_con_a_c, sell_con_d_c]:
        combobox.config(value=variables)

def add_stock():
    global stock_code, start_date, end_date, query_df, adjust, period, stock_selected, portfolio_value, current_price, last_bt_result, last_cerebro, trade_df_cache

    try:
        query_df = dictionary_df.copy().set_index('股票代码')
        pb.set_tu_token(tu_token)

        fq_dic = {'前复权':'qfq', '后复权':'hfq', '无复权': None}
        adjust = fq_dic[fq_combobox.get()]
        freq_dic = {'日数据':'D', '周数据':'W', '月数据':'M', '1min':'1min', '5min':'5min', '15min':'15min', '30min':'30min', '60min':'60min'}
        period = freq_dic[frequency_combobox.get()]

        if code_name_text == "股票代码:":
            stock_code = stock_code_entry.get()
            stock_name = str(query_df.loc[stock_code, '股票名称'])
        else:
            stock_name = str(stock_code_entry.get())
            stock_code = query_df.query(f'股票名称 == "{stock_code_entry.get()}"').index[0]

        stock_industry = str(query_df.loc[stock_code, '所属行业'])
        start_m = '{:02d}'.format(int(start_month.get()))
        end_m = '{:02d}'.format(int(end_month.get()))
        start_d = '{:02d}'.format(int(start_day.get()))
        end_d = '{:02d}'.format(int(end_day.get()))
        start_date = str(str(start_year.get()) + str(start_m) + str(start_d))
        end_date = str(str(end_year.get()) + str(end_m) + str(end_d))

        stock = pb.Stock(stock_code, stock_name, stock_industry, start_date, end_date)
        stock.get_stock_data(adjust, period)
        stock_selected = stock
        plot_stock_selected()
        # 添加新股票时清空回测的交易记录表格、Outcome 以及全局回测结果
        last_bt_result = None
        last_cerebro = None
        trade_df_cache = pd.DataFrame(columns=["开仓日", "平仓日", "买入价", "卖出价", "数量", "盈亏", "盈亏%"])
        _refresh_trade_table()
        _set_outcome_text("")
        portfolio_name_list.append(stock.title)
        portfolio_value_list.append(stock)
        info_stock_selected()
        update_variables()
        portfolio_value += current_price
        port_weight_bar.config(maximum=portfolio_value, value=current_price)
        update_portfolio_name()
        v_listbox.selection_set(tk.END)

        for b in after_grab_stock_b:
            b.config(state='normal', cursor='hand2')
        listbox_lbframe.config(text=f'Portfolio({len(portfolio_value_list)})--(￥{str(portfolio_value)})')
        deepseek.update_stock_instance(stock_selected)
    except Exception as e:
        _set_outcome_text(f"添加股票失败：{e}")
        import traceback
        traceback.print_exc()

def drop_stock():
    global stock_selected, portfolio_value, current_price_show

    try:
        if stock_selected is None:
            _set_outcome_text("没有可删除的股票。")
            return

        if messagebox.askyesno(title='删除股票', message=f'将要从投资组合中删除:“{stock_selected.name}”，是否继续？'):
            portfolio_value_list.remove(stock_selected)
            portfolio_value = portfolio_value - float(current_price_show)
            portfolio_name_list.remove(stock_selected.title)
            update_portfolio_name()
            listbox_lbframe.config(text=f'Portfolio({len(portfolio_value_list)})--(￥{str(portfolio_value)})')

            if len(portfolio_value_list) != 0:
                v_listbox.selection_set(tk.END)
                show_selected_stock()
            else:
                for b in after_grab_stock_b:
                    b.config(state='disabled', cursor='arrow')
    except Exception as e:
        _set_outcome_text(f"删除股票失败：{e}")
        import traceback
        traceback.print_exc()

def view_data(window_df):
    try:
        view_window = tk.Toplevel(root)
        view_window.title('View Data')
        view_window.iconphoto(False, tk.PhotoImage(file="./image/icon.png"))
        view_window.geometry("1350x800")

        data_view_frame = tk.Frame(view_window)
        data_view_frame.pack(fill='both', expand=True)
        data_view_table_dis = Table(data_view_frame, showstatusbar=True, showtoolbar=True)
        data_view_table_dis.model.df = window_df
        data_view_table_dis.cellbackgr = '#373737'
        data_view_table_dis.rowselectedcolor = '#707070'
        data_view_table_dis.rowheaderbgcolor = '#707070'
        data_view_table_dis.textcolor = '#ececec'
        data_view_table_dis.font = ('Arial', 12)
        data_view_table_dis.setRowHeight(24)
        data_view_table_dis.show()
        data_view_table_dis.setWrap()
        data_view_table_dis.zoomOut()
        data_view_table_dis.zoomIn()

        def select_save_path():
            path_s = tkinter.filedialog.asksaveasfilename(filetypes=[("Microsoft Excel 逗号分隔值文件 ", "*.csv"),
                                                                     ("Microsoft Excel 文件 ", "*.xlsx")],
                                                          defaultextension='.csv')
            path_s = path_s.replace("/", "\\\\")
            s_path.set(path_s)
            save_button.config(state="normal", cursor="hand2")

        def save_file():
            if file_save_e.get().endswith('.csv'):
                window_df.to_csv("{}".format(str(file_save_e.get())), index=False)
            elif file_save_e.get().endswith('.xlsx'):
                window_df.to_excel("{}".format(str(file_save_e.get())), index=False)
            save_success_info.config(text='保存成功!')

        file_save_lbframe = ttk.Labelframe(view_window, text='Save File')
        file_save_lbframe.pack(side='bottom', fill='x')
        file_save_e = ttk.Entry(file_save_lbframe, width=60, font=('微软雅黑', 10), textvariable=s_path)
        file_save_e.grid(row=0, column=0, padx=6, pady=4)
        ttk.Button(file_save_lbframe, text='选择路径', cursor='hand2', style='outline', command=select_save_path).grid(row=0, column=1, padx=2, pady=4)
        save_button = ttk.Button(file_save_lbframe, text='保存文件', style='outline', state=tk.DISABLED, command=save_file)
        if s_path != "":
            save_button.config(state='normal', cursor='hand2')
        save_button.grid(row=0, column=2, padx=2, pady=4)
        save_success_info = tk.Label(file_save_lbframe, text='' , font=('微软雅黑', 10))
        save_success_info.grid(row=0, column=3, padx=2, pady=4)
    except Exception as e:
        _set_outcome_text(f"显示数据失败：{e}")
        import traceback
        traceback.print_exc()

def show_selected_stock(event=None):
    global stock_selected, trade_df_cache, trade_table_ref, hline, vline, annotation, x_min_global, x_max_global, y_min_global, y_max_global
    try:
        get_stock_selected()
        info_stock_selected()
        # 切图前先清理旧十字线引用，避免 clear() 后残留引用报错
        try:
            if hline:
                hline.remove()
            if vline:
                vline.remove()
            if annotation:
                annotation.remove()
        except Exception:
            pass
        hline = vline = annotation = None

        # 先根据当前股票数据更新全局坐标范围（确保缩放/平移基于当前股票）
        if stock_selected is not None and not stock_selected.his_df.empty:
            date_nums = mdates.date2num(stock_selected.his_df['date'])
            x_min_global = date_nums.min() - 10
            x_max_global = date_nums.max() + 10
            y_min_global = stock_selected.his_df['close'].min()
            y_max_global = stock_selected.his_df['close'].max()

        # 判断该股票是否已进行过回测
        has_bt = stock_selected is not None and getattr(stock_selected, 'bt_has_figure', False)
        has_trades = has_bt and not stock_selected.bt_trades_df.empty

        if has_bt:
            # 有回测结果，恢复图 + Outcome + 交易表格
            stock_selected.render_bt_canvas(bt_ax, bt_canvas_draw, x_min_global, x_max_global, y_min_global, y_max_global)
            if stock_selected.bt_result:
                _set_outcome_text(bt_module.format_result_text(stock_selected.bt_result))
            if has_trades:
                trade_df_cache = stock_selected.bt_trades_df
                _refresh_trade_table()
            else:
                # 有回测图但无交易记录（可能全空仓），清空表格
                trade_df_cache = pd.DataFrame(columns=["开仓日", "平仓日", "买入价", "卖出价", "数量", "盈亏", "盈亏%"])
                _refresh_trade_table()
        else:
            # 未回测，仅画价格线，清空表格和 Outcome
            plot_stock_selected()
            trade_df_cache = pd.DataFrame(columns=["开仓日", "平仓日", "买入价", "卖出价", "数量", "盈亏", "盈亏%"])
            _refresh_trade_table()
            _set_outcome_text("")

        update_variables()
        deepseek.update_stock_instance(stock_selected)
    except Exception as e:
        _set_outcome_text(f"显示股票失败：{e}")
        import traceback
        traceback.print_exc()

def create_new_variable():
    global stock_selected, variables
    if stock_selected is None:
        tk.messagebox.showerror("错误", "请先选择股票！")
        return
    name = new_variable_name_e.get().strip()
    value = new_variable_value_e.get().strip()
    if not name:
        tk.messagebox.showerror("错误", "变量名不能为空！")
        return
    if name in variables:
        tk.messagebox.showerror("错误", f"变量名 '{name}' 已存在！")
        return
    try:
        df = stock_selected.his_df
        stock_selected.his_df[name] = eval(value, {"__builtins__": {}}, df)
    except Exception as e:
        tk.messagebox.showerror("错误", f"表达式求值失败：{e}")
        return
    variables = stock_selected.his_df.columns.values.tolist()
    update_variables()
    new_variable_name_e.delete(0, tk.END)
    new_variable_value_e.delete(0, tk.END)
    tk.messagebox.showinfo("成功", f"变量 '{name}' 创建成功！")

def clear_conditions():
    con_list_c = [buy_con_a_c, buy_con_b_c, buy_con_c_c, buy_con_d_c,
                sell_con_a_c, sell_con_b_c, sell_con_c_c,sell_con_d_c]
    for con in con_list_c:
        con.set('')
    buy_con_d_e.delete(0, tk.END)
    sell_con_d_e.delete(0, tk.END)

def _set_outcome_text(text: str):
    outcome_text.config(state="normal")
    outcome_text.delete("1.0", tk.END)
    outcome_text.insert(tk.END, text)
    outcome_text.config(state="disabled")

def _overlay_trades_on_canvas(res, ax, canvas, x_min, x_max, y_min, y_max):
    """
    把回测结果（买卖点）叠加画到主 bt_ax 画布上。
    - 买入：红色虚线 + 上三角 scatter（在买入价位置）
    - 卖出：绿色虚线 + 下三角 scatter（在卖出价位置）
    - 持仓区间：半透明蓝色 axvspan
    """
    if not res.ok or not res.trades:
        return ax, canvas

    ax.clear()
    global hline, vline, annotation
    # ax.clear() 会使 hline/vline/annotation 引用失效，重置它们防止 remove() 时出错
    try:
        if hline:
            hline.remove()
            vline.remove()
            annotation.remove()
    except Exception:
        pass
    hline = None
    vline = None
    annotation = None

    # 重新绘制价格线
    if 'stock_selected' in globals() and stock_selected is not None and not stock_selected.his_df.empty:
        df = stock_selected.his_df.copy()
        ax.plot(df['date'], df['close'], color='#3a7bd5', linewidth=1.5, label=f'收盘价（{getattr(stock_selected,"name","")}）')
        price_by_date = df.set_index('date')['close']
    else:
        price_by_date = pd.Series(dtype=float)

    # 解析买卖点（带价格）
    buy_x, buy_y, sell_x, sell_y = [], [], [], []
    for t in res.trades:
        try:
            dt = pd.to_datetime(t['date'])
            px = float(t['price'])
        except Exception:
            continue
        if t['type'] == 'BUY':
            buy_x.append(dt)
            buy_y.append(px)
        else:
            sell_x.append(dt)
            sell_y.append(px)

    # 持仓区间配对（按时间顺序配对买入→卖出）
    paired = []
    buys = sorted(zip(buy_x, buy_y), key=lambda x: x[0])
    sells = sorted(zip(sell_x, sell_y), key=lambda x: x[0])
    bi, si = 0, 0
    in_pos = False
    while bi < len(buys) or si < len(sells):
        if not in_pos:
            if bi < len(buys):
                cur_buy = buys[bi]
                bi += 1
                in_pos = True
            else:
                break
        else:
            if si < len(sells):
                paired.append((cur_buy, sells[si]))
                si += 1
                in_pos = False
            else:
                break

    # 画持仓区间阴影
    for (bdt, _), (sdt, _) in paired:
        ax.axvspan(bdt, sdt, alpha=0.18, color='#388df3')

    # 画买入虚线 + scatter（标注在买入价上）
    # ax.scatter(buy_x, buy_y, marker='^', color='#f34334', s=90, zorder=6,
               # edgecolors='white', linewidths=0.8, label='买入')
    for bx, by in zip(buy_x, buy_y):
        ax.axvline(x=bx, color='#f34334', linestyle=(0,(3,1,1,1)), linewidth=1.0, alpha=0.7)

    # 画卖出虚线 + scatter（标注在卖出价上）
    # ax.scatter(sell_x, sell_y, marker='v', color='#21be87', s=90, zorder=6,
               # edgecolors='white', linewidths=0.8, label='卖出')
    for sx, sy in zip(sell_x, sell_y):
        ax.axvline(x=sx, color='#21be87', linestyle=(0,(3,1,1,1)), linewidth=1.0, alpha=0.7)

    # 坐标范围
    all_dates = buy_x + sell_x
    if all_dates:
        all_nums = [mdates.date2num(d) for d in all_dates]
        pad = max((max(all_nums) - min(all_nums)) * 0.08, 8)
        ax.set_xlim(min(all_nums) - pad, max(all_nums) + pad)

    if not price_by_date.empty:
        ax.set_ylim(price_by_date.min() * 0.96, price_by_date.max() * 1.04)

    ax.patch.set_facecolor('#c9c9c9')
    ax.tick_params(axis='x', labelrotation=45)
    ax.grid(axis='y', alpha=0.8)
    ax.legend(loc='upper left', fontsize=9)
    canvas.draw()
    return ax, canvas


def apply_simple_backtest():
    global stock_selected, last_bt_result, last_cerebro, trade_df_cache, trade_table_ref
    try:
        if stock_selected is None or stock_selected.his_df is None or stock_selected.his_df.empty:
            _set_outcome_text("请先添加股票并获取历史数据!")
            return

        # ---- 读取下单模式 & 止损止盈 ----
        mode = stake_mode_var.get()
        if mode == "fixed":
            try:
                fixed_sz = int(stake_fixed_e.get())
            except Exception:
                fixed_sz = 100
            stake_pct_val = 0.95
        elif mode == "pct":
            try:
                stake_pct_val = float(stake_pct_e.get()) / 100.0
            except Exception:
                stake_pct_val = 0.95
            fixed_sz = 100
        else:   # "all"
            fixed_sz = 100
            stake_pct_val = 0.95

        try:
            sl = float(stop_loss_e.get()) / 100.0
        except Exception:
            sl = 0.0
        try:
            tp = float(take_profit_e.get()) / 100.0
        except Exception:
            tp = 0.0

        buy = {
            "left": buy_con_a_c.get().strip(),
            "consecutive": buy_con_b_c.get().strip() or "首次",
            "op": buy_con_c_c.get().strip(),
            "rhs_value": buy_con_d_e.get(),
            "rhs_var": buy_con_d_c.get().strip(),
        }
        sell = {
            "left": sell_con_a_c.get().strip(),
            "consecutive": sell_con_b_c.get().strip() or "首次",
            "op": sell_con_c_c.get().strip(),
            "rhs_value": sell_con_d_e.get(),
            "rhs_var": sell_con_d_c.get().strip(),
        }

        bt_params = dict(
            stake_mode=mode, fixed_size=fixed_sz,
            stake_pct=stake_pct_val, stop_loss=sl, take_profit=tp,
            buy=buy, sell=sell
        )

        res = bt_module.run_simple_backtest(
            stock_selected.his_df,
            buy=buy, sell=sell,
            stake_mode=mode,
            fixed_size=fixed_sz,
            stake_pct=stake_pct_val,
            stop_loss=sl,
            take_profit=tp,
            cash=float(_bt_cfg.get("cash", 100000.0)),
            commission=float(_bt_cfg.get("commission", 0.001)),
            slippage_perc=float(_bt_cfg.get("slippage_perc", 0.0)),
        )
        last_bt_result = res
        last_cerebro = res.cerebro if res.ok else None
        _set_outcome_text(bt_module.format_result_text(res))

        if res.ok:
            for b in after_bt_b:
                b.config(state="normal", cursor="hand2")
            trade_df_cache = bt_module.result_to_trade_df(res)
            _refresh_trade_table()
            # 写入股票实例（切回该股时自动恢复）
            stock_selected.save_bt_data(res, trade_df_cache, bt_params, _set_outcome_text)
            _overlay_trades_on_canvas(res, bt_ax, bt_canvas_draw, x_min_global, x_max_global, y_min_global, y_max_global)
        else:
            for b in after_bt_b:
                b.config(state="disabled", cursor="arrow")
    except Exception as e:
        _set_outcome_text(f"回测失败：{e}")

def apply_custom_backtest():
    global stock_selected, last_bt_result, last_cerebro, trade_df_cache, trade_table_ref
    try:
        if stock_selected is None or stock_selected.his_df is None or stock_selected.his_df.empty:
            _set_outcome_text("请先添加股票并获取历史数据。")
            return

        code = custom_strategy_text.get("1.0", "end-1c")
        res = bt_module.run_custom_backtest(
            stock_selected.his_df,
            code=code,
            cash=float(_bt_cfg.get("cash", 100000.0)),
            commission=float(_bt_cfg.get("commission", 0.001)),
            slippage_perc=float(_bt_cfg.get("slippage_perc", 0.0)),
        )
        last_bt_result = res
        last_cerebro = res.cerebro if res.ok else None
        _set_outcome_text(bt_module.format_result_text(res))

        if res.ok:
            for b in after_bt_b:
                b.config(state="normal", cursor="hand2")
            trade_df_cache = bt_module.result_to_trade_df(res)
            _refresh_trade_table()
            # 写入股票实例（切回该股时自动恢复）
            stock_selected.save_bt_data(res, trade_df_cache, {}, _set_outcome_text)
            _overlay_trades_on_canvas(res, bt_ax, bt_canvas_draw, x_min_global, x_max_global, y_min_global, y_max_global)
        else:
            for b in after_bt_b:
                b.config(state="disabled", cursor="arrow")
    except Exception as e:
        _set_outcome_text(f"回测失败：{e}")

def clear_backtest():
    global last_bt_result, last_cerebro, trade_df_cache, trade_table_ref, stock_selected
    try:
        last_bt_result = None
        last_cerebro = None
        trade_df_cache = pd.DataFrame(columns=["开仓日", "平仓日", "买入价", "卖出价", "数量", "盈亏", "盈亏%"])
        _refresh_trade_table()
        _set_outcome_text("")
        for b in after_bt_b:
            b.config(state="disabled", cursor="arrow")
        # 清除当前股票实例的回测缓存
        if stock_selected is not None:
            stock_selected.bt_result = None
            stock_selected.bt_trades_df = pd.DataFrame()
            stock_selected.bt_params = {}
            stock_selected.bt_has_figure = False
        # 恢复主画布：重绘价格曲线（清除买卖点）
        plot_stock_selected()
    except Exception as e:
        _set_outcome_text(f"重置失败：{e}")
        import traceback
        traceback.print_exc()


def _refresh_trade_table():
    """用 trade_df_cache 更新交易记录 pandastable 的内容"""
    trade_table_ref.model.df = trade_df_cache.copy()
    trade_table_ref.redraw()


def _show_bt_plot():
    """调用 cerebro.plot() 展示回测图像"""
    try:
        if last_cerebro:
            last_cerebro.plot()
        else:
            _set_outcome_text("尚无回测结果可显示。")
    except Exception as e:
        _set_outcome_text(f"显示图像失败：{e}")
        import traceback
        traceback.print_exc()


def export_bt_result():
    global last_bt_result, stock_selected, portfolio_value_list

    # 检查是否有回测结果
    if len(portfolio_value_list) == 0:
        _set_outcome_text("投资组合为空，无法导出。")
        return

    # 检查每只股票是否都有回测数据
    for stock in portfolio_value_list:
        if not hasattr(stock, 'bt_result') or stock.bt_result is None or not stock.bt_result.ok:
            _set_outcome_text(f"股票 {stock.title} 尚无有效的回测结果。")
            return

    path = tkinter.filedialog.asksaveasfilename(
        filetypes=[("PDF 文件", "*.pdf")],
        defaultextension=".pdf",
    )
    if not path:
        return
    path = path.replace("/", "\\")

    try:
        from matplotlib.backends.backend_pdf import PdfPages
        import matplotlib.pyplot as plt
        from matplotlib import rcParams, font_manager

        # 设置中文字体 - 使用系统中文字体
        font_paths = [
            r'C:\Windows\Fonts\msyh.ttc',  # 微软雅黑
            r'C:\Windows\Fonts\simhei.ttf',  # 黑体
            r'C:\Windows\Fonts\msyhbd.ttc',  # 微软雅黑 Bold
        ]
        for font_path in font_paths:
            try:
                font_prop = font_manager.FontProperties(fname=font_path)
                rcParams['font.sans-serif'] = [font_prop.get_name()]
                break
            except Exception:
                continue
        else:
            rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']

        rcParams['axes.unicode_minus'] = False
        # 确保字体嵌入PDF
        rcParams['pdf.fonttype'] = 42
        rcParams['ps.fonttype'] = 42

        with PdfPages(path) as pdf:
            # ============ 第1页：投资组合汇总 ============
            fig_summary = plt.figure(figsize=(8.27, 11.69))  # A4 portrait 竖向
            fig_summary.suptitle('投资组合回测报告', fontsize=16, fontweight='bold', y=0.96)

            # 汇总数据
            total_start_value = sum(stock.bt_result.start_value for stock in portfolio_value_list)
            total_end_value = sum(stock.bt_result.end_value for stock in portfolio_value_list)
            total_pnl = sum(stock.bt_result.pnl for stock in portfolio_value_list)
            total_pnl_pct = (total_pnl / total_start_value * 100) if total_start_value else 0.0

            # 计算平均最大回撤
            max_dd_list = [stock.bt_result.max_drawdown_pct for stock in portfolio_value_list]
            avg_max_dd = sum(max_dd_list) / len(max_dd_list) if max_dd_list else 0.0

            summary_text = f"""
┌─────────────────────────────────────────────────┐
 【投资组合总览】                         
├─────────────────────────────────────────────────┤
  初始总资产: ￥{total_start_value:>12,.2f}        
  最终总资产: ￥{total_end_value:>12,.2f}         
  总盈亏:     ￥{total_pnl:>12,.2f} ({total_pnl_pct:>6.2f}%) 
  平均最大回撤: {avg_max_dd:>11.2f}%              
└─────────────────────────────────────────────────┘

【个股明细】
─────────────────────────────────────────────────
       股票名称              初始价值          最终价值           盈亏          盈亏%
──────────────────────────────────────────────────
"""

            for i, stock in enumerate(portfolio_value_list, 1):
                res = stock.bt_result
                # 显示股票名称而不是title
                stock_name = getattr(stock, 'name', stock.title)
                summary_text += f"  {i:<3}  {stock_name:<14} ￥{res.start_value:>10,.0f}  ￥{res.end_value:>10,.0f}  ￥{res.pnl:>+10,.2f}  {res.pnl_pct:>+6.2f}%\n"

            fig_summary.text(0.08, 0.82, summary_text, fontsize=9.5, linespacing=1.5,
                             verticalalignment='top', family=rcParams['font.sans-serif'][0] if rcParams['font.sans-serif'] else 'sans-serif')

            pdf.savefig(fig_summary, bbox_inches='tight')
            plt.close(fig_summary)

            # ============ 每只股票的详细页 ============
            for idx, stock in enumerate(portfolio_value_list, 1):
                res = stock.bt_result
                trades_df = stock.bt_trades_df if hasattr(stock, 'bt_trades_df') else bt_module.result_to_trade_df(res)

                fig_stock = plt.figure(figsize=(8.27, 11.69))  # A4 portrait 竖向页面
                fig_stock.suptitle(f'[{idx}] {stock.title} 回测详情', fontsize=16, fontweight='bold', y=0.98)

                # 1. 汇总信息
                summary_info = f"""
回测参数: 起始资金=￥{res.start_value:,.0f}  佣金={_bt_cfg.get('commission', 0.001)*100:.1f}%  滑点={_bt_cfg.get('slippage_perc', 0.0)*100:.1f}%

─────────────────────────────────────
最终资产: ￥{res.end_value:,.2f}
累计盈亏: ￥{res.pnl:+,.2f}  ({res.pnl_pct:+.2f}%)
夏普比率: {res.sharpe:.2f}
最大回撤: {res.max_drawdown_pct:.2f}%
交易次数: {res.trade_count}
─────────────────────────────────────
"""

                fig_stock.text(0.05, 0.90, summary_info, fontsize=9, linespacing=1.4,
                               verticalalignment='top', family=rcParams['font.sans-serif'][0] if rcParams['font.sans-serif'] else 'sans-serif')

                # 2. 回测策略信息
                strategy_info = "【回测策略】\n"
                strategy_info += "─────────────────────────────────────\n"

                # 尝试从 res 对象中获取策略信息
                strategy_found = False

                # 通过 cerebro.strats 获取
                if res.cerebro is not None and hasattr(res.cerebro, 'strats') and res.cerebro.strats:
                    for strat in res.cerebro.strats:
                        strategy_obj = None

                        # 处理 Backtrader 的 strats 格式
                        # strat 通常是 (StrategyClass, args, kwargs) 或策略实例
                        if isinstance(strat, tuple) and len(strat) >= 1:
                            # strat[0] 是策略类或实例
                            potential_strategy = strat[0]

                            # 检查 potential_strategy 的类型
                            if isinstance(potential_strategy, type):
                                # 是策略类（未实例化），尝试从 kwargs 创建实例
                                try:
                                    kwargs = strat[2] if len(strat) > 2 else {}
                                    if kwargs:
                                        strategy_obj = potential_strategy(**kwargs)
                                    else:
                                        # 无法创建实例，使用类名
                                        strategy_obj = potential_strategy
                                except Exception as e:
                                    strategy_obj = potential_strategy
                            elif hasattr(potential_strategy, '__class__'):
                                # 已经是策略实例
                                strategy_obj = potential_strategy
                            else:
                                # 其他情况，尝试直接使用
                                strategy_obj = potential_strategy
                        elif hasattr(strat, '_obj'):
                            strategy_obj = strat._obj
                        elif hasattr(strat, 'strategy'):
                            strategy_obj = strat.strategy
                        elif hasattr(strat, '__class__') and hasattr(strat, 'lines'):
                            # 可能是策略实例（有 lines 属性）
                            strategy_obj = strat
                        else:
                            strategy_obj = strat

                        if strategy_obj is not None:
                            strategy_found = True

                            # 递归提取真正的策略对象
                            while isinstance(strategy_obj, (list, tuple)) and len(strategy_obj) > 0:
                                strategy_obj = strategy_obj[0]

                            # 再次验证 strategy_obj 是否有效
                            if strategy_obj is None:
                                strategy_info += "策略名称: 未找到策略对象\n"
                            else:
                                # 获取策略类名
                                try:
                                    if isinstance(strategy_obj, type):
                                        class_name = strategy_obj.__name__
                                    else:
                                        class_name = strategy_obj.__class__.__name__
                                    strategy_info += f"策略名称: {class_name}\n"
                                except:
                                    strategy_info += "策略名称: 未知\n"

                            # 获取策略详情（买卖条件）
                            strategy_info += "\n策略详情:\n"

                            buy_detail = "未知"
                            sell_detail = "未知"

                            # 优先从 bt_params 获取
                            if hasattr(stock, 'bt_params') and stock.bt_params:
                                bt_params = stock.bt_params
                                # 格式化买卖条件
                                def format_condition(cond):
                                    if not cond or not isinstance(cond, dict):
                                        return "未知"
                                    left = cond.get('left', '')
                                    op = cond.get('op', '')
                                    rhs_val = cond.get('rhs_value', '')
                                    rhs_var = cond.get('rhs_var', '')
                                    consec = cond.get('consecutive', '首次')
                                    rhs = rhs_var if rhs_var else (str(rhs_val) if rhs_val else '')
                                    return f"{left}({consec}){op}{rhs}"

                                buy_detail = format_condition(bt_params.get('buy', {}))
                                sell_detail = format_condition(bt_params.get('sell', {}))

                            strategy_info += f"  买入条件: {buy_detail}\n"
                            strategy_info += f"  卖出条件: {sell_detail}\n"
                            break

                # 备用方法：通过 stock 对象
                if not strategy_found and hasattr(stock, 'bt_strategy') and stock.bt_strategy:
                    strategy_obj = stock.bt_strategy
                    strategy_found = True
                    try:
                        strategy_info += f"策略名称: {strategy_obj.__class__.__name__}\n"
                    except:
                        strategy_info += "策略名称: 未知\n"

                    # 添加策略详情
                    strategy_info += "\n策略详情:\n"
                    buy_detail = "未知"
                    sell_detail = "未知"

                    if hasattr(stock, 'bt_params') and stock.bt_params:
                        bt_params = stock.bt_params
                        def format_condition(cond):
                            if not cond or not isinstance(cond, dict):
                                return "未知"
                            left = cond.get('left', '')
                            op = cond.get('op', '')
                            rhs_val = cond.get('rhs_value', '')
                            rhs_var = cond.get('rhs_var', '')
                            consec = cond.get('consecutive', '首次')
                            rhs = rhs_var if rhs_var else (str(rhs_val) if rhs_val else '')
                            return f"{left}({consec}){op}{rhs}"

                        buy_detail = format_condition(bt_params.get('buy', {}))
                        sell_detail = format_condition(bt_params.get('sell', {}))

                    strategy_info += f"  买入条件: {buy_detail}\n"
                    strategy_info += f"  卖出条件: {sell_detail}\n"

                strategy_info += "─────────────────────────────────────"

                fig_stock.text(0.05, 0.75, strategy_info, fontsize=9, linespacing=1.3,
                               verticalalignment='top', family=rcParams['font.sans-serif'][0] if rcParams['font.sans-serif'] else 'sans-serif')

                # 3. 交易记录表格
                ax_table = fig_stock.add_axes([0.05, 0.35, 0.90, 0.28])
                ax_table.axis('tight')
                ax_table.axis('off')

                # 表格数据（限制行数）
                table_data = [trades_df.columns.tolist()]
                display_df = trades_df.head(30)  # 限制30行
                for _, row in display_df.iterrows():
                    table_data.append([str(val) for val in row.tolist()])

                if len(trades_df) > 30:
                    fig_stock.text(0.5, 0.33, f'（仅显示前30笔交易，共 {len(trades_df)} 笔）',
                                   ha='center', va='center', fontsize=8, style='italic')

                table = ax_table.table(cellText=table_data, loc='center', cellLoc='center')
                table.auto_set_font_size(False)
                table.set_fontsize(7)
                table.scale(1, 1.5)

                for (row, col), cell in table.get_celld().items():
                    if row == 0:
                        cell.set_text_props(weight='bold', color='white')
                        cell.set_facecolor('#404040')
                    elif row % 2 == 0:
                        cell.set_facecolor('#F0F0F0')

                fig_stock.text(0.05, 0.35, '图像结果', fontsize=11, fontweight='bold')

                # 4. 回测图表 - 底部
                if res.cerebro is not None:
                    import tempfile
                    import os
                    import matplotlib
                    original_backend = matplotlib.get_backend()
                    matplotlib.use('Agg', force=True)
                    # 关闭所有可能存在的图形窗口
                    plt.close('all')

                    temp_img = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                    try:
                        # 保存并屏蔽 plt.show 函数，防止弹窗
                        original_show = plt.show
                        plt.show = lambda *args, **kwargs: None

                        if hasattr(stock, 'bt_fig') and stock.bt_fig is not None:
                            stock.bt_fig.savefig(temp_img.name, dpi=150, bbox_inches='tight')
                        elif hasattr(stock, 'bt_figure') and stock.bt_figure is not None:
                            stock.bt_figure.savefig(temp_img.name, dpi=150, bbox_inches='tight')
                        else:
                            figs = res.cerebro.plot(style='candlestick', volume=False, iplot=False, savefig=False)
                            if figs and len(figs) > 0:
                                fig = figs[0][0] if isinstance(figs[0], (list, tuple)) else figs[0]
                                fig.savefig(temp_img.name, dpi=150, bbox_inches='tight')
                                plt.close(fig)

                        # 恢复 plt.show
                        plt.show = original_show

                        ax_chart = fig_stock.add_axes([0.05, 0.05, 0.90, 0.25])
                        chart_img = plt.imread(temp_img.name)
                        ax_chart.imshow(chart_img)
                        ax_chart.axis('off')
                    finally:
                        if os.path.exists(temp_img.name):
                            temp_img.close()
                            try:
                                os.unlink(temp_img.name)
                            except Exception:
                                pass
                        try:
                            matplotlib.use(original_backend)
                        except Exception:
                            pass

                pdf.savefig(fig_stock, bbox_inches='tight')
                plt.close(fig_stock)

        _set_outcome_text("PDF报告导出成功。")
    except Exception as e:
        _set_outcome_text(f"导出失败：{e}")
        import traceback
        traceback.print_exc()

# GUI
# tp_frame
tk.Label(tp_frame, text="开始日期:", font=("微软雅黑", 10)).grid(row=0, column=0, padx=(10, 1))
start_year = ttk.Spinbox(tp_frame, from_=1990, to=datetime.date.today().year, width=5)
start_year.grid(row=0, column=1, padx=1, pady=1)
start_year.set(datetime.date.today().year - 1)
tk.Label(tp_frame, text="年", font=("微软雅黑", 10)).grid(row=0, column=2, padx=1)
start_month = ttk.Spinbox(tp_frame, from_=1, to=12, width=2)
start_month.grid(row=0, column=3, padx=(8, 1), pady=1)
start_month.set(datetime.date.today().month)
tk.Label(tp_frame, text="月", font=("微软雅黑", 10)).grid(row=0, column=4, padx=1)
start_day = ttk.Spinbox(tp_frame, from_=1, to=31, width=2)
start_day.grid(row=0, column=5, padx=(8, 1), pady=1)
start_day.set(datetime.date.today().day)
tk.Label(tp_frame, text="日", font=("微软雅黑", 10)).grid(row=0, column=6, padx=1)

tk.Label(tp_frame, text="结束日期:", font=("微软雅黑", 10)).grid(row=0, column=7, padx=(50, 1))
end_year = ttk.Spinbox(tp_frame, from_=1990, to=datetime.date.today().year, width=5)
end_year.grid(row=0, column=8, padx=1, pady=1)
end_year.set(datetime.date.today().year)
tk.Label(tp_frame, text="年", font=("微软雅黑", 10)).grid(row=0, column=9, padx=1)
end_month = ttk.Spinbox(tp_frame, from_=1, to=12, width=2)
end_month.grid(row=0, column=10, padx=(8, 1), pady=1)
end_month.set(datetime.date.today().month)
tk.Label(tp_frame, text="月", font=("微软雅黑", 10)).grid(row=0, column=11, padx=1)
end_day = ttk.Spinbox(tp_frame, from_=1, to=31, width=2)
end_day.grid(row=0, column=12, padx=(8, 1), pady=1)
end_day.set(datetime.date.today().day)
tk.Label(tp_frame, text="日", font=("微软雅黑", 10)).grid(row=0, column=13, padx=1)

tk.Label(tp_frame, text="频率:", font=("微软雅黑", 10)).grid(row=0, column=14, padx=(50, 1))
frequency_combobox = ttk.Combobox(tp_frame, values=('日数据', '周数据', '月数据','1min','5min','15min','30min','60min'), width=6, state="readonly")
frequency_combobox.grid(row=0, column=15, padx=1, pady=1)
frequency_combobox.set('日数据')
frequency_combobox.bind("<<ComboboxSelected>>", judge_frequency)
tk.Label(tp_frame, text="复权方式:", font=("微软雅黑", 10)).grid(row=0, column=16, padx=(50, 1))
fq_combobox = ttk.Combobox(tp_frame, values=('前复权', '后复权', '无复权'), width=6, state="readonly")
fq_combobox.grid(row=0, column=17, padx=1)
fq_combobox.set('前复权')
code_or_name = tk.Label(tp_frame, text=code_name_text, font=("微软雅黑", 10))
code_or_name.grid(row=0, column=18, padx=(50, 1))
stock_code_entry = ttk.Entry(tp_frame, textvariable=stock_code, width=9, font=("微软雅黑", 10))
stock_code_entry.grid(row=0, column=19, padx=1)
ttk.Checkbutton(tp_frame, text='简称', command=change_code_name, bootstyle="round-toggle", cursor='hand2').grid(row=0, column=20, padx=(3,1))
ttk.Button(tp_frame, cursor='hand2', image=dictionary_image, style='outline', command=lambda :view_data(dictionary_df)).grid(row=0, column=21, padx=(51,1))
ttk.Button(tp_frame, cursor='hand2', image=setting_image, style='outline', command=open_settings).grid(row=0, column=22, padx=(2,1))
ttk.Separator(tp_frame).grid(row=1, column=0, columnspan=25, padx=(3,1), pady=(5, 2), sticky='ew')

# left_frame
draw_frame = tk.Frame(left_frame)
draw_frame.pack(side='top', padx=(5, 1))
bt_canvas_lbframe = ttk.Labelframe(draw_frame, text='Canvas')  # , height=587, width=760
bt_canvas_lbframe.pack(side='top')
bt_canvas = tk.Canvas(bt_canvas_lbframe)
bt_canvas.pack()
bt_canvas.pack_propagate(False)
bt_figure = plt.Figure(figsize=(6.67, 4.4))
bt_figure.subplots_adjust(left=0.06, right=0.98, bottom=0.18, top=0.96)
bt_ax = bt_figure.subplots()
bt_canvas_draw = FigureCanvasTkAgg(bt_figure, bt_canvas)
bt_canvas_draw.get_tk_widget().grid(row=0, column=0, padx=3, pady=(0, 2))
bt_figure.patch.set_facecolor(figure_color)
bt_ax.patch.set_facecolor(ax_color)

# 鼠标拖动 处理事件
startx = 0
starty = 0
mPress = False

def call_back(event):
    axtemp = event.inaxes
    if axtemp is None:
        return
    base_scale = 1.5
    x_min, x_max = axtemp.get_xlim()  # 已经是浮点数
    y_min, y_max = axtemp.get_ylim()
    xdata = event.xdata   # 浮点数
    ydata = event.ydata

    # 计算缩放后的新范围（以鼠标为中心）
    new_xmin = xdata - (xdata - x_min) * (1/base_scale if event.button=='up' else base_scale)
    new_xmax = xdata + (x_max - xdata) * (1/base_scale if event.button=='up' else base_scale)
    new_ymin = ydata - (ydata - y_min) * (1/base_scale if event.button=='up' else base_scale)
    new_ymax = ydata + (y_max - ydata) * (1/base_scale if event.button=='up' else base_scale)

    # 边界限制（直接比较浮点数）
    new_xmin = max(new_xmin, x_min_global)
    new_xmax = min(new_xmax, x_max_global)
    new_ymin = max(new_ymin, y_min_global)
    new_ymax = min(new_ymax, y_max_global)

    if new_xmin < new_xmax and new_ymin < new_ymax:
        axtemp.set_xlim(new_xmin, new_xmax)
        # axtemp.set_ylim(new_ymin, new_ymax)  # 如果需要Y轴缩放
    bt_figure.canvas.draw_idle()

def call_move(event):
    global mPress, startx, starty
    mouse_x = event.x
    mouse_y = event.y
    axtemp = event.inaxes
    if event.name == 'button_press_event':
        if axtemp and event.button == 1:
            # 图例检测部分保持不变...
            # （你的原有代码）
            mPress = True
            startx = event.xdata
            starty = event.ydata
            return
    elif event.name == 'button_release_event':
        if axtemp and event.button == 1:
            mPress = False
    elif event.name == 'motion_notify_event':
        if axtemp and event.button == 1 and mPress:
            # 图例检测部分保持不变...
            # 计算平移后的新范围
            x_min, x_max = axtemp.get_xlim()
            y_min, y_max = axtemp.get_ylim()
            w = x_max - x_min
            h = y_max - y_min
            mx = event.xdata - startx
            my = event.ydata - starty

            left = x_min - mx
            right = left + w
            bottom = y_min - my
            top = bottom + h

            # 边界限制
            if left < x_min_global:
                left = x_min_global
                right = left + w
            if right > x_max_global:
                right = x_max_global
                left = right - w

            # 确保范围有效
            if left < right:
                axtemp.set_xlim(left, right)
                # axtemp.set_ylim(bottom, top)   # 如需Y轴拖动，取消注释

            bt_figure.canvas.draw_idle()

# 十字线
def on_mouse_move(event):
    """鼠标移动时触发，更新十字线和标签的位置"""
    global hline, vline, annotation
    if event.inaxes != bt_ax:
        return

    # --- 关键修改：将日期列转换为数值（浮点数）---
    # 假设你的日期列是 Pandas Series，类型为 datetime64
    # 方法1：使用 matplotlib.dates.date2num（推荐）
    date_nums = mdates.date2num(stock_selected.his_df['date'].dt.to_pydatetime())
    # 或者如果你的日期已经是 Timestamp 数组：date_nums = mdates.date2num(stock_selected.his_df['date'])

    # 价格数据（假设是数值类型，无需转换）
    prices = stock_selected.his_df['close'].values

    # 1. 寻找最近的数据点
    # event.xdata 已经是浮点数（Matplotlib 日期数值），可以直接与 date_nums 相减
    distances = np.hypot(date_nums - event.xdata, prices - event.ydata)
    closest_index = np.argmin(distances)
    closest_x_num = date_nums[closest_index]  # 最近点的日期（浮点数）
    closest_y = prices[closest_index]  # 最近点的价格

    # 2. 移除旧的十字线和文本（ax.clear() 后变量可能已成"空壳"，安全处理）
    try:
        if hline:
            hline.remove()
            vline.remove()
            annotation.remove()
    except Exception:
        pass

    # 3. 绘制新的十字线（直接使用数值坐标，Matplotlib 会自动映射到日期轴）
    hline = bt_ax.axhline(y=closest_y, color='gray', linestyle='--', linewidth=1, zorder=2)
    vline = bt_ax.axvline(x=closest_x_num, color='gray', linestyle='--', linewidth=1, zorder=2)

    # 4. 显示带格式的日期标签
    # 将浮点数日期转换回可读的日期字符串
    closest_date = mdates.num2date(closest_x_num).strftime('%Y-%m-%d')
    annotation = bt_ax.annotate(f'{closest_date}\n￥{closest_y:.2f}',
                             xy=(closest_x_num, closest_y),
                             xytext=(10, 10), textcoords='offset points',
                             bbox=dict(boxstyle='round,pad=0.3', fc='white', alpha=0.6))

    # 5. 刷新画布
    bt_figure.canvas.draw_idle()

bt_figure.canvas.mpl_connect('scroll_event', call_back)
bt_figure.canvas.mpl_connect('button_press_event', call_move)
bt_figure.canvas.mpl_connect('button_release_event', call_move)
bt_figure.canvas.mpl_connect('motion_notify_event', call_move)
bt_figure.canvas.mpl_connect('motion_notify_event', on_mouse_move)

bt_option_lbframe = ttk.Labelframe(left_frame, text="Function")
bt_option_lbframe.pack(side='top', padx=(5, 1))
tk.Label(bt_option_lbframe, text='新建变量:', font=("微软雅黑", 10)).grid(row=0, column=0, padx=7)
tk.Label(bt_option_lbframe, text='变量名:', font=("微软雅黑", 10)).grid(row=1, column=0, padx=(27, 0), pady=2)
new_variable_name_e = ttk.Entry(bt_option_lbframe, width=10, font=("微软雅黑", 10))
new_variable_name_e.grid(row=1, column=1, pady=2)
tk.Label(bt_option_lbframe, text='变量值:', font=("微软雅黑", 10)).grid(row=1, column=2, padx=(20, 0), pady=2)
new_variable_value_e = ttk.Entry(bt_option_lbframe, width=43, font=("微软雅黑", 10))
new_variable_value_e.grid(row=1, column=3, pady=2, columnspan=6)
create_variable_b = ttk.Button(bt_option_lbframe, text='创建变量', style="outline", state='disabled', command=create_new_variable)
create_variable_b.grid(row=1,column=9,padx=(6,12))

ttk.Separator(bt_option_lbframe).grid(row=2, column=0, columnspan=10, sticky='EW', pady=3, padx=6)

whole_strategy_frame = ttk.Frame(bt_option_lbframe)
whole_strategy_frame.grid(row=3, column=0, columnspan=10)

note = ttk.Notebook(whole_strategy_frame)
note.pack(ipady=2)
strategy_frame = ttk.Frame(note)
custom_frame = ttk.Frame(note)
note.add(strategy_frame, text="简单策略")
note.add(custom_frame, text="自定义策略(BackTrder)")

# ---- 简单策略----
cond_row = ttk.Frame(strategy_frame)
cond_row.pack(fill='x', padx=8, pady=(6, 0))
tk.Label(cond_row, text='买入条件:', font=("微软雅黑", 10)).pack(side='left')
buy_con_a_c = ttk.Combobox(cond_row, state='readonly', font=('微软雅黑', 9), width=11, values=variables)
buy_con_a_c.pack(side='left', padx=(4, 2))
buy_con_b_c = ttk.Combobox(cond_row, state='readonly', font=('微软雅黑', 9), width=7, values=('首次', '连续2天', '连续3天', '连续5天'))
buy_con_b_c.pack(side='left', padx=2)
buy_con_c_c = ttk.Combobox(cond_row, state='readonly', font=('微软雅黑', 9), width=4, values=(">", "<", ">=", "<=", "=", "≠"))
buy_con_c_c.pack(side='left', padx=2)
buy_con_d_e = ttk.Entry(cond_row, font=('微软雅黑', 9), width=10)
buy_con_d_e.pack(side='left', padx=2)
tk.Label(cond_row, text='/').pack(side='left', padx=2)
buy_con_d_c = ttk.Combobox(cond_row, state='readonly', font=('微软雅黑', 9), width=12, values=variables)
buy_con_d_c.pack(side='left', padx=2)
buy_con_d_e.bind('<KeyRelease>', lambda x: buy_con_d_c.set(''))
buy_con_d_c.bind('<<ComboboxSelected>>', lambda x: buy_con_d_e.delete(0, tk.END))

sell_cond_row = ttk.Frame(strategy_frame)
sell_cond_row.pack(fill='x', padx=8, pady=2)
tk.Label(sell_cond_row, text='卖出条件:', font=("微软雅黑", 10)).pack(side='left')
sell_con_a_c = ttk.Combobox(sell_cond_row, state='readonly', font=('微软雅黑', 9), width=11, values=variables)
sell_con_a_c.pack(side='left', padx=(4, 2))
sell_con_b_c = ttk.Combobox(sell_cond_row, state='readonly', font=('微软雅黑', 9), width=7, values=('首次', '连续2天', '连续3天', '连续5天'))
sell_con_b_c.pack(side='left', padx=2)
sell_con_c_c = ttk.Combobox(sell_cond_row, state='readonly', font=('微软雅黑', 9), width=4, values=(">", "<", ">=", "<=", "=", "≠"))
sell_con_c_c.pack(side='left', padx=2)
sell_con_d_e = ttk.Entry(sell_cond_row, font=('微软雅黑', 9), width=10)
sell_con_d_e.pack(side='left', padx=2)
tk.Label(sell_cond_row, text='/').pack(side='left', padx=2)
sell_con_d_c = ttk.Combobox(sell_cond_row, state='readonly', font=('微软雅黑', 9), width=12, values=variables)
sell_con_d_c.pack(side='left', padx=2)
sell_con_d_e.bind('<KeyRelease>', lambda x: sell_con_d_c.set(''))
sell_con_d_c.bind('<<ComboboxSelected>>', lambda x: sell_con_d_e.delete(0, tk.END))

ttk.Separator(strategy_frame, orient='horizontal').pack(fill='x', padx=8, pady=3)

# ---- 下单模式 ----
mode_row = ttk.Frame(strategy_frame)
mode_row.pack(fill='x', padx=8, pady=1)
tk.Label(mode_row, text='下单模式:', font=("微软雅黑", 10)).pack(side='left')
stake_mode_var = tk.StringVar(value="all")
ttk.Radiobutton(mode_row, text="全仓 ", variable=stake_mode_var, value="all", bootstyle="round-toggle").pack(side='left', padx=(40,0))
ttk.Radiobutton(mode_row, text="固定 ", variable=stake_mode_var, value="fixed", bootstyle="round-toggle").pack(side='left', padx=(40,0))
stake_fixed_e = ttk.Spinbox(mode_row, from_=1, to=999999, width=6, font=('微软雅黑', 9))
stake_fixed_e.pack(side='left', padx=2)
stake_fixed_e.set(100)
tk.Label(mode_row, text='手').pack(side='left', padx=(0, 4))
ttk.Radiobutton(mode_row, text="资金% ", variable=stake_mode_var, value="pct", bootstyle="round-toggle").pack(side='left', padx=(40,0))
stake_pct_e = ttk.Spinbox(mode_row, from_=1, to=100, width=5, font=('微软雅黑', 9))
stake_pct_e.pack(side='left', padx=2)
stake_pct_e.set(95)
tk.Label(mode_row, text='%').pack(side='left')

# ---- 止损止盈 + 按钮 ----
bottom_row = ttk.Frame(strategy_frame)
bottom_row.pack(fill='x', padx=8, pady=2)
tk.Label(bottom_row, text='止损:', font=("微软雅黑", 10)).pack(side='left', padx=(80,0))
stop_loss_e = ttk.Entry(bottom_row, font=('微软雅黑', 9), width=6)
stop_loss_e.pack(side='left', padx=2)
stop_loss_e.insert(0, "0")
tk.Label(bottom_row, text='%       止盈:', font=("微软雅黑", 10)).pack(side='left', padx=(4, 0))
take_profit_e = ttk.Entry(bottom_row, font=('微软雅黑', 9), width=6)
take_profit_e.pack(side='left', padx=2)
take_profit_e.insert(0, "0")
tk.Label(bottom_row, text='%').pack(side='left')
apply_bt_b = ttk.Button(bottom_row, text='执行回测', style="outline", state='disabled', command=apply_simple_backtest)
apply_bt_b.pack(side='right', padx=2, pady=(2,0))
clear_condition_b = ttk.Button(bottom_row, text='清空条件', style="outline", command=clear_conditions, state=tk.DISABLED)
clear_condition_b.pack(side='right', padx=2, pady=(2,0))

custom_input_frame = ttk.Frame(custom_frame)
custom_input_frame.pack(side='left', pady=(3, 0))
custom_strategy_text = tk.Text(custom_input_frame, font=("微软雅黑", 10), width=68, height=6)
custom_strategy_text.pack(side="left", padx=(3, 0), pady=(0, 3))
custom_strategy_text_yscrollbar = ttk.Scrollbar(custom_input_frame, command=custom_strategy_text.yview, style="round")
custom_strategy_text_yscrollbar.pack(side="right", fill='y', pady=(0, 3))
custom_strategy_text.config(yscrollcommand=custom_strategy_text_yscrollbar.set)
ide.setup_syntax_highlight(custom_strategy_text)
custom_strategy_text.insert(tk.END, "class CustomStrategy(bt.Strategy):")
custom_func_frame = ttk.Frame(custom_frame)
custom_func_frame.pack(side='left', pady=(3, 0), padx=(18,2))
clear_custom_strategy_b = ttk.Button(custom_func_frame, text='清空策略', style="outline", cursor='hand2', command=lambda: custom_strategy_text.delete(1.0, tk.END))
clear_custom_strategy_b.grid(row=0, column=0, padx=(15, 0), pady=3)
apply_custom_bt_b = ttk.Button(custom_func_frame, text='执行回测', style="outline", state=tk.DISABLED, command=apply_custom_backtest)
apply_custom_bt_b.grid(row=1, column=0, padx=(15, 0), pady=3)

# right_frame
up_down_label = tk.Label(right_frame, text=' ', font=("微软雅黑", 2), width=1, height=12)
up_down_label.grid(row=0, column=0, rowspan=2)
up_down_label.configure(bg='#ababab')
price_show_label = tk.Label(right_frame, text=str(current_price_show), font=("微软雅黑", 27, 'bold'), width=8)
price_show_label.grid(row=0, column=1, rowspan=2, columnspan=3)
price_show_label.config(fg='#ececec')
flu_range_label = tk.Label(right_frame, text=str(flu_range_show), font=("微软雅黑", 10, 'bold'))
flu_range_label.grid(row=0, column=4)
flu_range_spot_label = tk.Label(right_frame, text=str(flu_range_spot_show), font=("微软雅黑", 10, 'bold'))
flu_range_spot_label.grid(row=0, column=5, padx=(0, 1))
date_label = tk.Label(right_frame, text=str(price_date_show), font=("微软雅黑", 10, 'bold'), width=21)
date_label.grid(row=1, column=4, padx=(3, 1), columnspan=2)

add_b = ttk.Button(right_frame, text='添加股票', style="outline", cursor='hand2', command=add_stock) #, command=add_stock
add_b.grid(row=0, column=6, padx=(0, 1), pady=(1, 0), rowspan=2)
delete_b = ttk.Button(right_frame, text='删除股票', style="outline", state='disabled', command=drop_stock) #, command=drop_stock
delete_b.grid(row=0, column=7, padx=(2, 1), pady=(1, 0), rowspan=2)
detail_b = ttk.Menubutton(right_frame, text='股票详情', style="outline", state='disabled')
detail_b.grid(row=0, column=8, padx=(2, 1), pady=(1, 0), rowspan=2)
menu = ttk.Menu(detail_b)
menu.add_command(label="基本信息", command=lambda :view_data(stock_selected.profile.T.reset_index()))
menu.add_command(label="历史数据", command=lambda :view_data(stock_selected.his_df))
menu.add_command(label="K线图", command=lambda :stock_selected.plot_k_line())
menu.add_command(label="资产负债表", command=lambda :view_data(stock_selected.al_statement.T.reset_index()))
menu.add_command(label="现金流量表", command=lambda :view_data(stock_selected.cf_statement.T.reset_index()))
menu.add_command(label="利润表", command=lambda :view_data(stock_selected.profit_statement.T.reset_index()))
menu.add_command(label="业绩快报", command=lambda :view_data(stock_selected.express.T.reset_index()))
menu.add_command(label="财务指标", command=lambda :view_data(stock_selected.fin_indicators.T.reset_index()))
menu.add_command(label="估值指标", command=lambda :view_data(stock_selected.val_indicators))
menu.add_command(label="分红送股", command=lambda :view_data(stock_selected.dividend))
detail_b.config(menu=menu)

listbox_lbframe = tk.LabelFrame(right_frame, text=f'Portfolio(0)--(￥0)')
listbox_lbframe.grid(row=2, column=0, padx=(10,1), pady=1, columnspan=4, sticky=tk.W)
v_listbox = tk.Listbox(listbox_lbframe, width=27, height=8, selectmode='single', exportselection=False)
v_listbox.grid(row=0, column=0, padx=(2, 0), pady=(0, 3))
v_listbox_yscrollbar = ttk.Scrollbar(listbox_lbframe, command=v_listbox.yview, style="round")
v_listbox_yscrollbar.grid(row=0, column=1, sticky='ns')
v_listbox.config(yscrollcommand=v_listbox_yscrollbar.set)
v_listbox.bind('<<ListboxSelect>>', show_selected_stock)
update_portfolio_name()
port_weight_bar = ttk.Progressbar(listbox_lbframe, orient='vertical', length=177, maximum=portfolio_value)
port_weight_bar.grid(row=0, column=2, padx=2, sticky='ns')

# ---- 交易记录显示区（插入在 Portfolio 和 Outcome 之间）----
trade_lbframe = tk.LabelFrame(right_frame, text='Tradings', height=340, width=50)
trade_lbframe.grid(row=3, column=0, padx=(10, 1), pady=1, columnspan=4, sticky='nsew')
trade_lbframe.grid_propagate(False)
trade_table_frame = tk.Frame(trade_lbframe)
trade_table_frame.pack()
trade_table_frame.pack_propagate(False)
trade_table_ref = Table(trade_table_frame, height=200, width=218, cols=8)
trade_table_ref.cellbackgr = "#373737"
trade_table_ref.rowselectedcolor = "#707070"
trade_table_ref.rowheaderbgcolor = "#505050"
trade_table_ref.textcolor = "#ececec"
trade_table_ref.font = ("Arial", 6)
trade_table_ref.setRowHeight(21)
# 设置初始列名（空表格时也显示表头）
trade_table_ref.model.columnNames = ["开仓日", "平仓日", "买入价", "卖出价", "数量", "盈亏", "盈亏%"]
trade_table_ref.show()
trade_table_ref.zoomOut()
trade_table_ref.redraw()

outcome_lbframe = ttk.Labelframe(right_frame, text="Outcome")
outcome_lbframe.grid(row=4, padx=(10,1), pady=1, columnspan=5, sticky=tk.W)
outcome_text = tk.Text(outcome_lbframe, font=("微软雅黑", 10), width=25, height=11, state="disabled")
outcome_text.pack(side="left", padx=(3, 0), pady=(0, 3))
outcome_text_yscrollbar = ttk.Scrollbar(outcome_lbframe, command=outcome_text.yview, style="round")
outcome_text_yscrollbar.pack(side="right", fill='y', pady=(0, 3))
outcome_text.config(yscrollcommand=outcome_text_yscrollbar.set)

save_figure_b = ttk.Button(right_frame, style='outline', text='导出结果', state='disabled', command=export_bt_result)
save_figure_b.grid(row=5, column=0, padx=(11, 0), pady=4, columnspan=2, sticky=tk.W)
cerebro_plot_b = ttk.Button(right_frame, style='outline', text='图像结果', state='disabled', command=_show_bt_plot)
cerebro_plot_b.grid(row=5, column=2, padx=(6, 0), pady=4)
clear_strategy_b = ttk.Button(right_frame, style='outline', text='重置回测', state='disabled', command=clear_backtest)
clear_strategy_b.grid(row=5, column=3, padx=(0, 0), pady=4)

after_grab_stock_b = [delete_b, detail_b, create_variable_b, apply_bt_b, clear_condition_b, apply_custom_bt_b]
after_bt_b = [save_figure_b, cerebro_plot_b, clear_strategy_b]

# ai_frame
ai_lbframe = ttk.Labelframe(right_frame, text="Agent (Deepseek-chat)")
ai_lbframe.grid(row=2, column=4, columnspan=7, rowspan=4, padx=2)
ai_output_frame = tk.Frame(ai_lbframe, height=583, width=527)
ai_output_frame.pack(side="top")
ai_output_frame.pack_propagate(False)

ai_input_frame = tk.Frame(ai_lbframe)
ai_input_frame.pack(side="top", pady=(17, 0))
tk.Label(ai_input_frame, text='问问 Deepseek:', font=("微软雅黑", 10)).grid(row=0, column=0,sticky=tk.W)
ai_input_text = tk.Text(ai_input_frame, font=("微软雅黑", 10), width=50, height=6)
ai_input_text.grid(row=1, column=0, pady=(0, 5))
ai_input_text.config(bg=figure_color, foreground='black')
send_b = ttk.Button(ai_input_frame, style='outline', cursor='hand2', text='发送')
send_b.grid(row=1, column=0, sticky=tk.E, padx=(0, 4), pady=(86, 4))

deepseek = ai_module.attach_ai(ai_output_frame, ai_input_text, send_b)

root.mainloop()