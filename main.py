from helper.paths import ProjectPaths

p = ProjectPaths()
df, p = next(p.get_gate_pickup_data())
print(df)
print(p)