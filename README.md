# ApplyWise

ApplyWise is an internship application tracker with a FastAPI API and a static HTML/Tailwind frontend. It supports registration, login, viewing and updating the signed-in user's profile, private per-user applications, status tracking, notes, search, filtering, and application create/edit/delete.

## Run locally

1. Configure `Backend/.env` with `DATABASE_URL`, `JWT_SECRET_KEY`, and any other values used by the backend. Use a PostgreSQL database and keep this file private.
2. From `Backend`, activate your Python environment, install the dependencies, apply the database migration, and start the API:

   ```powershell
   pip install -r requirements.txt
   alembic upgrade head
   uvicorn app.main:app --reload
   ```

3. From `Frontend`, build the styles and start the static frontend server:

   ```powershell
   npm install
   npm run build
   npm start
   ```

4. Open `http://localhost:3000`. The server serves `Frontend/src` as the web root, so the URL opens the public landing page directly. New users can register or log in from there. The API runs at `http://localhost:8000`; for a same-origin frontend, open `http://localhost:8000/app/`.

For frontend styling changes, run `npm run dev:css` in another terminal while editing, then run `npm run build`. The API docs are available at `http://localhost:8000/docs`.

The dashboard hero photo is loaded from `Frontend/src/assets/Lone Hiker Above the Purple Mountains.png`.
