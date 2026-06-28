from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

COLORS = {"primary": "#1E3A5F", "secondary": "#2E6099", "accent": "#2E9CCA",
          "light": "#EFF4FB", "green": "#27AE60", "orange": "#E67E22", "red": "#E74C3C"}

def _style():
    plt.rcParams.update({
        'font.family': 'DejaVu Sans', 'axes.spines.top': False, 'axes.spines.right': False,
        'axes.grid': True, 'grid.alpha': 0.3, 'figure.facecolor': 'white',
    })

def plot_heating_vs_insulation(envelope_df):
    _style()
    grouped = envelope_df.groupby("insulation_cm", as_index=False)["heating_load_kWh_yr"].mean()
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(grouped["insulation_cm"], grouped["heating_load_kWh_yr"], marker="o",
            color=COLORS["primary"], linewidth=2.5, markersize=8)
    ax.fill_between(grouped["insulation_cm"], grouped["heating_load_kWh_yr"],
                    alpha=0.15, color=COLORS["primary"])
    for _, r in grouped.iterrows():
        ax.annotate(f'{r["heating_load_kWh_yr"]:,.0f}', (r["insulation_cm"], r["heating_load_kWh_yr"]),
                    textcoords="offset points", xytext=(0, 10), ha='center', fontsize=10, fontweight='bold')
    ax.set_xlabel("Insulation Thickness (cm)", fontsize=12)
    ax.set_ylabel("Average Heating Load (kWh/year)", fontsize=12)
    ax.set_title("Figure 1: Heating Load vs Insulation Thickness\n(Corrected Design Temp: -3°C winter, Istanbul)", fontsize=12, fontweight='bold')
    ax.set_xticks(grouped["insulation_cm"])
    plt.tight_layout()
    path = OUTPUT_DIR / "fig1_heating_vs_insulation.png"
    plt.savefig(path, dpi=180, bbox_inches='tight')
    plt.close()
    return path

def plot_cooling_vs_insulation(envelope_df):
    _style()
    grouped = envelope_df.groupby("insulation_cm", as_index=False)["cooling_load_kWh_yr"].mean()
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(grouped["insulation_cm"], grouped["cooling_load_kWh_yr"], marker="s",
            color=COLORS["accent"], linewidth=2.5, markersize=8)
    ax.fill_between(grouped["insulation_cm"], grouped["cooling_load_kWh_yr"],
                    alpha=0.15, color=COLORS["accent"])
    for _, r in grouped.iterrows():
        ax.annotate(f'{r["cooling_load_kWh_yr"]:,.0f}', (r["insulation_cm"], r["cooling_load_kWh_yr"]),
                    textcoords="offset points", xytext=(0, 10), ha='center', fontsize=10, fontweight='bold')
    ax.set_xlabel("Insulation Thickness (cm)", fontsize=12)
    ax.set_ylabel("Average Cooling Load (kWh/year)", fontsize=12)
    ax.set_title("Figure 2: Cooling Load vs Insulation Thickness\n(Corrected Design Temp: +33°C summer, Istanbul)", fontsize=12, fontweight='bold')
    ax.set_xticks(grouped["insulation_cm"])
    plt.tight_layout()
    path = OUTPUT_DIR / "fig2_cooling_vs_insulation.png"
    plt.savefig(path, dpi=180, bbox_inches='tight')
    plt.close()
    return path

def plot_window_heating(envelope_df):
    _style()
    grouped = envelope_df.groupby("window_type", as_index=False)["heating_load_kWh_yr"].mean()
    order = ["Single Pane", "Double Pane", "Triple Pane"]
    grouped["window_type"] = pd.Categorical(grouped["window_type"], categories=order, ordered=True)
    grouped = grouped.sort_values("window_type")
    colors = [COLORS["red"], COLORS["secondary"], COLORS["green"]]
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(grouped["window_type"], grouped["heating_load_kWh_yr"],
                  color=colors, width=0.5, edgecolor='white', linewidth=1.5)
    for bar, val in zip(bars, grouped["heating_load_kWh_yr"]):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 500,
                f'{val:,.0f}', ha='center', va='bottom', fontsize=11, fontweight='bold')
    ax.set_ylabel("Average Heating Load (kWh/year)", fontsize=12)
    ax.set_title("Figure 3: Heating Load by Window Type", fontsize=12, fontweight='bold')
    plt.tight_layout()
    path = OUTPUT_DIR / "fig3_heating_by_window.png"
    plt.savefig(path, dpi=180, bbox_inches='tight')
    plt.close()
    return path

