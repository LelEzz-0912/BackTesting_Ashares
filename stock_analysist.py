import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import akshare as ak
import ttkbootstrap as ttk
import tkinter as tk
import talib as ta
import datetime
import math
import webbrowser
import mplfinance as mpf
import tkinter.filedialog
from pandastable.core import Table
from tkinter import messagebox
from matplotlib.widgets import Cursor
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# 主窗口
root = ttk.Window(themename="superhero")
style = ttk.Style()
root.wm_attributes("-alpha", 0.995)
root.geometry("1168x729")
root.title("Stock Analysis (A Share)")

#定义frame
tp_frame = tk.Frame(root)
info_frame = tk.Frame(root)
describe_frame = tk.Frame(root)
bt_frame = tk.Frame(root)
tp_frame.pack(side='top', fill='x', pady=(10,5))
info_frame.pack(side='top', fill='x', pady=(15,9))
describe_frame.pack(side='top', fill='x', padx=(6,0))
bt_frame.pack(side='top', fill='x', padx=(6,0))

#定义变量
data = pd.DataFrame()
mktdata = pd.DataFrame()
institute_recommend_df = pd.DataFrame()
institution_evaluation_df = pd.DataFrame()
profile_df = pd.DataFrame()
fin_abstract_data = pd.DataFrame()
fin_report_al = pd.DataFrame()
fin_report_be = pd.DataFrame()
fin_report_xjll = pd.DataFrame()
all_stock_data = pd.DataFrame()
industry_info_df = pd.DataFrame()
industry_search_df = pd.DataFrame()
stock_valuation_df = pd.DataFrame()
dividend_df = pd.DataFrame()
cap_structure_df = pd.DataFrame()
window_df = pd.DataFrame()
rf_data = pd.DataFrame()
rf_des_df = pd.DataFrame()
individual_report_df = pd.DataFrame()
news_df = pd.DataFrame()
inday_df = pd.DataFrame()
summary_df_sh = pd.DataFrame()
summary_df_sz = pd.DataFrame()
ESG_df = pd.DataFrame()
bid_ask_df = pd.DataFrame()
data_for_bt = pd.DataFrame()

reload_df_list = [fin_abstract_data, fin_report_al, fin_report_be, fin_report_xjll, dividend_df, cap_structure_df, individual_report_df, industry_search_df]

stock_code = tk.StringVar()
adjust = tk.StringVar()
period = tk.StringVar()
start_date = tk.StringVar()
end_date = tk.StringVar()
mkt_code = tk.StringVar()
rf = tk.StringVar()
rm = tk.StringVar()
capm_out_str = tk.StringVar()
industry_name = tk.StringVar()
window_title = tk.StringVar()
s_path = tk.StringVar()
sf_path = tk.StringVar()

pb_ratio = 0
pe_ratio = 0
pb_ratio_show = '{:.2f}'.format(pb_ratio) + '( )'
pe_ratio_show = '{:.2f}'.format(pe_ratio) + '( )'
days = 0
price_date = '0000-00-00'
price_date_show = f'{days} days to {price_date}'
current_price = 0
intraday_price = 0
flu_range = 0
intraday_range = 0
flu_range_spot = 0
intraday_time = '00:00:00'
current_price_show = '{:.2f}'.format(current_price)
intraday_price_show = '{:.2f}'.format(intraday_price)
flu_range_show = str(' ' + '{:.2f}'.format(flu_range) + '%')
intraday_range_show = str(' ' + '{:.2f}'.format(intraday_range) + '%')
flu_range_spot_show = str(' (' + '{:.2f}'.format(flu_range_spot) + '%)')
Erp = 0
Erp_annual = 0
SR = 0
rf_label_text = '年化无风险利率(%):'
code_name_text = '股票代码:'
up = '#f34334'
down = '#21be87'
auto_update_value = 0
bt_df_list = []
variables = []

# 定义函数
def judge_interface(event):
    if interface_combobox.get() != '东方财富':
        frequency_combobox.set('日数据')
        frequency_combobox.config(state='disabled')
    else:
        frequency_combobox.config(state='readonly')

def get_trading_date():
    if datetime.date.isoweekday(datetime.date.today()) == 1:
        date = datetime.date.today() - datetime.timedelta(days=3)
    elif datetime.date.isoweekday(datetime.date.today()) <= 6:
        date = datetime.date.today() - datetime.timedelta(days=1)
    else:
        date = datetime.date.today() - datetime.timedelta(days=2)
    return date

def change_code_name():
    global code_name_text
    if code_name_text == "股票代码:":
        code_name_text = "股票简称:"
        code_or_name.config(text=code_name_text)
    else:
        code_name_text = "股票代码:"
        code_or_name.config(text=code_name_text)

def get_data():
    global data
    global adjust
    global period
    global stock_code
    global start_date
    global end_date
    global code_name_text
    global stock_valuation_df
    global bt_df_list
    global data_for_bt

    if code_name_text == "股票代码:":
        stock_code = stock_code_entry.get()
    else:
        stock_name_df = ak.stock_info_a_code_name().set_index('name')
        stock_code = str(stock_name_df.loc[stock_code_entry.get(), "code"])

    start_m = '{:02d}'.format(int(start_month.get()))
    end_m = '{:02d}'.format(int(end_month.get()))
    start_d = '{:02d}'.format(int(start_day.get()))
    end_d = '{:02d}'.format(int(end_day.get()))
    start_date = str(str(start_year.get()) + str(start_m) + str(start_d))
    end_date = str(str(end_year.get()) + str(end_m) + str(end_d))


    if fq_combobox.get() == '前复权':
        adjust = 'qfq'
    elif fq_combobox.get() == '后复权':
        adjust = 'hfq'

    if frequency_combobox.get() == '日数据':
        period = 'daily'
    elif frequency_combobox.get() == '周数据':
        period = 'weekly'
    elif frequency_combobox.get() == '月数据':
        period = 'monthly'

    if interface_combobox.get() == '东方财富':
        data = ak.stock_zh_a_hist(symbol=stock_code, start_date=start_date, end_date=end_date,
                                      period=period, adjust=adjust)

    if interface_combobox.get() == '新浪财经':
        data = ak.stock_zh_a_daily(symbol=stock_code, start_date=start_date, end_date=end_date,
                                       adjust=adjust)

    if interface_combobox.get() == '新浪财经':
        data = ak.stock_zh_a_hist_tx(symbol=stock_code, start_date=start_date, end_date=end_date,
                                       adjust=adjust)
    stock_valuation_df = ak.stock_value_em(symbol=stock_code)

    data['简单收益率'] = (data['收盘'] - data['收盘'].shift(1)) / data['收盘'].shift(1)
    data['对数收益率'] = np.log(data['收盘'] / data['收盘'].shift(1))
    data["RSI"] = ta.RSI(data['收盘'], timeperiod=12)
    data["MOM(5 days)"] = ta.MOM(data['收盘'], timeperiod=5)
    data["MA(5 days)"] = data['收盘'].rolling(5).mean()
    data["MA(10 days)"] = data['收盘'].rolling(10).mean()
    data["MA(20 days)"] = data['收盘'].rolling(20).mean()

    data_for_bt = data.copy()
    stock_code_entry.delete(0, tk.END)
    stock_code_entry.insert(0, stock_code)
    code_name_text = '股票代码:'
    code_or_name.config(text=code_name_text)

    bt_df_list.append('data_for_bt')
    bt_df_list.append('stock_valuation_df')

def update_info():
    global current_price
    global current_price_show
    global flu_range_show
    global flu_range
    global price_date
    global flu_range_spot_show
    global flu_range_spot
    global days
    global price_date_show
    global pe_ratio
    global pe_ratio_show
    global pb_ratio
    global pb_ratio_show
    global stock_valuation_df

    current_price = data['收盘'].iloc[-1]
    current_price_show = '{:.2f}'.format(current_price)
    price_show_label.config(text=current_price_show)

    flu_range = ((data['收盘'].iloc[-1] - data['收盘'].iloc[0]) / data['收盘'].iloc[0]) * 100
    if flu_range >= 0:
        flu_range_show = str("+" + '{:.2f}'.format(flu_range) + '%')
        fg_h = up
        bg = up
    else:
        flu_range_show = str('{:.2f}'.format(flu_range) + '%')
        fg_h = down
        bg = down

    flu_range_spot = data['涨跌幅'].iloc[-1]
    if flu_range_spot >= 0:
        flu_range_spot_show = str("(+" + '{:.2f}'.format(flu_range_spot) + '%)')
        fg_s = up
    else:
        flu_range_spot_show = str('(' + '{:.2f}'.format(flu_range_spot) + '%)')
        fg_s = down

    flu_range_spot_label.config(text=flu_range_spot_show, fg=fg_s)
    flu_range_label.config(text=flu_range_show, fg=fg_h)
    up_down_label.config(bg=bg)

    price_date = data['日期'].iloc[-1]
    days = data.shape[0]
    price_date_show = f'{days} days to {price_date}'
    date_label.config(text=price_date_show)

    ax.clear()
    ax.axis('off')
    ax.plot(data['日期'], data['收盘'], color=fg_h, linewidth=1)
    ax.axhline(y=data['收盘'].mean(), color='#ececec', alpha=0.6, linestyle='--', linewidth=0.8)
    canvas.draw()

    pb_ratio = stock_valuation_df['市净率'].iloc[-1]
    pe_ratio = stock_valuation_df['PE(静)'].iloc[-1]
    pb_scale.config(state='normal')
    pe_scale.config(state='normal')

    if pb_ratio > 2:
        pb_scale.set(2)
        arrow_pb = '↑'
    elif pb_ratio < 0.5:
        pb_scale.set(0.5)
        arrow_pb = '↓'
    else:
        pb_scale.set(pb_ratio)
        arrow_pb = '→'

    if pe_ratio > 30:
        pe_scale.set(30)
        arrow_pe = '↑'
    elif pe_ratio < 10:
        pe_scale.set(10)
        arrow_pe = '↓'
    else:
        pe_scale.set(pe_ratio)
        arrow_pe = '→'

    pb_scale.config(state='disabled')
    pe_scale.config(state='disabled')

    pb_ratio_show = str('{:.2f}'.format(pb_ratio)) + str(arrow_pb)
    pe_ratio_show = str('{:.2f}'.format(pe_ratio)) + str(arrow_pe)
    pb_value_label.config(text=pb_ratio_show)
    pe_value_label.config(text=pe_ratio_show)

def describe_data():
    global data
    data_desc = data.describe()
    table_desc.model.df = data_desc
    table_desc.show()
    table_desc.font = ('Arial', 12)
    table_desc.redraw()

def data_profile():
    global stock_code
    global start_date
    global end_date
    global profile_df

    profile_df = ak.stock_profile_cninfo(symbol=stock_code).T.reset_index()
    df_temp = ak.stock_individual_info_em(symbol=stock_code)
    add_row = df_temp.set_index('item').iloc[7]
    ind = df_temp['value'].iloc[7]
    profile_table.model.df = pd.concat([profile_df, add_row], ignore_index=True)
    profile_table.show()
    profile_table.font = ('Arial', 12)
    profile_table.redraw()
    industry_label_e.delete(0, 'end')
    industry_label_e.insert(0,ind)

def data_indicator():
    global fin_abstract_data
    global stock_code

    if fin_abstract_data.empty:
        fin_abstract_data = ak.stock_financial_abstract_ths(stock_code, '按报告期')
    indicator_table.model.df = fin_abstract_data.sort_values(by='报告期', ascending=False).T.reset_index()
    indicator_table.show()
    indicator_table.font = ('Arial', 12)
    indicator_table.redraw()

    bt_df_list.append('fin_abstract_data')

def macd_func(df):
    exp12 = df['Close'].ewm(span=12, adjust=False).mean()
    exp26 = df['Close'].ewm(span=26, adjust=False).mean()
    macd = exp12 - exp26
    signal = macd.ewm(span=9, adjust=False).mean()
    histogram = macd - signal
    return exp12, exp26, histogram, signal, macd

def boll_signal(df, n, m):
    boll_data = df.copy()
    mid = boll_data['Close'].rolling(n).mean()
    upper = mid + m * boll_data['Close'].rolling(n).std()
    lower = mid - m * boll_data['Close'].rolling(n).std()
    boll_data['mid'] = mid
    boll_data['upper'] = upper
    boll_data['lower'] = lower

    boll_data['close_lag1'] = boll_data['Close'].shift()
    boll_data['lower_lag1'] = boll_data['lower'].shift()
    boll_data['upper_lag1'] = boll_data['upper'].shift()
    boll_data['buy_signal'] = boll_data.query('Close > lower and close_lag1 < lower_lag1')['Low'] * 0.99
    boll_data['sell_signal'] = boll_data.query('Close < upper and close_lag1 > upper_lag1')['High'] * 1.01
    return boll_data['buy_signal'], boll_data['sell_signal']

def kline():
    global stock_code
    global up
    global down
    data_for_plot = data.rename(columns={"日期": "date"})
    data_for_plot = data_for_plot.set_index('date')[['开盘', '最高', '最低', '收盘', '成交量']]
    data_for_plot.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    data_for_plot.index = pd.to_datetime(data_for_plot.index)
    # 绘制K线图
    mc = mpf.make_marketcolors(up=up, down=down, volume='inherit')
    s = mpf.make_mpf_style(marketcolors=mc, y_on_right=False, gridaxis='both', facecolor='#c9c9c9', figcolor='#888888')

    exp12, exp26, histogram, signal, macd = macd_func(data_for_plot)
    buy_signal, sell_signal = boll_signal(data_for_plot, 20, 2)
    add_plot = [mpf.make_addplot(histogram, type='bar', width=0.7, panel=2, color='dimgray', secondary_y=False),
                mpf.make_addplot(macd, panel=2, color='fuchsia', secondary_y=True),
                mpf.make_addplot(signal, panel=2, color='b', secondary_y=True),
                mpf.make_addplot(buy_signal, type='scatter', markersize=45, marker='^', color='r'),
                mpf.make_addplot(sell_signal, type='scatter', markersize=45, marker='v', color='g')]

    mpf.plot(data_for_plot, type='candle', volume=True, title={"title": stock_code, "y": 1}, addplot=add_plot, panel_ratios=(7,2,2),
             ylabel='Price', ylabel_lower='Volume', mav=(5, 10, 30), style=s, figscale=1.5, tight_layout=True)

    # kax, kax2 = finplot.create_plot(stock_code, rows=2)
    # finplot.candlestick_ochl(data_for_plot[['Open', 'Close', 'High', 'Low']], ax=kax, colorfunc=finplot.color_func_diy)
    # finplot.volume_ocv(data_for_plot[['Open', 'Close', 'Volume']], ax=kax2, colorfunc=finplot.volume_colorfilter_diy)
    # finplot.plot(data_for_plot['Close'].rolling(5).mean(), ax=kax, legend='MA-5')
    # finplot.plot(data_for_plot['Close'].rolling(10).mean(), ax=kax, legend='MA-10')
    # finplot.plot(data_for_plot['Close'].rolling(20).mean(), ax=kax, legend='MA-20')
    # lo_wicks = data_for_plot[['Open', 'Close']].T.min() - data_for_plot['Low']
    # data_for_plot.loc[(lo_wicks > lo_wicks.quantile(0.99)), 'Marker'] = data_for_plot['Low']
    # finplot.plot(data_for_plot['Marker'], ax=kax, color='#4a5', style='^', legend='dumb mark')
    # finplot.show()

