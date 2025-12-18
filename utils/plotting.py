#
def donutplot(
    data,
    labels=None,
    title="Donut Chart",
    palette='Set2',
    figsize=(10, 8),
    textfontsize=12,
    show_values=True,
    startangle=90,
    explode=None,
    legend=True,
    legend_title=None,
    center_text=None  # central letter
):

    sns.set_style("white")
    sns.set_context("notebook", font_scale=1.1)

    # parse input data
    if isinstance(data, dict):
        labels = list(data.keys())
        values = list(data.values())
    elif isinstance(data, pd.Series):
        labels = data.index.tolist()
        values = data.values.tolist()
    else:
        values = data
        if labels is None:
            labels = [f'Category {i+1}' for i in range(len(values))]

    values = np.array(values)

    # set colors
    colors = sns.color_palette(palette, n_colors=len(values))

    # create figure
    fig, ax = plt.subplots(figsize=figsize)

    # create donut chart
    wedges, texts, autotexts = ax.pie(
        values,
        labels=None,  # labels shown on the sector
        autopct='%1.1f%%' if show_values else None,
        colors=colors,
        startangle=startangle,
        explode=explode,
        textprops={'fontsize': textfontsize, 'weight': 'bold'},
        wedgeprops={'edgecolor': 'white', 'linewidth': 3, 'width': 0.5}  # ring's width
    )

    if show_values and autotexts:
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(textfontsize - 1)
            autotext.set_weight('bold')

    # add center circle for donut effect
    centre_circle = plt.Circle((0, 0), 0.70, fc='white', linewidth=0)
    ax.add_artist(centre_circle)

    # add center text
    if center_text:
        ax.text(0, 0, center_text,
               ha='center', va='center',
               fontsize=20, fontweight='bold',
               color='#333333')
    else:
        total = sum(values)
        ax.text(0, 0, f'Total\n{total:.0f}',
               ha='center', va='center',
               fontsize=18, fontweight='bold',
               color='#333333')

    # add title
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)

    # add legend
    if legend:
        ax.legend(
            wedges,
            [f'{label}: {val:.1f}' for label, val in zip(labels, values)],
            title=legend_title,
            loc="center left",
            bbox_to_anchor=(1, 0, 0.5, 1),
            fontsize=11,
            frameon=False
        )

    ax.axis('equal')
    plt.tight_layout()

    return fig, ax


import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

# 
def barplot(
    data,
    x=None,
    y=None,
    labels=None,
    title="Bar Plot",
    xlabel=None,
    ylabel=None,
    color=True,  # if True, use single color; if False, use palette
    palette='husl',  # seaborn color palette
    figsize=(12, 8),
    horizontal=False,
    grid=True,
    grid_axis='y',
    grid_alpha=0.3,
    show_values=False,
    value_format='.2f',
    rotation=0,
    sort_values=False,
    ascending=True,
    legend_title=None,
    style='whitegrid'  # seaborn style: 'whitegrid', 'darkgrid', 'white', 'dark', 'ticks'
):

    # set seaborn style
    sns.set_style(style)

    # parse input data and convert to DataFrame
    if isinstance(data, dict):
        df = pd.DataFrame(list(data.items()), columns=['category', 'value'])
    elif isinstance(data, pd.DataFrame):
        df = data.copy()
        if len(df.columns) == 2:
            df.columns = ['category', 'value']
    elif isinstance(data, tuple) and len(data) == 2:
        df = pd.DataFrame({'category': data[0], 'value': data[1]})
    elif x is not None and y is not None:
        df = pd.DataFrame({'category': x, 'value': y})
    else:
        values = np.array(data)
        if labels is None:
            labels = list(range(len(values)))
        df = pd.DataFrame({'category': labels, 'value': values})

    # sort if requested
    if sort_values:
        df = df.sort_values('value', ascending=ascending).reset_index(drop=True)

    # create figure
    fig, ax = plt.subplots(figsize=figsize)

    # set color palette
    if color:
        colors = 'steelblue'
    else:
        colors = sns.color_palette(palette, n_colors=len(df))

    # create bar plot with seaborn
    if horizontal:
        sns.barplot(
            data=df,
            y='category',
            x='value',
            palette=colors if not color else None,
            color=colors if color else None,
            ax=ax,
            edgecolor='black',
            linewidth=0.5
        )

        # set labels
        ax.set_ylabel(xlabel if xlabel else '')
        ax.set_xlabel(ylabel if ylabel else 'Value')

        # grid
        if grid:
            ax.grid(True, axis='x', alpha=grid_alpha, linestyle='--', linewidth=0.7)
            ax.set_axisbelow(True)

        # add values on bars
        if show_values:
            fontsize = max(8, min(12, 120 / len(df)))
            for i, (idx, row) in enumerate(df.iterrows()):
                val = row['value']
                offset = val * 0.02
                ax.text(
                    val + offset,
                    i,
                    f'{val:{value_format}}',
                    ha='left',
                    va='center',
                    fontweight='bold',
                    fontsize=fontsize
                )
    else:
        sns.barplot(
            data=df,
            x='category',
            y='value',
            palette=colors if not color else None,
            color=colors if color else None,
            ax=ax,
            edgecolor='black',
            linewidth=0.5
        )

        # set labels
        ax.set_xlabel(xlabel if xlabel else '')
        ax.set_ylabel(ylabel if ylabel else 'Value')

        # rotate x labels
        if rotation != 0:
            ax.set_xticklabels(ax.get_xticklabels(), rotation=rotation, ha='right')

        # grid
        if grid:
            ax.grid(True, axis=grid_axis, alpha=grid_alpha, linestyle='--', linewidth=0.7)
            ax.set_axisbelow(True)

        # add values on bars
        if show_values:
            fontsize = max(8, min(12, 120 / len(df)))
            for i, (idx, row) in enumerate(df.iterrows()):
                val = row['value']
                offset = val * 0.01
                ax.text(
                    i,
                    val + offset,
                    f'{val:{value_format}}',
                    ha='center',
                    va='bottom',
                    fontweight='bold',
                    fontsize=fontsize
                )

    # add title
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)

    # remove spines for cleaner look
    sns.despine(left=False, bottom=False)

    # add legend if requested
    if legend_title is not None:
        handles = [plt.Rectangle((0,0),1,1, color=c) for c in colors]
        ax.legend(handles, df['category'].tolist(), title=legend_title,
                 bbox_to_anchor=(1.05, 1), loc='upper left')

    # apply tight layout
    plt.tight_layout()

    return fig, ax

