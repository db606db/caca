# French Discord Bot

## Overview

This is a comprehensive Discord moderation bot written in Python using the discord.py library. The bot provides moderation tools, anti-spam protection, server configuration management, and utility commands. It's designed with a modular cog-based architecture for easy maintenance and extensibility.

## System Architecture

### Frontend Architecture
- **Discord Interface**: Slash commands and traditional prefix commands (`!`)
- **Interactive Embeds**: Rich embed messages for user feedback and information display
- **Permission-based Access**: Role and permission-based command access control

### Backend Architecture
- **Modular Cog System**: Functionality separated into distinct modules (cogs)
- **In-Memory Configuration**: Guild settings stored in memory with default fallbacks
- **Event-driven Processing**: Discord.py event handlers for real-time message processing
- **Asynchronous Operations**: Full async/await pattern for non-blocking operations

### Core Framework
- **Discord.py**: Primary bot framework with full intents enabled
- **Python 3.7+**: Modern Python with type hints and async support
- **Logging System**: File and console logging for debugging and monitoring

## Key Components

### 1. Main Bot Class (`main.py`)
- **FrenchBot**: Custom bot class extending commands.Bot
- **Auto-loading**: Automatic cog loading on startup
- **Command Sync**: Slash command synchronization with Discord
- **Configuration Integration**: Built-in config system access

### 2. Moderation System (`cogs/moderation.py`)
- **Member Management**: Kick, ban, mute functionality
- **Permission Checks**: Hierarchical permission validation
- **Audit Logging**: Comprehensive action logging
- **DM Notifications**: Private message alerts to moderated users

### 3. Anti-Spam Protection (`cogs/anti_spam.py`)
- **URL Detection**: Regex-based link and domain filtering
- **Rate Limiting**: Message frequency monitoring
- **Whitelist System**: Configurable allowed domains
- **Automatic Actions**: Progressive punishment system

### 4. Configuration Management (`cogs/configuration.py`)
- **Guild Settings**: Per-server configuration storage
- **Role Management**: Moderator and mute role assignment
- **Channel Setup**: Logs channel configuration
- **Real-time Updates**: Live configuration viewing and editing

### 5. Utility Commands (`cogs/utility.py`)
- **Server Information**: Comprehensive server statistics
- **Bot Status**: Latency and performance monitoring
- **System Health**: Resource usage tracking

### 6. Support Systems
- **Embed Builder** (`utils/embeds.py`): Consistent message formatting
- **Permission Checks** (`utils/checks.py`): Reusable authorization decorators
- **Configuration Store** (`config/settings.py`): Centralized settings management

## Data Flow

### 1. Command Processing
```
User Input → Discord API → Bot Event Handler → Permission Check → Cog Method → Response Generation → Discord API → User
```

### 2. Anti-Spam Detection
```
Message Event → Content Analysis → Pattern Matching → Rule Evaluation → Action Decision → Moderation Response
```

### 3. Configuration Updates
```
Admin Command → Permission Validation → Config Update → Memory Storage → Confirmation Response
```

## External Dependencies

### Core Dependencies
- **discord.py**: Discord API wrapper and bot framework
- **asyncio**: Asynchronous I/O operations
- **logging**: Built-in Python logging system
- **re**: Regular expression processing for anti-spam
- **datetime**: Time-based operations and scheduling

### System Dependencies
- **psutil**: System performance monitoring (utility commands)
- **platform**: System information retrieval

### Discord API Integration
- **Gateway Connection**: Real-time event streaming
- **REST API**: Command responses and actions
- **Slash Commands**: Modern Discord command interface
- **Permissions System**: Discord's built-in authorization

## Deployment Strategy

### Render.com Production Deployment
- **Platform**: Optimized for Render.com hosting (not Replit)
- **Logging**: stdout-only logging for Render's log aggregation
- **Configuration Files**: Complete Render setup with render.yaml, Procfile, runtime.txt
- **Requirements**: render_requirements.txt for Python dependencies
- **Auto-deployment**: Configured for Render's continuous deployment

### Local Development
- **Environment Variables**: Token and configuration management via .env
- **Hot Reloading**: Cog reload capability for development
- **Debug Logging**: Enhanced logging for development debugging

### Production Considerations
- **Memory Storage**: Current configuration uses in-memory storage
- **Scalability**: Single-instance design suitable for moderate server loads
- **Monitoring**: stdout logging for Render's monitoring system
- **Zero-downtime**: Render handles deployment and health checks

### Configuration Files for Render
- **render.yaml**: Service configuration and environment variables
- **Procfile**: Start command specification
- **runtime.txt**: Python version specification (3.11.0)
- **render_requirements.txt**: Production dependencies list

## User Preferences

Preferred communication style: Simple, everyday language.

## Changelog

- June 29, 2025: Initial setup - Complete Discord bot with 30 slash commands
- June 29, 2025: Added comprehensive moderation system with progressive punishments
- June 29, 2025: Implemented anti-spam and anti-link protection with configurable settings
- June 29, 2025: Created interactive configuration panel `/panel` for administrators
- June 29, 2025: Added complete logging system with Discord embeds for all events
- June 29, 2025: **RENDER DEPLOYMENT READY** - Configured for Render.com hosting with optimized logging and deployment files