def rsi_mom():
    try:
        global data
        fig_rsi = plt.figure()
        fig_rsi.patch.set_facecolor('#888888')
        ax_rsi = plt.axes(facecolor='#c9c9c9')
        ax_rsi.plot(data['日期'], data['RSI'], label='RSI',linewidth=1.8)
        ax_rsi.grid(False)
        ax_mom = ax_rsi.twinx()
        ax_mom.plot(data['日期'], data['MOM(5 days)'], label='MOM', color='#666666',alpha=0.6)
        ax_mom.grid(True)

        startx = 0
        starty = 0
        mPress = False

        def call_back(event):
            axtemp = event.inaxes
            base_scale = 1.5
            x_min, x_max = axtemp.get_xlim()  ##获取x轴范围
            y_min, y_max = axtemp.get_ylim()  ##获取y轴范围
            fanwei_x = (x_max - x_min) / 2  # 范围缩放
            fanwei_y = (y_max - y_min) / 2
            xdata = event.xdata  # get event x location
            ydata = event.ydata  # get event y location
            if event.button == 'up':
                # deal with zoom in
                scale_factor = 1 / base_scale
            elif event.button == 'down':
                # deal with zoom out
                scale_factor = base_scale
            else:
                # deal with something that should never happen
                scale_factor = 1

            axtemp.set(xlim=(xdata - fanwei_x * scale_factor, xdata + fanwei_x * scale_factor))
            # axtemp.set(ylim=(ydata - fanwei_y * scale_factor, ydata + fanwei_y * scale_factor))
            fig_rsi.canvas.draw_idle()  # 绘图动作实时反映在图像上

        def call_move(event):
            # print(event.name)
            global mPress
            global startx
            global starty
            mouse_x = event.x
            mouse_y = event.y
            axtemp = event.inaxes
            if event.name == 'button_press_event':
                if axtemp and event.button == 1:
                    if axtemp.get_legend():
                        legend_bbox = axtemp.get_legend().get_window_extent()
                        left_bottom = legend_bbox.get_points()[0]
                        right_top = legend_bbox.get_points()[1]

                        if left_bottom[0] <= mouse_x <= right_top[0] and left_bottom[1] <= mouse_y <= right_top[1]:
                            # print("在图例上按下鼠标")
                            # 在图例上按下鼠标
                            mPress = False
                            return
                    # 没有图例的情况
                    # print("在 Axes 上按下鼠标")
                    # 在 Axes 上按下鼠标
                    mPress = True
                    startx = event.xdata
                    starty = event.ydata
                    return
            elif event.name == 'button_release_event':
                if axtemp and event.button == 1:
                    mPress = False
            elif event.name == 'motion_notify_event':
                if axtemp and event.button == 1 and mPress:
                    if axtemp.get_legend():
                        legend_bbox = axtemp.get_legend().get_window_extent()
                        left_bottom = legend_bbox.get_points()[0]
                        right_top = legend_bbox.get_points()[1]

                        if left_bottom[0] <= mouse_x <= right_top[0] and left_bottom[1] <= mouse_y <= right_top[1]:
                            print("在图例上移动鼠标")
                            # 在图例上按下鼠标
                            mPress = False
                            return

                    # 没有图例的情况
                    # print("在Axes上移动鼠标")
                    x_min, x_max = axtemp.get_xlim()
                    y_min, y_max = axtemp.get_ylim()
                    w = x_max - x_min
                    h = y_max - y_min
                    # print(event)
                    # 移动
                    mx = event.xdata - startx
                    my = event.ydata - starty
                    # 注意这里， -mx,  因为下一次 motion事件的坐标，已经是在本次做了移动之后的坐标系了，所以要体现出来
                    # startx=event.xdata-mx  startx=event.xdata-(event.xdata-startx)=startx, 没必要再赋值了
                    # starty=event.ydata-my
                    # print(mx,my,x_min,y_min,w,h)
                    left = x_min - mx
                    right = x_min - mx + w

                    axtemp.set(xlim=(left, right))

                    # axtemp.set(ylim=(y_min - my, y_min - my + h))
                    fig_rsi.canvas.draw_idle()  # 绘图动作实时反映在图像上

            return

        fig_rsi.canvas.mpl_connect('scroll_event', call_back)
        fig_rsi.canvas.mpl_connect('button_press_event', call_move)
        fig_rsi.canvas.mpl_connect('button_release_event', call_move)
        fig_rsi.canvas.mpl_connect('motion_notify_event', call_move)

        ax_rsi.axhline(30, color='#303030', linestyle='--', linewidth=0.8)
        ax_rsi.axhline(70, color='#303030', linestyle='--', linewidth=0.8)
        plt.title('RSI & Momentum')
        plt.xlabel('Date')
        ax_rsi.set_ylabel('RSI')
        ax_rsi.set_ylabel('MOM(5)')
        ax_rsi.legend()
        plt.show()
    except Exception as e:
        tk.messagebox.showerror("Error", f"绘制失败: {str(e)}")

def mkt_kline():
    global mkt_code
    global up
    global down
    try:
        mktdata_for_plot = mktdata.rename(columns={"日期": "date"})
        mktdata_for_plot = mktdata_for_plot.set_index('date')[['开盘', '最高', '最低', '收盘', '成交量']]
        mktdata_for_plot.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        mktdata_for_plot.index = pd.to_datetime(mktdata_for_plot.index)
        # 绘制K线图
        mc = mpf.make_marketcolors(up=up, down=down, volume='inherit')
        s = mpf.make_mpf_style(marketcolors=mc, y_on_right=False, gridaxis='both', facecolor='#c9c9c9', figcolor='#888888')

        exp12, exp26, histogram, signal, macd = macd_func(mktdata_for_plot)
        buy_signal, sell_signal = boll_signal(mktdata_for_plot, 20, 2)
        mkt_add_plot = [mpf.make_addplot(histogram, type='bar', width=0.7, panel=2, color='dimgray', secondary_y=False),
                    mpf.make_addplot(macd, panel=2, color='fuchsia', secondary_y=True),
                    mpf.make_addplot(signal, panel=2, color='b', secondary_y=True),
                    mpf.make_addplot(buy_signal, type='scatter', markersize=45, marker='^', color='r'),
                    mpf.make_addplot(sell_signal, type='scatter', markersize=45, marker='v', color='g')]

        mpf.plot(mktdata_for_plot, type='candle', volume=True, title=mkt_code, addplot=mkt_add_plot, panel_ratios=(7,2,2)
                 , ylabel='Price', ylabel_lower='Volume', mav=(5, 10, 30), style=s, figscale=1.5, tight_layout=True)
    except Exception as e:
        tk.messagebox.showerror("Error", f"绘制失败: {str(e)}")

def scatter_line():
    try:
        fig_sl = plt.figure()
        fig_sl.patch.set_facecolor('#888888')
        ax_sl = plt.axes(facecolor='#c9c9c9')
        ax_sl.scatter(x=data['日期'], y=data['简单收益率'] * 100)
        ax_sl.grid(True)
        cursor = Cursor(ax_sl, useblit=True, color='#888888', linewidth=1.5)
        plt.title('Scatter Plot')
        plt.xlabel('Date')
        plt.ylabel('Return')
        plt.show()
    except Exception as e:
        tk.messagebox.showerror("Error", f"绘制失败: {str(e)}")

def pe_line():
    global stock_valuation_df
    global stock_code
    try:
        if stock_valuation_df.empty:
            stock_valuation_df = ak.stock_value_em(symbol=stock_code)
        fig_pe = plt.figure()

        def call_back(event):
            axtemp = event.inaxes
            base_scale = 2
            x_min, x_max = axtemp.get_xlim()  ##获取x轴范围
            y_min, y_max = axtemp.get_ylim()  ##获取y轴范围
            fanwei_x = (x_max - x_min) / 2  # 范围缩放
            fanwei_y = (y_max - y_min) / 2
            xdata = event.xdata  # get event x location
            ydata = event.ydata  # get event y location
            if event.button == 'up':
                # deal with zoom in
                scale_factor = 1 / base_scale
            elif event.button == 'down':
                # deal with zoom out
                scale_factor = base_scale
            else:
                # deal with something that should never happen
                scale_factor = 1

            axtemp.set(xlim=(xdata - fanwei_x * scale_factor, xdata + fanwei_x * scale_factor))
            axtemp.set(ylim=(ydata - fanwei_y * scale_factor, ydata + fanwei_y * scale_factor))
            #     axtemp.set(ylim=(ydata  - fanwei_y*2, ydata  + fanwei_y*2))
            fig_pe.canvas.draw_idle()  # 绘图动作实时反映在图像上

        fig_pe.canvas.mpl_connect('scroll_event', call_back)
        fig_pe.canvas.toolbar.pan()
        fig_pe.patch.set_facecolor('#888888')
        ax_pe = plt.axes(facecolor='#c9c9c9')

        ax_pe.plot(stock_valuation_df["数据日期"] , stock_valuation_df['PE(TTM)'], label='PE(TTM)')
        ax_pe.plot(stock_valuation_df["数据日期"], stock_valuation_df['PE(静)'], label='PE(static)')
        ax_pe.grid(True)
        plt.title('PE Line Plot')
        plt.xlabel('Date')
        plt.ylabel('PE')
        ax_pe.legend()
        plt.show()

    except Exception as e:
        tk.messagebox.showerror("Error", f"绘制失败: {str(e)}")

def enable_button():
    enable_b = [view_data_b, kline_b, scatterline_b, fin_report_b, fin_benefit_b, fin_abstract_b, valuation_b,
                individual_report_b, pe_line_b, inday_b, capital_structure_b, dividend_b, rsi_b, backtesting_b]
    for b in enable_b:
        b.config(state='normal', cursor='hand2')

def grab_data(event=None):
    global bt_df_list
    try:
        for dfn in reload_df_list:
            dfn.drop(index=dfn.index)

        bt_df_list = []

        if stock_code_entry.get() and start_year.get() and end_year.get() and start_month.get() and end_month.get() and start_day.get() and end_day.get() != '':
            get_data()
            enable_button()
            data_profile()
            data_indicator()
            describe_data()
            update_info()
            if not mktdata.empty:
                build_model_b.config(state=tk.NORMAL, cursor='hand2')

        elif stock_code_entry.get() == '':
            tk.messagebox.showerror("Error", "获取数据失败: 请输入股票代码或股票简称！")
        elif start_year.get() or end_year.get() or start_month.get() or end_month.get() or start_day.get() or end_day.get() == '':
            tk.messagebox.showerror("Error", "获取数据失败: 请输入完整的起始日期！")
    except KeyError:
        tk.messagebox.showerror("Error", f"获取数据失败: 请检查股票代码或简称！")
    except Exception as e:
        tk.messagebox.showerror("Error", f"获取数据失败: {str(e)}")

def grab_mkt_data():
    global mktdata
    global adjust
    global period
    global start_date
    global end_date
    global mkt_code

    try:
        if start_year.get() and end_year.get() and start_month.get() and end_month.get() and start_day.get() and end_day.get() != '':
            if market_combobox.get() == '上证指数':
                mkt_code = '000001'
            elif market_combobox.get() == '深证成指':
                mkt_code = '399001'
            elif market_combobox.get() == '沪深300':
                mkt_code = '399300'
            elif market_combobox.get() == '创业板指数':
                mkt_code = '399006'
            elif market_combobox.get() == '科创50':
                mkt_code = '000688'
            elif market_combobox.get() == '北证50':
                mkt_code = '899050'

            start_m = '{:02d}'.format(int(start_month.get()))
            end_m = '{:02d}'.format(int(end_month.get()))
            start_d = '{:02d}'.format(int(start_day.get()))
            end_d = '{:02d}'.format(int(end_day.get()))
            start_date = str(str(start_year.get()) + str(start_m) + str(start_d))
            end_date = str(str(end_year.get()) + str(end_m) + str(end_d))

            if fq_combobox.get() == '前复权':
                adjust = 'qfq'
            elif fq_combobox.get() == '后复权':
                adjust = 'hfq'

            if frequency_combobox.get() == '日数据':
                period = 'daily'
            elif frequency_combobox.get() == '周数据':
                period = 'weekly'
            elif frequency_combobox.get() == '月数据':
                period = 'monthly'

            mktdata = ak.index_zh_a_hist(symbol=mkt_code, start_date=start_date, end_date=end_date,
                                          period=period)

            view_mkt_data_b.config(state=tk.NORMAL, cursor='hand2')
            view_mkt_des_b.config(state=tk.NORMAL, cursor='hand2')
            mkt_kline_b.config(state=tk.NORMAL, cursor='hand2')
            if not data.empty:
                build_model_b.config(state=tk.NORMAL, cursor='hand2')

            mktdata_for_capm = mktdata.copy()
            mktdata_for_capm['multiple'] = (mktdata_for_capm['涨跌幅'] + 100) / 100

            annual_rm = mktdata_for_capm['multiple'].prod() ** (1 / 252) - 1

            rm_entry.delete(0, tk.END)
            rm_entry.insert(0, str(round(annual_rm * 100, 4)))
        elif start_year.get() or end_year.get() or start_month.get() or end_month.get() or start_day.get() or end_day.get() == '':
            tk.messagebox.showerror("Error", "请输入完整的起始日期！")
    except Exception as e:
        tk.messagebox.showerror("Error", f"获取数据失败: {str(e)}")

def view_data():
    global window_title
    global window_df
    view_window = tk.Toplevel(root)
    view_window.title(str(window_title))
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

def view_stock_data():
    global window_title
    global window_df

    window_df = data.copy()
    window_title = 'View Stock Data'
    view_data()

def view_mkt_data():
    global window_title
    global window_df

    window_df = mktdata.copy()
    window_title = 'View Market Data'
    view_data()

def view_mkt_des():
    mkt_des_view_window = tk.Toplevel(root)
    mkt_des_view_window.title("View Market Describe")
    mkt_des_view_window.geometry("1080x320")

    mkt_data_des_view_frame = tk.Frame(mkt_des_view_window)
    mkt_data_des_view_frame.pack(fill='both', expand=True)
    mkt_data_des_view_table_dis = Table(mkt_data_des_view_frame, showstatusbar=True, showtoolbar=True)
    mkt_data_des_view_table_dis.model.df = mktdata.describe()
    mkt_data_des_view_table_dis.show()
    mkt_data_des_view_table_dis.font = ('Arial', 12)
    mkt_data_des_view_table_dis.redraw()
    mkt_data_des_view_table_dis.zoomOut()
    mkt_data_des_view_table_dis.zoomIn()

    mkt_des_view_window.wait_window()

def fin_report():
    global fin_report_al
    global stock_code
    global window_title
    global window_df

    try:
        if fin_report_al.empty:
            fin_report_al = ak.stock_financial_report_sina(stock_code,'资产负债表')
        window_df = fin_report_al.copy()
        window_title = 'View Financial Report'
        view_data()
    except Exception as e:
        tk.messagebox.showerror("Error", f"获取数据失败: {str(e)}")

def fin_benefit():
    global fin_report_be
    global stock_code
    global window_title
    global window_df

    try:
        if fin_report_be.empty:
            fin_report_be = ak.stock_financial_report_sina(stock_code, '利润表')
        window_df = fin_report_be.copy()
        window_title = 'View Financial Report'
        view_data()
    except Exception as e:
        tk.messagebox.showerror("Error", f"获取数据失败: {str(e)}")

def fin_cash_flow():
    global fin_report_xjll
    global stock_code
    global window_title
    global window_df

    try:
        if fin_report_xjll.empty:
            fin_report_xjll = ak.stock_financial_report_sina(stock_code, '现金流量表')
        window_df = fin_report_xjll.copy()
        window_title = 'View Financial Report'
        view_data()
    except Exception as e:
        tk.messagebox.showerror("Error", f"获取数据失败: {str(e)}")

