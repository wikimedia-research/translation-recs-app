import os
import argparse
import json


"""
python mk_data_dirs.py \ 
--translation_directions ../served_translation_directions.json
"""



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--translation_directions', required = False, default = '../served_translation_directions.json', help='path to json file defining language directions' )
    parser.add_argument('--data_dir', required = False, default = '../data', help='data dir' )
    args = parser.parse_args()   
    with open(args.translation_directions) as f:
        t_dict = json.load(f)

    for s in t_dict.keys():
        for s in t_dict.keys():
            directory = os.path.join(args.data_dir, s)
            if not os.path.exists(directory):
                os.makedirs(directory)
            for t in t_dict[s]:
                directory = os.path.join(args.data_dir, s, t)
                if not os.path.exists(directory):
                    os.makedirs(directory)


if __name__ == '__main__':
    main()