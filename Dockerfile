FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8
COPY . .
RUN python -m pip install --upgrade pip
RUN pip3 install -r requirements.txt
EXPOSE 8000
CMD ["uvicorn","main:app", "--host","0.0.0.0","--port","8000"] 

