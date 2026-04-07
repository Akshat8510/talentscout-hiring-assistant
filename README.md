# 🎯 TalentScout: AI Hiring Assistant

An intelligent chatbot designed to automate the initial screening process for technical roles. Built with Python, Streamlit, and Google Gemini 1.5.

## 🚀 Overview
TalentScout assists recruitment teams by:
1.  **Gathering Candidate Info:** Collecting personal and professional details.
2.  **Dynamic Technical Screening:** Generating 3-5 tailored technical questions based on the candidate's specific tech stack.
3.  **Secure Handling:** Managing data with privacy-first principles (GDPR-compliant hashing).

## 🛠️ Technical Stack
-   **Frontend:** Streamlit
-   **LLM:** Google Gemini 1.5 Flash (via Google AI Studio)
-   **Storage:** Local JSON (Simulated database)
-   **Security:** SHA-256 Hashing for sensitive PII logs.

## ⚙️ Setup Instructions
1.  **Clone the repository:**
    ```bash
    git clone <your-repo-link>
    cd talentscout
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Environment Variables:**
    - Create a `.env` file from `.env.example`.
    - Add your `GGROQ_API_KEY` from GROQ 
4.  **Run the app:**
    ```bash
    streamlit run app.py
    ```

## 🧠 Prompt Engineering Strategy
-   **Role Prompting:** The assistant is persona-locked as "Aria," a professional recruiter.
-   **Sequential Logic:** The system prompt enforces a 4-phase workflow (Greeting -> Info -> Tech Quiz -> Closing) to prevent the LLM from skipping steps.
-   **Few-Shot Context:** Current candidate data is injected into every prompt to ensure Aria remembers what has already been collected.

## 🛡️ Data Privacy
-   Emails are hashed using SHA-256 before being recorded in logs.
-   PII (Phone/Email) is stored in a separate `contact` object, simulating an encrypted production database.
