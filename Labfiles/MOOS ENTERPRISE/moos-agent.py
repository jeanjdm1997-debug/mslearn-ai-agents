import os
from typing import cast, Iterable, Any
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AzureOpenAI
from email_service import send_invoice_request

load_dotenv()

credential = DefaultAzureCredential()
token_provider = get_bearer_token_provider(
    credential,
    "https://cognitiveservices.azure.com/.default"
)
# Read required configuration from environment
azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2023-05-15")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

if not azure_openai_endpoint or not deployment:
    raise RuntimeError(
        "Missing environment variables: AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_DEPLOYMENT must be set"
    )

# Client
client = AzureOpenAI(
    azure_endpoint=azure_openai_endpoint,
    azure_ad_token_provider=token_provider,
    api_version=api_version,
)
system_prompt = """
You are an AI assistant for a construction company.

You help customers with:
- Plumbing
- Electrical
- Fencing
- Roofing
- Tiling
- Building
- Renovations

When a customer wants a quotation or invoice request, collect:
Client Name

Company Name

Email
Phone Number
Service Required
Address
Project Scope
Additional Notes

Once collected, tell the application to call send_invoice_request().
"""

conversation = [
    {
        "role": "system",
        "content": system_prompt
    }
]

while True:
    user = input("customer: ")
    if user.lower() == "Exit":
        break
    conversation.append(
        {
            "role":"user",
            "content": user
        }
    )

tool = [
    {
        "type": "function",
        "function": {
            "name": "send_invoice_request",
            "description": "Send a quotation or invoice request email to the company.",
            "parameters": {
                "type": "object",
                "properties": {
                    "client_name": {
                        "type": "string"
                    },
                    "company_name": {
                        "type": "string"
                    },
                    "email": {
                        "type": "string"
                    },
                    "phone": {
                        "type": "string"
                    },
                    "service_required": {
                        "type": "string"
                    },
                    "additional_notes": {
                        "type": "string"
                    }
                },
                "required": [
                    "client_name",
                    "company_name",
                    "email",
                    "phone",
                    "service_required"
                ]
            }
        }
    }
]

response = client.chat.completions.create(
    model=deployment,
    messages=cast(Iterable[Any], conversation),
    # use the functions parameter (OpenAI-compatible) instead of tools
    functions=cast(Iterable[Any], tool)
)

reply = response.choices[0].message.content or ""
print()
print("Assistant:")
print(reply)
print()

conversation.append(
    {
        "role": "assistant",
        "content": reply
    }
)

# The actual call to send_invoice_request should be performed with
# concrete values extracted from the assistant response. Keep as placeholder.
# send_invoice_request(client_name, company_name, email, phone, service_required, additional_notes)