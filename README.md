# 🤖 Corporate Internal RAG Chatbot with RBAC

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Framework](https://img.shields.io/badge/Framework-LangChain-green)
![Security](https://img.shields.io/badge/Security-RBAC%20%2B%20JWT-red)

## 📌 Project Overview
This project is an internal **Question-Answering Bot** designed for secure corporate environments. It uses **Retrieval-Augmented Generation (RAG)** to answer employee queries based on internal documents (PDFs, Markdown, CSVs). 

Crucially, it implements **Role-Based Access Control (RBAC)** to ensure employees only access data permitted for their department. For example, a Finance user can access financial reports, but cannot access HR salary data.

---

## 🚀 Key Features
* **📚 RAG Pipeline:** Ingests and indexes internal documents for accurate, context-aware answers.
* **🔐 Zero-Trust Security:** Every query is filtered based on the user's role (Finance, HR, Engineering, Marketing).
* **🧠 Hybrid Intelligence:** Uses internal docs for specific questions and switches to General AI for general knowledge.
* **🔑 JWT Authentication:** Secure login system with hashed passwords and session management.
* **⚡ Modern Stack:** Built with FastAPI (Backend), Streamlit (Frontend), and ChromaDB (Vector Store).

---

## 🛠️ Tech Stack
* **Frontend:** Streamlit
* **Backend:** FastAPI
* **LLM:** Google Gemini Pro (`gemini-pro-latest`)
* **Vector DB:** ChromaDB (Local Persistence)
* **Orchestration:** LangChain
* **Auth:** OAuth2 + JWT (HS256) + Bcrypt

---

## 🔐 Authentication Design (Milestone 4)
We implemented a secure **Role-Based Access Control** system.

### 1. User Roles & Scope
| Username | Role | Access Scope |
| :--- | :--- | :--- |
| `finance_user` | **Finance** | `resources/Finance/` + `resources/General/` |
| `hr_user` | **HR** | `resources/HR/` + `resources/General/` |
| `eng_user` | **Engineering** | `resources/Engineering/` + `resources/General/` |
| `marketing_user`| **Marketing** | `resources/Marketing/` + `resources/General/` |

### 2. Login Flow
1.  **Login:** User enters credentials in the Streamlit UI.
2.  **Verify:** Backend checks the hash against the secure registry.
3.  **Token:** If valid, the server issues a **JWT Token** containing the user's Role.
4.  **Query:** Every chat message includes this token. The backend extracts the role and applies a **Strict Filter** to the Vector Database search.

---

## 📂 Project Structure
```bash
rag-chatbot/
├── app/
│   ├── main.py          # FastAPI Backend (Routes & Logic)
│   ├── auth.py          # Authentication (Hashing & JWT)
│   ├── ingest.py        # ETL Pipeline (Load -> Chunk -> Vectorize)
│   └── models.py        # Pydantic Data Schemas
├── frontend/
│   └── streamlit_app.py # User Interface
├── resources/           # Document Knowledge Base
│   ├── Finance/         # (Restricted)
│   ├── HR/              # (Restricted)
│   ├── Marketing/       # (Restricted)
│   ├── Engineering/     # (Restricted)
│   └── General/         # (Public - Accessible by all)
├── chroma_db/           # Local Vector Database
├── requirements.txt     # Dependencies
└── README.md            # Documentation
