from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

endpoint = "https://moos-enterprise-agent-resource.services.ai.azure.com/api/projects/moos-enterprise-agent"

project_client = AIProjectClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential(),
)

openai_client = project_client.get_openai_client()

#Reference the agent to get a response
response = openai_client.responses.create(
    input = [{"role": "user", "content":"Tell me what you can help me with"}],
    extra_body = {"agent_reference": {"name": "MY_AGENT", "version": "MY_VERSION", "type": "agent_reference"}},
)

print (f"Response output: {response.output_text}")