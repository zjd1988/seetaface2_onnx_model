# seetaface2_onnx_model
contain face detect 、5/81 points 、face recognization models


1. pnet.onnx rnet.onnx onet.onnx 负责检测人脸

2. 5/81点检测分成了两个模型，Points5/81_Net1.onnx 和Points5/81_Net2.onnx，之所以分成两个是因为网络中包含了shapeIndexPatch 算子（具体实现请参考seetaface2的源码,或者测试脚本中的python实现），模型可以直接转换成MNN或者NCNN，
全网络结构参考Points5/81_Net_all.onnx

3. 人脸特征提取的模型因为文件比较大，所以放在网盘 https://pan.baidu.com/s/1R4rEpYxN3_GlZBBsOcWViQ 提取码：awb8。
