# -*- coding: utf-8 -*-
import os
import json
import random
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty, DictProperty

# ==================== 全局配置 ====================
SAVE_FILE = "save.json"
COLOR = {
    "paper": "#F5F1E4", "ink": "#232323",
    "red": "#C92E2E", "green": "#2E8B57", "blue": "#3A5F70",
    "purple": "#6A4C93", "orange": "#D88F30", "gray": "#8C8C8C"
}
RARITY_COLOR = {
    "凡品": get_color_from_hex("#8C8C8C"),
    "良品": get_color_from_hex("#2E8B57"),
    "优品": get_color_from_hex("#3A5F70"),
    "极品": get_color_from_hex("#6A4C93"),
    "绝品": get_color_from_hex("#D88F30"),
    "神品": get_color_from_hex("#C92E2E")
}

# ==================== 武学系统 + 特效 ====================
SKILLS = {
    "易筋经": {"type": "心法", "dmg": 0, "heal": 25, "rarity": "神品", "effect": "✨金光护体"},
    "九阴真经": {"type": "心法", "dmg": 0, "def_boost": 35, "rarity": "神品", "effect": "🌫墨影缠身"},
    "九阳神功": {"type": "心法", "dmg": 0, "atk_boost": 30, "rarity": "神品", "effect": "🔥炎阳环绕"},
    "降龙十八掌": {"type": "绝学", "dmg": 90, "aoe": 1, "rarity": "神品", "effect": "🐉金龙奔腾"},
    "独孤九剑": {"type": "绝学", "dmg": 85, "ignore_def": 1, "rarity": "神品", "effect": "⚔️剑气纵横"},
    "黯然销魂掌": {"type": "绝学", "dmg": 80, "stun": 1, "rarity": "绝品", "effect": "😵黑雾冲击"},
    "唐门暴雨梨花": {"type": "武学", "dmg": 50, "poison": 1, "rarity": "极品", "effect": "💀毒针四射"},
    "武当长拳": {"type": "武学", "dmg": 20, "rarity": "良品", "effect": "🥋拳风"},
    "少林罗汉拳": {"type": "武学", "dmg": 22, "rarity": "良品", "effect": "🛡️刚猛拳劲"},
    "逍遥扇法": {"type": "武学", "dmg": 28, "rarity": "优品", "effect": "🪭扇影"},
    "血刀刀法": {"type": "武学", "dmg": 45, "rarity": "极品", "effect": "🩸血光"},
    "市井消息": {"type": "趣味", "type": "fun", "rarity": "凡品", "effect": "💬打探情报"},
    "妙手空空": {"type": "趣味", "type": "fun", "rarity": "优品", "effect": "👋顺手牵羊"},
    "静心打坐": {"type": "趣味", "type": "fun", "rarity": "良品", "effect": "🧘内力恢复"}
}

# ==================== 212个NPC + 头像 + 关系 + 任务 ====================
NPC_AVATAR = {}
NPC_LOVE = {}
NPC_HATE = {}
NPC_TASK = {}
NPC_FORCE = {}
DYNAS = ["齐", "楚", "燕", "韩", "赵", "魏", "秦", "汉"]
for i in range(128):
    name = f"村民_{i:03d}"
    NPC_AVATAR[name] = random.choice(["👨‍🌾", "👩‍🌾", "👴", "👵", "👧", "👦"])
    NPC_LOVE[name] = f"村民_{(i+1)%128:03d}"
    NPC_HATE[name] = "山贼"
    NPC_TASK[name] = f"寻找丢失的物品_{i}"
    NPC_FORCE[name] = "无"
for i in range(64):
    name = f"朝臣_{i:03d}"
    NPC_AVATAR[name] = "👨‍💼"
    dyn = random.choice(DYNAS)
    NPC_FORCE[name] = dyn
    NPC_LOVE[name] = f"{dyn}太子"
    NPC_HATE[name] = f"{[d for d in DYNAS if d!=dyn][0]}"
    NPC_TASK[name] = f"{dyn}密令：刺探敌国情报"
for i in range(20):
    name = f"江湖侠客_{i:02d}"
    NPC_AVATAR[name] = random.choice(["🤺", "🥷", "👨‍⚖️", "👩‍⚖️"])
    NPC_FORCE[name] = random.choice(["少林", "武当", "唐门", "逍遥", "古墓", "血刀", "星宿", "无"])
    NPC_LOVE[name] = "同道中人"
    NPC_HATE[name] = "魔教"
    NPC_TASK[name] = f"铲除魔教爪牙_{i}"

