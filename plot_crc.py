"""CRC 시뮬레이션 결과 시각화 (matplotlib)."""
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

plt.rcParams["font.family"] = "Apple SD Gothic Neo"   # macOS 한글 폰트
plt.rcParams["axes.unicode_minus"] = False

SURFACE = "#fcfcfb"
TEXT = "#0b0b0b"
TEXT_2 = "#52514e"
GRID = "#e6e5e0"
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]   # 생성 다항식별 고정 색


def _style(ax):
    ax.set_facecolor(SURFACE)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(TEXT_2)
    ax.tick_params(colors=TEXT_2, length=0)
    ax.yaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def plot_results(results, generators, trials, path="crc_results.png", show=True):
    """results: {다항식 이름: {오류 유형: 검출률(%)}}"""
    names = list(results)
    error_types = list(next(iter(results.values())))
    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(12, 10), gridspec_kw={"height_ratios": [1.1, 1]}, facecolor=SURFACE)

    # (1) 오류 유형별 미검출률 — 그룹 막대
    width = 0.8 / len(names)
    for i, name in enumerate(names):
        misses = [100 - results[name][e] for e in error_types]
        xs = [x + (i - (len(names) - 1) / 2) * width for x in range(len(error_types))]
        ax1.bar(xs, misses, width * 0.9, color=SERIES[i], label=name)
        for x, m in zip(xs, misses):
            label = f"{m:.2f}" if m >= 0.1 else ("0" if m == 0 else f"{m:.3f}")
            ax1.text(x, m + 0.08, label, ha="center", va="bottom", fontsize=8, color=TEXT_2)
    _style(ax1)
    ax1.set_xticks(range(len(error_types)), error_types, color=TEXT)
    ax1.set_ylabel("미검출률 (%)", color=TEXT_2)
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}%"))
    ax1.set_title(f"오류 유형별 미검출률 (낮을수록 좋음, 유형별 {trials:,}회)",
                  loc="left", color=TEXT, fontsize=13, pad=12)
    ax1.legend(frameon=False, ncol=len(names), loc="upper left", labelcolor=TEXT)

    # (2) 체크섬 길이별 전체 미검출 건수 — 로그 스케일
    total = trials * len(error_types)
    floor = 100 / total   # 1건 미검출에 해당하는 비율
    for i, name in enumerate(names):
        missed = round(sum(100 - results[name][e] for e in error_types) * trials / 100)
        rate = missed / total * 100
        if missed > 0:
            ax2.bar(i, rate, 0.6, color=SERIES[i])
            ax2.text(i, rate * 1.15, f"{missed:,}건 ({rate:.3g}%)", ha="center", va="bottom",
                     fontsize=10, color=TEXT)
        else:
            ax2.text(i, floor * 0.6, "0건", ha="center", va="bottom", fontsize=10, color=TEXT)
    _style(ax2)
    ax2.set_yscale("log")
    ax2.set_ylim(floor * 0.4, 10)
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}%"))
    ax2.set_xticks(range(len(names)),
                   [f"{name}\n체크섬 {len(generators[name]) - 1}비트" for name in names], color=TEXT)
    ax2.set_ylabel("전체 미검출률 (%, 로그)", color=TEXT_2)
    ax2.set_title(f"체크섬 길이별 전체 미검출 건수 (다항식별 {total:,}회)",
                  loc="left", color=TEXT, fontsize=13, pad=12)

    fig.tight_layout(h_pad=3)
    fig.savefig(path, dpi=150, facecolor=SURFACE)
    print(f"\n그래프 저장: {path}")
    if show:
        plt.show()
