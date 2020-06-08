# seetaface2_onnx_model
only contain face detect 、5 points 、face recognization models


1 pnet.onnx rnet.onnx onet.onnx 负责检测人脸
2 5点检测分成了两个模型，Points5_Net1.onnx 和Points5_Net2.onnx，之所以分成两个是因为网络中包含了shapeIndexPatch 算子（具体实现请参考seetaface2的源码），直接转换乘MNN或者NCNN不支持
全网络结构参考Points5_Net_all.onnx
3 人脸特征提取的模型因为文件比较大，所以放在网盘。
