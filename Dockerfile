FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY montainer.py requirements.txt /usr/src/app/
COPY montainer .

CMD [ "python", "./montainer.py" ]
