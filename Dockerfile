FROM ubuntu:xenial as bondwb
RUN apt update && apt install -y git wget
RUN wget -qO- https://get.haskellstack.org/ | sh
RUN apt-get -y install ghc libncurses5-dev happy alex libcairo2-dev gsl-bin gsl-ref-html libgsl0-dev liblapack-dev libmpfr-dev
RUN git clone -n https://github.com/twright/bondwb.git && cd bondwb && git checkout 5557788f8cdf780fa2899ca29eb926ed5c3ab205
ENV PATH="/root/.local/bin:${PATH}"
RUN cd bondwb && mv -f stack-minimal.yaml stack.yaml && stack setup && stack install

FROM sagemath/sagemath:9.0-py3 as lbuclib

USER root
RUN apt update && apt -y install git wget software-properties-common
RUN add-apt-repository -y ppa:ubuntu-toolchain-r/test
RUN apt update && apt -y install build-essential bison libbison-dev flex gcc-9 g++-9
RUN update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-9  100 --slave /usr/bin/g++ g++ /usr/bin/g++-9
COPY flowstar flowstar
COPY setup.py setup.py
RUN sage -python3 ./setup.py choose_flowstar -m fastintervals
COPY ulbc ulbc
RUN sage -python3 ./setup.py build_ext

FROM sagemath/sagemath:9.0-py3

USER root
RUN apt update && apt install -y libgsl2 libblas3 liblapack3
COPY --from=bondwb /root/.local/bin/bondwb-minimal /usr/bin/bondwb
COPY --from=lbuclib /home/sage/flowstar/flowstar-2.1.0/libflowstar.so /usr/lib/libflowstar.so
COPY --chown=1000:1000 --from=lbuclib /home/sage/build/lib.linux-x86_64-3.7/flowstar/ /home/sage/sage/local/lib/python3.7/site-packages/flowstar/
COPY --chown=1000:1000 --from=lbuclib /home/sage/ulbc/*.py /home/sage/sage/local/lib/python3.7/site-packages/ulbc/

USER sage
COPY requirements.txt /tmp/
RUN sage -pip install -r /tmp/requirements.txt
COPY models ./models
COPY Introduction.ipynb .
EXPOSE 8888
CMD [ "sage", "-python", "-m", "jupyterlab", "--ip=0.0.0.0", "--no-browser" ]
