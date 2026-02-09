import pandas as pd

# 读取原 CSV，只取前两列（instruction 和 output）
df = pd.read_csv('backoffice_h2o_llm_studio_dataset.csv',
                 usecols=[0, 1])  # 只读第0列和第1列（instruction, output）

print("原行数:", len(df))

# 去重（基于 instruction 和 output）
df_unique = df.drop_duplicates(subset=['instruction', 'output'])

print("去重后行数:", len(df_unique))

# 保存时明确指定列名，避免 unnamed 列
df_unique.to_csv('cleaned_dataset.csv', index=False, columns=['instruction', 'output'])

print("已保存 cleaned_dataset.csv，只包含 instruction 和 output 两列。")