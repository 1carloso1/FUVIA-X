# start.ps1
$root = $PSScriptRoot

wt `
  new-tab --title "Backend" --startingDirectory "$root\backend" -- cmd /k "..\venv\Scripts\activate && uvicorn main:app --reload --port 8000" `; `
  new-tab --title "Agent" --startingDirectory "$root\agent" -- cmd /k ".\venv\Scripts\activate && uvicorn api:app --reload --port 8001" `; `
  new-tab --title "Frontend" --startingDirectory "$root\frontend" -- cmd /k "npm run dev"