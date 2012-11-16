#!/bin/sh

base_dir="$(dirname $0)"

if [ ! -e /etc/opt/bls/plato/local_settings.py ]; then
    ln -s /opt/bls/plato/src/webfront/local_settings.py /etc/opt/bls/plato/
fi

if [ ! -e /etc/opt/bls/plato/gunicorn.conf.py ]; then
    ln -s /opt/bls/plato/gunicorn.conf.py /etc/opt/bls/plato/
fi

echo /opt/bls/plato/src >/opt/bls/plato/ENV/lib/python2.6/site-packages/plato.pth
cp "${base_dir}/local_settings.py" ${base_dir}/../../src/webfront/
cp "${base_dir}/gunicorn.conf.py" ${base_dir}/../../

