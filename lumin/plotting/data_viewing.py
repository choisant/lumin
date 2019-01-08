import numpy as np
import pandas as pd
from typing import Union, List, Optional, Dict, Any

from .plot_settings import PlotSettings
from ..utils.misc import uncert_round, get_moments

import seaborn as sns
import matplotlib.pyplot as plt


def plot_feat(in_data:Union[pd.DataFrame,List[pd.DataFrame]], feat:str, weight_name:Optional[str]=None, cuts:Optional[List[pd.Series]]=1,
              labels:Optional[List[str]]=None, plot_bulk:bool=True, n_samples:int=100000,
              plot_params:List[Dict[str,Any]]={}, size='mid', moments=True, ax_labels={'y': 'Density', 'x': None},
              savename:Optional[str]=None, settings:PlotSettings=PlotSettings()) -> None:
    if not isinstance(cuts,   list): cuts   = [cuts]
    if not isinstance(labels, list): labels = [labels]    
    if not isinstance(cuts, list): raise ValueError(f"{len(cuts)} plots requested, but no labels passed")
    elif len(cuts) != len(labels): raise ValueError(f"{len(cuts)} plots requested, but {len(labels)} labels passed")
       
    with sns.axes_style(settings.style), sns.color_palette(settings.palette):
        plt.figure(figsize=(settings.str2sz(size, 'x'), settings.str2sz(size, 'y')))
        for i in range(len(cuts)):
            tmp_plot_params = plot_params[i] if isinstance(plot_params, list) else plot_params

            if plot_bulk:  # Ignore tails for indicative plotting
                feat_range = np.percentile(in_data[feat], [1, 99])
                if feat_range[0] == feat_range[1]: break
                cut = (in_data[feat] > feat_range[0]) & (in_data[feat] < feat_range[1])
                if cuts[i] is not None: cut = cut & (cuts[i])
                if weight_name is None:
                    plot_data = in_data.loc[cut, feat]
                else:
                    weights = in_data.loc[cut, weight_name].values.astype('float64')
                    weights /= weights.sum()
                    plot_data = np.random.choice(in_data.loc[cut, feat], n_samples, p=weights)
            else:
                tmp_data = in_data if cuts[i] is not None else in_data.loc[cuts[i]]
                if weight_name is None:
                    plot_data = tmp_data[feat]
                else:
                    weights = tmp_data[weight_name].values.astype('float64')
                    weights /= weights.sum()
                    plot_data = np.random.choice(tmp_data[feat], n_samples, p=weights)
            label = labels[i]
            if moments:
                moms = get_moments(plot_data)
                mean = uncert_round(moms[0], moms[1])
                std = uncert_round(moms[2], moms[3])
                label += r', $\bar{x}=$' + f'{mean[0]}±{mean[1]}' + r', $\sigma_x=$' + f'{std[0]}±{std[1]}'

            sns.distplot(plot_data, label=label, **tmp_plot_params)

        if len(cuts) > 1 or moments: plt.legend(loc=settings.leg_loc, fontsize=settings.leg_sz)
        plt.xticks(fontsize=settings.tk_sz, color=settings.tk_col)
        plt.yticks(fontsize=settings.tk_sz, color=settings.tk_col)
        plt.ylabel(ax_labels['y'], fontsize=settings.lbl_sz, color=settings.lbl_col)
        x_lbl = feat if ax_labels['y'] is None else ax_labels['y']
        plt.xlabel(x_lbl, fontsize=settings.lbl_sz, color=settings.lbl_col)
        if savename is not None: plt.savefig(settings.savepath/f'{savename}{settings.format}')
        plt.show()


def compare_events(events: list) -> None:
    with sns.axes_style('whitegrid'), sns.color_palette('tab10'):
        fig, axs = plt.subplots(3, len(events), figsize=(9*len(events), 18), gridspec_kw={'height_ratios': [1, 0.5, 0.5]})
        for vector in [x[:-3] for x in events[0].columns if '_px' in x.lower()]:
            for i, in_data in enumerate(events):
                x = in_data[vector + '_px'].values[0]
                try: y = in_data[vector + '_py'].values[0]
                except KeyError: y = 0
                try: z = in_data[vector + '_pz'].values[0]
                except KeyError: z = 0
                axs[0, i].plot((0, x), (0, y), label=vector)
                axs[1, i].plot((0, z), (0, x), label=vector)
                axs[2, i].plot((0, z), (0, y), label=vector)
        for ax in axs[0]:
            ax.add_artist(plt.Circle((0, 0), 1, color='grey', fill=False, linewidth=2))
            ax.set_xlim(-1.1, 1.1)
            ax.set_ylim(-1.1, 1.1)
            ax.set_xlabel(r"$p_x$", fontsize=16, color='black')
            ax.set_ylabel(r"$p_y$", fontsize=16, color='black')
            ax.legend(loc='right', fontsize=12)  
        for ax in axs[1]:
            ax.add_artist(plt.Rectangle((-2, -1), 4, 2, color='grey', fill=False, linewidth=2))
            ax.set_xlim(-2.2, 2.2)
            ax.set_ylim(-1.1, 1.1)
            ax.set_xlabel(r"$p_z$", fontsize=16, color='black')
            ax.set_ylabel(r"$p_x$", fontsize=16, color='black')
            ax.legend(loc='right', fontsize=12)
        for ax in axs[2]: 
            ax.add_artist(plt.Rectangle((-2, -1), 4, 2, color='grey', fill=False, linewidth=2))
            ax.set_xlim(-2.2, 2.2)
            ax.set_ylim(-1.1, 1.1)
            ax.set_xlabel(r"$p_z$", fontsize=16, color='black')
            ax.set_ylabel(r"$p_y$", fontsize=16, color='black')
            ax.legend(loc='right', fontsize=12)
        fig.show()
