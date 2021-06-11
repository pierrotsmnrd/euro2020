#--- Base ---
FROM python:3.8

RUN apt-get update && apt-get install -y wget vim 

RUN apt-get install -y libproj-dev proj-data proj-bin  
RUN apt-get install -y libgeos-dev  


# Copy and install requirements
COPY ./requirements.txt /app/requirements.txt
RUN pip3 install -r /app/requirements.txt


WORKDIR /app
EXPOSE 5006

CMD cron && python /app/app.py 


