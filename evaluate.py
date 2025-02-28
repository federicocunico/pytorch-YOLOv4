# -*- coding: utf-8 -*-

# import sys
# import time
# from PIL import Image, ImageDraw
# from models.tiny_yolo import TinyYoloNet
from tool.utils import *
from models import Yolov4
import argparse
from tqdm import tqdm

"""hyper parameters"""
use_cuda = True


def init_net(pretrained, n_classes):
    # m = Darknet(cfgfile)
    # model = Yolov4(cfg.pretrained, n_classes=cfg.classes)
    m = Yolov4(n_classes=n_classes)
    # model = Yolov4(n_classes=n_classes)
    pretrained_dict = torch.load(pretrained, map_location=torch.device('cuda'))
    from collections import OrderedDict
    new_state_dict = OrderedDict()

    for key, value in pretrained_dict.items():
        new_key = key.replace('module.', '')
        new_state_dict[new_key] = value
    m.load_state_dict(new_state_dict)

    # m.print_network()
    # m.load_weights(weightfile)
    print('Loading weights from %s... Done!' % (pretrained))

    if use_cuda:
        m.cuda()
    
    return m

def detect_imges(model, imgfile_list=['data/dog.jpg', 'data/giraffe.jpg']):
    m = model

    boxes = []
    imges_list = []
    # imgfile_list = [f for f in imgfile_list if '000101' in f or '001904' in f]# imgfile_list[0:100]
    for imgfile in tqdm(imgfile_list):
        img = Image.open(imgfile).convert('RGB')
        imges_list.append(img)
        # sized = img.resize((m.width, m.height))
        sized = img.resize((608, 608))  # TODO: generalize
        # imges.append()
        img1 = np.expand_dims(np.array(sized), axis=0)
        bb = do_detect(m, img1, 0.5, num_classes, 0.4, use_cuda)
        boxes.append(bb)

    # images = np.concatenate(imges, 0)
    # for i in range(2):
    #     start = time.time()
    #     boxes = do_detect(m, images, 0.5, num_classes, 0.4, use_cuda)
    #     finish = time.time()
    #     if i == 1:
    #         print('%s: Predicted in %f seconds.' % (imgfile, (finish - start)))

    class_names = load_class_names(namesfile)
    for i,(img,box) in enumerate(zip(imges_list,boxes)):
        plot_boxes(img, box, 'predictions{}.jpg'.format(i), class_names)


def detect_cv2(cfgfile, weightfile, imgfile):
    import cv2
    m = Darknet(cfgfile)

    m.print_network()
    m.load_weights(weightfile)
    print('Loading weights from %s... Done!' % (weightfile))

    if use_cuda:
        m.cuda()

    img = cv2.imread(imgfile)
    sized = cv2.resize(img, (m.width, m.height))
    sized = cv2.cvtColor(sized, cv2.COLOR_BGR2RGB)

    for i in range(2):
        start = time.time()
        boxes = do_detect(m, sized, 0.5, m.num_classes, 0.4, use_cuda)
        finish = time.time()
        if i == 1:
            print('%s: Predicted in %f seconds.' % (imgfile, (finish - start)))

    class_names = load_class_names(namesfile)
    plot_boxes_cv2(img, boxes, savename='predictions.jpg', class_names=class_names)


def detect_cv2_camera(cfgfile, weightfile):
    import cv2
    m = Darknet(cfgfile)

    m.print_network()
    m.load_weights(weightfile)
    print('Loading weights from %s... Done!' % (weightfile))

    if use_cuda:
        m.cuda()

    cap = cv2.VideoCapture(0)
    # cap = cv2.VideoCapture("./test.mp4")
    cap.set(3, 1280)
    cap.set(4, 720)
    print("Starting the YOLO loop...")

    while True:
        ret, img = cap.read()
        sized = cv2.resize(img, (m.width, m.height))
        sized = cv2.cvtColor(sized, cv2.COLOR_BGR2RGB)

        start = time.time()
        boxes = do_detect(m, sized, 0.5, num_classes, 0.4, use_cuda)
        finish = time.time()
        print('Predicted in %f seconds.' % (finish - start))

        class_names = load_class_names(namesfile)
        result_img = plot_boxes_cv2(img, boxes, savename=None, class_names=class_names)

        cv2.imshow('Yolo demo', result_img)
        cv2.waitKey(1)

    cap.release()


def detect_skimage(cfgfile, weightfile, imgfile):
    from skimage import io
    from skimage.transform import resize
    m = Darknet(cfgfile)

    m.print_network()
    m.load_weights(weightfile)
    print('Loading weights from %s... Done!' % (weightfile))

    if use_cuda:
        m.cuda()

    img = io.imread(imgfile)
    sized = resize(img, (m.width, m.height)) * 255

    for i in range(2):
        start = time.time()
        boxes = do_detect(m, sized, 0.5, m.num_classes, 0.4, use_cuda)
        finish = time.time()
        if i == 1:
            print('%s: Predicted in %f seconds.' % (imgfile, (finish - start)))

    class_names = load_class_names(namesfile)
    plot_boxes_cv2(img, boxes, savename='predictions.jpg', class_names=class_names)


def get_args():
    parser = argparse.ArgumentParser('Test your image or video by trained model.')
    # parser.add_argument('-cfgfile', type=str, default='./cfg/yolov4-x.cfg',
    #                     help='path of cfg file', dest='cfgfile')
    # parser.add_argument('-weightfile', type=str,
    #                     default='./checkpoints/Yolov4_epoch1.pth',
    #                     help='path of trained model.', dest='weightfile')
    # parser.add_argument('-imgfile', type=str,
    #                     default='./data/mscoco2017/train2017/190109_180343_00154162.jpg',
    #                     help='path of your image file.', dest='imgfile')
    parser.add_argument('-pretrained', type=str, required=True)
    parser.add_argument('-num_classes', type=int, required=True)
    args = parser.parse_args()

    return args


if __name__ == '__main__':
    args = get_args()
    num_classes = args.num_classes  # 2

    images_path = 'data/Images'
    files = os.listdir(images_path)
    # files = [os.path.join(images_path, f) for f in files if os.path.isfile(os.path.join(images_path,f)) and f.split('.')[-1] in ['jpg', 'jpeg', 'png']]
    with open('test.txt', 'r') as fp:
        lines = fp.readlines()
        lines = [f.split(' ')[0] for f in lines]
        lines = [f.split('/')[-1] for f in lines]
        files = [os.path.join(images_path, f) for f in lines]
        
    _model = init_net(args.pretrained, num_classes)
    if num_classes == 20:
        namesfile = 'data/voc.names'
    elif num_classes == 80:
        namesfile = 'data/coco.names'
    else:
        namesfile = 'data/x.names'

    detect_imges(_model, files)

    # if args.imgfile:
    #     detect(args.cfgfile, args.weightfile, args.imgfile)
    #     # detect_imges(args.cfgfile, args.weightfile)
    #     # detect_cv2(args.cfgfile, args.weightfile, args.imgfile)
    #     # detect_skimage(args.cfgfile, args.weightfile, args.imgfile)
    # else:
    #     detect_cv2_camera(args.cfgfile, args.weightfile)
