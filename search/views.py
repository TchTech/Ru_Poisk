from django.shortcuts import render
from django.http import HttpResponse
from .rucrawler import crawler
import sys
from .rank_methods.ru_rank import bm25_rank, ru_rank
from .rank_methods.dummy_rank import dummy_rank
from .rank_manager import RankManager
import re, requests
from bs4 import BeautifulSoup
import enum
#from .fast_rank import fast_rank
from pyaspeller import YandexSpeller

speller = YandexSpeller()

def index(request):
  return render(request,"search.html")

class Page:
  text : str
  title : str
  rank : float
  description : str
  link : str
  def __init__(self, text, title, rank, link):
     self.text = text
     self.title = title
     self.rank = round(rank, 2)
     self.link = link
     self.description = re.sub('&lt;/?[a-z]+&gt;', '', text[0:50] + "...")

class RankMethod(enum.Enum):
    Semantic = 1
    Accurate = 2
    BM_25 = 3

class SitemapMethod(enum.Enum):
    AutoParse = 1
    FindXML = 2

def xml_sitemapper(query : str, links : list, depth : int):
  links = links[:depth]
  texts_dict = dict()
  for link in links:
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    data = requests.get(link, headers=headers).text
    text = BeautifulSoup(data, features="lxml").get_text().replace("\n", " ").replace("\t", " ")
    texts_dict[link] = data[data.find('<title>') : data.find('</title>')+8] + " " + text
  return dict(sorted(texts_dict.items(), key=lambda item: item[1], reverse=True))

def dicts_to_objects(sorted_ranks_and_links : dict, texts_and_links : dict)->list[Page]:
  result = []
  for link in sorted_ranks_and_links.keys():
    text = texts_and_links[link]
    title = re.sub('&lt;/?[a-z]+&gt;', '', text[text.find('<title>') + 7 : text.find('</title>')])
    rank = sorted_ranks_and_links[link]
    result.append(Page(text, title, rank, link))
  return result

def results_found(request):
    if '--iocp' in sys.argv:
        from asyncio import events, windows_events
        sys.argv.remove('--iocp')
        el = windows_events.ProactorEventLoop()
        events.set_event_loop(el)
    link = request.GET.get("link")
    query = request.GET.get("query")
    if link == "" or query == "":
      return render(request, "search.html")
    fixed = speller.spelled(query)
    depth = request.COOKIES.get("depth")
    rank_method_enum = request.COOKIES.get("rank_method")
    sitemap_method_enum = request.COOKIES.get("sitemap_method")
    if depth == None  or depth==0: depth = 30
    depth = int(depth)
    if rank_method_enum == None: rank_method_enum = RankMethod.Semantic.value
    rank_method_enum = int(rank_method_enum)
    if sitemap_method_enum == None: sitemap_method_enum = SitemapMethod.AutoParse.value
    sitemap_method_enum = int(sitemap_method_enum)
    if sitemap_method_enum == SitemapMethod.AutoParse.value:
      exclude_urls = []
      include_urls = [link]
      texts_and_links = crawler(include_urls=include_urls, query=query, max_links=depth, need_texts=True)[0]
    else:
      links = get_xml_sitemap(link)
      texts_and_links = xml_sitemapper(query, links, depth)

    if texts_and_links == {}:
      return render(request,"search.html", {"query":query, "fixed": fixed})

    rank_mngr = RankManager()
    if rank_method_enum == RankMethod.Semantic.value:
      rank_mngr.add_method(ru_rank)
    elif rank_method_enum == RankMethod.BM_25.value:
      rank_mngr.add_method(bm25_rank)
    else:
      rank_mngr.add_method(dummy_rank)
    links_and_ranks = rank_mngr.rank(query, texts_and_links)
    sorted_ranks_and_links = dict(sorted(links_and_ranks.items(), key=lambda item: item[1], reverse=True))
    pages = dicts_to_objects(sorted_ranks_and_links=sorted_ranks_and_links, texts_and_links=texts_and_links)
    return render(request,"search.html", {"results": pages, "query":query, "fixed": fixed})


def clear_url(url : str):
  return re.search(r'^http[s]*:\/\/[\w\.]*', url).group()

def get_xml_sitemap(url : str):
  headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
  domain = clear_url(url)
  try:
    sitemap = requests.get(domain+"/sitemap.xml", headers=headers).text
  except:
    return []
  soup = BeautifulSoup(sitemap)
  links_arr = []
  for link in soup.findAll('loc'):
      linkstr = link.getText('', True)
      if linkstr.split(".")[-1] == "xml":
        new_sitemap = get_xml_sitemap(linkstr)
        links_arr = links_arr + new_sitemap
      else:
        links_arr.append(linkstr)

  return links_arr

# print(get_xml_sitemap("https://www.educba.com/sitemap_index.xml"))