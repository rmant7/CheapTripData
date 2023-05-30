import polars as pl
from urllib.parse import urlparse, urlencode
import json
import time

from logger import logger_setup
import openai, os

from config import NOT_FOUND, CITIES_COUNTRIES_CSV


logger = logger_setup()

# set up all dataframes
df_cities_countries = pl.read_csv(CITIES_COUNTRIES_CSV)

   
def get_cities():
    return sorted(df_cities_countries['city'])

   
def get_city_name(id):
    return df_cities_countries.filter(pl.col('id_city') == id)['city'][0]
    
    
def get_city_id(name):
    try:
        return df_cities_countries.filter(pl.col('city') == name)['id_city'][0]
    except:
        return NOT_FOUND

    
def get_prompts_GPT(prompt_json: str) -> dict:
    with open(prompt_json, 'r') as file:
        return json.load(file)
    

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
                result = func(*args, **kwargs)
            except Exception as error:
                # An exception was raised, trigger a delay and recursive function call with the same parameter
                print(f'\nDuring request there was an error: {error}')
                # time.sleep(60)
                # return wrapper(*args, **kwargs)
                
            calls.append(time.time())
            print('\n',result)
            
            return result
        return wrapper
    return decorator
    
  
@limit_calls_per_minute(3)    
def get_response_GPT(prompt: str, api_key: str):
    openai.organization = os.getenv('OPENAI_ID_CT')
    openai.api_key = os.getenv(api_key)
    
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                            messages=[
                                                        #{"role": "system", "content": f"Act as an {role}"},
                                                        {"role": "user", "content": prompt}
                                                    ],
                                            temperature=0
                                            )   
    
    return response['choices'][0]['message']['content']
     

@limit_calls_per_minute(5)    
def get_images_DALLE(prompt, n, size, api_key):
    openai.organization = os.getenv('OPENAI_ID_CT')
    openai.api_key = os.getenv(api_key)
    
    response = openai.Image.create(
                                    prompt=prompt,
                                    n=n,
                                    size=size
    )
    return [item['url'] for item in response['data']]
    
    
if __name__ == '__main__':
    print(get_cities())
    pass