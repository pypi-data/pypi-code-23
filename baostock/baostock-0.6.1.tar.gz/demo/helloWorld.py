import baostock as bs
import pandas as pd

#### 登陆系统 ####
lg = bs.login(user_id="anonymous", password="123456")
# 显示登陆返回信息
print('login respond error_code:'+lg.error_code)
print('login respond  error_msg:'+lg.error_msg)

#### 获取历史K线数据 ####
# 详细指标参数，参见“历史行情指标参数”章节
rs = bs.query_history_k_data("sh.600000",
    "date,code,open,high,low,close,volume,amount,adjustflag,peTTM,pbMRQ,psTTM,pcfNcfTTM,pctChg,isST",
    start_date='2017-01-01', end_date='2017-06-30', 
    frequency="d", adjustflag="3")
print('query_history_k_data respond error_code:'+rs.error_code)
print('query_history_k_data respond  error_msg:'+rs.error_msg)

#### 打印结果集 ####
result = pd.DataFrame(columns=["date","code","open","high","low","close","volume","amount","adjustflag","peTTM","pbMRQ","psTTM","pcfNcfTTM","pctChg","isST"])
while (rs.error_code == '0') & rs.next():
    # 分页查询，将每页信息合并在一起
    result = result.append(rs.get_row_data(), ignore_index=True)
    
#### 结果集输出到csv文件 ####   
result.to_csv("C:\\history_k_data.csv", index=False)
print(result)

#### 登出系统 ####
bs.logout()