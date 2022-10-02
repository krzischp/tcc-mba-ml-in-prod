"""Creates BigQuery table"""
import pandas as pd

col_names = [
    "id",
    "image_id",
    "gender",
    "master_category",
    "sub_category",
    "article_type",
    "base_colour",
    "season",
    "year",
    "usage",
    "display_name",
]

df = pd.read_csv("../tmp/database/data.csv", names=col_names, header=None)
df.to_gbq(
    destination_table="tcc-lucas-pierre.tcc.products",
    project_id="tcc-lucas-pierre",
    if_exists="replace",
)
