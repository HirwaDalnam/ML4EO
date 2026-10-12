"""Quick check of the course environment. Run:  python check_environment.py"""
import importlib, sys, os
print("Python", sys.version.split()[0], "at", sys.executable)
need = {"numpy": "numpy", "pandas": "pandas", "matplotlib": "matplotlib", "scipy": "scipy",
        "sklearn": "scikit-learn", "skimage": "scikit-image", "rasterio": "rasterio", "geopandas": "geopandas",
        "shapely": "shapely", "pyproj": "pyproj", "xarray": "xarray", "rioxarray": "rioxarray", "jupyterlab": "jupyterlab"}
missing = []
for mod, pkg in need.items():
    try:
        m = importlib.import_module(mod); print(f"  OK       {pkg:14s} {getattr(m, '__version__', '')}")
    except ImportError:
        print(f"  MISSING  {pkg}"); missing.append(pkg)
if missing:
    print("\nInstall the missing packages with:\n  conda install -n ml4eo -c conda-forge " + " ".join(missing))
    print("(Lecture 1 needs numpy, pandas, matplotlib, scipy, scikit-learn, scikit-image and rasterio.)")
else:
    print("\nAll packages found. You are ready.")

# course data: the images in ml4eo/data (this script sits in ml4eo/L1_Practical)
data = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data") if os.path.isdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data")) else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
if os.path.isdir(data):
    tiffs = [f for f in os.listdir(data) if f.endswith(".tiff")]
    print(f"\n  OK       data folder with {len(tiffs)} image files (expect 48)")
    for date in ["2026-01-21", "2026-05-13", "2026-09-03"]:
        print(f"           {date}: {sum(f.startswith(date) for f in tiffs)} files")      # expect 16 per date
    csv = os.path.join(data, "kigali_training_polygons.csv")
    print(("  OK       " if os.path.exists(csv) else "  MISSING  ") + "kigali_training_polygons.csv")
else:
    print("\n  MISSING  data folder:", os.path.abspath(data))
