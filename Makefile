setup:
	( make install-python-deps )

install-python-deps:
	conda env create -f environment.yml

setup-backend:
	wget https://cdn.jsdelivr.net/musescore/v3.5.2/MuseScore-3.5.2.312125617-x86_64.AppImage -O backend/MuseScore.AppImage
	chmod +x backend/MuseScore.AppImage

start-backend:
	conda init
	conda activate MelodySnippets
	( cd backend/; flask run --host=0.0.0.0)