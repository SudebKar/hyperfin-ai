from transformers import GPT2LMHeadModel, GPT2Tokenizer


def generate_message(prompt):
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    model = GPT2LMHeadModel.from_pretrained("gpt2")

    inputs = tokenizer(prompt, return_tensors="pt")

    outputs = model.generate(
        inputs.input_ids,
        max_length=200,  # Allow more tokens for a complete response
        temperature=0.3,  # Lower for more deterministic output
        top_k=15,  # Restrict to high-confidence tokens
        top_p=0.8,  # Focus on a narrow probability range
        repetition_penalty=3.0,  # Strongly penalize repetition
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id
    )

    return tokenizer.decode(outputs[0], skip_special_tokens=True)


if __name__ == '__main__':
    from transformers import GPT2LMHeadModel, GPT2Tokenizer


    def test_generate():
        tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
        model = GPT2LMHeadModel.from_pretrained("gpt2")

        prompt = """As a financial advisor, write a concise, empathetic message to the customer below. 
        Focus on their interests and suggest relevant services from the list provided below.

        Customer Details:
        - Interests: Luxury Shopping, Travel, Dining
        - Recent Spending: $34,000 on Equity, Gucci, International Flight
        - Services Available: Travel Credit Cards, Wealth Management, Loan EMI Assistance"""
        inputs = tokenizer(prompt, return_tensors="pt")

        outputs = model.generate(
            inputs.input_ids,
            max_length=150,
            temperature=0.5,  # Lower = more focused
            top_k=30,  # Restrict to high-probability tokens
            top_p=0.9,  # Avoid unlikely options
            repetition_penalty=2.0,  # Strongly discourage repetition
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )

        print(tokenizer.decode(outputs[0], skip_special_tokens=True))


    test_generate()

