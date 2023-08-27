import json
from pathlib import Path
from data_provider import CSVDataProvider
from datetime import datetime
from logger import logger_setup
import functions
from config import PROMPTS_DIR, SEO_TEXTS_DIR


dp = CSVDataProvider()
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
logger = logger_setup(f'{Path(__file__).stem}_{timestamp}')


@functions.elapsed_time
def gen_content():
    category = 'accomodations'
    base_url = f'http://20.240.63.21/files/images/{category}'
    save_dir = Path(f'{SEO_TEXTS_DIR}/{category}/en')
    save_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f'Making output dir...SUCCESSFULLY')
    prompts = functions.get_prompts_GPT(f'{PROMPTS_DIR}/{category}_pmt.json')
    logger.info(f'Getting prompts...SUCCESSFULLY')
    j = 1
    for city, country in dp.gen_data(from_=135, to_=145):
        logger.info(f'Processing {city}, {country} started...')
        city_ = city.replace(' ', '_').replace('-', '_')
        # getting option list for the given city
        try:
            accomodations = functions.load_json(f'{SEO_TEXTS_DIR}/{category}/en_copy/{city_}.json')
            processed_accomodations = functions.load_json(f'{SEO_TEXTS_DIR}/{category}/en/{city_}.json')
            logger.info(f'Category options loading...SUCCESS')
        except Exception as err:
            logger.error(f'{type(err).__name__}: {err} while getting options. Continue to process with next city')
            continue
        # looping over the options
        data = dict()
        for key in accomodations.keys():
            data[key] = dict()
            name = accomodations[key]['name']
            text = accomodations[key]['description']
            if key in processed_accomodations.keys(): 
                meta = processed_accomodations[key]['meta']
                keywords = processed_accomodations[key]['keywords']
                title = processed_accomodations[key]['title']
                links = processed_accomodations[key]['links']
                images = processed_accomodations[key]['images']
            else:
                logger.info(f'Starting process for "{key}.{name}"...')
                # composing prompt for the given option
                prompt = prompts['meta_keywords_links'].format(text=text)
                # getting response from ChatGPT
                try:
                    response = functions.get_response_GPT(prompt)
                    logger.info(f'Generating response for "{key}.{name}"...SUCCESS')
                    parsed = json.loads(response)
                    logger.info(f'Parsing response for "{key}.{name}"...SUCCESS')
                    meta = parsed['meta']
                    keywords = parsed['keywords']
                    title = parsed['title']
                    links = [link for link in parsed['links'] if functions.is_valid_link(link)]
                    logger.info(f'Validation links...SUCCESS')
                except Exception as err:
                    logger.error(f'{type(err).__name__}: {err} while getting ChatGPT response. Continue to process with next option')
                    del data[key]
                    continue
                prompt = prompts['images'].format(option=name, text=text)
                try:
                    url = functions.get_images_DALLE(prompt)
                    logger.info(f'Generating image of option "{key}.{name}"...SUCCESS')
                    img_name = functions.download_image(url[0], category, city, key, name)
                    images = [f'{base_url}/{city_}/{img_name}']
                    logger.info(f'Saving image of option "{key}.{name}"...SUCCESS')
                except Exception as err:
                    logger.error(f'{type(err).__name__}: {err} while generating or downloading image. Continue to process with next option')
                    del data[key]
                    continue
            # Compose a data[key] subdict
            data[key] = {'name': name,
                        'location': f'{city}, {country}',
                        'meta': meta,
                        'keywords': keywords,
                        'title': title,
                        'text': text,
                        'links': links,
                        'images': images
            }
            logger.info(f'Adding option "{key}.{name}"...SUCCESS')
        # avoid to save empty data dict
        if not data: continue
        # saving data dict to json
        with open(Path(f'{save_dir}/{city_}.json'), 'w') as fp:
            json.dump(data, fp, indent=4)
        logger.info(f'Processing {city}, {country} completed SUCCESSFULLY. Total score {j}/{dp.get_numrows()}')
        j += 1        
    

if __name__ == '__main__':
    gen_content()