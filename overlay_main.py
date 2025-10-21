# -*- coding: utf-8 -*-
import sys, re, ctypes, requests, urllib3, os
from datetime import datetime, timedelta
from urllib3.exceptions import InsecureRequestWarning

from requests.adapters import HTTPAdapter
from hashlib import sha1
import weakref

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QToolButton,
    QFrame, QGraphicsDropShadowEffect, QLayout, QWidget as QtWidget, QMenu,
    QSystemTrayIcon, QMessageBox, QStyle, QSlider, QWidgetAction
)
from PySide6.QtCore import Qt, QTimer, QSize, QPoint, QRectF, QEvent, QSettings, QSharedMemory
from PySide6.QtGui import QColor, QIcon, QPixmap, QImage, QPainter, QPainterPath, QActionGroup, QAction, QPen, QGuiApplication

# ---------- Preferencias UI ----------
SNAP_DIST = 8
OUTER_MARGIN = 0
PANEL_RADIUS = 8

APP_NAME = "Rex spells"
ICON_REL_PATH = "assets/rex_icon.ico"

def resource_path(rel):
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
    else:
        base = os.path.abspath(".")
    return os.path.join(base, rel)

def load_app_icon():
    p = resource_path(ICON_REL_PATH)
    ico = QIcon(p)
    if ico.isNull():
        base_png = os.path.splitext(p)[0] + ".png"
        ico = QIcon()
        for sz in (16, 24, 32, 48, 64, 128, 256):
            cand = os.path.splitext(base_png)[0] + f"_{sz}.png"
            if os.path.exists(cand):
                ico.addFile(cand, QSize(sz, sz))
    if ico.isNull():
        ico = QApplication.style().standardIcon(QStyle.SP_ComputerIcon)
    return ico  # [web:611][web:694]

# --- Red / SSL / sesiones persistentes ---
urllib3.disable_warnings(InsecureRequestWarning)
SESSION_LOCAL = requests.Session(); SESSION_LOCAL.verify = False
SESSION_WEB   = requests.Session()

ADAPTER = HTTPAdapter(pool_connections=4, pool_maxsize=8, max_retries=2)
for _sess in (SESSION_LOCAL, SESSION_WEB):
    _sess.mount("https://", ADAPTER); _sess.mount("http://", ADAPTER)  # [web:667]

API_LOCAL = "https://127.0.0.1:2999/liveclientdata"
TO = (0.25, 0.5)

CD = {"Destello":300,"Prender":180,"Curar":240,"Barrera":180,"Limpiar":210,"Exhaust":210,"Ghost":210,"Teleport":360,"Smite":90}

CODE_TO_ES = {"SummonerFlash":"Destello","SummonerTeleport":"Teleport","SummonerDot":"Prender","SummonerHeal":"Curar",
              "SummonerBarrier":"Barrera","SummonerBoost":"Limpiar","SummonerExhaust":"Exhaust","SummonerHaste":"Ghost","SummonerSmite":"Smite"}

VISIBLE_TO_CODE = {"destello":"SummonerFlash","flash":"SummonerFlash","teleport":"SummonerTeleport","teletransporte":"SummonerTeleport",
                   "prender":"SummonerDot","ignite":"SummonerDot","curar":"SummonerHeal","heal":"SummonerHeal","barrera":"SummonerBarrier",
                   "barrier":"SummonerBarrier","limpiar":"SummonerBoost","cleanse":"SummonerBoost","exhaust":"SummonerExhaust",
                   "agotamiento":"SummonerExhaust","ghost":"SummonerHaste","fantasmal":"SummonerHaste","smite":"SummonerSmite","castigo":"SummonerSmite"}

DD_CHAMP_EXC = {"Kai'Sa":"Kaisa","Cho'Gath":"Chogath","Vel'Koz":"Velkoz","Kha'Zix":"Khazix","LeBlanc":"Leblanc",
                "Kog'Maw":"KogMaw","Rek'Sai":"RekSai","Wukong":"MonkeyKing","Dr. Mundo":"DrMundo","Jarvan IV":"JarvanIV",
                "Lee Sin":"LeeSin","Master Yi":"MasterYi","Miss Fortune":"MissFortune","Twisted Fate":"TwistedFate",
                "Xin Zhao":"XinZhao","Aurelion Sol":"AurelionSol","Tahm Kench":"TahmKench","Renata Glasc":"Renata",
                "Nunu & Willump":"Nunu","Bel'Veth":"Belveth","K'Sante":"KSante"}

