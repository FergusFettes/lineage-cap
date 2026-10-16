"""Render figures directly from saved start-spread CSV grids."""

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


KERNELS = ("remote_visibility", "physical_arrival_diagnostic")
TITLES = ("Remote visibility", "Physical arrival diagnostic")
TARGET = 2.995732273553991
COLORS = ("#226f95", "#d47c30", "#55935a", "#8b65ad")


def load_rows(path):
    with path.open() as stream:
        rows = list(csv.DictReader(stream))
    for row in rows:
        for key, value in row.items():
            if value in ("True", "False"):
                row[key] = value == "True"
            elif value == "":
                row[key] = None
            else:
                try:
                    row[key] = float(value)
                except ValueError:
                    pass
    return rows


def select(rows, **criteria):
    return [r for r in rows if all(r[k] == v for k, v in criteria.items())]


def save(fig, output, name, title, caption, handles=None):
    fig.suptitle(title, x=.08, y=.975, ha="left", fontsize=17, weight="bold")
    fig.subplots_adjust(left=.08, right=.97, top=.86, bottom=.29, wspace=.28)
    if handles:
        fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(.5,.135),
                   ncol=len(handles), frameon=False)
    fig.text(.08,.075,caption,va="top",fontsize=10,color="#555555")
    for ax in fig.axes:
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(alpha=.2)
        ax.set_axisbelow(True)
    for suffix in ("png", "svg"):
        fig.savefig(output/f"{name}.{suffix}", dpi=160,
                    metadata={"Date": None} if suffix == "svg" else None)
    plt.close(fig)


def render_all(output):
    plt.rcParams.update({"font.size":11,"axes.titlesize":13,"axes.labelsize":11,
                         "lines.linewidth":2,"figure.facecolor":"white",
                         "svg.hashsalt":"lineage-cap"})
    bounds = load_rows(output/"start_bounds.csv")
    correlation = load_rows(output/"ancestry_groups.csv")
    ceilings = load_rows(output/"local_sync_q_ceilings.csv")

    fig, axes = plt.subplots(1,2,figsize=(11.8,6.6))
    handles = []
    for color, q in zip(COLORS, [1., 1e-10, 1e-12]):
        for ax, kernel in zip(axes, KERNELS):
            rows = select(bounds, zones_now=1e10, speed_c=.5, mu_threshold=TARGET,
                          q_per_zone=q, kernel=kernel)
            rows = sorted([r for r in rows if r["start_span_gyr"]>0], key=lambda r:r["start_span_gyr"])
            line, = ax.semilogx([r["start_span_gyr"]*1000 for r in rows],
                               [r["start_percentile_max"]*100 for r in rows],
                               "o-", color=color, markersize=4, label=f"q = {q:g}")
            if ax is axes[0]:
                handles.append(line)
    for ax,title in zip(axes,TITLES):
        ax.set(title=title,xlabel="Full start span W (Myr)",ylabel="Latest allowed start percentile (%)",ylim=(0,105))
        ax.set_xticks([10,30,100,200,500,1000,5000],labels=["10","30","100","200","500","1k","5k"])
    save(fig,output,"08_start_percentile","How early in the start window must we be?",
         "One shared start per galaxy; N = 10 billion, v = 0.5c, μ = −ln(0.05).\n100% allows the entire window. q is per zone; q = 10⁻⁶ follows q = 1.",handles)

    fig, axes = plt.subplots(1,2,figsize=(11.8,6.6))
    handles=[]
    for color,n in zip(COLORS,[1e8,1e9,1e10,1e11]):
        for ax,kernel in zip(axes,KERNELS):
            for target,style in [(TARGET,"-"),(1.,"--")]:
                rows=select(bounds,zones_now=n,speed_c=.5,mu_threshold=target,
                            kernel=kernel,start_span_gyr=.2)
                rows=sorted(rows,key=lambda r:r["q_per_zone"])
                line,=ax.semilogx([r["q_per_zone"] for r in rows],
                                 [r["start_percentile_max"]*100 for r in rows],
                                 style,color=color,label=f"N = {n:.0e}")
                if ax is axes[0] and target==TARGET:
                    handles.append(line)
    for ax,title in zip(axes,TITLES):
        ax.set(title=title,xlabel="Expansion probability per zone q",ylabel="Latest allowed start percentile (%)",xlim=(1e-18,1),ylim=(0,105))
    save(fig,output,"09_abundance_expansion","Abundance and expansion determine the leading edge",
         "One shared start per galaxy; W = 200 Myr, v = 0.5c. Solid: μ = −ln(0.05); dashed: μ = 1.\nAt qN ≫ 1 the galaxy probability saturates, so extra zones no longer tighten this model.",handles)

    fig, axes = plt.subplots(1,2,figsize=(11.8,6.6))
    handles=[]
    groups=[1.,100.,10000.,"per_zone"]
    for color,q in zip(COLORS,[1.,1e-10,1e-12]):
        for ax,kernel in zip(axes,KERNELS):
            rows=select(bounds+correlation,zones_now=1e10,speed_c=.5,mu_threshold=TARGET,
                        kernel=kernel,start_span_gyr=.2,q_per_zone=q)
            ordered=[select(rows,groups_per_galaxy=group)[0] for group in groups]
            line,=ax.plot(range(4),[r["start_percentile_max"]*100 for r in ordered],
                          "o-",color=color,label=f"q = {q:g}")
            if ax is axes[0]:
                handles.append(line)
    for ax,title in zip(axes,TITLES):
        ax.set(title=title,xlabel="Independent start groups per galaxy",ylabel="Latest allowed start percentile (%)",ylim=(0,105))
        ax.set_xticks(range(4),labels=["1","100","10,000","every zone"])
    save(fig,output,"10_ancestry_correlation","Shared ancestry changes the start-spread bound",
         "N = 10 billion, W = 200 Myr, v = 0.5c, μ = −ln(0.05).\nEach group shares a start; its zones decide independently whether to expand. Group counts are scenarios.",handles)

    fig, axes = plt.subplots(1,2,figsize=(11.8,6.6))
    handles=[]
    for color,n in zip(COLORS,[1e8,1e9,1e10,1e11]):
        for ax,kernel in zip(axes,KERNELS):
            for target,style in [(TARGET,"-"),(1.,"--")]:
                rows=select(ceilings,zones_now=n,speed_c=.5,mu_threshold=target,
                            kernel=kernel,our_start_percentile=.5)
                rows=sorted(rows,key=lambda r:r["start_span_gyr"])
                line,=ax.loglog([r["start_span_gyr"] for r in rows],
                               [r["q_per_zone_max"] for r in rows],style+"o",color=color,
                               markersize=4,label=f"N = {n:.0e}")
                if ax is axes[0] and target==TARGET:
                    handles.append(line)
    for ax,title in zip(axes,TITLES):
        ax.set(title=title,xlabel="Full galaxy-specific start span W (Gyr)",ylabel="Maximum expansion probability per zone q")
        ax.set_xticks([1,2,5],labels=["1","2","5"])
        ax.set_xticks([],minor=True)
    save(fig,output,"11_local_sync_ceiling","Gyr-wide local starts: the cost of a median start",
         "Our start is halfway through each window; one shared clock per galaxy, v = 0.5c.\nSolid: μ = −ln(0.05); dashed: μ = 1. Starting near the leading edge permits larger q.",handles)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=Path("results/start_spread"))
    render_all(parser.parse_args().output)


if __name__ == "__main__":
    main()
