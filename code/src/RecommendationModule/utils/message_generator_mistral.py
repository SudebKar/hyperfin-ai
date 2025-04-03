from transformers import AutoTokenizer, AutoModelForCausalLM


def generate_empathetic_message1(prompt):
    model_name = "HuggingFaceH4/zephyr-7b-beta"  # Publicly accessible
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="auto",
        load_in_4bit=True  # Reduces memory usage
    )

    # Format prompt
    formatted_prompt = f"""<|system|>
    You are a financial advisor. Write a short, empathetic message using the customer's transaction history and suggested services.
    </s>
    <|user|>
    {prompt}
    </s>
    <|assistant|>
    """

    # Generate response
    inputs = tokenizer(formatted_prompt, return_tensors="pt").to("cuda")
    outputs = model.generate(
        inputs.input_ids,
        max_new_tokens=200,
        temperature=0.3,
        top_k=20,
        repetition_penalty=1.2
    )

    return tokenizer.decode(outputs[0], skip_special_tokens=True).split("<|assistant|>")[-1].strip()


def generate_empathetic_message2(prompt):
    model_name = "microsoft/Phi-3-mini-4k-instruct"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="auto",
        load_in_4bit=True
    )

    formatted_prompt = f"""<|user|>
    As a financial advisor, write a concise, empathetic message to this customer:
    {prompt}
    <|assistant|>
    """

    inputs = tokenizer(formatted_prompt, return_tensors="pt").to("cuda")
    outputs = model.generate(
        inputs.input_ids,
        max_new_tokens=200,
        temperature=0.3
    )

    return tokenizer.decode(outputs[0], skip_special_tokens=True).split("<|assistant|>")[-1].strip()


def generate_empathetic_message3(prompt):
    model_name = "google/gemma-7b-it"
    tokenizer = AutoTokenizer.from_prained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="auto",
        load_in_4bit=True
    )

    formatted_prompt = f"""<start_of_turn>user
    As a financial advisor, write an empathetic message using these details: {prompt}<end_of_turn>
    <start_of_turn>model
    """

    inputs = tokenizer(formatted_prompt, return_tensors="pt").to("cuda")
    outputs = model.generate(
        inputs.input_ids,
        max_new_tokens=200,
        temperature=0.3
    )

    return tokenizer.decode(outputs[0], skip_special_tokens=True).split("<start_of_turn>model")[-1].strip()


from transformers import AutoTokenizer, AutoModelForCausalLM


def generate_empathetic_message4(prompt):
    model_name = "microsoft/phi-2"  # 2.7B parameters, runs on CPU
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)

    formatted_prompt = f"""Instruct: As a financial advisor, write a short, empathetic message to this customer:
    {prompt}
    Response:"""

    inputs = tokenizer(formatted_prompt, return_tensors="pt", return_attention_mask=False)
    outputs = model.generate(**inputs, max_length=200)
    return tokenizer.decode(outputs[0], skip_special_tokens=True).split("Response:")[-1].strip()