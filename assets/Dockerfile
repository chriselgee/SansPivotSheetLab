FROM python:3.10-bullseye

RUN python3 -m pip install flask \
    icecream \
    lxml

RUN mkdir /opt/website
COPY website/ /opt/website/

WORKDIR "/opt/website"
CMD ["/bin/bash"]
# CMD ["python3", "webserve.py"]