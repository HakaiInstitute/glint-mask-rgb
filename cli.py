# Created by: Taylor Denouden
# Organization: Hakai Institute
# Date: 2020-05-30
# Description: Command line interface to the glint-mask-tools.

# Based on Matlab script by Tom Bell written 6/28/2019
#
# Description: Generate masks for glint regions in in RGB images using Tom Bell's blue-channel binning algorithm.
import sys
from typing import Optional

import fire
from tqdm import tqdm

from core.bin_maskers import BlueBinMasker, MicasenseRedEdgeMasker, DJIMultispectralMasker
from core.specular_maskers import RGBSpecularMasker


def _err_callback(path, exception):
    tqdm.write(f"{path} failed with err:\n{exception}", file=sys.stderr)


def dji_ms(img_path: str, mask_out_path: str, glint_threshold: float = 0.9, mask_buffer_sigma: int = 0,
           num_bins: int = 8, max_workers: Optional[int] = None) -> None:
    """Generate masks for glint regions in multispectral imagery from the DJI camera using Tom Bell's algorithm.

    Parameters
    ----------
    img_path: str
        The path to a named input image or directory containing images. If img_path is a directory, all DJI_***4.TIF
        files will be processed.

    mask_out_path: str
        The path to send your out image including the file name and type. e.g. "/path/to/mask.png".
        mask_out_path must be a directory if img_path is specified as a directory.

    glint_threshold: Optional[float]
        The amount of binned "blueness" that should be glint. Domain for values is (0.0, 1.0).
        Play with this value. Default is 0.9.

    mask_buffer_sigma: Optional[int]
        The sigma for the Gaussian kernel used to buffer the mask. Defaults to 0.

    num_bins: Optional[int]
        The number of bins the blue channel is slotted into. Defaults to 8 as in Tom's script.

    max_workers: Optional[int]
        The maximum number of image processing workers. Useful for limiting memory usage.
        Defaults to the number of CPUs * 5.

    Returns
    -------
    None
        Side effects are that the mask is saved to the specified mask_out_path location.
    """
    masker = DJIMultispectralMasker(img_path, mask_out_path, glint_threshold, mask_buffer_sigma, num_bins)
    with tqdm(total=len(masker)) as progress:
        return masker.process(max_workers=max_workers, callback=lambda _: progress.update(), err_callback=_err_callback)


def micasense_re(img_path: str, mask_out_path: str, glint_threshold: float = 0.9, mask_buffer_sigma: int = 0,
                 num_bins: int = 8, max_workers: Optional[int] = None) -> None:
    """Generate masks for glint regions in multispectral imagery from the Micasense camera using Tom Bell's algorithm.

    Parameters
    ----------
    img_path: str
        The path to a named input image or directory containing images. If img_path is a directory, all IMG_xxxx_6.tif
        files will be processed.

    mask_out_path: str
        The path to send your out image including the file name and type. e.g. "/path/to/mask.png".
        mask_out_path must be a directory if img_path is specified as a directory.

    glint_threshold: Optional[float]
        The amount of binned "blueness" that should be glint. Domain for values is (0.0, 1.0).
        Play with this value. Default is 0.9.

    mask_buffer_sigma: Optional[int]
        The sigma for the Gaussian kernel used to buffer the mask. Defaults to 0.

    num_bins: Optional[int]
        The number of bins the blue channel is slotted into. Defaults to 8 as in Tom's script.

    max_workers: Optional[int]
        The maximum number of image processing workers. Useful for limiting memory usage.
        Defaults to the number of CPUs * 5.

    Returns
    -------
    None
        Side effects are that the mask is saved to the specified mask_out_path location.
    """
    masker = MicasenseRedEdgeMasker(img_path, mask_out_path, glint_threshold, mask_buffer_sigma, num_bins)
    with tqdm(total=len(masker)) as progress:
        return masker.process(max_workers=max_workers, callback=lambda _: progress.update(), err_callback=_err_callback)


def rgb(img_path: str, mask_out_path: str, glint_threshold: float = 0.9, mask_buffer_sigma: int = 20,
        num_bins: int = 8, max_workers: Optional[int] = None) -> None:
    """Generate masks for glint regions in RGB imagery using Tom Bell's binning algorithm.

    Parameters
    ----------
    img_path: str
        The path to a named input image or directory containing images. If img_path is a directory, all tif, jpg, jpeg,
        and png images in that directory will be processed.

    mask_out_path: str
        The path to send your out image including the file name and type. e.g. "/path/to/mask.png".
        mask_out_path must be a directory if img_path is specified as a directory.

    glint_threshold: Optional[float]
        The amount of binned "blueness" that should be glint. Domain for values is (0.0, 1.0).
        Play with this value. Default is 0.9.

    mask_buffer_sigma: Optional[int]
        The sigma for the Gaussian kernel used to buffer the mask. Defaults to 20.

    num_bins: Optional[int]
        The number of bins the blue channel is slotted into. Defaults to 8 as in Tom's script.

    max_workers: Optional[int]
        The maximum number of image processing workers. Useful for limiting memory usage.
        Defaults to the number of CPUs * 5.

    Returns
    -------
    None
        Side effects are that the mask is saved to the specified mask_out_path location.
    """
    masker = BlueBinMasker(img_path, mask_out_path, glint_threshold, mask_buffer_sigma, num_bins)
    with tqdm(total=len(masker)) as progress:
        return masker.process(max_workers=max_workers, callback=lambda _: progress.update(), err_callback=_err_callback)


def specular(img_path: str, mask_out_path: str, percent_diffuse: float = 0.1, mask_thresh: float = 0.8,
             opening: int = 5, closing: int = 5, max_workers: Optional[int] = None) -> None:
    """Generate masks for glint regions in RGB imagery by setting a threshold on estimated specular reflectance.

    Parameters
    ----------
    img_path: str
        The path to a named input image or directory containing images. If img_path is a directory, all tif, jpg, jpeg,
        and png images in that directory will be processed.

    mask_out_path: str
        The path to send your out image including the file name and type. e.g. "/path/to/mask.png".
        mask_out_path must be a directory if img_path is specified as a directory.

    percent_diffuse: Optional[float]
        An estimate of the percentage of pixels in an image that show pure diffuse reflectance, and
        thus no specular reflectance (glint). Defaults to 0.1. Try playing with values, low ones typically work well.

    mask_thresh: Optional[float]
        The threshold on the specular reflectance estimate image to convert into a mask.
        E.g. if more than 50% specular reflectance is unacceptable, use 0.5. Default is 0.4.

    opening: Optional[int]
        The number of morphological opening iterations on the produced mask.
        Useful for closing small holes in the mask. Set to 0 by default (i.e. it's shut off).

    closing: Optional[int]
        The number of morphological closing iterations on the produced mask.
        Useful for removing small bits of mask. Set to 0 by default (i.e. it's shut off).

    max_workers: Optional[int]
        The maximum number of image processing workers. Useful for limiting memory usage.
        Defaults to the number of CPUs * 5.

    Returns
    -------
    None
        Side effects are that the mask is saved to the specified mask_out_path location.
    """
    masker = RGBSpecularMasker(img_path, mask_out_path, percent_diffuse, mask_thresh, opening, closing)
    with tqdm(total=len(masker)) as progress:
        return masker.process(max_workers=max_workers, callback=lambda _: progress.update(), err_callback=_err_callback)


if __name__ == '__main__':
    fire.Fire({
        'rgb': rgb,
        'specular': specular,
        'micasense': micasense_re,
        'dji': dji_ms
    })
