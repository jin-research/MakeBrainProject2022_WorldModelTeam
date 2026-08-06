class make_env():
    def __init__():
        self.exe_path = f"/home/pbl/sim3.7.0/DonkeySimLinux/donkey_sim.x86_64"
        self.port = 9091
        self.conf = { "exe_path" : exe_path, "port" : port, "cam_resolution": [64,64,3], "max_cte": 5.0}
        self.env = GeneratedRoadsEnv(conf = conf)

#def make_env():
#    exe_path = f"/home/pbl/sim3.7.0/DonkeySimLinux/donkey_sim.x86_64"
#    port = 9091
#    conf = { "exe_path" : exe_path, "port" : port, "cam_resolution": [64,64,3], "max_cte": 5.0}
#    env = GeneratedRoadsEnv(conf = conf)

#    return env
