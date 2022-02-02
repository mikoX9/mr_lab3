import json
from matplotlib import pyplot as plt
import math
import numpy as np
import random
from numpy.polynomial.polynomial import polyfit


DATA_NUM = 512

def polar_to_cart_point(theta, value):
    if not math.isinf(value) and not math.isnan(value): 
        x = value*math.cos(theta)
        y = value*math.sin(theta)
        return x, y 
    else:
        return 0, 0

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
    angle = 0
    r = 0
    x = 0
    y = 0
    number = 0
    used = False

    def __init__(self, angle, r, number) -> None:
        self.angle = angle
        self.r = r
        self.number = number
        self.add_cartesian()

    def was_used(self):
        self.usef = True

    def add_cartesian(self):
        self.x, self.y = polar_to_cart_point(self.angle, self.r)
    

def unassigned_data_exist(points_list):
    for point in points_list:
        if not point.used:
            return True
    return False

def max_x_list_of_points(points_list):
    final_point = None
    for point in points_list:
        if final_point == None:
            final_point = point
        if point.x > final_point.x:
            final_point = point
    return final_point

def min_x_list_of_points(points_list):
    final_point = None
    for point in points_list:
        if final_point == None:
            final_point = point
        if point.x < final_point.x:
            final_point = point
    return final_point

def take_unused_points(points_list):
    unused_points = list()
    for point in points_list:
        if point.used == False:
            unused_points.append(point)
    return unused_points

def plot_points(points, args='o'):
    x = [point.x for point in points]
    y = [point.y for point in points]
    plt.plot(x, y, args)

def plot_walls(walls):

    for wall in walls:
        line_x = np.linspace(wall.min_x, wall.max_x, 2)
        line_y = wall.par_a*line_x + wall.par_b
        plt.plot(line_x, line_y, 'r' ,linewidth = 3)
    plt.show()


def ransac(points):
    N = 30
    D = 0.1 # angle of section
    S = 10
    I = 0
    X = 0.1 # error in values
    C = 30 # numbers of samples fitted in error margin
    C_proc = 0.9 # numbers of samples fitted in error margin but in precentage

    walls = list()

    while unassigned_data_exist(points) and I<N:
        points = take_unused_points(points)
        rand_point = random.choice(points)
        points_in_section = [point for point in points if point.angle>rand_point.angle-D and point.angle<rand_point.angle+D]
        if len(points_in_section) < S:
            continue
        rand_points_from_section = random.sample(points_in_section, S)
        
        # if list is not empty        
        if rand_points_from_section:

            ### test plot of data to regression
            plot_points(rand_points_from_section)
            # plt.show()
            #############
            
            x = [point.x for point in rand_points_from_section]
            y = [point.y for point in rand_points_from_section]
            
            b, a = polyfit(x, y, 1) # a*x+b 
            
            ### test plot of regression
            line_x = np.linspace( min_x_list_of_points(rand_points_from_section).x , max_x_list_of_points(rand_points_from_section).x, 10)
            line_y = a*line_x+b
            plt.plot(line_x, line_y)

            upper_line_y = a*line_x+ b + X
            lower_line_y = a*line_x+ b - X
            plt.fill_between(line_x, upper_line_y, lower_line_y, color='grey', alpha=0.1)


            ##############

            # sub_list_cartesian = polar_to_cart_one_list(sub_list)
            
            ### test plot of data within section
            plot_points(points_in_section)
            # sub_list_x = [point.x for point in points_in_section]
            # sub_list_y = [point.y for point in points_in_section]
            # plt.plot(sub_list_x, sub_list_y, 'o')
            ##############

            # how many samples are in the distance smaller then X form the line
            fitted_count = 0
            for point in points_in_section:
                if point.y < ((a*point.x+b)  + X) and point.y > ((a*point.x+b) - X):
                    fitted_count += 1
            
            print(f"Number of fitted samples: {fitted_count}")
            points_in_section_size = len(points_in_section)
            if fitted_count/points_in_section_size > C_proc:
                # recaluclate regression for all samples 
                x = [point.x for point in points_in_section]
                y = [point.y for point in points_in_section]

                real_b, real_a = polyfit(x, y, 1) 

                walls.append(Wall(real_a, real_b, max(x), min(x)))
                
                # mark used in points list
                for point in points_in_section:
                    point.used = True

            plt.clf() # clean plot

        I+=1

    return walls

        
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



    points = list()
    for i, p in enumerate(zip(theta, data)):
        if not math.isinf(p[1]) and not math.isnan(p[1]):
           points.append( Point(p[0], p[1], i))
    org_points = points

    walls = ransac(points)
    plot_points(org_points, args="x")
    print(f"Number of walls: {len(walls)}")
    plot_walls(walls)


    pass