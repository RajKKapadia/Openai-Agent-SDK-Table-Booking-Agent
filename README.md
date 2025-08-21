# Table Booking Agent

This project is an AI-powered agent that assists with booking tables at restaurants. It is built using FastAPI and the `openai-agents` library. The agent can check for table availability, save bookings, add users to a waitlist, and integrates with WhatsApp for messaging.

## Features

*   Check table availability for a given restaurant, date, and time
*   Book a table and provide a booking confirmation
*   Add users to a waitlist if no tables are available
*   Get the current date and time
*   WhatsApp integration for messaging
*   Guard rail system to validate user inputs
*   Database persistence for chat history and user data
*   Background task processing with Redis and ARQ

## Tech Stack

*   Python 3.12+
*   FastAPI
*   OpenAI Agents SDK
*   PostgreSQL (with SQLAlchemy and Alembic)
*   Redis
*   ARQ (for background tasks)
*   Uvicorn
*   Pydantic
*   WhatsApp Business API

## Getting Started

### Prerequisites

*   Python 3.12+
*   PostgreSQL
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
    
    Or using uv (recommended):
    ```bash
    uv sync
    ```

### Database Setup

1.  Create a PostgreSQL database
2.  Set up the database URL in your environment variables
3.  Run database migrations:
    ```bash
    alembic upgrade head
    ```

### Configuration

Create a `.env` file with the following environment variables:

```env
# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key

# Server Configuration
SERVER_API_KEY=your-server-api-key

# WhatsApp Business API Configuration
VERIFY_TOKEN=your-whatsapp-verify-token
APP_SECRET=your-whatsapp-app-secret
PHONE_NUMBER_ID=your-whatsapp-phone-number-id
ACCESS_TOKEN=your-whatsapp-access-token

# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/database_name

# Redis Configuration (defaults to localhost:6379)
REDIS_URL=redis://localhost:6379
```

### Running the Application

1.  Start the main application:
    ```bash
    python run.py
    ```
    The application will be available at `http://127.0.0.1:5000`.

2.  Start the background worker (in a separate terminal):
    ```bash
    python worker.py
    ```

## API Endpoints

### Health Check
*   `GET /api/v0/health`: Health check endpoint

### Agent Endpoints
*   `POST /api/v0/agent/chat/stream`: Stream chat with the table booking agent
*   `POST /api/v0/agent/chat`: Non-streaming chat with the table booking agent

### WhatsApp Integration
*   `GET /api/v0/whatsapp/webhook`: WhatsApp webhook verification
*   `POST /api/v0/whatsapp/webhook`: WhatsApp message processing

## Project Structure

```
Openai-Agent-SDK-Table-Booking-Agent/
├── alembic/                    # Database migrations
├── src/
│   ├── custom_agents/          # AI agent implementations
│   │   ├── guard_rail_agent.py # Input validation agent
│   │   └── table_booking_agent.py # Main booking agent
│   ├── models/                 # Database models
│   │   └── chat_model.py       # Chat and user models
│   ├── routes/                 # API route handlers
│   │   ├── agent_route.py      # Agent API endpoints
│   │   ├── health_route.py     # Health check endpoint
│   │   └── whatsapp_route.py   # WhatsApp integration
│   ├── schemas/                # Pydantic schemas
│   │   └── schemas.py          # Request/response models
│   ├── tools/                  # Agent tools
│   │   ├── current_date_tool.py
│   │   ├── join_waitlist_tool.py
│   │   ├── save_booking_tool.py
│   │   └── table_availability_tool.py
│   ├── utils/                  # Utility functions
│   │   └── prompts.py          # Agent prompts
│   ├── config.py               # Configuration settings
│   ├── database.py             # Database connection
│   ├── main.py                 # FastAPI application
│   └── queue.py                # Background task queue
├── worker.py                   # Background worker
├── run.py                      # Application entry point
├── pyproject.toml              # Project configuration
├── requirements.txt            # Python dependencies
└── alembic.ini                 # Alembic configuration
```

## Usage

### Agent Chat

The agent can handle natural language requests for table bookings. Example:

```
User: "I'd like to book a table for 4 people at 7 PM tonight"
Agent: "I'll help you check availability and book a table for 4 people at 7 PM tonight."
```

### WhatsApp Integration

The system integrates with WhatsApp Business API to handle booking requests via messaging. Users can send booking requests through WhatsApp and receive confirmations.

## Development

### Running Migrations

To create a new migration:
```bash
alembic revision --autogenerate -m "Description of changes"
```

To apply migrations:
```bash
alembic upgrade head
```

### Background Tasks

The application uses ARQ with Redis for background task processing. The worker handles:
- WhatsApp message processing
- Database operations
- Async task execution

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.