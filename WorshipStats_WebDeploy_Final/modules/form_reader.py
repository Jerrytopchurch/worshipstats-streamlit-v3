
import pandas as pd

def read_worship_form(filepath, month_tag):
    df = pd.read_excel(filepath, sheet_name=None)
    all_data = []
    for sheet_name, sheet_df in df.items():
        try:
            role_names = sheet_df.iloc[3:, 0].reset_index(drop=True)
            data = sheet_df.iloc[3:, 1:]
            data.columns = sheet_df.iloc[0, 1:]
            data = data.reset_index(drop=True)
            data.index = [f"row_{i}" for i in range(len(data))]
            melted = data.T.reset_index()
            melted.columns = ["聚會名稱"] + list(role_names)
            melted["月份"] = month_tag
            all_data.append(melted)
        except Exception as e:
            print(f"⚠️ 無法處理工作表：{sheet_name}，原因：{e}")
    return pd.concat(all_data, ignore_index=True)
