import os
import sys

from utils.analysis_sentiment_added import analyze_customer_sentiment, match_services_with_sentiment, build_prompt
from utils.data_loader import load_data
from utils.message_generator_hf import generate_empathetic_message, get_api_key
from utils.analysis_using_models import analyze_spending, match_services


def main(customer_id):
    # Load data
    transactions, individuals, orgs, social, providers = load_data()

    # Example: Process individual customer CUST2025A
    profile = individuals[individuals["Customer_id"] == customer_id]
    if profile.empty:
        print(f"Error: No profile found for customer_id {customer_id}")
        return
    profile = profile.iloc[0].to_dict()

    # Analyze financial behavior
    spending = analyze_spending(customer_id, transactions)

    # Analyze social media sentiment
    sentiment_data = social[social["Customer_Id"] == customer_id]
    sentiment_analysis = analyze_customer_sentiment(sentiment_data)

    # Match services with expanded keywords
    services = match_services(profile, providers)

    # Generate empathetic message
    prompt = f"Customer {customer_id} has interests in {profile['Interests']}. "
    prompt += f"They recently spent ${spending['total_spend']} on {spending['frequent_categories']}. "
    prompt += f"Suggest empathetic financial advice using these services: {services['name'].tolist()}"
    print(services['name'].tolist())

    message = generate_empathetic_message(prompt)
    print(message)


def main_with_sentiment(customer_id):
    hf_token = get_api_key()
    transactions, individuals, orgs, social, providers = load_data()

    # Get customer profile
    profile = individuals[individuals["Customer_id"] == customer_id]
    if profile.empty:
        print(f"Error: No profile found for customer_id {customer_id}")
        return
    profile = profile.iloc[0].to_dict()

    # Analyze financial behavior
    spending = analyze_spending(customer_id, transactions)

    # Analyze social media sentiment
    sentiment_data = social[social["Customer_Id"] == customer_id]
    sentiment_analysis = analyze_customer_sentiment(sentiment_data, hf_token)

    # Match services with expanded keywords
    services = match_services_with_sentiment(
        profile,
        providers,
        sentiment_analysis, hf_token
    )

    # Generate empathetic message
    prompt = build_prompt(
        customer_id,
        profile,
        spending,
        sentiment_analysis,
        services
    )

    message = generate_empathetic_message(prompt)
    print(message)
    return message

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_voice_search.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()