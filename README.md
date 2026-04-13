# Extractor Pro

## Run Scripts

### 1. Activate virtual environment

```bash
cd /home/bitskraft/Desktop/Bitskraft/extractor_pro
source venv/bin/activate
```

### 2. Run database migrations (Alembic)

```bash
cd backend
alembic upgrade head
```

### 3. Run backend (FastAPI with Uvicorn)

```bash
cd /home/bitskraft/Desktop/Bitskraft/extractor_pro/backend
uvicorn app.main:app --reload --port 8001
```

### 4. Run frontend (Streamlit)

```bash
cd /home/bitskraft/Desktop/Bitskraft/extractor_pro/frontend
streamlit run streamlit_app.py
```
