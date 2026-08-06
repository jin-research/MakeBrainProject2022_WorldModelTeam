import pickle
import cv2
import datetime
#from donkeycar.real_data_names_store import datafilename
from tqdm import tqdm
import time




class Gets_rewawd_done:
    def __init__(self):
    #        with open(datafilename, 'rb') as f:
    #            self.steerings = pickle.load(f)
    #            self.throttles = pickle.load(f)
    #            self.images = pickle.load(f)
        self.count_to_dead = 0
        self.dones = []
        self.rewards = []
        self.extention_color = 10

    def determine_episode_over(self,datafilename,steerings,throttles,images):
        # we have a few initial frames on start that are sometimes very large CTE when it's behind
        # the path just slightly. We ignore those.
        
        ### determined by a pixel percentage
        for image in images:
            over = False
            """
            r_range_1 =  ( 210 < (image[:,:,0]) )
            r_range_2 =  ( (image[:,:,0]) < 240 )
            g_range_1 =  ( 170 < (image[:,:,1]) )
            g_range_2 =  ( (image[:,:,1]) < 200 )
            b_range_1 =  ( 110 < (image[:,:,2]) )
            b_range_2 =  ( (image[:,:,2]) < 140 )
            """
            image = cv2.resize(image, dsize = (64, 64))
            #cv2.resize(image[:,:,0], dsize = (64, 64))
            #cv2.resize(image[:,:,1], dsize = (64, 64))
            #cv2.resize(image[:,:,2], dsize = (64, 64))
            r_range_1 =  ( 210 - self.extention_color < (image[:,:,0]) )
            r_range_2 =  ( (image[:,:,0]) < 240 + self.extention_color )
            g_range_1 =  ( 170 - self.extention_color < (image[:,:,1]) )
            g_range_2 =  ( (image[:,:,1]) < 200 + self.extention_color)
            b_range_1 =  ( 110 - self.extention_color < (image[:,:,2]) )
            b_range_2 =  ( (image[:,:,2]) < 140 + self.extention_color )
            pixel_range = r_range_1 * r_range_2 * g_range_1 * g_range_2 * b_range_1 * b_range_2
            pixel_range_num = pixel_range.sum()
            all_square_pixel = sum((image).shape) / 3
            dead_all_square_pixel_percentage = (pixel_range_num/all_square_pixel)*100

            # print("dead check c",self.count_to_dead)
            if dead_all_square_pixel_percentage < 0.1:
                print("dead_count: ",self.count_to_dead, dead_all_square_pixel_percentage)
                self.count_to_dead+=1
                if self.count_to_dead >= 15*2:
                    over = True
                    self.count_to_dead = 0.0
                #     for i in tqdm(range(15)):
                #       time.sleep(1)
                    print("game over! dead_all_square_pixel_percentage: ",dead_all_square_pixel_percentage)
            else:
                print("dead_all_square_pixel_percentage",dead_all_square_pixel_percentage)
                if self.count_to_dead > 5:
                    self.count_to_dead -= 5
            self.dones.append(over)

    def calc_reward(self,datafilename,steerings,throttles,images):
        # Normalization factor, real max speed is around 30
        # but only attained on a long straight line
        max_speed = 10
        
        #print("self.image_array[:,:,0]",self.image_array[:,:,0])
        for i in tqdm(range(len(throttles))):
            r_range_1 = (210 - self.extention_color<(images[i][:,:,0]))
            r_range_2 =  ( (images[i][:,:,0]) < 240+ self.extention_color )
            g_range_1 =  ( 170 - self.extention_color< (images[i][:,:,1]) )
            g_range_2 =  ( (images[i][:,:,1]) < 200+ self.extention_color )
            b_range_1 =  ( 110 - self.extention_color< (images[i][:,:,2]) )
            b_range_2 =  ( (images[i][:,:,2]) < 140+ self.extention_color )
            pixel_range = r_range_1 * r_range_2 * g_range_1 * g_range_2 * b_range_1 * b_range_2
            pixel_range_num = pixel_range.sum()
            all_square_pixel = sum((images[i]).shape) / 3
            all_square_pixel_percentage = (pixel_range_num/all_square_pixel)*100
            #print("all_square_pixel_percentage [%]",all_square_pixel_percentage)

            # print("image_array",self.image_array)

            if self.dones[i]:
                self.rewards.append(-1.0)

            #if self.cte > self.max_cte:
            #    return -1.0

            # Collision
            #if self.hit != "none":
            #    return -2.0

            # going fast close to the center of lane yields best reward
            #base_all_square_pixel_percentage = 5 #[%]
            #print("old_reward", (1.0 - (self.cte / self.max_cte) ** 2) * (self.speed / max_speed))
            #print("new_reward",( ( all_square_pixel_percentage / base_all_square_pixel_percentage )**2) * (self.speed / max_speed)

            # steering


            else:
                base_all_square_pixel_percentage = 5
                reward = ( ( all_square_pixel_percentage / base_all_square_pixel_percentage )) * ( throttles[i] / max_speed)
                #return_reward = all_square_pixel_percentage * (self.speed*3)
                #print("return_reward", return_reward)
                self.rewards.append(reward)
                #return (1.0 - (self.cte / self.max_cte) ** 2) * (self.speed / max_speed)

    def save_pickle(self,datafilename,steerings,throttles,images):
        #datafilename = "./data/" + str(datetime.datetime.now(pytz.timezone('Asia/Tokyo'))) + "5data.bin"
        with open(datafilename,"wb") as f:
            index_min = min(len(steerings), len(throttles), len(images))
            pickle.dump(steerings,f)
            pickle.dump(throttles,f)
            pickle.dump(images,f)
            pickle.dump(self.rewards, f)
            pickle.dump(self.dones,f)
            print("\n\n")
            print(datafilename," is saved")

if __name__ == '__main__':
    with open("real_data_names_store.txt") as f:
        l_strip = [s.strip() for s in f.readlines()]
    print("list from real_data_names_store.txt:\n",l_strip)

    for datafilename in l_strip:
        with open(datafilename, 'rb') as f:
            steerings = pickle.load(f)
            throttles = pickle.load(f)
            images = pickle.load(f)
        print("datafilename:\n",datafilename)
        fun = Gets_rewawd_done()
        fun.determine_episode_over(datafilename,steerings,throttles,images)
        fun.calc_reward(datafilename,steerings,throttles,images)
        fun.save_pickle(datafilename,steerings,throttles,images)
