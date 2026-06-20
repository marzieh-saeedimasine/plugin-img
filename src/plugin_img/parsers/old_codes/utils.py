import math

import matplotlib.pyplot as plt
import numpy as np


def read_envi_hdr(path):
    """
    Read an ENVI .hdr file into a dictionary.
    """
    metadata = {}

    with open(path) as f:
        lines = f.readlines()

    key = None
    collecting = False
    buffer = []

    for line in lines:
        line = line.strip()

        if not line or line.upper() == "ENVI":
            continue

        if collecting:
            buffer.append(line)
            if "}" in line:
                metadata[key] = " ".join(buffer)
                collecting = False
                buffer = []
            continue

        if "=" in line:
            k, v = map(str.strip, line.split("=", 1))

            if v.startswith("{") and not v.endswith("}"):
                key = k.lower()
                collecting = True
                buffer.append(v)
            else:
                metadata[k.lower()] = v

    return metadata

def read_bil(path, lines, samples, bands, dtype=np.float32):
    """
    Read a BIL hyperspectral file into a NumPy array.


    Returns array of shape:
    (lines, samples, bands)
    """
    data = np.fromfile(path, dtype=dtype)


    expected = lines * samples * bands
    if data.size != expected:
        raise ValueError(f"Size mismatch: expected {expected}, got {data.size}")


    # BIL order: (lines, bands, samples)
    data = data.reshape(lines, bands, samples)


    # Reorder to (lines, samples, bands)
    data = np.transpose(data, (0, 2, 1))


    return data

def plot_wavelength_images(
    cube,
    wavelengths,
    wavelength_list,
    cmap="gray",
    normalize=True,
    max_cols=3,
    figsize_per_plot=(4, 4)
):
    """
    Plot spatial images at selected wavelengths in a clean grid.

    Parameters
    ----------
    cube : ndarray (lines, samples, bands)
    wavelengths : ndarray (bands,)
    wavelength_list : list of float
        Wavelengths (nm) to visualize
    cmap : str
        Matplotlib colormap
    normalize : bool
        Normalize each image independently
    max_cols : int
        Maximum number of columns in the grid
    figsize_per_plot : tuple
        Size per subplot
    """

    n = len(wavelength_list)
    cols = min(max_cols, n)
    rows = math.ceil(n / cols)

    fig, axes = plt.subplots(
        rows,
        cols,
        figsize=(figsize_per_plot[0] * cols,
                 figsize_per_plot[1] * rows),
        squeeze=False
    )

    for ax in axes.flat:
        ax.axis("off")

    for i, wl in enumerate(wavelength_list):
        r = i // cols
        c = i % cols

        band = band_near(wl, wavelengths)
        img = cube[:, :, band].astype(float)

        if normalize:
            img /= img.max() + 1e-9

        im = axes[r, c].imshow(img, cmap=cmap)
        axes[r, c].set_title(f"{wavelengths[band]:.1f} nm")

        fig.colorbar(im, ax=axes[r, c], fraction=0.046)

    plt.tight_layout()
    plt.show()

import numpy as np


def grid_slices(lines, samples, n_rows, n_cols):
    """
    Generate (row_slice, col_slice) for each grid cell.
    """
    row_edges = np.linspace(0, lines, n_rows + 1, dtype=int)
    col_edges = np.linspace(0, samples, n_cols + 1, dtype=int)

    slices = []
    for i in range(n_rows):
        for j in range(n_cols):
            rs = slice(row_edges[i], row_edges[i + 1])
            cs = slice(col_edges[j], col_edges[j + 1])
            slices.append((rs, cs))

    return slices



def plot_grid_mean_spectra(
    cube,
    wavelengths,
    n_rows=2,
    n_cols=2,
    image_band=None,
    normalize_spectra=False,
    cmap="gray"
):
    """
    Plot spatial grid overlay and mean spectra per grid cell.
    """

    lines, samples, bands = cube.shape

    # Choose band for background image
    if image_band is None:
        image = cube.mean(axis=2)
        image_title = "Mean intensity image"
    else:
        image = cube[:, :, image_band]
        image_title = f"Band {image_band} ({wavelengths[image_band]:.1f} nm)"

    grid = grid_slices(lines, samples, n_rows, n_cols)

    fig, (ax_img, ax_spec) = plt.subplots(
        1, 2, figsize=(12, 5), gridspec_kw={"width_ratios": [1, 1.2]}
    )

    # ---- Image with grid ----
    ax_img.imshow(image, cmap=cmap)
    ax_img.set_title(image_title)
    ax_img.set_xlabel("Samples")
    ax_img.set_ylabel("Lines")

    # Draw grid lines
    for r in np.linspace(0, lines, n_rows + 1):
        ax_img.axhline(r, color="cyan", lw=1)
    for c in np.linspace(0, samples, n_cols + 1):
        ax_img.axvline(c, color="cyan", lw=1)

    # ---- Mean spectra ----
    for idx, (rs, cs) in enumerate(grid):
        spectrum = cube[rs, cs, :].mean(axis=(0, 1))

        if normalize_spectra:
            spectrum /= spectrum.max() + 1e-9

        ax_spec.plot(
            wavelengths,
            spectrum,
            label=f"Cell {idx + 1}"
        )
        # ---- Add grid cell numbers ----
    cell_idx = 1
    row_edges = np.linspace(0, lines, n_rows + 1)
    col_edges = np.linspace(0, samples, n_cols + 1)

    for i in range(n_rows):
        for j in range(n_cols):
            y_center = 0.5 * (row_edges[i] + row_edges[i + 1])
            x_center = 0.5 * (col_edges[j] + col_edges[j + 1])

            ax_img.text(
                x_center,
                y_center,
                str(cell_idx),
                color="yellow",
                fontsize=12,
                fontweight="bold",
                ha="center",
                va="center",
                bbox=dict(facecolor="black", alpha=0.4, edgecolor="none")
            )

            cell_idx += 1
    ax_spec.set_xlabel("Wavelength (nm)")
    ax_spec.set_ylabel("Normalized intensity" if normalize_spectra else "Intensity")
    ax_spec.set_title(f"Mean spectra ({n_rows} × {n_cols} grid)")
    ax_spec.grid(True)
    ax_spec.legend(fontsize=8, ncol=2)

    plt.tight_layout()
    plt.show()

