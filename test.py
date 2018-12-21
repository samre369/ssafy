# -*- coding: utf-8 -*-
import json
import os
import re
import urllib.request

from bs4 import BeautifulSoup
from slackclient import SlackClient
from flask import Flask, request, make_response, render_template

app = Flask(__name__)

slack_token = "xoxb-502651382259-507434822195-GJFrqI805bEnecxwy9fv5naI"
slack_client_id = "502651382259.508590230295"
slack_client_secret = "a641fd477807139e9cb57cb89181921d"
slack_verification = "ZO5YabK0Cs9R7cDtigftG4fS"
sc = SlackClient(slack_token)


# 크롤링 함수 구현하기
def _crawl_naver_keywords(text):


    urllist =[]

    urllist1 = ['%ED%86%A0%ED%8A%B8%EB%84%98','%EC%95%84%EC%8A%A4%EB%84%90','%EB%A6%AC%EB%B2%84%ED%92%80','%EB%A7%A8%EC%B2%B4%EC%8A%A4%ED%84%B0+%EC%8B%9C%ED%8B%B0','%EC%B2%BC%EC%8B%9C','=%EC%B2%BC%EC%8B%9C','EB%A7%A8%EC%B2%B4%EC%8A%A4%ED%84%B0+%EC%9C%A0%EB%82%98%EC%9D%B4%ED%8B%B0%EB%93%9C',"%EC%97%90%EB%B2%84%ED%84%B4","%EC%9B%A8%EC%8A%A4%ED%8A%B8%ED%96%84","%EC%99%93%ED%8F%AC%EB%93%9C","%EB%B3%B8%EB%A8%B8%EC%8A%A4","%EB%A0%88%EC%8A%A4%ED%84%B0","%EB%B8%8C%EB%9D%BC%EC%9D%B4%ED%8A%BC","%EB%89%B4%EC%BA%90%EC%8A%AC","%ED%81%AC%EB%A6%AC%EC%8A%A4%ED%83%88+%ED%8C%B0%EB%A6%AC%EC%8A%A4","%EC%B9%B4%EB%94%94%ED%94%84","%EC%82%AC%EC%9A%B0%EC%83%98%ED%94%84%ED%84%B4","%EB%B2%88%EB%A6%AC","%ED%97%88%EB%8D%94%EC%A6%88%ED%95%84%EB%93%9C","%ED%92%80%EB%9F%BC"]


# 토트넘
# 아스널
# 리버풀
# 맨체스터시티
# 첼시
# 맨체스터 유나이티드
# 울버 햄튼
# 에버턴
# 웨스트햄
# 왓포드
# 본머스
# 레스터
# 브라이튼
# 뉴캐슬
# 크리스탈 팰리스
# 카디프 시티
# 사우샘프턴
# 번리
# 허더즈 필드
# 풀럼

    teamlist = ["토트넘","아스널","리버풀","맨체스터 시티","첼시","맨체스터 유나이티드","울버햄튼","에버턴","웨스트햄","왓포드","본머스","레스터","브라이튼","뉴캐슬","크리스탈 팰리스","카디프 시티","사우샘프턴","번리","하더즈 필드","풀럼"]

    for j in range(0,19):
        if teamlist[j] in text:
            print (teamlist[j]+"정보 입니다")
            urlname = "https://search.naver.com/search.naver?sm=top_hty&fbm=1&ie=utf8&query=" + urllist1[j]
            break

    print(urlname)
    soup = BeautifulSoup(urllib.request.urlopen(urlname).read(), "html.parser")


    teams = []
    dfcontent = []
    contents = soup.select("div.tmp_area > table > tbody.tb_club > tr")

    # print(soup.find("div" ,{"id" : "Match_Table"}))
    for content in contents:
        tds = content.find_all("td")
        for td in tds:
            dfcontent.append(td.text)
        dict = {
            "date" : dfcontent[0],
            "time" : dfcontent[1],
            "score" : dfcontent[2],
            "league" : dfcontent[3]
         }

        dfcontent = []
        teams.append(dict)

    print(teams)


    printstr = "  날짜 및 시간  " + "   경기 결과   " + " 리그    \n"
    for i in range(len(teams)):
        date = teams[i]["date"]
        time = teams[i]["time"]
        score = teams[i]["score"]
        league = teams[i]["league"]
        printstr  = printstr + date + " / " + time + " / " + score + " / " + league + " \n"
    print(printstr)

    keywords = printstr

    return u''.join(keywords)

    # # 여기에 함수를 구현해봅시다.


# 이벤트 핸들하는 함수
def _event_handler(event_type, slack_event):
    print(slack_event["event"])

    if event_type == "app_mention":
        channel = slack_event["event"]["channel"]
        text = slack_event["event"]["text"]

        keywords = _crawl_naver_keywords(text)
        sc.api_call(
            "chat.postMessage",
            channel=channel,
            text=keywords
        )

        return make_response("App mention message has been sent", 200, )

    # ============= Event Type Not Found! ============= #
    # If the event_type does not have a handler
    message = "You have not added an event handler for the %s" % event_type
    # Return a helpful error message
    return make_response(message, 200, {"X-Slack-No-Retry": 1})


@app.route("/listening", methods=["GET", "POST"])
def hears():
    slack_event = json.loads(request.data)

    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type":
                                                                 "application/json"
                                                             })

    if slack_verification != slack_event.get("token"):
        message = "Invalid Slack verification token: %s" % (slack_event["token"])
        make_response(message, 403, {"X-Slack-No-Retry": 1})

    if "event" in slack_event:
        event_type = slack_event["event"]["type"]
        return _event_handler(event_type, slack_event)

    # If our bot hears things that are not events we've subscribed to,
    # send a quirky but helpful error response
    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                         you're looking for.", 404, {"X-Slack-No-Retry": 1})


@app.route("/", methods=["GET"])
def index():
    return "<h1>Server is ready.</h1>"


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000)
