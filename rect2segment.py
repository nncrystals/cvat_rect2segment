import logging
import os

logging.basicConfig(level=logging.INFO)
import skimage.draw as skdraw
import scipy.spatial as ss
import argparse
import typing
import numpy as np
from xml.etree import ElementTree as ET

parser = argparse.ArgumentParser()

parser.add_argument("xml_file", type=argparse.FileType('r'))
parser.add_argument("output_file", type=str)
args = parser.parse_args()

tree: ET.ElementTree = ET.parse(args.xml_file)

images: typing.List[ET.Element] = tree.findall("image")
logging.info(f"Image count: {len(images)}")


def get_spaced_elements(array, numElems=4):
    out = array[np.round(np.linspace(0, len(array) - 1, numElems)).astype(int)]
    return out

def coordinate_string(rr,cc):
    if rr.shape != cc.shape:
        raise Exception("RR and CC shape not matching")

    out = ""
    for r, c in zip(rr, cc):
        out = out + f"{c},{r};"
    out = out[:-1]
    return out
for i, image in enumerate(images):
    logging.info(f"Processing image {i}")

    rects: typing.List[ET.Element] = image.findall("box")
    width = int(image.attrib["width"])
    height = int(image.attrib["height"])
    logging.info(f"Found {len(rects)} boxes")

    for j, rect in enumerate(rects):
        logging.info(f"Processing rect {j}")

        children = rect.getchildren()
        attrs: typing.Dict = rect.attrib

        xtl = float(attrs.pop("xtl"))
        ytl = float(attrs.pop("ytl"))
        xbr = float(attrs.pop("xbr"))
        ybr = float(attrs.pop("ybr"))
        xc = (xtl + xbr) / 2
        yc = (ytl + ybr) / 2
        xr = xbr - xtl
        yr = ybr - ytl
        rr, cc = skdraw.ellipse_perimeter(int(yc), int(xc), int(yr / 2), int(xr / 2), shape=(height, width))
        hull = ss.ConvexHull(np.array((rr,cc)).T)
        rr = rr[hull.vertices]
        cc = cc[hull.vertices]
        n = 10
        rr = get_spaced_elements(rr, n)
        cc = get_spaced_elements(cc, n)

        attrs["points"]=coordinate_string(rr,cc)
        image.remove(rect)
        subs:ET.Element = ET.SubElement(image, "polygon", attrs)
        subs.extend(children)

logging.info(f"Writing XML to {args.output_file}")
tree.write(args.output_file, "utf-8", short_empty_elements=False)