# Getting Started with the ML4EO Practicals

This guide assumes that **Anaconda or Miniconda, Python and Jupyter are already installed** on your computer. It takes about 15 minutes, and you only need to do it once.

## 1. Organise your files

Create one course folder called `ml4eo`. It holds the shared data loader, one shared `data/` folder with the satellite images, and one subfolder per practical:

```
ml4eo/
├── environment.yml
├── ml4eo_data.py              ← shared loader used by every practical
├── data/                      ← all images, shared by every practical
│   ├── 2026-01-21-00_00_2026-01-21-23_59_Sentinel-2_L2A_B02_(Raw).tiff
│   ├── ...                    (48 GeoTIFFs: 16 per date, for January, May and September 2026)
│   └── kigali_training_polygons.csv
├── L1_Practical/
│   ├── L1_Practical_Student.ipynb
│   └── check_environment.py
├── L2_Practical/
└── ...
```

Each notebook reads the images with `import sys; sys.path.append("..")` followed by `from ml4eo_data import load_scene`. This only works when the notebook sits in a subfolder of `ml4eo/`.

Tips:
- Avoid spaces and special characters in folder names (use `ml4eo`, not `ML 4 EO (final)`).
- Keep the original data files unchanged, **with their original names**: the loader reads the date and band from the file name. Save your own results under new names.

## 2. Create the course environment (once)

Open a terminal:
- **Windows:** use *Anaconda Prompt* from the Start menu.
- **macOS / Linux:** use *Terminal*.

Go to the course folder:

```
cd path/to/ml4eo
```

Create the environment from the file provided:

```
conda env create -f environment.yml
```

This installs Python 3.11 and every package used in the course. It can take 5–15 minutes.

If the environment `ml4eo` already exists and you only need to add packages, use:

```
conda env update -f environment.yml --prune
```

## 3. Start working (every session)

```
conda activate ml4eo
cd path/to/ml4eo/L1_Practical
jupyter lab
```

A browser tab opens:
1. Double-click `L1_Practical_Student.ipynb` to open it.
2. Check that the kernel shown at the top right is **Python 3 (ml4eo)**. If it is not, choose *Kernel → Change Kernel…* and select it.

If the `ml4eo` kernel does not appear in that list, run this once (with the environment active):

```
python -m ipykernel install --user --name ml4eo --display-name "Python 3 (ml4eo)"
```

## 4. Check that everything works

From the `L1_Practical` folder, with the environment active, run:

```
python check_environment.py
```

Every line should say `OK`. For Lecture 1 only numpy, pandas, matplotlib, scipy, scikit-learn and scikit-image are required. The geospatial packages (rasterio, geopandas, xarray and so on) are needed from Lecture 3.

To install anything missing:

```
conda install -n ml4eo -c conda-forge <package-name>
```

## 5. Notebook essentials

| Action | How |
|---|---|
| Run a cell and move on | Shift + Enter |
| Run a cell and stay on it | Ctrl + Enter |
| New cell below / above | B / A (in command mode: press Esc first) |
| Turn a cell into Markdown / code | M / Y (command mode) |
| Delete a cell | D, D (command mode) |
| Save | Ctrl + S |
| Start again cleanly | *Kernel → Restart Kernel and Run All Cells…* |
| Stop a cell that runs too long | *Kernel → Interrupt* (■ button) |

Cells run in the order **you** execute them, not in the order they appear on the page. If a variable is "not defined", run the cells above it first.

## 6. Common problems

| Message / symptom | Cause and fix |
|---|---|
| `ModuleNotFoundError: No module named 'sklearn'` | Wrong kernel or missing package. Check the kernel name (step 3), or install with `conda install -n ml4eo -c conda-forge scikit-learn` |
| `ModuleNotFoundError: ml4eo_data` or `FileNotFoundError: Could not find the ml4eo/data folder` | The notebook is not in a subfolder of `ml4eo/`, or `ml4eo_data.py` / `data/` is missing. Run `import os; os.getcwd()` to see where you are. If the data must live elsewhere, run `import ml4eo_data; ml4eo_data.DATA_DIR = "/path/to/data"` |
| `conda: command not found` (macOS/Linux) | Open a new terminal, or run `conda init` once and restart the terminal |
| `conda activate` fails in Windows PowerShell | Use *Anaconda Prompt*, or run `conda init powershell` once |
| Kernel dies / "out of memory" | Close other notebooks (*Kernel → Shut Down Kernel*). The Kigali data need about 2 GB of RAM |
| Figures do not appear | Run the cell again. In old Jupyter versions, add `%matplotlib inline` in the first cell |

## 7. Working habits for all practicals

- **Run from top to bottom.** Before you submit, choose *Restart Kernel and Run All Cells* to make sure the notebook runs cleanly.
- **Complete the TODOs.** Fill in the cells marked `# TODO` by replacing `...`. Write your answers in the *Your answer* boxes.
- **Keep your answers.** Save a copy of the notebook with your name, e.g. `L1_Practical_Student_Uwimana.ipynb`.
- **Record your data.** Note the product, date, level and processing of every dataset you use.
