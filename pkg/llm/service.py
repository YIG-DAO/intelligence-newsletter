import os
import openai

openai.api_key  = os.getenv('API_KEY')

def GPT4(prompt):
    """
    Generate a response using GPT-4 model based on the given prompt.

    Args:
        prompt (str): The input prompt for generating the response.

    Returns:
        dict: The response generated by the GPT-4 model.

    Raises:
        OpenAIError: If there is an error while fetching the response.

    """
    print("> Fetching GPT4_EXEC_SYNOPSIS")
    # ChatGPT (or gpt3.5 turbo)
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an Cyber intelligence and economic security advisor"},
            {"role": "user", "content": prompt},
        ],
        max_tokens=400
    )
    return response