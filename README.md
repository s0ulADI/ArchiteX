# ArchiteX 🏗️

> **AI-powered architecture-to-code platform** — Upload a system architecture diagram or paste a URL, and ArchiteX analyzes it, generates a full backend project structure, and deploys it instantly to Vercel via GitHub.

---

## ✨ Features

- 🖼️ **Vision Parsing** — Understands architecture diagrams (images or screenshots) using Gemini or OpenAI vision models
- 🌐 **URL Scraping** — Scrapes and interprets architecture descriptions from any public URL
- 🧠 **AI Planning** — Uses LLMs to produce a structured service/component plan from parsed input
- 🔍 **Architecture Linting** — Validates and reviews the proposed architecture for best practices
- ⚙️ **Code Generation** — Generates production-ready backend service code for each component
- 🎨 **Frontend Generation** — Scaffolds a frontend interface based on the architecture
- 📦 **Repo Delivery** — Pushes the generated project directly to a new GitHub repository
- 🚀 **Vercel Deployment** — Deploys the project to Vercel automatically

---

## 🗂️ Project Structure

```
ArchiteX/
└── backend/
    ├── main.py               # FastAPI app entry point
    ├── config.py             # Pydantic settings (reads .env)
    ├── requirements.txt      # Python dependencies
    ├── .env.example          # Environment variable template
    ├── routers/
    │   ├── health.py         # Health check endpoint
    │   ├── parse.py          # Image/architecture parsing
    │   ├── generate.py       # Code generation pipeline
    │   ├── frontend_gen.py   # Frontend scaffolding
    │   ├── url_scrape.py     # URL-based architecture input
    │   └── delivery.py       # GitHub push & Vercel deploy
    ├── services/
    │   ├── vision_parser.py  # Vision model integration (Gemini/OpenAI)
    │   ├── planner.py        # Architecture planning via LLM
    │   ├── arch_linter.py    # Architecture validation
    │   ├── code_generator.py # Service code generation
    │   ├── frontend_generator.py  # Frontend code generation
    │   ├── readme_generator.py    # Auto-generates project READMEs
    │   ├── github_pusher.py  # GitHub API integration
    │   ├── vercel_deployer.py     # Vercel deployment integration
    │   ├── repository_store.py    # In-memory repo state management
    │   ├── verifier.py       # Output verification
    │   └── zipper.py         # Project zipping utilities
    ├── models/               # Pydantic request/response models
    ├── templates/            # Jinja2 code templates
    └── utils/                # Shared utilities
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- A [Gemini API key](https://aistudio.google.com/) and/or [OpenAI API key](https://platform.openai.com/)
- A [GitHub OAuth App](https://github.com/settings/developers) (for repo delivery)
- A [Vercel access token](https://vercel.com/account/tokens) (for deployment)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/ArchiteX.git
cd ArchiteX/backend

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env and fill in your API keys
```

### Running the Server

```bash
cd backend
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

---

## 🔑 Environment Variables

Copy `.env.example` to `.env` and populate the following:

| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | Google Gemini API key for vision/generation |
| `OPENAI_API_KEY` | OpenAI API key (optional alternative) |
| `GITHUB_CLIENT_ID` | GitHub OAuth App client ID |
| `GITHUB_CLIENT_SECRET` | GitHub OAuth App client secret |
| `VERCEL_ACCESS_TOKEN` | Vercel personal access token |
| `SCRAPER_TIMEOUT_SECONDS` | Timeout for URL scraping (default: `10`) |
| `MAX_SERVICES` | Max services in a generated architecture (default: `10`) |
| `VISION_MODEL` | Vision model to use: `gemini` or `openai` (default: `gemini`) |
| `REPO_TTL_SECONDS` | In-memory repo TTL in seconds (default: `3600`) |

> ⚠️ **Never commit your `.env` file.** It is listed in `.gitignore`.

---

## 📡 API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/parse` | Parse an architecture image |
| `POST` | `/generate` | Generate code from parsed architecture |
| `POST` | `/frontend/...` | Generate frontend scaffold |
| `POST` | `/url/...` | Scrape & parse a URL |
| `POST` | `/deliver/...` | Push to GitHub & deploy to Vercel |

Full interactive docs available at `/docs` when the server is running.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Framework** | [FastAPI](https://fastapi.tiangolo.com/) |
| **AI Vision** | Google Gemini / OpenAI GPT-4o |
| **GitHub Integration** | [PyGitHub](https://pygithub.readthedocs.io/) |
| **Web Scraping** | HTTPX + BeautifulSoup4 |
| **Templating** | Jinja2 |
| **Config** | Pydantic Settings |
| **Deployment** | Vercel API |

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
