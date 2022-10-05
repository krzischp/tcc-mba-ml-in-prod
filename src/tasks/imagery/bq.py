from google.cloud import bigquery

client = bigquery.Client()

query = f"""SELECT image_id,
                           gender,
                           master_category,
                           sub_category,
                           article_type,
                           base_colour,
                           season,
                           year,
                           usage,
                           display_name
                    FROM tcc.products
                    WHERE gender = 'Men' AND
                          sub_category = 'Shoes' AND
                          year = 2012
                    LIMIT 10
        """

query_job = client.query(query).result()
for row in query_job:
    # Row values can be accessed by field name or index.
    print(row)
