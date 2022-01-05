import json
from matplotlib import pyplot as plt
import math
import numpy as np
import random
from numpy.polynomial.polynomial import polyfit


DATA_NUM = 512

def polar_to_cart(thetas, values):
    xs = list()
    ys = list()
    for i in zip(thetas, values):
        if not math.isinf(i[1]) and not math.isnan(i[1]): 
            xs.append( i[1]*math.cos(i[0]) )
            ys.append( i[1]*math.sin(i[0]) )
    return xs, ys

def polar_to_cart_one_list(pol_coors):
    final_list = list()
    for i in pol_coors:
        if not math.isinf(i[1]) and not math.isnan(i[1]): 
            x = i[1]*math.cos(i[0]) 
            y = i[1]*math.sin(i[0]) 
            final_list.append((x,y))
    return final_list

def zero_in_list(l):
    for i in l:
        if i == 0:
            return True
    return False


class Wall:
    def __init__(self, par_a, par_b, max_x, min_x) -> None:
        self.par_a = par_a
        self.par_b = par_b
        self.max_x = max_x
        self.min_x = min_x

class Point:
    def __init__(self) -> None:
        pass

    angle = 0
    r = 0
    x = 0
    y = 0
    number = 0
    used = False


if __name__ == "__main__":        

    f = open('box.json')
    data = json.load(f)
    f.close()

    x = np.arange(0,DATA_NUM)
    theta = (np.pi/DATA_NUM )*x  # theta - scan angles in [rad]

    # fig1 = plt.figure()
    # #plotting in polar coordinates  
    # ax1 = fig1.add_axes([0.1,0.1,0.8,0.8],polar=True) 
    # line, = ax1.plot(theta,data,'o',lw=1.5)
    # #setting range limits
    # ax1.set_ylim(0,5)  
    # # plt.show()

    # x_s, y_s = polar_to_cart(theta, data)




    # RANSAC for line segments 
    # parameters:
    #  N, D, S, X, C
    # while exist unassigned samples and iteration is smaller than N
    #   choose a random angle r
    #   select randomly S samples from angle [r-D,r+D] as Rs
    #   fit the best line to set Rs (linear regression, least square method)
    #   determine how many samples are in distance smaller than X from the line
    #   if the number of matching samples is bigger than C
    #    for all samples matching the line recalculate line parameters
    #    add the line to the result
    #    remove samples fitting to the line from unassigned set



    pol_data = list()
    pol_data = [(i[0],i[1], 0) for i in zip(theta, data)]




    N = 5

    D = 0.2 # angle of section

    S = 10
    I = 0

    X = 0.1 # error in values
    C = 50 # numbers of samples fitted in error margin


    assigned_data = [0] * DATA_NUM
    walls = list()

    while zero_in_list(assigned_data) and I<N:
        rand_angle = random.choice(theta)
        sub_list = [i for i in pol_data if i[0]>rand_angle-D and i[0]<rand_angle+D]
        # sub_list_cartesian = polar_to_cart_one_list(sub_list)
        rand_list = random.sample(sub_list, S)
        rand_list_cartesian = polar_to_cart_one_list(rand_list)

        # if list is not empty        
        if rand_list_cartesian:

            x = [i[0] for i in rand_list_cartesian]
            y = [i[1] for i in rand_list_cartesian]
            
            ### test plot of data to regression
            plt.plot(x, y, 'o')
            plt.show()
            #############
            
            b, a = polyfit(x, y, 1) # a*x+b 
            
            ### test plot of regression
            line_x = np.linspace(min(rand_list_cartesian)[0], max(rand_list_cartesian)[0], 10)
            line_y = a*line_x+b
            plt.plot(line_x, line_y)

            upper_line_y = a*line_x+ b + X
            lower_line_y = a*line_x+ b - X
            plt.fill_between(line_x, upper_line_y, lower_line_y, color='grey', alpha=0.1)


            ##############

            sub_list_cartesian = polar_to_cart_one_list(sub_list)
            
            ### test plot of data within section
            sub_list_x = [i[0] for i in sub_list_cartesian]
            sub_list_y = [i[1] for i in sub_list_cartesian]
            plt.plot(sub_list_x, sub_list_y, 'o')
            ##############

            # how many samples are in the distance smaller then X form the line
            fitted_count = 0
            for i in sub_list_cartesian:
                if i[1] < ((a*i[0]+b)  + X) and i[1] > ((a*i[0]+b) - X):
                    fitted_count += 1
            
            print(f"Number of fitted samples: {fitted_count}")
            if fitted_count > C:
                # recaluclate regression for all samples 
                x = [i[0] for i in sub_list_cartesian]
                y = [i[1] for i in sub_list_cartesian]
                real_b, real_a = polyfit(x, y, 1) 

                walls.append(Wall(real_a, real_b, max(x), min(x)))


                for i in pol_data: # tu zamienic na polar
                    if i[0] in x: # tu sprawdzać w polar
                        i[2] = 1            
            plt.clf() # clean plot

        I+=1



