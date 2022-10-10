"""Creates BigQuery dataset"""
from google.cloud import bigquery

# Construct a BigQuery client object.
client = bigquery.Client(project="tcc-lucas-pierre")

dataset_id = f"{client.project}.tcc"

# Construct a full Dataset object to send to the API.
dataset = bigquery.Dataset(dataset_id)
dataset.location = "US"

# Send the dataset to the API for creation, with an explicit timeout.
# Raises google.api_core.exceptions.Conflict if the Dataset already
# exists within the project.
dataset = client.create_dataset(dataset, timeout=30)  # Make an API request.
print(f"Created dataset {client.project}.{dataset.dataset_id}")