def get_rf():
    global rf_data
    global start_date
    global end_date
    global rf_des_df
    try:
        if rf_data.empty:
            start_m = '{:02d}'.format(int(start_month.get()))
            end_m = '{:02d}'.format(int(end_month.get()))
            start_d = '{:02d}'.format(int(start_day.get()))
            end_d = '{:02d}'.format(int(end_day.get()))
            start_date = str(str(start_year.get()) + str(start_m) + str(start_d))
            end_date = str(str(end_year.get()) + str(end_m) + str(end_d))
            rf_data = ak.bond_china_yield(start_date=start_date,end_date=end_date)
            rf_des_df = rf_data[rf_data['曲线名称'] == '中债国债收益率曲线'].describe()

        view_window = tk.Toplevel(root)
        view_window.title("China Bond Yield")
        view_window.geometry("1350x800")

        data_view_frame = tk.Frame(view_window)
        data_view_frame.pack(side='top', fill='both', expand=True)
        rf_data_table = Table(data_view_frame, showstatusbar=True, showtoolbar=True)
        rf_data_table.model.df = rf_data[rf_data['曲线名称'] == '中债国债收益率曲线']
        rf_data_table.cellbackgr = '#373737'
        rf_data_table.rowselectedcolor = '#707070'
        rf_data_table.rowheaderbgcolor = '#707070'
        rf_data_table.textcolor = '#ececec'
        rf_data_table.font = ('Arial', 12)
        rf_data_table.show()
        rf_data_table.zoomOut()
        rf_data_table.zoomIn()

        describe_view_frame = tk.Frame(view_window)
        describe_view_frame.pack(side='top',fill='both', expand=True)
        rf_des_df_table = Table(describe_view_frame, showstatusbar=True, showtoolbar=True)
        rf_des_df_table.model.df = rf_des_df
        rf_des_df_table.cellbackgr = '#373737'
        rf_des_df_table.rowselectedcolor = '#707070'
        rf_des_df_table.rowheaderbgcolor = '#707070'
        rf_des_df_table.textcolor = '#ececec'
        rf_des_df_table.font = ('Arial', 12)
        rf_des_df_table.show()
        rf_des_df_table.zoomOut()
        rf_des_df_table.zoomIn()

        view_window.wait_window()

    except Exception as e:
        tk.messagebox.showerror("Error", f"获取数据失败: {str(e)}")

def institution_recommend():
    global institute_recommend_df
    global window_df
    global window_title
    try:
        if institute_recommend_df.empty:
            institute_recommend_df = ak.stock_institute_recommend(symbol="目标涨幅排名")
        window_df = institute_recommend_df.copy()
        window_title = 'Institution Recommend'
        view_data()

    except Exception as e:
        tk.messagebox.showerror("Error", f"获取数据失败: {str(e)}")

def institution_evaluation():
    global institution_evaluation_df
    global window_df
    global window_title
    try:
        if institution_evaluation_df.empty:
            institution_evaluation_df = ak.stock_rank_forecast_cninfo(date=str(datetime.date.today()).replace("-",""))
        window_df = institution_evaluation_df.copy()
        window_title = 'Institution Evaluation'
        view_data()
    except Exception as e:
        tk.messagebox.showerror("Error", f"获取数据失败: {str(e)}")

def industry_info():
    global industry_info_df
    global window_df
    global window_title
    try:
        if industry_info_df.empty:
            industry_info_df = ak.stock_board_industry_name_em()
        window_df = industry_info_df.copy()
        window_title = 'Industry Info'
        view_data()
    except Exception as e:
        tk.messagebox.showerror("Error", f"获取数据失败: {str(e)}")

def industry_search():
    global industry_search_df
    global industry_name
    global window_df
    global window_title
    try:
        if industry_label_e.get() != "":
            industry_name = industry_label_e.get()
            if industry_search_df.empty:
                industry_search_df = ak.stock_board_industry_cons_em(symbol=industry_name).drop('序号', axis=1)
            window_df = industry_search_df.copy()
            window_title = f"Industry Info({str(industry_name)})"
            view_data()

            industry_label_e.delete(0, tk.END)
            industry_label_e.insert(0, industry_name)
        else:
            tk.messagebox.showerror("Error", "请输入行业名称！")
    except Exception as e:
        tk.messagebox.showerror("Error", f"获取数据失败: {str(e)}")

def valuation_data():
    global stock_valuation_df
    global stock_code
    global window_df
    global window_title
    try:
        if stock_valuation_df.empty:
            stock_valuation_df = ak.stock_value_em(symbol=stock_code)
        window_df = stock_valuation_df.copy()
        window_title = 'Stock Valuation'
        view_data()

    except Exception as e:
        tk.messagebox.showerror("Error", f"获取数据失败: {str(e)}")

def dividend():
    global dividend_df
    global stock_code
    global window_df
    global window_title
    try:
        if dividend_df.empty:
            dividend_df = ak.stock_history_dividend_detail(symbol=stock_code, indicator="分红")
        window_df = dividend_df.copy()
        window_title = 'Dividend Data'
        view_data()

        bt_df_list.append('dividend_df')

    except Exception as e:
        tk.messagebox.showerror("Error", f"获取数据失败: {str(e)}")

def cap_structure():
    global cap_structure_df
    global stock_code
    global window_df
    global window_title
    try:
        if cap_structure_df.empty:
            if str(stock_code)[0] == '6':
                symbol = str(str(stock_code) + '.SH')
            elif str(stock_code)[0] == '0':
                    symbol = str(str(stock_code) + '.SZ')
            cap_structure_df = ak.stock_zh_a_gbjg_em(symbol=symbol)
        window_df = cap_structure_df.copy()
        window_title = 'Dividend Data'
        view_data()

        bt_df_list.append('cap_structure_df')

    except Exception as e:
        tk.messagebox.showerror("Error", f"获取数据失败: {str(e)}")

def individual_report():
    global individual_report_df
    global stock_code
    global window_df
    global window_title
    try:
        if individual_report_df.empty:
            individual_report_df = ak.stock_research_report_em(symbol=stock_code)
        window_df = individual_report_df.copy()
        window_title = 'Individual Report'
        view_data()

    except Exception as e:
        tk.messagebox.showerror("Error", f"获取数据失败: {str(e)}")

def inday_data():
    global inday_df
    global stock_code
    global bid_ask_df
    global end_date

    try:
        bid_ask_df = ak.stock_bid_ask_em(symbol=stock_code)
        inday_df = ak.stock_intraday_em(symbol=stock_code)
        inday_df['时间'] = str(datetime.date.today()) + ' ' + inday_df['时间']
        inday_df['时间'] = pd.to_datetime(inday_df['时间'], format='%Y-%m-%d %H:%M:%S')

        def veiw_intraday():
            global inday_df
            global window_df
            global window_title

            window_df = inday_df.copy()
            window_title = 'Intraday Data'
            view_data()

        def intraday_update_info():
            global intraday_price
            global intraday_price_show
            global intraday_range
            global intraday_range_show
            global intraday_time
            if inday_df['成交价'].iloc[-1] >= bid_ask_df['value'].iloc[-5]:
                color = up
            else:
                color = down
            intraday_up_down_label.configure(bg=color)
            intraday_price = inday_df['成交价'].iloc[-1]
            intraday_price_show = '{:.2f}'.format(intraday_price)
            intraday_price_show_label.configure(text=str(intraday_price_show))
            intraday_range = bid_ask_df['value'].iloc[22]
            intraday_time = inday_df['时间'].iloc[-1]
            intraday_time_label.configure(text=str(intraday_time))

            if color == up:
                intraday_range_show = str('+' + '{:.2f}'.format(intraday_range) + '%')
            else:
                intraday_range_show = str('{:.2f}'.format(intraday_range) + '%')
            intraday_flu_range_label.configure(fg=color, text=str(intraday_range_show))

        def intraday_plot():
            intraday_ax.clear()

            # 鼠标拖动 处理事件
            startx = 0
            starty = 0
            mPress = False
            def call_back(event):
                axtemp = event.inaxes
                base_scale = 1.5
                x_min, x_max = axtemp.get_xlim()  ##获取x轴范围
                y_min, y_max = axtemp.get_ylim()  ##获取y轴范围
                fanwei_x = (x_max - x_min) / 2  # 范围缩放
                fanwei_y = (y_max - y_min) / 2
                xdata = event.xdata  # get event x location
                ydata = event.ydata  # get event y location
                if event.button == 'up':
                    # deal with zoom in
                    scale_factor = 1 / base_scale
                elif event.button == 'down':
                    # deal with zoom out
                    scale_factor = base_scale
                else:
                    # deal with something that should never happen
                    scale_factor = 1

                axtemp.set(xlim=(xdata - fanwei_x * scale_factor, xdata + fanwei_x * scale_factor))
                # axtemp.set(ylim=(ydata - fanwei_y * scale_factor, ydata + fanwei_y * scale_factor))
                intraday_figure.canvas.draw_idle()  # 绘图动作实时反映在图像上

            def call_move(event):
                # print(event.name)
                global mPress
                global startx
                global starty
                mouse_x = event.x
                mouse_y = event.y
                axtemp = event.inaxes
                if event.name == 'button_press_event':
                    if axtemp and event.button == 1:
                        if axtemp.get_legend():
                            legend_bbox = axtemp.get_legend().get_window_extent()
                            left_bottom = legend_bbox.get_points()[0]
                            right_top = legend_bbox.get_points()[1]

                            if left_bottom[0] <= mouse_x <= right_top[0] and left_bottom[1] <= mouse_y <= right_top[1]:
                                # print("在图例上按下鼠标")
                                # 在图例上按下鼠标
                                mPress = False
                                return
                        # 没有图例的情况
                        # print("在 Axes 上按下鼠标")
                        # 在 Axes 上按下鼠标
                        mPress = True
                        startx = event.xdata
                        starty = event.ydata
                        return
                elif event.name == 'button_release_event':
                    if axtemp and event.button == 1:
                        mPress = False
                elif event.name == 'motion_notify_event':
                    if axtemp and event.button == 1 and mPress:
                        if axtemp.get_legend():
                            legend_bbox = axtemp.get_legend().get_window_extent()
                            left_bottom = legend_bbox.get_points()[0]
                            right_top = legend_bbox.get_points()[1]

                            if left_bottom[0] <= mouse_x <= right_top[0] and left_bottom[1] <= mouse_y <= right_top[1]:
                                print("在图例上移动鼠标")
                                # 在图例上按下鼠标
                                mPress = False
                                return

                        # 没有图例的情况
                        # print("在Axes上移动鼠标")
                        x_min, x_max = axtemp.get_xlim()
                        y_min, y_max = axtemp.get_ylim()
                        w = x_max - x_min
                        h = y_max - y_min
                        # print(event)
                        # 移动
                        mx = event.xdata - startx
                        my = event.ydata - starty
                        # 注意这里， -mx,  因为下一次 motion事件的坐标，已经是在本次做了移动之后的坐标系了，所以要体现出来
                        # startx=event.xdata-mx  startx=event.xdata-(event.xdata-startx)=startx, 没必要再赋值了
                        # starty=event.ydata-my
                        # print(mx,my,x_min,y_min,w,h)
                        left = x_min - mx
                        right = x_min - mx + w

                        axtemp.set(xlim=(left, right))

                        # axtemp.set(ylim=(y_min - my, y_min - my + h))
                        intraday_figure.canvas.draw_idle()  # 绘图动作实时反映在图像上

                return

            intraday_figure.canvas.mpl_connect('scroll_event', call_back)
            intraday_figure.canvas.mpl_connect('button_press_event', call_move)
            intraday_figure.canvas.mpl_connect('button_release_event', call_move)
            intraday_figure.canvas.mpl_connect('motion_notify_event', call_move)

            if inday_df['成交价'].iloc[-1] >= bid_ask_df['value'].iloc[-5]:
                color = up
            else:
                color = down
            intraday_ax.plot(inday_df['时间'], inday_df['成交价'], color=color, linewidth=0.9)
            intraday_ax.grid(True)
            intraday_ax.patch.set_facecolor('#c9c9c9')
            intraday_ax.tick_params(axis='x', labelrotation=45)
            intraday_ax.axhline(bid_ask_df['value'].iloc[-5], color='#353535', linestyle='--', linewidth=0.8)
            intraday_canvas_draw.draw()

        def update_intraday():
            global inday_df
            global bid_ask_df
            global stock_code

            bid_ask_df = ak.stock_bid_ask_em(symbol=stock_code)
            inday_df = ak.stock_intraday_em(symbol=stock_code)
            inday_df['时间'] = str(datetime.date.today()) + ' ' + inday_df['时间']
            inday_df['时间'] = pd.to_datetime(inday_df['时间'], format='%Y-%m-%d %H:%M:%S')

            data_view_table_dis.model.df = bid_ask_df
            data_view_table_dis.show()
            intraday_update_info()
            intraday_plot()

        # def auto_update():
        #     global auto_update_value
        #     if auto_update_value == 0:
        #         auto_update_value = 1
        #     elif auto_update_value == 1:
        #         auto_update_value = 0
        #     while auto_update_value == 1:
        #         update_intraday()
        #         sleep(10)

        intraday_window = tk.Toplevel(root)
        intraday_window.title('Intraday Data')
        intraday_window.geometry("1168x860")

        data_view_frame = tk.Frame(intraday_window)
        data_view_frame.pack(side='left', fill='y', padx=(10, 0), pady=10)
        data_view_table_dis = Table(data_view_frame, showstatusbar=True, width=300)
        data_view_table_dis.model.df = bid_ask_df
        data_view_table_dis.cellbackgr = '#373737'
        data_view_table_dis.rowselectedcolor = '#707070'
        data_view_table_dis.rowheaderbgcolor = '#707070'
        data_view_table_dis.textcolor = '#ececec'
        data_view_table_dis.font = ('Arial', 12)
        data_view_table_dis.setRowColors(rows=8, clr=down, cols='all')
        data_view_table_dis.setRowColors(rows=10, clr=up, cols='all')
        data_view_table_dis.show()
        data_view_table_dis.zoomOut()
        data_view_table_dis.zoomIn()

        r_frame = tk.Frame(intraday_window)
        r_frame.pack(side='left', fill='y', padx=10, pady=10)
        display_frame = tk.Frame(r_frame)
        display_frame.pack(side='top', fill='x', pady=5)
        intraday_up_down_label = tk.Label(display_frame, text=' ', font=("微软雅黑", 2), width=1, height=12)
        intraday_up_down_label.grid(row=0, column=0, padx=(50, 0), rowspan=2)
        intraday_up_down_label.configure(bg='#ababab')
        intraday_price_show_label = tk.Label(display_frame, text=str(intraday_price_show), font=("微软雅黑", 27, 'bold'), width=7)
        intraday_price_show_label.grid(row=0, column=1, rowspan=2)
        intraday_price_show_label.config(fg='#ececec')
        intraday_flu_range_label = tk.Label(display_frame, text=str(intraday_range_show), font=("微软雅黑", 10, 'bold'))
        intraday_flu_range_label.grid(row=0, column=2)
        intraday_time_label = tk.Label(display_frame, text=str(intraday_time), font=("微软雅黑", 10, 'bold'), width=21)
        intraday_time_label.grid(row=1, column=2, padx=(1, 1))
        ttk.Button(display_frame, text='查看数据', style="outline", command=veiw_intraday, cursor='hand2').grid(row=0, column=4, padx=(174,1))
        # ttk.Checkbutton(display_frame, text='自动刷新', bootstyle="round-toggle",
        #                 cursor='hand2', command=auto_update).grid(row=1, column=3, padx=(29, 4), pady=2)
        ttk.Button(display_frame, text='刷新数据', style="outline", command=update_intraday, cursor='hand2').grid(row=1, column=4, padx=(174,1), pady=2)

        draw_frame = tk.Frame(r_frame)
        draw_frame.pack(side='top', fill='x', pady=5)
        canvas_lbframe = ttk.Labelframe(draw_frame, text='canvas') #, height=587, width=760
        canvas_lbframe.pack(side='top')
        intraday_canvas = tk.Canvas(canvas_lbframe)
        intraday_canvas.pack()
        intraday_canvas.pack_propagate(False)
        intraday_figure = plt.Figure(figsize=(6, 5.6))
        intraday_figure.subplots_adjust(left=0.12, right=0.98, bottom=0.12, top=0.97)
        intraday_ax = intraday_figure.subplots()
        intraday_canvas_draw = FigureCanvasTkAgg(intraday_figure, intraday_canvas)
        intraday_canvas_draw.get_tk_widget().grid(row=0, column=0, padx=7, pady=(0,7))
        intraday_figure.patch.set_facecolor('#888888')
        intraday_ax.patch.set_facecolor('#c9c9c9')
        intraday_plot()
        intraday_update_info()

        intraday_window.wait_window()

    except Exception as e:
        tk.messagebox.showerror("Error", f"获取数据失败: {str(e)}")

