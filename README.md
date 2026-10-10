# Neusoft Reach Mono3D

**Monocular RGB 3D detection with an offline prediction viewer.**

Turn single-image 3D predictions into camera-view overlays and bird's-eye-view visualizations. The viewer works offline and does not require LiDAR or model weights.

## Preview

[Offline geometry demo](examples/geometry-demo.html)

The offline demo uses synthetic 3D boxes and a synthetic background to demonstrate projection and visualization.

## View Predictions

The viewer requires only Python 3.

```bash
python3 tools/render_predictions.py \
  --predictions examples/synthetic_predictions.txt \
  --calibration examples/synthetic_calib.txt \
  --synthetic \
  --output examples/geometry-demo.html
```

To visualize your own predictions:

```bash
python3 tools/render_predictions.py \
  --predictions /path/to/000001.txt \
  --calibration /path/to/calib/000001.txt \
  --image /path/to/image_2/000001.png \
  --width 1242 \
  --height 375 \
  --output report.html
```

The viewer supports KITTI-style camera-coordinate predictions with:

- 15/16-field prediction format
- H/W/L object dimensions
- bottom-center 3D positions
- P2 camera calibration

Make sure the specified image dimensions match the input image.

The bird's-eye-view visualization covers:

- lateral range: ±25 m
- forward range: 0–50 m

## Reference Results

| Split | Setup | Car AP3D |
|---|---|---:|
| KITTI validation | Car / Pedestrian / Cyclist | 23.72 |
| KITTI validation | Car only | 24.05 |
| KITTI test | Moderate | 19.11 |

These values are provided as reference results and may vary depending on training settings, data preparation, and evaluation configuration.

## Train and Evaluate

Prepare a CUDA environment, KITTI dataset, and the required model checkpoint.

```bash
bash train.sh 0 --config config/monocop.yaml
bash test.sh 0 --config config/monocop_test.yaml
```

## Testing

Viewer tests cover projection, coordinate handling, invalid inputs, and HTML escaping.

```bash
python3 -m unittest discover -s tests -v
```

These tests validate the visualization pipeline and do not measure detector accuracy.

## License

[MIT](LICENSE)
