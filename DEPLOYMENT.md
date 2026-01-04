# Deployment Guide (Vercel)

This application is ready for deployment on Vercel. Follow these steps to deploy.

## Prerequisites
1. [Vercel CLI](https://vercel.com/docs/cli) installed or use the Vercel Dashboard.
2. A Vercel account.

## Environment Variables
The application relies on several environment variables for authentication and configuration. You must set these in your Vercel Project Settings.

| Variable | Description |
|----------|-------------|
| `GOOGLE_API_KEY` | Your Google Gemini API Key. |
| `GOOGLE_TOKEN_JSON` | The contents of your local `token.json`. Minify it (remove newlines) to fit in one line. |
| `GOOGLE_CREDENTIALS_JSON` | The contents of your local `credentials.json`. Minify it. |

> [!TIP]
> To "minify" a JSON file for the env var value, you can use an online tool or just run `python -c "import json; print(json.dumps(json.load(open('token.json'))))"` in your terminal.

## Limitations on Serverless
- **Voice Chat**: The voice chat feature uses `ffmpeg` for audio conversion. Vercel Serverless environments do not include `ffmpeg` by default. Voice capabilities might be restricted or fail if the browser sends incompatible audio formats.
- **Database**: If using a local file-based database (like ChromaDB default), data will **not persist** between restarts because the Vercel filesystem is ephemeral. Re-deploying will wipe memory.
- **Dependencies**: To fit within Vercel's serverless limits, I have commented out heavy libraries like `chromadb`, `sentence-transformers` (PyTorch), and `pydub` in `requirements.txt`. The core agent functionality (Email, Calendar) will work, but RAG/Knowledge features are disabled on Vercel.

## Deploying
Run the following command in your terminal:

```bash
vercel --prod
```