def back_testing():
    try:
        global bt_df_list
        global data_for_bt
        global variables
        plt.rcParams["font.sans-serif"] = ["Microsoft YaHei"]  # 设置字体
        plt.rcParams["axes.unicode_minus"] = False  # 该语句解决图像中的“-”负号的乱码问题

        variables = data_for_bt.columns.values.tolist()
        bt_window = tk.Toplevel(root)
        bt_window.title('Back Testing')
        bt_window.geometry("1162x913")

        def update_listbox():
            global variables
            v_listbox.delete(0, tk.END)
            for column_names in variables:
                v_listbox.insert(tk.END, column_names)
            v_listbox.selection_set(3, None)
            for cb in [buy_con_a_c, buy_con_d_c, sell_con_a_c, sell_con_d_c]:
                cb.config(values=variables)

        def show_table_without_event():
            display_table.model.df = eval(bt_df_choose_c.get())
            describe_table.model.df = display_table.model.df.describe()
            display_table.show()
            describe_table.show()

        def show_table(event):
            show_table_without_event()

        def bt_plot_without_event():
            global bt_df_list
            global data_for_bt

            plot_list = []
            bt_ax.clear()

            for variable in v_listbox.curselection():
                plot_list.append(v_listbox.get(variable))
            for v in plot_list:
                bt_ax.plot(data_for_bt['日期'], data_for_bt[v], label=v)

            bt_ax.patch.set_facecolor('#c9c9c9')
            bt_ax.tick_params(axis='x', labelrotation=45)
            bt_ax.legend()
            bt_canvas_draw.draw()

        def bt_plot(event):
            bt_plot_without_event()

        def save_figure():
            sf_window = tk.Toplevel(root)
            sf_window.title('Save Figure')
            sf_window.geometry("500x90")

            def sf_select_save_path():
                v_path_s = tkinter.filedialog.asksaveasfilename(
                    filetypes=[("png图像", "*.png"), ("jpg图像", "*.jpg"), ("pdf文件", "*.pdf")], defaultextension='.png')
                v_path_s = v_path_s.replace("/", "\\\\")
                sf_path.set(v_path_s)
                sf_b.config(state="normal")

            def sf_save_file():
                bt_figure.savefig('{}'.format(str(sf_path_e.get())), dpi=720)
                tk.messagebox.showinfo(message="保存成功！", title="Info")
                sf_window.destroy()

            tk.Label(sf_window, text='保存路径:', font=("微软雅黑", 10)).grid(row=0, column=0, padx=(10,0), pady=(15,3), sticky=tk.W)
            sf_path_e = ttk.Entry(sf_window, width=29, font=("微软雅黑", 10), textvariable=sf_path)
            sf_path_e.grid(row=1, column=0, padx=(10,2))
            ttk.Button(sf_window, text='选择路径', style='outline', cursor='hand2', command=sf_select_save_path).grid(row=1, column=1, padx=2)
            sf_b = ttk.Button(sf_window, text='保存图像', style='outline', cursor='hand2', state='disabled', command=sf_save_file)
            sf_b.grid(row=1, column=2, padx=2)

        def create_new_variable():
            global data_for_bt
            global variables
            name = new_variable_name_e.get()
            value = new_variable_value_e.get()
            if name not in variables:
                data_for_bt[name] = eval(value)
                variables = data_for_bt.columns.values.tolist()
                show_table_without_event()
                update_listbox()
            else:
                tk.messagebox.showerror("Error", "创建变量失败：变量名重复！")

        def clear_conditions():
            con_list_c = [buy_con_a_c, buy_con_b_c, buy_con_c_c, buy_con_d_c,
                        sell_con_a_c, sell_con_b_c, sell_con_c_c,sell_con_d_c]
            for con in con_list_c:
                con.set('')
            buy_con_d_e.delete(0, tk.END)
            sell_con_d_e.delete(0, tk.END)

        def clear_buy_c(event):
            buy_con_d_c.set('')

        def clear_buy_e(event):
            buy_con_d_e.delete(0, tk.END)

        def clear_sell_c(event):
            sell_con_d_c.set('')

        def clear_sell_e(event):
            sell_con_d_e.delete(0, tk.END)

        def clear_canvas():
            v_listbox.config(state="normal")
            apply_bt_b.config(state="normal")
            outcome_text.config(state="normal")
            outcome_text.delete(1.0, tk.END)
            outcome_text.config(state="disabled")
            bt_ax.clear()
            bt_ax.patch.set_facecolor('#c9c9c9')
            bt_ax.grid(axis='y',alpha=0.8)
            bt_ax.plot(data_for_bt['日期'], data_for_bt['收盘'], label='收盘')
            bt_canvas_draw.draw()

        def apply_strategy():
            try:
                global data_for_bt
                buy_con_number = 0
                sell_con_number = 0

                buy_conlist = [buy_con_a_c, buy_con_b_c, buy_con_c_c, buy_con_d_c, buy_con_d_e]
                sell_conlist = [sell_con_a_c, sell_con_b_c, sell_con_c_c,sell_con_d_c, sell_con_d_e]
                for con in buy_conlist:
                    if con.get() != '':
                        buy_con_number += 1
                for con in sell_conlist:
                    if con.get() != '':
                        sell_con_number += 1

                if buy_con_number == 4 and sell_con_number == 4:
                    buy_sign_list = []
                    sell_sign_list = []
                    # buy signal
                    if buy_con_b_c.get() == '首次':
                        if buy_con_c_c.get() == '>':
                            if buy_con_d_c.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[buy_con_a_c.get()]>data_for_bt[buy_con_d_c.get()], 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i-1] == 0:
                                        buy_sign_list.append(i)
                            elif buy_con_d_e.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[buy_con_a_c.get()]>float(buy_con_d_e.get()), 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i-1] == 0:
                                        buy_sign_list.append(i)
                        elif buy_con_c_c.get() == '>=':
                            if buy_con_d_c.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[buy_con_a_c.get()]>=data_for_bt[buy_con_d_c.get()], 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i-1] == 0:
                                        buy_sign_list.append(i)
                            elif buy_con_d_e.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[buy_con_a_c.get()]>=float(buy_con_d_e.get()), 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i-1] == 0:
                                        buy_sign_list.append(i)
                        elif buy_con_c_c.get() == '<':
                            if buy_con_d_c.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[buy_con_a_c.get()]<data_for_bt[buy_con_d_c.get()], 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i-1] == 0:
                                        buy_sign_list.append(i)
                            elif buy_con_d_e.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[buy_con_a_c.get()]<float(buy_con_d_e.get()), 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i-1] == 0:
                                        buy_sign_list.append(i)
                        elif buy_con_c_c.get() == '<=':
                            if buy_con_d_c.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[buy_con_a_c.get()]<=data_for_bt[buy_con_d_c.get()], 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i-1] == 0:
                                        buy_sign_list.append(i)
                            elif buy_con_d_e.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[buy_con_a_c.get()]<=float(buy_con_d_e.get()), 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i-1] == 0:
                                        buy_sign_list.append(i)
                        elif buy_con_c_c.get() == '=':
                            if buy_con_d_c.get() != '':
                                data_for_bt['sign'] = np.where(
                                    data_for_bt[buy_con_a_c.get()] == data_for_bt[buy_con_d_c.get()], 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i - 1] == 0:
                                        buy_sign_list.append(i)
                            elif buy_con_d_e.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[buy_con_a_c.get()] == float(buy_con_d_e.get()),1,0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i - 1] == 0:
                                        buy_sign_list.append(i)
                        elif buy_con_c_c.get() == '≠':
                            if buy_con_d_c.get() != '':
                                data_for_bt['sign'] = np.where(
                                    data_for_bt[buy_con_a_c.get()] != data_for_bt[buy_con_d_c.get()], 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i - 1] == 0:
                                        buy_sign_list.append(i)
                            elif buy_con_d_e.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[buy_con_a_c.get()] != float(buy_con_d_e.get()),1,0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i - 1] == 0:
                                        buy_sign_list.append(i)

                    elif buy_con_b_c.get() == '连续2天':
                        if buy_con_c_c.get() == '>':
                            if buy_con_d_c.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[buy_con_a_c.get()]>data_for_bt[buy_con_d_c.get()], 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i-1] == 1 and data_for_bt['sign'][i-2] == 0:
                                        buy_sign_list.append(i)
                            elif buy_con_d_e.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[buy_con_a_c.get()]>float(buy_con_d_e.get()), 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i-1] == 1 and data_for_bt['sign'][i-2] == 0:
                                        buy_sign_list.append(i)
                        elif buy_con_c_c.get() == '>=':
                            if buy_con_d_c.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[buy_con_a_c.get()]>=data_for_bt[buy_con_d_c.get()], 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i-1] == 1 and data_for_bt['sign'][i-2] == 0:
                                        buy_sign_list.append(i)
                            elif buy_con_d_e.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[buy_con_a_c.get()]>=float(buy_con_d_e.get()), 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i-1] == 1 and data_for_bt['sign'][i-2] == 0:
                                        buy_sign_list.append(i)
                        elif buy_con_c_c.get() == '<':
                            if buy_con_d_c.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[buy_con_a_c.get()]<data_for_bt[buy_con_d_c.get()], 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i-1] == 1 and data_for_bt['sign'][i-2] == 0:
                                        buy_sign_list.append(i)
                            elif buy_con_d_e.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[buy_con_a_c.get()]<float(buy_con_d_e.get()), 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i-1] == 1 and data_for_bt['sign'][i-2] == 0:
                                        buy_sign_list.append(i)
                        elif buy_con_c_c.get() == '<=':
                            if buy_con_d_c.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[buy_con_a_c.get()]<=data_for_bt[buy_con_d_c.get()], 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i-1] == 1 and data_for_bt['sign'][i-2] == 0:
                                        buy_sign_list.append(i)
                            elif buy_con_d_e.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[buy_con_a_c.get()]<=float(buy_con_d_e.get()), 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i-1] == 1 and data_for_bt['sign'][i-2] == 0:
                                        buy_sign_list.append(i)
                        elif buy_con_c_c.get() == '=':
                            if buy_con_d_c.get() != '':
                                data_for_bt['sign'] = np.where(
                                    data_for_bt[buy_con_a_c.get()] == data_for_bt[buy_con_d_c.get()], 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i-1] == 1 and data_for_bt['sign'][i-2] == 0:
                                        buy_sign_list.append(i)
                            elif buy_con_d_e.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[buy_con_a_c.get()] == float(buy_con_d_e.get()),1,0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i-1] == 1 and data_for_bt['sign'][i-2] == 0:
                                        buy_sign_list.append(i)
                        elif buy_con_c_c.get() == '≠':
                            if buy_con_d_c.get() != '':
                                data_for_bt['sign'] = np.where(
                                    data_for_bt[buy_con_a_c.get()] != data_for_bt[buy_con_d_c.get()], 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i-1] == 1 and data_for_bt['sign'][i-2] == 0:
                                        buy_sign_list.append(i)
                            elif buy_con_d_e.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[buy_con_a_c.get()] != float(buy_con_d_e.get()),1,0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i-1] == 1 and data_for_bt['sign'][i-2] == 0:
                                        buy_sign_list.append(i)

                    elif buy_con_b_c.get() == '连续3天':
                        if buy_con_c_c.get() == '>':
                            if buy_con_d_c.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[buy_con_a_c.get()]>data_for_bt[buy_con_d_c.get()], 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i-1] == 1 and data_for_bt['sign'][i-2] == 1 and data_for_bt['sign'][i-3] == 0:
                                        buy_sign_list.append(i)
                            elif buy_con_d_e.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[buy_con_a_c.get()]>float(buy_con_d_e.get()), 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i-1] == 1 and data_for_bt['sign'][i-2] == 1 and data_for_bt['sign'][i-3] == 0:
                                        buy_sign_list.append(i)
                        elif buy_con_c_c.get() == '>=':
                            if buy_con_d_c.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[buy_con_a_c.get()]>=data_for_bt[buy_con_d_c.get()], 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i-1] == 1 and data_for_bt['sign'][i-2] == 1 and data_for_bt['sign'][i-3] == 0:
                                        buy_sign_list.append(i)
                            elif buy_con_d_e.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[buy_con_a_c.get()]>=float(buy_con_d_e.get()), 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i-1] == 1 and data_for_bt['sign'][i-2] == 1 and data_for_bt['sign'][i-3] == 0:
                                        buy_sign_list.append(i)
                        elif buy_con_c_c.get() == '<':
                            if buy_con_d_c.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[buy_con_a_c.get()]<data_for_bt[buy_con_d_c.get()], 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i-1] == 1 and data_for_bt['sign'][i-2] == 1 and data_for_bt['sign'][i-3] == 0:
                                        buy_sign_list.append(i)
                            elif buy_con_d_e.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[buy_con_a_c.get()]<float(buy_con_d_e.get()), 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i-1] == 1 and data_for_bt['sign'][i-2] == 1 and data_for_bt['sign'][i-3] == 0:
                                        buy_sign_list.append(i)
                        elif buy_con_c_c.get() == '<=':
                            if buy_con_d_c.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[buy_con_a_c.get()]<=data_for_bt[buy_con_d_c.get()], 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i-1] == 1 and data_for_bt['sign'][i-2] == 1 and data_for_bt['sign'][i-3] == 0:
                                        buy_sign_list.append(i)
                            elif buy_con_d_e.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[buy_con_a_c.get()]<=float(buy_con_d_e.get()), 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i-1] == 1 and data_for_bt['sign'][i-2] == 1 and data_for_bt['sign'][i-3] == 0:
                                        buy_sign_list.append(i)
                        elif buy_con_c_c.get() == '=':
                            if buy_con_d_c.get() != '':
                                data_for_bt['sign'] = np.where(
                                    data_for_bt[buy_con_a_c.get()] == data_for_bt[buy_con_d_c.get()], 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i-1] == 1 and data_for_bt['sign'][i-2] == 1 and data_for_bt['sign'][i-3] == 0:
                                        buy_sign_list.append(i)
                            elif buy_con_d_e.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[buy_con_a_c.get()] == float(buy_con_d_e.get()),1,0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i-1] == 1 and data_for_bt['sign'][i-2] == 1 and data_for_bt['sign'][i-3] == 0:
                                        buy_sign_list.append(i)
                        elif buy_con_c_c.get() == '≠':
                            if buy_con_d_c.get() != '':
                                data_for_bt['sign'] = np.where(
                                    data_for_bt[buy_con_a_c.get()] != data_for_bt[buy_con_d_c.get()], 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i-1] == 1 and data_for_bt['sign'][i-2] == 1 and data_for_bt['sign'][i-3] == 0:
                                        buy_sign_list.append(i)
                            elif buy_con_d_e.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[buy_con_a_c.get()] != float(buy_con_d_e.get()),1,0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i-1] == 1 and data_for_bt['sign'][i-2] == 1 and data_for_bt['sign'][i-3] == 0:
                                        buy_sign_list.append(i)

                    elif buy_con_b_c.get() == '连续5天':
                        if buy_con_c_c.get() == '>':
                            if buy_con_d_c.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[buy_con_a_c.get()]>data_for_bt[buy_con_d_c.get()], 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i-1] == 1 and data_for_bt['sign'][i-2] == 1 and data_for_bt['sign'][i-3] == 1 and data_for_bt['sign'][i-4] == 1 and data_for_bt['sign'][i-5] == 0:
                                        buy_sign_list.append(i)
                            elif buy_con_d_e.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[buy_con_a_c.get()]>float(buy_con_d_e.get()), 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i-1] == 1 and data_for_bt['sign'][i-2] == 1 and data_for_bt['sign'][i-3] == 1 and data_for_bt['sign'][i-4] == 1 and data_for_bt['sign'][i-5] == 0:
                                        buy_sign_list.append(i)
                        elif buy_con_c_c.get() == '>=':
                            if buy_con_d_c.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[buy_con_a_c.get()]>=data_for_bt[buy_con_d_c.get()], 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i-1] == 1 and data_for_bt['sign'][i-2] == 1 and data_for_bt['sign'][i-3] == 1 and data_for_bt['sign'][i-4] == 1 and data_for_bt['sign'][i-5] == 0:
                                        buy_sign_list.append(i)
                            elif buy_con_d_e.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[buy_con_a_c.get()]>=float(buy_con_d_e.get()), 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i-1] == 1 and data_for_bt['sign'][i-2] == 1 and data_for_bt['sign'][i-3] == 1 and data_for_bt['sign'][i-4] == 1 and data_for_bt['sign'][i-5] == 0:
                                        buy_sign_list.append(i)
                        elif buy_con_c_c.get() == '<':
                            if buy_con_d_c.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[buy_con_a_c.get()]<data_for_bt[buy_con_d_c.get()], 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i-1] == 1 and data_for_bt['sign'][i-2] == 1 and data_for_bt['sign'][i-3] == 1 and data_for_bt['sign'][i-4] == 1 and data_for_bt['sign'][i-5] == 0:
                                        buy_sign_list.append(i)
                            elif buy_con_d_e.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[buy_con_a_c.get()]<float(buy_con_d_e.get()), 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i-1] == 1 and data_for_bt['sign'][i-2] == 1 and data_for_bt['sign'][i-3] == 1 and data_for_bt['sign'][i-4] == 1 and data_for_bt['sign'][i-5] == 0:
                                        buy_sign_list.append(i)
                        elif buy_con_c_c.get() == '<=':
                            if buy_con_d_c.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[buy_con_a_c.get()]<=data_for_bt[buy_con_d_c.get()], 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i-1] == 1 and data_for_bt['sign'][i-2] == 1 and data_for_bt['sign'][i-3] == 1 and data_for_bt['sign'][i-4] == 1 and data_for_bt['sign'][i-5] == 0:
                                        buy_sign_list.append(i)
                            elif buy_con_d_e.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[buy_con_a_c.get()]<=float(buy_con_d_e.get()), 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i-1] == 1 and data_for_bt['sign'][i-2] == 1 and data_for_bt['sign'][i-3] == 1 and data_for_bt['sign'][i-4] == 1 and data_for_bt['sign'][i-5] == 0:
                                        buy_sign_list.append(i)
                        elif buy_con_c_c.get() == '=':
                            if buy_con_d_c.get() != '':
                                data_for_bt['sign'] = np.where(
                                    data_for_bt[buy_con_a_c.get()] == data_for_bt[buy_con_d_c.get()], 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i-1] == 1 and data_for_bt['sign'][i-2] == 1 and data_for_bt['sign'][i-3] == 1 and data_for_bt['sign'][i-4] == 1 and data_for_bt['sign'][i-5] == 0:
                                        buy_sign_list.append(i)
                            elif buy_con_d_e.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[buy_con_a_c.get()] == float(buy_con_d_e.get()),1,0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i-1] == 1 and data_for_bt['sign'][i-2] == 1 and data_for_bt['sign'][i-3] == 1 and data_for_bt['sign'][i-4] == 1 and data_for_bt['sign'][i-5] == 0:
                                        buy_sign_list.append(i)
                        elif buy_con_c_c.get() == '≠':
                            if buy_con_d_c.get() != '':
                                data_for_bt['sign'] = np.where(
                                    data_for_bt[buy_con_a_c.get()] != data_for_bt[buy_con_d_c.get()], 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i-1] == 1 and data_for_bt['sign'][i-2] == 1 and data_for_bt['sign'][i-3] == 1 and data_for_bt['sign'][i-4] == 1 and data_for_bt['sign'][i-5] == 0:
                                        buy_sign_list.append(i)
                            elif buy_con_d_e.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[buy_con_a_c.get()] != float(buy_con_d_e.get()),1,0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i-1] == 1 and data_for_bt['sign'][i-2] == 1 and data_for_bt['sign'][i-3] == 1 and data_for_bt['sign'][i-4] == 1 and data_for_bt['sign'][i-5] == 0:
                                        buy_sign_list.append(i)

                    data_for_bt = data_for_bt.drop('sign', axis=1)

                    # sell signal
                    if sell_con_b_c.get() == '首次':
                        if sell_con_c_c.get() == '>':
                            if sell_con_d_c.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[sell_con_a_c.get()]>data_for_bt[sell_con_d_c.get()], 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i-1] == 0:
                                        sell_sign_list.append(i)
                            elif sell_con_d_e.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[sell_con_a_c.get()]>float(sell_con_d_e.get()), 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i-1] == 0:
                                        sell_sign_list.append(i)
                        elif sell_con_c_c.get() == '>=':
                            if sell_con_d_c.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[sell_con_a_c.get()]>=data_for_bt[sell_con_d_c.get()], 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i-1] == 0:
                                        sell_sign_list.append(i)
                            elif sell_con_d_e.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[sell_con_a_c.get()]>=float(sell_con_d_e.get()), 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i-1] == 0:
                                        sell_sign_list.append(i)
                        elif sell_con_c_c.get() == '<':
                            if sell_con_d_c.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[sell_con_a_c.get()]<data_for_bt[sell_con_d_c.get()], 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i-1] == 0:
                                        sell_sign_list.append(i)
                            elif sell_con_d_e.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[sell_con_a_c.get()]<float(sell_con_d_e.get()), 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i-1] == 0:
                                        sell_sign_list.append(i)
                        elif sell_con_c_c.get() == '<=':
                            if sell_con_d_c.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[sell_con_a_c.get()]<=data_for_bt[sell_con_d_c.get()], 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i-1] == 0:
                                        sell_sign_list.append(i)
                            elif sell_con_d_e.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[sell_con_a_c.get()]<=float(sell_con_d_e.get()), 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i-1] == 0:
                                        sell_sign_list.append(i)
                        elif sell_con_c_c.get() == '=':
                            if sell_con_d_c.get() != '':
                                data_for_bt['sign'] = np.where(
                                    data_for_bt[sell_con_a_c.get()] == data_for_bt[sell_con_d_c.get()], 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i - 1] == 0:
                                        sell_sign_list.append(i)
                            elif sell_con_d_e.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[sell_con_a_c.get()] == float(sell_con_d_e.get()),1,0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i - 1] == 0:
                                        sell_sign_list.append(i)
                        elif sell_con_c_c.get() == '≠':
                            if sell_con_d_c.get() != '':
                                data_for_bt['sign'] = np.where(
                                    data_for_bt[sell_con_a_c.get()] != data_for_bt[sell_con_d_c.get()], 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i - 1] == 0:
                                        sell_sign_list.append(i)
                            elif sell_con_d_e.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[sell_con_a_c.get()] != float(sell_con_d_e.get()),1,0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i - 1] == 0:
                                        sell_sign_list.append(i)

                    elif sell_con_b_c.get() == '连续2天':
                        if sell_con_c_c.get() == '>':
                            if sell_con_d_c.get() != '':
                                data_for_bt['sign'] = np.where(
                                    data_for_bt[sell_con_a_c.get()] > data_for_bt[sell_con_d_c.get()], 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i - 1] == 1 and data_for_bt['sign'][i - 2] == 0:
                                        sell_sign_list.append(i)
                            elif sell_con_d_e.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[sell_con_a_c.get()] > float(sell_con_d_e.get()), 1,
                                                               0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i - 1] == 1 and data_for_bt['sign'][i - 2] == 0:
                                        sell_sign_list.append(i)
                        elif sell_con_c_c.get() == '>=':
                            if sell_con_d_c.get() != '':
                                data_for_bt['sign'] = np.where(
                                    data_for_bt[sell_con_a_c.get()] >= data_for_bt[sell_con_d_c.get()], 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i - 1] == 1 and data_for_bt['sign'][i - 2] == 0:
                                        sell_sign_list.append(i)
                            elif sell_con_d_e.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[sell_con_a_c.get()] >= float(sell_con_d_e.get()), 1,
                                                               0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i - 1] == 1 and data_for_bt['sign'][i - 2] == 0:
                                        sell_sign_list.append(i)
                        elif sell_con_c_c.get() == '<':
                            if sell_con_d_c.get() != '':
                                data_for_bt['sign'] = np.where(
                                    data_for_bt[sell_con_a_c.get()] < data_for_bt[sell_con_d_c.get()], 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i - 1] == 1 and data_for_bt['sign'][i - 2] == 0:
                                        sell_sign_list.append(i)
                            elif sell_con_d_e.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[sell_con_a_c.get()] < float(sell_con_d_e.get()), 1,
                                                               0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i - 1] == 1 and data_for_bt['sign'][i - 2] == 0:
                                        sell_sign_list.append(i)
                        elif sell_con_c_c.get() == '<=':
                            if sell_con_d_c.get() != '':
                                data_for_bt['sign'] = np.where(
                                    data_for_bt[sell_con_a_c.get()] <= data_for_bt[sell_con_d_c.get()], 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i - 1] == 1 and data_for_bt['sign'][i - 2] == 0:
                                        sell_sign_list.append(i)
                            elif sell_con_d_e.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[sell_con_a_c.get()] <= float(sell_con_d_e.get()), 1,
                                                               0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i - 1] == 1 and data_for_bt['sign'][i - 2] == 0:
                                        sell_sign_list.append(i)
                        elif sell_con_c_c.get() == '=':
                            if sell_con_d_c.get() != '':
                                data_for_bt['sign'] = np.where(
                                    data_for_bt[sell_con_a_c.get()] == data_for_bt[sell_con_d_c.get()], 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i - 1] == 1 and data_for_bt['sign'][i - 2] == 0:
                                        sell_sign_list.append(i)
                            elif sell_con_d_e.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[sell_con_a_c.get()] == float(sell_con_d_e.get()), 1,
                                                               0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i - 1] == 1 and data_for_bt['sign'][i - 2] == 0:
                                        sell_sign_list.append(i)
                        elif sell_con_c_c.get() == '≠':
                            if sell_con_d_c.get() != '':
                                data_for_bt['sign'] = np.where(
                                    data_for_bt[sell_con_a_c.get()] != data_for_bt[sell_con_d_c.get()], 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i - 1] == 1 and data_for_bt['sign'][i - 2] == 0:
                                        sell_sign_list.append(i)
                            elif sell_con_d_e.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[sell_con_a_c.get()] != float(sell_con_d_e.get()), 1,
                                                               0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i - 1] == 1 and data_for_bt['sign'][i - 2] == 0:
                                        sell_sign_list.append(i)

                    elif sell_con_b_c.get() == '连续3天':
                        if sell_con_c_c.get() == '>':
                            if sell_con_d_c.get() != '':
                                data_for_bt['sign'] = np.where(
                                    data_for_bt[sell_con_a_c.get()] > data_for_bt[sell_con_d_c.get()], 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i - 1] == 1 and data_for_bt['sign'][i - 2] == 1 and data_for_bt['sign'][i - 3] == 0:
                                        sell_sign_list.append(i)
                            elif sell_con_d_e.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[sell_con_a_c.get()] > float(sell_con_d_e.get()), 1,
                                                               0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i - 1] == 1 and data_for_bt['sign'][i - 2] == 1 and data_for_bt['sign'][i - 3] == 0:
                                        sell_sign_list.append(i)
                        elif sell_con_c_c.get() == '>=':
                            if sell_con_d_c.get() != '':
                                data_for_bt['sign'] = np.where(
                                    data_for_bt[sell_con_a_c.get()] >= data_for_bt[sell_con_d_c.get()], 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i - 1] == 1 and data_for_bt['sign'][i - 2] == 1 and data_for_bt['sign'][i - 3] == 0:
                                        sell_sign_list.append(i)
                            elif sell_con_d_e.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[sell_con_a_c.get()] >= float(sell_con_d_e.get()), 1,
                                                               0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i - 1] == 1 and data_for_bt['sign'][i - 2] == 1 and data_for_bt['sign'][i - 3] == 0:
                                        sell_sign_list.append(i)
                        elif sell_con_c_c.get() == '<':
                            if sell_con_d_c.get() != '':
                                data_for_bt['sign'] = np.where(
                                    data_for_bt[sell_con_a_c.get()] < data_for_bt[sell_con_d_c.get()], 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i - 1] == 1 and data_for_bt['sign'][i - 2] == 1 and data_for_bt['sign'][i - 3] == 0:
                                        sell_sign_list.append(i)
                            elif sell_con_d_e.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[sell_con_a_c.get()] < float(sell_con_d_e.get()), 1,
                                                               0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i - 1] == 1 and data_for_bt['sign'][i - 2] == 1 and data_for_bt['sign'][i - 3] == 0:
                                        sell_sign_list.append(i)
                        elif sell_con_c_c.get() == '<=':
                            if sell_con_d_c.get() != '':
                                data_for_bt['sign'] = np.where(
                                    data_for_bt[sell_con_a_c.get()] <= data_for_bt[sell_con_d_c.get()], 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i - 1] == 1 and data_for_bt['sign'][i - 2] == 1 and data_for_bt['sign'][i - 3] == 0:
                                        sell_sign_list.append(i)
                            elif sell_con_d_e.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[sell_con_a_c.get()] <= float(sell_con_d_e.get()), 1,
                                                               0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i - 1] == 1 and data_for_bt['sign'][i - 2] == 1 and data_for_bt['sign'][i - 3] == 0:
                                        sell_sign_list.append(i)
                        elif sell_con_c_c.get() == '=':
                            if sell_con_d_c.get() != '':
                                data_for_bt['sign'] = np.where(
                                    data_for_bt[sell_con_a_c.get()] == data_for_bt[sell_con_d_c.get()], 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i - 1] == 1 and data_for_bt['sign'][i - 2] == 1 and data_for_bt['sign'][i - 3] == 0:
                                        sell_sign_list.append(i)
                            elif sell_con_d_e.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[sell_con_a_c.get()] == float(sell_con_d_e.get()), 1,
                                                               0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i - 1] == 1 and data_for_bt['sign'][i - 2] == 1 and data_for_bt['sign'][i - 3] == 0:
                                        sell_sign_list.append(i)
                        elif sell_con_c_c.get() == '≠':
                            if sell_con_d_c.get() != '':
                                data_for_bt['sign'] = np.where(
                                    data_for_bt[sell_con_a_c.get()] != data_for_bt[sell_con_d_c.get()], 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i - 1] == 1 and data_for_bt['sign'][i - 2] == 1 and data_for_bt['sign'][i - 3] == 0:
                                        sell_sign_list.append(i)
                            elif sell_con_d_e.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[sell_con_a_c.get()] != float(sell_con_d_e.get()), 1,
                                                               0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i - 1] == 1 and data_for_bt['sign'][i - 2] == 1 and data_for_bt['sign'][i - 3] == 0:
                                        sell_sign_list.append(i)

                    elif sell_con_b_c.get() == '连续5天':
                        if sell_con_c_c.get() == '>':
                            if sell_con_d_c.get() != '':
                                data_for_bt['sign'] = np.where(
                                    data_for_bt[sell_con_a_c.get()] > data_for_bt[sell_con_d_c.get()], 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i - 1] == 1 and data_for_bt['sign'][i - 2] == 1 and data_for_bt['sign'][i - 3] == 1 and data_for_bt['sign'][i - 4] == 1 and data_for_bt['sign'][i - 5] == 0:
                                        sell_sign_list.append(i)
                            elif sell_con_d_e.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[sell_con_a_c.get()] > float(sell_con_d_e.get()), 1,
                                                               0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i - 1] == 1 and data_for_bt['sign'][i - 2] == 1 and data_for_bt['sign'][i - 3] == 1 and data_for_bt['sign'][i - 4] == 1 and data_for_bt['sign'][i - 5] == 0:
                                        sell_sign_list.append(i)
                        elif sell_con_c_c.get() == '>=':
                            if sell_con_d_c.get() != '':
                                data_for_bt['sign'] = np.where(
                                    data_for_bt[sell_con_a_c.get()] >= data_for_bt[sell_con_d_c.get()], 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i - 1] == 1 and data_for_bt['sign'][i - 2] == 1 and data_for_bt['sign'][i - 3] == 1 and data_for_bt['sign'][i - 4] == 1 and data_for_bt['sign'][i - 5] == 0:
                                        sell_sign_list.append(i)
                            elif sell_con_d_e.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[sell_con_a_c.get()] >= float(sell_con_d_e.get()), 1,
                                                               0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i - 1] == 1 and data_for_bt['sign'][i - 2] == 1 and data_for_bt['sign'][i - 3] == 1 and data_for_bt['sign'][i - 4] == 1 and data_for_bt['sign'][i - 5] == 0:
                                        sell_sign_list.append(i)
                        elif sell_con_c_c.get() == '<':
                            if sell_con_d_c.get() != '':
                                data_for_bt['sign'] = np.where(
                                    data_for_bt[sell_con_a_c.get()] < data_for_bt[sell_con_d_c.get()], 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i - 1] == 1 and data_for_bt['sign'][i - 2] == 1 and data_for_bt['sign'][i - 3] == 1 and data_for_bt['sign'][i - 4] == 1 and data_for_bt['sign'][i - 5] == 0:
                                        sell_sign_list.append(i)
                            elif sell_con_d_e.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[sell_con_a_c.get()] < float(sell_con_d_e.get()), 1,
                                                               0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i - 1] == 1 and data_for_bt['sign'][i - 2] == 1 and data_for_bt['sign'][i - 3] == 1 and data_for_bt['sign'][i - 4] == 1 and data_for_bt['sign'][i - 5] == 0:
                                        sell_sign_list.append(i)
                        elif sell_con_c_c.get() == '<=':
                            if sell_con_d_c.get() != '':
                                data_for_bt['sign'] = np.where(
                                    data_for_bt[sell_con_a_c.get()] <= data_for_bt[sell_con_d_c.get()], 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i - 1] == 1 and data_for_bt['sign'][i - 2] == 1 and data_for_bt['sign'][i - 3] == 1 and data_for_bt['sign'][i - 4] == 1 and data_for_bt['sign'][i - 5] == 0:
                                        sell_sign_list.append(i)
                            elif sell_con_d_e.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[sell_con_a_c.get()] <= float(sell_con_d_e.get()), 1,
                                                               0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i - 1] == 1 and data_for_bt['sign'][i - 2] == 1 and data_for_bt['sign'][i - 3] == 1 and data_for_bt['sign'][i - 4] == 1 and data_for_bt['sign'][i - 5] == 0:
                                        sell_sign_list.append(i)
                        elif sell_con_c_c.get() == '=':
                            if sell_con_d_c.get() != '':
                                data_for_bt['sign'] = np.where(
                                    data_for_bt[sell_con_a_c.get()] == data_for_bt[sell_con_d_c.get()], 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i - 1] == 1 and data_for_bt['sign'][i - 2] == 1 and data_for_bt['sign'][i - 3] == 1 and data_for_bt['sign'][i - 4] == 1 and data_for_bt['sign'][i - 5] == 0:
                                        sell_sign_list.append(i)
                            elif sell_con_d_e.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[sell_con_a_c.get()] == float(sell_con_d_e.get()), 1,
                                                               0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i - 1] == 1 and data_for_bt['sign'][i - 2] == 1 and data_for_bt['sign'][i - 3] == 1 and data_for_bt['sign'][i - 4] == 1 and data_for_bt['sign'][i - 5] == 0:
                                        sell_sign_list.append(i)
                        elif sell_con_c_c.get() == '≠':
                            if sell_con_d_c.get() != '':
                                data_for_bt['sign'] = np.where(
                                    data_for_bt[sell_con_a_c.get()] != data_for_bt[sell_con_d_c.get()], 1, 0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i - 1] == 1 and data_for_bt['sign'][i - 2] == 1 and data_for_bt['sign'][i - 3] == 1 and data_for_bt['sign'][i - 4] == 1 and data_for_bt['sign'][i - 5] == 0:
                                        sell_sign_list.append(i)
                            elif sell_con_d_e.get() != '':
                                data_for_bt['sign'] = np.where(data_for_bt[sell_con_a_c.get()] != float(sell_con_d_e.get()), 1,
                                                               0)
                                for i in range(data_for_bt.shape[0]):
                                    if data_for_bt['sign'][i] == 1 and data_for_bt['sign'][i - 1] == 1 and data_for_bt['sign'][i - 2] == 1 and data_for_bt['sign'][i - 3] == 1 and data_for_bt['sign'][i - 4] == 1 and data_for_bt['sign'][i - 5] == 0:
                                        sell_sign_list.append(i)

                    data_for_bt = data_for_bt.drop('sign', axis=1)

                    i, j = 0, 0  # i: 买入索引, j: 卖出索引
                    current_position = 0
                    n_buy, n_sell_1 = len(buy_sign_list), len(sell_sign_list)
                    for sell_t in range(n_sell_1):
                        if sell_sign_list[sell_t] < buy_sign_list[0]:
                            del sell_sign_list[sell_t]
                        else:
                            break

                    n_sell_2 = len(sell_sign_list)

                    buy_date = []
                    sell_date = []

                    if n_buy > 1 and n_sell_2 != 0:
                        while i < n_buy and j < n_sell_2:
                            if current_position == 0:
                                buy_date.append(buy_sign_list[i])
                                i += 1
                                current_position = 1
                            elif current_position == 1:
                                if sell_sign_list[j] > buy_date[-1]:
                                    sell_date.append(sell_sign_list[j])
                                    current_position = 2
                                elif sell_sign_list[j] <= buy_date[-1]:
                                    j += 1
                            elif current_position == 2:
                                if buy_sign_list[i] > sell_date[-1]:
                                    buy_date.append(buy_sign_list[i])
                                    current_position = 1
                                elif buy_sign_list[i] <= sell_date[-1]:
                                    i += 1
                    elif n_buy == 1 and n_sell_2 != 0:
                        buy_date.append(buy_sign_list[0])
                        while j < n_sell_2:
                            if sell_sign_list[j] > buy_date[-1]:
                                sell_date.append(sell_sign_list[j])
                                break
                            elif sell_sign_list[j] <= buy_date[-1]:
                                j += 1
                    elif n_buy == 0 or n_sell_2 == 0:
                        pass

                    for buy_d in buy_date:
                        buy_x = data_for_bt.iloc[buy_d]['日期']
                        bt_ax.axvline(x=buy_x, color=up, linestyle='--', linewidth=1, alpha=0.9)

                    for sell_d in sell_date:
                        sell_x = data_for_bt.iloc[sell_d]['日期']
                        bt_ax.axvline(x=sell_x, color=down, linestyle='--', linewidth=1, alpha=0.9)

                    list_for_fill = buy_date + sell_date
                    list_for_fill.sort()
                    n = len(list_for_fill)
                    a, b = 0, 1
                    c, d = 0, 1
                    k = 1
                    outcome_text_display = ''
                    total_holding_period = 0
                    total_return = 1
                    while a in range(n):
                        if b in range(n):
                            t = list_for_fill[a]
                            s = list_for_fill[b]
                            x1 = data_for_bt.iloc[t]['日期']
                            x2 = data_for_bt.iloc[s]['日期']
                            bt_ax.axvspan(x1, x2, alpha=0.2, color='#0098cb')
                            a += 2
                            b += 2
                        else:
                            break

                    while c in range(n):
                        if d in range(n):
                            m = list_for_fill[c]
                            l = list_for_fill[d]
                            return_rate = (data_for_bt.iloc[l]['收盘'] - data_for_bt.iloc[m]['收盘']) / data_for_bt.iloc[m]['收盘']
                            t1 = data_for_bt.iloc[m]['日期']
                            t2 = data_for_bt.iloc[l]['日期']
                            holding_period = (t2 - t1).days
                            transaction_text = f"""第{k}次交易：
买入日期：{t1} ({data_for_bt.iloc[m]['收盘']})
卖出日期：{t2} ({data_for_bt.iloc[l]['收盘']})
持有天数：{holding_period}
持有期收益率：{round(return_rate * 100, 2)}%
        
===================="""
                            outcome_text_display = outcome_text_display + transaction_text
                            total_holding_period = total_holding_period + holding_period
                            total_return = total_return * (1 + return_rate)
                            k += 1
                            c += 2
                            d += 2
                        else:
                            break

                    conclusion_str = f"""====================
交易次数：{k - 1}
总持有天数：{total_holding_period} / {data_for_bt.shape[0]}
持有期总收益率：{round((total_return - 1) * 100, 2)}%
年化收益率：{round(((1 + (total_return - 1) / (252/total_holding_period)) ** (252/total_holding_period) - 1) * 100, 2)}%"""

                    bt_canvas_draw.draw()
                    v_listbox.config(state="disabled")
                    outcome_text.config(state="normal")
                    outcome_text.delete(1.0, tk.END)
                    outcome_text.insert(tk.END, str(outcome_text_display + conclusion_str))
                    outcome_text.config(state="disabled")
                    apply_bt_b.config(state="disabled")
            except ZeroDivisionError:
                tk.messagebox.showerror("Error", "回测失败:期间无满足条件的交易！")
            except Exception as e:
                tk.messagebox.showerror("Error", f"回测失败: {str(e)}")

        listbox_frame = tk.Frame(bt_window)
        listbox_frame.grid(row=0, column=0, padx=5, pady=5)
        v_listbox = tk.Listbox(listbox_frame, width=15, height=13, selectmode='multiple', exportselection=False)
        v_listbox.grid(row=0, column=0)
        v_listbox_yscrollbar = ttk.Scrollbar(listbox_frame, command=v_listbox.yview, style="round")
        v_listbox_yscrollbar.grid(row=0, column=1, sticky='ns')
        v_listbox.config(yscrollcommand=v_listbox_yscrollbar.set)
        v_listbox.bind('<<ListboxSelect>>', bt_plot)
        ttk.Separator(bt_window).grid(row=1, column=0, padx=5, pady=5, sticky='EW')
        tk.Label(bt_window, text='显示表格:', font=("微软雅黑", 10)).grid(row=2, column=0, padx=3)
        bt_df_choose_c = ttk.Combobox(bt_window, state='readonly', font=('微软雅黑', 10), width=11, values=bt_df_list)
        bt_df_choose_c.grid(row=3, column=0, padx=3, pady=(7,3))
        bt_df_choose_c.set('data_for_bt')
        bt_df_choose_c.bind('<<ComboboxSelected>>', show_table)
        ttk.Separator(bt_window).grid(row=4, column=0, padx=5, pady=5, sticky='EW')
        ttk.Button(bt_window, text='清空画布', cursor='hand2', style='outline', command=clear_canvas).grid(row=5, column=0, padx=5, pady=5)
        ttk.Button(bt_window, text='保存图像', cursor='hand2', style='outline', command=save_figure).grid(row=6, column=0, padx=5, pady=5)
        outcome_lbframe = ttk.Labelframe(bt_window, text="Outcome")
        outcome_lbframe.grid(row=7, column=0, padx=5, columnspan=2, rowspan=2)
        outcome_text = tk.Text(outcome_lbframe, font=("微软雅黑", 10), width=27, height=16, state="disabled")
        outcome_text.pack(side="left", padx=(3, 0), pady=(0, 3))
        outcome_text_yscrollbar = ttk.Scrollbar(outcome_lbframe, command=outcome_text.yview, style="round")
        outcome_text_yscrollbar.pack(side="right", fill='y', pady=(0, 3))
        outcome_text.config(yscrollcommand=outcome_text_yscrollbar.set)

        draw_frame = tk.Frame(bt_window)
        draw_frame.grid(row=0, column=1, padx=5, pady=5, rowspan=7, columnspan=8)
        bt_canvas_lbframe = ttk.Labelframe(draw_frame, text='canvas')  # , height=587, width=760
        bt_canvas_lbframe.pack(side='top')
        bt_canvas = tk.Canvas(bt_canvas_lbframe)
        bt_canvas.pack()
        bt_canvas.pack_propagate(False)
        bt_figure = plt.Figure(figsize=(7.8, 3.7))
        bt_figure.subplots_adjust(left=0.06, right=0.99, bottom=0.18, top=0.96)
        bt_ax = bt_figure.subplots()
        bt_canvas_draw = FigureCanvasTkAgg(bt_figure, bt_canvas)
        bt_canvas_draw.get_tk_widget().grid(row=0, column=0, padx=3, pady=(0, 2))
        bt_figure.patch.set_facecolor('#888888')
        bt_ax.patch.set_facecolor('#c9c9c9')

        # 鼠标拖动 处理事件
        startx = 0
        starty = 0
        mPress = False

        def call_back(event):
            axtemp = event.inaxes
            base_scale = 1.5
            x_min, x_max = axtemp.get_xlim()  ##获取x轴范围
            y_min, y_max = axtemp.get_ylim()  ##获取y轴范围
            fanwei_x = (x_max - x_min) / 2  # 范围缩放
            fanwei_y = (y_max - y_min) / 2
            xdata = event.xdata  # get event x location
            ydata = event.ydata  # get event y location
            if event.button == 'up':
                # deal with zoom in
                scale_factor = 1 / base_scale
            elif event.button == 'down':
                # deal with zoom out
                scale_factor = base_scale
            else:
                # deal with something that should never happen
                scale_factor = 1

            axtemp.set(xlim=(xdata - fanwei_x * scale_factor, xdata + fanwei_x * scale_factor))
            # axtemp.set(ylim=(ydata - fanwei_y * scale_factor, ydata + fanwei_y * scale_factor))
            bt_figure.canvas.draw_idle()  # 绘图动作实时反映在图像上

        def call_move(event):
            # print(event.name)
            global mPress
            global startx
            global starty
            mouse_x = event.x
            mouse_y = event.y
            axtemp = event.inaxes
            if event.name == 'button_press_event':
                if axtemp and event.button == 1:
                    if axtemp.get_legend():
                        legend_bbox = axtemp.get_legend().get_window_extent()
                        left_bottom = legend_bbox.get_points()[0]
                        right_top = legend_bbox.get_points()[1]

                        if left_bottom[0] <= mouse_x <= right_top[0] and left_bottom[1] <= mouse_y <= right_top[1]:
                            # print("在图例上按下鼠标")
                            # 在图例上按下鼠标
                            mPress = False
                            return
                    # 没有图例的情况
                    # print("在 Axes 上按下鼠标")
                    # 在 Axes 上按下鼠标
                    mPress = True
                    startx = event.xdata
                    starty = event.ydata
                    return
            elif event.name == 'button_release_event':
                if axtemp and event.button == 1:
                    mPress = False
            elif event.name == 'motion_notify_event':
                if axtemp and event.button == 1 and mPress:
                    if axtemp.get_legend():
                        legend_bbox = axtemp.get_legend().get_window_extent()
                        left_bottom = legend_bbox.get_points()[0]
                        right_top = legend_bbox.get_points()[1]

                        if left_bottom[0] <= mouse_x <= right_top[0] and left_bottom[1] <= mouse_y <= right_top[1]:
                            print("在图例上移动鼠标")
                            # 在图例上按下鼠标
                            mPress = False
                            return

                    # 没有图例的情况
                    # print("在Axes上移动鼠标")
                    x_min, x_max = axtemp.get_xlim()
                    y_min, y_max = axtemp.get_ylim()
                    w = x_max - x_min
                    h = y_max - y_min
                    # print(event)
                    # 移动
                    mx = event.xdata - startx
                    my = event.ydata - starty
                    # 注意这里， -mx,  因为下一次 motion事件的坐标，已经是在本次做了移动之后的坐标系了，所以要体现出来
                    # startx=event.xdata-mx  startx=event.xdata-(event.xdata-startx)=startx, 没必要再赋值了
                    # starty=event.ydata-my
                    # print(mx,my,x_min,y_min,w,h)
                    left = x_min - mx
                    right = x_min - mx + w

                    axtemp.set(xlim=(left, right))

                    # axtemp.set(ylim=(y_min - my, y_min - my + h))
                    bt_figure.canvas.draw_idle()  # 绘图动作实时反映在图像上

            return

        bt_figure.canvas.mpl_connect('scroll_event', call_back)
        bt_figure.canvas.mpl_connect('button_press_event', call_move)
        bt_figure.canvas.mpl_connect('button_release_event', call_move)
        bt_figure.canvas.mpl_connect('motion_notify_event', call_move)

        table_dis_lbframe = ttk.Labelframe(bt_window, text="Table Display")
        table_dis_lbframe.grid(row=7, column=2, columnspan=4, ipadx=2, ipady=2, padx=(4,0))
        table_dis_frame = tk.Frame(table_dis_lbframe)
        table_dis_frame.pack()
        table_dis_frame.pack_propagate(False)
        display_table = Table(table_dis_frame, height=130, width=423, cols=8)

        table_des_lbframe = ttk.Labelframe(bt_window, text="Describe")
        table_des_lbframe.grid(row=7, column=6, columnspan=4, ipadx=2, ipady=2)
        table_des_frame = tk.Frame(table_des_lbframe)
        table_des_frame.pack()
        table_des_frame.pack_propagate(False)
        describe_table = Table(table_des_frame, height=130, width=270, cols=8)

        display_table.model.df = data_for_bt
        describe_table.model.df = data_for_bt.describe()

        for table in [display_table, describe_table]:
            table.cellbackgr = '#373737'
            table.textcolor = "#ececec"
            table.rowselectedcolor = '#707070'
            table.rowheaderbgcolor = '#707070'
            table.font = ('Arial', 8)
            table.show()
            table.zoomOut()

        bt_option_lbframe = ttk.Labelframe(bt_window, text="Function")
        bt_option_lbframe.grid(row=8, column=2, pady=1, columnspan=8, ipady=2)
        tk.Label(bt_option_lbframe, text='新建变量:', font=("微软雅黑", 10)).grid(row=0, column=0, padx=7)
        tk.Label(bt_option_lbframe, text='变量名:', font=("微软雅黑", 10)).grid(row=1, column=0, padx=(27, 0), pady=2)
        new_variable_name_e = ttk.Entry(bt_option_lbframe, width=10, font=("微软雅黑", 10))
        new_variable_name_e.grid(row=1, column=1, pady=2)
        tk.Label(bt_option_lbframe, text='变量值:', font=("微软雅黑", 10)).grid(row=1, column=2, padx=(18, 0), pady=2)
        new_variable_value_e = ttk.Entry(bt_option_lbframe, width=42, font=("微软雅黑", 10))
        new_variable_value_e.grid(row=1, column=3, pady=2, columnspan=6)
        ttk.Button(bt_option_lbframe, text='创建变量', style="outline", cursor='hand2', command=create_new_variable).grid(row=1,column=9,padx=(6,12))

        ttk.Separator(bt_option_lbframe).grid(row=2, column=0, columnspan=10, sticky='EW', pady=3, padx=6)

        strategy_frame = ttk.Frame(bt_option_lbframe)
        strategy_frame.grid(row=3, column=0, columnspan=10)
        tk.Label(strategy_frame, text='交易策略:', font=("微软雅黑", 10)).grid(row=0, column=0, padx=7)
        tk.Label(strategy_frame, text='买入条件:', font=("微软雅黑", 10)).grid(row=1, column=0, padx=(27, 0), pady=2)
        buy_con_a_c = ttk.Combobox(strategy_frame, state='readonly', font=('微软雅黑', 10), width=11, values=variables)
        buy_con_a_c.grid(row=1, column=1, padx=2, pady=2)
        buy_con_b_c = ttk.Combobox(strategy_frame, state='readonly', font=('微软雅黑', 10), width=7, values=('首次', '连续2天', '连续3天', '连续5天'))
        buy_con_b_c.grid(row=1, column=2, padx=2, pady=2)
        buy_con_c_c = ttk.Combobox(strategy_frame, state='readonly', font=('微软雅黑', 10), width=4, values=(">", "<", ">=", "<=", "=", "≠"))
        buy_con_c_c.grid(row=1, column=3, padx=2, pady=2)
        buy_con_d_e = ttk.Entry(strategy_frame, font=('微软雅黑', 10), width=10)
        buy_con_d_e.grid(row=1, column=4, padx=2, pady=2)
        tk.Label(strategy_frame, text='/', font=("微软雅黑", 10)).grid(row=1, column=5, padx=6, pady=2)
        buy_con_d_c = ttk.Combobox(strategy_frame, state='readonly', font=('微软雅黑', 10), width=12, values=variables)
        buy_con_d_c.grid(row=1, column=6, padx=2, pady=2)
        buy_con_d_e.bind('<KeyRelease>', clear_buy_c)
        buy_con_d_c.bind('<<ComboboxSelected>>', clear_buy_e)
        ttk.Button(strategy_frame, text='清空条件', style="outline", cursor='hand2', command=clear_conditions).grid(row=1, column=7, padx=(6, 12))

        tk.Label(strategy_frame, text='卖出条件:', font=("微软雅黑", 10)).grid(row=2, column=0, padx=(27, 0), pady=2)
        sell_con_a_c = ttk.Combobox(strategy_frame, state='readonly', font=('微软雅黑', 10), width=11, values=variables)
        sell_con_a_c.grid(row=2, column=1, padx=2, pady=2)
        sell_con_b_c = ttk.Combobox(strategy_frame, state='readonly', font=('微软雅黑', 10), width=7, values=('首次', '连续2天', '连续3天', '连续5天'))
        sell_con_b_c.grid(row=2, column=2, padx=2, pady=2)
        sell_con_c_c = ttk.Combobox(strategy_frame, state='readonly', font=('微软雅黑', 10), width=4, values=(">", "<", ">=", "<=", "=", "≠"))
        sell_con_c_c.grid(row=2, column=3, padx=2, pady=2)
        sell_con_d_e = ttk.Entry(strategy_frame, font=('微软雅黑', 10), width=10)
        sell_con_d_e.grid(row=2, column=4, padx=2, pady=2)
        tk.Label(strategy_frame, text='/', font=("微软雅黑", 10)).grid(row=2, column=5, padx=6, pady=2)
        sell_con_d_c = ttk.Combobox(strategy_frame, state='readonly', font=('微软雅黑', 10), width=12, values=variables)
        sell_con_d_c.grid(row=2, column=6, padx=2, pady=2)
        sell_con_d_e.bind('<KeyRelease>', clear_sell_c)
        sell_con_d_c.bind('<<ComboboxSelected>>', clear_sell_e)
        apply_bt_b = ttk.Button(strategy_frame, text='执行回测', style="outline", cursor='hand2', command=apply_strategy)
        apply_bt_b.grid(row=2, column=7, padx=(6, 12))

        update_listbox()
        bt_ax.plot(data_for_bt['日期'], data_for_bt['收盘'], label='收盘')
        bt_ax.tick_params(axis='x', labelrotation=45)
        bt_ax.legend()
        bt_ax.grid(axis='y',alpha=0.8)
        bt_canvas_draw.draw()
    except Exception as e:
        tk.messagebox.showerror("Error", f"回测失败: {str(e)}")