#
def pieplot(
    data,
    x=None,
    y=None,
    labels=None,
    title="Pie Chart",
    palette='pastel',  # seaborn color palette
    figsize=(10, 8),
    textfontsize=12,
    textcolor='black',
    show_values=True,
    autopct='%1.1f%%',
    startangle=90,
    explode=None,
    legend=True,
    legend_title=None,
    style='whitegrid'
):

    # set seaborn style
    sns.set_style(style)
    sns.set_context("notebook", font_scale=1.1)

    # parse input data
    if isinstance(data, dict):
        labels = list(data.keys())
        values = list(data.values())
    elif isinstance(data, pd.Series):
        labels = data.index.tolist()
        values = data.values.tolist()
    elif isinstance(data, tuple) and len(data) == 2:
        labels, values = data
    elif x is not None and y is not None:
        labels = x
        values = y
    else:
        values = data
        if labels is None:
            labels = [f'Category {i+1}' for i in range(len(values))]

    # convert to numpy arrays
    values = np.array(values)

    # set colors using seaborn palette
    colors = sns.color_palette(palette, n_colors=len(values))

    # create figure
    fig, ax = plt.subplots(figsize=figsize)

    # create wedges
    wedges, texts, autotexts = ax.pie(
        values,
        labels=labels if not legend else None,
        autopct=autopct if show_values else None,
        colors=colors,
        startangle=startangle,
        explode=explode,
        textprops={'fontsize': textfontsize, 'weight': 'bold'},
        wedgeprops={'edgecolor': 'white', 'linewidth': 2}
    )

    if show_values and autotexts:
        for autotext in autotexts:
            autotext.set_color(textcolor)
            autotext.set_fontsize(textfontsize)
            autotext.set_weight('bold')

    # add title
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)

    # add legend
    if legend:
        ax.legend(
            wedges,
            [f'{label}: {int(val)}' for label, val in zip(labels, values)],
            title=legend_title,
            loc="center left",
            bbox_to_anchor=(1, 0, 0.5, 1),
            fontsize=11
        )

    # equal aspect ratio ensures that pie is drawn as a circle
    ax.axis('equal')

    # apply tight layout
    plt.tight_layout()

    return fig, ax

#
def boxplot_by_category(
    data,
    x_col,
    y_col,
    title="Box Plot",
    xlabel=None,
    ylabel=None,
    figsize=(14, 8),
    palette='Set2',
    show_mean=True,
    rotation=45
):
    """
    创建分组箱线图
    """
    plt.figure(figsize=figsize)

    sns.boxplot(
        data=data,
        x=x_col,
        y=y_col,
        palette=palette,
        width=0.6,
        linewidth=1.5
    )

    if show_mean:
        sns.pointplot(
            data=data,
            x=x_col,
            y=y_col,
            estimator=np.mean,
            color='red',
            markers='D',
            scale=0.8,
            linestyles='none',
            label='Mean'
        )

    plt.title(title, fontsize=16, fontweight='bold', pad=20)
    plt.xlabel(xlabel if xlabel else x_col, fontsize=12)
    plt.ylabel(ylabel if ylabel else y_col, fontsize=12)
    plt.xticks(rotation=rotation, ha='right')
    plt.grid(True, alpha=0.3, linestyle='--', axis='y')
    plt.legend()
    plt.tight_layout()

    return plt.gcf(), plt.gca()

#
def heatmap(
    data,
    title="Heatmap",
    figsize=(14, 10),
    cmap='YlOrRd',
    annot=True,
    fmt='g',
    linewidths=1,
    cbar_label='Value'
):
    """
    创建热力图
    """
    plt.figure(figsize=figsize)
    
    sns.heatmap(
        data,
        cmap=cmap,
        annot=annot,
        fmt=fmt,
        cbar_kws={'label': cbar_label},
        linewidths=linewidths,
        linecolor='white'
    )

    plt.title(title, fontsize=16, fontweight='bold', pad=20)
    plt.xlabel(data.columns.name or 'X', fontsize=12)
    plt.ylabel(data.index.name or 'Y', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()

    return plt.gcf(), plt.gca()