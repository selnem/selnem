"""metrics indepth 모드에서 언어 색이 회색으로 나오는 문제를 후처리로 보정한다."""
import re
import sys

COLORS = {
    "java": "#b07219",
    "kotlin": "#A97BFF",
    "plpgsql": "#336790",
    "shell": "#89e051",
    "python": "#3572A5",
    "javascript": "#f1e05a",
    "css": "#563d7c",
    "dockerfile": "#384d54",
    "jinja": "#a52a2a",
    "procfile": "#3A4EAD",
    "html": "#e34c26",
    "typescript": "#3178c6",
    "c": "#555555",
    "c++": "#f34b7d",
    "jupyter notebook": "#DA5B0B",
    "cmake": "#DA3434",
}

DOT = r'd="M8 4a4 4 0 100 8 4 4 0 000-8z"/>'

path = sys.argv[1]
with open(path, encoding="utf-8") as f:
    svg = f.read()

# 1) 범례 점 색: <path fill="#xxx" ... /></svg> 뒤에 언어 이름이 온다
legend_re = re.compile(
    r'(<path fill=")(#[0-9a-fA-F]{6})(" fill-rule="evenodd" ' + DOT +
    r'\s*</svg>\s*)([A-Za-z+#][^<\n]*)'
)

def legend_sub(m):
    color = COLORS.get(m.group(4).strip().lower())
    if not color:
        return m.group(0)
    return m.group(1) + color + m.group(3) + m.group(4)

svg = legend_re.sub(legend_sub, svg)

# 2) 언어별 퍼센트를 읽어 막대 순서(내림차순)를 계산
entries = re.findall(
    DOT + r'\s*</svg>\s*([A-Za-z+#][^<\n]*)\s*</div>\s*<small>\s*<div>([\d.]+)%',
    svg,
)
order = sorted(((n.strip(), float(p)) for n, p in entries), key=lambda x: -x[1])

# 3) 막대 rect를 순서대로 색칠 (캘린더 셀은 mask 속성이 없어 안전)
bar_re = re.compile(
    r'(<rect mask="url\(#languages-bar\)" x="[^"]+" y="[^"]+" width="([^"]+)" height="[^"]+" fill=")(#[0-9a-fA-F]{6})("/>)'
)
idx = 0

def bar_sub(m):
    global idx
    try:
        width = float(m.group(2))
    except ValueError:
        width = 0
    if width <= 0:
        return m.group(0)
    color = None
    if idx < len(order):
        color = COLORS.get(order[idx][0].lower())
    idx += 1
    return m.group(1) + (color or m.group(3)) + m.group(4)

svg = bar_re.sub(bar_sub, svg)

with open(path, "w", encoding="utf-8") as f:
    f.write(svg)

print(f"legend entries: {len(entries)}, bar rects recolored: {idx}")
