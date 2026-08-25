"""为 Big Muzzy 各单元创建"课程模块"种子数据(幂等,可重复执行)。

用法(在 WSL /home/xsq/happy-learning 下):
    python3 scripts/seed_courses.py

配置说明(课时 content.steps 各步骤类型):
    story       {"type":"story","title","text","emoji"}            中文故事开场
    learn       {"type":"learn","title","words":[...],"cn":{词:中文}}  词卡学习
    listen_tap  {"type":"listen_tap","title","words":[...],"count"}   听音选图
    look_choose {"type":"look_choose","title","words":[...],"count"}  看图选词
    sentence    {"type":"sentence","title","sentences":[{text,cn,word}]} 句子跟读

sentence 的 word 字段用于取配图:需是 vocab_words 里存在的词/短语(如 "I love you.")。
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database import SessionLocal, Base, engine
from app.models import Course, CourseLesson, CourseProgress

TEXTBOOK_ID = 3  # Big Muzzy


# ---------- 单元课程配置 ----------

def unit1_course():
    people = ["king", "queen", "princess", "gardener"]
    greetings = ["morning", "afternoon", "evening", "night"]
    all_words = people + greetings
    return {
        "unit_id": 18,
        "title": "Big Muzzy · 认识人物和问候",
        "description": "跟着 Muzzy 认识冈多兰王国的人物,学会用英语打招呼。零基础友好,点一点、听一听、选一选,边玩边学。",
        "cover_emoji": "🐻",
        "order": 1,
        "lessons": [
            {
                "title": "认识国王一家",
                "subtitle": "人物单词:国王、王后、公主、园丁",
                "steps": [
                    {
                        "type": "story",
                        "title": "故事开场",
                        "emoji": "👑",
                        "text": "欢迎来到冈多兰(Gondoland)王国!\n国王、王后、公主和园丁都在等着认识你。\n点一点卡片,听听他们怎么介绍自己。",
                    },
                    {
                        "type": "learn",
                        "title": "学一学:认识人物",
                        "words": people,
                        "cn": {"king": "国王", "queen": "王后", "princess": "公主", "gardener": "园丁"},
                    },
                    {"type": "listen_tap", "title": "听一听,点一点", "words": people, "count": 4},
                    {"type": "look_choose", "title": "看一看,选一选", "words": people, "count": 4},
                ],
            },
            {
                "title": "问候的时间",
                "subtitle": "单词:早上、下午、晚上、夜里",
                "steps": [
                    {
                        "type": "story",
                        "title": "故事开场",
                        "emoji": "🌅",
                        "text": "一天有四个时间段:早上、下午、晚上和夜里。\n不同时间见面,要说出不同的问候语哦!\n听一听,学一学。",
                    },
                    {
                        "type": "learn",
                        "title": "学一学:时间问候",
                        "words": greetings,
                        "cn": {"morning": "早上", "afternoon": "下午", "evening": "晚上", "night": "夜里"},
                    },
                    {"type": "listen_tap", "title": "听一听,点一点", "words": greetings, "count": 4},
                    {"type": "look_choose", "title": "看一看,选一选", "words": greetings, "count": 4},
                    {
                        "type": "sentence",
                        "title": "句子跟读",
                        "sentences": [
                            {"text": "Good morning.", "cn": "早上好。", "word": "morning"},
                            {"text": "Good night.", "cn": "晚安。", "word": "night"},
                        ],
                    },
                ],
            },
            {
                "title": "综合小挑战",
                "subtitle": "混合闯关:8 个单词 + 2 个句子",
                "steps": [
                    {
                        "type": "story",
                        "title": "挑战开始",
                        "emoji": "⭐",
                        "text": "现在把今天学的单词和句子都拿出来挑战一下吧!\n每答对一题,就能得到一颗星星哦!\n准备好了吗?出发!",
                    },
                    {"type": "listen_tap", "title": "听一听,点一点", "words": all_words, "count": 6},
                    {"type": "look_choose", "title": "看一看,选一选", "words": all_words, "count": 6},
                    {
                        "type": "sentence",
                        "title": "句子跟读",
                        "sentences": [
                            {"text": "I'm the King of Gondoland.", "cn": "我是冈多兰王国的国王。", "word": "king"},
                            {"text": "Good morning.", "cn": "早上好。", "word": "morning"},
                        ],
                    },
                ],
            },
        ],
    }


def unit2_course():
    numbers = ["eleven", "twelve", "thirteen", "fourteen", "fifteen",
               "sixteen", "seventeen", "eighteen", "nineteen", "twenty"]
    feelings = ["hungry", "lovely", "delicious", "horrible", "up", "down"]
    countries = ["France", "Britain", "Germany", "Italy", "Greece", "Japan"]
    things = ["cat", "clocks", "bell", "spaceship", "typewriter", "parking meter"]
    return {
        "unit_id": 19,
        "title": "Big Muzzy · 数字、感觉和国家",
        "description": "跟着 Muzzy 学会数 11-20、表达自己的感觉、认识世界国家,还能用英语提问。零基础友好,边玩边学。",
        "cover_emoji": "🔢",
        "order": 2,
        "lessons": [
            {
                "title": "数字大作战",
                "subtitle": "数字 11-20",
                "steps": [
                    {
                        "type": "story",
                        "title": "故事开场",
                        "emoji": "🔢",
                        "text": "Muzzy 一口气吃掉了十九个停车计时器!\n今天我们来学数字 11 到 20。\n数一数,听一听,开始吧!",
                    },
                    {
                        "type": "learn",
                        "title": "学一学:数字 11-20",
                        "words": numbers,
                        "cn": {"eleven": "十一", "twelve": "十二", "thirteen": "十三", "fourteen": "十四",
                               "fifteen": "十五", "sixteen": "十六", "seventeen": "十七", "eighteen": "十八",
                               "nineteen": "十九", "twenty": "二十"},
                    },
                    {"type": "listen_tap", "title": "听一听,点一点", "words": numbers, "count": 6},
                    {"type": "look_choose", "title": "看一看,选一选", "words": numbers, "count": 6},
                ],
            },
            {
                "title": "我感觉…",
                "subtitle": "形容词:饿、可爱、美味、可怕、上、下",
                "steps": [
                    {
                        "type": "story",
                        "title": "故事开场",
                        "emoji": "😋",
                        "text": "Muzzy 总是很饿(hungry)!\n吃了好吃的东西会开心,吃到难吃的会皱眉头。\n学一学形容感觉和味道的词。",
                    },
                    {
                        "type": "learn",
                        "title": "学一学:感觉形容词",
                        "words": feelings,
                        "cn": {"hungry": "饿的", "lovely": "可爱的", "delicious": "美味的",
                               "horrible": "可怕的", "up": "上面", "down": "下面"},
                    },
                    {"type": "listen_tap", "title": "听一听,点一点", "words": feelings, "count": 5},
                    {"type": "look_choose", "title": "看一看,选一选", "words": feelings, "count": 5},
                    {
                        "type": "sentence",
                        "title": "句子跟读",
                        "sentences": [
                            {"text": "I'm hungry.", "cn": "我饿了。", "word": "hungry"},
                            {"text": "I love you.", "cn": "我爱你。", "word": "I love you."},
                        ],
                    },
                ],
            },
            {
                "title": "国家你好",
                "subtitle": "国家:法国、英国、德国、意大利、希腊、日本",
                "steps": [
                    {
                        "type": "story",
                        "title": "故事开场",
                        "emoji": "🌍",
                        "text": "Muzzy 来自天上,大家好奇地问:\n\"你来自哪里?\"\n今天学一学世界各国的英文名字。",
                    },
                    {
                        "type": "learn",
                        "title": "学一学:国家名称",
                        "words": countries,
                        "cn": {"France": "法国", "Britain": "英国", "Germany": "德国",
                               "Italy": "意大利", "Greece": "希腊", "Japan": "日本"},
                    },
                    {"type": "listen_tap", "title": "听一听,点一点", "words": countries, "count": 5},
                    {"type": "look_choose", "title": "看一看,选一选", "words": countries, "count": 5},
                    {
                        "type": "sentence",
                        "title": "句子跟读",
                        "sentences": [
                            {"text": "Where do you come from?", "cn": "你来自哪里?", "word": "Where do you come from?"},
                            {"text": "What's your name?", "cn": "你叫什么名字?", "word": "What's your name?"},
                        ],
                    },
                ],
            },
            {
                "title": "这是什么?",
                "subtitle": "物品:猫、钟表、铃铛、飞船、打字机、停车计时器",
                "steps": [
                    {
                        "type": "story",
                        "title": "故事开场",
                        "emoji": "🔔",
                        "text": "Muzzy 偷偷收集了好多有趣的东西!\n有钟表、铃铛,还有宇宙飞船……\n学一学这些物品的名字,再问问\"这是什么?\"",
                    },
                    {
                        "type": "learn",
                        "title": "学一学:物品名称",
                        "words": things,
                        "cn": {"cat": "猫", "clocks": "钟表", "bell": "铃铛",
                               "spaceship": "宇宙飞船", "typewriter": "打字机", "parking meter": "停车计时器"},
                    },
                    {"type": "listen_tap", "title": "听一听,点一点", "words": things, "count": 5},
                    {"type": "look_choose", "title": "看一看,选一选", "words": things, "count": 5},
                    {
                        "type": "sentence",
                        "title": "句子跟读",
                        "sentences": [
                            {"text": "What's this?", "cn": "这是什么?", "word": "What's this?"},
                            {"text": "I like clocks.", "cn": "我喜欢钟表。", "word": "I like clocks."},
                        ],
                    },
                ],
            },
        ],
    }


def unit3_course():
    body = ["a head", "an eye", "a nose", "a mouth", "an ear", "a neck", "a hand", "a leg"]
    feelings = ["thirsty", "hot", "cold", "tired", "wet", "dry"]
    colors = ["green", "red", "yellow", "brown", "blue", "black", "white"]
    actions = ["run", "walk", "jump", "swim", "listen", "talk"]
    return {
        "unit_id": 20,
        "title": "Big Muzzy · 身体、感觉和颜色",
        "description": "认识身体部位,学会说渴了热了冷了累了,再认识七种颜色和六个动作动词。零基础友好,边玩边学。",
        "cover_emoji": "🧍",
        "order": 3,
        "lessons": [
            {
                "title": "我的身体",
                "subtitle": "身体部位:头、眼睛、鼻子、嘴巴、耳朵、脖子、手、腿",
                "steps": [
                    {
                        "type": "story",
                        "title": "故事开场",
                        "emoji": "🪞",
                        "text": "照照镜子,看看自己:\n头、眼睛、鼻子、嘴巴、耳朵……\n今天来认识我们身体各部分的英文名字!",
                    },
                    {
                        "type": "learn",
                        "title": "学一学:身体部位",
                        "words": body,
                        "cn": {"a head": "头", "an eye": "眼睛", "a nose": "鼻子", "a mouth": "嘴巴",
                               "an ear": "耳朵", "a neck": "脖子", "a hand": "手", "a leg": "腿"},
                    },
                    {"type": "listen_tap", "title": "听一听,点一点", "words": body, "count": 6},
                    {"type": "look_choose", "title": "看一看,选一选", "words": body, "count": 6},
                    {
                        "type": "sentence",
                        "title": "句子跟读",
                        "sentences": [
                            {"text": "Can you see me?", "cn": "你能看见我吗?", "word": "Can you see me?"},
                        ],
                    },
                ],
            },
            {
                "title": "我感觉…",
                "subtitle": "感觉:渴、热、冷、累、湿、干",
                "steps": [
                    {
                        "type": "story",
                        "title": "故事开场",
                        "emoji": "💧",
                        "text": "渴了想喝水,热了想洗个澡,累了想休息……\n学一学怎么用英语说自己的感觉。",
                    },
                    {
                        "type": "learn",
                        "title": "学一学:感觉形容词",
                        "words": feelings,
                        "cn": {"thirsty": "口渴的", "hot": "热的", "cold": "冷的",
                               "tired": "累的", "wet": "湿的", "dry": "干的"},
                    },
                    {"type": "listen_tap", "title": "听一听,点一点", "words": feelings, "count": 5},
                    {"type": "look_choose", "title": "看一看,选一选", "words": feelings, "count": 5},
                    {
                        "type": "sentence",
                        "title": "句子跟读",
                        "sentences": [
                            {"text": "I am thirsty.", "cn": "我渴了。", "word": "thirsty"},
                            {"text": "It's hot.", "cn": "好热呀。", "word": "hot"},
                        ],
                    },
                ],
            },
            {
                "title": "五颜六色",
                "subtitle": "颜色:绿、红、黄、棕、蓝、黑、白",
                "steps": [
                    {
                        "type": "story",
                        "title": "故事开场",
                        "emoji": "🌈",
                        "text": "彩虹有七种颜色!\n红橙黄绿蓝靛紫……今天学学颜色的英文,看看你认识几种?",
                    },
                    {
                        "type": "learn",
                        "title": "学一学:颜色",
                        "words": colors,
                        "cn": {"green": "绿色", "red": "红色", "yellow": "黄色", "brown": "棕色",
                               "blue": "蓝色", "black": "黑色", "white": "白色"},
                    },
                    {"type": "listen_tap", "title": "听一听,点一点", "words": colors, "count": 6},
                    {"type": "look_choose", "title": "看一看,选一选", "words": colors, "count": 6},
                    {
                        "type": "sentence",
                        "title": "句子跟读",
                        "sentences": [
                            {"text": "That's right.", "cn": "说得对!", "word": "That's right."},
                        ],
                    },
                ],
            },
            {
                "title": "动起来",
                "subtitle": "动作:跑、走、跳、游泳、听、说话",
                "steps": [
                    {
                        "type": "story",
                        "title": "故事开场",
                        "emoji": "🏃",
                        "text": "跑一跑、跳一跳、游一游……\n学一学这些动作的英文,再跟着爸爸妈妈做动作!",
                    },
                    {
                        "type": "learn",
                        "title": "学一学:动作动词",
                        "words": actions,
                        "cn": {"run": "跑", "walk": "走", "jump": "跳",
                               "swim": "游泳", "listen": "听", "talk": "说话"},
                    },
                    {"type": "listen_tap", "title": "听一听,点一点", "words": actions, "count": 5},
                    {"type": "look_choose", "title": "看一看,选一选", "words": actions, "count": 5},
                    {
                        "type": "sentence",
                        "title": "句子跟读",
                        "sentences": [
                            {"text": "Let me try again.", "cn": "让我再试一次。", "word": "Let me try again."},
                        ],
                    },
                ],
            },
        ],
    }


def unit4_course():
    daily = ["have breakfast", "have lunch", "take a bath", "go to bed", "lunch-time"]
    sick = ["doctor", "headache", "stomachache", "toothache", "backache", "feeling better"]
    sports = ["swimming", "tennis", "the swimming pool", "tennis court", "rain", "time", "quick"]
    return {
        "unit_id": 21,
        "title": "Big Muzzy · 我的一天",
        "description": "从早餐到睡觉,从生病看医生到游泳打网球,学会用英语描述一天的生活。零基础友好,边玩边学。",
        "cover_emoji": "⏰",
        "order": 4,
        "lessons": [
            {
                "title": "我的一天",
                "subtitle": "作息:吃早餐、吃午餐、洗澡、上床睡觉",
                "steps": [
                    {
                        "type": "story",
                        "title": "故事开场",
                        "emoji": "🍳",
                        "text": "早上吃早餐,中午吃午餐,晚上洗澡睡觉……\nMuzzy 的一天是怎么过的?\n跟着学一学吧!",
                    },
                    {
                        "type": "learn",
                        "title": "学一学:一天的作息",
                        "words": daily,
                        "cn": {"have breakfast": "吃早餐", "have lunch": "吃午餐",
                               "take a bath": "洗澡", "go to bed": "上床睡觉", "lunch-time": "午餐时间"},
                    },
                    {"type": "listen_tap", "title": "听一听,点一点", "words": daily, "count": 4},
                    {"type": "look_choose", "title": "看一看,选一选", "words": daily, "count": 4},
                    {
                        "type": "sentence",
                        "title": "句子跟读",
                        "sentences": [
                            {"text": "It’s eight o’clock.", "cn": "八点钟了。", "word": "It’s eight o’clock."},
                            {"text": "I’m busy.", "cn": "我很忙。", "word": "I’m busy."},
                        ],
                    },
                ],
            },
            {
                "title": "生病了",
                "subtitle": "看医生:头痛、肚子疼、牙疼、背疼",
                "steps": [
                    {
                        "type": "story",
                        "title": "故事开场",
                        "emoji": "🤒",
                        "text": "哎呀,不舒服了!\n头痛、肚子疼、牙疼……\n去看医生,学一学这些症状怎么说。",
                    },
                    {
                        "type": "learn",
                        "title": "学一学:生病看医生",
                        "words": sick,
                        "cn": {"doctor": "医生", "headache": "头痛", "stomachache": "肚子疼",
                               "toothache": "牙疼", "backache": "背疼", "feeling better": "感觉好多了"},
                    },
                    {"type": "listen_tap", "title": "听一听,点一点", "words": sick, "count": 5},
                    {"type": "look_choose", "title": "看一看,选一选", "words": sick, "count": 5},
                    {
                        "type": "sentence",
                        "title": "句子跟读",
                        "sentences": [
                            {"text": "I’ve got a terrible headache.", "cn": "我头疼得厉害。", "word": "I’ve got a terrible headache."},
                            {"text": "Sylvia isn’t very well.", "cn": "西尔维娅不太舒服。", "word": "Sylvia isn’t very well."},
                        ],
                    },
                ],
            },
            {
                "title": "游泳和网球",
                "subtitle": "运动:游泳、网球、游泳池、网球场、下雨、时间、快",
                "steps": [
                    {
                        "type": "story",
                        "title": "故事开场",
                        "emoji": "🏊",
                        "text": "下雨天也要运动!\n去游泳池游泳,去网球场打网球……\n学一学运动场地和时间天气的说法。",
                    },
                    {
                        "type": "learn",
                        "title": "学一学:运动与天气",
                        "words": sports,
                        "cn": {"swimming": "游泳", "tennis": "网球", "the swimming pool": "游泳池",
                               "tennis court": "网球场", "rain": "下雨", "time": "时间", "quick": "快的"},
                    },
                    {"type": "listen_tap", "title": "听一听,点一点", "words": sports, "count": 6},
                    {"type": "look_choose", "title": "看一看,选一选", "words": sports, "count": 6},
                    {
                        "type": "sentence",
                        "title": "句子跟读",
                        "sentences": [
                            {"text": "It’s raining.", "cn": "下雨了。", "word": "It’s raining."},
                            {"text": "What’s the time now?", "cn": "现在几点了?", "word": "What’s the time now?"},
                        ],
                    },
                ],
            },
        ],
    }


def unit5_course():
    seasons = ["spring", "summer", "autumn", "winter", "dark", "tall", "short"]
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    months = ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]
    sports_rooms = ["play soccer", "play basketball", "roller-skating", "golf",
                    "kitchen", "bathroom", "hall", "sitting room"]
    return {
        "unit_id": 22,
        "title": "Big Muzzy · 四季、月份和星期",
        "description": "认识春夏秋冬、12 个月份和 7 个星期,学会运动项目和房间的说法。零基础友好,边玩边学。",
        "cover_emoji": "📅",
        "order": 5,
        "lessons": [
            {
                "title": "春夏秋冬",
                "subtitle": "四季:春、夏、秋、冬;高、矮、暗",
                "steps": [
                    {
                        "type": "story",
                        "title": "故事开场",
                        "emoji": "🍂",
                        "text": "一年有四个季节:\n春天开花,夏天游泳,秋天落叶,冬天堆雪人。\n学一学四季的英文吧!",
                    },
                    {
                        "type": "learn",
                        "title": "学一学:四季",
                        "words": seasons,
                        "cn": {"spring": "春天", "summer": "夏天", "autumn": "秋天", "winter": "冬天",
                               "dark": "黑暗的", "tall": "高的", "short": "矮的"},
                    },
                    {"type": "listen_tap", "title": "听一听,点一点", "words": seasons, "count": 6},
                    {"type": "look_choose", "title": "看一看,选一选", "words": seasons, "count": 6},
                    {
                        "type": "sentence",
                        "title": "句子跟读",
                        "sentences": [
                            {"text": "I'm frightened.", "cn": "我好害怕。", "word": "frightened"},
                        ],
                    },
                ],
            },
            {
                "title": "星期歌",
                "subtitle": "星期:周一至周日",
                "steps": [
                    {
                        "type": "story",
                        "title": "故事开场",
                        "emoji": "🗓️",
                        "text": "一周有七天:\n星期一到星期日。\n跟着唱一唱、点一点,记住每一天的名字!",
                    },
                    {
                        "type": "learn",
                        "title": "学一学:星期",
                        "words": weekdays,
                        "cn": {"Monday": "星期一", "Tuesday": "星期二", "Wednesday": "星期三", "Thursday": "星期四",
                               "Friday": "星期五", "Saturday": "星期六", "Sunday": "星期日"},
                    },
                    {"type": "listen_tap", "title": "听一听,点一点", "words": weekdays, "count": 6},
                    {"type": "look_choose", "title": "看一看,选一选", "words": weekdays, "count": 6},
                    {
                        "type": "sentence",
                        "title": "句子跟读",
                        "sentences": [
                            {"text": "It's dinner-time.", "cn": "该吃晚饭了。", "word": "dinner-time"},
                        ],
                    },
                ],
            },
            {
                "title": "月份大挑战",
                "subtitle": "月份:一月到十二月",
                "steps": [
                    {
                        "type": "story",
                        "title": "故事开场",
                        "emoji": "🎂",
                        "text": "一年有 12 个月:\n一月、二月、三月……十二月。\n你的生日在几月?学完记得告诉爸爸妈妈!",
                    },
                    {
                        "type": "learn",
                        "title": "学一学:月份",
                        "words": months,
                        "cn": {"January": "一月", "February": "二月", "March": "三月", "April": "四月",
                               "May": "五月", "June": "六月", "July": "七月", "August": "八月",
                               "September": "九月", "October": "十月", "November": "十一月", "December": "十二月"},
                    },
                    {"type": "listen_tap", "title": "听一听,点一点", "words": months, "count": 8},
                    {"type": "look_choose", "title": "看一看,选一选", "words": months, "count": 8},
                ],
            },
            {
                "title": "运动与房间",
                "subtitle": "运动:足球、篮球、轮滑、高尔夫;房间:厨房、浴室、大厅、客厅",
                "steps": [
                    {
                        "type": "story",
                        "title": "故事开场",
                        "emoji": "⚽",
                        "text": "踢足球、打篮球、轮滑、打高尔夫……\n再看看王宫里的厨房、浴室和大厅。\n学一学它们的名字!",
                    },
                    {
                        "type": "learn",
                        "title": "学一学:运动与房间",
                        "words": sports_rooms,
                        "cn": {"play soccer": "踢足球", "play basketball": "打篮球",
                               "roller-skating": "轮滑", "golf": "高尔夫",
                               "kitchen": "厨房", "bathroom": "浴室", "hall": "大厅", "sitting room": "客厅"},
                    },
                    {"type": "listen_tap", "title": "听一听,点一点", "words": sports_rooms, "count": 6},
                    {"type": "look_choose", "title": "看一看,选一选", "words": sports_rooms, "count": 6},
                    {
                        "type": "sentence",
                        "title": "句子跟读",
                        "sentences": [
                            {"text": "She’s playing tennis.", "cn": "她在打网球。", "word": "She’s playing tennis."},
                        ],
                    },
                ],
            },
        ],
    }


def unit6_course():
    comparatives = ["fat", "fatter", "small", "smaller", "tall", "taller", "big", "bigger"]
    ordinals = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth"]
    misc = ["silly", "helicopter", "hot", "wake up", "job", "dirty"]
    return {
        "unit_id": 23,
        "title": "Big Muzzy · 大小高低",
        "description": "学会比较大小高矮、数第一到第八,再学几个常用的动作短语。零基础友好,边玩边学。",
        "cover_emoji": "⚖️",
        "order": 6,
        "lessons": [
            {
                "title": "谁更大?",
                "subtitle": "比较级:胖、更胖、小、更小、高、更高、大、更大",
                "steps": [
                    {
                        "type": "story",
                        "title": "故事开场",
                        "emoji": "🐘",
                        "text": "大象大,蚂蚁小;这个高,那个更高。\n学一学怎么比较大小高矮,\n\"更\" 要用 -er 结尾哦!",
                    },
                    {
                        "type": "learn",
                        "title": "学一学:比较级",
                        "words": comparatives,
                        "cn": {"fat": "胖的", "fatter": "更胖的", "small": "小的", "smaller": "更小的",
                               "tall": "高的", "taller": "更高的", "big": "大的", "bigger": "更大的"},
                    },
                    {"type": "listen_tap", "title": "听一听,点一点", "words": comparatives, "count": 6},
                    {"type": "look_choose", "title": "看一看,选一选", "words": comparatives, "count": 6},
                    {
                        "type": "sentence",
                        "title": "句子跟读",
                        "sentences": [
                            {"text": "I'm bigger.", "cn": "我更大。", "word": "bigger"},
                            {"text": "That one's fatter.", "cn": "那个更胖。", "word": "fatter"},
                        ],
                    },
                ],
            },
            {
                "title": "第一到第八",
                "subtitle": "序数词:第一、第二……第八",
                "steps": [
                    {
                        "type": "story",
                        "title": "故事开场",
                        "emoji": "🥇",
                        "text": "排队啦!\n谁是第一,谁是第二,谁排第八?\n学一学序数词:first、second、third……",
                    },
                    {
                        "type": "learn",
                        "title": "学一学:序数词",
                        "words": ordinals,
                        "cn": {"first": "第一", "second": "第二", "third": "第三", "fourth": "第四",
                               "fifth": "第五", "sixth": "第六", "seventh": "第七", "eighth": "第八"},
                    },
                    {"type": "listen_tap", "title": "听一听,点一点", "words": ordinals, "count": 6},
                    {"type": "look_choose", "title": "看一看,选一选", "words": ordinals, "count": 6},
                    {
                        "type": "sentence",
                        "title": "句子跟读",
                        "sentences": [
                            {"text": "The first one's big.", "cn": "第一个是大的。", "word": "first"},
                            {"text": "The fifth is tall.", "cn": "第五个是高个。", "word": "fifth"},
                        ],
                    },
                ],
            },
            {
                "title": "忙碌的 Muzzy",
                "subtitle": "短语:傻傻的、直升机、热、醒醒、工作、脏",
                "steps": [
                    {
                        "type": "story",
                        "title": "故事开场",
                        "emoji": "🚁",
                        "text": "Muzzy 今天好忙!\n坐直升机、醒醒、干活、弄得脏兮兮……\n学一学这些短语,然后叫醒身边的人吧!",
                    },
                    {
                        "type": "learn",
                        "title": "学一学:常用短语",
                        "words": misc,
                        "cn": {"silly": "傻傻的", "helicopter": "直升机", "hot": "热的",
                               "wake up": "醒醒", "job": "工作", "dirty": "脏的"},
                    },
                    {"type": "listen_tap", "title": "听一听,点一点", "words": misc, "count": 5},
                    {"type": "look_choose", "title": "看一看,选一选", "words": misc, "count": 5},
                    {
                        "type": "sentence",
                        "title": "句子跟读",
                        "sentences": [
                            {"text": "Wake up!", "cn": "醒醒!", "word": "wake up"},
                            {"text": "Be careful.", "cn": "小心点。", "word": "Be careful."},
                        ],
                    },
                ],
            },
        ],
    }


def unit7_course():
    party = ["party", "daughter", "husband", "baby", "girl", "surprise", "secret", "cake", "naughty"]
    times = ["5:30", "8:00", "10:00", "10:15", "10:30", "11:00",
             "quarter to eleven", "quarter to three", "half past four", "half"]
    foods = ["flour", "sugar", "currants", "salt", "pepper", "rice", "cheese", "biscuits", "eggs", "milk"]
    return {
        "unit_id": 24,
        "title": "Big Muzzy · 派对、时间和食物",
        "description": "参加王宫的生日派对,认识家人,学会看钟表说时间,再认识好吃的食物。零基础友好,边玩边学。",
        "cover_emoji": "🎂",
        "order": 7,
        "lessons": [
            {
                "title": "派对惊喜",
                "subtitle": "家人与惊喜:派对、女儿、丈夫、宝宝、女孩、蛋糕",
                "steps": [
                    {
                        "type": "story",
                        "title": "故事开场",
                        "emoji": "🎉",
                        "text": "王宫里要开派对啦!\n有蛋糕、有惊喜,还有可爱的小宝宝。\n学一学和家人、派对有关的词吧!",
                    },
                    {
                        "type": "learn",
                        "title": "学一学:派对词汇",
                        "words": party,
                        "cn": {"party": "派对", "daughter": "女儿", "husband": "丈夫", "baby": "宝宝",
                               "girl": "女孩", "surprise": "惊喜", "secret": "秘密", "cake": "蛋糕",
                               "naughty": "淘气的"},
                    },
                    {"type": "listen_tap", "title": "听一听,点一点", "words": party, "count": 7},
                    {"type": "look_choose", "title": "看一看,选一选", "words": party, "count": 7},
                    {
                        "type": "sentence",
                        "title": "句子跟读",
                        "sentences": [
                            {"text": "What a nice surprise!", "cn": "真是个惊喜!", "word": "What a nice surprise!"},
                            {"text": "She's a girl.", "cn": "她是个女孩。", "word": "She's a girl."},
                        ],
                    },
                ],
            },
            {
                "title": "几点钟了?",
                "subtitle": "时间:五点半、八点、十点一刻、十一点差一刻……",
                "steps": [
                    {
                        "type": "story",
                        "title": "故事开场",
                        "emoji": "🕰️",
                        "text": "派对几点开始?\n八点?十点一刻?\n学一学怎么用英语看钟表、说时间!",
                    },
                    {
                        "type": "learn",
                        "title": "学一学:看钟表",
                        "words": times,
                        "cn": {"5:30": "五点半", "8:00": "八点", "10:00": "十点", "10:15": "十点一刻",
                               "10:30": "十点半", "11:00": "十一点", "quarter to eleven": "十一点差一刻",
                               "quarter to three": "三点差一刻", "half past four": "四点半", "half": "一半"},
                    },
                    {"type": "listen_tap", "title": "听一听,点一点", "words": times, "count": 7},
                    {"type": "look_choose", "title": "看一看,选一选", "words": times, "count": 7},
                    {
                        "type": "sentence",
                        "title": "句子跟读",
                        "sentences": [
                            {"text": "Don't be late.", "cn": "别迟到!", "word": "Don't be late."},
                        ],
                    },
                ],
            },
            {
                "title": "好吃的食物",
                "subtitle": "食物:面粉、糖、盐、胡椒、米饭、奶酪、饼干、鸡蛋、牛奶",
                "steps": [
                    {
                        "type": "story",
                        "title": "故事开场",
                        "emoji": "🧁",
                        "text": "做蛋糕要面粉和糖,吃饭要米饭和奶酪……\n学一学这些食物的英文名字吧!",
                    },
                    {
                        "type": "learn",
                        "title": "学一学:食物",
                        "words": foods,
                        "cn": {"flour": "面粉", "sugar": "糖", "currants": "葡萄干", "salt": "盐",
                               "pepper": "胡椒", "rice": "米饭", "cheese": "奶酪", "biscuits": "饼干",
                               "eggs": "鸡蛋", "milk": "牛奶"},
                    },
                    {"type": "listen_tap", "title": "听一听,点一点", "words": foods, "count": 7},
                    {"type": "look_choose", "title": "看一看,选一选", "words": foods, "count": 7},
                    {
                        "type": "sentence",
                        "title": "句子跟读",
                        "sentences": [
                            {"text": "What about milk?", "cn": "牛奶怎么样?", "word": "What about milk?"},
                            {"text": "I want some apples.", "cn": "我想要一些苹果。", "word": "I want some apples."},
                        ],
                    },
                ],
            },
        ],
    }


def unit8_course():
    around = ["outside", "inside", "push", "button", "on the top", "box", "door", "window", "floor", "boat", "old", "new"]
    guests = ["guest", "greet", "politely", "darling", "rude", "sing a song", "hold", "open", "close", "find"]
    snacks = ["peanuts", "chips", "biscuit", "bun", "lemonade", "orange juice", "pizzas", "pies",
              "chocolate", "strawberry ice", "spaghetti"]
    return {
        "unit_id": 25,
        "title": "Big Muzzy · 房子里外和招待客人",
        "description": "学会说里里外外、开开关关,礼貌地招待客人,再认识各种好吃的点心和饮料。零基础友好,边玩边学。",
        "cover_emoji": "🏠",
        "order": 8,
        "lessons": [
            {
                "title": "里里外外",
                "subtitle": "位置与动作:外面、里面、推、按钮、门、窗、地板、船",
                "steps": [
                    {
                        "type": "story",
                        "title": "故事开场",
                        "emoji": "🚪",
                        "text": "屋里还是屋外?门和窗户在哪里?\n按一按按钮,推一推门……\n学一学这些位置和动作的词!",
                    },
                    {
                        "type": "learn",
                        "title": "学一学:位置与动作",
                        "words": around,
                        "cn": {"outside": "外面", "inside": "里面", "push": "推", "button": "按钮",
                               "on the top": "在上面", "box": "盒子", "door": "门", "window": "窗户",
                               "floor": "地板", "boat": "船", "old": "旧的", "new": "新的"},
                    },
                    {"type": "listen_tap", "title": "听一听,点一点", "words": around, "count": 8},
                    {"type": "look_choose", "title": "看一看,选一选", "words": around, "count": 8},
                    {
                        "type": "sentence",
                        "title": "句子跟读",
                        "sentences": [
                            {"text": "She went that way.", "cn": "她往那边去了。", "word": "She went that way."},
                        ],
                    },
                ],
            },
            {
                "title": "招待客人",
                "subtitle": "礼貌用语:客人、问候、礼貌地、亲爱的、粗鲁的、唱歌",
                "steps": [
                    {
                        "type": "story",
                        "title": "故事开场",
                        "emoji": "🤝",
                        "text": "有客人来家里,要怎么礼貌地打招呼呢?\n要微笑问候,不能粗鲁哦!\n学一学招待客人的词。",
                    },
                    {
                        "type": "learn",
                        "title": "学一学:招待客人",
                        "words": guests,
                        "cn": {"guest": "客人", "greet": "问候", "politely": "礼貌地", "darling": "亲爱的",
                               "rude": "粗鲁的", "sing a song": "唱歌", "hold": "拿着", "open": "打开",
                               "close": "关上", "find": "找到"},
                    },
                    {"type": "listen_tap", "title": "听一听,点一点", "words": guests, "count": 7},
                    {"type": "look_choose", "title": "看一看,选一选", "words": guests, "count": 7},
                    {
                        "type": "sentence",
                        "title": "句子跟读",
                        "sentences": [
                            {"text": "Can you greet the guests politely?", "cn": "你能礼貌地问候客人吗?", "word": "Can you greet the guests politely?"},
                            {"text": "Off you go", "cn": "走吧!", "word": "Off you go"},
                        ],
                    },
                ],
            },
            {
                "title": "好吃的点心",
                "subtitle": "点心饮料:花生、薯条、柠檬水、橙汁、披萨、巧克力、意大利面",
                "steps": [
                    {
                        "type": "story",
                        "title": "故事开场",
                        "emoji": "🍕",
                        "text": "派对上有好多好吃的!\n薯条、披萨、巧克力、柠檬水……\n学一学它们的名字,选出你最爱的吧!",
                    },
                    {
                        "type": "learn",
                        "title": "学一学:点心饮料",
                        "words": snacks,
                        "cn": {"peanuts": "花生", "chips": "薯条", "biscuit": "饼干", "bun": "小面包",
                               "lemonade": "柠檬水", "orange juice": "橙汁", "pizzas": "披萨", "pies": "派",
                               "chocolate": "巧克力", "strawberry ice": "草莓冰淇淋", "spaghetti": "意大利面"},
                    },
                    {"type": "listen_tap", "title": "听一听,点一点", "words": snacks, "count": 8},
                    {"type": "look_choose", "title": "看一看,选一选", "words": snacks, "count": 8},
                    {
                        "type": "sentence",
                        "title": "句子跟读",
                        "sentences": [
                            {"text": "How much?", "cn": "多少钱?", "word": "How much?"},
                        ],
                    },
                ],
            },
        ],
    }


def unit9_course():
    shout_words = ["shout", "scream", "teach", "learn", "river", "catch", "bird", "far", "funny", "carry"]
    way_words = ["right", "left", "straight on", "way", "deep", "sink", "plug", "marry", "get out", "important"]
    return {
        "unit_id": 26,
        "title": "Big Muzzy · 河边历险",
        "description": "和 Muzzy 一起在河边冒险:大声喊、学本领、找方向,学会重要的动词和方向词。零基础友好,边玩边学。",
        "cover_emoji": "🏞️",
        "order": 9,
        "lessons": [
            {
                "title": "大声喊一喊",
                "subtitle": "动词:喊叫、尖叫、教、学、抓、搬运、鸟、河、远、有趣",
                "steps": [
                    {
                        "type": "story",
                        "title": "故事开场",
                        "emoji": "📣",
                        "text": "在河边遇到了危险,要大声喊救命!\n学一学喊叫、尖叫、教、学这些动词,\n还有河边的鸟和小树。",
                    },
                    {
                        "type": "learn",
                        "title": "学一学:河边动词",
                        "words": shout_words,
                        "cn": {"shout": "喊叫", "scream": "尖叫", "teach": "教", "learn": "学",
                               "river": "河", "catch": "抓住", "bird": "鸟", "far": "远的",
                               "funny": "有趣的", "carry": "搬运"},
                    },
                    {"type": "listen_tap", "title": "听一听,点一点", "words": shout_words, "count": 7},
                    {"type": "look_choose", "title": "看一看,选一选", "words": shout_words, "count": 7},
                    {
                        "type": "sentence",
                        "title": "句子跟读",
                        "sentences": [
                            {"text": "Be quiet.", "cn": "安静!", "word": "Be quiet."},
                            {"text": "Don't worry.", "cn": "别担心。", "word": "Don't worry."},
                        ],
                    },
                ],
            },
            {
                "title": "走哪条路?",
                "subtitle": "方向:右、左、直走、路、深、下沉、塞子、结婚、出去、重要",
                "steps": [
                    {
                        "type": "story",
                        "title": "故事开场",
                        "emoji": "🧭",
                        "text": "左转还是右转?直走还是拐弯?\n船会不会沉下去?水有多深?\n学一学方向和这些动词。",
                    },
                    {
                        "type": "learn",
                        "title": "学一学:方向与动词",
                        "words": way_words,
                        "cn": {"right": "右", "left": "左", "straight on": "直走", "way": "路",
                               "deep": "深的", "sink": "下沉", "plug": "塞子", "marry": "结婚",
                               "get out": "出去", "important": "重要的"},
                    },
                    {"type": "listen_tap", "title": "听一听,点一点", "words": way_words, "count": 7},
                    {"type": "look_choose", "title": "看一看,选一选", "words": way_words, "count": 7},
                    {
                        "type": "sentence",
                        "title": "句子跟读",
                        "sentences": [
                            {"text": "Which way?", "cn": "走哪条路?", "word": "Which way?"},
                            {"text": "Be calm.", "cn": "冷静点。", "word": "Be calm."},
                        ],
                    },
                ],
            },
        ],
    }


def unit10_course():
    road_words = ["road", "cars", "driver", "faster", "slower", "start", "safe", "danger", "heavy", "hat"]
    adj_words = ["smaller", "stronger", "shorter", "better", "nice", "ill", "enough", "an awful bird", "fantastic place", "rubbish"]
    return {
        "unit_id": 27,
        "title": "Big Muzzy · 出发旅行",
        "description": "坐上汽车去旅行:学开车、认路标、懂安全与危险,再学一堆有用的形容词。零基础友好,边玩边学。",
        "cover_emoji": "🚗",
        "order": 10,
        "lessons": [
            {
                "title": "公路旅行",
                "subtitle": "交通:公路、汽车、司机、更快、更慢、出发、安全、危险",
                "steps": [
                    {
                        "type": "story",
                        "title": "故事开场",
                        "emoji": "🛣️",
                        "text": "嘀嘀——出发去旅行!\n路上有汽车和司机,还有危险的路牌。\n学一学和公路、安全有关的词!",
                    },
                    {
                        "type": "learn",
                        "title": "学一学:公路旅行",
                        "words": road_words,
                        "cn": {"road": "公路", "cars": "汽车", "driver": "司机", "faster": "更快",
                               "slower": "更慢", "start": "出发", "safe": "安全的", "danger": "危险",
                               "heavy": "重的", "hat": "帽子"},
                    },
                    {"type": "listen_tap", "title": "听一听,点一点", "words": road_words, "count": 7},
                    {"type": "look_choose", "title": "看一看,选一选", "words": road_words, "count": 7},
                    {
                        "type": "sentence",
                        "title": "句子跟读",
                        "sentences": [
                            {"text": "Look out!", "cn": "小心!", "word": "Look out!"},
                            {"text": "What does this mean?", "cn": "这是什么意思?", "word": "What does this mean?"},
                        ],
                    },
                ],
            },
            {
                "title": "形容词大集合",
                "subtitle": "形容词:更小、更强壮、更矮、更好、漂亮、生病、糟糕、棒极了",
                "steps": [
                    {
                        "type": "story",
                        "title": "故事开场",
                        "emoji": "✨",
                        "text": "这个地方太棒了!\n那辆车更小,这个人更强壮……\n学一学这些形容人和物的词。",
                    },
                    {
                        "type": "learn",
                        "title": "学一学:形容词",
                        "words": adj_words,
                        "cn": {"smaller": "更小", "stronger": "更强壮", "shorter": "更矮", "better": "更好",
                               "nice": "漂亮的", "ill": "生病的", "enough": "足够的", "an awful bird": "一只可怕的鸟",
                               "fantastic place": "很棒的地方", "rubbish": "垃圾"},
                    },
                    {"type": "listen_tap", "title": "听一听,点一点", "words": adj_words, "count": 7},
                    {"type": "look_choose", "title": "看一看,选一选", "words": adj_words, "count": 7},
                    {
                        "type": "sentence",
                        "title": "句子跟读",
                        "sentences": [
                            {"text": "It looks awful.", "cn": "看起来很糟糕。", "word": "It looks awful."},
                            {"text": "I’m not feeling well.", "cn": "我感觉不舒服。", "word": "I’m not feeling well."},
                        ],
                    },
                ],
            },
        ],
    }


def unit11_course():
    direction_words = ["North", "South", "West", "East", "house", "rocks", "behind the rocks", "bottle", "milk", "pour"]
    compare_words = ["wide", "wider", "widest", "laugh", "video", "colour", "train", "plane", "food", "have a lesson"]
    return {
        "unit_id": 28,
        "title": "Big Muzzy · 方向和比较",
        "description": "学会东南西北四个方向,再学宽、更宽、最宽怎么比较,顺带认识火车飞机和颜色。零基础友好,边玩边学。",
        "cover_emoji": "🧭",
        "order": 11,
        "lessons": [
            {
                "title": "东南西北",
                "subtitle": "方向:北、南、西、东;房子、岩石、瓶子、牛奶、倒",
                "steps": [
                    {
                        "type": "story",
                        "title": "故事开场",
                        "emoji": "🧭",
                        "text": "指南针指哪里?\n北、南、西、东,四个方向要记牢!\n再把牛奶倒进瓶子里。",
                    },
                    {
                        "type": "learn",
                        "title": "学一学:方向",
                        "words": direction_words,
                        "cn": {"North": "北", "South": "南", "West": "西", "East": "东",
                               "house": "房子", "rocks": "岩石", "behind the rocks": "在岩石后面",
                               "bottle": "瓶子", "milk": "牛奶", "pour": "倒"},
                    },
                    {"type": "listen_tap", "title": "听一听,点一点", "words": direction_words, "count": 7},
                    {"type": "look_choose", "title": "看一看,选一选", "words": direction_words, "count": 7},
                    {
                        "type": "sentence",
                        "title": "句子跟读",
                        "sentences": [
                            {"text": "Pour the milk into the bottle.", "cn": "把牛奶倒进瓶子里。", "word": "Pour the milk into the bottle."},
                            {"text": "What kind of animal is it?", "cn": "它是什么动物?", "word": "What kind of animal is it?"},
                        ],
                    },
                ],
            },
            {
                "title": "宽窄比较",
                "subtitle": "比较:宽、更宽、最宽;笑、视频、颜色、火车、飞机、食物",
                "steps": [
                    {
                        "type": "story",
                        "title": "故事开场",
                        "emoji": "📏",
                        "text": "这条河宽,那条河更宽,还有一条最宽!\n宽、更宽、最宽,怎么比较呢?\n学一学,再去坐火车和飞机!",
                    },
                    {
                        "type": "learn",
                        "title": "学一学:宽窄与更多词",
                        "words": compare_words,
                        "cn": {"wide": "宽的", "wider": "更宽", "widest": "最宽", "laugh": "笑",
                               "video": "视频", "colour": "颜色", "train": "火车", "plane": "飞机",
                               "food": "食物", "have a lesson": "上课"},
                    },
                    {"type": "listen_tap", "title": "听一听,点一点", "words": compare_words, "count": 7},
                    {"type": "look_choose", "title": "看一看,选一选", "words": compare_words, "count": 7},
                    {
                        "type": "sentence",
                        "title": "句子跟读",
                        "sentences": [
                            {"text": "I can't get through.", "cn": "我过不去。", "word": "I can't get through."},
                        ],
                    },
                ],
            },
        ],
    }


def unit12_course():
    holiday_words = ["vacation", "radio", "noise", "argue", "fault", "new", "round", "a fly"]
    date_words = ["ninth", "tenth", "eleventh", "thirty-first", "right", "Look outside.", "out of the river", "What's the date today?"]
    return {
        "unit_id": 29,
        "title": "Big Muzzy · 度假和日期",
        "description": "Muzzy 去度假啦!学学假期里的词,再说说今天几号、第几天。零基础友好,边玩边学。",
        "cover_emoji": "🏖️",
        "order": 12,
        "lessons": [
            {
                "title": "度假了",
                "subtitle": "假期:度假、收音机、噪音、争吵、过错、新、圆、苍蝇",
                "steps": [
                    {
                        "type": "story",
                        "title": "故事开场",
                        "emoji": "🏖️",
                        "text": "Muzzy 去海边度假啦!\n听听收音机,晒晒太阳……\n学一学和假期有关的词吧!",
                    },
                    {
                        "type": "learn",
                        "title": "学一学:度假词汇",
                        "words": holiday_words,
                        "cn": {"vacation": "假期", "radio": "收音机", "noise": "噪音", "argue": "争吵",
                               "fault": "过错", "new": "新的", "round": "圆的", "a fly": "一只苍蝇"},
                    },
                    {"type": "listen_tap", "title": "听一听,点一点", "words": holiday_words, "count": 6},
                    {"type": "look_choose", "title": "看一看,选一选", "words": holiday_words, "count": 6},
                    {
                        "type": "sentence",
                        "title": "句子跟读",
                        "sentences": [
                            {"text": "I'm having a holiday.", "cn": "我在度假。", "word": "I'm having a holiday."},
                        ],
                    },
                ],
            },
            {
                "title": "今天几号?",
                "subtitle": "日期:第九、第十、第十一、第三十一;今天几号?",
                "steps": [
                    {
                        "type": "story",
                        "title": "故事开场",
                        "emoji": "📆",
                        "text": "今天是几号?\n第九天、第十天还是第三十一天?\n学一学日期和序数词,再学最后一课!",
                    },
                    {
                        "type": "learn",
                        "title": "学一学:日期与序数词",
                        "words": date_words,
                        "cn": {"ninth": "第九", "tenth": "第十", "eleventh": "第十一", "thirty-first": "第三十一",
                               "right": "正确的", "Look outside.": "往外看", "out of the river": "从河里出来",
                               "What's the date today?": "今天几号?"},
                    },
                    {"type": "listen_tap", "title": "听一听,点一点", "words": date_words, "count": 6},
                    {"type": "look_choose", "title": "看一看,选一选", "words": date_words, "count": 6},
                    {
                        "type": "sentence",
                        "title": "句子跟读",
                        "sentences": [
                            {"text": "What's the date today?", "cn": "今天几号?", "word": "What's the date today?"},
                        ],
                    },
                ],
            },
        ],
    }


COURSES = [unit1_course(), unit2_course(), unit3_course(), unit4_course(), unit5_course(), unit6_course(),
           unit7_course(), unit8_course(), unit9_course(), unit10_course(), unit11_course(), unit12_course()]


def seed_course(db, cfg):
    """幂等写入一门课程:保留课程记录,重建课时与进度。"""
    course = (
        db.query(Course)
        .filter(Course.textbook_id == TEXTBOOK_ID, Course.unit_id == cfg["unit_id"])
        .first()
    )
    if not course:
        course = Course(
            textbook_id=TEXTBOOK_ID,
            unit_id=cfg["unit_id"],
            title=cfg["title"],
            description=cfg["description"],
            cover_emoji=cfg["cover_emoji"],
            order=cfg["order"],
            status="active",
        )
        db.add(course)
        db.flush()
    else:
        course.title = cfg["title"]
        course.description = cfg["description"]
        course.cover_emoji = cfg["cover_emoji"]
        course.order = cfg["order"]
        course.status = "active"
        db.flush()

    # 清掉旧课时与相关进度(重建),保留课程记录
    old_lesson_ids = [l.id for l in course.lessons]
    if old_lesson_ids:
        db.query(CourseProgress).filter(
            CourseProgress.lesson_id.in_(old_lesson_ids)
        ).delete(synchronize_session=False)
    db.query(CourseLesson).filter(CourseLesson.course_id == course.id).delete(
        synchronize_session=False
    )
    db.flush()
    # 清空 identity map,避免旧课时删除后自增 id 复用产生 SAWarning
    db.expire_all()

    for idx, lesson_data in enumerate(cfg["lessons"], start=1):
        db.add(
            CourseLesson(
                course_id=course.id,
                title=lesson_data["title"],
                subtitle=lesson_data["subtitle"],
                order=idx,
                content={"steps": lesson_data["steps"]},
            )
        )

    db.commit()
    lessons = db.query(CourseLesson).filter(CourseLesson.course_id == course.id).count()
    print(f"OK: 课程 id={course.id}「{cfg['title']}」,共 {lessons} 节课")


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        for cfg in COURSES:
            seed_course(db, cfg)
    finally:
        db.close()


if __name__ == "__main__":
    main()
