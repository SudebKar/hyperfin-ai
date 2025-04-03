import pandas as pd
import os
# LocalProviders.xlsx schema is below
# resource_id	resource_type	name	description	eligibility_criteria	location	services_offered	contact_information	keywords	organization_types

# Transaction history schema is below
# Customer_Id	Product_Id	Transaction Type	Category	Amount (In Dollars)	Purchase_Date	Payment Mode

# customer profile (individual) schema is below
# Customer_id	Age	Gender	Location	Interests	Preferences	Income per	Education	Occupation

# customer profile (organization) schema is below
# Customer_Id	Industry	Financial Needs	Preferences	Revenue (in Dollars)	No. of employees

# Social Media Sentiment schema is below
# Customer_Id	Post_Id	Platform	Content	Timestamp	Sentiment_Score	Intent
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
DATA_FOLDER = os.path.join(BASE_DIR, "Data")

def load_data():
    try:
        df_resources = pd.read_excel( os.path.join(DATA_FOLDER, "LocalProviders.xlsx"))
    except FileNotFoundError:
        print("Error: LocalProviders.xlsx not found.")
        df_resources = pd.DataFrame()  # Create an empty DataFrame to continue

    try:
        excel_file = os.path.join(DATA_FOLDER, "CustomerData.xlsx")
        df_organizations = pd.read_excel(excel_file, sheet_name="Customer Profile (Organisation)")
        df_personal_profiles = pd.read_excel(excel_file, sheet_name="Customer Profile (Individual)")
        df_sentiment = pd.read_excel(excel_file, sheet_name="Social Media Sentiment")
        df_purchase_history = pd.read_excel(excel_file, sheet_name="Transaction history")
    except FileNotFoundError:
        print(f"Error: {excel_file} not found.")
        df_organizations = pd.DataFrame()
        df_personal_profiles = pd.DataFrame()
        df_sentiment = pd.DataFrame()
        df_purchase_history = pd.DataFrame()

    print("All data loaded (or empty DataFrames created if files not found).")
    return df_resources, df_organizations, df_personal_profiles, df_sentiment, df_purchase_history

def filter_by_resource_type(df, resource_type):
    if 'resource_type' in df.columns:
        return df[df['resource_type'] == resource_type]
    else:
        print("Error: 'resource_type' column not found in DataFrame.")
        return pd.DataFrame()

def filter_by_location(df, location):
    if 'location' in df.columns:
        return df[df['location'] == location]
    else:
        print("Error: 'location' column not found in DataFrame.")
        return pd.DataFrame()

def filter_by_eligibility(df, eligibility):
    if 'eligibility_criteria' in df.columns:
        return df[df['eligibility_criteria'] == eligibility]
    else:
        print("Error: 'eligibility_criteria' column not found in DataFrame.")
        return pd.DataFrame()

def recommend_for_organization(df_resources, df_organizations, industry, size):
    if 'Industry' in df_organizations.columns and 'organization_types' in df_resources.columns and 'No. of employees' in df_organizations.columns:
        df_organizations['No. of employees'] = pd.to_numeric(df_organizations['No. of employees'], errors='coerce')
        relevant_orgs = df_organizations[(df_organizations['Industry'] == industry) & (df_organizations['No. of employees'] >= size)]
        df_resources['relevance'] = df_resources['organization_types'].apply(lambda x: 2 if x in relevant_orgs['Industry'].values else 1)
        df_resources.sort_values(by='relevance', ascending=False, inplace=True)
    else:
        print("Error: Required columns not found in DataFrames.")
        df_resources['relevance'] = 1

def recommend_for_personal_profile(df_resources, df_personal_profiles, role, financial_goals):
    if 'Occupation' in df_personal_profiles.columns and 'keywords' in df_resources.columns:
        relevant_profiles = df_personal_profiles[df_personal_profiles['Occupation'] == role]
        df_resources['relevance'] = df_resources['keywords'].apply(lambda x: 2 if financial_goals in x else 1)
        df_resources.sort_values(by='relevance', ascending=False, inplace=True)
    else:
        print("Error: Required columns not found in DataFrames.")
        df_resources['relevance'] = 1

def recommend_based_on_purchase_history(df_resources, df_purchase_history, customer_id):
    if 'Customer_Id' in df_purchase_history.columns and 'keywords' in df_resources.columns:
        past_purchases = df_purchase_history[df_purchase_history['Customer_Id'] == customer_id]
        df_resources['relevance'] = df_resources['keywords'].apply(lambda x: 2 if x in past_purchases['Category'].values else 1)
        df_resources.sort_values(by='relevance', ascending=False, inplace=True)
    else:
        print("Error: Required columns not found in DataFrames.")
        df_resources['relevance'] = 1

def recommend_based_on_sentiment(df_resources, df_sentiment, customer_id):
    if 'Customer_Id' in df_sentiment.columns and 'keywords' in df_resources.columns:
        customer_sentiment = df_sentiment[df_sentiment['Customer_Id'] == customer_id]
        positive_sentiment = customer_sentiment[customer_sentiment['Sentiment_Score'] > 0]
        df_resources['relevance'] = df_resources['keywords'].apply(lambda x: 2 if x in positive_sentiment['Intent'].values else 1)
        df_resources.sort_values(by='relevance', ascending=False, inplace=True)
    else:
        print("Error: Required columns not found in DataFrames.")
        df_resources['relevance'] = 1

def get_resource_recommendations(user_profile, search_query=None):
    """
    Retrieves and ranks resource recommendations based on user profile and search query.
    """
    # Load data
    df_resources, df_organizations, df_personal_profiles, df_sentiment, df_purchase_history = load_data()

    # Start with all resources
    recommendations_df = df_resources.copy()

    # Filter by search query (if provided)
    if search_query:
        recommendations_df = recommendations_df[recommendations_df['keywords'].str.contains(search_query, case=False, na=False)]

    # Filter by user profile (example: organization)
    if "organization_id" in user_profile:
        org_id = user_profile["organization_id"]
        org_profile = df_organizations[df_organizations["Customer_Id"] == org_id].iloc[0].to_dict()  # Get the org profile
        recommend_for_organization(recommendations_df, df_organizations, org_profile['Industry'], org_profile['No. of employees'])

    # Filter by user profile (example: personal profile)
    if "personal_id" in user_profile:
        personal_id = user_profile["personal_id"]
        personal_profile = df_personal_profiles[df_personal_profiles["Customer_id"] == personal_id].iloc[0].to_dict()  # Get the personal profile
        recommend_for_personal_profile(recommendations_df, df_personal_profiles, personal_profile['Occupation'], personal_profile['Preferences'])

    # Filter by user profile (example: purchase history)
    if "customer_id" in user_profile:
        customer_id = user_profile["customer_id"]
        recommend_based_on_purchase_history(recommendations_df, df_purchase_history, customer_id)

    # Filter by user profile (example: sentiment)
    if "customer_id" in user_profile:
        customer_id = user_profile["customer_id"]
        recommend_based_on_sentiment(recommendations_df, df_sentiment, customer_id)

    # Sort by relevance (or other criteria)
    recommendations_df = recommendations_df.sort_values(by='relevance', ascending=False)

    return recommendations_df

# Example usage:
user_profile = {"organization_id": "org_123", "personal_id": "pers_456", "customer_id": "cust_789"}  # Example user profile
recommendations = get_resource_recommendations(user_profile, search_query="business loans")
print(recommendations)