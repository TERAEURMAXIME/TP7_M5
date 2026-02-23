from datetime import date
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates


BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR))

app = FastAPI()


MONTHS_FR = {
	"janvier": 1,
	"février": 2,
	"fevrier": 2,
	"mars": 3,
	"avril": 4,
	"mai": 5,
	"juin": 6,
	"juillet": 7,
	"août": 8,
	"aout": 8,
	"septembre": 9,
	"octobre": 10,
	"novembre": 11,
	"décembre": 12,
	"decembre": 12,
}


def compute_age(day: int, month: int, year: int) -> int:
	today = date.today()
	age = today.year - year
	if (today.month, today.day) < (month, day):
		age -= 1
	return age


@app.get("/")
def index_page(request: Request):
	return templates.TemplateResponse("index.html", {"request": request})


@app.get("/style.css")
def stylesheet():
	return FileResponse(BASE_DIR / "style.css", media_type="text/css")


@app.get("/images/{filename:path}")
def images(filename: str):
	return FileResponse(BASE_DIR / "images" / filename)


@app.post("/inscription", response_class=HTMLResponse)
async def registration_result(request: Request):
	form_data = await request.form()

	nom = str(form_data.get("nom", "")).strip()
	prenom = str(form_data.get("prenom", "")).strip()

	day = int(str(form_data.get("jour", "1")))
	month_label = str(form_data.get("mois", "janvier")).strip().lower()
	year = int(str(form_data.get("annee", "2000")))
	month = MONTHS_FR.get(month_label, 1)

	age_utilisateur = compute_age(day, month, year)

	reponses_questionnaire = [
		str(form_data.get(f"q{i}", "Non")).strip().capitalize() for i in range(1, 6)
	]

	cout_base = 50
	cout_questions = reponses_questionnaire.count("Oui") * 10
	surcharge_age = 0
	if isinstance(age_utilisateur, int) and age_utilisateur > 65:
		surcharge_age = 0.02 * (age_utilisateur - 65) * cout_base
	cout_total = round(cout_base + cout_questions + surcharge_age, 2)
	monthly_fee_formatted = f"{cout_total:.2f}".replace(".", ",")

	return templates.TemplateResponse(
		"inscription.html",
		{
			"request": request,
			"nom": nom,
			"prenom": prenom,
			"age": age_utilisateur,
			"monthly_fee": monthly_fee_formatted,
		},
	)


if __name__ == "__main__":
	uvicorn.run("main:app", host="127.0.0.1", port=5000, reload=False)
