import cv2
import torch
import torch.backends.cudnn as cudnn
from PoseModule.yolov7.models.experimental import attempt_load
from PoseModule.yolov7.utils.datasets import LoadStreams, LoadImages
from PoseModule.yolov7.utils.general import check_img_size, check_imshow, non_max_suppression, apply_classifier, \
    scale_coords, set_logging
from PoseModule.yolov7.utils.plots import colors, plot_one_box
from PoseModule.yolov7.utils.torch_utils import select_device, load_classifier



def detect(weights, view_img, imgsz, half_precision, kpt_label, scr, device, conf_thres, iou_thres,classes, agnostic_nms, line_thickness):
    source = scr
    webcam = source.isnumeric() or source.endswith('.txt') or source.lower().startswith(
        ('rtsp://', 'rtmp://', 'http://', 'https://'))    

    kpts = None

    # Initialize
    set_logging()
    device = select_device(device)
    half = device.type != 'cpu' and half_precision  # half precision only supported on CUDA

    # Load model
    model = attempt_load(weights, map_location=device)  # load FP32 model
    stride = int(model.stride.max())  # model stride


    if isinstance(imgsz, (list,tuple)):
        assert len(imgsz) ==2; "height and width of image has to be specified"
        imgsz[0] = check_img_size(imgsz[0], s=stride)
        imgsz[1] = check_img_size(imgsz[1], s=stride)
    else:
        imgsz = check_img_size(imgsz, s=stride)  # check img_size
    names = model.module.names if hasattr(model, 'module') else model.names  # get class names
    

    if half:
        model.half()  # to FP16

    # Second-stage classifier
    classify = False
    if classify:
        modelc = load_classifier(name='resnet101', n=2)  # initialize
        modelc.load_state_dict(torch.load('weights/resnet101.pt', map_location=device)['model']).to(device).eval()

    # Set Dataloader
    if webcam:
        view_img = check_imshow()
        cudnn.benchmark = True  # set True to speed up constant image size inference
        dataset = LoadStreams(source, img_size=imgsz, stride=stride)
    else:
        dataset = LoadImages(source, img_size=imgsz, stride=stride)

    # Run inference
    if device.type != 'cpu':
        model(torch.zeros(1, 3, imgsz, imgsz).to(device).type_as(next(model.parameters())))  # run once

    for path, img, im0s, vid_cap in dataset:

        img = torch.from_numpy(img).to(device)
        img = img.half() if half else img.float()  # uint8 to fp16/32
        img /= 255.0  # 0 - 255 to 0.0 - 1.0
        if img.ndimension() == 3:
            img = img.unsqueeze(0)

        # Inference
        pred = model(img, augment=False)[0]

        # Apply NMS
        
        pred = non_max_suppression(pred, conf_thres, iou_thres, classes=classes, agnostic=agnostic_nms, kpt_label=kpt_label)
        

        # Apply Classifier
        if classify:
            pred = apply_classifier(pred, modelc, img, im0s)

        # Process detections
        for i, det in enumerate(pred):  # detections per image
            if webcam:  # batch_size >= 1
               im0 = im0s[i].copy()
            else:
                im0 = im0s.copy()

            if len(det):
                # Rescale boxes from img_size to im0 size
                scale_coords(img.shape[2:], det[:, :4], im0.shape, kpt_label=False)
                scale_coords(img.shape[2:], det[:, 6:], im0.shape, kpt_label=kpt_label, step=3)

                # Write results
                for det_index, (*xyxy, conf, cls) in enumerate(reversed(det[:,:6])):
                    if view_img:  # Add bbox to image
                        c = int(cls)  # integer class
                        label = None if False else (names[c] if False else f'{names[c]} {conf:.2f}')
                        kpts = det[det_index, 6:]
                        
                        plot_one_box(xyxy, im0, label=label, color=colors(c, True), line_thickness=line_thickness, kpt_label=kpt_label, kpts=kpts, steps=3, orig_shape=im0.shape[:2])
                

            # Stream results
            if view_img:
                cv2.imshow("Pose detection", im0)
                cv2.waitKey(1)  # 1 millisecond

            if kpts != None:
                print(kpts)


