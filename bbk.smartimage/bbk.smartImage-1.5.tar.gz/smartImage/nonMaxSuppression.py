# Created by babiking on Jan.29th, 2018 @tucodec
#       nonMaxSuppression.py: non-maximum suppression algorithm
import numpy as np


def _non_maximum_suppression(scores, boxes, overThresh):

    '''
        Function:
                    _non_maximum_suppression
                        i.e. select high-scoring detection bounding box and skip
        Input:
                    [1] scores, <ndarray>, dimension->[num_boxes, num_classes], i.e. row_item = [score1, score2, ..., scoreN]
                    [2] boxes,  <ndarray>, dimension->[num_boxes, 4],           i.e. row_item = [xmin, ymin, xmax, ymax]
                    [3] overThresh, <float>,  note. IoU threshold
        Output:
                    [1] nms_scores
                    [2] nms_boxes
    '''
    num_boxes = scores.shape[0]

    if len(scores.shape) > 1:
        num_classes = scores.shape[1]
    else:
        num_classes = 1



    nms_scores = []
    nms_boxes = []

    if boxes is None:
        return nms_scores, nms_boxes


    # !Coordinates [xmin, ymin, xmax, ymax] of vertices within a bounding box...
    xmin = boxes[:, 0]
    ymin = boxes[:, 1]
    xmax = boxes[:, 2]
    ymax = boxes[:, 3]

    area = (xmax-xmin+1) * (ymax-ymin+1)


    # !Non-maximum suppression for each object class...
    for cls_id in range(num_classes):

        if num_classes == 1:
            cls_scores = scores
        else:
            cls_scores = scores[:, cls_id]
        cls_boxes  = []

        if np.sum(cls_scores) == 0:
            continue

        # !I: sorted index in acending order...
        I = np.argsort(cls_scores)

        # !pick: indexes of selected bounding boxes...
        pick = []

        while(I.size != 0):

            # !Keep the bounding boxes with maximum score i.e. fidelity...
            last = len(I)
            indx = I[last-1]
            pick.append(indx)

            xxmin = np.array([ max(xmin[indx], x) for x in xmin[I[0:last-1]] ])
            yymin = np.array([ max(ymin[indx], y) for y in ymin[I[0:last-1]] ])
            xxmax = np.array([ min(xmax[indx], x) for x in xmax[I[0:last-1]] ])
            yymax = np.array([ min(ymax[indx], y) for y in ymax[I[0:last-1]] ])

            # !Calculate the overlap between maximum-scoring bounding box with others...
            inter_h = np.array([max(0, h) for h in (xxmax-xxmin)])
            inter_w = np.array([max(0, w) for w in (yymax-yymin)])

            inter_area = inter_h * inter_w

            overlap = inter_area / float(area[indx])

            select = [i for i in range(last-1) if overlap[i]<=overThresh]
            I = I[select]


        cls_scores = cls_scores[pick]
        cls_boxes  = boxes[pick, :]

        nms_scores.append(cls_scores)
        nms_boxes.append(cls_boxes)


    return nms_scores[0], nms_boxes[0]