def extract_code_and_label(sp):
    raw=(sp.get("rawDisplayName") or "")+" "+(sp.get("rawDescription") or "")
    for code in CODE_TO_ES:
        if code in raw: return code, CODE_TO_ES[code]
    vis=(sp.get("displayName") or "").strip().lower()
    if vis in VISIBLE_TO_CODE:
        c=VISIBLE_TO_CODE[vis]; return c, CODE_TO_ES.get(c, vis.title())
    return "SummonerFlash","Destello"

def norm_champ(name:str)->str:
    if name in DD_CHAMP_EXC: return DD_CHAMP_EXC[name]
    parts=re.sub(r"[^A-Za-z0-9 ]","",name).split()
    return "".join(p[:1].upper()+p[1:] for p in parts)

def circular_icon_from_image(img:QImage, size:int)->QIcon:
    pm=QPixmap(size, size); pm.fill(Qt.transparent)
    p = QPainter(pm); p.setRenderHint(QPainter.Antialiasing, True)
    path = QPainterPath(); path.addEllipse(0,0,size,size)
    p.setClipPath(path)
    p.drawImage(QRectF(0,0,size,size), img, QRectF(0,0,img.width(),img.height()))
    p.end()
    return QIcon(pm)

class DD:
    ver=None; cache={}
    @classmethod
    def ensure(cls):
        if cls.ver: return
        r=SESSION_WEB.get("https://ddragon.leagueoflegends.com/api/versions.json", timeout=2); r.raise_for_status()
        cls.ver=r.json()[0]
    @classmethod
    def icon(cls,url,size):
        key=(url,size)
        if key in cls.cache: return cls.cache[key]
        img=SESSION_WEB.get(url,timeout=3); img.raise_for_status()
        pm=QPixmap(); pm.loadFromData(img.content)
        pm=pm.scaled(QSize(size,size), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        ic=QIcon(pm); cls.cache[key]=ic; return ic
    @classmethod
    def spell(cls,code,size=20):
        cls.ensure(); url=f"https://ddragon.leagueoflegends.com/cdn/{cls.ver}/img/spell/{code}.png"
        try: return cls.icon(url,size)
        except Exception: return QIcon()
    @classmethod
    def champ(cls,name,size=22):
        cls.ensure()
        dd=norm_champ(name); url=f"https://ddragon.leagueoflegends.com/cdn/{cls.ver}/img/champion/{dd}.png"
        key=("champ_circ",url,size)
        if key in cls.cache: return cls.cache[key]
        try:
            r=SESSION_WEB.get(url,timeout=3); r.raise_for_status()
            img=QImage.fromData(r.content).convertToFormat(QImage.Format_RGBA8888)
            ic=circular_icon_from_image(img, size)
            cls.cache[key]=ic; return ic
        except Exception:
            return QIcon()

QSS = f"""
QFrame#Panel {{ background: rgba(24,24,28,190); border: 1px solid rgba(255,255,255,35); border-radius: {PANEL_RADIUS}px; }}
QFrame#Card  {{ background: rgba(30,30,34,165); border: 1px solid rgba(255,255,255,26); border-radius: 7px; }}

QToolButton {{ background: rgba(255,255,255,14); border: 1px solid rgba(255,255,255,38); border-radius: 6px; padding: 0px; }}
QToolButton:hover {{ background: rgba(255,255,255,22); }}
QToolButton#Champ {{ border-radius: 13px; background: rgba(255,255,255,8); }}

#TopBar {{ margin: 0px; }}
QToolButton#MinBtn, QToolButton#Lock, QToolButton#Cfg {{
    min-width: 18px; max-width: 18px; min-height: 18px; max-height: 18px;
    border-radius: 6px; padding: 0px; border: 1px solid rgba(255,255,255,38);
}}
QToolButton#MinBtn {{ background: rgba(130,130,130,160); }}
QToolButton#MinBtn:hover {{ background: rgba(130,130,130,200); }}
QToolButton#Cfg {{ background: rgba(100,149,237,170); }}
QToolButton#Cfg:hover {{ background: rgba(100,149,237,210); }}
QToolButton#Lock[locked="true"]  {{ background: rgba(244,67,54,200); }}
QToolButton#Lock[locked="false"] {{ background: rgba(76,175,80,200); }}
"""

class OutlineLabel(QLabel):
    def paintEvent(self, e):
        p = QPainter(self); p.setRenderHint(QPainter.TextAntialiasing, True)
        r = self.rect(); txt = self.text()
        if txt:
            p.setPen(QPen(QColor(0,0,0,255)))
            for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]: p.drawText(r.translated(dx,dy), Qt.AlignCenter, txt)
            p.setPen(QPen(QColor(255,255,255,255))); p.drawText(r, Qt.AlignCenter, txt)
        p.end()

