import os
from textwrap import fill

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np


def shadow_box(ax, x, y, w, h, title, subtitle, color, title_size=10, subtitle_size=8.8):
    shadow = FancyBboxPatch(
        (x + 0.004, y - 0.004),
        w,
        h,
        boxstyle="round,pad=0.012,rounding_size=0.012",
        linewidth=0.0,
        facecolor="#1a202c",
        alpha=0.12,
        zorder=1,
    )
    ax.add_patch(shadow)

    box = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.012,rounding_size=0.012",
        linewidth=1.4,
        edgecolor=color,
        facecolor="#ffffff",
        alpha=0.98,
        zorder=2,
    )
    ax.add_patch(box)

    ax.text(x + 0.012, y + h - 0.015, fill(title, 24), ha="left", va="top", fontsize=title_size, color="#0f172a", fontweight="bold", zorder=3)
    if subtitle:
        ax.text(x + 0.012, y + h - 0.050, fill(subtitle, 34), ha="left", va="top", fontsize=subtitle_size, color="#334155", zorder=3)


def label_chip(ax, x, y, text, color):
    chip = FancyBboxPatch(
        (x, y),
        0.09,
        0.025,
        boxstyle="round,pad=0.008,rounding_size=0.01",
        linewidth=0.0,
        facecolor=color,
        alpha=0.14,
        zorder=2,
    )
    ax.add_patch(chip)
    ax.text(x + 0.045, y + 0.0125, text, ha="center", va="center", fontsize=8, color="#1f2937", zorder=3)


def connector(ax, x1, y1, x2, y2, color, text=None):
    ax.annotate(
        "",
        xy=(x2, y2),
        xytext=(x1, y1),
        arrowprops=dict(arrowstyle="-|>", lw=2.2, color=color, shrinkA=6, shrinkB=6),
        zorder=2,
    )
    if text:
        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2
        ax.text(mx, my + 0.015, text, ha="center", va="bottom", fontsize=8.5, color="#334155", zorder=3)


