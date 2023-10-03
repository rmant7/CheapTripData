from pathlib import Path
import json


partly_folder = Path('/home/andrii/code/projects/CheapTripData/Java/target/output/output_02_10_23/partly')
direct_routes_path = Path('/home/andrii/code/projects/CheapTripData/Java/target/output/output_02_10_23/direct_routes.json')
partly_adapted_folder = Path('/home/andrii/code/projects/CheapTripData/Java/target/output/output_02_10_23/partly_adapted')


# direct_routes is apart because it`s a bit more complicated to adapt than other types of routes (other_routes_adapt())
def direct_routes_adapt():
    try:
        save_folder = Path(f'{partly_adapted_folder}/direct_routes')
        save_folder.mkdir(parents=True, exist_ok=True)
        
        with open(direct_routes_path, 'r') as f:
            direct_routes = json.load(f)
            
        ids = set(value['from'] for value in direct_routes.values())
        
    except Exception as err:
        print(f'''\n{type(err).__name__}: {err}
               while opening input file: {direct_routes_path} or making save folder: {save_folder}''')
        
    for id in ids:
        try:
            # adaptation ******************
            adapted = {key: value for key, value in direct_routes.items() if value['from'] == id}
            adapted = {key: {k: v for k, v in value.items() if k != 'from'} for key, value in adapted.items()}
            # *****************************
            
            file_path = Path(f'{save_folder}/{id}.json')
            with open(file_path, 'w', ) as f:
                json.dump(adapted, f)
            
        except Exception as err:
            print(f'\n{type(err).__name__}: {err} while processing city with id={id}')
            continue 
    
    print('\tdirect_routes adaptation......SUCCESS!')          
    
            
def other_routes_adapt():
    try:
        partly_folders = [folder for folder in partly_folder.rglob('*') 
                        if folder.is_dir() and not folder.name.startswith('direct')]
    except Exception as err:
        print(f'{type(err).__name__}: {err} while processing input folder: {partly_folder}')
       
    for folder in partly_folders:
        try:
            adapted_folder = Path(partly_adapted_folder/folder.name)
            adapted_folder.mkdir(parents=True, exist_ok=True)
            
            for file in folder.glob('*.json'):
                with open(file, 'r') as f:
                    adapted = json.load(f)
                
                # adaptation ***********    
                for value in adapted.values():
                    value['direct_routes'] = value['direct_routes'].split(',')
                # **********************
                    
                with open(adapted_folder/file.name, 'w') as f:
                    json.dump(adapted, f)
        
            print(f'\t{folder.name} adaptation......SUCCESS!')
                    
        except Exception as err:
            print(f'{type(err).__name__}: {err} while processing file {file.name} in folder {folder.name}')
            continue           
                

if __name__ == '__main__':
    try:
        partly_adapted_folder.mkdir(parents=True, exist_ok=True)
        print('Adaptation started...')
        direct_routes_adapt()
        other_routes_adapt()
        print('Adaptation finished......SUCCESSFULLY')
    except Exception as err:
        print(f'{type(err).__name__}: {err} while making save folder {partly_adapted_folder}')