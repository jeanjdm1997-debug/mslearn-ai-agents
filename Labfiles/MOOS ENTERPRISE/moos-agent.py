import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AzureOpenAI
from email_service import send_invoice_request

load_dotenv()

#create an openai client
token_provider = get_bearer_token_provider(
    DefaultAzureCredential(), "https://ai.azure.com/.default"
)

openai_client = OpenAI(
    base_url = "Azure_Openai_Endpoint",
    api_key = token_provider,
)

#ChatBot Message System
#Intial Messages
conversation_message=[
    {
        "role": "system",
        "content": "You are a AI assitant at Moos Enterprise"
    }
]
#Loop until the user wants to quit
print ("Assistant: How can I Assist You Today? \\ or Type Quit to Exit!")
while True:
    input_text = input('\nYou:')
    if input_text.lower() == "Quit":
        print("Assistant: Goodbye! Hope To Hear From You Soon.")
        break

    #Add User Message
    conversation_message.append(
        {"role": "user",
            "content": input_text}
    )

    #Agent Completion
    completion = openai_client.client.chat.completion.create(
        model = "gpt-5.4"
        message = conversation_message
    )

    assistant_message = completion.choices[0].message.content
    print ("\nAssistant:", assistant_message)

    #Append the response to the conversation
    conversation_message.append(
        {"role": "assistant", "content": assistant_message}
    )