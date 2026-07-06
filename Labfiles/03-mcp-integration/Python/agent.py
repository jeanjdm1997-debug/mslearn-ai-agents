import os
from dotenv import load_dotenv

# Add references
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, MCPTool
from openai.types.responses.response_input_param import McpApprovalResponse, ResponseInputParam



# Load environment variables from .env file
load_dotenv()
project_endpoint = os.getenv("PROJECT_ENDPOINT")
model_deployment = os.getenv("MODEL_DEPLOYMENT_NAME")

# Connect to the agents client
with (
    DefaultAzureCredential() as credential, 
    AIProjectClient(endpoint="PROJECT_ENDPOINT", credential=credential) as project_client,
    project_client.get_openai_client() as openai_client,
    ):


    # Initialize agent MCP tool
    mcp_tool = MCPTool(
        server_label="api-spec",
        server_url="https://learn.microsoft.com/api/mcp",
        require_approval="always",
    )

    # Create a new agent with the MCP tool
    agent = project_client.agents.create_version(
        agent_name = "mcp-agent",
        definition = PromptAgentDefinition(
            model = "gpt-5",
            instructions = "You are an agent that can call the MCP tool to retrieve API specifications. Use the available MCP tools to answer users",
            tools = [mcp_tool],
        ),
    )
    print(f"Agent created(id: {agent.id}, name: {agent.name}, version: {agent.version})")

    # Create conversation thread
    conversation = openai_client.conversations.create()
    print (f"Conversation created id: {conversation.id}")
    

    # Send initial request that will trigger the MCP tool
    response = openai_client.responses.create(
        conversation=conversation.id,
        input= "Give me the azure CLI command to create an Azure Container App with a managed identity.",
        extra_body = {"agent_reference": {"name": agent.name, "type": "agent_reference"}},
    )
    

    # Process any MCP approval requests that were generated
    # The agent may issue several tool calls, each needin its own approval.
    # So we loop until there are none left
    while True:
        # Check if the response contains any MCP approval requests
        input_list: ResponseInputParam = []
        for item in response.output:
            if item.type == "mcp_approval_request":
                if item.server_label == "api-spec" and item.id:
                    #Automatically approve the request to allow agent to proceed
                    input_list.append(
                        McpApprovalResponse(
                            type="mcp_approval_response",
                            approve=True,
                            approval_request_id=item.id,
                        )
                    )

        # no more approvals needed, the agent has completed its work
        if not input_list:
            break

        # Send the approval responses back and retrieve the next response
        response = openai_client.responses.create(
            input=input_list,
            previous_response_id=response.id,
            extra_body = {"agent_reference": {"name": agent.name, "type": "agent_reference"}},
        )

    print (f"\nAgent response: {response.output_text}")


                    
    
    # Clean up resources by deleting the agent version
    project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
    print("Agent deleted")