def main():
    out_dir = "docks"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "docks-router-api-architecture.png")
    out_path_pro = os.path.join(out_dir, "router-api-architecture-professional.png")
    out_path_luxe = os.path.join(out_dir, "router-api-architecture-luxury.png")
    out_path_beautiful = os.path.join(out_dir, "router-api-architecture-beautiful.png")

    fig, ax = plt.subplots(figsize=(16, 9), dpi=200)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    fig.patch.set_facecolor("#f8fafc")
    ax.set_facecolor("#f8fafc")

    colors = {
        "net": "#2563eb",
        "compute": "#16a34a",
        "ai": "#7c3aed",
        "target": "#0f766e",
        "security": "#d97706",
        "obs": "#475569",
        "cicd": "#db2777",
        "env": "#0891b2",
    }
    ax.text(0.04, 0.955, "Router API - Production AWS Architecture", ha="left", va="top", fontsize=23, color="#0f172a", fontweight="bold")
    ax.text(0.04, 0.922, "Hybrid request routing with Bedrock fallback and environment promotion", ha="left", va="top", fontsize=11.5, color="#475569")

    # Main request flow
    shadow_box(ax, 0.04, 0.59, 0.14, 0.13, "Client", "Web / Mobile / Service Consumers", colors["net"])
    shadow_box(ax, 0.22, 0.57, 0.18, 0.16, "API Gateway", "HTTP API\nRoute: ANY /router", colors["net"])
    shadow_box(ax, 0.44, 0.52, 0.19, 0.21, "Router Lambda", "Python 3.11\nRequest parsing + routing orchestration", colors["compute"])
    label_chip(ax, 0.47, 0.665, "Compute", colors["compute"])

    shadow_box(ax, 0.67, 0.71, 0.27, 0.10, "Rule-based Router", "GET -> get, POST create/update", colors["compute"])
    shadow_box(ax, 0.67, 0.58, 0.27, 0.10, "Bedrock Fallback", "Claude 3 Sonnet decides target + endpoint_type", colors["ai"])

    # Target lane
    shadow_box(ax, 0.67, 0.36, 0.27, 0.18, "Target Lambdas", "get, create, update\npublic + private variants", colors["target"])
    label_chip(ax, 0.84, 0.495, "Targets", colors["target"])

    # Supporting controls
    shadow_box(ax, 0.04, 0.32, 0.28, 0.14, "CloudWatch Observability", "Structured logs for API Gateway + Lambdas", colors["obs"])
    shadow_box(ax, 0.35, 0.32, 0.26, 0.14, "IAM Least Privilege", "bedrock:InvokeModel\nlambda:InvokeFunction (scoped)", colors["security"])
    shadow_box(ax, 0.64, 0.32, 0.30, 0.14, "GitHub Actions + Terraform", "init -> validate -> plan -> apply\nOIDC auth to AWS", colors["cicd"])

    shadow_box(ax, 0.04, 0.10, 0.40, 0.14, "Terraform Modules", "iam module | lambda module | api_gateway module", colors["cicd"])
    shadow_box(ax, 0.47, 0.10, 0.47, 0.14, "Environment Promotion", "develop -> dev\nmain -> int -> prod (manual approval)", colors["env"])

    # Main connectors
    connector(ax, 0.18, 0.655, 0.22, 0.655, colors["net"])
    connector(ax, 0.40, 0.655, 0.44, 0.655, colors["net"])
    connector(ax, 0.63, 0.655, 0.67, 0.75, colors["compute"], "Rule match")
    connector(ax, 0.63, 0.62, 0.67, 0.62, colors["ai"], "Fallback")
    connector(ax, 0.81, 0.71, 0.81, 0.54, colors["target"])
    connector(ax, 0.81, 0.58, 0.81, 0.54, colors["target"])

    # Support connectors
    connector(ax, 0.53, 0.52, 0.47, 0.46, colors["security"])
    connector(ax, 0.50, 0.52, 0.20, 0.46, colors["obs"])
    connector(ax, 0.76, 0.32, 0.76, 0.24, colors["cicd"])
    connector(ax, 0.58, 0.17, 0.68, 0.17, colors["env"])

    # Legend panel
    legend = FancyBboxPatch((0.79, 0.86), 0.17, 0.10, boxstyle="round,pad=0.01,rounding_size=0.01", linewidth=1.0, edgecolor="#cbd5e1", facecolor="#ffffff", alpha=0.98)
    ax.add_patch(legend)
    ax.text(0.875, 0.948, "Legend", ha="center", va="top", fontsize=10, fontweight="bold", color="#0f172a")
    items = [("Network", colors["net"]), ("Compute", colors["compute"]), ("AI", colors["ai"]), ("Security", colors["security"]), ("CI/CD", colors["cicd"])]
    for i, (txt, clr) in enumerate(items):
        y = 0.932 - (i * 0.017)
        ax.add_patch(FancyBboxPatch((0.802, y - 0.008), 0.018, 0.010, boxstyle="round,pad=0.004", linewidth=0, facecolor=clr, alpha=0.22))
        ax.text(0.825, y - 0.002, txt, ha="left", va="center", fontsize=8.3, color="#334155")

    plt.tight_layout()
    fig.savefig(out_path, bbox_inches="tight")
    fig.savefig(out_path_pro, bbox_inches="tight")
    plt.close(fig)

    # Luxury variant
    fig2, ax2 = plt.subplots(figsize=(16, 9), dpi=220)
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)
    ax2.axis("off")

    # Dark gradient background
    x = np.linspace(0, 1, 1200)
    y = np.linspace(0, 1, 700)
    xv, yv = np.meshgrid(x, y)
    grad = 0.25 + 0.75 * (1 - ((xv - 0.15) ** 2 + (yv - 0.2) ** 2))
    grad = np.clip(grad, 0, 1)
    c0 = np.array([9, 14, 28]) / 255.0
    c1 = np.array([26, 39, 70]) / 255.0
    img = c0[None, None, :] * (1 - grad[..., None]) + c1[None, None, :] * grad[..., None]
    ax2.imshow(img, extent=[0, 1, 0, 1], origin="lower", aspect="auto")

    def luxe_box(x, y, w, h, title, subtitle, edge="#d4af37", fill_alpha=0.12):
        sh = FancyBboxPatch((x + 0.004, y - 0.004), w, h, boxstyle="round,pad=0.012,rounding_size=0.018", linewidth=0, facecolor="#020617", alpha=0.45, zorder=1)
        ax2.add_patch(sh)
        b = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012,rounding_size=0.018", linewidth=1.3, edgecolor=edge, facecolor="#ffffff", alpha=fill_alpha, zorder=2)
        ax2.add_patch(b)
        ax2.text(x + 0.014, y + h - 0.014, fill(title, 24), ha="left", va="top", fontsize=11, fontweight="bold", color="#f8fafc", zorder=3)
        if subtitle:
            ax2.text(x + 0.014, y + h - 0.05, fill(subtitle, 36), ha="left", va="top", fontsize=9, color="#cbd5e1", zorder=3)

    def luxe_arrow(x1, y1, x2, y2, text=None):
        ax2.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="-|>", lw=2.4, color="#d4af37", shrinkA=7, shrinkB=7), zorder=2)
        if text:
            ax2.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.013, text, ha="center", va="bottom", fontsize=8.5, color="#f8fafc")

    ax2.text(0.04, 0.955, "Router API | Elite Cloud Architecture", ha="left", va="top", fontsize=24, color="#f8fafc", fontweight="bold")
    ax2.text(0.04, 0.92, "High-availability routing with Bedrock intelligence and secure Terraform delivery", ha="left", va="top", fontsize=11, color="#cbd5e1")

    luxe_box(0.04, 0.60, 0.14, 0.12, "Client Layer", "Web apps, mobile apps,\nB2B integrations")
    luxe_box(0.22, 0.58, 0.18, 0.15, "API Gateway", "HTTP API\nANY /router")
    luxe_box(0.44, 0.52, 0.19, 0.21, "Router Lambda", "Python 3.11\nHybrid routing brain")
    luxe_box(0.67, 0.70, 0.27, 0.10, "Rule Engine", "GET -> get\nPOST create/update")
    luxe_box(0.67, 0.57, 0.27, 0.10, "Bedrock AI Decision", "Claude 3 Sonnet\nJSON route resolution")
    luxe_box(0.67, 0.35, 0.27, 0.18, "Target Lambda Fleet", "get / create / update\npublic + private endpoints")

    luxe_box(0.04, 0.31, 0.28, 0.14, "CloudWatch Telemetry", "Structured logs, diagnostics,\nerror insights")
    luxe_box(0.35, 0.31, 0.26, 0.14, "IAM Security", "Least privilege roles\ninvoke-only permissions")
    luxe_box(0.64, 0.31, 0.30, 0.14, "CI/CD Orchestration", "GitHub Actions + OIDC\ninit > validate > plan > apply")
    luxe_box(0.04, 0.09, 0.40, 0.14, "Terraform Modules", "iam | lambda | api_gateway")
    luxe_box(0.47, 0.09, 0.47, 0.14, "Promotion Path", "develop -> dev\nmain -> int -> prod (approval gate)")

    luxe_arrow(0.18, 0.66, 0.22, 0.66)
    luxe_arrow(0.40, 0.66, 0.44, 0.66)
    luxe_arrow(0.63, 0.66, 0.67, 0.75, "Rule hit")
    luxe_arrow(0.63, 0.62, 0.67, 0.62, "AI fallback")
    luxe_arrow(0.80, 0.70, 0.80, 0.53)
    luxe_arrow(0.80, 0.57, 0.80, 0.53)
    luxe_arrow(0.53, 0.52, 0.46, 0.45)
    luxe_arrow(0.50, 0.52, 0.22, 0.45)
    luxe_arrow(0.78, 0.31, 0.78, 0.23)
    luxe_arrow(0.58, 0.16, 0.68, 0.16)

    # Gold separators
    ax2.plot([0.03, 0.97], [0.86, 0.86], color="#d4af37", alpha=0.35, lw=1.1)
    ax2.plot([0.03, 0.97], [0.27, 0.27], color="#d4af37", alpha=0.25, lw=1.0)

    plt.tight_layout()
    fig2.savefig(out_path_luxe, bbox_inches="tight")
    plt.close(fig2)

    # Beautiful light premium variant
    fig3, ax3 = plt.subplots(figsize=(16, 9), dpi=220)
    ax3.set_xlim(0, 1)
    ax3.set_ylim(0, 1)
    ax3.axis("off")

    # Soft pastel background gradient
    x3 = np.linspace(0, 1, 1200)
    y3 = np.linspace(0, 1, 700)
    xv3, yv3 = np.meshgrid(x3, y3)
    g1 = np.exp(-((xv3 - 0.18) ** 2 + (yv3 - 0.8) ** 2) / 0.16)
    g2 = np.exp(-((xv3 - 0.85) ** 2 + (yv3 - 0.25) ** 2) / 0.24)
    base = np.clip(0.35 * g1 + 0.28 * g2, 0, 1)
    b0 = np.array([247, 250, 255]) / 255.0
    b1 = np.array([235, 244, 255]) / 255.0
    img3 = b0[None, None, :] * (1 - base[..., None]) + b1[None, None, :] * base[..., None]
    ax3.imshow(img3, extent=[0, 1, 0, 1], origin="lower", aspect="auto")

    palette = {
        "line": "#2563eb",
        "box_edge": "#bfdbfe",
        "title": "#0f172a",
        "subtitle": "#334155",
        "accent1": "#4f46e5",
        "accent2": "#0ea5e9",
        "accent3": "#10b981",
        "accent4": "#f59e0b",
    }

    def glass_box(x, y, w, h, title, subtitle, accent):
        sh = FancyBboxPatch((x + 0.003, y - 0.004), w, h, boxstyle="round,pad=0.012,rounding_size=0.02", linewidth=0, facecolor="#1e293b", alpha=0.10, zorder=1)
        ax3.add_patch(sh)
        bg = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012,rounding_size=0.02", linewidth=1.1, edgecolor=palette["box_edge"], facecolor="#ffffff", alpha=0.82, zorder=2)
        ax3.add_patch(bg)
        top = FancyBboxPatch((x, y + h - 0.010), w, 0.010, boxstyle="round,pad=0.00,rounding_size=0.006", linewidth=0, facecolor=accent, alpha=0.85, zorder=3)
        ax3.add_patch(top)
        ax3.text(x + 0.012, y + h - 0.015, fill(title, 24), ha="left", va="top", fontsize=11, color=palette["title"], fontweight="bold", zorder=4)
        ax3.text(x + 0.012, y + h - 0.050, fill(subtitle, 38), ha="left", va="top", fontsize=8.9, color=palette["subtitle"], zorder=4)

    def curve_arrow(x1, y1, x2, y2, rad=0.0, text=None):
        ax3.annotate(
            "",
            xy=(x2, y2),
            xytext=(x1, y1),
            arrowprops=dict(arrowstyle="-|>", lw=2.0, color=palette["line"], shrinkA=8, shrinkB=8, connectionstyle=f"arc3,rad={rad}"),
            zorder=3,
        )
        if text:
            ax3.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.014, text, ha="center", va="bottom", fontsize=8.4, color="#1e3a8a", zorder=4)

    ax3.text(0.04, 0.955, "Router API - Architecture View", ha="left", va="top", fontsize=23, color=palette["title"], fontweight="bold")
    ax3.text(0.04, 0.922, "Elegant production blueprint for API routing, AI fallback, security and CI/CD promotion", ha="left", va="top", fontsize=11.2, color=palette["subtitle"])

    glass_box(0.04, 0.60, 0.14, 0.12, "Client", "Consumers across web,\nmobile and services", palette["accent2"])
    glass_box(0.22, 0.58, 0.18, 0.15, "API Gateway", "HTTP API\nANY /router", palette["accent1"])
    glass_box(0.44, 0.52, 0.19, 0.21, "Router Lambda", "Python 3.11\nHybrid rule + LLM routing", palette["accent3"])
    glass_box(0.67, 0.70, 0.27, 0.10, "Rule Engine", "Fast deterministic routing", palette["accent3"])
    glass_box(0.67, 0.57, 0.27, 0.10, "Bedrock Decision", "Claude Sonnet fallback", palette["accent1"])
    glass_box(0.67, 0.35, 0.27, 0.18, "Target Lambda Suite", "GET / CREATE / UPDATE\npublic + private handlers", palette["accent2"])

    glass_box(0.04, 0.31, 0.28, 0.14, "CloudWatch Logs", "Traceable structured logs\nfor request lifecycle", palette["accent2"])
    glass_box(0.35, 0.31, 0.26, 0.14, "IAM", "Least privilege controls\ninvoke-only permissions", palette["accent4"])
    glass_box(0.64, 0.31, 0.30, 0.14, "GitHub Actions + Terraform", "init -> validate -> plan -> apply", palette["accent1"])
    glass_box(0.04, 0.09, 0.40, 0.14, "Terraform Modules", "iam | lambda | api_gateway", palette["accent4"])
    glass_box(0.47, 0.09, 0.47, 0.14, "Promotion Flow", "dev -> int -> prod with approval gates", palette["accent3"])

    curve_arrow(0.18, 0.66, 0.22, 0.66)
    curve_arrow(0.40, 0.66, 0.44, 0.66)
    curve_arrow(0.63, 0.66, 0.67, 0.75, rad=0.15, text="rule path")
    curve_arrow(0.63, 0.62, 0.67, 0.62, rad=0.0, text="LLM fallback")
    curve_arrow(0.80, 0.70, 0.80, 0.53)
    curve_arrow(0.80, 0.57, 0.80, 0.53)
    curve_arrow(0.53, 0.52, 0.47, 0.45, rad=-0.12)
    curve_arrow(0.50, 0.52, 0.22, 0.45, rad=0.12)
    curve_arrow(0.78, 0.31, 0.78, 0.23)
    curve_arrow(0.58, 0.16, 0.68, 0.16, rad=0.05)

    # Decorative divider lines
    ax3.plot([0.03, 0.97], [0.86, 0.86], color="#93c5fd", alpha=0.35, lw=1.0)
    ax3.plot([0.03, 0.97], [0.27, 0.27], color="#93c5fd", alpha=0.30, lw=1.0)

    plt.tight_layout()
    fig3.savefig(out_path_beautiful, bbox_inches="tight")
    plt.close(fig3)

    print(f"Diagram written to: {out_path}")
    print(f"Diagram written to: {out_path_pro}")
    print(f"Diagram written to: {out_path_luxe}")
    print(f"Diagram written to: {out_path_beautiful}")


if __name__ == "__main__":
    main()