# ==================== 地图 ====================
MAP = {
    "清溪村": {
        "desc": "宁静山村，江湖起点",
        "exits": ["城郊", "洛阳城", "少林", "武当"],
        "npcs": [f"村民_{i:03d}" for i in range(64)] + ["村长", "阿美", "阿牛", "铁匠", "郎中", "神秘老人"]
    },
    "城郊": {"desc": "密林荒野", "exits": ["清溪村", "黑风寨"], "npcs": ["野狼", "山贼喽啰", "猎人"]},
    "黑风寨": {"desc": "山贼巢穴", "exits": ["城郊"], "npcs": ["二寨主", "大寨主", "魔教密使"]},
    "洛阳城": {
        "desc": "中原雄城，八王朝交汇之地",
        "exits": ["清溪村", "齐宫", "楚宫", "汉宫", "秦宫", "赵宫", "魏宫", "韩宫", "燕宫"],
        "npcs": [f"朝臣_{i:03d}" for i in range(64)] + [f"江湖侠客_{i:02d}" for i in range(20)] + ["知府", "富商", "花魁", "书生"]
    }
}
for d in DYNAS: MAP[f"{d}宫"] = {"desc": f"{d}王朝朝堂", "exits": ["洛阳城"], "npcs": [f"{d}王", f"{d}太子", f"{d}将军"]}

# ==================== 存档数据 ====================
class GameData:
    def __init__(self):
        self.custom_options = {
            "hair": ["束发", "披发", "道髻", "侠髻", "高马尾", "双丫髻", "云鬓", "斗笠"],
            "face": ["坚毅", "温润", "冷艳", "圆脸", "清瘦", "豪爽"],
            "eye": ["锐目", "杏眼", "凤眼", "柔目"],
            "nose": ["高挺", "圆润", "微翘"],
            "mouth": ["薄唇", "丰唇", "含笑", "肃然"],
            "cloth": ["粗布劲装", "青衫", "锦衣", "道袍", "披风", "战甲"],
            "decor": ["玉佩", "玉簪", "护腕", "斗笠", "面纱", "无"]
        }
        self.player = {
            "name": "少侠", "gender": "男",
            "custom": {"hair":"束发","face":"坚毅","eye":"锐目","nose":"高挺","mouth":"薄唇","cloth":"青衫","decor":"玉佩"},
            "level":1, "exp":0, "need_exp":100, "life":100, "max_life":100, "mana":60, "max_mana":60,
            "attack":12, "defense":10, "money":800, "good_evil":0, "force":None, "room":"清溪村", "rod":True,
            "skills": {"mind":[], "ult":[], "combat":[], "fun":[]},
            "skill_exp": {}, "inventory": {}, "tasks": {}, "favor": {}
        }
        self.msg = ""

    def get_avatar(self):
        c = self.player["custom"]
        return f"[{self.player['gender']}] {c['hair']} | {c['face']} | {c['cloth']} | {c['decor']}"

    def change_part(self, k):
        lst = self.custom_options[k]
        cur = self.player["custom"][k]
        self.player["custom"][k] = lst[(lst.index(cur)+1)%len(lst)]

    def save(self):
        with open(SAVE_FILE,"w",encoding="utf-8") as f: json.dump(self.player,f,ensure_ascii=False,indent=2)
        self.msg = "✅ 存档成功"

    def load(self):
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE,"r",encoding="utf-8") as f: self.player = json.load(f)
            self.msg = "✅ 读档成功"

    def move(self, t):
        if t in MAP[self.player["room"]]["exits"]:
            self.player["room"] = t
            self.msg = f"🚶 前往 {t}"

    def talk(self, n):
        f = self.player["force"]
        favor = self.player["favor"].get(n,50)
        if NPC_FORCE.get(n,"无") != "无" and f != NPC_FORCE[n] and f != None:
            self.msg = f"😠 {n} 对你充满敌意（势力对立）"
        else:
            self.player["favor"][n] = min(100, favor+5)
            self.msg = f"💬 与 {n} 交谈 | 好感：{self.player['favor'][n]}"
            if random.random()<0.3: self.player["tasks"][n] = NPC_TASK[n]

    def practice(self, sk):
        self.player["skill_exp"][sk] = self.player["skill_exp"].get(sk,0)+15
        self.player["exp"] += 8
        self.msg = f"🧘 修炼 {sk} | 武学经验+15"
        self.level_up()

    def level_up(self):
        while self.player["exp"] >= self.player["need_exp"]:
            self.player["exp"] -= self.player["need_exp"]
            self.player["level"] += 1
            self.player["max_life"] += 20
            self.player["max_mana"] += 15
            self.player["attack"] += 3
            self.player["defense"] += 2
            self.player["life"] = self.player["max_life"]
            self.msg = f"🎉 等级提升 Lv.{self.player['level']}"

    def fight(self, n):
        p = self.player
        dmg = p["attack"] + sum(SKILLS[s]["dmg"] for s in p["skills"]["combat"]+p["skills"]["ult"])
        self.msg = f"{SKILLS[random.choice(p['skills']['combat'])]['effect']} 造成{dmg}点伤害！击败{n}"
        p["exp"] += 30
        self.level_up()

    def fish(self):
        if not self.player["rod"]: self.msg="没有鱼竿"; return
        r = random.random()
        if r<0.4: item,rar="草鱼","凡品"
        elif r<0.7: item,rar="鲤鱼","良品"
        elif r<0.9: item,rar="灵鱼","优品"
        elif r<0.98: item,rar="千年锦鲤","极品"
        else: item,rar="寒渊龙鲤","神品"
        self.player["inventory"][item] = self.player["inventory"].get(item,0)+1
        self.msg = f"🎣 钓到 {item}({rar})"

