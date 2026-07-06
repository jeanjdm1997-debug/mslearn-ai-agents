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
    AIProjectClient(endpoint=project_endpoint, credential=credential) as project_client,
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
            model = model_deployment,
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
    
    # Clean up resources by deleting the agent version
    
