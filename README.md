# Photoscan Script to Automate Processing UMich Iver3 Stereo Images

## Example Command
`/opt/photoscan/photoscan-pro/photoscan.sh -platform offscreen -r photoscan-processing-stereo-iver.py /image_dir /lat_lon_csv -n project_name -o ouput_dir`

## Common Errors
>warning out of memory (2)

The GPU server probably has something else running already. Check with either `nvidia-smi` or `htop`.

