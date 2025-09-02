
# Car Diagnostic Agent

This A2A agent acts as a virtual car mechanic. It uses a Large Language Model to diagnose car problems based on the model, year, and Diagnostic Trouble Codes (DTCs) you provide.

## How It Works

The agent assumes the persona of the car itself and provides explanations for the trouble codes, suggests potential causes, and recommends fixes.

**IMPORTANT LIMITATION:** This agent cannot connect to a real car. You must manually provide the car's details and the OBD-II codes in your text prompt.

## Prerequisites

- Python 3.12 or higher
- [UV](https://docs.astral.sh/uv/)
- A Google Gemini API Key

## Running the Agent

1.  **Set up your environment:**

    Create a `.env` file in this directory with your Google API key:
    ```bash
    echo "GOOGLE_API_KEY=your_api_key_here" > .env
    ```

2.  **Start the agent server:**

    From this directory (`samples/python/agents/car_diagnostic_agent`), run:
    ```bash
    uv run python -m app
    ```
    The agent will start on `http://localhost:10011`.

3.  **Interact with the Agent:**

    Use a generic A2A client, like the CLI host, to talk to the agent.

    ```bash
    # From the a2a-samples root directory
    cd samples/python/hosts/cli
    uv run . --agent http://localhost:10011
    ```

    **Example Prompts:**

    *   "I have a 2015 Ford Focus and I'm seeing codes P0171 and P0174. What's going on?"
    *   "My 2019 Toyota Camry is showing a check engine light with code C1201."
