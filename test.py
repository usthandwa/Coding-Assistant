import os

from groq import Groq

client = Groq(
    # This is the default and can be omitted
    api_key="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",
)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "you are a helpful assistant."
        },
        {
            "role": "user",
            "content": "Explain the importance of fast language models",
        }
    ],
    model="deepseek-r1-distill-llama-70b",
)

print(chat_completion.choices[0].message.content)