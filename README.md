# Boggart 2

## Configuration

Copy this code block to a yaml file on your target machine and save your api tokens:
```yaml
---
discord_token: string
openai_api_key: string
```

> By default, the application looks for the config file at `$HOME/boggart.yml`. Set `BOGGART_CONFIG_PATH` to your custom config file if the location differs.

## Run the Application
This project is packaged with the `uv` package manager. These instructions assume that `uv` and `git ` are installed.

1. Clone this repository
```bash
git clone https://github.com/chandlerberry/boggart-2.git
```

2. Set up the environment
```bash
uv lock
```

3. Run the program:
```bash
uv run boggart
```
