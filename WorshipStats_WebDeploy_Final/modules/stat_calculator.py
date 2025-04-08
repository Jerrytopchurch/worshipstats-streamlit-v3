
import pandas as pd
from collections import Counter

TYPE_WEIGHTS = {
    "禱告會": 3,
    "主日崇拜": 4,
    "青年主日": 4,
    "QQ": 1,
    "英文崇拜": 1,
    "大Q": 1,
}

TYPE_KEYWORDS = {
    "禱告會": ["禱告會"],
    "青年主日": ["青年主日"],
    "主日崇拜": ["三民早堂", "美河堂"],
    "QQ": ["QQ"],
    "英文崇拜": ["英文崇拜"],
    "大Q": ["大Q"]
}

def clean_and_expand(df):
    expanded_rows = []
    for _, row in df.iterrows():
        for col in row.index:
            if col not in ["聚會名稱", "月份"]:
                cell = row[col]
                if pd.notna(cell):
                    for name in str(cell).split("/"):
                        name = name.strip()
                        if name and name not in ["NaN", "暫停"]:
                            new_row = {"姓名": name, "聚會名稱": row["聚會名稱"], "月份": row["月份"], "角色": col}
                            expanded_rows.append(new_row)
    return pd.DataFrame(expanded_rows)

def calculate_stats(flat_df):
    # 計算每月次數
    monthly = pd.crosstab(flat_df["姓名"], flat_df["月份"])
    monthly["總次數"] = monthly.sum(axis=1)

    # 計算加權
    weighted = Counter()
    early_bonus = Counter()
    md = Counter()
    bl = Counter()
    vl = Counter()

    for _, row in flat_df.iterrows():
        name = row["姓名"]
        role = row["角色"]
        meeting = str(row["聚會名稱"])

        # 類型加權
        for key, keywords in TYPE_KEYWORDS.items():
            if any(k in meeting for k in keywords):
                weighted[name] += TYPE_WEIGHTS[key]

        # 早上飽加權
        if "早上飽" in meeting:
            early_bonus[name] += 2

        # 特殊角色
        if "MD" in role: md[name] += 1
        if "Band Leader" in role: bl[name] += 1
        if "Vocal Leader" in role: vl[name] += 1

    summary = pd.DataFrame({
        "姓名": list(set(flat_df["姓名"])),
        "加權分數": [weighted[n] for n in flat_df["姓名"].unique()],
        "早上飽加權": [early_bonus[n] for n in flat_df["姓名"].unique()],
        "MD次數": [md[n] for n in flat_df["姓名"].unique()],
        "Band Leader次數": [bl[n] for n in flat_df["姓名"].unique()],
        "Vocal Leader次數": [vl[n] for n in flat_df["姓名"].unique()],
    })
    summary["角色加權"] = 0.5 * (summary["MD次數"] + summary["Band Leader次數"] + summary["Vocal Leader次數"])
    summary["加權總分"] = summary["加權分數"] + summary["早上飽加權"] + summary["角色加權"]

    return monthly.reset_index(), summary
