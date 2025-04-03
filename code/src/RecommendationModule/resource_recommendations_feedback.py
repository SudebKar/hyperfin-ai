import pandas as pd
import os
# --- Data Loading (as in your code) ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
DATA_FOLDER = os.path.join(BASE_DIR, "Data")
def load_data():
    try:
        df_resources = pd.read_excel( os.path.join(DATA_FOLDER, "LocalProviders.xlsx"))
    except FileNotFoundError:
        print("Error: LocalProviders.xlsx not found.")
        df_resources = pd.DataFrame()

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

# --- Enhanced Recommendation Logic ---

# Initialize feature weights (can be adjusted later)
org_weights = {"Industry": 0.6, "No. of employees": 0.4}
personal_weights = {"Occupation": 0.7, "Preferences": 0.3}

# Store feedback (in a real system, use a database)
feedback_data = {}  # {resource_id: [helpful_count, not_helpful_count]}

def calculate_organization_relevance(resource_row, org_profile):
    """Calculates relevance score for organization recommendations."""
    relevance = 0
    if 'Industry' in resource_row and 'Industry' in org_profile:
        if resource_row['Industry'] == org_profile['Industry']:
            relevance += org_weights["Industry"]
    if 'No. of employees' in resource_row and 'No. of employees' in org_profile:
        # Example: Give higher score if resource is suitable for the organization size
        if resource_row['No. of employees'] <= org_profile['No. of employees']:
            relevance += org_weights["No. of employees"]
    return relevance

def calculate_personal_relevance(resource_row, personal_profile):
    """Calculates relevance score for personal profile recommendations."""

    relevance = 0
    if 'Occupation' in resource_row and 'Occupation' in personal_profile:
        if resource_row['Occupation'] == personal_profile['Occupation']:
            relevance += personal_weights["Occupation"]
    if 'Preferences' in resource_row and 'Preferences' in personal_profile:
        # Example: Check if the resource keywords match user preferences
        if personal_profile['Preferences'] in resource_row['keywords']:
            relevance += personal_weights["Preferences"]
    return relevance

def get_resource_recommendations(user_profile, search_query=None):
    """
    Retrieves and ranks resource recommendations based on user profile and search query,
    incorporating weighted preferences and feedback.
    """
    df_resources, df_organizations, df_personal_profiles, df_sentiment, df_purchase_history = load_data()

    recommendations_df = df_resources.copy()

    if search_query:
        recommendations_df['relevance'] = recommendations_df['keywords'].apply(
            lambda x: 1 if search_query in str(x).lower() else 0
        )
    else:
        recommendations_df['relevance'] = 0  # Default relevance

    # Personalization logic
    if "organization_id" in user_profile:
        org_id = user_profile["organization_id"]
        org_profile = df_organizations.loc[df_organizations["Customer_Id"] == org_id].iloc[0].to_dict()
        recommendations_df['relevance'] += recommendations_df.apply(
            lambda row: calculate_organization_relevance(row, org_profile), axis=1
        )

    if "personal_id" in user_profile:
        personal_id = user_profile["personal_id"]
        personal_profile = df_personal_profiles.loc[df_personal_profiles["Customer_id"] == personal_id].iloc[0].to_dict()
        recommendations_df['relevance'] += recommendations_df.apply(
            lambda row: calculate_personal_relevance(row, personal_profile), axis=1
        )

    # --- Incorporate Feedback (Illustrative) ---
    # In a real system, you'd retrieve feedback from a database
    # For the hackathon, you can use the 'feedback_data' dictionary

    if recommendations_df.shape[0] > 0:  # Check if there are recommendations
        recommendations_df['feedback_score'] = recommendations_df['resource_id'].apply(
            lambda x: feedback_data.get(x, [0, 0])[0] - feedback_data.get(x, [0, 0])[1]
        )
        recommendations_df['relevance'] += recommendations_df['feedback_score'] * 0.2  # Weight feedback

    recommendations_df.sort_values(by='relevance', ascending=False, inplace=True)
    return recommendations_df

# --- Example Usage and Feedback Simulation ---

# Simulate user feedback (for demonstration)
feedback_data["resource_123"] = [5, 1]  # 5 helpful, 1 not helpful
feedback_data["resource_456"] = [2, 3]  # 2 helpful, 3 not helpful

user_profile = {"organization_id": "org_123", "personal_id": "pers_456", "customer_id": "cust_789"}
recommendations = get_resource_recommendations(user_profile, search_query="business loans")
print(recommendations)