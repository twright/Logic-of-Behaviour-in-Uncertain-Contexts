FROM fedora:latest

RUN dnf -y install sagemath
RUN dnf -y install git wget glpk-devel bison bison-devel flex patch ImageMagick-devel
RUN wget -qO- https://get.haskellstack.org/ | sh
ENV PATH="/root/.local/bin:${PATH}"
RUN git clone https://github.com/twright/bondwb.git
# RUN cd bondwb && perl -pe 's/(?<=enable: )true/false/g' stack.yaml && stack setup
COPY local.patch bondwb/local.patch
RUN cd bondwb && ./install-deps-fedora.sh && patch < local.patch && stack setup && stack install
COPY . lbuc
RUN useradd -m -s /bin/bash -N -u 1000 lbuc && chown -R lbuc lbuc && chown -R lbuc bondwb && cp /root/.local/bin/bondwb /usr/bin/bondwb && cp /root/.local/bin/cpiwb /usr/bin/cpiwb && chmod a+rwx /usr/bin/bondwb && chmod a+rwx /usr/bin/cpiwb
USER lbuc
WORKDIR lbuc
RUN pip3 install --user -r requirements.txt
ENV SAGE_DOC=/usr/share/doc/sagemath SAGE_LOCAL=/usr/lib64/sagemath/local SAGE_EXTCODE=/usr/share/sagemath/etc SAGE_DOC_SRC=/usr/share/doc/sagemath SAGE_SRC=/usr/lib64/sagemath/src SAGE_ROOT=/usr/lib64/sagemath SAGE_PKGS=/usr/lib64/sagemath/local/var/lib/sage/installed SAGE_TESTDIR=/home/twright/.sage/tmp PYTHONPATH=/usr/lib64/sagemath/site-packages:/usr/lib64/sagemath/local/bin SYMPOW_DIR=/home/twright/.sage/sympow SAGE_SHARE=/usr/share/sagemath SAGE_ETC=/usr/share/sagemath/etc SINGULAR_DATA_DIR=/usr/share SINGULAR_SO=/usr/lib64/libSingular-4.1.1.so SINGULAR_BIN_DIR=/usr/lib64/Singular
ENV PATH=/lbuc:${PATH}
ENV PYTHONPATH=/lbuc:${PYTHONPATH}
ENV JUPYTERPATH=/lbuc:${JUPYTERPATH}
ENV SAGE_PATH=/lbuc:${SAGE_PATH}
RUN ./setup.py choose_flowstar -m fastintervals && ./setup.py build_ext
# RUN ./setup.py install --user
RUN cp -R flowstar/ /home/lbuc/.local/lib/python3.7/site-packages/ && cp -R ulbc/ /home/lbuc/.local/lib/python3.7/site-packages/ && cp -R interval_utils.py /home/lbuc/.local/lib/python3.7/site-packages/
EXPOSE 8888
CMD [ "sage", "-n", "jupyter", "--ip=0.0.0.0", "--no-browser" ]