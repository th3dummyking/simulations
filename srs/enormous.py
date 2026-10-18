import time
front_d=["     _________ ",
         "    /    |    \  ",
         "    \ _     _ / ",
         "     |       | ",
         "     |       | ",
         "     |       | ",
         "    _|       |_",
         "   /     Y     \ ",
         "   \_____/\____/  "        
]

back_d= ["     _________ ",
         "    /  _____  \   ",
         "    \ /     \ /   ",
         "     |       |   ",
         "     |       | ",
         "     |       | ",
         "    _|       |_",
         "   /           \ ",
         "   \_____/\____/  "  
]
side_r =["       _______ ",
         "      /        \   ",
         "     /     \__ /    ",
         "     |       |   ",
         "     |       |",
         "     |       | ",
         "     |       |_",
         "     \      Y   \ ",
         "      \_____/___/  " 
]

side_l =["    _______ ",
         "   /        \   ",
         "   \_ _/     \          ",
         "     |       |   ",
         "     |       |",
         "     |       | ",
         "    _|       |",
         "   /   Y     \ ",
         "   \___\_____/  " 
]


running = True
phase = [front_d, side_r, back_d, side_l]
chose = 0
last_s = time.time()
timer = 0.5

def chose_num (current):
    return (current +1) % len(phase) 

frame = 0

try:
    while running:
        t = time.time()
        frame += 1
        if t -  last_s >= timer:
            print("\033[H\033[J", end="")

            chose = chose_num(chose)
            last_s = t
        
            for i in range(len(front_d)):
                print (phase[chose][i])
except KeyboardInterrupt:
    print ("enormous pe e e nis")