def news():
    global news_df
    global stock_code
    global window_df
    global window_title
    try:
       # if news_df.empty:
           # news_df = ak.stock_info_global_cls(symbol="全部")
       # window_df = news_df.copy()
       # window_title = 'News'
       # view_data()
        webbrowser.open_new("https://www.cls.cn/telegraph")

    except Exception as e:
        tk.messagebox.showerror("Error", f"获取数据失败: {str(e)}")

def all_stock():
    global all_stock_data
    global window_df
    global window_title
    try:
        if all_stock_data.empty:
            all_stock_data = ak.stock_zh_a_spot_em().drop('序号', axis=1)

        window_df = all_stock_data.copy()
        window_title = 'Spot Data'
        view_data()
    except Exception as e:
        tk.messagebox.showerror("Error", f"获取数据失败: {str(e)}")

def capm():
    global rf
    global rm
    global SR
    global Erp
    global Erp_annual
    global capm_out_str
    global rf_label_text
    try:
        if rf_label_text == "年化无风险利率(%):":
            rf_annual = float(rf_entry.get()) / 100
            rf = (1 + rf_annual) ** (1 / 252) - 1 #rf daily
            rf_label_text = "日度无风险利率(%):"
            rf_label.config(text=rf_label_text)
        else:
            rf = float(rf_entry.get()) / 100
            rf_annual = (1 + rf) ** 252 - 1
        rm = float(rm_entry.get()) / 100  # rm daily
        data_for_capm = data.copy()
        data_for_capm['multiple'] = (data_for_capm['涨跌幅'] + 100) / 100
        rp = data_for_capm['multiple'].prod() ** (1 / data_for_capm.shape[0]) - 1 #rp daily
        cov = data['涨跌幅'].cov(mktdata['涨跌幅'])
        var_m = mktdata['涨跌幅'].var()
        beta = cov / var_m
        Erp = beta * (rm - rf) + rf
        Erp_annual = ((1 + Erp) ** 252) - 1
        rp_annual = ((1 + rp) ** 252) - 1
        alpha = rp_annual - Erp_annual
        SR = (rp_annual - rf_annual) / float(data['涨跌幅'].std() * math.sqrt(252))

        capm_out_str = f'α={round(alpha,4)}  β={round(beta,4)}  SR={round(SR,4)}'
        capm_output.config(state=tk.NORMAL)
        capm_output.delete(0, tk.END)
        capm_output.insert(0, capm_out_str)
        capm_output.config(state='readonly')

        rf_entry.delete(0, tk.END)
        rf_entry.insert(0, str(round(rf * 100, 4)))
        rm_entry.delete(0, tk.END)
        rm_entry.insert(0, str(rm * 100))

    except Exception as e:
        tk.messagebox.showerror("Error", f"获取数据失败: {str(e)}")

