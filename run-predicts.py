'''
Authour: Songyan Zhu and Jian Xu
Date: 03/01/2023
Contact: soonyenju@outlook.com; xujian@nssc.ac.cn
'''

import pickle
import rioxarray
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path

def load_model(p):
    with open(p, "rb") as f:
        model = pickle.load(f)
    return model

def process(target, path_save, path_model, path_S5P, path_ERA5, path_bounds):
    regr = load_model(path_model)
    # dt = pd.to_datetime(f'{year}-{month}-01', format = '%Y-%m-%d')
    era5 = xr.open_dataset(path_ERA5)
    s5p = xr.open_dataset(path_S5P)
    xds = rioxarray.open_rasterio(path_bounds)
    xds = xds.mean(dim = 'band')
    xds = xds.to_pandas()
    x_names = ['s5p', 'cc', 'crwc', 'o3', 'r', 'ssr', 'ssrd', 't', 'u', 'v', 'doy', 'year', 'season', 'longitude', 'latitude']
    dfo = []
    y_loc, x_loc = np.where(xds == 1)
    prov_lats = xds.index[y_loc].values
    prov_lons = xds.columns[x_loc].values
    prov_name = 'china'
    if len(prov_lons) | len(prov_lats) == 0: raise(Exception('Wrong'))
    
    sy = s5p[target].interp(longitude = np.unique(prov_lons), latitude = np.unique(prov_lats)).to_dataframe().rename(columns = {target: 's5p'})
    zh = era5.interp(longitude = np.unique(prov_lons), latitude = np.unique(prov_lats)).to_dataframe()

    df = pd.concat([sy, zh], axis = 1)

    pnts_tar = df.index.get_level_values(1).astype(str) + '-' + df.index.get_level_values(2).astype(str)
    pnts_ref = pd.Index(prov_lats).astype(str) + '-' + pd.Index(prov_lons).astype(str)
    df = df[pnts_tar.isin(pnts_ref)]
    df['longitude'] = df.index.get_level_values(2)
    df['latitude'] = df.index.get_level_values(1)

    df['doy'] = df.index.get_level_values(0).day_of_year
    df['year'] = df.index.get_level_values(0).year
    df["season"] = (df.index.get_level_values(0).month%12 + 3) // 3
    df = df[x_names]
    predicts = pd.DataFrame(regr.predict(df.fillna(0)), columns = [target], index = df.index)
    dfo.append(predicts)

    nco = pd.concat(dfo, axis = 0).to_xarray()
    nco.to_netcdf(path = path_save)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('target', type = str)
    parser.add_argument('path_save', type = str)
    parser.add_argument('path_model', type = str)
    parser.add_argument('path_S5P', type = str)
    parser.add_argument('path_ERA5', type = str)
    parser.add_argument('path_bounds', type = str)
    args = parser.parse_args()
    target = args.target.lower()
    path_save = Path(args.path_save)
    path_model = Path(args.path_model)
    path_S5P = Path(args.path_S5P)
    path_ERA5 = Path(args.path_ERA5)
    path_bounds = Path(args.path_bounds)
    
    process(target, path_save, path_model, path_S5P, path_ERA5, path_bounds)
