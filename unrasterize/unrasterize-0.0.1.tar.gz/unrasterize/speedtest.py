"""Tests for speed."""
import rasterio

from unrasterize import classes


def main():
    """Test speed."""
    raster_path = 'data/Rwanda/raster/RWA_ppp_v2b_2015_UNadj.tif'
    raster_data = rasterio.open(raster_path)
    n = classes.WindowedUnrasterizer(mask_width=25)
    n.select_representative_pixels(raster_data)


if __name__ == '__main__':
    main()