class SpellButton(QToolButton):
    def __init__(self, on_clicked=lambda: None):
        super().__init__()
        self.setFixedSize(24,24)
        self.setIconSize(QSize(20,20))
        self.setCheckable(True)
        self.setFocusPolicy(Qt.NoFocus)
        self._end=None
        self._icon_normal=None
        self._txt = OutlineLabel("", self)
        self._txt.setStyleSheet("font: 10px 'Segoe UI'; font-weight: 700; letter-spacing: -0.2px;")
        self._txt.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self._veil = QLabel("", self)
        self._veil.setStyleSheet("background: rgba(0,0,0,110); border-radius: 6px;")
        self._veil.hide()
        self._veil.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self._veil.lower(); self._txt.raise_()
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.clicked.connect(on_clicked)
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.setDown(True); e.accept()
        super().mousePressEvent(e)
    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            inside = self.rect().contains(e.position().toPoint())
            self.setDown(False)
            if inside: self.click()
            e.accept()
        super().mouseReleaseEvent(e)
    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._txt.resize(self.size()); self._veil.resize(self.size()); self._veil.lower(); self._txt.raise_()
    def set_spell_icons(self, code:str):
        self._icon_normal = DD.spell(code); self.setIcon(self._icon_normal)
    def start_cd(self, seconds:int):
        self._end = datetime.utcnow() + timedelta(seconds=seconds)
        self.setChecked(True); self._veil.show(); self._veil.lower(); self._txt.raise_()
    def reset_ready(self):
        self._end=None; self.setChecked(False); self.setIcon(self._icon_normal); self._veil.hide(); self._txt.setText(""); self._txt.raise_()
    def tick(self):
        if self._end is None: return
        r=int((self._end - datetime.utcnow()).total_seconds())
        if r<=0: self.reset_ready()
        else: self._txt.setText(f"{r//60}:{r%60:02d}")

class Fila(QFrame):
    def __init__(self, on_any_click=lambda: None):
        super().__init__(); self.setObjectName("Card"); self.setFrameShape(QFrame.StyledPanel)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.champ = QToolButton(); self.champ.setObjectName("Champ"); self.champ.setIconSize(QSize(22,22))
        self.champ.setEnabled(True); self.champ.setFocusPolicy(Qt.NoFocus)
        self.champ.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.b1 = SpellButton(on_clicked=on_any_click); self.b2 = SpellButton(on_clicked=on_any_click)
        row=QHBoxLayout(self); row.setContentsMargins(6,5,6,5); row.setSpacing(6)
        row.addWidget(self.champ); row.addStretch(); row.addWidget(self.b1); row.addWidget(self.b2)
        self.lab1=None; self.lab2=None
        self.b1.clicked.connect(lambda: self.toggle(1)); self.b2.clicked.connect(lambda: self.toggle(2))
        self.b1.clicked.connect(lambda: self.clearFocus()); self.b2.clicked.connect(lambda: self.clearFocus())
        self.timer=QTimer(self); self.timer.timeout.connect(self.tick); self.timer.start(250)
    def set_champ(self,name): self.champ.setIcon(DD.champ(name,22)); self.champ.setToolTip(name)
    def set_spells(self,o1,o2):
        c1,l1 = extract_code_and_label(o1); c2,l2 = extract_code_and_label(o2)
        self.lab1,self.lab2 = l1,l2; self.b1.set_spell_icons(c1); self.b2.set_spell_icons(c2)
        self.b1.setToolTip(l1 or ""); self.b2.setToolTip(l2 or "")
    def toggle(self, which):
        if which==1:
            if self.b1._end is None and self.lab1 in CD: self.b1.start_cd(CD[self.lab1])
            else: self.b1.reset_ready()
        else:
            if self.b2._end is None and self.lab2 in CD: self.b2.start_cd(CD[self.lab2])
            else: self.b2.reset_ready()
    def tick(self): self.b1.tick(); self.b2.tick()

