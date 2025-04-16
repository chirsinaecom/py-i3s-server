
# Import python modules
# from __future__ import annotations

from flask import Flask,  abort, Response
from HTTPResponse import HTTPResponse
from io import BytesIO
import os
from pathlib import Path
# import sys
import json
import gzip
import zipfile
# User parameter
host = 'localhost'
port = 5000
home = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), "slpk")  # SLPK Folder

# Flask constructor takes the name of
# current module (__name__) as argument.
app = Flask(__name__)

# #List available SLPK
slpks = [f for f in os.listdir(home) if
         f.lower().endswith('slpk')
         or f.lower().endswith('.eslpk')]


def read_slpk(f, slpk):
    with open(os.path.join(home, slpk), 'rb') as file:
        with zipfile.ZipFile(file) as zip:
            if os.path.splitext(f)[1] == ".gz":  # Unzip GZ
                # GZ file -> convert path sep to zip path sep
                gz = BytesIO(zip.read(f.replace("\\", "/")))
                with gzip.GzipFile(fileobj=gz) as gzfile:
                    return gzfile.read()
            else:
                return zip.read(f.replace("\\", "/"))  # Direct read


def read_eslpk(f, slpk):
    eslpk_path = os.path.join(home, slpk)
    f_path = Path(eslpk_path, f)

    if os.path.splitext(f_path)[1] == ".gz":
        with gzip.open(f_path, 'rb') as gzfile:
            return gzfile.read()
    else:
        with open(f_path, 'rb') as file:
            return file.read()
    pass


def read(f, slpk):
    """Read gz compressed file from slpk (=zip archive) and output result.

    Args:
        f (str): File path inside the SLPK archive.
        slpk (str): Name of the SLPK file (Scene Layer Package).
    """
    if f.startswith("\\"):  # Remove first backslash
        f = f[1:]
    if slpk.endswith('.eslpk'):
        return read_eslpk(f, slpk)
    else:
        return read_slpk(f, slpk)

# @app.after_request
# def after_request_func(response):
#     return response


def stringify_response(func):
    """Convert the HTTPResponse object to a string."""

    def _wrapper(*args, **kwargs):
        response = func(*args, **kwargs)
        if isinstance(response, HTTPResponse):
            return response.toJSON()
        return response
    _wrapper.__name__ = func.__name__
    return _wrapper


@app.route('/')
@stringify_response
def list_services():
    """ List all available SLPK, with LINK to I3S service and Viewer page"""

    return HTTPResponse(body=slpks)


@app.route('/<slpk>/SceneServer')
@app.route('/<slpk>/SceneServer/')
@stringify_response
def service_info(slpk):
    """ Service information JSON """
    if slpk not in slpks:  # Get 404 if slpk doesn't exists
        abort(404, "Can't found SLPK: %s" % slpk)
    SceneServiceInfo = dict()
    SceneServiceInfo["serviceName"] = slpk
    SceneServiceInfo["name"] = slpk
    SceneServiceInfo["currentVersion"] = 10.6
    SceneServiceInfo["serviceVersion"] = "1.6"
    SceneServiceInfo["supportedBindings"] = ["REST"]
    SceneServiceInfo["layers"] = [
        json.loads(read("3dSceneLayer.json.gz", slpk))]

    return HTTPResponse(body=SceneServiceInfo,
                        content_type='application/json')


@app.route('/<slpk>/SceneServer/layers/0')
@app.route('/<slpk>/SceneServer/layers/0/')
@stringify_response
def layer_info(slpk):
    """ Layer information JSON """
    if slpk not in slpks:  # Get 404 if slpk doesn't exists
        abort(404, "Can't found SLPK: %s" % slpk)
    SceneLayerInfo = json.loads(read("3dSceneLayer.json.gz", slpk))
    return HTTPResponse(body=SceneLayerInfo,
                        content_type='application/json')


@app.route('/<slpk>/SceneServer/layers/<layer>/nodepages')
@app.route('/<slpk>/SceneServer/layers/<layer>/nodepages/')
@stringify_response
def node_info(slpk, layer):
    NodeIndexDocument = json.loads(read(
        "nodepages/0.json.gz", slpk
    ))
    return HTTPResponse(body=NodeIndexDocument,
                        content_type='application/json')


@app.route('/<slpk>/SceneServer/layers/<layer>/nodepages/<node>')
@app.route('/<slpk>/SceneServer/layers/<layer>/nodepages/<node>/')
@stringify_response
def node_pages_info(slpk, layer, node):
    """ Node information JSON """
    NodeIndexDocument = json.loads(
        read(f"nodepages/{node}.json.gz", slpk))
    return HTTPResponse(body=NodeIndexDocument,
                        content_type='application/json')


