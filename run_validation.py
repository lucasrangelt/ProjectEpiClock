import great_expectations as gx
import sys
import os
import requests
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)

ENV_HOST = os.getenv("ENV_HOST")
ENV_USER = os.getenv("ENV_USER")
ENV_PASSWORD = os.getenv("ENV_PASSWORD")
ENV_DATABASE = os.getenv("ENV_DATABASE")
ENV_PORT = os.getenv("ENV_PORT")
# ENV_DISCORD_WEBHOOK_URL = os.getenv("ENV_DISCORD_WEBHOOK_URL")

# def send_discord_alert(error_message):
#     data = {
#         "content": error_message,
#         "username": "PC GX Quality Bot" #You can customize the username that appears in Discord
#     }
#     try:
#         response = requests.post(ENV_DISCORD_WEBHOOK_URL, json=data)
#         response.raise_for_status()
#     except Exception as e:
#         print(f"Failed to send Discord alert: {e}")

def func():
    project_path = Path(__file__).parent.resolve()
    context = gx.get_context(project_root_dir=str(project_path))
    try:
        checkpoint = context.checkpoints.get("gx_data_quality_checkpoint")
    except KeyError:
        print("CHECKPOINT NOT FOUND. Run setup_gx.py first.")
        sys.exit(1)
    result = checkpoint.run()
    context.build_data_docs()
    if not result.success:
        error_message = "⚠️ ⚠️ ⚠️ ⚠️ ⚠️  Data quality warning: validations not passed. Check your GX html and dbt modelling.⚠️ ⚠️ ⚠️ ⚠️ ⚠️"
        print(error_message)
        # send_discord_alert(error_message)
        sys.exit(0)
    else:
        print("Data quality passed! Safe to trigger dbt.")
        sys.exit(0)

if __name__ == "__main__":
    func()