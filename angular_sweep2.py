import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import json

q_e = 1.602176565e-19

def WriteFile(file_name, data):
    
    with open(file_name, 'w') as f:
        json.dump(data, f) 
        f.close()

def ReadFile(file_name):
    file = open(file_name, encoding='utf-8')
    file_1 = file.read()
    file_2 = json.loads(file_1)
    file.close()
    return file_2       

def inverse(m):
    return np.linalg.inv(m)


def str_l(l):
    return [str(x) for x in l]
def float_l(l):
    return [float(x) for x in l]
def norm(v):
    return np.linalg.norm(v)


def spherical_to_cartesian(p):
    r, theta, phi = p[0], p[1], p[2]
    x = r * np.sin(theta) * np.cos(phi)
    y = r * np.sin(theta) * np.sin(phi)
    z = r * np.cos(theta)
    return [x, y, z]

def cartesian_to_spherical(p):
    x, y, z = p[0], p[1], p[2]
    r = np.sqrt(x**2 + y**2 + z**2)
    # theta = np.arctan(np.sqrt(x**2 + y**2)/z)
    theta = np.arccos(z/r)
    phi = np.arctan2(y,x)
    return [r, theta, phi]

def rotation_matrix_x(theta):
    R = np.array([
        [1, 0, 0],
        [0, np.cos(theta), -np.sin(theta)],
        [0, np.sin(theta), np.cos(theta)]
        ])
    return R

def rotation_matrix_y(theta):
    R = np.array([
        [np.cos(theta),0,  -np.sin(theta)],
        [0, 1, 0],
        [np.sin(theta),0, np.cos(theta)]
        ])
    return R

def rotation_matrix_z(theta):
    R = np.array([
    [np.cos(theta), -np.sin(theta), 0],
    [np.sin(theta), np.cos(theta), 0],
    [0, 0, 1]
    ])
    return R

def tot_rotate_vector(p, normal_vec, alpha):
    x, y, z = p
    n_R, n_theta, n_phi = normal_vec
    R = rotation_matrix_z(n_phi).dot(rotation_matrix_y(-n_theta)).dot(rotation_matrix_z(alpha)).dot(rotation_matrix_y(n_theta)).dot(rotation_matrix_z(-n_phi))
    return np.dot(R, np.array([x,y,z]))

def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    return vector / norm(vector)



def angle_between(v1, v2):
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))

# def angle_between(v1, v2):
#     v1_u = unit_vector(v1)
#     v2_u = unit_vector(v2)
#     return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))


def colorFader(c1,c2,mix=0): #fade (linear interpolate) from color c1 (at mix=0) to c2 (mix=1)
    c1=np.array(mpl.colors.to_rgb(c1))
    c2=np.array(mpl.colors.to_rgb(c2))
    return mpl.colors.to_hex((1-mix)*c1 + mix*c2)

def colorFaderN(c_l, m):
    N_c = len(c_l)
    cut_vals = np.linspace(0, 1, N_c)
    intvs = [[cut_vals[i], cut_vals[i+1]] for i in range(N_c - 1)]
    j = 0
    for interval in intvs:
        if m >= interval[0] and m < interval[1]:
            return colorFader(c_l[j], c_l[j + 1], (m - cut_vals[j])/(cut_vals[j + 1] - cut_vals[j]))
        j += 1



    




def full_rotation_sweep(normal_vector_spherical, N, v_init_g, B_magnitude, angle_max):

    #normal vector in spherical coordinates. (Phi is about the x axis counterclockwise).
    n_sph = [1, normal_vector_spherical[0], normal_vector_spherical[1]]

    #The sweep goes from alpha = 0 to alpha = alpha_max
    alpha_max = angle_max

    #init_angle specifies the angle that corresponds to alpha = 0. The angle is in the xy plane starting aligned with the x axis and goes (counterclockwise).

    coords_all = []
    
    n_cart = spherical_to_cartesian(n_sph)
    N_v = np.array(n_cart)
    if v_init_g == None:
        init_cross = np.dot(rotation_matrix_z(3*np.pi/2), np.array([1, 0, 0]))
        v_init_1 = np.cross(N_v, init_cross)
        v_init = v_init_1/norm(v_init_1)
    else:
        v_init = v_init_g/norm(v_init_g)
    
    for i in range(N):
        alpha_i = i/(N-1) * alpha_max
        rotated_coords = tot_rotate_vector(v_init, n_sph, alpha_i)
        rotated_coords *= B_magnitude
        coords_all.append(tuple(rotated_coords))


    dot_l = [np.dot(np.array(n_cart), np.array(p)) for p in coords_all]

    # print("Min of all dot products", min(dot_l))
    # print("Max of all dot products", max(dot_l))

    return coords_all

