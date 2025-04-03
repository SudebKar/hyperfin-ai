import os

from huggingface_hub import InferenceClient
import configparser

# Create a ConfigParser instance
def get_api_key():
    config = configparser.ConfigParser()
    path = os.path.dirname(os.path.abspath(__file__))
    config.read(os.path.join(path, "config.ini"))
    key_value = config.get("HUGGINGFACE_KEY", "key")
    return key_value

def generate_empathetic_message(prompt):
    client = InferenceClient(token=get_api_key())

    response = client.text_generation(
        prompt=f"""<|system|>
        You are a financial advisor. Write a short, empathetic message using these details:
        {prompt}
        </s>
        <|user|>
        </s>
        <|assistant|>""",
        model="HuggingFaceH4/zephyr-7b-beta",
        max_new_tokens=500,
        temperature=0.3
    )
    return response


if __name__ == '__main__':
    prompt = """As a financial advisor, write a concise, empathetic message to Customer CUST2025A. Focus on their interests and suggest relevant services. Avoid creative stories.

    Customer Details:
    - Interests: Luxury Shopping, Travel, Dining
    - Recent Spending: $34,000 on Equity, Gucci, International Flight
    - Services Available: Travel Credit Cards, Wealth Management, Loan EMI Assistance

    Message:"""
    print(generate_empathetic_message(prompt))