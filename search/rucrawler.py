import asyncio
import re
import urllib.parse
import aiohttp
import sys
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    stream=sys.stdout)

class Crawler:

    def __init__(self, rooturl, maxtasks=100,
                 todo_queue_backend=set, done_backend=dict, need_texts = False, query="", max_links=10):
        self.rooturl = rooturl
        self.todo_queue = todo_queue_backend()
        self.busy = set()
        self.done = done_backend()
        self.tasks = set()
        self.sem = asyncio.Semaphore(maxtasks)
        self.session = None  # Сессия создается позже
        self.texts = dict()
        self.need_texts = need_texts
        self.query = query
        self.max_links = max_links
        self.exclude_urls = [] # Initialize exclude_urls
    def set_exclude_url(self, urls_list):
        self.exclude_urls = urls_list

    async def run(self):
        """Запускает обход для одного root_url."""
        logging.info(f"Запуск обхода для {self.rooturl}")
        t = asyncio.ensure_future(self.addurls([(self.rooturl, '')]))
        await asyncio.sleep(0.5)  # Даем время запуститься addurls
        while self.busy:
            await asyncio.sleep(0.5)

        await t
        if self.need_texts:
            return self.texts
        else:
            return self.done

    async def addurls(self, urls):
        for url, parenturl in urls:
            url = urllib.parse.urljoin(parenturl, url)
            url, frag = urllib.parse.urldefrag(url)
            if (url.startswith(self.rooturl) and
                    not any(exclude_part in url for exclude_part in self.exclude_urls) and
                    url not in self.busy and
                    url not in self.done and
                    url not in self.todo_queue and
                    len(self.done)<self.max_links):
                self.todo_queue.add(url)

                await self.sem.acquire()

                task = asyncio.ensure_future(self.process(url))

                task.add_done_callback(lambda t: self.sem.release())

                task.add_done_callback(self.tasks.remove)

                self.tasks.add(task)

    async def process(self, url):
        self.todo_queue.remove(url)
        self.busy.add(url)

        try:
            resp = await self.session.get(url)
        except Exception as exc:
            logging.warning(f"...{url} has error {repr(str(exc))}")
            self.done[url] = False
        else:
            if (resp.status == 200 and
                    ('text/html' in resp.headers.get('content-type', ''))):
                try:
                    data = (await resp.read()).decode('utf-8', 'replace')

                    if self.need_texts:
                        soup = BeautifulSoup(data, features="lxml")
                        text = soup.get_text().replace("\n", " ").replace("\t", " ")
                        title_start = data.find('<title>')
                        title_end = data.find('</title>')
                        title = data[title_start:title_end+8] if title_start != -1 and title_end != -1 else ""
                        self.texts[url] = title + " " + text

                    urls = re.findall(r'(?i)href=["\']?([^\s"\'<>]+)', data)
                    asyncio.create_task(self.addurls([(u, url) for u in urls]))  # Use create_task

                except Exception as e:
                    logging.exception(f"Ошибка при обработке HTML {url}: {e}")
            resp.close()
            self.done[url] = True
        self.busy.remove(url)

def crawler(maxtasks=25, exclude_urls=None, include_urls=[], need_texts = False, query="", max_links = 10):
    """Обходит несколько root_url в одном цикле событий."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError as e:
        if str(e).startswith('There is no current event loop in thread'):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        else:
            raise
    results = []
    try:
        async def run_crawlers():
            """Запускает несколько обходчиков."""
            async with aiohttp.ClientSession() as session: # Создаем ClientSession здесь
                tasks = []
                for root_url in include_urls:
                    c = Crawler(root_url, maxtasks=maxtasks, need_texts=need_texts, query=query, max_links=max_links)
                    c.session = session  # Передаем общую сессию
                    if exclude_urls:
                        c.set_exclude_url(urls_list=exclude_urls)
                    tasks.append(c.run()) # Добавляем корутину c.run() в список tasks
                return await asyncio.gather(*tasks)  # Запускаем все задачи параллельно и ждем их завершения

        results = loop.run_until_complete(run_crawlers())
    except KeyboardInterrupt: # Обрабатываем Ctrl+C
        logging.info("Получен сигнал прерывания. Завершаем работу...")
    finally:
        #loop.run_until_complete(asyncio.sleep(0.1)) # Даем задачам время завершиться
        #tasks = asyncio.all_tasks(loop)
        #for task in tasks:
        #    task.cancel()
        #loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
        #loop.stop()  # Это, вероятно, не нужно
        loop.close() # Закрываем цикл событий
        logging.info("Цикл событий закрыт.")
    return results