def plot_cost_vs_performance(cost_df):
    _style()
    total_energy = cost_df["heating_load_kWh_yr"] + cost_df["cooling_load_kWh_yr"]
    ins_vals = cost_df["insulation_thickness_cm"].unique()
    cmap = plt.cm.get_cmap('Blues', len(ins_vals) + 1)
    fig, ax = plt.subplots(figsize=(9, 6))
    for i, ins in enumerate(sorted(ins_vals)):
        mask = cost_df["insulation_thickness_cm"] == ins
        ax.scatter(cost_df.loc[mask, "total_cost_TL"], total_energy[mask],
                   alpha=0.6, s=20, color=cmap(i + 1), label=f'{ins:.0f} cm insulation')
    ax.set_xlabel("Total Cost (TL)", fontsize=12)
    ax.set_ylabel("Total Energy Load (kWh/year)", fontsize=12)
    ax.set_title("Figure 4: Cost vs Energy Performance\n(All parametric combinations)", fontsize=12, fontweight='bold')
    ax.legend(fontsize=10)
    plt.tight_layout()
    path = OUTPUT_DIR / "fig4_cost_vs_performance.png"
    plt.savefig(path, dpi=180, bbox_inches='tight')
    plt.close()
    return path

def plot_ua_breakdown(envelope_df):
    """Figure 5: UA contribution breakdown by component"""
    _style()
    from geometry import compute_building_geometry
    from config import BuildingInputs
    geom = compute_building_geometry(BuildingInputs())

    rows = envelope_df[envelope_df["movable_insulation"] == False].drop_duplicates(["insulation_cm", "window_type"])
    labels = []
    ua_wall, ua_roof, ua_win = [], [], []
    for _, r in rows.iterrows():
        labels.append(f"{r['insulation_cm']:.0f}cm\n{r['window_type'][:3]}")
        ua_wall.append(r["wall_U"] * geom["opaque_wall_area_m2"])
        ua_roof.append(r["roof_U"] * geom["roof_area_m2"])
        ua_win.append(r["window_U_heating"] * geom["window_area_m2"])

    x = np.arange(len(labels))
    w = 0.6
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.bar(x, ua_wall, w, label='Wall UA (W/K)', color=COLORS["primary"])
    ax.bar(x, ua_roof, w, bottom=ua_wall, label='Roof UA (W/K)', color=COLORS["accent"])
    ax.bar(x, ua_win,  w, bottom=[a + b for a, b in zip(ua_wall, ua_roof)],
           label='Window UA (W/K)', color=COLORS["orange"])
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=7)
    ax.set_ylabel("UA Value (W/K)", fontsize=12)
    ax.set_title("Figure 5: UA Breakdown by Envelope Component\n(All configurations, no movable insulation)",
                 fontsize=11, fontweight='bold')
    ax.legend(fontsize=10)
    plt.tight_layout()
    path = OUTPUT_DIR / "fig5_ua_breakdown.png"
    plt.savefig(path, dpi=180, bbox_inches='tight')
    plt.close()
    return path

def plot_furnace_efficiency_impact(combination_df):
    """Figure 6: Effect of furnace efficiency on gas consumption"""
    _style()
    ref = combination_df[
        (combination_df["insulation_cm"] == 10.0) &
        (combination_df["window_type"] == "Double Pane") &
        (combination_df["movable_insulation"] == False) &
        (combination_df["ac_COP"] == 3.0)
    ].sort_values("furnace_efficiency")

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(ref["furnace_efficiency"] * 100, ref["gas_use_kWh_yr"], marker="o",
            color=COLORS["orange"], linewidth=2.5, markersize=9)
    for _, r in ref.iterrows():
        ax.annotate(f'{r["gas_use_kWh_yr"]:,.0f} kWh',
                    (r["furnace_efficiency"] * 100, r["gas_use_kWh_yr"]),
                    textcoords="offset points", xytext=(5, 5), fontsize=9)
    ax.set_xlabel("Furnace Efficiency (%)", fontsize=12)
    ax.set_ylabel("Annual Gas Consumption (kWh/year)", fontsize=12)
    ax.set_title("Figure 6: Gas Consumption vs Furnace Efficiency\n(10cm insulation, Double Pane — reference case)",
                 fontsize=11, fontweight='bold')
    plt.tight_layout()
    path = OUTPUT_DIR / "fig6_furnace_efficiency.png"
    plt.savefig(path, dpi=180, bbox_inches='tight')
    plt.close()
    return path

