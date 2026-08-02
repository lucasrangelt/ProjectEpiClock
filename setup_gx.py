##### initial setup:

import great_expectations as gx
from great_expectations.exceptions import DataContextError
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)

ENV_HOST = os.getenv("ENV_HOST")
ENV_USER = os.getenv("ENV_USER")
ENV_PASSWORD = os.getenv("ENV_PASSWORD")
ENV_DATABASE = os.getenv("ENV_DATABASE")
ENV_PORT = os.getenv("ENV_PORT")

context = gx.get_context(project_root_dir="./")

##### sources:

try:
    datasource = context.data_sources.get("my_postgres_db")
except KeyError:
    datasource = context.data_sources.add_postgres(
        name = "my_postgres_db",
        connection_string = f"postgresql+psycopg2://{ENV_USER}:{ENV_PASSWORD}@{ENV_HOST}:{ENV_PORT}/{ENV_DATABASE}"
    )
    
try:
    asset = datasource.get_asset("gx_stg_data")
except LookupError:
    datasource.add_table_asset(name="gx_stg_data", table_name="my_dbt_schema.stg_data")

##### suites:

suite_name = "data_quality_suite"

try:
    suite = context.suites.get(suite_name)
except DataContextError:
    suite = context.suites.add(gx.ExpectationSuite(name=suite_name))

suite.add_expectation(gx.expectations.ExpectColumnValuesToNotBeNull(column="full_title"))
suite.add_expectation(gx.expectations.ExpectColumnValuesToBeBetween(column="price", min_value=100, max_value=50000))
suite.add_expectation(gx.expectations.ExpectColumnValuesToBeBetween(column="rating", min_value=0))

##### checkpoints:

checkpoint_name = "gx_data_quality_checkpoint"

try:
    checkpoint = context.checkpoints.get(checkpoint_name)
except DataContextError:
    vd = context.validation_definitions.add(gx.ValidationDefinition(
        name="my_validation",
        data=asset.add_batch_definition_whole_table("whole_table_batch"),
        suite=suite
    ))

    checkpoint = context.checkpoints.add(gx.Checkpoint(name=checkpoint_name, validation_definitions=[vd]))