# Table Booking Agent

This project is an AI-powered agent that assists with booking tables at restaurants. It is built using FastAPI and the `openai-agents` library. The agent can check for table availability, save bookings, and add users to a waitlist.

## Features

*   Check table availability for a given restaurant, date, and time.
*   Book a table and provide a booking confirmation.
*   Add users to a waitlist if no tables are available.
*   Get the current date and time.

## Tech Stack

*   Python
*   FastAPI
*   OpenAI
*   Redis
*   Uvicorn
*   Pydantic

## Getting Started

### Prerequisites

*   Python 3.x
*   Redis

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/your-username/Openai-Agent-SDK-Table-Booking-Agent.git
    cd Openai-Agent-SDK-Table-Booking-Agent
    ```
2.  Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Configuration

1.  Create a `.env` file from the `.env.example` file:
    ```bash
    cp .env.example .env
    ```
2.  Add your OpenAI API key to the `.env` file:
    ```
    OPENAI_API_KEY="your-openai-api-key"
    ```

### Running the application

```bash
python run.py
```
The application will be available at `http://127.0.0.1:5000`.

## API Endpoints

*   `GET /health`: Health check endpoint.
*   `POST /agent/invoke`: Endpoint to interact with the table booking agent.

## Project Structure
```
/home/logan/Desktop/My-Learning/Openai-Agent-SDK-Table-Booking-Agent/
├───.env.example
├───.gitignore
├───.python-version
├───pyproject.toml
├───README.md
├───requirements.txt
├───run.py
├───uv.lock
├───.git/...
├───.venv/
│   ├───bin/...
│   └───lib/...
└───src/
    ├───__init__.py
    ├───config.py
    ├───main.py
    ├───__pycache__/
    ├───custom_agents/
    │   ├───guard_rail_agent.py
    │   ├───table_booking_agent.py
    │   └───__pycache__/
    ├───models/
    │   ├───schemas.py
    │   └───__pycache__/
    ├───routes/
    │   ├───agent_route.py
    │   ├───health_route.py
    │   ├───whatsapp_route.py
    │   └───__pycache__/
    ├───tools/
    │   ├───current_date_tool.py
    │   ├───join_waitlist_tool.py
    │   ├───save_booking_tool.py
    │   ├───table_availability_tool.py
    │   └───__pycache__/
    └───utils/
        ├───prompts.py
        └───__pycache__/
```