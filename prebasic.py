import numpy as np
import pandas as pd
import tushare as ts
import mplfinance as mpf
import matplotlib.pyplot as plt
import talib as ta

def set_tu_token(token):
    global pro
    ts.set_token(token)
    pro = ts.pro_api()

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
    boll_data['buy_signal'] = boll_data.query('Close > lower and close_lag1 < lower_lag1')['Low'] * 0.995
    boll_data['sell_signal'] = boll_data.query('Close < upper and close_lag1 > upper_lag1')['High'] * 1.005
    return boll_data['buy_signal'], boll_data['sell_signal']

class Stock:
    def __init__(self, code, name, industry, start_date, end_date):
        self.code = code
        self.name = name
        self.industry = industry
        self.title = f'{self.name}({self.code}) — {self.industry}'
        self.start_date = start_date
        self.end_date = end_date

        self.profile = pd.DataFrame()
        self.his_df = pd.DataFrame()
        self.describe_data = pd.DataFrame()
        self.al_statement = pd.DataFrame()
        self.cf_statement = pd.DataFrame()
        self.profit_statement = pd.DataFrame()
        self.fin_indicators = pd.DataFrame()
        self.val_indicators = pd.DataFrame()
        self.express = pd.DataFrame()
        self.dividend = pd.DataFrame()

        # ── 回测结果缓存 ──────────────────────────────────────
        self.bt_result: 'Optional[BacktestResult]' = None
        self.bt_params: dict = {}          # 下单模式/止损止盈等参数
        self.bt_trades_df: pd.DataFrame = pd.DataFrame()   # 合并格式交易记录
        self.bt_has_figure: bool = False   # 是否有回测图数据

    def grab_profile_data(self):
        self.profile = pro.stock_company(ts_code=self.code, fields='ts_code,com_name,com_id,exchange,chairman,manager,'
                                                                   'secretary,reg_capital,setup_date,province,city,'
                                                                   'website,email,office,employees,main_business,business_scope')
        self.profile.columns = ['股票代码','公司全称','统一社会信用代码','交易所代码','法人代表','总经理','董秘','注册资本(万元)',
                                '注册日期','所在省份','所在城市','公司主页','电子邮件','办公室','员工人数','主要业务及产品','经营范围']

    def grab_history_data(self, fq, freq):
        if freq == 'D':
            self.his_df = ts.pro_bar(ts_code=self.code, adj=fq, freq=freq, start_date=self.start_date, end_date=self.end_date,
                                  fields='trade_date, open, high, low, close, vol, amount, pct_chg')
        else:
            self.his_df = ts.pro_bar(ts_code=self.code, freq=freq, start_date=self.start_date, end_date=self.end_date,
                                  fields='trade_date, open, high, low, close, vol, amount, pct_chg')

        self.his_df.columns = ['date', 'open', 'high', 'low', 'close', 'vol', 'amount', 'pct_chg']
        self.his_df['date'] = pd.to_datetime(self.his_df['date'], format='%Y%m%d')
        self.his_df = self.his_df.sort_values('date')
        self.his_df['log_return'] = np.log(self.his_df['close'] / self.his_df['close'].shift(1))
        self.his_df["RSI"] = ta.RSI(self.his_df['close'], timeperiod=12)
        self.his_df["MOM(5 days)"] = ta.MOM(self.his_df['close'], timeperiod=5)
        self.his_df["MA(5 days)"] = self.his_df['close'].rolling(5).mean()
        self.his_df["MA(10 days)"] = self.his_df['close'].rolling(10).mean()
        self.his_df["MA(20 days)"] = self.his_df['close'].rolling(20).mean()

        self.describe_data = self.his_df.describe()

    def grab_al_data(self):
        self.al_statement = pro.balancesheet(ts_code=self.code, start_date=self.start_date, end_date=self.end_date,
                                             fields='ts_code,ann_date,f_ann_date,end_date,report_type,comp_type,end_type,'
                                                    'total_share,cap_rese,undistr_porfit,surplus_rese,special_rese,money_cap,'
                                                    'trad_asset,notes_receiv,accounts_receiv,oth_receiv,prepayment,div_receiv,'
                                                    'int_receiv,inventories,amor_exp,nca_within_1y,sett_rsrv,loanto_oth_bank_fi,'
                                                    'premium_receiv,reinsur_receiv,reinsur_res_receiv,pur_resale_fa,oth_cur_assets,'
                                                    'total_cur_assets,fa_avail_for_sale,htm_invest,lt_eqt_invest,invest_real_estate,'
                                                    'time_deposits,oth_assets,lt_rec,fix_assets,cip,const_materials,fixed_assets_disp,'
                                                    'produc_bio_assets,oil_and_gas_assets,intan_assets,r_and_d,goodwill,lt_amor_exp,'
                                                    'defer_tax_assets,decr_in_disbur,oth_nca,total_nca,cash_reser_cb,depos_in_oth_bfi,'
                                                    'prec_metals,deriv_assets,rr_reins_une_prem,rr_reins_outstd_cla,rr_reins_lins_liab,'
                                                    'rr_reins_lthins_liab,refund_depos,ph_pledge_loans,refund_cap_depos,indep_acct_assets,'
                                                    'client_depos,client_prov,transac_seat_fee,invest_as_receiv,total_assets,lt_borr,'
                                                    'st_borr,cb_borr,depos_ib_deposits,loan_oth_bank,trading_fl,notes_payable,acct_payable,'
                                                    'adv_receipts,sold_for_repur_fa,comm_payable,payroll_payable,taxes_payable,'
                                                    'int_payable,div_payable,oth_payable,acc_exp,deferred_inc,st_bonds_payable,'
                                                    'payable_to_reinsurer,rsrv_insur_cont,acting_trading_sec,acting_uw_sec,'
                                                    'non_cur_liab_due_1y,oth_cur_liab,total_cur_liab,bond_payable,lt_payable,'
                                                    'specific_payables,estimated_liab,defer_tax_liab,defer_inc_non_cur_liab,'
                                                    'oth_ncl,total_ncl,depos_oth_bfi,deriv_liab,depos,agency_bus_liab,oth_liab,'
                                                    'prem_receiv_adva,depos_received,ph_invest,reser_une_prem,reser_outstd_claims,'
                                                    'reser_lins_liab,reser_lthins_liab,indept_acc_liab,pledge_borr,indem_payable,'
                                                    'policy_div_payable,total_liab,treasury_share,ordin_risk_reser,forex_differ,'
                                                    'invest_loss_unconf,minority_int,total_hldr_eqy_exc_min_int,total_hldr_eqy_inc_min_int,'
                                                    'total_liab_hldr_eqy,lt_payroll_payable,oth_comp_income,oth_eqt_tools,'
                                                    'oth_eqt_tools_p_shr,lending_funds,acc_receivable,st_fin_payable,payables,hfs_assets,'
                                                    'hfs_sales,cost_fin_assets,fair_value_fin_assets,cip_total,oth_pay_total,'
                                                    'long_pay_total,debt_invest,oth_debt_invest,oth_eq_invest,oth_illiq_fin_assets,'
                                                    'oth_eq_ppbond,receiv_financing,use_right_assets,lease_liab,contract_assets,'
                                                    'contract_liab,accounts_receiv_bill,accounts_pay,oth_rcv_total,fix_assets_total,update_flag')
        self.al_statement.columns = ['股票代码','公告日期','实际公告日期','报告期','报表类型','公司类型(1一般工商业2银行3保险4证券)','报告期类型',
                                     '期末总股本','资本公积金','未分配利润','盈余公积金','专项储备','货币资金','交易性金融资产','应收票据',
                                     '应收账款','其他应收款','预付款项','应收股利','应收利息','存货','待摊费用','一年内到期的非流动资产','结算备付金',
                                     '拆出资金','应收保费','应收分保账款','应收分保合同准备金','买入返售金融资产','其他流动资产','流动资产合计',
                                     '可供出售金融资产','持有至到期投资','长期股权投资','投资性房地产','定期存款','其他资产','长期应收款',
                                     '固定资产','在建工程','工程物资','固定资产清理','生产性生物资产','油气资产','无形资产','研发支出',
                                     '商誉','长期待摊费用','递延所得税资产','发放贷款及垫款','其他非流动资产','非流动资产合计',
                                     '现金及存放中央银行款项','存放同业和其它金融机构款项','贵金属','衍生金融资产','应收分保未到期责任准备金',
                                     '应收分保未决赔款准备金','应收分保寿险责任准备金','应收分保长期健康险责任准备金','存出保证金','保户质押贷款',
                                     '存出资本保证金','独立账户资产','其中：客户资金存款','其中：客户备付金','其中:交易席位费','应收款项类投资',
                                     '资产总计','长期借款','短期借款','向中央银行借款','吸收存款及同业存放','拆入资金','交易性金融负债',
                                     '应付票据','应付账款','预收款项','卖出回购金融资产款','应付手续费及佣金','应付职工薪酬','应交税费',
                                     '应付利息','应付股利','其他应付款','预提费用','递延收益','应付短期债券','应付分保账款','保险合同准备金',
                                     '代理买卖证券款','代理承销证券款','一年内到期的非流动负债','其他流动负债','流动负债合计','应付债券',
                                     '长期应付款','专项应付款','预计负债','递延所得税负债','递延收益-非流动负债','其他非流动负债',
                                     '非流动负债合计','同业和其它金融机构存放款项','衍生金融负债','吸收存款','代理业务负债','其他负债',
                                     '预收保费','存入保证金','保户储金及投资款','未到期责任准备金','未决赔款准备金','寿险责任准备金',
                                     '长期健康险责任准备金','独立账户负债','其中:质押借款','应付赔付款','应付保单红利','负债合计','减:库存股',
                                     '一般风险准备','外币报表折算差额','未确认的投资损失','少数股东权益', '股东权益合计(不含少数股东权益)',
                                     '股东权益合计(含少数股东权益)', '负债及股东权益总计','长期应付职工薪酬', '其他综合收益', '其他权益工具',
                                     '其他权益工具(优先股)', '融出资金', '应收款项','应付短期融资款', '应付款项', '持有待售的资产',
                                     '持有待售的负债', '以摊余成本计量的金融资产','以公允价值计量且其变动计入其他综合收益的金融资产',
                                     '在建工程(合计)(元)', '其他应付款(合计)(元)','长期应付款(合计)(元)', '债权投资(元)', '其他债权投资(元)',
                                     '其他权益工具投资(元)','其他非流动金融资产(元)', '其他权益工具:永续债(元)', '应收款项融资','使用权资产',
                                     '租赁负债','合同资产', '合同负债', '应收票据及应收账款', '应付票据及应付账款', '其他应收款(合计)(元)',
                                     '固定资产(合计)(元)', '更新标识']

    def grab_profit_data(self):
        self.profit_statement = pro.income(ts_code=self.code, start_date=self.start_date, end_date=self.end_date,
                                           fields='ts_code,ann_date,f_ann_date,end_date,report_type,comp_type,end_type,'
                                                 'basic_eps,diluted_eps,total_revenue,revenue,int_income,prem_earned,'
                                                 'comm_income,n_commis_income,n_oth_income,n_oth_b_income,prem_income,'
                                                 'out_prem,une_prem_reser,reins_income,n_sec_tb_income,n_sec_uw_income,'
                                                 'n_asset_mg_income,oth_b_income,fv_value_chg_gain,invest_income,'
                                                 'ass_invest_income,forex_gain,total_cogs,oper_cost,int_exp,comm_exp,biz_tax_surchg,'
                                                 'sell_exp,admin_exp,fin_exp,assets_impair_loss,prem_refund,compens_payout,'
                                                 'reser_insur_liab,div_payt,reins_exp,oper_exp,compens_payout_refu,insur_reser_refu,'
                                                 'reins_cost_refund,other_bus_cost,operate_profit,non_oper_income,non_oper_exp,'
                                                 'nca_disploss,total_profit,income_tax,n_income,n_income_attr_p,minority_gain,'
                                                 'oth_compr_income,t_compr_income,compr_inc_attr_p,compr_inc_attr_m_s,ebit,'
                                                 'ebitda,insurance_exp,undist_profit,distable_profit,rd_exp,fin_exp_int_exp,'
                                                 'fin_exp_int_inc,transfer_surplus_rese,transfer_housing_imprest,transfer_oth,'
                                                 'adj_lossgain,withdra_legal_surplus,withdra_legal_pubfund,withdra_biz_devfund,'
                                                 'withdra_rese_fund,withdra_oth_ersu,workers_welfare,distr_profit_shrhder,'
                                                 'prfshare_payable_dvd,comshare_payable_dvd,capit_comstock_div,net_after_nr_lp_correct,'
                                                 'credit_impa_loss,net_expo_hedging_benefits,oth_impair_loss_assets,'
                                                 'total_opcost,amodcost_fin_assets,oth_income,asset_disp_income,continued_net_profit,'
                                                 'end_net_profit,update_flag')
        self.profit_statement.columns = ['TS代码','公告日期','实际公告日期','报告期','报告类型 见底部表','公司类型(1一般工商业2银行3保险4证券)',
                                         '报告期类型','基本每股收益','稀释每股收益','营业总收入','营业收入','利息收入','已赚保费','手续费及佣金收入',
                                         '手续费及佣金净收入','其他经营净收益','加:其他业务净收益','保险业务收入','减:分出保费','提取未到期责任准备金',
                                         '其中:分保费收入','代理买卖证券业务净收入','证券承销业务净收入','受托客户资产管理业务净收入','其他业务收入',
                                         '加:公允价值变动净收益','加:投资净收益','其中:对联营企业和合营企业的投资收益','加:汇兑净收益','营业总成本',
                                         '减:营业成本','减:利息支出','减:手续费及佣金支出','减:营业税金及附加','减:销售费用','减:管理费用','减:财务费用',
                                         '减:资产减值损失','退保金','赔付总支出','提取保险责任准备金','保户红利支出','分保费用','营业支出',
                                         '减:摊回赔付支出','减:摊回保险责任准备金','减:摊回分保费用','其他业务成本','营业利润','加:营业外收入',
                                         '减:营业外支出','其中:减:非流动资产处置净损失','利润总额','所得税费用','净利润(含少数股东损益)',
                                         '净利润(不含少数股东损益)','少数股东损益','其他综合收益','综合收益总额','归属于母公司(或股东)的综合收益总额',
                                         '归属于少数股东的综合收益总额','息税前利润','息税折旧摊销前利润','保险业务支出','年初未分配利润',
                                         '可分配利润','研发费用','财务费用:利息费用','财务费用:利息收入','盈余公积转入','住房周转金转入',
                                         '其他转入','调整以前年度损益','提取法定盈余公积','提取法定公益金','提取企业发展基金','提取储备基金',
                                         '提取任意盈余公积金','职工奖金福利','可供股东分配的利润','应付优先股股利','应付普通股股利',
                                         '转作股本的普通股股利','扣除非经常性损益后的净利润（更正前）','信用减值损失','净敞口套期收益',
                                         '其他资产减值损失','营业总成本（二）','以摊余成本计量的金融资产终止确认收益','其他收益','资产处置收益',
                                         '持续经营净利润','终止经营净利润','更新标识']

    def grab_cf_data(self):
        self.cf_statement = pro.cashflow(ts_code=self.code, start_date=self.start_date, end_date=self.end_date,
                                         fields='ts_code,ann_date,f_ann_date,end_date,comp_type,report_type,end_type,net_profit,'
                                               'finan_exp,c_fr_sale_sg,recp_tax_rends,n_depos_incr_fi,n_incr_loans_cb,'
                                               'n_inc_borr_oth_fi,prem_fr_orig_contr,n_incr_insured_dep,n_reinsur_prem,'
                                               'n_incr_disp_tfa,ifc_cash_incr,n_incr_disp_faas,n_incr_loans_oth_bank,'
                                               'n_cap_incr_repur,c_fr_oth_operate_a,c_inf_fr_operate_a,c_paid_goods_s,'
                                               'c_paid_to_for_empl,c_paid_for_taxes,n_incr_clt_loan_adv,n_incr_dep_cbob,'
                                               'c_pay_claims_orig_inco,pay_handling_chrg,pay_comm_insur_plcy,oth_cash_pay_oper_act,'
                                               'st_cash_out_act,n_cashflow_act,oth_recp_ral_inv_act,c_disp_withdrwl_invest,'
                                               'c_recp_return_invest,n_recp_disp_fiolta,n_recp_disp_sobu,stot_inflows_inv_act,'
                                               'c_pay_acq_const_fiolta,c_paid_invest,n_disp_subs_oth_biz,oth_pay_ral_inv_act,'
                                               'n_incr_pledge_loan,stot_out_inv_act,n_cashflow_inv_act,c_recp_borrow,proc_issue_bonds,'
                                               'oth_cash_recp_ral_fnc_act,stot_cash_in_fnc_act,free_cashflow,c_prepay_amt_borr,'
                                               'c_pay_dist_dpcp_int_exp,incl_dvd_profit_paid_sc_ms,oth_cashpay_ral_fnc_act,'
                                               'stot_cashout_fnc_act,n_cash_flows_fnc_act,eff_fx_flu_cash,n_incr_cash_cash_equ,'
                                               'c_cash_equ_beg_period,c_cash_equ_end_period,c_recp_cap_contrib,incl_cash_rec_saims,'
                                               'uncon_invest_loss,prov_depr_assets,depr_fa_coga_dpba,amort_intang_assets,'
                                               'lt_amort_deferred_exp,decr_deferred_exp,incr_acc_exp,loss_disp_fiolta,loss_scr_fa,'
                                               'loss_fv_chg,invest_loss,decr_def_inc_tax_assets,incr_def_inc_tax_liab,decr_inventories,'
                                               'decr_oper_payable,incr_oper_payable,others,im_net_cashflow_oper_act,conv_debt_into_cap,'
                                               'conv_copbonds_due_within_1y,fa_fnc_leases,im_n_incr_cash_equ,net_dism_capital_add,'
                                               'net_cash_rece_sec,credit_impa_loss,use_right_asset_dep,oth_loss_asset,end_bal_cash,'
                                               'beg_bal_cash,end_bal_cash_equ,beg_bal_cash_equ,update_flag')
        self.cf_statement.columns = ['TS股票代码','公告日期','实际公告日期','报告期','公司类型(1一般工商业2银行3保险4证券)','报表类型',
                                     '报告期类型','净利润','财务费用','销售商品、提供劳务收到的现金','收到的税费返还','客户存款和同业存放款项净增加额',
                                     '向中央银行借款净增加额','向其他金融机构拆入资金净增加额','收到原保险合同保费取得的现金','保户储金净增加额',
                                     '收到再保业务现金净额','处置交易性金融资产净增加额','收取利息和手续费净增加额','处置可供出售金融资产净增加额',
                                     '拆入资金净增加额','回购业务资金净增加额','收到其他与经营活动有关的现金','经营活动现金流入小计',
                                     '购买商品、接受劳务支付的现金','支付给职工以及为职工支付的现金','支付的各项税费','客户贷款及垫款净增加额',
                                     '存放央行和同业款项净增加额','支付原保险合同赔付款项的现金','支付手续费的现金','支付保单红利的现金',
                                     '支付其他与经营活动有关的现金','经营活动现金流出小计','经营活动产生的现金流量净额','收到其他与投资活动有关的现金',
                                     '收回投资收到的现金','取得投资收益收到的现金','处置固定资产、无形资产和其他长期资产收回的现金净额',
                                     '处置子公司及其他营业单位收到的现金净额','投资活动现金流入小计','购建固定资产、无形资产和其他长期资产支付的现金',
                                     '投资支付的现金','取得子公司及其他营业单位支付的现金净额','支付其他与投资活动有关的现金','质押贷款净增加额',
                                     '投资活动现金流出小计','投资活动产生的现金流量净额','取得借款收到的现金','发行债券收到的现金',
                                     '收到其他与筹资活动有关的现金','筹资活动现金流入小计','企业自由现金流量','偿还债务支付的现金',
                                     '分配股利、利润或偿付利息支付的现金','其中:子公司支付给少数股东的股利、利润','支付其他与筹资活动有关的现金',
                                     '筹资活动现金流出小计','筹资活动产生的现金流量净额','汇率变动对现金的影响','现金及现金等价物净增加额',
                                     '期初现金及现金等价物余额','期末现金及现金等价物余额','吸收投资收到的现金','其中:子公司吸收少数股东投资收到的现金',
                                     '未确认投资损失','加:资产减值准备','固定资产折旧、油气资产折耗、生产性生物资产折旧','无形资产摊销',
                                     '长期待摊费用摊销','待摊费用减少','预提费用增加','处置固定、无形资产和其他长期资产的损失','固定资产报废损失',
                                     '公允价值变动损失','投资损失','递延所得税资产减少','递延所得税负债增加','存货的减少','经营性应收项目的减少',
                                     '经营性应付项目的增加','其他','经营活动产生的现金流量净额(间接法)','债务转为资本','一年内到期的可转换公司债券',
                                     '融资租入固定资产','现金及现金等价物净增加额(间接法)','拆出资金净增加额','代理买卖证券收到的现金净额(元)',
                                     '信用减值损失','使用权资产折旧','其他资产减值损失','现金的期末余额','减:现金的期初余额','加:现金等价物的期末余额',
                                     '减:现金等价物的期初余额','更新标志']

    def grab_fin_indicators_data(self):
        self.fin_indicators = pro.fina_indicator(ts_code=self.code, start_date=self.start_date, end_date=self.end_date,
                                                 fields='ts_code,ann_date,end_date,eps,dt_eps,total_revenue_ps,revenue_ps,'
                                                       'capital_rese_ps,surplus_rese_ps,undist_profit_ps,extra_item,profit_dedt,'
                                                       'gross_margin,current_ratio,quick_ratio,cash_ratio,invturn_days,arturn_days,'
                                                       'inv_turn,ar_turn,ca_turn,fa_turn,assets_turn,op_income,valuechange_income,'
                                                       'interst_income,daa,ebit,ebitda,fcff,fcfe,current_exint,noncurrent_exint,'
                                                       'interestdebt,netdebt,tangible_asset,working_capital,networking_capital,'
                                                       'invest_capital,retained_earnings,diluted2_eps,bps,ocfps,retainedps,cfps,'
                                                       'ebit_ps,fcff_ps,fcfe_ps,netprofit_margin,grossprofit_margin,cogs_of_sales,'
                                                       'expense_of_sales,profit_to_gr,saleexp_to_gr,adminexp_of_gr,finaexp_of_gr,'
                                                       'impai_ttm,gc_of_gr,op_of_gr,ebit_of_gr,roe,roe_waa,roe_dt,roa,npta,roic,'
                                                       'roe_yearly,roa2_yearly,roe_avg,opincome_of_ebt,investincome_of_ebt,'
                                                       'n_op_profit_of_ebt,tax_to_ebt,dtprofit_to_profit,salescash_to_or,'
                                                       'ocf_to_or,ocf_to_opincome,capitalized_to_da,debt_to_assets,assets_to_eqt,'
                                                       'dp_assets_to_eqt,ca_to_assets,nca_to_assets,tbassets_to_totalassets,'
                                                       'int_to_talcap,eqt_to_talcapital,currentdebt_to_debt,longdeb_to_debt,'
                                                       'ocf_to_shortdebt,debt_to_eqt,eqt_to_debt,eqt_to_interestdebt,tangibleasset_to_debt,'
                                                       'tangasset_to_intdebt,tangibleasset_to_netdebt,ocf_to_debt,ocf_to_interestdebt,'
                                                       'ocf_to_netdebt,ebit_to_interest,longdebt_to_workingcapital,ebitda_to_debt,'
                                                       'turn_days,roa_yearly,roa_dp,fixed_assets,profit_prefin_exp,non_op_profit,'
                                                       'op_to_ebt,nop_to_ebt,ocf_to_profit,cash_to_liqdebt,cash_to_liqdebt_withinterest,'
                                                       'op_to_liqdebt,op_to_debt,roic_yearly,total_fa_trun,profit_to_op,q_opincome,'
                                                       'q_investincome,q_dtprofit,q_eps,q_netprofit_margin,q_gsprofit_margin,'
                                                       'q_exp_to_sales,q_profit_to_gr,q_saleexp_to_gr,q_adminexp_to_gr,q_finaexp_to_gr,'
                                                       'q_impair_to_gr_ttm,q_gc_to_gr,q_op_to_gr,q_roe,q_dt_roe,q_npta,q_opincome_to_ebt,'
                                                       'q_investincome_to_ebt,q_dtprofit_to_profit,q_salescash_to_or,q_ocf_to_sales,'
                                                       'q_ocf_to_or,basic_eps_yoy,dt_eps_yoy,cfps_yoy,op_yoy,ebt_yoy,netprofit_yoy,'
                                                       'dt_netprofit_yoy,ocf_yoy,roe_yoy,bps_yoy,assets_yoy,eqt_yoy,tr_yoy,or_yoy,'
                                                       'q_gr_yoy,q_gr_qoq,q_sales_yoy,q_sales_qoq,q_op_yoy,q_op_qoq,q_profit_yoy,'
                                                       'q_profit_qoq,q_netprofit_yoy,q_netprofit_qoq,equity_yoy,rd_exp,update_flag')
        self.fin_indicators.columns = ['TS代码','公告日期','报告期','基本每股收益','稀释每股收益','每股营业总收入','每股营业收入','每股资本公积',
                                       '每股盈余公积','每股未分配利润','非经常性损益','扣除非经常性损益后的净利润（扣非净利润）','毛利','流动比率',
                                       '速动比率','保守速动比率','存货周转天数','应收账款周转天数','存货周转率','应收账款周转率','流动资产周转率',
                                       '固定资产周转率','总资产周转率','经营活动净收益','价值变动净收益','利息费用','折旧与摊销','息税前利润',
                                       '息税折旧摊销前利润','企业自由现金流量','股权自由现金流量','无息流动负债','无息非流动负债','带息债务',
                                       '净债务','有形资产','营运资金','营运流动资本','全部投入资本','留存收益','期末摊薄每股收益','每股净资产',
                                       '每股经营活动产生的现金流量净额','每股留存收益','每股现金流量净额','每股息税前利润','每股企业自由现金流量',
                                       '每股股东自由现金流量','销售净利率','销售毛利率','销售成本率','销售期间费用率','净利润/营业总收入',
                                       '销售费用/营业总收入','管理费用/营业总收入','财务费用/营业总收入','资产减值损失/营业总收入','营业总成本/营业总收入',
                                       '营业利润/营业总收入','息税前利润/营业总收入','净资产收益率','加权平均净资产收益率','净资产收益率(扣除非经常损益)',
                                       '总资产报酬率','总资产净利润','投入资本回报率','年化净资产收益率','年化总资产报酬率','平均净资产收益率(增发条件)',
                                       '经营活动净收益/利润总额','价值变动净收益/利润总额','营业外收支净额/利润总额','所得税/利润总额',
                                       '扣除非经常损益后的净利润/净利润','销售商品提供劳务收到的现金/营业收入','经营活动产生的现金流量净额/营业收入',
                                       '经营活动产生的现金流量净额/经营活动净收益','资本支出/折旧和摊销','资产负债率','权益乘数','权益乘数(杜邦分析)',
                                       '流动资产/总资产','非流动资产/总资产','有形资产/总资产','带息债务/全部投入资本','归属于母公司的股东权益/全部投入资本',
                                       '流动负债/负债合计','非流动负债/负债合计','经营活动产生的现金流量净额/流动负债','产权比率','归属于母公司的股东权益/负债合计',
                                       '归属于母公司的股东权益/带息债务','有形资产/负债合计','有形资产/带息债务','有形资产/净债务','经营活动产生的现金流量净额/负债合计',
                                       '经营活动产生的现金流量净额/带息债务','经营活动产生的现金流量净额/净债务','已获利息倍数(EBIT/利息费用)',
                                       '长期债务与营运资金比率','息税折旧摊销前利润/负债合计','营业周期','年化总资产净利率','总资产净利率(杜邦分析)',
                                       '固定资产合计','扣除财务费用前营业利润','非营业利润','营业利润／利润总额','非营业利润／利润总额',
                                       '经营活动产生的现金流量净额／营业利润','货币资金／流动负债','货币资金／带息流动负债','营业利润／流动负债',
                                       '营业利润／负债合计','年化投入资本回报率','固定资产合计周转率','利润总额／营业收入','经营活动单季度净收益',
                                       '价值变动单季度净收益','扣除非经常损益后的单季度净利润','每股收益(单季度)','销售净利率(单季度)',
                                       '销售毛利率(单季度)','销售期间费用率(单季度)','净利润／营业总收入(单季度)','销售费用／营业总收入 (单季度)',
                                       '管理费用／营业总收入 (单季度)','财务费用／营业总收入 (单季度)','资产减值损失／营业总收入(单季度)',
                                       '营业总成本／营业总收入 (单季度)','营业利润／营业总收入(单季度)','净资产收益率(单季度)','净资产单季度收益率(扣除非经常损益)',
                                       '总资产净利润(单季度)','经营活动净收益／利润总额(单季度)','价值变动净收益／利润总额(单季度)','扣除非经常损益后的净利润／净利润(单季度)',
                                       '销售商品提供劳务收到的现金／营业收入(单季度)','经营活动产生的现金流量净额／营业收入(单季度)',
                                       '经营活动产生的现金流量净额／经营活动净收益(单季度)','基本每股收益同比增长率(%)','稀释每股收益同比增长率(%)',
                                       '每股经营活动产生的现金流量净额同比增长率(%)','营业利润同比增长率(%)','利润总额同比增长率(%)',
                                       '归属母公司股东的净利润同比增长率(%)','归属母公司股东的净利润-扣除非经常损益同比增长率(%)','经营活动产生的现金流量净额同比增长率(%)',
                                       '净资产收益率(摊薄)同比增长率(%)','每股净资产相对年初增长率(%)','资产总计相对年初增长率(%)','归属母公司的股东权益相对年初增长率(%)',
                                       '营业总收入同比增长率(%)','营业收入同比增长率(%)','营业总收入同比增长率(%)(单季度)','营业总收入环比增长率(%)(单季度)',
                                       '营业收入同比增长率(%)(单季度)','营业收入环比增长率(%)(单季度)','营业利润同比增长率(%)(单季度)',
                                       '营业利润环比增长率(%)(单季度)','净利润同比增长率(%)(单季度)','净利润环比增长率(%)(单季度)',
                                       '归属母公司股东的净利润同比增长率(%)(单季度)','归属母公司股东的净利润环比增长率(%)(单季度)','净资产同比增长率','研发费用','更新标识']

    def grab_val_indicators_data(self):
        self.val_indicators = pro.daily_basic(ts_code=self.code, start_date=self.start_date, end_date=self.end_date,
                                              fields='ts_code,trade_date,close,turnover_rate,turnover_rate_f,volume_ratio,'
                                                     'pe,pe_ttm,pb,ps,ps_ttm,dv_ratio,dv_ttm,total_share,float_share,free_share,total_mv,circ_mv')
        self.val_indicators.columns = ['TS股票代码','交易日期','当日收盘价','换手率（%）','换手率（自由流通股）','量比','市盈率（总市值/净利润， 亏损的PE为空）',
                                       '市盈率（TTM，亏损的PE为空）','市净率（总市值/净资产）','市销率','市销率（TTM）','股息率 （%）','股息率（TTM）（%）',
                                       '总股本 （万股）','流通股本 （万股）','自由流通股本 （万）','总市值 （万元）','流通市值（万元）']

    def grab_express_data(self):
        self.express = pro.express(ts_code=self.code, start_date=self.start_date, end_date=self.end_date,
                                   fields='ts_code,ann_date,end_date,revenue,operate_profit,total_profit,n_income,total_assets,'
                                          'total_hldr_eqy_exc_min_int,diluted_eps,diluted_roe,yoy_net_profit,bps,yoy_sales,yoy_op,'
                                          'yoy_tp,yoy_dedu_np,yoy_eps,yoy_roe,growth_assets,yoy_equity,growth_bps,or_last_year,'
                                          'op_last_year,tp_last_year,np_last_year,eps_last_year,open_net_assets,open_bps,'
                                          'perf_summary,is_audit,remark')
        self.express.columns = ['TS股票代码','公告日期','报告期','营业收入(元)','营业利润(元)','利润总额(元)','净利润(元)','总资产(元)',
                                '股东权益合计(不含少数股东权益)(元)','每股收益(摊薄)(元)','净资产收益率(摊薄)(%)','去年同期修正后净利润',
                                '每股净资产','同比增长率:营业收入','同比增长率:营业利润','同比增长率:利润总额','同比增长率:归属母公司股东的净利润',
                                '同比增长率:基本每股收益','同比增减:加权平均净资产收益率','比年初增长率:总资产','比年初增长率:归属母公司的股东权益',
                                '比年初增长率:归属于母公司股东的每股净资产','去年同期营业收入','去年同期营业利润','去年同期利润总额','去年同期净利润',
                                '去年同期每股收益','期初净资产','期初每股净资产','业绩简要说明','是否审计：(1是 0否)','备注']

    def grab_dividend_data(self):
        self.dividend = pro.dividend(ts_code=self.code,fields='ts_code,end_date,ann_date,div_proc,stk_div,stk_bo_rate,stk_co_rate,cash_div,'
                                            'cash_div_tax,record_date,ex_date,pay_date,div_listdate,imp_ann_date,base_date,base_share')
        self.dividend.columns = ['TS代码','分红年度','预案公告日','实施进度','每股送转','每股送股比例','每股转增比例','每股分红（税后）',
                                 '每股分红（税前）','股权登记日','除权除息日','派息日','红股上市日','实施公告日','基准日','基准股本（万）']

    def plot_k_line(self):
        plt.rcParams["font.sans-serif"] = ["Microsoft YaHei"]  # 设置字体
        plt.rcParams["axes.unicode_minus"] = False  # 该语句解决图像中的“-”负号的乱码问题

        data_for_plot = self.his_df.set_index('date')[['open', 'high', 'low', 'close', 'vol']]
        data_for_plot.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        data_for_plot.index = pd.to_datetime(data_for_plot.index)
        # 绘制K线图
        mc = mpf.make_marketcolors(up='#f34334', down='#21be87', volume='inherit')
        s = mpf.make_mpf_style(marketcolors=mc, y_on_right=False, gridaxis='horizontal', facecolor='#c9c9c9',
                               figcolor='#888888')

        exp12, exp26, histogram, signal, macd = macd_func(data_for_plot)
        buy_signal, sell_signal = boll_signal(data_for_plot, 20, 2)
        add_plot = [mpf.make_addplot(histogram, type='bar', width=0.7, panel=2, color='dimgray', secondary_y=False),
                    mpf.make_addplot(macd, panel=2, color='fuchsia', secondary_y=True),
                    mpf.make_addplot(signal, panel=2, color='b', secondary_y=True),
                    mpf.make_addplot(buy_signal, type='scatter', markersize=45, marker='^', color='r'),
                    mpf.make_addplot(sell_signal, type='scatter', markersize=45, marker='v', color='g')]

        mpf.plot(data_for_plot, type='candle', volume=True, title={"title": str(self.code), "y": 1}, addplot=add_plot,
                 panel_ratios=(7, 2, 2),
                 ylabel='Price', ylabel_lower='Volume', mav=(5, 10, 30), style=s, figscale=1.5, tight_layout=True)

        plt.rcParams["font.sans-serif"] = ["Microsoft YaHei"]  # 设置字体
        plt.rcParams["axes.unicode_minus"] = False  # 该语句解决图像中的“-”负号的乱码问题

    def get_stock_data(self, fq, freq):
        self.grab_profile_data()
        self.grab_history_data(fq, freq)
        self.grab_dividend_data()
        self.grab_al_data()
        self.grab_cf_data()
        self.grab_profit_data()
        self.grab_express_data()
        self.grab_fin_indicators_data()
        self.grab_val_indicators_data()

    # ──────────────────────────────────────────────────────────
    # 回测结果持久化 & 绘图（供 main.py 调用）
    # ──────────────────────────────────────────────────────────
    def save_bt_data(self, res, trades_df, params, outcome_text_func=None):
        """
        将回测结果写入股票实例，供后续切回该股票时恢复显示。

        参数
        ----
        res         : bt_module.BacktestResult
        trades_df   : pd.DataFrame，合并格式交易记录（来自 result_to_trade_df）
        params      : dict，简单策略参数（stake_mode / stop_loss / take_profit 等）
        outcome_text_func : 可选，回调函数，用来把指标文本写入 Outcome 文本框
        """
        import bt_module
        self.bt_result = res
        self.bt_trades_df = trades_df
        self.bt_params = params
        self.bt_has_figure = res.ok and bool(res.trades)

        # 若提供了回调，同步更新右侧 Outcome 文本框
        if callable(outcome_text_func) and res.ok:
            outcome_text_func(bt_module.format_result_text(res))

    def render_bt_canvas(self, ax, canvas, x_min, x_max, y_min, y_max):
        """
        将该股票实例中缓存的回测结果重新绘制到指定 Axes。

        流程：清空 Axes → 画价格线 → 画买卖点/持仓区间阴影。
        需在 main.py 中传入 globals() 里的 bt_ax / bt_canvas_draw / 全局坐标范围。

        若无回测缓存（bt_has_figure=False），则仅重绘价格线。
        """
        import pandas as pd
        import matplotlib.dates as mdates

        ax.clear()

        if self.his_df is None or self.his_df.empty:
            return ax, canvas

        df = self.his_df.copy()
        ax.plot(df['date'], df['close'], color='#3a7bd5', linewidth=1.5,
                label=f'收盘价（{self.name}）')
        price_by_date = df.set_index('date')['close']

        if not self.bt_has_figure or not self.bt_result or not self.bt_result.trades:
            # 无回测图：只画价格线，自动适配坐标
            x_min_val = mdates.date2num(df['date'].min()) - 10
            x_max_val = mdates.date2num(df['date'].max()) + 10
            y_min_val = df['close'].min() * 0.97
            y_max_val = df['close'].max() * 1.03
            ax.set_xlim(x_min_val, x_max_val)
            ax.set_ylim(y_min_val, y_max_val)
        else:
            # 有回测图：画买卖点 + 持仓区间
            buy_x, buy_y, sell_x, sell_y = [], [], [], []
            for t in self.bt_result.trades:
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

            # 配对：按时间顺序买入→卖出
            paired = []
            buys = sorted(zip(buy_x, buy_y))
            sells = sorted(zip(sell_x, sell_y))
            bi, si = 0, 0
            in_pos = False
            while bi < len(buys) or si < len(sells):
                if not in_pos:
                    if bi < len(buys):
                        cur = buys[bi]
                        bi += 1
                        in_pos = True
                    else:
                        break
                else:
                    if si < len(sells):
                        paired.append((cur, sells[si]))
                        si += 1
                        in_pos = False
                    else:
                        break

            # 持仓区间阴影
            for (bdt, _), (sdt, _) in paired:
                ax.axvspan(bdt, sdt, alpha=0.18, color='#388df3')

            # 买入虚线（红色）
            for bx, by in zip(buy_x, buy_y):
                ax.axvline(x=bx, color='#f34334', linestyle='--', linewidth=1.0, alpha=0.7)

            # 卖出虚线（绿色）
            for sx, sy in zip(sell_x, sell_y):
                ax.axvline(x=sx, color='#21be87', linestyle='--', linewidth=1.0, alpha=0.7)

            # 坐标范围：适配买卖点
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
