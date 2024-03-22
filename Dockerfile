FROM python:3.10-slim
WORKDIR /app

# Install FreeTDS and dependencies
RUN apt-get update \
 && apt-get install unixodbc -y \
 && apt-get install unixodbc-dev -y \
 && apt-get install freetds-dev -y \
 && apt-get install freetds-bin -y \
 && apt-get install tdsodbc -y \
 && apt-get install --reinstall build-essential -y

# Populate "ocbcinst.ini" as this is where ODBC driver config sits
RUN echo "[FreeTDS]\n\
Description = FreeTDS Driver\n\
Driver = /usr/lib/x86_64-linux-gnu/odbc/libtdsodbc.so\n\
Setup = /usr/lib/x86_64-linux-gnu/odbc/libtdsS.so" >> /etc/odbcinst.ini

# Pip install
ADD src ./src
ADD pyproject.toml .
ADD setup.py .

# Pip command. Without '-e' flag, index.html isn't found. There's probably a
# better way to add the static html files to the site-packages.
RUN pip install -e .[server] --no-cache-dir

CMD ["uvicorn", "aind_metadata_service.server:app", "--host", "0.0.0.0", "--port", "5000"]
