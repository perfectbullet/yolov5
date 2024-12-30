import os.path
import shutil
import xml.etree.ElementTree as ET
from os.path import join
from tqdm import tqdm
import argparse


def get_class_names(voc_dir):
    '''
    获取分类名词
    '''
    cls_names = set()
    for fname in os.listdir(voc_dir):
        if fname.endswith('.xml'):
            in_file = open(join(voc_dir, fname))
            tree = ET.parse(in_file)
            root = tree.getroot()

            for obj in root.iter('object'):
                cls_name = obj.find('name').text
                cls_names.add(cls_name)
    return list(cls_names)


def convert_label(voc_dir, lb_path, image_id, names):
    def convert_box(size, box):
        dw, dh = 1. / size[0], 1. / size[1]
        x, y, w, h = (box[0] + box[1]) / 2.0 - 1, (box[2] + box[3]) / 2.0 - 1, box[1] - box[0], box[3] - box[2]
        return x * dw, y * dh, w * dw, h * dh

    in_file = open(join(voc_dir, f'{image_id}.xml'))
    out_file = open(lb_path, 'w')
    tree = ET.parse(in_file)
    root = tree.getroot()
    size = root.find('size')
    w = int(size.find('width').text)
    h = int(size.find('height').text)

    for obj in root.iter('object'):
        cls = obj.find('name').text
        if cls in names and int(obj.find('difficult').text) != 1:
            xmlbox = obj.find('bndbox')
            bb = convert_box((w, h), [float(xmlbox.find(x).text) for x in ('xmin', 'xmax', 'ymin', 'ymax')])
            cls_id = names.index(cls)  # class id
            out_file.write(" ".join([str(a) for a in (cls_id, *bb)]) + '\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--voc_dir', type=str, required=True)
    parser.add_argument('--yolo_dir', type=str, required=True)
    args = parser.parse_args()

    # Convert
    voc_dir = args.voc_dir # label image data dir
    yolo_dir = args.yolo_dir
    yolo_images = join(yolo_dir, 'images')
    yolo_labels = join(yolo_dir, 'labels')
    if os.path.exists(yolo_images):
        shutil.rmtree(yolo_images)
    if os.path.exists(yolo_labels):
        shutil.rmtree(yolo_labels)

    os.makedirs(yolo_images, exist_ok=True)
    os.makedirs(yolo_labels, exist_ok=True)

    classes_path = os.path.join(voc_dir, 'classes.txt')
    if os.path.exists(classes_path):
        with open(classes_path) as f:
            names = f.read().strip().split()
    else:
        names = get_class_names(voc_dir)
    for idx, nm in enumerate(names):
        print('{}: {}'.format(idx, nm))
    image_ids = [name.replace('.jpg', '') for name in os.listdir(voc_dir) if name.endswith(('.jpg', ))]
    for id in tqdm(image_ids, desc=f'{voc_dir}'):
        old_image = join(voc_dir, f'{id}.jpg')    # old img path
        new_image = join(yolo_images, f'{id}.jpg')
        lb_path = os.path.join(yolo_labels, f'{id}.txt')  # new label path
        old_xml = os.path.join(voc_dir, f'{id}.xml')
        if os.path.exists(old_xml):
            shutil.copy(old_image, new_image)  # copy image
            convert_label(voc_dir, lb_path, id, names)  # convert labels to YOLO format
