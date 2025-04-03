from huggingface_hub import InferenceClient
from transformers import pipeline
import pandas as pd
from rapidfuzz import fuzz
from utils.message_generator_hf import get_api_key


# def analyze_sentiment(text):
#     classifier = pipeline("text-classification", model="bhadresh-savani/distilbert-base-uncased-emotion")
#     return classifier(text)[0]["label"]

def analyze_spending(customer_id, transactions):
    customer_tx = transactions[transactions["Customer_Id"] == customer_id]
    total_spend = customer_tx["Amount (In Dollars)"].sum()
    frequent_categories = customer_tx["Category"].mode().tolist()
    return {"total_spend": total_spend, "frequent_categories": frequent_categories}

# def match_services(customer_profile, providers_df):
#     keywords = []
#     if "Interests" in customer_profile:
#         keywords += customer_profile["Interests"].split(", ")
#     if "Financial Needs" in customer_profile:
#         keywords += customer_profile["Financial Needs"].split(", ")
#
#     # Find providers with matching keywords
#     matched_services = providers_df[
#         providers_df["keywords"].apply(lambda x: any(kw in x for kw in keywords))
#     ]
#     return matched_services

def expand_keywords(original_keywords):
    hf_token = get_api_key()
    client = InferenceClient(token=hf_token)

    prompt = f"""Analyze these customer interests: {original_keywords}.
    Generate 3-5 additional semantically related keywords that could help match financial services.
    Focus on broader categories and related concepts. Respond only with comma-separated keywords."""

    try:
        response = client.text_generation(
            prompt=prompt,
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            max_new_tokens=50,
            temperature=0.5
        )

        # Clean and combine keywords
        new_keywords = [kw.strip().lower() for kw in response.split(",")]
        return list(set(original_keywords + new_keywords))

    except Exception as e:
        print(f"Keyword expansion failed: {str(e)}")
        return original_keywords

def match_services(customer_profile, providers_df, threshold=60):
    # Extract and preprocess customer keywords (case-insensitive)
    customer_keywords = []
    if "Interests" in customer_profile and pd.notna(customer_profile["Interests"]):
        customer_keywords += [kw.strip().lower() for kw in customer_profile["Interests"].split(",")]
    if "Financial Needs" in customer_profile and pd.notna(customer_profile["Financial Needs"]):
        customer_keywords += [kw.strip().lower() for kw in customer_profile["Financial Needs"].split(",")]

    customer_keywords = expand_keywords(customer_keywords)
    # Create a mask list to store match results
    mask = []

    # Iterate through each row explicitly
    for index, row in providers_df.iterrows():
        provider_keywords_str = row["keywords"]
        match_found = False

        if pd.isna(provider_keywords_str):
            mask.append(False)
            continue

        provider_keywords = [pk.strip().lower() for pk in provider_keywords_str.split(",")]

        # Check fuzzy match for each provider keyword
        for pk in provider_keywords:
            for ck in customer_keywords:
                if fuzz.ratio(pk, ck) >= threshold:
                    match_found = True
                    break
            if match_found:
                break

        mask.append(match_found)

    # Filter dataframe using our manually created mask
    matched_services = providers_df[mask]
    return matched_services
