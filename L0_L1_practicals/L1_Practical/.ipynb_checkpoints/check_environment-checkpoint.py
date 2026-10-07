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
    print("(Lecture 1 needs only numpy, pandas, matplotlib, scipy, scikit-learn, scikit-image.)")
else:
    print("\nAll packages found. You are ready.")

# course data: ml4eo/data, read with ml4eo/ml4eo_data.py (run this script from ml4eo/L1_Practical)
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
try:
    import ml4eo_data as ml
    files = ml.list_files()
    print(f"\n  OK       data folder {ml.DATA_DIR}")
    for date, n in files.groupby("date").size().items():
        print(f"           {date}: {n} files")           # expect 16 per date
    csv = ml.DATA_DIR / "kigali_training_polygons.csv"
    print(("  OK       " if csv.exists() else "  MISSING  ") + csv.name)
except (ImportError, FileNotFoundError) as e:
    print("\n  MISSING  course data:", e)
