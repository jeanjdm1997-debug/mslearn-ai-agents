from openai import OpenAI
from azure.identity import DefaultAzureCredential

end_point = "project_endpoint"
model = "gpt-5.4"
token_provider = DefaultAzureCredential(),

#create client
