import asyncio
from datetime import datetime, timedelta
from utils.methods import get_names_from_link
from utils.post_methods import add_task_facebook
from utils.config import config

page_name = 'CheapTrip. Pay less, visit more.'
# page_name = 'Chiptriptest'


async def main():
    url = 'http://20.240.63.21/files/posts/city_attractions/ru/'

    json_files = await get_names_from_link(url)

    post_date = datetime.strptime('06/15/2023, 14:30:00', '%m/%d/%Y, %H:%M:%S')

    for name in json_files:
        print(f'{json_files.index(name)}/{len(json_files)}')
        task = await add_task_facebook(post_path=url + name, post_date=post_date,
                                       page_name=page_name,
                                       acc_token=config.fb_token.get_secret_value())
        if task:
            post_date = post_date + timedelta(hours=1)
            await asyncio.sleep(1)
        else:
            continue
    await asyncio.sleep(100000)


if __name__ == "__main__":
    asyncio.run(main())
