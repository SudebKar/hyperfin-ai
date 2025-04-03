import pandas as pd
from huggingface_hub import InferenceClient
from rapidfuzz import fuzz


def analyze_customer_sentiment(sentiment_data, hf_token):
    """Analyze social media posts with sentiment scores"""

    client = InferenceClient(token=hf_token)

    # Aggregate existing scores
    avg_score = sentiment_data["Sentiment_Score"].mean()

    # Analyze post content for emotional tone
    emotional_tones = []
    for content in sentiment_data["Content"]:
        response = client.text_classification(
            text=content,
            model="SamLowe/roberta-base-go_emotions"
        )
        emotional_tones.append(response[0]['label'])
        # emotional_tones.extend([label['label'] for label in response])

    # Get most frequent emotion
    primary_emotion = max(set(emotional_tones), key=emotional_tones.count) if emotional_tones else "neutral"

    return {
        "average_sentiment": avg_score,
        "primary_emotion": primary_emotion,
        "emotional_trends": emotional_tones
    }


def match_services_with_sentiment(profile, providers, sentiment, hf_token, threshold=80):
    """Enhanced matching considering sentiment"""
    # Expand keywords with emotional context
    emotional_context = f"Customer tends towards {sentiment['primary_emotion']} based on social media"
    if "Interests" in profile and pd.notna(profile["Interests"]):
        expanded_keywords = expand_keywords_with_emotion(
            profile["Interests"],
            emotional_context,
            hf_token
        )
    if "Financial Needs" in profile and pd.notna(profile["Financial Needs"]):
        expanded_keywords = expand_keywords_with_emotion(
            profile["Financial Needs"],
            emotional_context,
            hf_token
        )
    # Modified fuzzy matching considering sentiment
    providers_df = providers.copy()
    scores = []

    for _, row in providers_df.iterrows():
        provider_keywords = process_keywords(row["keywords"])
        match_score = calculate_match_score(
            expanded_keywords,
            provider_keywords,
            sentiment["average_sentiment"]
        )
        scores.append(match_score)
    providers_df = providers_df.assign(match_score=scores)
    filtered = providers_df[providers_df['match_score'] >= threshold]
    # Sort and select top 10
    sorted_matches = filtered.sort_values('match_score', ascending=False)
    return sorted_matches.head(10).reset_index(drop=True)


def expand_keywords_with_emotion(interests, emotional_context, hf_token):
    """Generate emotionally-aware keyword suggestions"""
    client = InferenceClient(token=hf_token)

    prompt = f"""Given a customer with interests: {interests}
    and emotional context: {emotional_context}
    Suggest 5-7 financial service keywords each having 1 to 2 words only that would be appropriate:
    Respond only with comma-separated keywords"""

    response = client.text_generation(
        prompt=prompt,
        model="mistralai/Mixtral-8x7B-Instruct-v0.1",
        max_new_tokens=100,
        temperature=0.4
    )

    return list(set(
        [kw.strip().lower() for kw in response.split(",")] +
        [kw.strip().lower() for kw in interests.split(",")]
    ))


def build_prompt(customer_id, profile, spending, sentiment, services):
    """Construct comprehensive prompt with sentiment analysis"""
    return f"""Customer Profile:
- ID: {customer_id}
- Demographics: {profile['Age']}yo {profile['Gender']} in {profile['Location']}
- Occupation: {profile['Occupation']}
- Interests: {profile['Interests']}
- Financial Capacity: ${profile['Income per']}/year

Behavioral Analysis:
- Recent Spending: ${spending['total_spend']} on {spending['frequent_categories']}
- Payment Preferences: {profile['Preferences']}

Sentiment Analysis:
- Average Sentiment Score: {sentiment['average_sentiment']}/1.0
- Primary Emotional Tone: {sentiment['primary_emotion']}
- Observed Emotional Trends: {', '.join(set(sentiment['emotional_trends']))}

Available Services: {services['name'].tolist()}

Task: Create empathetic financial advice that:
1. Acknowledges observed emotional state
2. Aligns with spending patterns
3. Suggests relevant services
4. Maintains professional yet compassionate tone

Response:
"""


def process_keywords(keyword_str):
    """Clean and normalize keywords from provider data"""
    if pd.isna(keyword_str):
        return []
    return [str(kw).strip().lower() for kw in keyword_str.split(",")]


def calculate_match_score(customer_keywords, provider_keywords, avg_sentiment):
    """Calculate sentiment-adjusted fuzzy match score"""
    if not provider_keywords:
        return 0

    best_match = 0
    for pk in provider_keywords:
        for ck in customer_keywords:
            current_score = fuzz.ratio(pk, ck)
            if current_score > best_match:
                best_match = current_score

    # Adjust score based on sentiment (-1 to 1 scale)
    sentiment_boost = avg_sentiment * 15  # ±15% maximum adjustment
    adjusted_score = best_match + sentiment_boost

    # Keep within 0-100 bounds
    return max(0, min(100, adjusted_score))


