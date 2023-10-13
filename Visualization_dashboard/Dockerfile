FROM python:3.8-slim

WORKDIR /streamlit_dashboard

COPY . .

COPY ./ceps_dev/ceps /usr/local/sbin

RUN chmod +x /usr/local/sbin/ceps  

RUN pip3 install -r requirements.txt

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
CMD [ "streamlit_app.py", "--server.headless", "true", "--server.fileWatcherType", "none", "--browser.gatherUsageStats", "false"]