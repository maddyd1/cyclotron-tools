#!/bin/bash
cd "$(dirname "$0")/.."
source venv/bin/activate
cd trace
streamlit run app.py
