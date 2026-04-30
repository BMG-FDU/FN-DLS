import numpy as np
import tensorflow as tf
import cv2
import scipy.ndimage as ndi# SciPy库的子模块，用于处理多维图像数据
from scipy.ndimage import measurements# 用于处理图像的形态学变换和测量功能
from scipy.ndimage.morphology import generate_binary_structure

class afm_segment():
    def __init__(self,model_name):# 初始化方法，传入一个模型名称，加载模型
        self.model_name = model_name
        self.model = self.load_model()

    def load_model(self):# 加载模型的方法，使用tensorflow.keras.models.load_model加载模型
        model = tf.keras.models.load_model(self.model_name)
        return model

    def afm_import(self, path):# 读取图像的方法，使用cv2.imread从指定路径读取图像
        img = cv2.imread(path)
        return img

    def whole_predict(self, img):# 对整个图像进行预测，输入图像应具有（107,107,3）的形状，输出预测结果。
        assert img.shape == (107,107,3)
        img_expand = np.expand_dims(self, img, axis=0)
        prediction = self.model.predict(img_expand)
        prediction = prediction.reshape(107,107)
        return prediction

    def conv_predict(self, img, conv_num):# 对图像进行卷积预测，将图像分成conv_num x conv_num个小块，对每个小块进行预测，然后将预测结果合并成一个完整的预测结果
        def combine(l, n):
            length = int(len(l)/n)
            slice_range = [l[i*length:i*length+length] for i in range(n)]
            slice_range_small = []
            for i in slice_range:
                i = np.hstack(i)
                slice_range_small.append(i)
            whole = np.vstack(slice_range_small)
            return whole
        img_c = cv2.resize(img, (int(conv_num*107),int(conv_num*107)))
        print('The target img shape is',img_c.shape)
        x_window_range = np.linspace(0,img_c.shape[0]-107,conv_num)
        y_window_range = np.linspace(0,img_c.shape[0]-107,conv_num)
        slice_range = [(i,j) for i in x_window_range for j in y_window_range]
        out_list = []
        for (i,j) in  slice_range:
            slice_window = img_c[int(i) : int(i + 107), int(j) : int(j + 107), :]
            out_list.append(slice_window)
            #print(int((i*conv_num+j)/107),'/',conv_num**2,'is under prediction')   
        first = []
        for i in out_list:
            i = np.expand_dims(i, axis=0)
            i = self.model.predict(i)
            i = i.reshape(107,107)
            first.append(i)
        print(len(first),'sub-pictures obtained, with shape',first[0].shape)
        undo = combine(first, conv_num)
        return undo

    def activation(segment, threshold):# 使用阈值激活预测结果，将小于阈值的部分设为0，大于阈值的部分设为1
        return np.ceil(np.clip(segment,threshold,1)-threshold)

    def get_large_connect(self, img, area_thresh = 20):# 获取大连通区域，对输入的图像进行二值化处理，然后计算连通区域并过滤掉面积小于给定阈值的区域
        i = img.copy()# 复制输入图像img到变量i
        s = generate_binary_structure(2,2)# 使用generate_binary_structure函数生成一个二值结构（形态学操作所需结构元素）参数2,2表示一个2维的结构元素，它具有完全连接的性质（即8-连通）
        label, number = measurements.label(img, structure = s)# 使用measurements.label函数对图像进行标记，得到标记图像label和连通区域的数量number。
        # 函数中的structure参数表示用于确定连通区域的结构元素（在这里是2,2生成的结构元素）
        area = measurements.sum(img, label, index=range(label.max() + 1))
        # 使用measurements.label函数对图像进行标记，得到标记图像label和连通区域的数量number。函数中的structure参数表示用于确定连通区域的结构元素（在这里是2,2生成的结构元素）
        areaImg = area[label]# 创建一个名为areaImg的新图像，其中每个像素的值表示其所在连通区域的面积
        for y in range(i.shape[0]):# 遍历i中的所有像素。如果像素所在连通区域的面积小于等于给定阈值area_thresh，则将该像素值设为0（黑色）；否则，将像素值设为1（白色）
            for x in range(i.shape[1]):
                if areaImg[y,x] <= area_thresh:
                    i[y,x] = 0
                else:
                    i[y,x] = 1
        return i# 返回处理后的图像i

    def split_segment(self, img, num_list=(7,8,9,11,13)):# 使用不同的卷积数量对图像进行预测，返回预测结果列表
        split_list = []
        for conv_num in num_list:
            segment = afm_segment.conv_predict(self, img, conv_num)
            split_list.append(segment)
        return split_list

    def posterior(self, segment):# 计算后验概率，使用距离变换计算输入图像的距离图
        post = ndi.distance_transform_edt(segment)
        return post

    def posterior_check(self, threshold, split_list):# 检查后验概率，将多个预测结果组合成一个加权图，并使用给定的阈值进行激活
        weight_map = 0
        for segment in split_list:
            segment = cv2.resize(segment, (500,500))
            segment = afm_segment.activation(segment=segment, threshold=threshold)
            segment_check = ndi.distance_transform_edt(segment)
            weight_map += segment_check/len(split_list)
        weight_map[weight_map < 1] = 0
        return np.sign(weight_map)

    def segment_save(self, segment, file_path):# 将分割结果保存为图像文件
        plt.imshow(segment, cmap='binary')
        plt.axis('off')
        plt.savefig(file_path,bbox_inches='tight',pad_inches=0,dpi=300,figsize=(3,3))

    def segment_transfer(self, segment, target_size=(900,900)):# 将分割结果转换为目标尺寸的图像
        pic = np.concatenate([segment,segment,segment],axis=-1) * 255
        pic = cv2.resize(pic, target_size)
        return pic