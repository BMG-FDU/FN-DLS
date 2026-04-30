import numpy as np

def fullPath2locSeq(full_path, node_list):
    update_list = []
    for path in full_path:
        update_list.append(np.array([node_list[i-1] for i in path]))
    return update_list
def sample(seq):
    num = len(seq)
    if num > 10:
        update_ = seq[range(0,num,10)]
        last = seq[-1].reshape((1,3))
        update = np.vstack((update_, last))
    else:
        update = seq[range(0,-2,-1)]
    return update
def str_generate(coordinate):
    #str_g = str(int(coordinate[0]))+","+str(int(coordinate[1]))+","+str(int(coordinate[2]))
    str_g = str(int(coordinate[2]))+","+str(coordinate[1])+","+str(coordinate[0])
    return str_g
def write_sc(sam_list,name):
    count = 0
    with open(name,"w") as f:
        f.write("3d=true")
        f.write('\n')
        for x in sam_list:
            count += 1
            for coordinate in x:
                coordinate_str = str_generate(coordinate)
                f.write(coordinate_str)
                f.write('\n')
            f.write('\r\n')
    print("轨迹计数：{}".format(count))
def shift_generate(coordinate, shift):
    str_g = str(int(shift))+","+str(coordinate[1])+","+str(coordinate[0])
    return str_g
def write_shift(path_list, name, shift1, shift2):
    count = 0
    with open(name,"w") as f:
        f.write("3d=true")
        f.write("\n")
        for connection in path_list:
            upper = shift_generate(connection[0], shift=shift1)
            f.write(upper)
            f.write("\n")
            down = shift_generate(connection[1], shift=shift2)
            f.write(down)
            f.write("\n")
            f.write("\r")
            count += 1
    print("轨迹计数：{}".format(count))