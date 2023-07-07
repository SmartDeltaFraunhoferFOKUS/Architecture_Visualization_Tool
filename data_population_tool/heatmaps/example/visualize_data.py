import matplotlib.pyplot as plt
from matplotlib import image
import pandas as pd
from matplotlib import colors
from IPython.display import display

def plot_data_points(df):
    #visualize_data.plotTable(df)
    # generate some example data
    def background_gradient(s, m, M, cmap='PuBu', low=0, high=0):
        rng = M - m
        norm = colors.Normalize(m - (rng * low),
                                M + (rng * high))
        normed = norm(s.values)
        c = [colors.rgb2hex(x) for x in plt.cm.get_cmap(cmap)(normed)]
        return ['background-color: %s' % color for color in c]

    display(df.style.apply(background_gradient,
                cmap='OrRd',
                m=df.min().min(),
                M=df.max().max(),
                low=0,
                high=0.2))
                
def plot_data_points_logs(data_frame, labels_list):
    df = pd.DataFrame(data_frame)
    pd.set_option("display.precision", 3)
    df.columns= labels_list
    df.index = labels_list    
    #visualize_data.plotTable(df)
    # generate some example data
    def background_gradient(s, m, M, cmap='PuBu', low=0, high=0):
        rng = M - m
        norm = colors.Normalize(m - (rng * low),
                                M + (rng * high))
        normed = norm(s.values)
        c = [colors.rgb2hex(x) for x in plt.cm.get_cmap(cmap)(normed)]
        return ['background-color: %s' % color for color in c]

    display(df.style.apply(background_gradient,
                cmap='Blues',
                m=df.min().min(),
                M=df.max().max(),
                low=0,
                high=0.2))