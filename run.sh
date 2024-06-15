pip install -r requirements.txt
export PYTHONPATH=$PYTHONPATH:$(pwd)
streamlit run app/landing.py --server.port 3049