@app.route(
    '/<slpk>/SceneServer/layers/<layer>/nodes/<node>/geometries/<geometry_id>'
)
@app.route(
    '/<slpk>/SceneServer/layers/<layer>/nodes/<node>/geometries/<geometry_id>/'
)
def geometry_info(slpk, layer, node, geometry_id):
    """ Geometry information bin """
    if slpk not in slpks:  # Get 404 if slpk doesn't exists
        abort(404, "Can't found SLPK: %s" % slpk)
    content = read("nodes/%s/geometries/%s.bin.gz" %
                   (node, geometry_id), slpk, )
    if not content:
        abort(404, "Can't found content: %s" % slpk)
    # todo: update to cus http response
    response = Response(
        content, mimetype="application/octet-stream; charset=binary")
    return response


@app.route('/<slpk>/SceneServer/layers/<layer>/nodes/<node>/textures/0_0')
@app.route('/<slpk>/SceneServer/layers/<layer>/nodes/<node>/textures/0_0/')
def textures_info(slpk, layer, node):
    """ Texture information JPG """
    if slpk not in slpks:  # Get 404 if slpk doesn't exists
        abort(404, "Can't found SLPK: %s" % slpk)

    try:
        content = read("nodes/%s/textures/0_0.jpg" % node, slpk)
    except Exception:
        try:
            content = read("nodes/%s/textures/0_0.bin" % node, slpk)
        except Exception:
            content = ""
    finally:
        if content == "":
            abort(404, "Can't found content: %s" % slpk)
        else:
            response = Response(
                content, mimetype='image/jpeg')
            response.headers['Content-Disposition'] = (
                'attachment; filename="0_0.jpg"'
            )
            return response


@app.route('/<slpk>/SceneServer/layers/<layer>/nodes/<node>/textures/0_0_1')
@app.route('/<slpk>/SceneServer/layers/<layer>/nodes/<node>/textures/0_0_1/')
def Ctextures_info(slpk, layer, node):
    """ Compressed texture information """
    if slpk not in slpks:  # Get 404 if slpk doesn't exists
        abort(404, "Can't found SLPK: %s" % slpk)
    try:
        return read("nodes/%s/textures/0_0_1.bin.dds.gz" % node, slpk)
    except Exception as e:
        return abort(404, "Can't found content: %s" % slpk)


@app.route('/<slpk>/SceneServer/layers/<layer>/nodes/<node>/features/0')
@app.route('/<slpk>/SceneServer/layers/<layer>/nodes/<node>/features/0/')
@stringify_response
def feature_info(slpk, layer, node):
    """ Feature information JSON """
    if slpk not in slpks:  # Get 404 if slpk doesn't exists
        abort(404, "Can't found SLPK: %s" % slpk)
    print("%s")
    FeatureData = json.loads(read("nodes/%s/features/0.json.gz" % node, slpk))
    response = HTTPResponse(FeatureData)
    return response


@app.route('/<slpk>/SceneServer/layers/<layer>/nodes/<node>/shared')
@app.route('/<slpk>/SceneServer/layers/<layer>/nodes/<node>/shared/')
@stringify_response
def shared_info(slpk, layer, node):
    """ Shared node information JSON """
    if slpk not in slpks:  # Get 404 if slpk doesn't exists
        abort(404, "Can't found SLPK: %s" % slpk)
    try:
        Sharedressource = json.loads(
            read("nodes/%s/shared/sharedResource.json.gz" % node, slpk))

        response = HTTPResponse(Sharedressource)
        return response
    except Exception as e:
        print(f"Error occurred: {e}")
        return ""


@app.route(
    '/<slpk>/SceneServer/layers/<layer>/nodes/<node>/attributes/<attribute>/0'
)
@app.route(
    '/<slpk>/SceneServer/layers/<layer>/nodes/<node>/attributes/<attribute>/0/'
)
def attribute_info(slpk, layer, node, attribute):
    """ Attribute information JSON """
    if slpk not in slpks:  # Get 404 if slpk doesn't exists
        abort(404, "Can't found SLPK: %s" % slpk)
    return read("nodes/%s/attributes/%s/0.bin.gz" % (node, attribute), slpk)


if __name__ == '__main__':
    # run() method of Flask class runs the application
    # on the local development
    # server.
    app.run(port=port)