def rotation_between_2_vectors(B1_spherical, B2_spherical, N):
    #Initial and final vectors. The sweep starts at B1 and goes to B2 counterclockwise. This direction is with respect to the plane spanned by B1 and B2 with B1 x B2 pointing out of the plane. 
    #spherical coordinates. phi is from the x axis counterclockwise

    B1_cart = spherical_to_cartesian(B1_spherical)
    B2_cart = spherical_to_cartesian(B2_spherical)

    B1 = np.array(B1_cart)
    B2 = np.array(B2_cart)

    B12_cross = np.cross(B1, B2)


    # print("ang tot", np.degrees(ang_tot))
    # print("norms",norm(B1),  norm(B2))

    N_v = B12_cross/norm(B12_cross)

    coords_all = []
    v_init = B1

    n_sph = cartesian_to_spherical(N_v)
    

    #determining angle between both vectors

    #might need adjusting, not reliable. 
    # ang_tot = angle_between(B1, B2)

    all_angles_coords_all = []
    N_precision = 10000
    for i in range(N_precision):
        alpha_i = i/N_precision * 2*np.pi
        rotated_coords = tot_rotate_vector(v_init, n_sph, alpha_i)
        all_angles_coords_all.append(tuple(rotated_coords))

    cos_l = [np.dot(vec, B2) for vec in all_angles_coords_all]
    max_index = cos_l.index(max(cos_l))
    angle_between = max_index/N_precision * 2* np.pi



    for i in range(N):
        alpha_i = i/(N-1) * angle_between
        rotated_coords = tot_rotate_vector(v_init,n_sph, alpha_i)
        coords_all.append(tuple(rotated_coords))


    dot_l = [np.dot(N_v, np.array(p)) for p in coords_all]

    # print("Min of all dot products", np.min(dot_l))
    # print("Max of all dot products", np.max(dot_l))

    return coords_all




def plot_vectors_in_plane_sweep(coords_all, normal_vector_theta_phi, B_magnitude):

    N = len(coords_all)
    fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
    ax.set_axis_off()

    col1 = 'orange'
    col2 = 'red'
    c = 0
    for i in range(N):
        coord = coords_all[i]
        ax.quiver(0, 0, 0, coord[0], coord[1], coord[2], color = colorFader(col1,col2,c/N))
        c += 1

    n_cart = spherical_to_cartesian([B_magnitude, normal_vector_theta_phi[0], normal_vector_theta_phi[1]])


    ax.quiver(0, 0, 0, 2, 0, 0, color='#00FE23', label='x')
    ax.quiver(0, 0, 0, 0, 2, 0, color='#00A216', label='y')
    ax.quiver(0, 0, 0, 0, 0, 2, color='#175E21', label='z')

    ax.quiver(0, 0, 0, n_cart[0],n_cart[1],n_cart[2], color='k', label='Normal vector')

    ax.set_xlim([-1, 1])
    ax.set_ylim([-1, 1])
    ax.set_zlim([-1, 1])

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('Full angular sweep')
    plt.legend()

    plt.show()

def plot_vectors_between_2_vectors(coords_all, B1_spherical, B2_spherical):

    N = len(coords_all)
    fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
    ax.set_axis_off()

    ax.quiver(0, 0, 0, 2, 0, 0, color='#00FE23', label='x')
    ax.quiver(0, 0, 0, 0, 2, 0, color='#00A216', label='y')
    ax.quiver(0, 0, 0, 0, 0, 2, color='#175E21', label='z')

    # fig = plt.figure()
    # ax = fig.add_subplot(111, projection='3d')

    col1 = 'orange'
    col2 = 'red'
    c = 0
    for i in range(N):
        coord = coords_all[i]
        ax.quiver(0, 0, 0, coord[0], coord[1], coord[2], color = colorFader(col1,col2,c/N))
        c += 1

    
    B1_cart = spherical_to_cartesian(B1_spherical)
    B2_cart = spherical_to_cartesian(B2_spherical)
    ax.quiver(0, 0, 0, B1_cart[0],B1_cart[1],B1_cart[2], color='#FEFE00')
    ax.quiver(0, 0, 0, B2_cart[0],B2_cart[1],B2_cart[2], color='#A91700')
    


    ax.set_xlim([-1, 1])
    ax.set_ylim([-1, 1])
    ax.set_zlim([-1, 1])

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('Angular sweep between B1 (yellow) and B2 (dark red).')
    plt.legend()

    plt.show()





#N = 10 # magnet points 
#n = 1 # data points


#specify theta and phi
# normal_unit_vector_spherical = [np.pi/2, np.pi/2]
# B_magnitude = 0.5

# coord_list = full_rotation_sweep(normal_unit_vector_spherical, N, [B_magnitude, 0, 0], B_magnitude, 2*np.pi)
# plot_vectors_in_plane_sweep(coord_list, normal_unit_vector_spherical, B_magnitude)



# print([norm(np.array(c)) for c in coord_list])




# N = 100 # magnet points
# n = 1 # data points

# #The r value, the magnitude of B, needs to be the same for B1 and B2.
# B1_spherical = [1, -np.pi/3, -np.pi/6]
# B2_spherical = [1, 7/8 * np.pi, np.pi/3]
# coord_list = rotation_between_2_vectors(B1_spherical, B2_spherical, N)

# plot_vectors_between_2_vectors(coord_list, B1_spherical, B2_spherical)