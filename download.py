# Download labels
from utils.general import download, Path
import yaml
segments = True  # segment or box labels

with open('data/gxcoco.yaml', errors="ignore") as f:
    gxcoco = yaml.safe_load(f)  # load hyps dict
    dir = Path(gxcoco['path'])  # dataset root dir
url = 'https://github.com/ultralytics/assets/releases/download/v0.0.0/'
urls = [url + ('coco2017labels-segments.zip' if segments else 'coco2017labels.zip')]  # labels
download(urls, dir=dir.parent)

# Download data
urls = ['http://images.cocodataset.org/zips/train2017.zip',  # 19G, 118k images
        'http://images.cocodataset.org/zips/val2017.zip',  # 1G, 5k images
        'http://images.cocodataset.org/zips/test2017.zip']  # 7G, 41k images (optional)
download(urls, dir=dir / 'images', threads=3)