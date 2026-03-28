# LexAI — Agentic AI for Autonomous Legal Case Analysis

Upload legal documents (PDF) and let an AI agent autonomously perform a 9-step deep analysis: case classification, summarization, key issue extraction, party identification, timeline building, risk scoring, evidence gap analysis, recommendations, and similar case search. Generates downloadable PDF reports.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React + Tailwind CSS (Vite) |
| Backend | Python FastAPI |
| PDF Parsing | pdfplumber |
| AI | Groq API (llama-3.3-70b-versatile) |
| PDF Export | reportlab |

## Prerequisites

- Python 3.10+
- Node.js 18+
- [Groq API key](https://console.groq.com) (free)

## Setup

### 1. Backend

```bash
cd legal-ai/backend
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt

# Set your Groq API key:
# Windows PowerShell:
$env:GROQ_API_KEY="gsk_your_key_here"
# macOS/Linux:
export GROQ_API_KEY="gsk_your_key_here"

# Run the backend:
uvicorn main:app --reload --port 8000
```

### 2. Frontend

```bash
cd legal-ai/frontend
npm install
npm run dev
```

### 3. Open

Visit **http://localhost:5173** in your browser.

## Demo Mode

Click **"Try Demo"** on the upload page to see a full analysis of a realistic Indian property dispute case — no API key required.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/ready` | Readiness check (dependency-aware) |
| POST | `/upload` | Upload PDF, run analysis, return JSON |
| POST | `/report` | Accept analysis JSON, return PDF |
| GET | `/demo` | Return demo analysis data |
| GET | `/analyze-stream` | SSE demo stream with progress |
| POST | `/analyze-stream-upload` | SSE stream for uploaded PDF |

## Environment Profile

Backend now supports `.env` loading with profile-based behavior.

Key variables (see `backend/.env.example`):

- `ENV_PROFILE` — `development` or `production`
- `ALLOWED_ORIGINS` — required in production for strict CORS
- `REQUEST_MAX_BODY_MB` — max accepted request body size
- `READINESS_REQUIRE_GROQ` — if `true`, `/ready` returns `503` without `GROQ_API_KEY`
- `LOG_LEVEL` — API log verbosity

## Project Structure

```
legal-ai/
├── backend/
│   ├── main.py           # FastAPI app with endpoints
│   ├── agent.py          # 9-step agentic AI pipeline
│   ├── pdf_parser.py     # PDF text extraction
│   ├── report_gen.py     # PDF report generation
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx       # Main app (3 states: upload → analyzing → results)
│   │   ├── components/
│   │   │   ├── UploadZone.jsx    # Drag & drop PDF upload
│   │   │   ├── Dashboard.jsx     # Results grid layout
│   │   │   ├── RiskScore.jsx     # Animated circular risk gauge
│   │   │   ├── Timeline.jsx      # Vertical timeline with events
│   │   │   ├── Insights.jsx      # Tabbed analysis details
│   │   │   └── ReportButton.jsx  # Download PDF report
│   │   └── index.css
│   └── package.json
└── README.md
```

## How It Works

1. **Upload** — User drags/drops a PDF or clicks to browse
2. **Extract** — Backend parses PDF text with pdfplumber
3. **Analyze** — 9-step agentic pipeline runs sequentially via Groq API:
   - Case classification
   - Plain English summary
   - Key legal issues
   - Party identification
   - Timeline extraction
   - Risk scoring (0-100 per party)
   - Missing evidence flags
   - Actionable recommendations
   - Similar Indian court cases
4. **Display** — Results shown in animated dashboard
5. **Export** — Click "Download Report" for professional PDF

## Without a Groq API Key

The app works in demo mode without an API key — it returns realistic mock analysis data for an Indian property dispute case. Set `GROQ_API_KEY` to enable real AI analysis.

## License

MIT
