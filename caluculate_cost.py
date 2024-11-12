from config import CONFIG


def calculate_openai_cost(input_tokens, output_tokens):
    # Define costs per million tokens
    input_cost_per_million = float(CONFIG["OPENAI_INPUT_COST"])  # in euros
    output_cost_per_million = float(CONFIG["OPENAI_OUTPUT_COST"])  # in euros

    print(input_cost_per_million)
    # Calculate costs based on the number of tokens
    input_cost = (input_tokens / 1_000_000) * input_cost_per_million
    output_cost = (output_tokens / 1_000_000) * output_cost_per_million

    # Total cost
    total_cost = input_cost + output_cost

    return {
        "input": input_cost,
        "output": input_cost,
    }