G = GameData()

# ==================== 界面 ====================
class BaseScreen(Screen):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.bg = get_color_from_hex(COLOR["paper"])
        self.ink = get_color_from_hex(COLOR["ink"])

class CreateScreen(BaseScreen):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical",padding=20,spacing=10)
        self.add_widget(self.layout)
        self.layout.add_widget(Label(text="水墨江湖 · 天下第一",font_size=28,color=self.ink))
        self.name_ipt = TextInput(hint_text="输入名号",size_hint=(1,.08))
        self.layout.add_widget(self.name_ipt)
        self.gender_btn = Button(text="性别: 男",size_hint=(1,.08),background_color=RARITY_COLOR["良品"])
        self.gender_btn.bind(on_press=lambda x: setattr(G.player,"gender","女" if G.player["gender"]=="男" else "男") or self.refresh())
        self.layout.add_widget(self.gender_btn)
        self.face_lbl = Label(text=G.get_avatar(),color=self.ink,font_size=16)
        self.layout.add_widget(self.face_lbl)
        g = GridLayout(cols=3,spacing=6)
        for k in ["hair","face","eye","nose","mouth","cloth","decor"]:
            b = Button(text=k,size_hint_y=None,height=40)
            b.bind(on_press=lambda x,k=k: G.change_part(k) or self.refresh())
            g.add_widget(b)
        self.layout.add_widget(g)
        s = Button(text="进入江湖",size_hint=(1,.12),background_color=RARITY_COLOR["绝品"])
        s.bind(on_press=self.start)
        self.layout.add_widget(s)
    def refresh(self):
        self.gender_btn.text = f"性别: {G.player['gender']}"
        self.face_lbl.text = G.get_avatar()
    def start(self,x):
        if self.name_ipt.text.strip(): G.player["name"]=self.name_ipt.text.strip()
        if not os.path.exists(SAVE_FILE): G.save()
        self.manager.current = "main"

class MainScreen(BaseScreen):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical",padding=12,spacing=6)
        self.add_widget(self.layout)
        Clock.schedule_interval(self.refresh,1)
    def refresh(self,dt):
        self.layout.clear_widgets()
        p = G.player
        self.layout.add_widget(Label(text=f"{p['name']} Lv.{p['level']} 善恶:{p['good_evil']}",font_size=18,color=self.ink))
        self.layout.add_widget(Label(text=f"❤️{p['life']}/{p['max_life']} ✨{p['mana']}/{p['max_mana']}",color=self.ink))
        self.layout.add_widget(Label(text=f"势力:{p['force'] or '无'} 银两:{p['money']}",color=self.ink))
        self.layout.add_widget(Label(text=f"[{p['room']}]",font_size=22,color=self.ink))
        self.layout.add_widget(Label(text=MAP[p['room']]["desc"],color=self.ink))
        self.layout.add_widget(Label(text=G.msg,color=RARITY_COLOR["神品"],font_size=14))
        g = GridLayout(cols=3,spacing=8)
        g.add_widget(Button(text="移动",on_press=lambda x:self.switch("move")))
        g.add_widget(Button(text="交谈",on_press=lambda x:self.switch("talk")))
        g.add_widget(Button(text="武学",on_press=lambda x:self.switch("skill")))
        g.add_widget(Button(text="任务",on_press=lambda x:self.switch("task")))
        g.add_widget(Button(text="钓鱼",on_press=lambda x:G.fish()))
        g.add_widget(Button(text="战斗",on_press=lambda x:self.switch("fight")))
        g.add_widget(Button(text="存档",on_press=lambda x:G.save()))
        g.add_widget(Button(text="读档",on_press=lambda x:G.load()))
        g.add_widget(Button(text="势力",on_press=lambda x:self.switch("force")))
        self.layout.add_widget(g)
    def switch(self,n): self.manager.current = n

