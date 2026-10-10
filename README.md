# Neusoft Reach Mono3D

**Monocular RGB 3D detection with an offline prediction viewer.** Turn single-image 3D predictions into camera overlays and bird's-eye views. The viewer needs no LiDAR or model weights.

## Preview

[Offline geometry demo](examples/geometry-demo.html)

The offline demo uses synthetic boxes and a synthetic background to demonstrate projection and layout.

## View predictions

The viewer requires only Python 3:

```bash
python3 tools/render_predictions.py \
  --predictions examples/synthetic_predictions.txt \
  --calibration examples/synthetic_calib.txt \
  --synthetic --output examples/geometry-demo.html
```

For your own predictions and image:

```bash
python3 tools/render_predictions.py \
  --predictions /path/to/000001.txt \
  --calibration /path/to/calib/000001.txt \
  --image /path/to/image_2/000001.png \
  --width 1242 --height 375 --output report.html
```

Use KITTI's 15/16-field camera-coordinate format, H/W/L dimensions, bottom-center positions and P2 calibration. Match the image dimensions. Bird's-eye range is ±25 m laterally and 0–50 m forward.

## Reference results

| Split | Setup | Car AP3D |
|---|---|---:|
| KITTI validation | Car / Pedestrian / Cyclist | 23.72 |
| KITTI validation | Car only | 24.05 |
| KITTI test | Moderate | 19.11 |

[Table reference](https://github.com/alanzhangcs/MonoCoP#model-zoo). Validation difficulty is unspecified. These reference results have not been reproduced here.

## Train and evaluate

Prepare a CUDA environment, KITTI data and the required checkpoint. [Setup guide](docs/UPSTREAM_README.md).

```bash
bash train.sh 0 --config config/monocop.yaml
bash test.sh 0 --config config/monocop_test.yaml
```

Viewer checks cover projection, coordinates, invalid inputs and HTML escaping; they do not measure detector accuracy:

```bash
python3 -m unittest discover -s tests -v
```

## License

[MIT](LICENSE) · [Source](https://github.com/alanzhangcs/MonoCoP) · [Paper](https://arxiv.org/abs/2503.11651)
