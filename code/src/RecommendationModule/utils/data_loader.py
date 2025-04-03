import pandas as pd
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
DATA_FOLDER = os.path.join(BASE_DIR, "Data")
def load_data():
    # Load Customer Data
    excel_file = os.path.join(DATA_FOLDER, "CustomerData.xlsx")
    customer_transactions = pd.read_excel(excel_file, sheet_name="Transaction history")
    individual_profiles = pd.read_excel(excel_file, sheet_name="Customer Profile (Individual)")
    org_profiles = pd.read_excel(excel_file, sheet_name="Customer Profile (Organisation)")
    social_media = pd.read_excel(excel_file, sheet_name="Social Media Sentiment")

    # Load Local Providers Data
    providers = pd.read_excel(os.path.join(DATA_FOLDER, "LocalProviders.xlsx"), sheet_name="Sheet1")

    return customer_transactions, individual_profiles, org_profiles, social_media, providers