def summary():
    global summary_df_sh
    global summary_df_sz
    try:
        date = get_trading_date()
        if summary_df_sh.empty:
            summary_df_sh = ak.stock_sse_summary()
        if summary_df_sz.empty:
            summary_df_sz = ak.stock_szse_summary(str(date).replace("-",""))

        view_window = tk.Toplevel(root)
        view_window.title("Market Summary")
        view_window.geometry("600x900")

        summary_df_sh_frame = tk.Frame(view_window)
        summary_df_sh_frame.pack(side='top', fill='both', expand=True)
        summary_df_sh_lbframe = ttk.Labelframe(summary_df_sh_frame, text="上交所.SH")
        summary_df_sh_lbframe.pack(pady=0, padx=1, side="top", ipadx=3, ipady=3)
        summary_sh_data_table = Table(summary_df_sh_lbframe, showstatusbar=True, showtoolbar=True)
        summary_sh_data_table.model.df = summary_df_sh
        summary_sh_data_table.cellbackgr = '#373737'
        summary_sh_data_table.rowselectedcolor = '#707070'
        summary_sh_data_table.rowheaderbgcolor = '#707070'
        summary_sh_data_table.textcolor = "#ececec"
        summary_sh_data_table.font = ('Arial', 12)
        summary_sh_data_table.show()
        summary_sh_data_table.zoomOut()
        summary_sh_data_table.zoomIn()

        summary_df_sz_frame = tk.Frame(view_window)
        summary_df_sz_frame.pack(side='top', fill='both', expand=True)
        summary_df_sz_lbframe = ttk.Labelframe(summary_df_sz_frame, text=f"深交所.SZ ({date})")
        summary_df_sz_lbframe.pack(pady=0, padx=1, side="top", ipadx=3, ipady=3)
        summary_sz_data_table = Table(summary_df_sz_lbframe, showstatusbar=True, showtoolbar=True)
        summary_sz_data_table.model.df = summary_df_sz
        summary_sz_data_table.cellbackgr = '#373737'
        summary_sz_data_table.rowselectedcolor = '#707070'
        summary_sz_data_table.rowheaderbgcolor = '#707070'
        summary_sz_data_table.textcolor = "#ececec"
        summary_sz_data_table.font = ('Arial', 12)
        summary_sz_data_table.show()
        summary_sz_data_table.zoomOut()
        summary_sz_data_table.zoomIn()

        view_window.wait_window()

    except Exception as e:
        tk.messagebox.showerror("Error", f"获取数据失败: {str(e)}")

