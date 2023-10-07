"""
Created on November 22, 2018

This script is to convert LAPSO netCDF files into txt files in ASC-II format.

@author: xu_jn
"""


from pathlib import Path
import numpy as np
import pandas as pd
import xarray as xr
from datetime import datetime

def create_folder(des):
    # exist_ok = False: DO NOT make if the directory exists!
    try:
        des.mkdir(mode = 0o777, parents = True, exist_ok = False)
        print(f'Directory made: {des} ')
    except FileExistsError as e:
        print('Not creating, target directory exists!')
        # FileExistsError

        
def run(gas):
    name = gas.upper()
    print(f'Start processing nc data of {name}:')
    print('*' * 40)
    savefolder = Path(gas)
    create_folder(savefolder)
    paths = list(Path.cwd().glob(f'SUR-{name}-*.nc'))
    # ---------------------------------------------------------------------------------------------------------
    # Iterating files:
    for p in paths:
        try:
            # print(p.stem)
            nc = xr.load_dataset(p)
            # -----------------------------------------------------------------------------------------------------
            # Iterating days:
            for dt in nc.time.data:
                try:
                    print(dt)
                    dft = nc.sel(time = dt).to_dataframe()[gas].reset_index()
                    # dft = dft.pivot(columns = ['longitude'], index = ['latitude'], values = [gas])
                    # dft.columns = dft.columns.droplevel(0)
                    # dft.columns.name = None
                    # dft.index.name = None
                    # dft = dft.fillna(-9999).round(4)
                    # dft.index = np.round(dft.index, 4)
                    # dft.columns = np.round(dft.columns, 4)
                    dft = dft.round(4)
                    dft['latitude'] = dft['latitude'].round(2)
                    dft['longitude'] = dft['longitude'].round(2)
                    dft = dft.fillna('NaN')
                    dft = dft.rename(columns = {'latitude': '# Latitude', 'longitude': 'Longitude', gas: name + '(ug/m3)'})
                    # saving daily text:
                    savefile = savefolder.joinpath(f"{datetime.strftime(pd.to_datetime(dt), '%Y%m%d')}-{gas}.txt")
                    if savefile.exists(): continue

                    dft.to_csv(
                        savefile, 
                        index=None, 
                        sep='\t', 
                        mode='w'
                    )
                    print(f"{datetime.strftime(pd.to_datetime(dt), '%Y%m%d')} is done...")
                except:
                    pass
        except:
            pass
    print('All done!')
    
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('gas', type = str)
    args = parser.parse_args()
    gas = args.gas.lower()
    run(gas)
