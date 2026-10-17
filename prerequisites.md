# Prerequisites

To run this project you need:

1. Python 3.10 or newer
2. A free Neo4j AuraDB account and one Free instance
3. The ESCO v1.2.1 English CSV dataset (download from the
   European Commission ESCO website, then unzip into a folder named "esco")
4. The Python packages in requirements.txt:
   pip install -r requirements.txt
5. A file named .env in the project folder (copy .env.example and
   fill in your own Aura details). Never upload .env to GitHub.

## Run order (planned, not tested yet)

1. python load_esco.py esco --dry-run
2. python load_esco.py esco
3. Run the PREREQUISITE_OF queries
4. streamlit run app.py
