from pathlib import Path

NOT_FOUND = -1

# set up inputs
INPUT_CSV_DIR = Path('../files/csv')
AIRPORT_CODES_CSV = Path(INPUT_CSV_DIR/'airport_codes.csv')
IATA_CODES_CSV = Path('../files/airports/iata_codes.csv')
BBOXES_CSV = Path(INPUT_CSV_DIR/'bounding_boxes.csv')
CITIES_COUNTRIES_CSV = Path(INPUT_CSV_DIR/'cities_countries.csv')
INPUT_JSONS_DIR = Path('../files/json')

# setup outputs
OUTPUT_IMAGES_DIR = Path('../output/images')

# logging set up 
LOGS_DIR = Path('../logs')
LOG_CRITICAL = Path(LOGS_DIR/'critical_errors.log')
LOG_CRITICAL_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

# prompts folder setup
PROMPTS_DIR = Path('../prompts')

# lists directory setup
OPTION_LISTS_DIR = Path('../cities_data/option_lists')
CITY_ATTRACTIONS_LIST_DIR = Path(OPTION_LISTS_DIR/'city_attractions')
CHILDREN_ATTRACTIONS_LIST_DIR = Path(OPTION_LISTS_DIR/'children_attractions')

# SEO folders setup
SEO_TEXTS_DIR = Path('../cities_data/seo/texts')
SEO_HTMLS_DIR = Path('../cities_data/seo/htmls')
SEO_CITY_DESCRIPTIONS_DIR = Path(SEO_TEXTS_DIR/'city_descriptions/en_old')
SEO_CITY_ATTRACTIONS_DIR = Path(SEO_TEXTS_DIR/'city_attractions/en')
SEO_CITY_ATTRACTIONS_BENGALI = Path(SEO_TEXTS_DIR/'city_attractions_bengali')
SEO_CHILDREN_ATTRACTIONS_DIR = Path(SEO_TEXTS_DIR/'children_attractions/en')
SEO_ACCOMODATIONS_DIR = Path(SEO_TEXTS_DIR/'accomodations_seo')
SEO_TRANSPORTATIONS_DIR = Path(SEO_TEXTS_DIR/'transportations_seo')
SEO_FESTIVALS_DIR = Path(SEO_TEXTS_DIR/'events_festivals_seo')

# SMM folders setup
SMM_TEXTS_DIR = Path('../cities_data/smm')
SMM_POSTS_DIR = Path('../cities_data/smm/posts')
SMM_CITY_ATTRACTIONS_FP_DIR = Path(SMM_TEXTS_DIR/'city_attractions_first_person_fixed/en')

# image directories setup
PEXEL_IMG_DIR = Path('../cities_data/images/pexel')
CHILDREN_ATTRACTIONS_IMG_DIR = Path('../cities_data/images/children_attractions')
CITY_ATTRACTIONS_IMG_DIR = Path('/home/andrii/code/projects/CheapTripData/ContentAutomator/Contentio/GPT/cities_data/images/Landmark_of_the_cities')