class MoveScreen(BaseScreen):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical")
        self.add_widget(self.layout)
    def on_enter(self):
        self.layout.clear_widgets()
        for d in MAP[G.player["room"]]["exits"]:
            b = Button(text=f"前往 {d}",size_hint=(1,.1))
            b.bind(on_press=lambda x,t=d: G.move(t))
            self.layout.add_widget(b)
        self.layout.add_widget(Button(text="返回",on_press=lambda x:self.manager.current="main"))

class TalkScreen(BaseScreen):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical")
        self.sv = ScrollView()
        self.il = GridLayout(cols=1,spacing=10,size_hint_y=None)
        self.il.bind(minimum_height=self.il.setter("height"))
        self.sv.add_widget(self.il)
        self.layout.add_widget(self.sv)
        self.layout.add_widget(Button(text="返回",on_press=lambda x:self.manager.current="main"))
    def on_enter(self):
        self.il.clear_widgets()
        for n in MAP[G.player["room"]]["npcs"]:
            if n not in NPC_AVATAR: continue
            b = BoxLayout(size_hint_y=None,height=100)
            b.add_widget(Label(text=NPC_AVATAR[n],font_size=30))
            c = BoxLayout(orientation="vertical")
            c.add_widget(Label(text=n,font_size=16,color=self.ink))
            c.add_widget(Label(text=f"好感:{G.player['favor'].get(n,50)}",color=self.ink))
            c.add_widget(Button(text="交谈",size_hint=(1,.4),on_press=lambda x,n=n:G.talk(n)))
            b.add_widget(c)
            self.il.add_widget(b)

class SkillScreen(BaseScreen):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical")
        self.add_widget(self.layout)
    def on_enter(self):
        self.layout.clear_widgets()
        self.layout.add_widget(Label(text="武学修炼",font_size=20,color=self.ink))
        g = GridLayout(cols=2,spacing=6)
        p = G.player
        for t,lst in p["skills"].items():
            for s in lst:
                if s not in SKILLS: continue
                g.add_widget(Label(text=f"{t}:{s}",color=RARITY_COLOR[SKILLS[s]["rarity"]]))
                b = Button(text="修炼")
                b.bind(on_press=lambda x,s=s:G.practice(s))
                g.add_widget(b)
        self.layout.add_widget(g)
        self.layout.add_widget(Button(text="返回",on_press=lambda x:self.manager.current="main"))

class FightScreen(BaseScreen):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical")
        self.add_widget(self.layout)
    def on_enter(self):
        self.layout.clear_widgets()
        for n in ["野狼","山贼喽啰","二寨主"]:
            b = Button(text=f"挑战 {n}",size_hint=(1,.1))
            b.bind(on_press=lambda x,n=n:G.fight(n))
            self.layout.add_widget(b)
        self.layout.add_widget(Button(text="返回",on_press=lambda x:self.manager.current="main"))

# ==================== APP入口 ====================
class InkWarriorApp(App):
    def build(self):
        Window.clearcolor = get_color_from_hex(COLOR["paper"])
        sm = ScreenManager()
        sm.add_widget(CreateScreen(name="create"))
        sm.add_widget(MainScreen(name="main"))
        sm.add_widget(MoveScreen(name="move"))
        sm.add_widget(TalkScreen(name="talk"))
        sm.add_widget(SkillScreen(name="skill"))
        sm.add_widget(FightScreen(name="fight"))
        return sm

if __name__ == "__main__":
    InkWarriorApp().run()
