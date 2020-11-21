setup:
	( make setup-backend )
	( make setup-frontend )

setup-backend:
	conda env create -f environment.yml
	wget https://cdn.jsdelivr.net/musescore/v3.5.2/MuseScore-3.5.2.312125617-x86_64.AppImage -O backend/MuseScore.AppImage
	chmod +x backend/MuseScore.AppImage

start-backend:
	( cd backend/; flask run --host=0.0.0.0)

setup-frontend:
	( cd frontend/; yarn )

start-frontend:
	( cd frontend/; yarn start )