class Overlay(QWidget):
    def __init__(self, tray_ref=None):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFocusPolicy(Qt.NoFocus)
        self.setWindowTitle(APP_NAME)

        self._settings = QSettings("RexSpells", "RexSpells")
        self._drag = None; self._locked = True; self._drag_enabled = False
        self._collapsed = False; self._expanded_size = None
        self._buttons_side = "right"; self._open_menu = None
        self._tray_ref = tray_ref  # weakref a QSystemTrayIcon global para no duplicar [web:694]

        QApplication.instance().installEventFilter(self)

        app_icon = load_app_icon(); self.setWindowIcon(app_icon)

        root=QVBoxLayout(self); root.setContentsMargins(OUTER_MARGIN,OUTER_MARGIN,OUTER_MARGIN,OUTER_MARGIN); root.setSpacing(0); root.setSizeConstraint(QLayout.SetFixedSize)
        self.panel=QFrame(); self.panel.setObjectName("Panel"); self.panel.setStyleSheet(QSS)
        p=QVBoxLayout(self.panel); p.setContentsMargins(8,8,8,8); p.setSpacing(5)
        sh=QGraphicsDropShadowEffect(self.panel); sh.setBlurRadius(12); sh.setOffset(0,3); sh.setColor(QColor(0,0,0,160)); self.panel.setGraphicsEffect(sh)

        self.top=QHBoxLayout(); self.top.setObjectName("TopBar"); self.top.setContentsMargins(0,0,0,0); self.top.setSpacing(5)
        self.btn_lock = QToolButton(); self.btn_lock.setObjectName("Lock"); self.btn_lock.setCheckable(True); self.btn_lock.setFocusPolicy(Qt.NoFocus)
        self.btn_min  = QToolButton(); self.btn_min.setObjectName("MinBtn"); self.btn_min.setFocusPolicy(Qt.NoFocus); self.btn_min.setText("–")
        self.btn_cfg  = QToolButton(); self.btn_cfg.setObjectName("Cfg");    self.btn_cfg.setFocusPolicy(Qt.NoFocus); self.btn_cfg.setText("⚙")
        self.btn_lock.setChecked(True); self._apply_lock_style()
        self._rebuild_top_bar(); p.addLayout(self.top)

        self.btn_lock.toggled.connect(self._toggle_lock)
        self.btn_min.clicked.connect(self._toggle_collapse)
        self.btn_cfg.clicked.connect(self._open_config_menu)

        self._pos_group = QActionGroup(self); self._pos_group.setExclusive(True)
        self._act_left  = QAction("Izquierda", self); self._act_left.setCheckable(True);  self._pos_group.addAction(self._act_left)
        self._act_right = QAction("Derecha",   self); self._act_right.setCheckable(True); self._pos_group.addAction(self._act_right)
        self._act_right.setChecked(True)
        self._act_left.triggered.connect(lambda checked: checked and self._apply_buttons_side("left"))
        self._act_right.triggered.connect(lambda checked: checked and self._apply_buttons_side("right"))

        self.content=QtWidget(); self.lc=QVBoxLayout(self.content); self.lc.setContentsMargins(0,0,0,0); self.lc.setSpacing(5)
        p.addWidget(self.content); root.addWidget(self.panel)

        self.rows=[]
        self._sig_last = None; self._in_game = False; self._empty_since = 0
        self._poll_fast_ms = 1200; self._poll_slow_ms = 6000; self._poll_fail_ms = 10000
        self._schedule_poll(self._poll_slow_ms)

        self.setMinimumWidth(158)
        saved_opacity = self._settings.value("window_opacity", 0.95, type=float)
        self.setWindowOpacity(max(0.3, min(1.0, saved_opacity)))

        self.show(); self._place_right_high(); self._clamp_to_screen()

    # ----- Bandeja / salida -----
    def _quit_from_tray(self):
        self._save_settings()
        tr = self._tray_ref() if self._tray_ref else None
        if tr: tr.hide()
        QApplication.quit()  # cierre correcto para eliminar el icono sin “fantasmas” [web:690]

    def _save_settings(self):
        self._settings.setValue("window_opacity", self.windowOpacity())

    def closeEvent(self, event):
        tr = self._tray_ref() if self._tray_ref else None
        if tr: tr.hide()
        self._save_settings(); event.accept()

    # ----- Posicionamiento / anclajes -----
    def _rebuild_top_bar(self):
        while self.top.count():
            item=self.top.takeAt(0); w=item.widget()
            if w: w.setParent(None)
        if self._buttons_side == "left":
            self.top.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.top.addWidget(self.btn_lock); self.top.addWidget(self.btn_min); self.top.addWidget(self.btn_cfg)
        else:
            self.top.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.top.addWidget(self.btn_cfg); self.top.addWidget(self.btn_min); self.top.addWidget(self.btn_lock)

    def _screen_geom(self):
        fg = self.frameGeometry()
        scr = QGuiApplication.screenAt(fg.center())
        return scr.availableGeometry() if scr else QGuiApplication.primaryScreen().availableGeometry()

    def _place_right_high(self):
        scr = self._screen_geom()
        x = scr.right() - self.width()
        y = scr.top() + int(scr.height()*0.18)
        self.move(x, y)

    def _clamp_to_screen(self):
        scr = self._screen_geom()
        nx = max(scr.left(), min(self.x(), scr.right()-self.width()))
        ny = max(scr.top(),  min(self.y(), scr.bottom()-self.height()))
        if nx!=self.x() or ny!=self.y(): self.move(nx, ny)

    def _anchor_point(self):
        fg = self.frameGeometry()
        return fg.topRight() if self._buttons_side == "right" else fg.topLeft()

    def _apply_with_anchor(self, fn):
        before = self._anchor_point(); fn(); after = self._anchor_point()
        dx = before.x() - after.x(); dy = before.y() - after.y()
        if dx or dy: self.move(self.x() + dx, self.y() + dy)
        self._clamp_to_screen(); QTimer.singleShot(0, self._clamp_to_screen)

    def _apply_preserving_top_left(self, fn):
        before = self.frameGeometry().topLeft(); fn(); after = self.frameGeometry().topLeft()
        dx = before.x() - after.x(); dy = before.y() - after.y()
        if dx or dy: self.move(self.x() + dx, self.y() + dy)
        self._clamp_to_screen(); QTimer.singleShot(0, self._clamp_to_screen)

    # ----- Arrastre / UI -----
    def enterEvent(self, e): self.unsetCursor(); e.accept()
    def leaveEvent(self, e): self.unsetCursor(); e.accept()
    def childEvent(self, ev):
        w = ev.child()
        if isinstance(w, QToolButton): w.setCursor(Qt.ArrowCursor)
        super().childEvent(ev)
    def mousePressEvent(self,e):
        if not self._drag_enabled or e.button()!=Qt.LeftButton: return
        self._drag=e.globalPosition().toPoint()
    def mouseMoveEvent(self,e):
        if not self._drag_enabled or self._drag is None: return
        delta=e.globalPosition().toPoint()-self._drag
        new_pos=self.pos()+delta
        scr = self._screen_geom()
        nx = max(scr.left(), min(new_pos.x(), scr.right()-self.width()))
        ny = max(scr.top(),  min(new_pos.y(), scr.bottom()-self.height()))
        self.move(QPoint(nx, ny)); self._drag=e.globalPosition().toPoint()
    def mouseReleaseEvent(self,e):
        if not self._drag_enabled: return
        self._drag=None
        scr = self._screen_geom()
        x, y = self.x(), self.y()
        if abs(x - scr.left()) < SNAP_DIST: x = scr.left()
        elif abs(scr.right() - self.width() - x) < SNAP_DIST: x = scr.right() - self.width()
        if abs(y - scr.top()) < SNAP_DIST: y = scr.top()
        elif abs(scr.bottom() - self.height() - y) < SNAP_DIST: y = scr.bottom() - self.height()
        self.move(x, y)
    def _apply_lock_style(self):
        if self.btn_lock.isChecked():
            self.btn_lock.setProperty("locked","true"); self.btn_lock.setText("🔒")
        else:
            self.btn_lock.setProperty("locked","false"); self.btn_lock.setText("🔓")
        self.btn_lock.style().unpolish(self.btn_lock); self.btn_lock.style().polish(self.btn_lock)
    def _toggle_lock(self):
        self._locked = self.btn_lock.isChecked(); self._drag_enabled = not self._locked
        self._apply_lock_style(); self.clearFocus()
    def _toggle_collapse(self):
        def act():
            if not self._collapsed:
                self._expanded_size = self.size(); self.content.hide(); self._collapsed = True
            else:
                self.content.show(); 
                if self._expanded_size: self.resize(self._expanded_size)
                self._collapsed = False
            self.panel.adjustSize(); self.adjustSize(); self.update()
        self._apply_with_anchor(act)

    # ----- Menú configuración -----
    def _open_config_menu(self):
        if self._open_menu: self._open_menu.close(); self._open_menu=None
        menu = QMenu(self); css = """
            QMenu, QMenu * { background: rgba(30,30,34,235); color:#FFFFFF; }
            QMenu { border: 1px solid rgba(255,255,255,40); padding: 4px; }
            QMenu::item { padding: 4px 22px 4px 8px; border-radius: 6px; }
            QMenu::item:selected { background: rgba(255,255,255,22); }
            QMenu::right-arrow { width: 10px; height: 10px; }
        """; menu.setStyleSheet(css)
        pos_menu = QMenu("Posición de los botones", menu); pos_menu.setStyleSheet(css)
        self._act_left.setChecked(self._buttons_side=="left"); self._act_right.setChecked(self._buttons_side!="left")
        pos_menu.clear(); pos_menu.addAction(self._act_left); pos_menu.addAction(self._act_right); menu.addMenu(pos_menu)
        w = QtWidget(menu); lay = QHBoxLayout(w); lay.setContentsMargins(8,6,8,6); lay.setSpacing(8)
        lab = QLabel("Opacidad", w); lab.setStyleSheet("color:#fff; font: 11px 'Segoe UI';")
        sld = QSlider(Qt.Horizontal, w); sld.setMinimum(30); sld.setMaximum(100); sld.setSingleStep(5); sld.setValue(int(self.windowOpacity()*100))
        sld.setStyleSheet("""
            QSlider::groove:horizontal { background: rgba(255,255,255,32); height: 4px; border-radius: 2px; }
            QSlider::sub-page:horizontal { background: #3b82f6; border-radius: 2px; }
            QSlider::add-page:horizontal { background: rgba(255,255,255,20); border-radius: 2px; }
            QSlider::handle:horizontal { background: #3b82f6; border: 1px solid rgba(255,255,255,60);
                                         width: 12px; height: 12px; margin: -5px 0; border-radius: 6px; }
        """); lay.addWidget(lab); lay.addWidget(sld)
        act_op = QWidgetAction(menu); act_op.setDefaultWidget(w); menu.addAction(act_op)
        sld.valueChanged.connect(lambda v: (self.setWindowOpacity(max(0.3, min(1.0, v/100.0))), self._settings.setValue("window_opacity", max(0.3, min(1.0, v/100.0)))))
        menu.addSeparator(); menu.addAction("Salir").triggered.connect(self._quit_from_tray)
        self._open_menu = menu; menu.popup(self.btn_cfg.mapToGlobal(self.btn_cfg.rect().bottomLeft())); self.clearFocus()
    def eventFilter(self, obj, ev):
        if self._open_menu and ev.type() in (QEvent.MouseButtonPress, QEvent.MouseButtonDblClick):
            gp = getattr(ev, "globalPosition", None)
            if gp:
                pt = gp().toPoint(); w = QApplication.widgetAt(pt); is_in_menu = False
                while w is not None:
                    if isinstance(w, QMenu): is_in_menu = True; break
                    w = w.parentWidget()
                if not is_in_menu: self._open_menu.close()
        return super().eventFilter(obj, ev)

    # ----- Polling adaptativo -----
    def _schedule_poll(self, ms:int):
        QTimer.singleShot(ms, self._poll_once)  # programa próximo tick dinámicamente [web:662]

    def _signature_state(self, enemies:list)->str:
        parts=[]
        for p in enemies:
            c=p.get("championName",""); s=p.get("summonerSpells",{})
            a=(s.get("summonerSpellOne",{}) or {}).get("displayName","")
            b=(s.get("summonerSpellTwo",{}) or {}).get("displayName","")
            parts.append(f"{c}|{a}|{b}")
        return sha1("|".join(parts).encode("utf-8")).hexdigest()

    def _poll_once(self):
        try:
            r = SESSION_LOCAL.get(f"{API_LOCAL}/allgamedata", timeout=TO)
            if r.status_code != 200:
                self._empty_since += 1
                if self._empty_since >= 3: self._reset_ui(); self._sig_last = None
                self._schedule_poll(6000); return
            self._empty_since = 0; data = r.json()
            me=data.get("activePlayer",{}).get("summonerName"); team=None
            for p in data.get("allPlayers",[]):
                if p.get("summonerName")==me: team=p.get("team"); break
            if not team: self._reset_ui(); self._schedule_poll(6000); return
            enemies=[p for p in data.get("allPlayers",[]) if p.get("team")!=team]
            sig = self._signature_state(enemies)
            if sig != self._sig_last:
                self._sig_last = sig
                def act():
                    if len(enemies)!=len(self.rows):
                        for w in self.rows: w.setParent(None)
                        self.rows.clear()
                        for _ in range(len(enemies)):
                            f=Fila(on_any_click=lambda: None)
                            self.rows.append(f); self.lc.addWidget(f)
                    for i,row in enumerate(self.rows):
                        pe=enemies[i]; row.set_champ(pe.get("championName",""))
                        spells=pe.get("summonerSpells",{})
                        row.set_spells(spells.get("summonerSpellOne",{}) or {}, spells.get("summonerSpellTwo",{}) or {})
                    self.panel.adjustSize(); self.adjustSize(); self.update(); self._clamp_to_screen()
                self._apply_with_anchor(act)
            self._schedule_poll(1200)
        except Exception:
            self._schedule_poll(10000)

    # ----- Reset / posición botones -----
    def _apply_buttons_side(self, side:str):
        if side==self._buttons_side: return
        def act():
            self._buttons_side = side
            self._rebuild_top_bar(); self.panel.adjustSize(); self.adjustSize(); self.update()
        self._apply_preserving_top_left(act)

    def _reset_ui(self):
        for w in self.rows: w.setParent(None)
        self.rows.clear(); self.panel.adjustSize(); self.adjustSize(); self.update()