class HyperspectralCube:
    def __init__(self, data, wavelengths, metadata=None):
        self.data = data
        self.wavelengths = wavelengths
        self.metadata = metadata or {}

    def band(self, wl):
        idx = int((abs(self.wavelengths - wl)).argmin())
        return self.data[:, :, idx]

    def spectrum(self, x, y):
        return self.data[x, y, :]

    def mean_spectrum(self, roi=None):
        if roi is None:
            return self.data.mean(axis=(0, 1))
        x1, x2, y1, y2 = roi
        return self.data[x1:x2, y1:y2, :].mean(axis=(0, 1))

hdr = read_envi_hdr("cube1.bil.hdr")

ENVI_DTYPE_MAP = {
    "12": np.uint16,
    "4": np.float32,
    "5": np.float64,
    "2": np.int16,
}

dtype = ENVI_DTYPE_MAP[hdr["data type"]]

wavelengths = hdr["wavelength"]
wavelengths = wavelengths.strip("{}")
wavelengths = np.array(
    [float(w) for w in wavelengths.split(",")]
)

#print(wavelengths.shape)

print("=== Cube summary ===")
print("Lines     :", hdr["lines"])
print("Samples   :", hdr["samples"])
print("Bands     :", hdr["bands"])
print("Interleave:", hdr["interleave"])
print("Data type :", hdr["data type"])
print("Gain      :", hdr.get("gain"))
print("Shutter   :", hdr.get("shutter"))
print("Framerate :", hdr.get("framerate"))
print("Camera    :", hdr.get("imager serial number"))
print("λ range   :", wavelengths[0], "→", wavelengths[-1], "nm")



bil_path = "cube1.bil"


lines = int(hdr["lines"])
samples = int(hdr["samples"])
bands = int(hdr["bands"])


cube = read_bil(
bil_path,
lines=lines,
samples=samples,
bands=bands,
dtype=dtype
)


print(cube.shape) # (lines, samples, bands)



#def band_near(wavelength_nm):
#    return int((abs(wavelengths - wavelength_nm)).argmin())
def band_near(wavelength_nm, wavelengths):
    return int((abs(wavelengths - wavelength_nm)).argmin())

r = band_near(650, wavelengths)
g = band_near(550, wavelengths)
b = band_near(450, wavelengths)

rgb = np.stack([
    cube[:, :, r],
    cube[:, :, g],
    cube[:, :, b]
], axis=-1)

# normalize for display
rgb = rgb.astype(float)
rgb /= rgb.max()

plt.figure(figsize=(6, 4))
plt.imshow(rgb)
plt.title("RGB quicklook")
plt.axis("off")
plt.tight_layout()
plt.show()

x, y = 400, 450  # pick a point

spectrum = cube[x, y, :]

plt.figure(figsize=(6, 4))
plt.plot(wavelengths, spectrum)
plt.xlabel("Wavelength (nm)")
plt.ylabel("Intensity")
plt.title("Pixel spectrum")
plt.grid(True)
plt.tight_layout()
plt.show()

roi = cube[350:450, 400:500, :]
mean_spectrum = roi.mean(axis=(0, 1))

plt.figure(figsize=(6, 4))
plt.plot(wavelengths, mean_spectrum)
plt.xlabel("Wavelength (nm)")
plt.ylabel("Mean intensity")
plt.title("ROI-averaged spectrum")
plt.grid(True)
plt.tight_layout()
plt.show()

norm_spectrum = mean_spectrum / mean_spectrum.max()

plt.plot(wavelengths, norm_spectrum)
plt.xlabel("Wavelength (nm)")
plt.ylabel("Normalized intensity")
plt.title("Normalized spectrum")
plt.grid(True)
plt.show()

b1 = band_near(700, wavelengths)
b2 = band_near(500, wavelengths)

ratio = cube[:, :, b1] / (cube[:, :, b2] + 1e-6)

plt.imshow(ratio, cmap="inferno")
plt.colorbar(label="Band ratio")
plt.title(f"{wavelengths[b1]:.0f} nm / {wavelengths[b2]:.0f} nm")
plt.show()

mean_image = cube.mean(axis=2)

plt.imshow(mean_image, cmap="gray")
plt.colorbar(label="Mean intensity")
plt.title("Mean intensity across spectrum")
plt.show()

line_idx = 400
profile = mean_image[line_idx, :]

plt.plot(profile)
plt.xlabel("Sample index")
plt.ylabel("Mean intensity")
plt.title("Line profile across film")
plt.grid(True)
plt.show()

plot_wavelength_images(
    cube,
    wavelengths,
    wavelength_list=[350,450, 550, 650, 750, 850, 950, 1050],
    max_cols=3
)

plot_grid_mean_spectra(
    cube,
    wavelengths,
    n_rows=2,
    n_cols=2
)

plot_grid_mean_spectra(
    cube,
    wavelengths,
    n_rows=3,
    n_cols=3
)

plot_grid_mean_spectra(
    cube,
    wavelengths,
    n_rows=8,
    n_cols=8,
    #image_band=band_near(600, wavelengths)
)

