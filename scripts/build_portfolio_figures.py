"""Render public portfolio figures from the generated synthetic demo exports."""
from collections import defaultdict
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "output" / "demo"
DEST = ROOT / "assets" / "portfolio"
CREAM, PANEL, INK, BROWN, GOLD, SUBTLE = "#FBF8F1", "#FFFDF8", "#231F1D", "#634F43", "#937449", "#DDD0BE"
plt.rcParams.update({"font.family":"DejaVu Sans","text.color":INK,"axes.labelcolor":INK,
                     "xtick.color":BROWN,"ytick.color":BROWN,"axes.spines.top":False,"axes.spines.right":False})


def source(group, name):
    with (DEMO / group / f"{name}.csv").open(encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def figure(title, caption, footer):
    fig, ax = plt.subplots(figsize=(10.6, 4.7), facecolor=CREAM)
    fig.subplots_adjust(left=.22, right=.92, top=.69, bottom=.21)
    fig.text(.075,.89,title,fontsize=23,weight="bold")
    fig.text(.077,.81,caption,fontsize=11,color=BROWN)
    fig.text(.077,.065,footer,fontsize=9,color=BROWN)
    ax.set_facecolor(PANEL)
    ax.spines[["left","bottom"]].set_color(SUBTLE)
    ax.tick_params(length=0,pad=7)
    return fig, ax


def save(fig,name):
    DEST.mkdir(parents=True,exist_ok=True)
    fig.savefig(DEST / f"{name}.png",dpi=150,facecolor=CREAM)
    plt.close(fig)


def bars(ax,labels,values,colors=None):
    marks = ax.barh(labels,values,color=colors or BROWN,height=.48)
    ax.invert_yaxis()
    ax.set_axisbelow(True)
    ax.grid(axis="x",color=SUBTLE,linewidth=.7)
    return marks


def main():
    records = source("catalog","portfolio")
    categories = defaultdict(int)
    for row in records:
        if (row["vintage"],row["market"]) == ("recent","US"):
            categories[row["category"].title()] += int(row["products"])
    category_rows = sorted(categories.items(), key=lambda pair:(-pair[1],pair[0]))
    names, counts = zip(*category_rows)
    fig,ax = figure("US assortment by category","Representative products  |  Synthetic November 2026 snapshot",
                    "Source: portfolio.csv  ·  Cohort counts describe catalog coverage.")
    marks=bars(ax,names,counts)
    ax.set_xlim(0,max(counts)*1.18)
    ax.bar_label(marks,padding=6,color=INK)
    save(fig,"commercial-overview")

    plan=source("finance","fact_simulated_finance")
    base=[row for row in plan if row["scenario"]=="Base"]
    totals=lambda rows,key:sum(float(row[key]) for row in rows)
    keys=("net_revenue","gross_profit","contribution","operating_profit")
    fig,ax=figure("Base case financial performance","Annual simulated P&L  |  USD",
                  "Source: fact_simulated_finance.csv  ·  All financial values are simulated.")
    values=[totals(base,key) for key in keys]
    marks=bars(ax,("Net revenue","Gross profit","Contribution","Operating profit"),values,[BROWN,GOLD,BROWN,GOLD])
    ax.set_xlim(0,max(values)*1.22)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda n,_: f"{n/1000:,.0f}k"))
    ax.bar_label(marks,labels=[f"${n/1000:,.1f}k" for n in values],padding=6,color=INK)
    save(fig,"financial-overview")

    fig,ax=figure("Scenario comparison","Annual simulated operating profit  |  USD",
                  "Source: fact_simulated_finance.csv  ·  Cases vary modeled growth, cost inflation, and discount assumptions.")
    cases=("Bear","Base","Bull")
    values=[totals([row for row in plan if row["scenario"]==case],"operating_profit") for case in cases]
    marks=bars(ax,cases,values,[BROWN,GOLD,BROWN])
    ax.set_xlim(0,max(values)*1.25)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda n,_: f"{n/1000:,.0f}k"))
    ax.bar_label(marks,labels=[f"${n/1000:,.1f}k" for n in values],padding=6,color=INK)
    save(fig,"scenario-comparison")

    grid=source("finance","fact_simulated_promotion")
    campaign=[row for row in grid if float(row["discount"])==.15]
    uplifts=[float(row["uplift"])*100 for row in campaign]
    contribution=[float(row["incremental_contribution"]) for row in campaign]
    fig,ax=figure("Does the offer earn its spend?","Simulated incremental contribution  |  15% proposed discount",
                  "Source: fact_simulated_promotion.csv  ·  Dotted line marks unchanged contribution.")
    ax.axhline(0,color=GOLD,linestyle=":",linewidth=1.5)
    ax.plot(uplifts,contribution,color=BROWN,linewidth=2.5,marker="o")
    ax.set_xticks(uplifts,[f"{x:.0f}%" for x in uplifts])
    ax.set_xlabel("Assumed unit uplift",fontsize=10)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda n,_: f"-${abs(n)/1000:g}k" if n<0 else f"${n/1000:g}k"))
    point=uplifts.index(20)
    ax.annotate(f"-${abs(contribution[point]):,.0f} at 20%",(20,contribution[point]),xytext=(28,-2700),
                color=BROWN,arrowprops={"arrowstyle":"-","color":GOLD})
    ax.grid(axis="y",color=SUBTLE,linewidth=.6)
    save(fig,"promotion-profitability")

    quality=source("catalog","quality_completeness")
    fields={"country":"Country","rating":"Rating","sale_price":"Sale price","collected_at":"Collection date"}
    rows={row["field"]:row for row in quality if row["vintage"]=="recent"}
    fig,ax=figure("How much of the catalog can we use?","Recent synthetic catalog  |  Share of evaluated values",
                  "Source: quality_completeness.csv  ·  A blank sale price leaves promotion status unknown.")
    names=list(fields.values())
    y=range(len(names))
    ax.barh([i-.13 for i in y],[float(rows[k]["completeness_rate"])*100 for k in fields],height=.24,color=GOLD,label="Present")
    ax.barh([i+.13 for i in y],[float(rows[k]["parse_valid_rate"])*100 for k in fields],height=.24,color=BROWN,label="Parse-valid")
    ax.set_yticks(list(y),names)
    ax.invert_yaxis()
    ax.set_xlim(0,105)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda n,_: f"{n:,.0f}%"))
    ax.legend(loc="upper right",bbox_to_anchor=(1,1.18),frameon=False,ncols=2)
    save(fig,"data-quality")


if __name__ == "__main__":
    main()
