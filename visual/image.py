# ======================================================================
# >> IMPORTS
# ======================================================================

# Python
from PIL import Image
import io
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import seaborn as sns


# ======================================================================
# >> Colors
# ======================================================================
class Colors:
    blue = (0.325, 0.514, 0.91, 1)
    red = (0.91, 0.251, 0.341, 1)
    grey = (0.258, 0.259, 0.329, 1)
    black = (0.156, 0.156, 0.188, 1)
    white = (1, 1, 1, 1)

colors = Colors()

# ======================================================================
# >> Teams
# ======================================================================
def create_bar(info, team_id, max_count, title):
    data = pd.DataFrame({'x':info,
                         'y':[1, 2, 3, 4, 5]})
    data1 = pd.DataFrame({'x':[max_count]*5,
                         'y':[1, 2, 3, 4, 5]})

    sns.set_style("dark", {'axes.facecolor':colors.black})
    gfg1 = sns.barplot(data=data1, x='x', y='y', orient="h", facecolor=colors.grey, linewidth=0)
    gfg = sns.barplot(data=data, x='x', y='y', orient="h", facecolor=[colors.blue, colors.red][team_id], linewidth=0)

    gfg1.set_xlim(0, max_count)
    gfg.set(xlabel='',
           ylabel='',
           title=title)

    gfg.bar_label(gfg.containers[1], fontsize=14, color=colors.white, label_type='center')

    plt.tick_params(left=False, right=False , labelleft=False ,
                    labelbottom=False, bottom=False, labelright=False)

    fig = plt.gcf()
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=400)

    img = Image.open(buf)
    img.show()

    return fig
