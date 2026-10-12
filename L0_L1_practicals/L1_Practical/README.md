# Lecture 1 Guided Practical: Getting Started and Exploring Kigali Sentinel-2 Data

**Course:** Machine Learning for Earth Observation (Year 3)
**Duration:** 45–60 min; students work in pairs
**Data:** Sentinel-2 L2A over Kigali, on three dates: 21 January, 13 May and 3 September 2026. All three were exported from Copernicus Browser with the same box and settings: one 20 m grid (2380 × 1702 pixels, 47.5 × 34.0 km) in UTM zone 36S (EPSG:32736).

## Contents

| File | Purpose |
|---|---|
| `GETTING_STARTED.md` | For students: folder set-up, creating and activating the `ml4eo` conda environment, starting Jupyter, notebook shortcuts, troubleshooting |
| `../environment.yml` | The course environment, with every package for Lectures 1–10 (GEE packages commented out until Lecture 10) |
| `check_environment.py` | Checks the packages and data files from the terminal |
| `L1_Practical_Student.ipynb` | Student notebook: Part 0 (getting started), Steps 1–7, 8 `# TODO` cells and answer boxes |
| `L1_Practical_Solutions.ipynb` | Lecturer version, fully executed, with outputs and model answers |
| `../ml4eo_data.py` | Shared loader, used by all practicals. It reads the GeoTIFFs (all on one grid), decodes the SCL and treats 0 as no data |
| `../data/*.tiff` | The 48 Copernicus Browser exports: for each date, 12 bands plus NDVI, NDWI, SCL and True_color pictures. Not in this pack; they are the images already in `ml4eo/data/` |
| `../data/kigali_training_polygons.csv` | The 1,225 labelled polygon pixels (49 polygons, 5 classes): row/col on the 20 m grid, UTM x/y, lon/lat, and a 5 km block id for spatial cross-validation |

**Set-up:** unzip the pack so that `L1_Practical/`, `ml4eo_data.py` and `data/kigali_training_polygons.csv` sit inside `ml4eo/`, next to the GeoTIFFs in `ml4eo/data/`.

## Requirements

The `ml4eo` environment, or any Python ≥ 3.9 with numpy, pandas, matplotlib, scipy, scikit-learn and scikit-image. A full run takes about 15 seconds and needs about 2 GB of RAM.

## Structure and expected checkpoints

| Part | Content | TODO | Expected result |
|---|---|---|---|
| 0 | How notebooks work; environment and data check; NumPy warm-up | `np.full` | All lines `OK`; 16 files per date; `(3, 4) 1.2` |
| 1 | List the GeoTIFFs; B04, B05 and B01 share one grid; zoom shows 10 / 20 / 60 m detail; load as DN; convert to reflectance | reflectance conversion | (12, 1702, 2380) `uint16`, 97 MB; DN 45–16,250 on valid pixels; 192,972 no-data values (the 0.4% edge frame × 12 bands); 19.98 × 19.96 m; 47.5 × 34.0 km; EPSG:32736; 13 values > 1 |
| 2 | True- and false-colour composites | false-colour band order | Vegetation appears red in false colour |
| 3 | Class spectra from the 1,225 polygon pixels | groupby mean / SD | Water ≈0.03–0.04 in NIR/SWIR; bare soil vs built-up overlap |
| 4 | Aggregate to 100 m / 300 m / 1 km; purity from the SCL | block mean | ≥ 90% one class: 61.3 / 46.5 / 30.3%; strongly mixed 7.4 / 10.5 / 12.0%; water 2.35% → 1.9% of 1 km pixels |
| 5 | Re-quantise to 8/10/12 bits | quantisation | 38 distinct red values over water at 8 bits (1,012 originally); NDVI RMSE over water 0.031 / 0.0075 / 0.0019 |
| 6 | Three dates, SCL shares, validity masks | SCL mask | January: 3.95% medium + 0.27% high cloud, 2.36% cirrus, 0.21% shadow. Valid: 92.0 / 99.2 / 98.6%; 91.1% valid on all three dates. Median NDVI 0.61 / 0.67 / 0.32 |
| 7 | Sample table (x, y); saved as `kigali_samples_L1.csv` | band extraction | 1,225 × 13 table. Label vs SCL: dense vegetation 300 / 0; sparse vegetation 124 / 101; 25 water pixels are SCL "unclassified" |

**Differences from the Lecture 1 slides.** The slides were made with the earlier ≈33 m exports in geographic coordinates. The numbers above come from the 20 m UTM exports, so they differ from the slides: for example the grid and pixel size, the purity percentages, and the January cloud (the January export now covers the whole area, including the cloud bank in the south-west). The class spectra and the label-vs-SCL table are almost unchanged.

## Suggested running order

1. **Part 0 (10 min).** Do it together, on the projector. Make sure everyone has the right kernel before moving on. This is the most common problem in week 1.
2. **Steps 1–3 (18 min).**
3. **Steps 4–5 (10 min).**
4. **Steps 6–7 (11 min).**
5. **Reflection:** homework.

The Lecture 1 deck lists five key questions; the notebook has seven. Questions 1 and 3–6 correspond to the slide questions.

## Caveats

- **Labels.** The class labels were produced from the September image itself (Lecture 3). Lecture 4 discusses why that matters.
- **One 20 m grid.** Every band was resampled to 20 m at export: the 10 m bands lost detail and the 60 m bands were interpolated. This is shown in Step 1 and discussed in Question 1.
- **Damaged pictures.** The January and September `True_color.tiff` files are truncated (Copernicus Browser export). The notebooks do not use them; true colour is built from the bands.
