import onnxruntime
import numpy as np
import cv2

m_origin_patch = [15, 15]
m_origin = [112, 112]

class HypeShape:
    def __init__(self, shape):
        self.m_shape = shape
        self.m_weights = [0]*len(self.m_shape)
        size = len(self.m_shape)
        self.m_weights[size - 1] = self.m_shape[size - 1]
        for times in range(size - 1):
             self.m_weights[size - 1 - times - 1] =  self.m_weights[size - 1 - times] * self.m_shape[size - 1 - times - 1]

    def to_index(self, coordinate):
        if len(coordinate) == 0:
            return 0
        size = len(coordinate)
        weight_start = len(self.m_weights) - size + 1
        index = 0
        for times in range(size - 1):
            index += self.m_weights[weight_start + times] * coordinate[times]
        index += coordinate[size - 1]
        return index


def shape_index_process(feat_data, pos_data):
    feat_h = feat_data.shape[2]
    feat_w = feat_data.shape[3]

    landmarkx2 = pos_data.shape[1]
    x_patch_h = int( m_origin_patch[0] * feat_data.shape[2] / float( m_origin[0] ) + 0.5 )
    x_patch_w = int( m_origin_patch[1] * feat_data.shape[3] / float( m_origin[1] ) + 0.5 )

    feat_patch_h = x_patch_h
    feat_patch_w = x_patch_w

    num = feat_data.shape[0]
    channels = feat_data.shape[1]

    r_h = ( feat_patch_h - 1 ) / 2.0
    r_w = ( feat_patch_w - 1 ) / 2.0
    landmark_num = int(landmarkx2 * 0.5)

    pos_offset = HypeShape([pos_data.shape[0], pos_data.shape[1]])
    feat_offset = HypeShape([feat_data.shape[0], feat_data.shape[1], feat_data.shape[2], feat_data.shape[3]])
    nmarks = int( landmarkx2 * 0.5 )
    out_shape = [feat_data.shape[0], feat_data.shape[1], x_patch_h, nmarks, x_patch_w]
    out_offset = HypeShape([feat_data.shape[0], feat_data.shape[1], x_patch_h, nmarks, x_patch_w])
    buff = np.zeros(out_shape)
    zero = 0

    buff = buff.reshape((-1))
    pos_data = pos_data.reshape((-1))
    feat_data = feat_data.reshape((-1))

    for i in range(landmark_num):
        for n in range(num):
            # coordinate of the first patch pixel, scale to the feature map coordinate
            y = int( pos_data[pos_offset.to_index( [n, 2 * i + 1] )] * ( feat_h - 1 ) - r_h + 0.5 )
            x = int( pos_data[pos_offset.to_index( [n, 2 * i] )] * ( feat_w - 1 ) - r_w + 0.5 )

            for c in range(channels):
                for ph in range(feat_patch_h):
                    for pw in range(feat_patch_w):
                        y_p = y + ph
                        x_p = x + pw
                        # set zero if exceed the img bound
                        if y_p < 0 or y_p >= feat_h or x_p < 0 or x_p >= feat_w:
                            buff[out_offset.to_index( [n, c, ph, i, pw] )] = zero
                        else:
                            buff[out_offset.to_index( [n, c, ph, i, pw] )] = feat_data[feat_offset.to_index( [n, c, y_p, x_p] )]

    return buff.reshape((1,-1,1,1)).astype(np.float32)




devices = onnxruntime.get_device()
session = onnxruntime.InferenceSession("./Points81_Net1.onnx")
first_input_name = session.get_inputs()[0].name

test_img = cv2.imread("./head.jpg")
gray_img = cv2.cvtColor(test_img, cv2.COLOR_BGR2GRAY)
gray_img = gray_img.reshape((1, 1, 112, 112)).astype(np.float32)
# points81 net1
results_1 = session.run([], {first_input_name : gray_img})

# shape index process
feat_data = results_1[0]
pos_data = results_1[1]
shape_index_results = shape_index_process(feat_data, pos_data)

# points81 net2
session = onnxruntime.InferenceSession("./Points81_Net2.onnx")
first_input_name = session.get_inputs()[0].name
results_2 = session.run([], {first_input_name : shape_index_results})

landmarks = (results_2[0] + results_1[1])*112
landmarks = landmarks.reshape((-1)).astype(np.int32)

point_size = 1
point_color = (0, 0, 255) # BGR
thickness = 4 # 可以为 0 、4、8
for i in range(landmarks.size // 2):
    point = (landmarks[2*i], landmarks[2*i + 1])
    cv2.circle(test_img, point, point_size, point_color, thickness)

cv2.imwrite("points81_result.jpg", test_img)
print(landmarks)