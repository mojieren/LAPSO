import os
from pathlib import Path
from urllib.request import urlretrieve
from datetime import datetime, timedelta, date

def hist_site_aqi(dates, savefolder):
    # base_url = 'http://beijingair.sinaapp.com/data/china/sites/20151205/csv'
    base_url = 'https://quotsoft.net/air/data/china_sites_20151205.csv'
    for date in dates:
        savefile = savefolder.joinpath(date + ".csv")
        if savefile.exists(): continue
        url = base_url
        url = url.replace('20151205',date)
        # print(url)
        print("*********************************************")
        print(date)
        try:
            # urlretrieve(url, os.path.join(path, date + ".csv"), callbackfunc)
            urlretrieve(url, savefile, callbackfunc)
        except:
            pass
        print("*********************************************")


def cal_time(s = "19970101", e = "20030701"):
    start_date = datetime.strptime(s, "%Y%m%d")
    end_date = datetime.strptime(e, "%Y%m%d")
    delta = end_date - start_date
    dates = []
    months = []
    years = []
    for day in range(delta.days):
        step = timedelta(day)
        date_iter = datetime.strftime(start_date + step, "%Y%m%d")
        month_iter = datetime.strftime(start_date + step, "%Y%m")
        year_iter = datetime.strftime(start_date + step, "%Y")
        dates.append(date_iter)
        months.append(month_iter)
        years.append(year_iter)
    months = list(set(months))
    months.sort()
    years = list(set(years))
    years.sort()
    return dates, months, years


def callbackfunc(blocknum, blocksize, totalsize):
    '''回调函数
    @blocknum: 已经下载的数据块
    @blocksize: 数据块的大小
    @totalsize: 远程文件的大小
    '''
    percent = 100.0 * blocknum * blocksize / totalsize
    if percent > 100: percent = 100
    if percent % 10 == 0: print("%.2f%%"% percent)

folder = root_proj.joinpath("CNEMC")
print('Starting...')
today = datetime.strftime(date.today(), '%Y%m%d')
dates, _, _ = cal_time(s = '20220101', e = today)
existing = [p.stem for p in folder.glob('*.csv')]
download_dates = list(set(dates) - set(existing))
download_dates.sort()
hist_site_aqi(download_dates, folder)
print('Finished!')