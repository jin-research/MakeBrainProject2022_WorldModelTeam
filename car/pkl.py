import pickle
import cv2
import numpy as np
import os
from tqdm import tqdm

images = []
with open("real_data_names_store.txt") as f:
    l_strip = [s.strip() for s in f.readlines()]


print("list from real_data_names_store.txt:\n",l_strip)

for filedataname in l_strip:
    print("filedataname:\n",filedataname)

    with open(filedataname, mode="rb") as f:
        steerings_record = pickle.load(f)
        throttles_record = pickle.load(f)
        images_record = pickle.load(f)
        #rewards = pickle.load(f)
        #dones = pickle.load(f)
    print("steerings_record\n",len(steerings_record))
    print("throttles_record\n",len(throttles_record))
    print("images_record\n",len(images_record))
    #print("rewards\n",len(rewards))
    #print("dones\n",len(dones))
    #print(images_record[-1])



    #cv2.imshow("srtdd", images_record[-1])

    #images_record = np.array(images_record)
    '''
    print("images_record.shape",images_record.shape)
    for i in range(255):
        print((images_record[-1])[i][:])
    '''
    save_image_datafilename = "image_data_"+filedataname
    os.makedirs(save_image_datafilename, exist_ok=True)
    print("n rewards throttles_record")
    for n, epi in tqdm(enumerate(range(500))):
        image=images_record[epi].astype(np.float32)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        images.append(image)
        #images.append(images_record[epi])
        cv2.imwrite("{}/real_env{}.png".format(save_image_datafilename, epi),images[epi])
        #print("n rewards throttles_record")
        #print(n, rewards[epi], throttles_record[epi])
    
    
    '''
    for epi in range(len(rewards)):
        print(steerings_record[epi])
        print(throttles_record[epi])
        print(images_record[epi+1])
        print(rewards[epi])
        print(dones[epi])
    '''
