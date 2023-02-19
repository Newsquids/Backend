from crawler import Crawl, main
from datetime import datetime
import asyncio

start = datetime.now()
asyncio.run(main())
print(f'{start} 크롤링 시작')
print(f'{datetime.now()} 크롤링 종료')