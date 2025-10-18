# 🇮🇳 AI-Sahayak — Government Scheme Explainer

**AI-Sahayak** is an intelligent Streamlit web application that simplifies complex Indian Government schemes into clear, structured summaries in both **English** and **Telugu**.  
It automatically extracts, analyzes, and presents essential details like **eligibility, benefits, and how to apply**, helping citizens and students easily understand official scheme information.

---

## 🚀 Features

### 🧠 Core Functionalities
- **Multi-layer content extraction**  
  Extracts data from government websites using a fallback system:
  - Playwright → Selenium → Readability → Requests.
- **AI-powered summarization**  
  Uses OpenRouter/OpenAI models to generate structured summaries.

### 📄 Consolidated Summary Format
Each output follows this exact, official-style structure:

Consolidated Summary: [Scheme Name]

Eligibility
Who can apply (age, gender, income, occupation, etc.)
Required conditions (BPL, disability, widowhood, etc.)

Benefits
Financial benefits and assistance amounts
Mode of transfer (DBT, PFMS, etc.)
Monitoring or review mechanisms (if any)

How to Apply
Application steps
Where to apply (Gram Panchayat, online portal, etc.)
Required documents
Approval and disbursement process

Additional Information (if available)
Scheme objectives
Implementing ministry/department
Helpline or grievance redressal mechanism

yaml
Copy code

### 🌐 Other Features
- **Telugu Translation** — Converts English summaries into clear Telugu text.  
- **PDF Generation** — Automatically saves summaries to your local `Downloads/AI-Sahayak/` folder.  
- **WhatsApp Sharing** — Share short summaries directly, or full summaries via PDF.  
- **Voice Output (Telugu)** — Listen to the translated summary using `gTTS`.  
- **Smart Q&A Engine** — Ask natural-language questions about any extracted scheme.  
- **Recent History Sidebar** — Displays last 5 analyzed schemes.  
- **Category Pie Chart** — Visual overview of common government scheme domains.  

---

## 🏗️ Tech Stack

| Component | Technology |
|------------|-------------|
| Frontend UI | Streamlit |
| Backend | Python |
| LLM Provider | OpenRouter API (Mistral, Gemma, etc.) |
| Database Cache | SQLite |
| Text-to-Speech | gTTS |
| PDF Export | ReportLab |
| Visualization | Plotly |
| Web Scraping | Playwright, Selenium, Readability, BeautifulSoup |

---