def plot_ac_cop_impact(combination_df):
    """Figure 7: Effect of AC COP on electricity consumption"""
    _style()
    ref = combination_df[
        (combination_df["insulation_cm"] == 10.0) &
        (combination_df["window_type"] == "Double Pane") &
        (combination_df["movable_insulation"] == False) &
        (combination_df["furnace_efficiency"] == 0.90)
    ].sort_values("ac_COP")

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(ref["ac_COP"], ref["ac_electricity_kWh_yr"], marker="s",
            color=COLORS["green"], linewidth=2.5, markersize=9)
    for _, r in ref.iterrows():
        ax.annotate(f'{r["ac_electricity_kWh_yr"]:,.0f} kWh',
                    (r["ac_COP"], r["ac_electricity_kWh_yr"]),
                    textcoords="offset points", xytext=(5, 5), fontsize=9)
    ax.set_xlabel("AC COP (-)", fontsize=12)
    ax.set_ylabel("Annual Electricity Consumption (kWh/year)", fontsize=12)
    ax.set_title("Figure 7: Electricity Use vs AC COP\n(10cm insulation, Double Pane — reference case)",
                 fontsize=11, fontweight='bold')
    plt.tight_layout()
    path = OUTPUT_DIR / "fig7_ac_cop.png"
    plt.savefig(path, dpi=180, bbox_inches='tight')
    plt.close()
    return path

def plot_movable_insulation_benefit(envelope_df):
    """Figure 8: Movable insulation heating load reduction"""
    _style()
    df_no  = envelope_df[envelope_df["movable_insulation"] == False].copy()
    df_yes = envelope_df[envelope_df["movable_insulation"] == True].copy()
    merged = df_no.merge(df_yes, on=["insulation_cm", "window_type"], suffixes=("_no", "_yes"))
    merged["reduction_pct"] = (
        (merged["heating_load_kWh_yr_no"] - merged["heating_load_kWh_yr_yes"])
        / merged["heating_load_kWh_yr_no"] * 100
    )
    merged["label"] = (merged["insulation_cm"].astype(int).astype(str)
                       + "cm / " + merged["window_type"])

    fig, ax = plt.subplots(figsize=(10, 5))
    colors_list = [COLORS["green"] if v > 15 else COLORS["accent"]
                   for v in merged["reduction_pct"]]
    bars = ax.barh(merged["label"], merged["reduction_pct"],
                   color=colors_list, edgecolor='white')
    for bar, val in zip(bars, merged["reduction_pct"]):
        ax.text(val + 0.3, bar.get_y() + bar.get_height() / 2,
                f'{val:.1f}%', va='center', fontsize=9)
    ax.set_xlabel("Heating Load Reduction (%)", fontsize=12)
    ax.set_title("Figure 8: Heating Load Reduction with Movable Insulation",
                 fontsize=11, fontweight='bold')
    ax.axvline(x=10, color='red', linestyle='--', alpha=0.5, label='10% threshold')
    ax.legend()
    plt.tight_layout()
    path = OUTPUT_DIR / "fig8_movable_insulation.png"
    plt.savefig(path, dpi=180, bbox_inches='tight')
    plt.close()
    return path