def esg_grade():
    global ESG_df
    global window_df
    global window_title
    try:
        if ESG_df.empty:
            try:
                ESG_df = pd.read_csv('ESG.csv')
            except FileNotFoundError:
                ESG_df = ak.stock_esg_hz_sina()

        window_df = ESG_df.copy()
        window_title = 'ESG Grade'
        view_data()
    except Exception as e:
        tk.messagebox.showerror("Error", f"获取数据失败: {str(e)}")

#top frame
tk.Label(tp_frame, text="接口:", font=("微软雅黑", 10)).grid(row=0, column=0, padx=(25, 1))
interface_combobox = ttk.Combobox(tp_frame, values=('东方财富', '新浪财经', '腾讯'), width=8, state="readonly")
interface_combobox.grid(row=0, column=1, padx=1, pady=1)
interface_combobox.set('东方财富')
interface_combobox.bind("<<ComboboxSelected>>", judge_interface)
tk.Label(tp_frame, text="频率:", font=("微软雅黑", 10)).grid(row=1, column=0, padx=(25, 1))
frequency_combobox = ttk.Combobox(tp_frame, values=('日数据', '周数据', '月数据'), width=8, state="readonly")
frequency_combobox.grid(row=1, column=1, padx=1, pady=1)
frequency_combobox.set('日数据')
code_or_name = tk.Label(tp_frame, text=code_name_text, font=("微软雅黑", 10))
code_or_name.grid(row=0, column=2, padx=(28, 1))
ttk.Checkbutton(tp_frame, text='简称查找', command=change_code_name, bootstyle="round-toggle", cursor='hand2').grid(row=0, column=4, padx=(3,1))

stock_code_entry = ttk.Entry(tp_frame, textvariable=stock_code, width=9, font=("微软雅黑", 10))
stock_code_entry.grid(row=0, column=3, padx=1)
tk.Label(tp_frame, text="复权方式:", font=("微软雅黑", 10)).grid(row=1, column=2, padx=(28, 1))
fq_combobox = ttk.Combobox(tp_frame, values=('前复权', '后复权'), width=8, state="readonly")
fq_combobox.grid(row=1, column=3, padx=1)
fq_combobox.set('前复权')

