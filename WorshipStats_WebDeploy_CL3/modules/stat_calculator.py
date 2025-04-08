import pandas as pd
from collections import Counter, defaultdict

def split_names(value):
    if pd.isna(value): return []
    return [n.strip() for n in str(value).split("/") if n.strip() not in ["", "NaN", "暫停"]]

def flatten_people(df):
    melted = df.drop(columns=['聚會名稱', '來源檔案'], errors='ignore')
    names = melted.values.flatten()
    all_names = []
    for cell in names:
        all_names.extend(split_names(cell))
    return Counter(all_names)

def calculate_statistics(df, weights):
    counts = flatten_people(df)
    df_people = pd.DataFrame(counts.items(), columns=["姓名", "總次數"])

    # 類型分類規則
    type_keywords = {
        "禱告會": ["禱告會"],
        "主日崇拜": ["三民早堂", "美河堂"],
        "青年主日": ["青年主日"],
        "QQ堂": ["QQ", "大Q"],
        "英文崇拜": ["英文崇拜"],
        "早上飽": ["早上飽"]
    }

    source_counter = defaultdict(lambda: defaultdict(int))
    for _, row in df.iterrows():
        gathering = str(row["聚會名稱"])
        weight = 0
        match_type = None
        for t, keys in type_keywords.items():
            if any(k in gathering for k in keys):
                weight = weights.get(t, 1)
                match_type = t
                break
        if weight == 0: continue

        for name in row.drop(labels=["聚會名稱", "來源檔案"], errors='ignore'):
            for n in split_names(name):
                source_counter[n][match_type] += weight

    # 建立明細表（含原始與加權）
    raw_df = pd.DataFrame.from_dict(source_counter, orient='index').fillna(0).astype(float)
    source_df = raw_df.copy()
    for col in source_df.columns:
        if col in weights:
            source_df[col] *= weights[col]
    source_df = source_df.round(2)
    source_df["加權總分"] = source_df.sum(axis=1)
    source_df = source_df.reset_index().rename(columns={"index": "姓名"})
    raw_df = raw_df.reset_index().rename(columns={"index": "姓名"})
    source_df = pd.merge(raw_df, source_df, on="姓名", suffixes=("_原始", "_加權"))

    # 整體加權分數與篩選
    df_people = pd.merge(df_people, source_df[["姓名", "加權總分"]], on="姓名", how="left")
    df_people = df_people.rename(columns={"加權總分": "加權分數"})

    median = df_people["總次數"].median()
    potential = df_people[(df_people["總次數"] <= median) & (df_people["總次數"] >= 2)].copy()
    heavy = df_people[(df_people["加權分數"] > df_people["加權分數"].quantile(0.9)) | (df_people["總次數"] > 15)].copy()

    return df_people, potential, heavy, source_df
