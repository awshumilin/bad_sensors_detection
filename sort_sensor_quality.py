
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import pandas as pd
import numpy as np
from nptdms import TdmsFile
from matplotlib import pyplot as plt
import seaborn as sns
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
from dams import col_list1, col_list3, col_list4, col_list5, col_list_b, col_list_b_d
# from tqdm.auto import tqdm
# from tqdm import tqdm
matplotlib.use('TkAgg')

# Function to get the difference of two lists while preserving the order
def diff(first, second):
    second = set(second)
    return [item for item in first if item not in second]

# Main function for getting a list of suspicious sensors and plotting
def sort_sensor_quality(num_points, dam_num, path):

    # Path to archive
    if path == '':
        path = "ARCHIVE/"
    else:
        path = path + '\\'

    filelist = []
    df_full = []
    col_list_ = []

    # Open files from the archive according to the number of the dam
    if dam_num == '1-2':
        for file in os.listdir(path):
            if str(file)[-4:] == 'tdms' and str(file)[:3] == 'D11':
                filelist.append(file)
        col_list = col_list1
    elif dam_num == '3':
        for file in os.listdir(path):
            if str(file)[-4:] == 'tdms' and str(file)[:3] == 'D32':
                filelist.append(file)
        col_list = col_list3
    elif dam_num == '4':
        for file in os.listdir(path):
            if str(file)[-4:] == 'tdms' and str(file)[:3] == 'D42':
                filelist.append(file)
        col_list = col_list4
    elif dam_num == '5':
        for file in os.listdir(path):
            if str(file)[-4:] == 'tdms' and str(file)[:3] == 'D52':
                filelist.append(file)
        col_list = col_list5
    elif dam_num == 'Все плотины':
        for file in os.listdir(path):
            if str(file)[-4:] == 'tdms' and str(file)[:1] == 'D':
                filelist.append(file)
        col_list = col_list1 + col_list3 + col_list4 + col_list5
    elif dam_num == 'Здание ГЭС - перемещение':
        for file in os.listdir(path):
            if str(file)[-4:] == 'tdms' and \
                    (str(file)[:5] == 'B0101' or str(file)[:7] == 'B010609' or str(file)[:7] == 'B010704' or str(file)[:7] == 'B010809'):
                filelist.append(file)
        col_list = col_list_b_d
    elif dam_num == 'Здание ГЭС - давление':
        for file in os.listdir(path):
            if str(file)[-4:] == 'tdms' and str(file)[:3] == 'B01' and \
                    (str(file)[:5] != 'B0101' and str(file)[:7] != 'B010609' and str(file)[:7] != 'B010704' and str(file)[:7] != 'B010809'):
                filelist.append(file)
        col_list = col_list_b

    # All files to dataframe
    # for file, col in tqdm(zip(filelist, col_list)):
    for file, col in zip(filelist, col_list):
        filepath = path + file
        try:
            df_full.append(TdmsFile(r"{}".format(filepath)).as_dataframe()["/'Data'/'Value'"])
            col_list_.append(col)
        except ValueError:
            print(col)

    df = pd.concat(df_full, axis=1)
    df.columns = col_list_

    df = df.dropna(axis=0)
    df = df[-num_points:]
    df = df - df.iloc[0]
    df = df[:-2]

    # Features to determine the deviation of sensors from each other
    df_mean = df.mean(axis=0)
    df_std = df.std(axis=0)
    # df_skew = df.skew(axis=0)
    df_min = df.min(axis=0)
    df_max = df.max(axis=0)

    df_info = pd.concat([df_mean, df_std, df_min, df_max], axis=1)
    df_info.columns = ['mean', 'std', 'min', 'max']
    df_info['delta1'] = df.iloc[num_points - 3] - df.iloc[0]

    # Scaling
    scaler = StandardScaler()
    df_info = scaler.fit_transform(df_info)
    df_info = pd.DataFrame(df_info, index=col_list_)

    # PCA (Translation to two-dimensional space for plotting scatterplot)
    pca = PCA(n_components=2)
    res = pca.fit_transform(df_info)
    res = pd.DataFrame(res, index=col_list_)

    res['bad'] = 0
    X = res[0].mean()
    Y = res[1].mean()
    res['dist'] = ((res[0] - X) ** 2 + (res[1] - Y) ** 2) ** 0.5
    r = 2 * res['dist'].mean()
    res.loc[res.dist > r, 'bad'] = 5

    # Plotting scatterplot
    ax = sns.scatterplot(data=res, x=res[0], y=res[1], hue='bad', size='bad', legend=False)
    for i, txt in enumerate(res.index):
        plt.annotate(txt, (res[0][i], res[1][i]))
    circle1 = plt.Circle(xy=(X, Y), radius=r, color='red', fill=False)
    ax.add_patch(circle1)
    ax.legend([],[], frameon=False)
    fig1 = ax.get_figure()

    # Plots for suspicious sensors
    res = res[res.dist > r]
    res = res.sort_values(by='dist', ascending=False)
    res = res[:10]

    df1 = df[res.index]
    df1 = pd.concat([df1, df[diff(col_list_, res.index)].mean(axis=1)], axis=1)
    df1 = df1.rename(columns={0: 'average'})
    df1['index'] = np.arange(num_points-2)
    df1['index'] = df1['index'] / (12 * 24)
    df1.set_index('index', inplace=True)

    try:
        ax2 = df1.clip(-5, 5).plot()
        fig2 = ax2.get_figure()
    except TypeError:
        fig2 = None

    return res, fig1, fig2

# Helper function for displaying plots in the GUI
def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.get_tk_widget().forget()
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg