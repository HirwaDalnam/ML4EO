"""
ml4eo_data.py - one shared way to read the course's Sentinel-2 images
======================================================================
Machine Learning for Earth Observation (Year 3) - all practicals.

Folder layout:

    ml4eo/
    |-- ml4eo_data.py                 <- this file
    |-- data/                         <- Copernicus Browser GeoTIFF exports + training pixels
    |   |-- 2026-09-03-00_00_2026-09-03-23_59_Sentinel-2_L2A_B04_(Raw).tiff
    |   |-- ...
    |   `-- kigali_training_polygons.csv
    |-- L1_Practical/
    `-- ...

In a practical notebook:

    import sys; sys.path.append("..")          # ml4eo_data.py is one folder up
    from ml4eo_data import load_scene, valid_mask, add_indices

    sep = load_scene("sep")          # dict: "B01" ... "B12" (reflectance, NaN = no data) + "SCL" (codes 0-11)

The data
--------
Sentinel-2 L2A over Kigali for 21 Jan, 13 May and 3 Sept 2026, exported from
Copernicus Browser with the same box and settings: 2380 x 1702 pixels of 20 m,
UTM zone 36S (EPSG:32736). Every file of every date is on this one grid, so a
pixel (row, col) is the same place on the ground in every band and on every date.

* Bands are surface reflectance (0-1). A value of 0 means "no data" (a thin
  frame around the image edge); the loader turns it into NaN.
* The SCL is exported as a coloured picture; the loader turns it back into codes 0-11.
* NDVI, NDWI and True_color files are coloured pictures, not values: compute
  indices from the bands with add_indices() instead.
"""
from __future__ import annotations

import os
import re
from pathlib import Path

import numpy as np

try:                                    # preferred reader (in the course environment)
    import rasterio
    _HAVE_RASTERIO = True
except ImportError:                     # fallback: pure-python reader
    _HAVE_RASTERIO = False
import tifffile                         # always available (installed with scikit-image)

__all__ = ["DATA_DIR", "S2_BANDS", "DATES", "SCL_NAMES", "SCL_PALETTE",
           "list_files", "read_tif", "grid", "load_scene", "as_stack", "valid_mask",
           "add_indices", "load_polygons", "pixel_table", "spatial_blocks",
           "extent", "scl_cmap", "save_geotiff"]

S2_BANDS = ["B01", "B02", "B03", "B04", "B05", "B06", "B07", "B08", "B8A", "B09", "B11", "B12"]
DATES = {"jan": "2026-01-21", "may": "2026-05-13", "sep": "2026-09-03"}

# Copernicus Browser SCL colours -> (code, name)
SCL_PALETTE = {(0, 0, 0): (0, "No data"), (255, 0, 0): (1, "Saturated / defective"),
               (47, 47, 47): (2, "Dark area pixels"), (100, 50, 0): (3, "Cloud shadows"),
               (0, 160, 0): (4, "Vegetation"), (255, 230, 90): (5, "Not vegetated"),
               (0, 0, 255): (6, "Water"), (128, 128, 128): (7, "Unclassified"),
               (192, 192, 192): (8, "Cloud (medium prob.)"), (255, 255, 255): (9, "Cloud (high prob.)"),
               (100, 200, 255): (10, "Thin cirrus"), (255, 150, 255): (11, "Snow / ice")}
SCL_NAMES = {code: name for code, name in SCL_PALETTE.values()}


# ----------------------------------------------------------------------------
# Finding the files
# ----------------------------------------------------------------------------
def _find_data_dir():
    env = os.environ.get("ML4EO_DATA")
    if env and Path(env).is_dir():
        return Path(env)
    here = Path.cwd().resolve()
    for p in [here, *here.parents]:
        for c in (p / "data", p / "ml4eo" / "data"):
            if c.is_dir() and any(c.glob("*Sentinel-2_L2A*.tif*")):
                return c
    c = Path(__file__).resolve().parent / "data"
    return c if c.is_dir() else None


DATA_DIR = _find_data_dir()        # can be set by hand: ml4eo_data.DATA_DIR = "/path/to/data"


def _data_dir():
    if DATA_DIR is None:
        raise FileNotFoundError(
            "Could not find the ml4eo/data folder with the Sentinel-2 .tiff files. Open the notebook "
            "from inside the ml4eo folder, or set it by hand:\n"
            "    import ml4eo_data; ml4eo_data.DATA_DIR = '/path/to/ml4eo/data'")
    return Path(DATA_DIR)


_NAME = re.compile(r"(?P<date>\d{4}-\d{2}-\d{2})-00_00_.*Sentinel-2_L2A_(?P<layer>.+?)\.tiff?$")


def _layer(raw):
    raw = raw.replace("_(Raw)", "")
    return "SCL" if raw.startswith("Scene_classification") else raw.strip("_")


def list_files():
    """Table of the image files: date, layer, file name."""
    import pandas as pd
    rows = [{"date": m["date"], "layer": _layer(m["layer"]), "file": f.name}
            for f in sorted(_data_dir().glob("*.tif*")) if (m := _NAME.search(f.name))]
    return pd.DataFrame(rows)


def _path(date, layer):
    for f in _data_dir().glob(f"{date}-*.tif*"):
        m = _NAME.search(f.name)
        if m and _layer(m["layer"]) == layer:
            return f
    raise FileNotFoundError(f"No {layer} file for {date} in {_data_dir()}")


# ----------------------------------------------------------------------------
# Reading
# ----------------------------------------------------------------------------
def read_tif(path):
    """Read one GeoTIFF -> (array, grid).
    array: (rows, cols) for a band, (rows, cols, 3) for a coloured picture (SCL, NDVI, ...).
    grid : dict(ulx, uly, dx, dy, h, w, crs); ulx/uly = upper-left corner, dx/dy = pixel size (m)."""
    if _HAVE_RASTERIO:
        with rasterio.open(path) as src:
            a, t = src.read(), src.transform
            g = dict(ulx=t.c, uly=t.f, dx=t.a, dy=-t.e, h=src.height, w=src.width, crs=str(src.crs))
        return (a[0] if a.shape[0] == 1 else np.moveaxis(a, 0, -1)), g
    with tifffile.TiffFile(path) as t:
        p = t.pages[0]
        tags = {k.name: k.value for k in p.tags.values()}
        geo = t.geotiff_metadata or {}
        epsg = geo.get("ProjectedCSTypeGeoKey", geo.get("GeographicTypeGeoKey"))
        a = p.asarray()
        return a, dict(ulx=tags["ModelTiepointTag"][3], uly=tags["ModelTiepointTag"][4],
                       dx=tags["ModelPixelScaleTag"][0], dy=tags["ModelPixelScaleTag"][1],
                       h=a.shape[0], w=a.shape[1], crs=f"EPSG:{int(getattr(epsg, 'value', epsg))}")


def decode_scl(rgb):
    """Coloured SCL picture (0-1 or 0-255) -> uint8 codes 0-11. Unknown colours -> 0 (no data)."""
    key = np.round(rgb * 255 if rgb.max() <= 1.0 else rgb).astype(int)
    out = np.zeros(rgb.shape[:2], np.uint8)
    for colour, (code, _) in SCL_PALETTE.items():
        out[np.all(key == colour, axis=-1)] = code
    return out


def grid(date="sep"):
    """The pixel grid: dict(ulx, uly, dx, dy, h, w, crs). The same for all dates."""
    return read_tif(_path(DATES.get(date, date), "SCL"))[1]


def load_scene(date="sep", bands=None, scale="reflectance"):
    """Load one date: {"B01": 2-D array, ..., "SCL": 2-D codes}.

    date  : "jan", "may", "sep" (or "2026-01-21", "2026-05-13", "2026-09-03")
    bands : e.g. ["B02", "B03", "B04", "B08"]; default: all 12 bands
    scale : "reflectance" -> float32 0-1, NaN = no data
            "dn"          -> uint16 digital numbers = reflectance x 10000, 0 = no data
    """
    date = DATES.get(date, date)
    scene, ref = {}, None
    for b in (bands or S2_BANDS):
        a, g = read_tif(_path(date, b))
        if ref is None:
            ref = g
        elif (g["h"], g["w"]) != (ref["h"], ref["w"]) or not np.allclose(
                [g["ulx"], g["uly"], g["dx"], g["dy"]], [ref["ulx"], ref["uly"], ref["dx"], ref["dy"]]):
            raise ValueError(f"{b} of {date} is not on the same grid as the other bands; re-export it "
                             "with the same box, resolution and projection.")
        if scale == "dn":
            scene[b] = np.clip(np.round(a * 10000), 0, 65535).astype(np.uint16)   # 0 stays 0 = no data
        else:
            a = a.astype("float32")
            a[a == 0] = np.nan
            scene[b] = a
    scene["SCL"] = decode_scl(read_tif(_path(date, "SCL"))[0])
    return scene


def as_stack(scene, bands=None):
    """dict of 2-D bands -> 3-D array (n_bands, rows, cols)."""
    return np.stack([scene[b] for b in (bands or [k for k in scene if k != "SCL"])])


# ----------------------------------------------------------------------------
# Helpers used in the practicals
# ----------------------------------------------------------------------------
def valid_mask(scene, codes=(4, 5, 6)):
    """True where the SCL is vegetation (4), not vegetated (5) or water (6) and every band has data."""
    scl = scene["SCL"] if isinstance(scene, dict) else scene
    m = np.isin(scl, codes)
    if isinstance(scene, dict):
        for k, v in scene.items():
            if k != "SCL":
                m &= np.isfinite(v) if v.dtype.kind == "f" else v > 0
    return m


def add_indices(scene, which=("NDVI", "NDWI", "MNDWI", "NDBI")):
    """Add normalised-difference indices to the scene dict (in place) and return it."""
    formulas = {"NDVI": ("B08", "B04"), "NDWI": ("B03", "B08"), "MNDWI": ("B03", "B11"),
                "NDBI": ("B11", "B08"), "NDRE": ("B8A", "B05")}
    for name in which:
        a, b = (scene[x].astype("float32") for x in formulas[name])
        with np.errstate(divide="ignore", invalid="ignore"):
            scene[name] = (a - b) / (a + b)
    return scene


def load_polygons():
    """The 1,225 labelled pixels: class, polygon (group_id), row/col, x/y (UTM), lon/lat, block_id."""
    import pandas as pd
    return pd.read_csv(_data_dir() / "kigali_training_polygons.csv")


def pixel_table(scene, table, layers=None):
    """Copy of `table` with the value of each layer at its row/col added as columns."""
    out = table.copy()
    r, c = table["row"].to_numpy(), table["col"].to_numpy()
    for k in (layers or [k for k in scene if k != "SCL"]):
        out[k] = scene[k][r, c]
    return out


def spatial_blocks(size_m=5000, g=None):
    """2-D array giving every pixel the id of its size_m x size_m block (for spatial cross-validation).
    Same numbering as block_id in kigali_training_polygons.csv (5 km)."""
    g = g or grid()
    rows = (np.arange(g["h"]) * g["dy"] // size_m).astype(int)
    cols = (np.arange(g["w"]) * g["dx"] // size_m).astype(int)
    return cols[None, :] * 100 + rows[:, None]


def extent(g=None, km=True):
    """[left, right, bottom, top] for plt.imshow(..., extent=extent()); UTM 36S, in km by default."""
    g = g or grid()
    e = [g["ulx"], g["ulx"] + g["w"] * g["dx"], g["uly"] - g["h"] * g["dy"], g["uly"]]
    return [v / 1000 for v in e] if km else e


def scl_cmap():
    """(cmap, norm) that draw SCL codes in their standard colours."""
    from matplotlib.colors import BoundaryNorm, ListedColormap
    colours = [np.array(c) / 255 for c, _ in sorted(SCL_PALETTE.items(), key=lambda kv: kv[1][0])]
    return ListedColormap(colours), BoundaryNorm(np.arange(-0.5, 12), 12)


def save_geotiff(array, path, g=None, nodata=None):
    """Write a 2-D map on the course grid (e.g. a classification) as a GeoTIFF for QGIS."""
    g = g or grid()
    array = np.asarray(array)
    epsg = int(g["crs"].split(":")[-1])
    if _HAVE_RASTERIO:
        from rasterio.transform import from_origin
        with rasterio.open(path, "w", driver="GTiff", height=g["h"], width=g["w"], count=1,
                           dtype=array.dtype.name, crs=g["crs"], nodata=nodata, compress="deflate",
                           transform=from_origin(g["ulx"], g["uly"], g["dx"], g["dy"])) as dst:
            dst.write(array, 1)
        return path
    geokeys = (1, 1, 0, 3, 1024, 0, 1, 1, 1025, 0, 1, 1, 3072, 0, 1, epsg)   # projected, pixel-is-area, EPSG
    tags = [(33550, "d", 3, (g["dx"], g["dy"], 0.0), True),
            (33922, "d", 6, (0.0, 0.0, 0.0, g["ulx"], g["uly"], 0.0), True),
            (34735, "H", len(geokeys), geokeys, True)]
    if nodata is not None:
        tags.append((42113, "s", 0, str(nodata), True))
    tifffile.imwrite(path, array, extratags=tags, compression="zlib")
    return path


if __name__ == "__main__":        # quick self-check: python ml4eo_data.py
    print("Data folder:", _data_dir(), "| reader:", "rasterio" if _HAVE_RASTERIO else "tifffile")
    for date, grp in list_files().groupby("date"):
        print(f"  {date}: {len(grp)} files")
    g = grid()
    print(f"Grid: {g['w']} x {g['h']} pixels of {g['dx']:.2f} x {g['dy']:.2f} m, {g['crs']}")
    s = load_scene("sep")
    print("Sept valid pixels:", int(valid_mask(s).sum()))