# ---------- Creación de TRAY GLOBAL en main (único) ----------
def create_tray(app, window_weak):
    tray = QSystemTrayIcon()  # sin parent para que viva aunque se oculte la ventana [web:694]
    tray.setIcon(load_app_icon()); tray.setToolTip(APP_NAME)
    tray_menu = QMenu()
    act_toggle = tray_menu.addAction("Mostrar/Ocultar")
    act_quit   = tray_menu.addAction("Salir")
    def toggle():
        w = window_weak()
        if w: w.setVisible(not w.isVisible())
    act_toggle.triggered.connect(toggle)
    act_quit.triggered.connect(QApplication.quit)
    tray.setContextMenu(tray_menu)
    def on_tray_activated(reason):
        if reason == QSystemTrayIcon.Trigger:
            toggle()
    tray.activated.connect(on_tray_activated)
    app.aboutToQuit.connect(lambda: (tray.hide(), tray.deleteLater()))  # limpieza correcta [web:690]
    tray.show()
    return tray

def main():
    app=QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setQuitOnLastWindowClosed(False)
    app.setWindowIcon(load_app_icon())

    shared_mem = QSharedMemory("RexSpellsUniqueLock")
    if not shared_mem.create(1):
        QMessageBox.warning(None, APP_NAME, "La aplicación ya está en ejecución.")
        sys.exit(0)

    # Crea ventana primero y luego tray único global
    w=Overlay()  # todavía sin tray
    tray = create_tray(app, weakref.ref(w))
    # pasa weakref del tray a la ventana (no crear otro)
    w._tray_ref = weakref.ref(tray)

    sys.exit(app.exec())

if __name__=="__main__":
    main()
