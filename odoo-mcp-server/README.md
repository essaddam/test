# Odoo MCP Server

A FastAPI-based Model Context Protocol (MCP) server for Odoo integration with HTTP streaming support.

## Features

- **MCP Protocol Support**: Full implementation of the Model Context Protocol for AI model integration
- **Operating Modes**: Readonly and readwrite modes for controlled access
- **HTTP Streaming**: Real-time streaming of large data responses
- **WebSocket Support**: Real-time bidirectional communication
- **Comprehensive Odoo Integration**: Support for all major Odoo operations (CRUD, reports, workflows)  
- **Permission System**: Advanced permission management based on operation modes
- **Async/Await**: Built with modern Python async/await patterns for high performance
- **Security**: API key authentication and IP filtering support
- **Rate Limiting**: Configurable request rate limiting
- **Monitoring**: Comprehensive logging and error handling

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd odoo-mcp-server
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your Odoo credentials
```

4. Start the server:
```bash
python start.py
```

## Configuration

Create a `.env` file based on `.env.example`:

```env
# Odoo Connection
ODOO_URL=http://localhost:8069
ODOO_DATABASE=odoo
ODOO_USERNAME=admin
ODOO_PASSWORD=admin

# Server Settings
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DEBUG=false

# MCP Mode (readonly or readwrite)
MCP_MODE=readwrite
```

## Operating Modes

The server supports two operating modes for controlled access:

### 🔒 Readonly Mode
```env
MCP_MODE=readonly
```
- **Allowed**: Search, read operations, reports generation
- **Forbidden**: Create, update, delete operations
- **Use cases**: Dashboards, analytics, public APIs, demo environments

### 🔓 Readwrite Mode  
```env
MCP_MODE=readwrite
```
- **Allowed**: All operations (CRUD, reports, method calls)
- **Use cases**: Full integrations, data synchronization, automated workflows

### Mode Verification
```bash
curl http://localhost:8000/mcp/mode
```

For detailed information, see [Operating Modes Documentation](docs/modes.md).

## API Endpoints

### Health Check
```
GET /health
```

### MCP Protocol Endpoints

#### Initialize MCP
```
POST /mcp/initialize
```

#### List Tools
```
POST /mcp/tools/list
```

#### Call Tool
```
POST /mcp/tools/call
```

#### Stream Tool Call
```
POST /mcp/stream/tools/call
```

#### List Resources
```
POST /mcp/resources/list
```

#### Read Resource
```
POST /mcp/resources/read
```

### Direct Odoo Integration

#### Query Odoo
```
POST /odoo/query
```

#### List Models
```
GET /odoo/models
```

#### Get Model Fields
```
GET /odoo/models/{model_name}/fields
```

### WebSocket
```
WS /mcp/ws
```

## MCP Tools

The server provides several MCP tools for Odoo operations:

### odoo_search
Search for records in Odoo models.

```json
{
  "method": "odoo_search",
  "params": {
    "model": "res.partner",
    "domain": [["is_company", "=", true]],
    "fields": ["name", "email", "phone"],
    "limit": 10
  }
}
```

### odoo_create
Create new records in Odoo.

```json
{
  "method": "odoo_create",
  "params": {
    "model": "res.partner",
    "values": {
      "name": "New Company",
      "email": "info@newcompany.com",
      "is_company": true
    }
  }
}
```

### odoo_write
Update existing records.

```json
{
  "method": "odoo_write",
  "params": {
    "model": "res.partner",
    "ids": [1, 2, 3],
    "values": {
      "email": "updated@email.com"
    }
  }
}
```

### odoo_unlink
Delete records.

```json
{
  "method": "odoo_unlink",
  "params": {
    "model": "res.partner",
    "ids": [1, 2, 3]
  }
}
```

### odoo_call
Call any Odoo model method.

```json
{
  "method": "odoo_call",
  "params": {
    "model": "account.move",
    "method": "post",
    "args": [[1, 2, 3]]
  }
}
```

### odoo_fields_get
Get field definitions for a model.

```json
{
  "method": "odoo_fields_get",
  "params": {
    "model": "res.partner",
    "fields": ["name", "email"]
  }
}
```

### odoo_report
Generate reports.

```json
{
  "method": "odoo_report",
  "params": {
    "report_name": "account.report_invoice",
    "record_ids": [1, 2, 3],
    "format": "pdf"
  }
}
```

## MCP Resources

The server provides several MCP resources:

- `odoo://models` - List of all available Odoo models
- `odoo://users` - List of Odoo users
- `odoo://companies` - List of companies
- `odoo://config` - Odoo server configuration

## HTTP Streaming

For large datasets, use the streaming endpoints:

```bash
curl -X POST "http://localhost:8000/mcp/stream/tools/call" \
  -H "Content-Type: application/json" \
  -d '{"method": "odoo_search", "params": {"model": "res.partner", "limit": 1000}}'
```

The response will be streamed as Server-Sent Events (SSE):

```
data: {"type": "start", "tool": "odoo_search", "timestamp": "2024-01-01T00:00:00"}
data: {"type": "chunk", "data": [...], "progress": {"current": 10, "total": 1000}}
data: {"type": "chunk", "data": [...], "progress": {"current": 20, "total": 1000}}
...
data: {"type": "end", "timestamp": "2024-01-01T00:00:10"}
```

## WebSocket Usage

Connect to the WebSocket endpoint for real-time communication:

```javascript
const ws = new WebSocket('ws://localhost:8000/mcp/ws');

ws.onopen = function(event) {
    // Send MCP request
    ws.send(JSON.stringify({
        method: 'tools/call',
        params: {
            name: 'odoo_search',
            arguments: {
                model: 'res.partner',
                limit: 10
            }
        },
        id: '1'
    }));
};

ws.onmessage = function(event) {
    const response = JSON.parse(event.data);
    console.log('Received:', response);
};
```

## Docker Support

Build and run with Docker:

```bash
# Build image
docker build -t odoo-mcp-server .

# Run container
docker run -p 8000:8000 --env-file .env odoo-mcp-server
```

## Development

Run in development mode:

```bash
DEBUG=true python start.py
```

This enables:
- Auto-reload on code changes
- Detailed logging
- Enhanced error messages

## Testing

Run tests:

```bash
pytest tests/
```

## Security

- Configure `API_KEY` for authentication
- Set `ALLOWED_IPS` to restrict access
- Use HTTPS in production
- Keep Odoo credentials secure

## Claude Desktop Integration

### Quick Setup

Generate Claude Desktop configuration automatically:

```bash
# Interactive configuration
make claude-config

# View examples
make claude-examples
```

### Manual Configuration

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "odoo": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-http-client",
        "http://localhost:8000/mcp"
      ],
      "env": {
        "MCP_HTTP_URL": "http://localhost:8000"
      }
    }
  }
}
```

For detailed Claude Desktop setup, see [Claude Desktop Setup Guide](docs/claude-desktop-setup.md).

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Claude Desktop │───▶│   FastAPI       │───▶│   Odoo Server   │
│   MCP Client    │    │   MCP Server    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                       ┌─────────────────┐
                       │   HTTP/WS       │
                       │   Streaming     │
                       └─────────────────┘
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.