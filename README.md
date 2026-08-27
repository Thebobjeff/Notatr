# 📝 Notatr

> Transform handwritten meeting notes into actionable Notion tasks using Gemini AI.

## 💥 The Problem
Students and professionals waste hours deciphering scribbled notes because converting handwritten pages into structured tasks is tedious work. Insights get buried, and valuable time is spent transcribing notebooks instead of learning or executing.

## ✨ The Solution
**Notatr** is a Streamlit application powered by Gemini Vision AI. Simply upload photos of your handwritten notes or whiteboards, and the app automatically extracts actionable tasks and syncs them straight into your Notion workspace.

## 🚀 Key Features
* **Multi-Image Upload:** Process multiple pages of meeting notes or whiteboard photos at once.
* **Gemini Vision AI:** Accurate handwriting recognition and intelligent extraction of tasks, assignees, and action items.
* **Direct Notion Integration:** Automatically creates new entries in your target Notion notebook.
* **Live Status Tracking:** Real-time feedback visualizer during processing.

## ⚙️ Tech Stack
* **Frontend:** Streamlit
* **AI Model:** Google Gemini 3.7 Flash
* **Integrations:** Notion API (`notion-client`)
* **Language:** Python 3.10+

## 🛠️ Quickstart

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/your-username/meeting-notes-digitizer.git](https://github.com/your-username/meeting-notes-digitizer.git)
   cd meeting-notes-digitizer

2. **Run the program**
   ```bash
   streamlit run app.py
