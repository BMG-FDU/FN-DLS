import numpy as np
import matplotlib.pyplot as plt
#%matplotlib inline
from mpl_toolkits.mplot3d import axes3d



def path2seq(path, locations):
    update = []
    for i in path:
        loc = locations[i - 1]
        update.append(loc)
    return np.array(update)


def rotate(seq_):
    seq = seq_ - seq_[0]
    di = seq[5]
    sina = -di[0] / ((di[0] ** 2 + di[1] ** 2) ** 0.5)
    cosa = di[1] / ((di[0] ** 2 + di[1] ** 2) ** 0.5)
    update = []
    for i in seq:
        update.append([i[1] * cosa - i[0] * sina, i[1] * sina + i[0] * cosa])
    return np.array(update)


def sample(seq):
    num = len(seq)
    update = seq[range(0, num, 5)]
    return update


def sample_index(seq):
    num = len(seq)
    update = list[range(0, num, 5)]


def rotate(locations, angle):
    locations = locations - np.array([450, 450])
    sina = np.sin(angle)
    cosa = np.cos(angle)
    update = []
    for i in locations:
        update.append([i[1] * cosa - i[0] * sina, i[1] * sina + i[0] * cosa])
    return np.array(update) + np.array([450, 450])



def z_estimate(locations):
    global node_index
    xyz_locations = np.zeros(shape=(locations.shape[0], 3))
    xyz_locations[:, 0] = locations[:, 0]
    xyz_locations[:, 1] = locations[:, 1]
    node_z_estimation = np.random.normal(0, 5, size=node_index.shape)
    for index, z_loc in zip(node_index, node_z_estimation):
        xyz_locations[index - 1, -1] = z_loc
    return xyz_locations


def sin_estimate(path, sample_len):
    sample_len = len(path)
    freq = 1 / sample_len
    sin_index = np.array(list(range(len(path))))
    psi = np.random.rand(len(path))
    A = np.random.normal(0, 2, 1)
    # sin = A * np.sin(freq*sin_index+psi)
    sin = A * np.sin(freq * sin_index)
    return sin


def get_z(path_list, xyz_locations):
    for path in path_list:
        sample_len = np.random.randint(low=120, high=200)
        z_locations = sin_estimate(path, sample_len=sample_len)

        for index, z_loc in zip(path, z_locations):
            xyz_locations[index - 1, -1] = z_loc
    return xyz_locations


def path2seq(path, locations):
    update = []
    for i in path:
        loc = locations[i - 1]
        update.append(loc)
    return np.array(update)


def draw_3d(path_list):
    global xyz
    fig = plt.figure()
    ax = fig.gca(projection="3d")
    ax.grid(False)
    # ax.set_ylim3d(0, 500)
    # ax.set_xlim3d(0, 500)
    # ax.axes.xaxis.set_visible(False)
    # ax.axes.yaxis.set_visible(False)
    plt.xlabel("x")
    plt.ylabel("y")
    for path in path_list:
        locs = path2seq(path, xyz)
        ax.plot(locs[:, 0], locs[:, 1], locs[:, 2], lw=3, color="dimgrey")


def wave(w=50):
    # xmk = np.array([list(range(50))*10]*500)
    # ymk = np.array([list(range(50))*10]*500)
    # xmk = np.array([list(range(512))]*512)
    # ymk = np.array([list(range(512))]*512)
    xmk = np.array([list(range(Img_scale))] * Img_scale)
    ymk = np.array([list(range(Img_scale))] * Img_scale)
    ymk = np.transpose(ymk)
    # c_x = (250-1)/2.0
    # c_y = (250-1)/2.0
    xxd = xmk
    yyd = ymk
    x = 10 * np.sin(2 * np.pi * yyd / w)  # + xxd
    y = 10 * np.cos(2 * np.pi * xxd / w)  # + yyd
    return x, y


def update_xyz(wave_space):
    global xyz
    for i in range(xyz.shape[0]):
        xyz[i, 2] = wave_space[int(xyz[i, 1]), int(xyz[i, 0])]