tk.Label(tp_frame, text="开始日期:", font=("微软雅黑", 10)).grid(row=0, column=5, padx=(80, 1))
start_year = ttk.Spinbox(tp_frame, from_=1990, to=datetime.date.today().year, width=5)
start_year.grid(row=0, column=6, padx=1, pady=1)
start_year.set(datetime.date.today().year - 1)
tk.Label(tp_frame, text="年", font=("微软雅黑", 10)).grid(row=0, column=7, padx=1)
start_month = ttk.Spinbox(tp_frame, from_=1, to=12, width=2)
start_month.grid(row=0, column=8, padx=(15, 1), pady=1)
start_month.set(datetime.date.today().month)
tk.Label(tp_frame, text="月", font=("微软雅黑", 10)).grid(row=0, column=9, padx=1)
start_day = ttk.Spinbox(tp_frame, from_=1, to=31, width=2)
start_day.grid(row=0, column=10, padx=(15, 1), pady=1)
start_day.set(datetime.date.today().day)
tk.Label(tp_frame, text="日", font=("微软雅黑", 10)).grid(row=0, column=11, padx=1)

tk.Label(tp_frame, text="结束日期:", font=("微软雅黑", 10)).grid(row=1, column=5, padx=(80, 1))
end_year = ttk.Spinbox(tp_frame, from_=1990, to=datetime.date.today().year, width=5)
end_year.grid(row=1, column=6, padx=1, pady=1)
end_year.set(datetime.date.today().year)
tk.Label(tp_frame, text="年", font=("微软雅黑", 10)).grid(row=1, column=7, padx=1)
end_month = ttk.Spinbox(tp_frame, from_=1, to=12, width=2)
end_month.grid(row=1, column=8, padx=(15, 1), pady=1)
end_month.set(datetime.date.today().month)
tk.Label(tp_frame, text="月", font=("微软雅黑", 10)).grid(row=1, column=9, padx=1)
end_day = ttk.Spinbox(tp_frame, from_=1, to=31, width=2)
end_day.grid(row=1, column=10, padx=(15, 1), pady=1)
end_day.set(datetime.date.today().day)
tk.Label(tp_frame, text="日", font=("微软雅黑", 10)).grid(row=1, column=11, padx=1)

ttk.Button(tp_frame, text='机构推荐', style="outline", command=institution_recommend, cursor='hand2').grid(row=0, column=12, padx=(115,1))
ttk.Button(tp_frame, text='投资评级', style="outline", command=institution_evaluation, cursor='hand2').grid(row=1, column=12, padx=(115,1))

# info frame
up_down_label = tk.Label(info_frame, text=' ', font=("微软雅黑", 2), width=1, height=12)
up_down_label.grid(row=0, column=0, padx=(50, 0), rowspan=2)
up_down_label.configure(bg='#ababab')
price_show_label = tk.Label(info_frame, text=str(current_price_show), font=("微软雅黑", 27, 'bold'), width=7)
price_show_label.grid(row=0, column=1, padx=(3, 0), rowspan=2)
price_show_label.config(fg='#ececec')
flu_range_label = tk.Label(info_frame, text=str(flu_range_show), font=("微软雅黑", 10, 'bold'))
flu_range_label.grid(row=0, column=2)
flu_range_spot_label = tk.Label(info_frame, text=str(flu_range_spot_show), font=("微软雅黑", 10, 'bold'))
flu_range_spot_label.grid(row=0, column=3, padx=(0, 1))
date_label = tk.Label(info_frame, text=str(price_date_show), font=("微软雅黑", 10, 'bold'), width=21)
date_label.grid(row=1, column=2, padx=(5, 1), columnspan=2)

canvas_frame = ttk.Frame(info_frame)
canvas_frame.grid(row=0, column=4, rowspan=2, padx=(3,0))
v_canvas = tk.Canvas(canvas_frame)
v_canvas.pack()
v_canvas.pack_propagate(False)
figure = plt.Figure(figsize=(1.4, 0.7))
ax = figure.subplots()
ax.axis('off')
figure.patch.set_alpha(0.0)
ax.patch.set_alpha(0.0)
canvas = FigureCanvasTkAgg(figure, v_canvas)
canvas.get_tk_widget().grid(row=0, column=0)

pbpe_lbframe = ttk.Labelframe(info_frame, text="PB & PE")
pbpe_lbframe.grid(row=0, column=5, rowspan=2, padx=(223, 0), pady=(0, 4))
tk.Label(pbpe_lbframe, text="P/B:", font=("微软雅黑", 10)).grid(row=0, column=0, padx=(8, 2))
tk.Label(pbpe_lbframe, text="P/E:", font=("微软雅黑", 10)).grid(row=1, column=0, padx=(8, 2), pady=(0, 2))
pb_scale = ttk.Scale(pbpe_lbframe, from_=0.5, to=2, orient=tk.HORIZONTAL, state=tk.DISABLED)
pb_scale.grid(row=0, column=1, padx=2, pady=(2, 0))
pe_scale = ttk.Scale(pbpe_lbframe, from_=10, to=30, orient=tk.HORIZONTAL, state=tk.DISABLED)
pe_scale.grid(row=1, column=1, padx=2)
pb_value_label = tk.Label(pbpe_lbframe, text=pb_ratio_show, font=("微软雅黑", 10), width=8)
pb_value_label.grid(row=0, column=2, padx=(2, 4))
pe_value_label = tk.Label(pbpe_lbframe, text=pe_ratio_show, font=("微软雅黑", 10), width=8)
pe_value_label.grid(row=1, column=2, padx=(2, 4), pady=(0, 6))

# profile frame
profile_table_lbframe = ttk.Labelframe(describe_frame, text="Profile", height=355, width=332)
profile_table_lbframe.pack(pady=0, padx=1, side="left", ipadx=5, ipady=5)
profile_table_lbframe.pack_propagate(False)
profile_table_frame = tk.Frame(profile_table_lbframe)
profile_table_frame.pack()
profile_table_frame.pack_propagate(False)

profile_table = Table(profile_table_frame, height=303, width=276, cols=8)
profile_table.show()
profile_table.zoomIn()

# Indicator frame
indicator_table_lbframe = ttk.Labelframe(describe_frame, text="Indicator", height=355, width=562)
indicator_table_lbframe.pack(pady=0, padx=1, side="left", ipadx=5, ipady=5)
indicator_table_lbframe.pack_propagate(False)
indicator_table_frame = tk.Frame(indicator_table_lbframe)
indicator_table_frame.pack()
indicator_table_frame.pack_propagate(False)

indicator_table = Table(indicator_table_frame, height=303, width=506, cols=8)
indicator_table.show()
indicator_table.zoomIn()

#opt frame
opt_frame = tk.Frame(describe_frame)
opt_frame.pack(side='left')
opt_lbframe = ttk.Labelframe(opt_frame, text="Stock Data")
opt_lbframe.pack(pady=0, padx=1, side="top", ipadx=3, ipady=3)
root.bind("<Return>", grab_data)

ttk.Button(opt_lbframe, text='获取数据', command=grab_data, style="outline", cursor='hand2', width=7).grid(row=0, column=0, padx=(10,1))
view_data_b = ttk.Button(opt_lbframe, text='查看数据', style="outline", command=view_stock_data, state="disabled", width=7)
view_data_b.grid(row=1, column=0, padx=(10,1), pady=(5,0))
valuation_b = ttk.Button(opt_lbframe, text='估值数据', style="outline", state="disabled", command=valuation_data, width=7)
valuation_b.grid(row=2, column=0, padx=(10,1), pady=(5,0))
dividend_b = ttk.Button(opt_lbframe, text='分红信息', style="outline", state="disabled", command=dividend, width=7)
dividend_b.grid(row=3, column=0, padx=(10,1), pady=(5,0))
individual_report_b = ttk.Button(opt_lbframe, text='个股研报', style="outline", state="disabled", command=individual_report, width=7)
individual_report_b.grid(row=4, column=0, padx=(10,1), pady=(5,0))
backtesting_b = ttk.Button(opt_lbframe, text='回测模拟', style="outline", state="disabled", command=back_testing, width=7)
backtesting_b.grid(row=5, column=0, padx=(10,1), pady=(5,0))

ttk.Button(opt_lbframe, text='财联社', style="outline", command=news, cursor='hand2', width=7).grid(row=7, column=0, padx=(10,1), pady=(5,0))
ttk.Button(opt_lbframe, text='市场概况', style="outline", command=summary, cursor='hand2', width=7).grid(row=8, column=0, padx=(10,1), pady=(5,0))

ttk.Separator(opt_lbframe).grid(row=6, column=0, columnspan=3, sticky='EW', pady=(10,3), padx=(8, 0))

kline_b = ttk.Button(opt_lbframe, text='K线图MACD', style="outline", command=kline, state="disabled", width=10)
kline_b.grid(row=0, column=1, padx=(10,0))
rsi_b = ttk.Button(opt_lbframe, text='RSI&MOM', style="outline", command=rsi_mom, state="disabled", width=10)
rsi_b.grid(row=1, column=1, padx=(10,0), pady=(5,0))
scatterline_b = ttk.Button(opt_lbframe, text='收益率散点图', style="outline", command=scatter_line, state="disabled", width=10)
scatterline_b.grid(row=2, column=1, columnspan=2, padx=(10,0), pady=(5,0))
pe_line_b = ttk.Button(opt_lbframe, text='市盈率趋势图', style="outline", state="disabled", command=pe_line, width=10)
pe_line_b.grid(row=3, column=1, padx=(10,0), pady=(5,0))
capital_structure_b = ttk.Button(opt_lbframe, text='股本结构', style="outline", state="disabled", command=cap_structure, width=10)
capital_structure_b.grid(row=4, column=1, padx=(10,0), pady=(5,0))
inday_b = ttk.Button(opt_lbframe, text='日内时分数据', style="outline", state="disabled", command=inday_data, width=10)
inday_b.grid(row=5, column=1, columnspan=2, padx=(10,0), pady=(5,0))

ttk.Button(opt_lbframe, text='市场实时数据', command=all_stock, style="outline", cursor='hand2', width=10).grid(row=7, column=1, padx=(10,1), pady=(5,0))
ttk.Button(opt_lbframe, text='ESG(华证)', command=esg_grade, style="outline", cursor='hand2', width=10).grid(row=8, column=1, padx=(10,1), pady=(5,0))

# describe frame
describe_lbframe = ttk.Labelframe(bt_frame, text="Describe", height=144, width=347)
describe_lbframe.pack(pady=0, padx=1, side="left", ipadx=5, ipady=5)
describe_lbframe.pack_propagate(False)
table_desc_frame = tk.Frame(describe_lbframe)
table_desc_frame.pack()
table_desc_frame.pack_propagate(False)

table_desc = Table(table_desc_frame, height=102, width=293, cols=8)
table_desc.show()
table_desc.zoomOut()


#financial frame
financial_lbframe = ttk.Labelframe(bt_frame, text="Financial Data")
financial_lbframe.pack(pady=0, padx=5, side="left", ipadx=0, ipady=5)
fin_report_b = ttk.Button(financial_lbframe, text='资产负债表', style="outline", command=fin_report, state="disabled")
fin_report_b.grid(row=0, column=0, padx=(7,0), pady=(5,0))
fin_benefit_b = ttk.Button(financial_lbframe, text='利润表数据', style="outline", command=fin_benefit, state="disabled")
fin_benefit_b.grid(row=1, column=0, padx=(7,0), pady=(5,0))
fin_abstract_b = ttk.Button(financial_lbframe, text='现金流量表', style="outline", command=fin_cash_flow, state="disabled")
fin_abstract_b.grid(row=2, column=0, padx=(7,0), pady=(5,0))

#market frame
market_lbframe = ttk.Labelframe(bt_frame, text="Market Data", height=218, width=100)
market_lbframe.pack(pady=0, padx=1, side="left", ipadx=5, ipady=3)
tk.Label(market_lbframe, text="选择指数:", font=("微软雅黑", 10)).grid(row=0, column=0, padx=(10, 1))
market_combobox = ttk.Combobox(market_lbframe, values=('上证指数', '深证成指', '沪深300', '创业板指数', '科创50', '北证50'), width=7, state="readonly")
market_combobox.grid(row=0, column=1, padx=1)
market_combobox.set('上证指数')
ttk.Button(market_lbframe, text='获取数据', command=grab_mkt_data, style="outline", cursor='hand2').grid(row=0, column=2, padx=2)
view_mkt_data_b = ttk.Button(market_lbframe, text='查看数据', style="outline", command=view_mkt_data, state="disabled")
view_mkt_data_b.grid(row=1, column=2, padx=2, pady=(5,0))
view_mkt_des_b = ttk.Button(market_lbframe, text='统计信息', style="outline", command=view_mkt_des, state="disabled")
view_mkt_des_b.grid(row=1, column=1, padx=2, pady=(5,0))
mkt_kline_b = ttk.Button(market_lbframe, text='K线图', style="outline", command=mkt_kline, state="disabled")
mkt_kline_b.grid(row=1, column=0, padx=(12,2), pady=(5,0))
ttk.Separator(market_lbframe).grid(row=2, column=0, columnspan=3, sticky='EW', pady=5, padx=(8, 0))
ttk.Button(market_lbframe, text='行业数据', style="outline", command=industry_info, cursor='hand2').grid(row=3, column=0, padx=(10, 1))
industry_label_e = ttk.Entry(market_lbframe, textvariable=industry_name, width=8, font=("微软雅黑", 9))
industry_label_e.grid(row=3, column=1, padx=(3,40), columnspan=2)
ttk.Button(market_lbframe, text='详情', style="outline", command=industry_search, cursor='hand2').grid(row=3, column=2, padx=(22,0))

#CAPM frame
capm_lbframe = ttk.Labelframe(bt_frame, text="CAPM")
capm_lbframe.pack(pady=0, padx=3, side="left", ipadx=2, ipady=5)
rf_label = tk.Label(capm_lbframe, text=rf_label_text, font=("微软雅黑", 10))
rf_label.grid(row=0, column=0, padx=(8, 1))
rf_entry = ttk.Entry(capm_lbframe, textvariable=rf, width=7, font=("微软雅黑", 10))
rf_entry.grid(row=0, column=1, padx=1)
ttk.Button(capm_lbframe, text='国债收益率', command=get_rf, style="outline", cursor='hand2').grid(row=0, column=2, padx=5)
tk.Label(capm_lbframe, text="日度市场收益率(%):", font=("微软雅黑", 10)).grid(row=1, column=0, padx=(8, 1))
rm_entry = ttk.Entry(capm_lbframe, textvariable=rm, width=7, font=("微软雅黑", 10))
rm_entry.grid(row=1, column=1, padx=1)
build_model_b = ttk.Button(capm_lbframe, text='CAPM定价', style="outline", state="disabled", command=capm)
build_model_b.grid(row=1, column=2, padx=5)
ttk.Separator(capm_lbframe).grid(row=2, column=0, columnspan=3, sticky='EW', pady=5, padx=(4, 0))
capm_output = ttk.Entry(capm_lbframe, textvariable=capm_out_str, width=33, font=("微软雅黑", 10), state='readonly')
capm_output.grid(row=3, column=0, columnspan=3, padx=(7, 0))

# 深色模式
table_list = [profile_table, indicator_table, table_desc]
for table in table_list:
    table.cellbackgr = '#373737'
    table.textcolor = "#ececec"
    table.rowselectedcolor = '#707070'
    table.rowheaderbgcolor = '#707070'
    table.font = ('Arial', 8)
    table.zoomIn()
    table.zoomOut()
    table.zoomOut()
    table.zoomOut()
    table.show()
profile_table.setRowHeight(24)
indicator_table.setRowHeight(24)


root.mainloop()