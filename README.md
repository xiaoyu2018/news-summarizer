- [🇨🇳 简体中文](README.zh-CN.md)
- [🇺🇸 English](README.md)

# Synapulse

**Synapulse** connects you with industry frontiers.

- **Collect**: Automatically gather raw information from designated sources (email newsletters, X accounts, Reddit, etc.)
- **Analyze**: AI-powered filtering, deduplication, and core insight extraction to generate structured summaries
- **Deliver**: Send to your preferred channel (email, Feishu, etc.) on a scheduled basis (daily/weekly)


## Features

- **Modular Architecture**: Pluggable Collectors, Processors, and Senders
- **Multi-domain Support**: Configure multiple domains (tech, finance, healthcare, etc.) with independent processing
- **Multi-instance Support**: Multiple instances of the same type, with sensitive info via separate environment variables
- **Configuration-driven**: YAML config + Markdown prompts, separated from code
- **Environment Variable Injection**: Sensitive info uses `${ENV_VAR_NAME}` placeholders for security

## Project Structure

```
Synapulse/
├── app/                        # Application code directory
│   ├── conf/                   # Configuration files
│   │   ├── config.yaml         # Config file (not committed)
│   │   └── config.example.yaml # Config example
│   ├── prompts/                # Prompt templates
│   │   └── tech.md             # Tech domain prompt
│   ├── src/                    # Source code
│   │   ├── main.py             # Main entry point
│   │   ├── models.py           # Data models
│   │   ├── config_loader.py    # Config loader
│   │   ├── summarizer.py       # Main controller
│   │   ├── collectors/         # Collectors
│   │   │   ├── base.py
│   │   │   └── email_collector.py
│   │   ├── processors/         # Processors
│   │   │   ├── base.py
│   │   │   └── ai_processor.py
│   │   ├── senders/            # Senders
│   │   │   ├── base.py
│   │   │   └── email_sender.py
│   │   └── utils/              # Utilities
│   │       ├── logger.py
│   │       └── html_cleaner.py
│   └── tests/                  # Tests
│       └── test_email_collector.py
├── .github/workflows/           # GitHub Actions
│   └── daily_summary.yml       # Daily scheduled task
├── pyproject.toml
└── README.md
```

## Quick Start

### 1. Clone the Project

```bash
git clone <repository-url>
cd synapulse
```

### 2. Install Dependencies

```bash
uv sync
```

### 3. Configuration

Edit `app/conf/config.yaml` and configure:

- **Collector**: IMAP email settings (account, password, env var placeholders)
- **Processor**: AI API settings (provider, api_base, api_key, model)
- **Sender**: SMTP settings (sender, receiver, password)

### 4. Set Environment Variables

Set corresponding environment variables based on placeholders in the config:

```bash
# Email account and password
export EMAIL1_ACCOUNT="your-email@gmail.com"
export EMAIL1_PASSWORD="your-email-password"

# AI API Key
export LLM1_API_KEY="your-deepseek-api-key"

# Sender and receiver
export EMAIL3_ACCOUNT="sender@gmail.com"
export EMAIL3_PASSWORD="your-sender-password"
export RECEIVER_EMAIL="receiver@example.com"
```

### 5. Run

```bash
uv run python -m app.src.main
```

## Configuration Guide

### Global Config

```yaml
global:
  timezone: "Asia/Shanghai"
  log_level: "INFO"
```

### Domain Config

```yaml
domains:
  - name: "tech"              # Domain name
    collectors:               # Collector list
      - name: "EMAIL1"
        type: email
        imap_server: "imap.gmail.com"
        email_account: "sub@gmail.com"
        email_password: "${PASSWORD_EMAIL1}"
        mailbox: "INBOX"
        mark_as_seen: true
        time_range_days: 1
    processor:                # Processor
      type: ai
      name: "LLM1"
      provider: "deepseek"
      api_base: "https://api.deepseek.com/v1"
      api_key: "${LLM1_API_KEY}"
      model: "deepseek-chat"
      prompt_file: "app/prompts/tech.md"
    sender:                   # Sender
      type: email
      name: "EMAIL2"
      smtp_server: "smtp.gmail.com"
      smtp_port: 465
      sender_email: "sender@gmail.com"
      sender_password: "${EMAIL3_PASSWORD}"
      receiver_email: "daily@example.com"
      subject_prefix: "Tech Daily"
```

### Environment Variable Placeholders

Sensitive info in config uses `${ENV_VAR_NAME}` format placeholders, resolved at runtime from environment variables.

## Prompt Configuration

Prompt templates are in `app/prompts/` directory, in Markdown format. `{combined_content}` in the template will be replaced with collected news content.

Example (`app/prompts/tech.md`):

```markdown
You are a tech news editor. Please organize today's tech news summary based on the following content.

Requirements:
- Only extract information related to AI applications, mobile devices, and digital products
- Remove duplicate news
- Provide core summary for each news item

News Content:
{combined_content}
```

## GitHub Actions Scheduled Task

The project has GitHub Actions configured to run daily at UTC 0.

Add the following Secrets in GitHub repository settings:

- `EMAIL1_ACCOUNT`
- `EMAIL1_PASSWORD`
- `LLM1_API_KEY`
- `EMAIL3_ACCOUNT`
- `EMAIL3_PASSWORD`
- `RECEIVER_EMAIL`

## Extension Development

### Add New Collector

1. Create a new file in `app/src/collectors/`, inherit from `Collector` base class
2. Implement `collect()` method
3. Register in `app/src/summarizer.py` `_create_collector()`

### Add New Processor

1. Create a new file in `app/src/processors/`, inherit from `Processor` base class
2. Implement `process()` method
3. Register in `app/src/summarizer.py` `_create_processor()`

### Add New Sender

1. Create a new file in `app/src/senders/`, inherit from `Sender` base class
2. Implement `send()` method
3. Register in `app/src/summarizer.py` `_create_sender()`

## Sponsor

If you find this project helpful, please scan to sponsor!

<img src="assets/sponsor-wechat.png" width="200" alt="WeChat Sponsor QR Code">

## TODO

- [ ] Optimize SourceItem structure (urls), unify parsing methods (to_str, to_dict...)
- [ ] Improve tech.md prompt, optimize generated content (categorized summary, better info display)
- [ ] Fix occasional info extraction failure in ai_processor
- [x] Optimize logging pattern

## License

MIT
