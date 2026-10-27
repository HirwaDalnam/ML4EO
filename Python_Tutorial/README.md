# Python for ML4EO: self-study tutorials

Self-study notebooks that teach the Python used in the ML4EO practicals. They are done in students' own time, not in class.

| Tutorial | Topic | Time | Status |
|---|---|---|---|
| T0 | Working in Jupyter and finding your files (Windows paths, 45 min)
| T1 | Python essentials: values, text, lists, dictionaries, `if`, loops, functions (60 min)
| T2 | NumPy: images as arrays (75 min)
| T3 | Reading satellite images with rasterio (60 min) 
| T4 | pandas: tables (75 min, to be provided later)
| T5 | Plotting with matplotlib (60 min, to be provided later)
| T6 | The scikit-learn workflow (60 min, to be provided later)


## Where to put the files

Copy the folder `Python_Tutorial` into your course folder, next to `data`:

```
ml4eo
├── data
├── L0_Data_ACcess
├── L1_Practical
└── …
├── Python_Tutorial      ← T0_Working_in_Jupyter.ipynb, …
└── …
```

**Data:** the tutorials use only the course files in `ml4eo/data` (Sentinel-2 GeoTIFFs and CSV tables); no extra files are needed.

**Software:** from T2 onwards the library `rasterio` is needed to read the GeoTIFF images. If `import rasterio` gives `ModuleNotFoundError`, open the Anaconda Prompt and type `conda activate ml4eo`, then `conda install -c conda-forge rasterio` (T2, 6.2).

Start Jupyter from the `ml4eo` folder (see Part 1 of T0). The tutorials read files from `../data`, exactly like the practicals.

## How to work

- Each notebook explains one small step at a time.
- Tasks are marked **▶ RUN** (run and read), **✎ CHANGE** (change a value and run again) and **✍ EXERCISE** (write a little code). A `check(...)` cell then prints ✓ or a hint.
- Some cells produce an error **on purpose** (marked in the cell). Read the message: learning to read errors is part of the tutorial.
- If something stops working: *Kernel → Restart Kernel and Run All Cells* (T0, Part 3).
- Model solutions will be shared later. Try every exercise yourself; when stuck, read the hint, look back at the earlier steps, or ask through email (preferably using class email).
