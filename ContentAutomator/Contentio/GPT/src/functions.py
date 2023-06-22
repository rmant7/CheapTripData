import polars as pl
import json
import time
import openai
import os
from pathlib import Path
from PIL import Image
import requests


from config import NOT_FOUND, CITIES_COUNTRIES_CSV, IMG_DIR


# set up all dataframes
df_cities_countries = pl.read_csv(CITIES_COUNTRIES_CSV)

   
def get_cities(from_: int=0, to_: int=df_cities_countries.shape[0]) -> list:
    """
    Returns sorted list of the cities. Parameters:'from_' and 'to_' define a list slice.
    """
    cities = sorted(df_cities_countries['city'])
    return cities[from_:to_]


def get_cities_countries(from_: int=0, to_: int=df_cities_countries.shape[0]) -> list:
    """
    Returns sorted list of the cities and countries. Parameters:'from_' and 'to_' define a list slice.
    """
    cities_countries = df_cities_countries[['city', 'country']].sort('city')
    return cities_countries[from_:to_].rows()

   
def get_city_name(id):
    return df_cities_countries.filter(pl.col('id_city') == id)['city'][0]
    
    
def get_city_id(name):
    try:
        return df_cities_countries.filter(pl.col('city') == name)['id_city'][0]
    except Exception:
        return NOT_FOUND


def correct_image_names():
    rep = {"'":"", ".":"", "__":"_"}
    for file in Path(f'{IMG_DIR}/city_attractions').rglob('*.jpg'):
        new_stem = file.stem
        for key, value in rep.items():
            if key in file.stem:
                new_stem = new_stem.replace(key, value)
        file.rename(file.with_stem(new_stem))


def resize_images(folder_path: Path | str, to_size: tuple=(1024, 1024)) -> None:
    if isinstance(folder_path, str):
        folder_path = Path(folder_path)
    try:
        for file_path in folder_path.rglob('*.jpeg'):
            print(file_path)
            try:
                img = Image.open(file_path)
                if img.size == to_size:
                    print(f"Skipping {file_path.name} (already {to_size}.")
                else:
                    img = img.resize(to_size, Image.ANTIALIAS)
                    img.save(file_path)
                    print(f"Resized {file_path.name} successfully.")
            except Exception as e:
                print(f"Error resizing {file_path.name}: {str(e)}")
    except StopIteration as err:
        print(err)
    except Exception as err:
        print(f'\n It was something wrong with {file_path}: {err}')
        

def resize_image(file_path: Path | str, to_size: tuple=(1024, 1024)) -> None:
    try:
        img = Image.open(file_path)
        if img.size == to_size:
            print(f"Skipping {file_path.name} (already {to_size}.")
        else:
            img = img.resize(to_size, Image.ANTIALIAS)
            img.save(file_path)
            print(f"Resized {file_path.name} to {to_size} successfully.")
    except Exception as e:
        print(f"Error resizing {file_path.name}: {str(e)}")


def is_valid_link(url: str, timeout: int=10) -> bool:
    try:
        requests.head(url, timeout=timeout, allow_redirects=False).raise_for_status()
        return True
    except requests.exceptions.RequestException as err:
        print("An error occurred during the request:", err)
        return False


def get_prompts_GPT(prompt_json_path: Path | str) -> dict:
    with open(prompt_json_path, 'r') as f:
        return json.load(f)
    

def limit_calls_per_minute(max_calls):
    """
    Decorator that limits a function to being called `max_calls` times per minute,
    with a delay between subsequent calls calculated based on the time since the
    previous call.
    """
    calls = []
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Remove any calls from the call history that are older than 1 minute
            
            calls[:] = [call for call in calls if call > time.time() - 60]
            if len(calls) >= max_calls:
                # Too many calls in the last minute, calculate delay before allowing additional calls
                time_since_previous_call = time.time() - calls[-1]
                delay_seconds = 60 / max_calls - time_since_previous_call
                if delay_seconds > 0:
                    time.sleep(delay_seconds)
            # Call the function and add the current time to the call history
            try:
                # print('\n', args[0])
                result = func(*args, **kwargs)
            except openai.OpenAIError as err:
                print("An error occurred during the OpenAI request:", err)
                result = None
                # An exception was raised, trigger a delay and recursive function call with the same parameter
                # time.sleep(60)
                # return wrapper(*args, **kwargs)
            finally:    
                calls.append(time.time())
                print('\n',result)
                return result
        return wrapper
    return decorator
    
  
@limit_calls_per_minute(3)    
def get_response_GPT(prompt: str, api_key: str='OPENAI_API_KEY_CT_2'):
    openai.organization = os.getenv('OPENAI_ID_CT')
    openai.api_key = os.getenv(api_key)
    response = openai.ChatCompletion.create(model='gpt-3.5-turbo',
                                            messages=[
                                                        #{"role": "system", "content": f"Act as an {role}"},
                                                        {'role': 'user', 'content': prompt}
                                                    ],
                                            temperature=0)   
    return response['choices'][0]['message']['content']
     

@limit_calls_per_minute(3)    
def get_images_DALLE(prompt: str, n: int=1, size: str='512x512', api_key: str='OPENAI_API_KEY_CT_2') -> list:
    openai.organization = os.getenv('OPENAI_ID_CT')
    openai.api_key = os.getenv(api_key)
    response = openai.Image.create(
                                    prompt=prompt,
                                    n=n,
                                    size=size)
    return [item['url'] for item in response['data']]
    

def elapsed_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed = end_time - start_time
        elapsed_minutes = int(elapsed // 60)
        elapsed_seconds = int(elapsed % 60)
        elapsed_hours = int(elapsed_minutes // 60)
        elapsed_minutes %= 60
        print(f'Elapsed time for {func.__name__}: {elapsed_hours} hours, '
                f'{elapsed_minutes} minutes, {elapsed_seconds} seconds')
        return result
    return wrapper

    
if __name__ == '__main__':
    print(get_cities_countries(), type(get_cities_countries()))
    # print(get_cities())
    pass