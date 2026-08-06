#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 25 10:44:24 2017

@author: wroscoe
"""

import sys
import pprint
#print(pprint.pprint(sys.path))
#print("#####################")


#sys.path.append("/home/xiaor/mycar/donkeycar/real_data_names_store/directory")



import time
import pytz
import datetime
import csv
from csv import writer
from threading import Thread
from .memory import Memory
from .log import get_logger
#from partscamera import CSICamera
import pickle
logger = get_logger(__name__)
from donkeycar.parts.datastore_for_record import steerings_record
from donkeycar.parts.datastore_for_record import throttles_record
from donkeycar.parts.datastore_for_record import images_record
from .real_data_names_store import datafilename
import sys
sys.path.append("../")
#from gets_rewawd_done import Gets_rewawd_done
import cv2
import numpy as np

class Vehicle:
    def __init__(self, mem=None):
        if not mem:
            mem = Memory()
        self.mem = mem
        self.parts = []
        self.threads = []
        self.count_to_dead = 0
        self.extention_color = 10
        self.index_min = 0

    def add(self, part, inputs=[], outputs=[],
            threaded=False, run_condition=None):
        """
        Method to add a part to the vehicle drive loop.

        Parameters
        ----------
            inputs : list
                Channel names to get from memory.
            outputs : list
                Channel names to save to memory.
            threaded : boolean
                If a part should be run in a separate thread.
            run_condition: boolean
                If a part should be run at all.
        """

        p = part
        logger.info('Adding part {}.'.format(p.__class__.__name__))
        entry = dict()
        entry['part'] = p
        entry['inputs'] = inputs
        entry['outputs'] = outputs
        entry['run_condition'] = run_condition

        if threaded:
            t = Thread(target=part.update, args=())
            t.daemon = True
            entry['thread'] = t
        self.parts.append(entry)

    def start(self, rate_hz=10, max_loop_count=None):
        """
        Start vehicle's main drive loop.

        This is the main thread of the vehicle. It starts all the new
        threads for the threaded parts then starts an infinit loop
        that runs each part and updates the memory.

        Parameters
        ----------

        rate_hz : int
            The max frequency that the drive loop should run. The actual
            frequency may be less than this if there are many blocking parts.
        max_loop_count : int
            Maxiumum number of loops the drive loop should execute. This is
            used for testing the all the parts of the vehicle work.
        """

        try:
            self.on = True

            for entry in self.parts:
                if entry.get('thread'):
                    # start the update thread
                    entry.get('thread').start()

            # wait until the parts warm up.
            logger.info('Starting vehicle...')
            time.sleep(1)

            loop_count = 0
            while self.on:
                start_time = time.time()
                loop_count += 1

                self.update_parts()

                # stop drive loop if loop_count exceeds max_loopcount
                if max_loop_count and loop_count > max_loop_count:
                    self.on = False

                sleep_time = 1.0 / rate_hz - (time.time() - start_time)
                if sleep_time > 0.0:
                    time.sleep(sleep_time)

        except KeyboardInterrupt:
            pass
        finally:
            for i in range(5):
                print("last time:", i)
                time.sleep(1)
            print("Do not push CTRL C!!!!!!!")
            print("Do not push CTRL C!!!!!!!")
            print("Do not push CTRL C!!!!!!!")
            print("Do not push CTRL C!!!!!!!")
            print("Do not push CTRL C!!!!!!!")
            print("Do not push CTRL C!!!!!!!")
            print("Do not push CTRL C!!!!!!!")
            print("Do not push CTRL C!!!!!!!")
            print("Do not push CTRL C!!!!!!!")
            print("Do not push CTRL C!!!!!!!")
            print("Do not push CTRL C!!!!!!!")
            print("images_record",images_record)
            #datafilename = "./data/3data.bin"
            #datafilename = "./data/" + str(datetime.datetime.now(pytz.timezone('Asia/Tokyo'))) + "_data.bin"
            #f = open("real_data_names_store.txt","a")
            f= open("real_data_names_store.txt", mode='a')
            f.write("{}\n".format(datafilename))
            f.close()
            print("name saved in real_data_names_store")
            self.index_min = min(len(images_record), len(steerings_record), len(throttles_record))
            if(len(images_record) > self.index_min):
                images_record.pop()
            if(len(steerings_record) > self.index_min):
                steerings_record.pop()
            if(len(throttles_record) > self.index_min):
                throttles_record.pop()
            with open(datafilename,"wb") as f:
                print("steerings_record is being saved")
                pickle.dump(steerings_record,f)
                print("throttles_record is being saved")
                pickle.dump(throttles_record,f)
                print("images_record is being saved")
                pickle.dump(images_record,f)
                print("\n\n")
                print("############################")
                print(datafilename," is saved")
            '''pd.to_pickle(,'./data/steerings_record.pkl')
            pd.to_pickle(,'./data/throttles_record.pkl')
            pd.to_pickle(,'./data/images_.pkl')'''
            print("Gets_rewawd_done()")
            #fun = Gets_rewawd_done()
            #fun.determine_episode_over()
            #fun.calc_reward()
            print("save_pickle()")
            #fun.save_pickle()
            self.stop()
            print("> CTRL C OK")
    def determine_episode_over(self,image):
        image = cv2.resize(image, dsize = (64, 64))
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
    
        print("dead check self.count_to_dead",self.count_to_dead)
        if dead_all_square_pixel_percentage < 0.1:
            print("dead_count: ",self.count_to_dead, dead_all_square_pixel_percentage)
            self.count_to_dead+=1
            if self.count_to_dead >= 15*2:
                action=[0,0]


                self.count_to_dead = 0.0
                #self.add(action[0], inputs=['angle'])
                #self.add(, inputs=['throttle'])
                for i in range(15):
                    print("dead!!!!!")
                    print("moving wait time: ",15-i)
                    time.sleep(1)

                print("dead! dead_all_square_pixel_percentage: ",dead_all_square_pixel_percentage)
        else:
            print("dead_all_square_pixel_percentage",dead_all_square_pixel_percentage)
            if self.count_to_dead > 5:
                self.count_to_dead -= 5

    def update_parts(self):
        """
        loop over all parts
        """
        for entry in self.parts:
            # don't run if there is a run condition that is False
            run = True
            if entry.get('run_condition'):
                run_condition = entry.get('run_condition')
                run = self.mem.get([run_condition])[0]
                # print('run_condition', entry['part'], entry.get('run_condition'), run)

            if run:
                p = entry['part']
                # get inputs from memory
                inputs = self.mem.get(entry['inputs'])

                # run the part
                if entry.get('thread'):
                    outputs = p.run_threaded(*inputs)
                    #print("p",p)
                    #print("outputs",outputs)
                    images_record.append(outputs)
                    self.determine_episode_over(outputs)
                else:
                    outputs = p.run(*inputs)

                # save the output to memory
                if outputs is not None:
                    self.mem.put(entry['outputs'], outputs)

    def stop(self):
        logger.info('Shutting down vehicle and its parts...')
        for entry in self.parts:
            try:
                entry['part'].shutdown()
            except Exception as e:
                logger.debug(e)