def draw_hvac_flow_diagram():
    """Figure 9: HVAC system flow diagrams — heating and cooling modes"""
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    fig.patch.set_facecolor('white')

    # ── HEATING MODE ──────────────────────────────────────────────────────────
    ax = axes[0]
    ax.set_xlim(0, 10); ax.set_ylim(0, 12); ax.axis('off')
    ax.set_title("HEATING MODE — Gas Furnace System",
                 fontsize=12, fontweight='bold', color=COLORS["primary"])

    components_heat = [
        (5, 10.5, "GAS SUPPLY\n(Utility)",            COLORS["orange"]),
        (5,  8.5, "GAS BURNER\n(Combustion)",          COLORS["red"]),
        (5,  6.5, "HEAT EXCHANGER\n(Air-to-Flue Gas)", COLORS["primary"]),
        (5,  4.5, "AHU BLOWER\n(Fan)",                 COLORS["secondary"]),
        (5,  2.5, "SUPPLY DUCT\n& REGISTERS",          COLORS["accent"]),
        (5,  0.5, "CONDITIONED\nSPACE (20°C)",         COLORS["green"]),
    ]
    labels_heat = [
        "Gas pressure\n(supply)",
        "T_flame ≈ 1100°C\nAFUE: 70–95%",
        "T_air: 20→55°C\nT_flue exit: ~55°C",
        "ΔP = 125 Pa\nVariable speed",
        "T_supply ≈ 50°C\nLoss ≈ 5%",
        "T_indoor = 20°C\nQ_heat absorbed",
    ]

    for i, (x, y, label, color) in enumerate(components_heat):
        box = mpatches.FancyBboxPatch((x - 2, y - 0.7), 4, 1.2,
                                      boxstyle="round,pad=0.1",
                                      facecolor=color, edgecolor='white',
                                      linewidth=1.5, alpha=0.9)
        ax.add_patch(box)
        ax.text(x, y, label, ha='center', va='center',
                fontsize=7.5, color='white', fontweight='bold')
        if i < len(components_heat) - 1:
            ax.annotate("", xy=(x, components_heat[i + 1][1] + 0.7),
                        xytext=(x, y - 0.7),
                        arrowprops=dict(arrowstyle="->",
                                        color=COLORS["primary"], lw=1.5))
        ax.text(7.5, y, labels_heat[i], ha='left', va='center',
                fontsize=6.5, color='#333333', style='italic')

    # ── COOLING MODE ──────────────────────────────────────────────────────────
    ax2 = axes[1]
    ax2.set_xlim(0, 10); ax2.set_ylim(0, 12); ax2.axis('off')
    ax2.set_title("COOLING MODE — Refrigeration Cycle",
                  fontsize=12, fontweight='bold', color=COLORS["accent"])

    components_cool = [
        (5, 10.5, "COMPRESSOR\n(Outdoor Unit)",    COLORS["red"]),
        (5,  8.5, "CONDENSER COIL\n(Heat rejection)", COLORS["orange"]),
        (5,  6.5, "EXPANSION VALVE\n(Throttling)",  COLORS["secondary"]),
        (5,  4.5, "EVAPORATOR COIL\n(Indoor Unit)", COLORS["accent"]),
        (5,  2.5, "AHU FAN\n(Air distribution)",   COLORS["primary"]),
        (5,  0.5, "CONDITIONED\nSPACE (24°C)",      COLORS["green"]),
    ]
    labels_cool = [
        "Refrigerant vapour\nLow→High P",
        "T_cond ≈ 40°C\nHeat → outdoor air",
        "T: 40→7°C\nP: High→Low",
        "T_evap ≈ 7°C\nHeat absorbed from air",
        "T_supply ≈ 13°C\nT_return ≈ 26°C",
        "T_indoor = 24°C\nCOP: 2.5–4.0",
    ]

    for i, (x, y, label, color) in enumerate(components_cool):
        box = mpatches.FancyBboxPatch((x - 2, y - 0.7), 4, 1.2,
                                      boxstyle="round,pad=0.1",
                                      facecolor=color, edgecolor='white',
                                      linewidth=1.5, alpha=0.9)
        ax2.add_patch(box)
        ax2.text(x, y, label, ha='center', va='center',
                 fontsize=7.5, color='white', fontweight='bold')
        if i < len(components_cool) - 1:
            ax2.annotate("", xy=(x, components_cool[i + 1][1] + 0.7),
                         xytext=(x, y - 0.7),
                         arrowprops=dict(arrowstyle="->",
                                         color=COLORS["accent"], lw=1.5))
        ax2.text(7.5, y, labels_cool[i], ha='left', va='center',
                 fontsize=6.5, color='#333333', style='italic')

    ax2.annotate("Refrigerant\ncycle (closed)", xy=(2.5, 5.5),
                 fontsize=7, color='gray', ha='center', style='italic',
                 bbox=dict(boxstyle='round', facecolor='#f0f0f0', alpha=0.7))

    fig.suptitle("Figure 9: HVAC System Flow Diagrams",
                 fontsize=14, fontweight='bold', color=COLORS["primary"], y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    path = OUTPUT_DIR / "fig9_flow_diagram.png"
    plt.savefig(path, dpi=180, bbox_inches='tight')
    plt.close()
    return path