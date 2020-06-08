FROM python:3.8

WORKDIR /app

ADD ./data /app/data
ADD ./assets /app/assets

RUN apt-get update && apt-get install -y binutils libproj-dev gdal-bin
RUN apt-get update && apt-get install --yes libgdal-dev
RUN apt-get update && apt-get install --yes libspatialindex-dev
RUN apt-get -y update && apt-get install -y libzbar-dev python-dev
RUN apt-get -y update && apt-get install gcc libc-dev g++ libffi-dev libxml2 libffi-dev unixodbc-dev -y
RUN apt-get update && apt-get install -y --no-install-recommends \
    unixodbc-dev \
    unixodbc \
    libpq-dev
# Update C env vars so compiler can find gdal
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

COPY ["./requirements.txt", "/data", "./analyzer.py", "./app.py", "./extractor.py", "./"]

RUN pip install -r ./requirements.txt

EXPOSE 8050

CMD ["python", "./extractor.py"]
CMD ["python", "./app.py"]