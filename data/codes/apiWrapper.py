# coding:utf-8
# 
import urllib2
import urllib
import pickle
import xml.dom.minidom
import json

def auction_title(auctionIDlist,outstr,option='a'):
    '''オークションのタイトルを取る関数
    入力はauctionIDlist：オークションIDのリスト　outstr：書き出すファイルの名前　option：書き出すのオプション、デフォルトは追加、新しいのを作りたい場合はwに
    タイトルだけではなく他のものを取り出したい場合はtitle = jobject[u'ResultSet'][u'Result'][u'Title']に適当に変形すればよい
    使用例としては下のsearch_auctionをまず利用してIDのリストを取り、そのリストをauction_titleに渡してタイトルをとる'''
    f2=open(outstr,option)
    for index in xrange(len(auctionIDlist)):
        print index
        aucres=api_goods(auctionIDlist[index],output='json').get_response()
        if aucres == None:
            break
        page = aucres.read()
        #print page
        jobject=json.loads(page[7:-1],encoding="cp932")
        #jobject=json.load(aucres)
        try:
            title = jobject[u'ResultSet'][u'Result'][u'Title']
            line=auctionIDlist[index] + " , " +title + "\n"
            f2.write(line)
        except KeyError as e:
            print e
    f2.close()



def Auction_data(auctionIDlist,outstr,option='a'):
    '''オークションの詳細リストをファイルに書き出す関数：
	入力はauctionIDlist：オークションIDのリスト　outstr：書き出すファイルの名前　option：書き出すのオプション、デフォルトは追加、新しいのを作りたい場合はwに
	htmlタグなどがエラーになるため"Description"タグを削除した、ほかに"ResultSet"と'?xml'も削除
	今はxmlにしたがデータベースなどを考えるとあとにjsonに変更する可能性ある'''
    if type(auctionIDlist) != list:
        auctionIDlist=[auctionIDlist]

    f2=open(auctionIDlist,option)
    for index in xrange(len(auctionIDlist)):
        print index
        aucres=api_goods(auctionIDlist[index],output='xml').get_response()
        if aucres == None:
            continue
        line=aucres.readline()
        while line != "":
            if "ResultSet" in line or "Description" in line or '?xml' in line: 
                pass
            else:
                f2.write(line)
            line=aucres.readline()
    f2.close()



def search_auction(catagoryID,pages=5,tagName='AuctionID'):
    '''特定のcatagoryIDの商品を検索し、そのcatagoryの商品の特定のフィルドを返す（デフォルト）はAuctionIDのリストを返す
	入力はcatagoryID：catagoryのID　pages：何ページまで検索、デフォルトは５　tagName：catagoryの商品の特定のフィルドを指定、デフォルトはAuctionID'''
    result=[]
    for i in xrange(1,pages+1,1):
        category1=api_search(catagoryID,page=i)
        if category1==None:
            break

        res=category1.get_response()
        doms = xml.dom.minidom.parse(res)
        for dom in doms.getElementsByTagName(tagName):
            result += [dom.childNodes[0].data]
    return result




def save_object(savething,text_name,option='w'):
    '''ある特定のオブジェクトをテキストファイルに保存'''
    f = open(text_name, option)
    pickle.dump(savething, f)
    f.close()
    print 'save successfully!'

def load_object(text_name):
    '''テキストファイルに保存したオブジェクトをロード'''
    f1=open(text_name)
    l = pickle.load(f1)
    f1.close()
    return l



'''API問い合わせクラスの定義'''
class yahoo_api(object):

    def __init__(self):
        self.params={}
        self.url=''

    def code_para(self):
        return urllib.urlencode(self.params)

    def get_response(self):
        codedpara=self.code_para()
        req = urllib2.Request(self.url,data=codedpara)
        try:
            response = urllib2.urlopen(req)
            return response
        except urllib2.HTTPError, e:
            print 'The server couldn\'t fulfill the request.'
            print 'Error code: ', e.code
            return None
        except urllib2.URLError, e:
            print 'We failed to reach a server.'
            print 'Reason: ', e.reason
            return None


class api_history(yahoo_api):
    def __init__(self,aucID,num_page=1,output='xml'):
        self.url='http://auctions.yahooapis.jp/AuctionWebService/V1/BidHistoryDetail'
        self.params={
            'auctionID':aucID,
            'appid':'dj0zaiZpPXlvZHVobmUxRmJoViZzPWNvbnN1bWVyc2VjcmV0Jng9ZDk-',
            'output':output,
            'page':num_page
            }

class api_goods(yahoo_api):
    def __init__(self,aucID,output='json'):
        self.url='http://auctions.yahooapis.jp/AuctionWebService/V2/auctionItem'
        self.params={
            'auctionID':aucID,
            'appid':'dj0zaiZpPXlvZHVobmUxRmJoViZzPWNvbnN1bWVyc2VjcmV0Jng9ZDk-',
            'output':output
            }

class api_search(yahoo_api):
    def __init__(self,categoryID,page=1,output='xml'):
        self.url='http://auctions.yahooapis.jp/AuctionWebService/V2/categoryLeaf'
        self.params={
            'category':categoryID,
            'appid':'dj0zaiZpPXlvZHVobmUxRmJoViZzPWNvbnN1bWVyc2VjcmV0Jng9ZDk-',
            'output':output,
            'page':page,
            'ranking':'popular',
            'sort' : 'bids',
            'order' : 'd'
            }
