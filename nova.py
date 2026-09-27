from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math

# ─────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────
ARENA_SIZE   = 1550
SHIP_SPEED   = 13       
BULLET_SPEED = 14
MAX_BULLETS  = 500
MAX_LASERS   = 300

# ─────────────────────────────────────────────
#  CAMERA
# ─────────────────────────────────────────────
camera_mode = 0

# ─────────────────────────────────────────────
#  GAME STATE  (added intro)
# ─────────────────────────────────────────────
# game_state: 'intro' | 'playing'
game_state = 'intro'

# ─────────────────────────────────────────────
#  SHIP STATE
# ─────────────────────────────────────────────
ship_x      = 0.0
ship_y      = -300.0
ship_z      = 30.0
ship_angle  = 90.0
ship_tilt   = 0.0
target_tilt = 0.0

# ─────────────────────────────────────────────
#  BOOST STATE
# ─────────────────────────────────────────────
boost_active    = False
boost_timer     = 0
boost_cooldown  = 0
BOOST_DURATION  = 90
BOOST_COOLDOWN  = 180
BOOST_SPEED     = 22
BOOST_AUTO_SPD  = 10

auto_fire         = False
auto_fire_timer   = 0
AUTO_FIRE_INTERVAL = 15

invincible            = False
invincible_timer      = 0
invincible_start_time = 0
INVINCIBLE_SECONDS    = 25
invincible_pulse      = 0

# ─────────────────────────────────────────────
#  WEAPONS STATE
# ─────────────────────────────────────────────
bullet_count     = MAX_BULLETS
laser_uses       = MAX_LASERS
bullets          = []
bullet_add_count = 0

canon_cooldown      = 0
CANON_COOLDOWN_TIME = 40

# ─────────────────────────────────────────────
#  GAME STATE
# ─────────────────────────────────────────────
score     = 0
player_hp = 10
game_over = False
paused    = False

# ─────────────────────────────────────────────
#  ENEMIES
# ─────────────────────────────────────────────
aliens               = []
alien_timer          = 0
ALIEN_SPAWN_INTERVAL = 300
MAX_ALIENS           = 6
alien_speed_multiplier = 1.0

# ─────────────────────────────────────────────
#  ASTEROIDS
# ─────────────────────────────────────────────
asteroids               = []
asteroid_timer          = 0
ASTEROID_SPAWN_INTERVAL = 300
MAX_ASTEROIDS           = 2

# ─────────────────────────────────────────────
#  FUEL SYSTEM
# ─────────────────────────────────────────────
fuel             = 100.0
FUEL_DRAIN       = 0.008
BOOST_FUEL_DRAIN = 0.06
fuel_containers  = []
fuel_spawn_timer = 0
FUEL_SPAWN_INTERVAL = 300

# ─────────────────────────────────────────────
#  STARS
# ─────────────────────────────────────────────
random.seed(700)   ##for star  to be in random places 
stars_far = [
    (random.uniform(-4000, 4000),
     random.uniform(-4000, 4000),
     random.uniform(-800,  2500))
    for _ in range(1500)
]
stars_mid = [
    (random.uniform(-3000, 3000),
     random.uniform(-3000, 3000),
     random.uniform(-500,  1500))
    for _ in range(600)
]
stars_near = [
    (random.uniform(-2000, 2000),
     random.uniform(-2000, 2000),
     random.uniform(  10,   700))
    for _ in range(200)
]


# ═══════════════════════════════════════════════
#  HELPERS     
#  trigonometry (cos/sin) converts a heading angle into an (x,y) direction vector
def get_forward(angle):   
    rad = math.radians(angle)
    return math.cos(rad), math.sin(rad)


def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def draw_text_col(x, y, text, r, g, b, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(r, g, b)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

#  Euclidean distance formula sqrt((x2-x1)^2 + (y2-y1)^2) used for all 2D collision detection
def dist2d(ax, ay, bx, by):
    return math.sqrt((ax - bx)**2 + (ay - by)**2)

#  HUD Display
def draw_bar(x, y, w, h, fraction, r_fill, g_fill, b_fill, label="", show_pct=False):
    fraction = max(0.0, min(1.0, fraction))   ##bar draw
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glDisable(GL_DEPTH_TEST)

    glColor3f(0.1, 0.1, 0.13)
    glBegin(GL_QUADS)
    glVertex3f(x,   y,   0); glVertex3f(x+w, y,   0)
    glVertex3f(x+w, y+h, 0); glVertex3f(x,   y+h, 0)
    glEnd()

    fw = w * fraction
    if fw > 1:
        glColor3f(r_fill, g_fill, b_fill)
        glBegin(GL_QUADS)
        glVertex3f(x,    y,   0); glVertex3f(x+fw, y,   0)
        glVertex3f(x+fw, y+h, 0); glVertex3f(x,    y+h, 0)
        glEnd()
        glColor3f(min(1,r_fill+0.3), min(1,g_fill+0.3), min(1,b_fill+0.3))
        glBegin(GL_QUADS)
        glVertex3f(x,    y+h-2, 0); glVertex3f(x+fw, y+h-2, 0)
        glVertex3f(x+fw, y+h,   0); glVertex3f(x,    y+h,   0)
        glEnd()

    glColor3f(0.5, 0.5, 0.55)
    glBegin(GL_LINES)
    glVertex3f(x,   y,   0); glVertex3f(x+w, y,   0)
    glVertex3f(x+w, y,   0); glVertex3f(x+w, y+h, 0)
    glVertex3f(x+w, y+h, 0); glVertex3f(x,   y+h, 0)
    glVertex3f(x,   y+h, 0); glVertex3f(x,   y,   0)
    glEnd()

    glEnable(GL_DEPTH_TEST)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    if label:
        draw_text_col(x - 52, y, label, 0.8, 0.8, 0.85, GLUT_BITMAP_HELVETICA_12)
    if show_pct:
        pct_str = f"{int(fraction*100)}%"
        draw_text_col(x + w//2 - 10, y + 2, pct_str, 1, 1, 1, GLUT_BITMAP_HELVETICA_12)


# ═══════════════════════════════════════════════
#  INTRO SCREEN  
# ═══════════════════════════════════════════════
def draw_intro():  ##black background
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glDisable(GL_DEPTH_TEST)

    # Semi-transparent dark overlay 
    glColor3f(0.0, 0.0, 0.04)
    glBegin(GL_QUADS)
    glVertex3f(0,   0,   0); glVertex3f(1000, 0,   0)
    glVertex3f(1000, 800, 0); glVertex3f(0,   800, 0)
    glEnd()

    # ── Title box ──
    glColor3f(0.0, 0.12, 0.05)
    glBegin(GL_QUADS)
    glVertex3f(150, 500, 0); glVertex3f(850, 500, 0)
    glVertex3f(850, 630, 0); glVertex3f(150, 630, 0)
    glEnd()
    # Title box border (bright green)
    glColor3f(0.0, 0.85, 0.35)
    glBegin(GL_LINES)
    glVertex3f(150, 500, 0); glVertex3f(850, 500, 0)
    glVertex3f(850, 500, 0); glVertex3f(850, 630, 0)
    glVertex3f(850, 630, 0); glVertex3f(150, 630, 0)
    glVertex3f(150, 630, 0); glVertex3f(150, 500, 0)
    glEnd()

    # ── Subtitle box ──
    glColor3f(0.0, 0.08, 0.03)
    glBegin(GL_QUADS)
    glVertex3f(300, 440, 0); glVertex3f(700, 440, 0)
    glVertex3f(700, 478, 0); glVertex3f(300, 478, 0)
    glEnd()

    # ── Enter prompt box ──  ##press enter
    glColor3f(0.0, 0.1, 0.04)
    glBegin(GL_QUADS)
    glVertex3f(300, 340, 0); glVertex3f(700, 340, 0)
    glVertex3f(700, 388, 0); glVertex3f(300, 388, 0)
    glEnd()
    glColor3f(0.0, 0.7, 0.3)
    glBegin(GL_LINES)
    glVertex3f(300, 340, 0); glVertex3f(700, 340, 0)
    glVertex3f(700, 340, 0); glVertex3f(700, 388, 0)
    glVertex3f(700, 388, 0); glVertex3f(300, 388, 0)
    glVertex3f(300, 388, 0); glVertex3f(300, 340, 0)
    glEnd()

    # ── Controls hint box ──
    glColor3f(0.0, 0.06, 0.02)
    glBegin(GL_QUADS)
    glVertex3f(100, 160, 0); glVertex3f(900, 160, 0)
    glVertex3f(900, 310, 0); glVertex3f(100, 310, 0)
    glEnd()
    glColor3f(0.0, 0.45, 0.2)
    glBegin(GL_LINES)
    glVertex3f(100, 160, 0); glVertex3f(900, 160, 0)
    glVertex3f(900, 160, 0); glVertex3f(900, 310, 0)
    glVertex3f(900, 310, 0); glVertex3f(100, 310, 0)
    glVertex3f(100, 310, 0); glVertex3f(100, 160, 0)
    glEnd()

    glEnable(GL_DEPTH_TEST)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    # ── Text ──
    # Big title
    draw_text_col(255, 560, "NOVA  SIEGE", 0.15, 1.0, 0.45, GLUT_BITMAP_TIMES_ROMAN_24)

    # Subtitle
    draw_text_col(370, 452, "Space  Shooter", 0.4, 0.85, 0.55, GLUT_BITMAP_HELVETICA_18)

    # Enter prompt
    draw_text_col(345, 356, "Press  ENTER  to  Start", 0.2, 1.0, 0.5, GLUT_BITMAP_HELVETICA_18)

    # Controls
    draw_text_col(200, 288, "CONTROLS", 0.2, 0.9, 0.45, GLUT_BITMAP_HELVETICA_18)
    draw_text_col(145, 258, "ARROWS = Move / Rotate          A = Left Laser", 0.55, 0.85, 0.65, GLUT_BITMAP_HELVETICA_12)
    draw_text_col(145, 235, "S = Middle Shot                 D = Triple Shot", 0.55, 0.85, 0.65, GLUT_BITMAP_HELVETICA_12)
    draw_text_col(145, 212, "F = Canon Arc         SPACE = Boost    V = Auto-Fire", 0.55, 0.85, 0.65, GLUT_BITMAP_HELVETICA_12)
    draw_text_col(145, 189, "C = Invincible        B = +Ammo   P = Pause   R = Restart", 0.55, 0.85, 0.65, GLUT_BITMAP_HELVETICA_12)


# ═══════════════════════════════════════════════
#  Feature 2: SCI-FI ARENA & STAR FIELD
# ═══════════════════════════════════════════════
def draw_stars():
    glColor3f(0.45, 0.45, 0.65)
    glPointSize(1)
    glBegin(GL_POINTS)
    for s in stars_far:
        glVertex3f(*s)
    glEnd()
    glColor3f(0.85, 0.85, 1.0)
    glPointSize(2)
    glBegin(GL_POINTS)
    for s in stars_mid:
        glVertex3f(*s)
    glEnd()
    glColor3f(1.0, 1.0, 1.0)
    glPointSize(3)
    glBegin(GL_POINTS)
    for s in stars_near:
        glVertex3f(*s)
    glEnd()
    glPointSize(1)


def draw_floor():
    A = ARENA_SIZE
    glColor3f(0.0, 0.18, 0.25)
    glBegin(GL_QUADS)
    glVertex3f(-A, -A, -1)
    glVertex3f( A, -A, -1)
    glVertex3f( A,  A, -1)
    glVertex3f(-A,  A, -1)
    glEnd()
    glColor3f(0.0, 0.35, 0.4)
    step = 300
    coord = -A
    glBegin(GL_LINES)
    while coord <= A:
        glVertex3f(coord, -A, 0); glVertex3f(coord,  A, 0)
        glVertex3f(-A, coord, 0); glVertex3f( A, coord, 0)
        coord += step
    glEnd()


def draw_walls():
    A  = ARENA_SIZE
    EX = A + 50
    T  = 12
    HL = 2
    glColor3f(0.0, 0.95, 0.75)
    glBegin(GL_QUADS)
    glVertex3f(-EX,  A, 0); glVertex3f( EX,  A, 0)
    glVertex3f( EX,  A, T); glVertex3f(-EX,  A, T)
    glVertex3f(-EX, -A, 0); glVertex3f( EX, -A, 0)
    glVertex3f( EX, -A, T); glVertex3f(-EX, -A, T)
    glVertex3f( A, -EX, 0); glVertex3f( A,  EX, 0)
    glVertex3f( A,  EX, T); glVertex3f( A, -EX, T)
    glVertex3f(-A, -EX, 0); glVertex3f(-A,  EX, 0)
    glVertex3f(-A,  EX, T); glVertex3f(-A, -EX, T)
    glEnd()
    glColor3f(0.6, 1.0, 1.0)
    glBegin(GL_QUADS)
    glVertex3f(-EX,  A, T);    glVertex3f( EX,  A, T)
    glVertex3f( EX,  A, T+HL); glVertex3f(-EX,  A, T+HL)
    glVertex3f(-EX, -A, T);    glVertex3f( EX, -A, T)
    glVertex3f( EX, -A, T+HL); glVertex3f(-EX, -A, T+HL)
    glVertex3f( A, -EX, T);    glVertex3f( A,  EX, T)
    glVertex3f( A,  EX, T+HL); glVertex3f( A, -EX, T+HL)
    glVertex3f(-A, -EX, T);    glVertex3f(-A,  EX, T)
    glVertex3f(-A,  EX, T+HL); glVertex3f(-A, -EX, T+HL)
    glEnd()


# ═══════════════════════════════════════════════
#  PLANETS
# ═══════════════════════════════════════════════
def draw_planet_saturn(px, py, pz, radius):
    q = gluNewQuadric()
    glPushMatrix()
    glTranslatef(px, py, pz)
    glColor3f(0.95, 0.88, 0.6)
    gluSphere(q, radius, 18, 14)
    glColor3f(0.85, 0.72, 0.45)
    glPushMatrix()
    glRotatef(70, 1, 0.3, 0)
    gluCylinder(q, radius * 1.5, radius * 2.2, radius * 0.12, 20, 2)
    glPopMatrix()
    glColor3f(0.75, 0.62, 0.38)
    glPushMatrix()
    glRotatef(70, 1, 0.3, 0)
    gluCylinder(q, radius * 2.3, radius * 2.8, radius * 0.08, 20, 2)
    glPopMatrix()
    glColor3f(0.8, 0.7, 0.35)
    glPushMatrix()
    glTranslatef(radius * 0.4, radius * 0.3, radius * 0.85)
    gluSphere(q, radius * 0.18, 8, 6)
    glPopMatrix()
    glPopMatrix()


def draw_planet_neptune(px, py, pz, radius):
    q = gluNewQuadric()
    glPushMatrix()
    glTranslatef(px, py, pz)
    glColor3f(0.1, 0.2, 0.85)
    gluSphere(q, radius, 18, 14)
    glColor3f(0.3, 0.45, 0.95)
    glPushMatrix()
    glRotatef(20, 1, 0, 0)
    gluCylinder(q, radius * 0.98, radius * 0.98, radius * 0.18, 18, 1)
    glPopMatrix()
    glColor3f(0.55, 0.65, 1.0)
    glPushMatrix()
    glRotatef(-30, 1, 0, 0)
    glTranslatef(0, 0, radius * 0.2)
    gluCylinder(q, radius * 0.92, radius * 0.92, radius * 0.1, 16, 1)
    glPopMatrix()
    glColor3f(0.05, 0.08, 0.55)
    glPushMatrix()
    glTranslatef(-radius * 0.3, radius * 0.2, radius * 0.9)
    gluSphere(q, radius * 0.22, 8, 6)
    glPopMatrix()
    glPopMatrix()


def draw_planet_mars(px, py, pz, radius):
    q = gluNewQuadric()
    glPushMatrix()
    glTranslatef(px, py, pz)
    glColor3f(0.78, 0.28, 0.12)
    gluSphere(q, radius, 18, 14)
    glColor3f(0.92, 0.92, 0.95)
    glPushMatrix()
    glTranslatef(0, 0, radius * 0.82)
    gluSphere(q, radius * 0.32, 10, 8)
    glPopMatrix()
    glColor3f(0.55, 0.18, 0.08)
    glPushMatrix()
    glTranslatef(radius * 0.5, 0, radius * 0.75)
    gluSphere(q, radius * 0.25, 8, 6)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(-radius * 0.4, radius * 0.3, radius * 0.6)
    gluSphere(q, radius * 0.18, 7, 5)
    glPopMatrix()
    glPopMatrix()


def draw_planet_jupiter(px, py, pz, radius):
    q = gluNewQuadric()
    glPushMatrix()
    glTranslatef(px, py, pz)
    glColor3f(0.88, 0.72, 0.52)
    gluSphere(q, radius, 20, 16)
    band_colors = [
        (0.72, 0.48, 0.28), (0.82, 0.65, 0.45),
        (0.65, 0.42, 0.22), (0.78, 0.60, 0.40),
    ]
    offsets = [0.15, 0.35, -0.2, -0.4]
    widths  = [0.22, 0.15,  0.18,  0.12]
    for (rc, gc, bc), oz, bw in zip(band_colors, offsets, widths):
        glColor3f(rc, gc, bc)
        glPushMatrix()
        glRotatef(10, 1, 0, 0)
        glTranslatef(0, 0, oz * radius)
        gluCylinder(q, radius * 0.99, radius * 0.99, bw * radius, 20, 1)
        glPopMatrix()
    glColor3f(0.75, 0.22, 0.12)
    glPushMatrix()
    glTranslatef(radius * 0.6, 0, radius * 0.2)
    glScalef(1.6, 1.0, 1.0)
    gluSphere(q, radius * 0.22, 10, 8)
    glPopMatrix()
    glPopMatrix()


def draw_planets():
    A = ARENA_SIZE    ##these are used so that the plantes are in 4 diff side of the arena
    D = A + 600
    Z = 350
    R = 220
    draw_planet_saturn(  0,    D, Z, R)
    draw_planet_neptune( 0,   -D, Z, R)
    draw_planet_mars(    D,    0, Z, R * 0.85)
    draw_planet_jupiter(-D,    0, Z, R * 1.1)


# ═══════════════════════════════════════════════
#    Feature 3: ENGINE FIRE (Boost Effect)
# ═══════════════════════════════════════════════
def draw_engine_fire(scale=1.0):   ##default  continuos fire from the engine
    q = gluNewQuadric()
    glColor3f(1.0, 0.45, 0.0)
    glPushMatrix()
    glRotatef(180, 1, 0, 0)
    gluCylinder(q, 9 * scale, 0, 35 * scale, 8, 3)
    glPopMatrix()
    glColor3f(1.0, 0.9, 0.3)
    glPushMatrix()
    glRotatef(180, 1, 0, 0)
    gluCylinder(q, 5 * scale, 0, 22 * scale, 6, 2)
    glPopMatrix()
    glColor3f(1.0, 1.0, 0.9)
    glPushMatrix()
    glRotatef(180, 1, 0, 0)
    gluCylinder(q, 2 * scale, 0, 12 * scale, 5, 2)
    glPopMatrix()


# ═══════════════════════════════════════════════
#  Feature 9:INVINCIBLE ZONE RING  (replaces ship when invisible)
# ═══════════════════════════════════════════════
def draw_invincible_zone(pulse):
    
    ##Draw a flat glowing ring on the ground at the ship's position.
    ##Ship is hidden — only this ring shows the 'zone'.
    ##Three concentric rings that pulse in size/brightness.
    q = gluNewQuadric()
    p = (math.sin(pulse * 0.12) + 1.0) * 0.5   # for pulsing effect

    glPushMatrix()
    glTranslatef(ship_x, ship_y, 2)   # sit just above the floor

    # ── Outer ring ──
    R_outer = 110 + p * 20   ##radius set for outer
    glColor3f(0.0, 0.8 + p * 0.2, 1.0)
    N = 48
    for i in range(N):
        a1 = math.radians(i     * 360 / N)
        a2 = math.radians((i+1) * 360 / N)
        glBegin(GL_QUADS)
        glVertex3f((R_outer - 6) * math.cos(a1), (R_outer - 6) * math.sin(a1), 0)
        glVertex3f((R_outer + 6) * math.cos(a1), (R_outer + 6) * math.sin(a1), 0)
        glVertex3f((R_outer + 6) * math.cos(a2), (R_outer + 6) * math.sin(a2), 0)
        glVertex3f((R_outer - 6) * math.cos(a2), (R_outer - 6) * math.sin(a2), 0)
        glEnd()

    # ── Middle ring ──
    R_mid = 75 + p * 12  ##radius set for mid
    glColor3f(0.2, 1.0, 1.0)
    for i in range(N):
        a1 = math.radians(i     * 360 / N)
        a2 = math.radians((i+1) * 360 / N)
        glBegin(GL_QUADS)
        glVertex3f((R_mid - 4) * math.cos(a1), (R_mid - 4) * math.sin(a1), 0)
        glVertex3f((R_mid + 4) * math.cos(a1), (R_mid + 4) * math.sin(a1), 0)
        glVertex3f((R_mid + 4) * math.cos(a2), (R_mid + 4) * math.sin(a2), 0)
        glVertex3f((R_mid - 4) * math.cos(a2), (R_mid - 4) * math.sin(a2), 0)
        glEnd()

    # ── Inner ring ──
    R_inner = 38 + p * 8   ##radius set for inner
    glColor3f(0.6, 1.0, 1.0)
    for i in range(N):
        a1 = math.radians(i     * 360 / N)
        a2 = math.radians((i+1) * 360 / N)
        glBegin(GL_QUADS)
        glVertex3f((R_inner - 3) * math.cos(a1), (R_inner - 3) * math.sin(a1), 0)
        glVertex3f((R_inner + 3) * math.cos(a1), (R_inner + 3) * math.sin(a1), 0)
        glVertex3f((R_inner + 3) * math.cos(a2), (R_inner + 3) * math.sin(a2), 0)
        glVertex3f((R_inner - 3) * math.cos(a2), (R_inner - 3) * math.sin(a2), 0)
        glEnd()

    # ── Center dot ──
    glColor3f(0.8 + p * 0.2, 1.0, 1.0)
    gluSphere(gluNewQuadric(), 8 + p * 4, 10, 8)

    # Spoke lines from center to outer ring 
    glColor3f(0.0, 0.6 + p * 0.4, 0.9)
    spoke_count = 8  ##number of lines
    for i in range(spoke_count):
        ang = math.radians(i * 360 / spoke_count + pulse * 2)
        glBegin(GL_LINES)
        glVertex3f(10 * math.cos(ang), 10 * math.sin(ang), 1)
        glVertex3f((R_outer - 6) * math.cos(ang), (R_outer - 6) * math.sin(ang), 1)
        glEnd()

    glPopMatrix()


# ═══════════════════════════════════════════════
#  Feature 4:SPACESHIP
# ═══════════════════════════════════════════════
def draw_ship(x, y, z, angle, tilt):
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(angle - 90, 0, 0, 1)
    glRotatef(tilt, 0, 1, 0)
    glScalef(0.75, 0.75, 0.75)

    q = gluNewQuadric()

    # Main fuselage
    glColor3f(0.92, 0.92, 0.95)
    glPushMatrix()
    glRotatef(90, 1, 0, 0)
    gluCylinder(q, 12, 8, 80, 14, 5)
    glPopMatrix()
    glColor3f(0.85, 0.85, 0.9)
    glBegin(GL_QUADS)
    glVertex3f(-8, -30, 12); glVertex3f(8, -30, 12)
    glVertex3f(8,   50, 10); glVertex3f(-8, 50, 10)
    glEnd()
    glColor3f(0.12, 0.12, 0.18)
    glBegin(GL_QUADS)
    glVertex3f(-5, 20, 13); glVertex3f(5, 20, 13)
    glVertex3f(5,  45, 11); glVertex3f(-5, 45, 11)
    glEnd()

    # Nose
    glColor3f(0.75, 0.75, 0.8)
    glPushMatrix()
    glTranslatef(0, 75, 5)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(q, 8, 0.5, 35, 12, 4)
    glPopMatrix()
    glColor3f(0.3, 0.3, 0.35)
    glPushMatrix()
    glTranslatef(0, 108, 5)
    gluSphere(q, 3, 8, 8)
    glPopMatrix()

    # Left wing
    glColor3f(0.88, 0.88, 0.92)
    glBegin(GL_QUADS)
    glVertex3f(-12,  40,  4); glVertex3f(-90,  -5,  1)
    glVertex3f(-90, -25,  1); glVertex3f(-12, -30,  4)
    glEnd()
    glColor3f(0.65, 0.65, 0.7)
    glBegin(GL_QUADS)
    glVertex3f(-12,  40,  3); glVertex3f(-90,  -5,  0)
    glVertex3f(-90, -25,  0); glVertex3f(-12, -30,  3)
    glEnd()
    glColor3f(0.3, 0.3, 0.35)
    glBegin(GL_QUADS)
    glVertex3f(-12, 40, 4); glVertex3f(-90, -5, 1)
    glVertex3f(-90, -5, 0); glVertex3f(-12, 40, 3)
    glEnd()

    # Right wing
    glColor3f(0.88, 0.88, 0.92)
    glBegin(GL_QUADS)
    glVertex3f( 12,  40,  4); glVertex3f( 90,  -5,  1)
    glVertex3f( 90, -25,  1); glVertex3f( 12, -30,  4)
    glEnd()
    glColor3f(0.65, 0.65, 0.7)
    glBegin(GL_QUADS)
    glVertex3f( 12,  40,  3); glVertex3f( 90,  -5,  0)
    glVertex3f( 90, -25,  0); glVertex3f( 12, -30,  3)
    glEnd()
    glColor3f(0.3, 0.3, 0.35)
    glBegin(GL_QUADS)
    glVertex3f(12, 40, 4); glVertex3f(90, -5, 1)
    glVertex3f(90, -5, 0); glVertex3f(12, 40, 3)
    glEnd()

    # Left booster
    glColor3f(0.78, 0.78, 0.82)
    glPushMatrix()
    glTranslatef(-22, 10, 2)
    glRotatef(90, 1, 0, 0)
    gluCylinder(q, 7, 5, 65, 10, 3)
    glPopMatrix()
    glColor3f(0.6, 0.6, 0.65)
    glPushMatrix()
    glTranslatef(-22, 68, 2)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(q, 5, 0, 18, 8, 2)
    glPopMatrix()

    # Right booster
    glColor3f(0.78, 0.78, 0.82)
    glPushMatrix()
    glTranslatef(22, 10, 2)
    glRotatef(90, 1, 0, 0)
    gluCylinder(q, 7, 5, 65, 10, 3)
    glPopMatrix()
    glColor3f(0.6, 0.6, 0.65)
    glPushMatrix()
    glTranslatef(22, 68, 2)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(q, 5, 0, 18, 8, 2)
    glPopMatrix()

    # Engine block
    glColor3f(0.2, 0.2, 0.25)
    glPushMatrix()
    glTranslatef(0, -28, 2)
    glutSolidCube(22)
    glPopMatrix()

    # Nozzles
    glColor3f(0.35, 0.35, 0.4)
    for ex in [-9, 0, 9]:
        glPushMatrix()
        glTranslatef(ex, -40, 2)
        glRotatef(90, 1, 0, 0)
        gluCylinder(q, 6, 4, 14, 8, 2)
        glPopMatrix()

    # Engine fire
    if boost_active:   ####for the instant fire in the keyborad space fire boost
        fire_scale = 2.8
        for ex in [-9, 0, 9]:
            glPushMatrix()
            glTranslatef(ex, -54, 2)
            draw_engine_fire(fire_scale)
            glPopMatrix()
        glPushMatrix()
        glTranslatef(-22, -55, 2)
        draw_engine_fire(2.0)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(22, -55, 2)
        draw_engine_fire(2.0)
        glPopMatrix()
    else:
        for ex in [-9, 0, 9]:
            glPushMatrix()
            glTranslatef(ex, -54, 2)
            draw_engine_fire(0.4)
            glPopMatrix()

    # Left gun (A)
    glColor3f(0.5, 0.5, 0.55)
    glPushMatrix()
    glTranslatef(-80, -10, 2)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(q, 3, 2, 45, 7, 2)
    glPopMatrix()
    glColor3f(0.0, 0.9, 1.0)
    glPushMatrix()
    glTranslatef(-80, 35, 2)
    gluSphere(q, 3.5, 6, 6)
    glPopMatrix()

    # Middle gun (S)
    glColor3f(0.55, 0.55, 0.6)
    glPushMatrix()
    glTranslatef(0, 75, 4)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(q, 2.5, 1.5, 40, 7, 2)
    glPopMatrix()
    glColor3f(1.0, 0.6, 0.0)
    glPushMatrix()
    glTranslatef(0, 115, 4)
    gluSphere(q, 3.5, 6, 6)
    glPopMatrix()

    # Right gun (D)
    glColor3f(0.5, 0.5, 0.55)
    glPushMatrix()
    glTranslatef(80, -10, 2)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(q, 3, 2, 45, 7, 2)
    glPopMatrix()
    glColor3f(0.0, 0.9, 1.0)
    glPushMatrix()
    glTranslatef(80, 35, 2)
    gluSphere(q, 3.5, 6, 6)
    glPopMatrix()

    # Canon turret (F)
    glColor3f(0.7, 0.15, 0.1)
    glPushMatrix()
    glTranslatef(0, 10, 20)
    glutSolidCube(13)
    glPopMatrix()
    glColor3f(0.55, 0.1, 0.08)
    glPushMatrix()
    glTranslatef(0, 18, 24)
    glRotatef(-65, 1, 0, 0)
    gluCylinder(q, 3, 2, 30, 7, 2)
    glPopMatrix()

    glPopMatrix()


# ═══════════════════════════════════════════════
#  Feature 5:WEAPONS
# ═══════════════════════════════════════════════

#  left wing laser — perpendicular offset spawn, limited uses, no bullet cost
def fire_left_gun():  ##laser fire
    global laser_uses
    if laser_uses <= 0:
        return
    laser_uses -= 1
    dx, dy = get_forward(ship_angle)  ##helps the laser to emit from the ship
    px, py = -dy, dx
    bullets.append({'x': ship_x + px*35, 'y': ship_y + py*35, 'z': ship_z,
                    'dx': dx, 'dy': dy, 'dz': 0, 'type': 'laser', 'life': 40, 'trail': []})

#  middle gun — single orange bullet forward, costs 1 bullet
def fire_middle_gun():
    global bullet_count
    if bullet_count <= 0:
        return
    bullet_count -= 1
    dx, dy = get_forward(ship_angle)
    bullets.append({'x': ship_x + dx*50, 'y': ship_y + dy*50, 'z': ship_z,
                    'dx': dx, 'dy': dy, 'dz': 0, 'type': 'middle', 'life': 120, 'trail': []})


#  right gun — 3 bullets in angular spread, costs 3 bullets
def fire_right_gun():
    global bullet_count  
    if bullet_count < 3:
        return
    bullet_count -= 3
    dx, dy = get_forward(ship_angle)  #take diff possition of bullet
    px, py = -dy, dx
    for spread in [-0.12, 0.0, 0.12]:
        fdx = dx + px * spread
        fdy = dy + py * spread   ## take position to spread bullet intro diff sides
        n = math.sqrt(fdx*fdx + fdy*fdy)   ##math sqrt-inverse operation of squaring a num  
        bullets.append({'x': ship_x - px*35, 'y': ship_y - py*35, 'z': ship_z,
                        'dx': fdx/n, 'dy': fdy/n, 'dz': 0,
                        'type': 'right', 'life': 100, 'trail': []})


#  canon turret — arc projectile with dz gravity, costs 1, has cooldown
def fire_canon():
    global bullet_count, canon_cooldown
    if bullet_count <= 0 or canon_cooldown > 0:
        return
    bullet_count -= 1
    canon_cooldown = CANON_COOLDOWN_TIME  ##canon is emiited after a break,not continuos
    dx, dy = get_forward(ship_angle)   ##for the projectile angle 
    bullets.append({'x': ship_x, 'y': ship_y, 'z': ship_z + 20,
                    'dx': dx * 0.6, 'dy': dy * 0.6, 'dz': 0.4,
                    'type': 'canon', 'life': 160, 'trail': []})

#  moves all bullets each frame, applies gravity to canon, removes expired
def update_bullets():
    global canon_cooldown
    if canon_cooldown > 0:
        canon_cooldown -= 1
    dead = []  ##to store the emitted canon bullet
    for b in bullets:
        if b['type'] == 'canon':
            b['trail'].append((b['x'], b['y'], b['z']))
            if len(b['trail']) > 18:
                b['trail'].pop(0)
            b['dz'] -= 0.012
        b['x'] += b['dx'] * BULLET_SPEED
        b['y'] += b['dy'] * BULLET_SPEED
        b['z'] += b['dz'] * BULLET_SPEED
        b['life'] -= 1
        if b['life'] <= 0 or b['z'] < -10:
            dead.append(b)
    for b in dead:
        if b in bullets:
            bullets.remove(b)


def draw_bullets():
    q = gluNewQuadric()
    for b in bullets:
        glPushMatrix()
        glTranslatef(b['x'], b['y'], b['z'])
        if b['type'] == 'laser':
            glColor3f(0.0, 1.0, 1.0)
            ang = math.degrees(math.atan2(b['dy'], b['dx'])) ##math atan2-Math.atan2(y, x) calculates the counterclockwise angle \(\theta \) in radians between the positive x-axis and a point \((x, y)\)
            glPushMatrix()
            glRotatef(ang - 90, 0, 0, 1)
            glRotatef(90, 1, 0, 0)
            gluCylinder(gluNewQuadric(), 4, 4, 200, 8, 2)
            glPopMatrix()
        elif b['type'] == 'middle':
            glColor3f(1.0, 0.5, 0.0)
            ang = math.degrees(math.atan2(b['dy'], b['dx']))
            glPushMatrix()
            glRotatef(ang - 90, 0, 0, 1)
            glRotatef(90, 1, 0, 0)
            gluCylinder(gluNewQuadric(), 5, 3, 55, 8, 2)
            glPopMatrix()
            gluSphere(q, 7, 8, 8)
        elif b['type'] == 'right':
            glColor3f(1.0, 0.65, 0.1)
            ang = math.degrees(math.atan2(b['dy'], b['dx']))
            glPushMatrix()
            glRotatef(ang - 90, 0, 0, 1)
            glRotatef(90, 1, 0, 0)
            gluCylinder(gluNewQuadric(), 4, 2.5, 40, 8, 2)
            glPopMatrix()
            gluSphere(q, 5, 8, 8)
        elif b['type'] == 'canon':
            glColor3f(1.0, 0.15, 0.15)
            gluSphere(q, 12, 8, 8)
        glPopMatrix()
        if b['type'] == 'canon' and len(b['trail']) > 1:
            for i, (tx, ty, tz) in enumerate(b['trail']):
                alpha = (i + 1) / len(b['trail'])
                glPushMatrix()
                glTranslatef(tx, ty, tz)
                glColor3f(1.0 * alpha, 0.1, 0.1 * alpha)
                gluSphere(gluNewQuadric(), 3 + alpha * 6, 5, 5)
                glPopMatrix()


# ═══════════════════════════════════════════════
#  Feature 3:BOOST
# ═══════════════════════════════════════════════

#  sets boost flag + countdown; cooldown prevents immediate re-use
def activate_boost():
    global boost_active, boost_timer, boost_cooldown
    if boost_cooldown > 0 or boost_active or fuel <= 5:
        return
    boost_active = True  ##active boost 
    boost_timer  = BOOST_DURATION   ##for a certain amount of time

#  auto-moves ship forward every idle frame during boost, drains fuel
def update_boost():
    global boost_active, boost_timer, boost_cooldown, fuel, game_over, ship_x, ship_y
    if boost_active:
        boost_timer -= 1
        fuel = max(0, fuel - BOOST_FUEL_DRAIN)
        if fuel <= 0:
            game_over = True
            boost_active = False
            return
        A = ARENA_SIZE - 60
        dx, dy = get_forward(ship_angle)  #helps to move ship in a angle automatically
        ship_x = max(-A, min(A, ship_x + dx * BOOST_AUTO_SPD))
        ship_y = max(-A, min(A, ship_y + dy * BOOST_AUTO_SPD))
        if boost_timer <= 0:
            boost_active   = False
            boost_cooldown = BOOST_COOLDOWN
    elif boost_cooldown > 0:
        boost_cooldown -= 1

# auto_fire timer fires middle gun automatically when V is toggled on
def update_auto_fire():
    global auto_fire_timer
    if auto_fire and not game_over and not paused:
        auto_fire_timer += 1
        if auto_fire_timer >= AUTO_FIRE_INTERVAL:
            fire_middle_gun()
            auto_fire_timer = 0


# ═══════════════════════════════════════════════
#  Feature 9:INVINCIBLE
# ═══════════════════════════════════════════════
# proper wall-clock accurate countdown using glutGet(GLUT_ELAPSED_TIME) ,without this time runs out instantly
def update_invincible():
    global invincible, invincible_timer, invincible_pulse
    if invincible:
        elapsed = glutGet(GLUT_ELAPSED_TIME) - invincible_start_time  
        remaining_ms = INVINCIBLE_SECONDS * 1000 - elapsed
        invincible_timer = max(0, int(remaining_ms / 1000))
        invincible_pulse += 1
        if remaining_ms <= 0:  #if time runs out  
            invincible       = False
            invincible_timer = 0
            invincible_pulse = 0

#  boolean toggle; records glutGet timestamp on activation
def toggle_invincible():
    global invincible, invincible_timer, invincible_pulse, invincible_start_time
    if invincible:
        invincible       = False
        invincible_timer = 0
        invincible_pulse = 0
    else:
        invincible            = True
        invincible_start_time = glutGet(GLUT_ELAPSED_TIME)
        invincible_timer      = INVINCIBLE_SECONDS
        invincible_pulse      = 0


# ═══════════════════════════════════════════════
# Feature 7: ALIENS
# ═══════════════════════════════════════════════
def draw_normal_alien(x, y, z):
    q = gluNewQuadric()
    glPushMatrix()
    glTranslatef(x, y, z)
    glScalef(0.7, 0.7, 0.7)
    glColor3f(0.2, 0.65, 0.25)
    for lx in [-10, 10]:
        glPushMatrix()
        glTranslatef(lx, 0, 0)
        glRotatef(90, 1, 0, 0)
        gluCylinder(q, 4, 3, 28, 6, 2)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(lx, -28, 0)
        glScalef(1.4, 0.6, 1.0)
        gluSphere(q, 6, 7, 5)
        glPopMatrix()
    glColor3f(0.25, 0.72, 0.28)
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    gluCylinder(q, 10, 7, 35, 10, 4)
    glPopMatrix()
    glColor3f(0.2, 0.65, 0.25)
    glPushMatrix()
    glTranslatef(-13, 15, 8)
    glRotatef(40, 0, 0, 1)
    glRotatef(90, 1, 0, 0)
    gluCylinder(q, 3.5, 2.5, 28, 6, 2)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(-26, 30, 8)
    gluSphere(q, 6, 7, 6)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(13, 10, 8)
    glRotatef(-20, 0, 0, 1)
    glRotatef(90, 1, 0, 0)
    gluCylinder(q, 3.5, 2.5, 25, 6, 2)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(20, -12, 8)
    gluSphere(q, 6, 7, 6)
    glPopMatrix()
    glColor3f(0.28, 0.78, 0.3)
    glPushMatrix()
    glTranslatef(0, 0, 50)
    glScalef(1.1, 0.95, 1.25)
    gluSphere(q, 22, 14, 12)
    glPopMatrix()
    glColor3f(0.25, 0.72, 0.28)
    glPushMatrix()
    glTranslatef(0, 0, 36)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(q, 7, 9, 15, 8, 2)
    glPopMatrix()
    glColor3f(0.18, 0.05, 0.35)
    for ex in [-10, 10]:
        glPushMatrix()
        glTranslatef(ex, 18, 60)
        glScalef(1.5, 0.6, 1.1)
        gluSphere(q, 9, 10, 8)
        glPopMatrix()
    glColor3f(0.85, 0.85, 1.0)
    for ex in [-10, 10]:
        glPushMatrix()
        glTranslatef(ex + 2, 22, 65)
        gluSphere(q, 3, 5, 5)
        glPopMatrix()
    glColor3f(0.1, 0.4, 0.12)
    for nx in [-3, 3]:
        glPushMatrix()
        glTranslatef(nx, 18, 52)
        gluSphere(q, 2, 5, 5)
        glPopMatrix()
    glColor3f(0.1, 0.35, 0.12)
    glBegin(GL_QUADS)
    glVertex3f(-6, 16, 47); glVertex3f(6, 16, 47)
    glVertex3f(6,  17, 46); glVertex3f(-6, 17, 46)
    glEnd()
    glPopMatrix()


def draw_bird_alien(x, y, z, dx, dy_val): 
    glPushMatrix()
    glTranslatef(x, y, z)
    face_angle = math.degrees(math.atan2(dy_val, dx))
    glRotatef(face_angle - 90, 0, 0, 1)
    glScalef(0.7, 0.7, 0.7)
    q = gluNewQuadric()
    glColor3f(0.55, 0.0, 0.75)
    glPushMatrix()
    glScalef(0.7, 1.0, 0.5)
    glRotatef(90, 1, 0, 0)
    gluCylinder(q, 10, 4, 50, 10, 4)
    glPopMatrix()
    glColor3f(0.75, 0.0, 0.95)
    glPushMatrix()
    glTranslatef(0, 48, 0)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(q, 4, 0, 22, 8, 2)
    glPopMatrix()
    glColor3f(0.4, 0.0, 0.6)
    glBegin(GL_QUADS)
    glVertex3f( -8,  20,  6); glVertex3f(-100,  0,  0)
    glVertex3f(-100, -8,  0); glVertex3f( -8,   5,  4)
    glEnd()
    glColor3f(0.75, 0.1, 1.0)
    glBegin(GL_QUADS)
    glVertex3f(-8, 20, 6); glVertex3f(-100, 0, 0)
    glVertex3f(-100, 0,-1); glVertex3f(-8, 20, 5)
    glEnd()
    glColor3f(0.4, 0.0, 0.6)
    glBegin(GL_QUADS)
    glVertex3f( 8,  20,  6); glVertex3f(100,  0,  0)
    glVertex3f(100, -8,  0); glVertex3f( 8,   5,  4)
    glEnd()
    glColor3f(0.75, 0.1, 1.0)
    glBegin(GL_QUADS)
    glVertex3f(8, 20, 6); glVertex3f(100, 0, 0)
    glVertex3f(100, 0,-1); glVertex3f(8, 20, 5)
    glEnd()
    glColor3f(0.5, 0.0, 0.7)
    glBegin(GL_QUADS)
    glVertex3f(-5, -5, 4); glVertex3f(-25, -30, 1)
    glVertex3f(-20, -30, 1); glVertex3f(-3, -5, 6)
    glEnd()
    glBegin(GL_QUADS)
    glVertex3f(5, -5, 4); glVertex3f(25, -30, 1)
    glVertex3f(20, -30, 1); glVertex3f(3, -5, 6)
    glEnd()
    glColor3f(1.0, 0.85, 0.0)
    glPushMatrix()
    glTranslatef(0, 25, 6)
    gluSphere(q, 5, 8, 8)
    glPopMatrix()
    glColor3f(1.0, 0.4, 0.0)
    glPushMatrix()
    glTranslatef(0, 25, 9)
    gluSphere(q, 2.5, 6, 6)
    glPopMatrix()
    glPopMatrix()


def draw_aliens():
    for al in aliens:
        if al['type'] == 'normal':
            draw_normal_alien(al['x'], al['y'], al['z'])
        else:
            draw_bird_alien(al['x'], al['y'], al['z'], al['dx'], al['dy'])

# spawn position on arena edge, initial direction aimed at ship
def spawn_alien():
    if len(aliens) >= MAX_ALIENS:
        return
    atype = random.choice(['normal', 'bird'])
    A = ARENA_SIZE - 100
    if atype == 'normal':
        x = random.uniform(-A, A)
        y = A
    else:
        side = random.choice([-1, 1])
        x = side * A
        y = random.uniform(-A * 0.5, A * 0.5)

    ddx = ship_x - x   # these ddx ddy needed to identify the spaceship position and alien will go to them
    ddy = ship_y - y
    n = math.sqrt(ddx*ddx + ddy*ddy) or 1

    aliens.append({
        'x': x, 'y': y, 'z': 30,
        'type': atype,
        'speed': random.uniform(0.4, 0.9),
        'hp': 1,
        'dx': ddx/n, 'dy': ddy/n,
        'wander_dx': random.uniform(-1, 1),
        'wander_dy': random.uniform(-1, 1),
    })

#  lerp-based homing chase (0.02 blend); speed multiplier grows with elapsed time;
#            invincible mode makes aliens wander instead of chase
def update_aliens():
    global alien_timer, alien_speed_multiplier, game_over, player_hp, score
    alien_timer += 1
    if alien_timer >= ALIEN_SPAWN_INTERVAL:
        spawn_alien()
        alien_timer = 0

    alien_speed_multiplier = 1.0 + (glutGet(GLUT_ELAPSED_TIME) / 1000.0) * 0.001  # as time grows alien speed will increase

    dead = []
    A = ARENA_SIZE
    for al in aliens:
        if invincible:  # this helps alien to wander freely,not towards the spaceship in invincible mode
            al['x'] += al['wander_dx'] * al['speed'] * 0.5
            al['y'] += al['wander_dy'] * al['speed'] * 0.5
            if abs(al['x']) > A - 50:
                al['wander_dx'] *= -1
            if abs(al['y']) > A - 50:
                al['wander_dy'] *= -1
            al['x'] = max(-A, min(A, al['x']))
            al['y'] = max(-A, min(A, al['y']))
        else: # not invincible mode
            ddx = ship_x - al['x']    
            ddy = ship_y - al['y']  # spaceship position detect
            n = math.sqrt(ddx*ddx + ddy*ddy)
            if n > 1:
                target_dx = ddx / n
                target_dy = ddy / n  # when invincible mode gets off alien again chase spaceship
                al['dx'] += (target_dx - al['dx']) * 0.02
                al['dy'] += (target_dy - al['dy']) * 0.02
                nd = math.sqrt(al['dx']**2 + al['dy']**2)
                if nd > 0:
                    al['dx'] /= nd
                    al['dy'] /= nd
            al['x'] += al['dx'] * al['speed'] * alien_speed_multiplier
            al['y'] += al['dy'] * al['speed'] * alien_speed_multiplier
            al['x'] = max(-A, min(A, al['x']))
            al['y'] = max(-A, min(A, al['y']))

            if dist2d(al['x'], al['y'], ship_x, ship_y) < 45:  # euclidean is used to check alien  collision with player 
                player_hp -= 1
                dead.append(al)
                if player_hp <= 0:
                    game_over = True

        for b in bullets[:]:
            if dist2d(al['x'], al['y'], b['x'], b['y']) < 40 and abs(al['z'] - b['z']) < 40:
                al['hp'] -= 1  # euclidean is used to check bullet collision with alien
                if b in bullets:
                    bullets.remove(b)
                if al['hp'] <= 0:
                    dead.append(al)    # hits alien which add point
                    score += 10
                break

    for al in dead:
        if al in aliens:  # hitted alien removed from the list
            aliens.remove(al)


# ═══════════════════════════════════════════════
#   Feature 8: ARMORED ASTEROIDS
# ═══════════════════════════════════════════════
ASTEROID_COLORS = [
    (0.55, 0.55, 0.55),
    (1.0,  0.45, 0.0),
    (0.9,  0.1,  0.1),
]

#  spawns from top edge aimed at ship with random wander fallback
def spawn_asteroid():
    if len(asteroids) >= MAX_ASTEROIDS:
        return
    A = ARENA_SIZE - 100
    x = random.uniform(-A, A)
    y = A
    ddx = ship_x - x
    ddy = ship_y - y
    n = math.sqrt(ddx*ddx + ddy*ddy) or 1
    asteroids.append({
        'x': x, 'y': y, 'z': 30,
        'speed': random.uniform(0.5, 1.2),
        'hits': 0,
        'dx': ddx/n, 'dy': ddy/n,
        'rot': 0,
        'wander_dx': random.uniform(-1, 1),
        'wander_dy': random.uniform(-0.5, 0),
    })

#   3 hits to destroy; ASTEROID_COLORS changes per hit
def update_asteroids():
    global asteroid_timer, player_hp, game_over, score
    asteroid_timer += 1
    if asteroid_timer >= ASTEROID_SPAWN_INTERVAL:
        spawn_asteroid()
        asteroid_timer = 0

    dead = []
    A = ARENA_SIZE
    for ast in asteroids: # this helps astrnoids to wander freely,not towards the spaceship in invincible mode
        ast['rot'] += 0.8
        if invincible:  
            ast['x'] += ast['wander_dx'] * ast['speed'] * 0.4
            ast['y'] += ast['wander_dy'] * ast['speed'] * 0.4
            if abs(ast['x']) > A - 50:
                ast['wander_dx'] *= -1
            if abs(ast['y']) > A - 50:
                ast['wander_dy'] *= -1
            ast['x'] = max(-A, min(A, ast['x']))
            ast['y'] = max(-A, min(A, ast['y']))
        else:  # when invincible mode gets off alien again chase spaceship
            ddx = ship_x - ast['x']
            ddy = ship_y - ast['y']
            n = math.sqrt(ddx*ddx + ddy*ddy)
            if n > 1:
                target_dx = ddx / n
                target_dy = ddy / n
                ast['dx'] += (target_dx - ast['dx']) * 0.01
                ast['dy'] += (target_dy - ast['dy']) * 0.01
                nd = math.sqrt(ast['dx']**2 + ast['dy']**2)
                if nd > 0:
                    ast['dx'] /= nd
                    ast['dy'] /= nd
            ast['y'] += ast['dy'] * ast['speed']
            ast['x'] += ast['dx'] * ast['speed']

            if dist2d(ast['x'], ast['y'], ship_x, ship_y) < 50: # euclidean is used to check astrnoid  collision with player 
                player_hp -= 2
                dead.append(ast)
                if player_hp <= 0:
                    game_over = True

        for b in bullets[:]:
            if dist2d(ast['x'], ast['y'], b['x'], b['y']) < 50 and abs(ast['z'] - b['z']) < 40:
                ast['hits'] += 1    # euclidean is used to check bullet collision with astrnoid 
                if b in bullets:
                    bullets.remove(b)
                if ast['hits'] >= 3:
                    dead.append(ast)  # hits astrnoid  which add point
                    score += 5
                break

        if abs(ast['x']) > A + 300 or abs(ast['y']) > A + 300:
            dead.append(ast)

    for ast in dead:
        if ast in asteroids:
            asteroids.remove(ast)  # hitted astrnoid removed from the list


def draw_asteroids():
    for ast in asteroids:
        glPushMatrix()
        glTranslatef(ast['x'], ast['y'], ast['z'])
        glRotatef(ast['rot'], 0.5, 1, 0.3)
        glScalef(0.75, 0.75, 0.75)
        r, g, b = ASTEROID_COLORS[min(ast['hits'], 2)]  # for astrnoid 3 color for 3 hit
        glColor3f(r, g, b)
        glPushMatrix()
        glScalef(1.0, 0.85, 0.9)
        gluSphere(gluNewQuadric(), 55, 10, 8)
        glPopMatrix()
        glColor3f(r * 0.7, g * 0.7, b * 0.7)
        glPushMatrix()
        glTranslatef(30, 20, 20)
        gluSphere(gluNewQuadric(), 18, 6, 6)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(-25, -20, 15)
        gluSphere(gluNewQuadric(), 14, 6, 6)
        glPopMatrix()
        glPopMatrix()


# ═══════════════════════════════════════════════
#  Feature 9: FUEL CONTAINERS 
# ═══════════════════════════════════════════════

# fuel drains each frame; one rotating container spawns at a time;
#            bullet hit restores +20% fuel
def update_fuel():
    global fuel, fuel_spawn_timer, game_over
    if not paused and not boost_active:
        fuel = max(0, fuel - FUEL_DRAIN)
        if fuel <= 0:  # fuel ends,game over
            game_over = True

    fuel_spawn_timer += 1
    if fuel_spawn_timer >= FUEL_SPAWN_INTERVAL and len(fuel_containers) == 0:
        A = ARENA_SIZE - 200
        fuel_containers.append({'x': random.uniform(-A, A), 'y': random.uniform(-A, A),
                                 'z': 30, 'rot': 0})  # helps fuel to spawn at random position in the arena
        fuel_spawn_timer = 0

    for fc in fuel_containers:
        fc['rot'] = (fc['rot'] + 1.5) % 360

    dead_fc = []
    for fc in fuel_containers:
        for b in bullets[:]:
            if dist2d(fc['x'], fc['y'], b['x'], b['y']) < 40 and abs(fc['z'] - b['z']) < 40:
                fuel = min(100, fuel + 20)  # euclidean is used to check bullet collision with fuel,if bullet hits fuel restore 20%
                if b in bullets:
                    bullets.remove(b)
                dead_fc.append(fc) # hitted feul append to fuel list
                break
    for fc in dead_fc:
        if fc in fuel_containers:
            fuel_containers.remove(fc)  # hitted fuel removed from the list


def draw_fuel_containers():
    for fc in fuel_containers:
        glPushMatrix()
        glTranslatef(fc['x'], fc['y'], fc['z'])
        glRotatef(fc['rot'], 0, 0, 1)
        glRotatef(fc['rot'] * 0.5, 1, 0, 0)
        glColor3f(0.9, 0.1, 0.1)
        glutSolidCube(35)
        glColor3f(1.0, 0.85, 0.0)
        s = 18
        edges = [
            (-s,-s, s,  s,-s, s), ( s,-s, s,  s, s, s),
            ( s, s, s, -s, s, s), (-s, s, s, -s,-s, s),
            (-s,-s,-s,  s,-s,-s), ( s,-s,-s,  s, s,-s),
            ( s, s,-s, -s, s,-s), (-s, s,-s, -s,-s,-s),
            (-s,-s,-s, -s,-s, s), ( s,-s,-s,  s,-s, s),
            ( s, s,-s,  s, s, s), (-s, s,-s, -s, s, s),
        ]
        glBegin(GL_LINES)
        for sx, sy, sz, ex, ey, ez in edges:
            glVertex3f(sx, sy, sz); glVertex3f(ex, ey, ez)
        glEnd()
        glColor3f(1.0, 0.5, 0.0)
        gluSphere(gluNewQuadric(), 8, 8, 8)
        glPopMatrix()


# ═══════════════════════════════════════════════
#  Feature 1: COCKPIT OVERLAY   for the 1st person mode
# ═══════════════════════════════════════════════
def draw_steering_wheel():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glDisable(GL_DEPTH_TEST)

    cx, cy = 500, 95
    R_out = 52
    R_in  = 44
    glColor3f(0.22, 0.22, 0.28)
    N = 24
    for i in range(N):
        a1 = math.radians(i     * 360 / N)
        a2 = math.radians((i+1) * 360 / N)
        glBegin(GL_QUADS)
        glVertex3f(cx + R_in  * math.cos(a1), cy + R_in  * math.sin(a1), 0)
        glVertex3f(cx + R_out * math.cos(a1), cy + R_out * math.sin(a1), 0)
        glVertex3f(cx + R_out * math.cos(a2), cy + R_out * math.sin(a2), 0)
        glVertex3f(cx + R_in  * math.cos(a2), cy + R_in  * math.sin(a2), 0)
        glEnd()

    glColor3f(0.45, 0.45, 0.52)
    for i in range(6, 18):
        a1 = math.radians(i     * 360 / N)
        a2 = math.radians((i+1) * 360 / N)
        glBegin(GL_QUADS)
        glVertex3f(cx + R_in       * math.cos(a1), cy + R_in       * math.sin(a1), 0)
        glVertex3f(cx + (R_in+3)   * math.cos(a1), cy + (R_in+3)   * math.sin(a1), 0)
        glVertex3f(cx + (R_in+3)   * math.cos(a2), cy + (R_in+3)   * math.sin(a2), 0)
        glVertex3f(cx + R_in       * math.cos(a2), cy + R_in       * math.sin(a2), 0)
        glEnd()

    glColor3f(0.28, 0.28, 0.35)
    for sa in [90, 210, 330]:
        rad  = math.radians(sa)
        sx   = cx + R_in * math.cos(rad)
        sy   = cy + R_in * math.sin(rad)
        perp = math.radians(sa + 90)
        w = 4
        px2 = w * math.cos(perp)
        py2 = w * math.sin(perp)
        glBegin(GL_QUADS)
        glVertex3f(cx - px2, cy - py2, 0)
        glVertex3f(cx + px2, cy + py2, 0)
        glVertex3f(sx + px2, sy + py2, 0)
        glVertex3f(sx - px2, sy - py2, 0)
        glEnd()

    glColor3f(0.35, 0.35, 0.42)
    hub_r = 10
    for i in range(N):
        a1 = math.radians(i     * 360 / N)
        a2 = math.radians((i+1) * 360 / N)
        glBegin(GL_QUADS)
        glVertex3f(cx, cy, 0)
        glVertex3f(cx + hub_r * math.cos(a1), cy + hub_r * math.sin(a1), 0)
        glVertex3f(cx + hub_r * math.cos(a2), cy + hub_r * math.sin(a2), 0)
        glVertex3f(cx, cy, 0)
        glEnd()

    glColor3f(0.18, 0.18, 0.22)
    glBegin(GL_QUADS)
    glVertex3f(cx-6, cy-R_out, 0); glVertex3f(cx+6, cy-R_out, 0)
    glVertex3f(cx+6, 0,        0); glVertex3f(cx-6, 0,        0)
    glEnd()

    glEnable(GL_DEPTH_TEST)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def draw_cockpit_overlay():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glDisable(GL_DEPTH_TEST)

    W, H = 1000, 800
    LR  = 130
    BOT = 155
    TOP = 70

    glColor3f(0.88, 0.88, 0.9)
    glBegin(GL_QUADS)
    glVertex3f(0, 0, 0);   glVertex3f(W, 0, 0)
    glVertex3f(W, BOT, 0); glVertex3f(0, BOT, 0)
    glEnd()
    glBegin(GL_QUADS)
    glVertex3f(0, H-TOP, 0); glVertex3f(W, H-TOP, 0)
    glVertex3f(W, H, 0);     glVertex3f(0, H, 0)
    glEnd()
    glBegin(GL_QUADS)
    glVertex3f(0, 0, 0);   glVertex3f(LR, 0, 0)
    glVertex3f(LR, H, 0);  glVertex3f(0, H, 0)
    glEnd()
    glBegin(GL_QUADS)
    glVertex3f(W-LR, 0, 0); glVertex3f(W, 0, 0)
    glVertex3f(W, H, 0);    glVertex3f(W-LR, H, 0)
    glEnd()

    glColor3f(0.7, 0.7, 0.75)
    glBegin(GL_QUADS)
    glVertex3f(0, H//2-1, 0); glVertex3f(LR, H//2-1, 0)
    glVertex3f(LR, H//2+1, 0); glVertex3f(0, H//2+1, 0)
    glEnd()
    glBegin(GL_QUADS)
    glVertex3f(W-LR, H//2-1, 0); glVertex3f(W, H//2-1, 0)
    glVertex3f(W, H//2+1, 0); glVertex3f(W-LR, H//2+1, 0)
    glEnd()

    glColor3f(0.6, 0.6, 0.65)
    for ry in [BOT+30, BOT+80, H-TOP-30, H-TOP-80]:
        for rx in [15, W-LR+15]:
            glBegin(GL_QUADS)
            glVertex3f(rx+12, ry-3, 0); glVertex3f(rx+18, ry-3, 0)
            glVertex3f(rx+18, ry+3, 0); glVertex3f(rx+12, ry+3, 0)
            glEnd()

    glColor3f(0.18, 0.18, 0.22)
    BW = 6
    glBegin(GL_QUADS)
    glVertex3f(LR, H-TOP-BW, 0); glVertex3f(W-LR, H-TOP-BW, 0)
    glVertex3f(W-LR, H-TOP, 0);  glVertex3f(LR, H-TOP, 0)
    glEnd()
    glBegin(GL_QUADS)
    glVertex3f(LR, BOT, 0);      glVertex3f(W-LR, BOT, 0)
    glVertex3f(W-LR, BOT+BW, 0); glVertex3f(LR, BOT+BW, 0)
    glEnd()
    glBegin(GL_QUADS)
    glVertex3f(LR, BOT, 0);      glVertex3f(LR+BW, BOT, 0)
    glVertex3f(LR+BW, H-TOP, 0); glVertex3f(LR, H-TOP, 0)
    glEnd()
    glBegin(GL_QUADS)
    glVertex3f(W-LR-BW, BOT, 0); glVertex3f(W-LR, BOT, 0)
    glVertex3f(W-LR, H-TOP, 0);  glVertex3f(W-LR-BW, H-TOP, 0)
    glEnd()

    glColor3f(0.4, 0.4, 0.45)
    for bx, by in [(LR, BOT), (W-LR, BOT), (LR, H-TOP), (W-LR, H-TOP)]:
        glBegin(GL_QUADS)
        glVertex3f(bx-7, by-7, 0); glVertex3f(bx+7, by-7, 0)
        glVertex3f(bx+7, by+7, 0); glVertex3f(bx-7, by+7, 0)
        glEnd()
    glColor3f(0.7, 0.7, 0.75)
    for bx, by in [(LR, BOT), (W-LR, BOT), (LR, H-TOP), (W-LR, H-TOP)]:
        glBegin(GL_QUADS)
        glVertex3f(bx-3, by-3, 0); glVertex3f(bx+3, by-3, 0)
        glVertex3f(bx+3, by+3, 0); glVertex3f(bx-3, by+3, 0)
        glEnd()

    glColor3f(0.55, 0.55, 0.6)
    glBegin(GL_QUADS)
    glVertex3f(0, BOT-4, 0); glVertex3f(W, BOT-4, 0)
    glVertex3f(W, BOT, 0);   glVertex3f(0, BOT, 0)
    glEnd()

    glColor3f(0.1, 0.1, 0.15)
    for gx in [200, 800]:
        glBegin(GL_QUADS)
        glVertex3f(gx-70, 12, 0); glVertex3f(gx+70, 12, 0)
        glVertex3f(gx+70, BOT-8, 0); glVertex3f(gx-70, BOT-8, 0)
        glEnd()
        glColor3f(0.4, 0.4, 0.48)
        glBegin(GL_QUADS)
        glVertex3f(gx-72, 10, 0); glVertex3f(gx+72, 10, 0)
        glVertex3f(gx+72, 13, 0); glVertex3f(gx-72, 13, 0)
        glVertex3f(gx-72, BOT-8, 0); glVertex3f(gx+72, BOT-8, 0)
        glVertex3f(gx+72, BOT-5, 0); glVertex3f(gx-72, BOT-5, 0)
        glVertex3f(gx-72, 10, 0); glVertex3f(gx-69, 10, 0)
        glVertex3f(gx-69, BOT-5, 0); glVertex3f(gx-72, BOT-5, 0)
        glVertex3f(gx+69, 10, 0); glVertex3f(gx+72, 10, 0)
        glVertex3f(gx+72, BOT-5, 0); glVertex3f(gx+69, BOT-5, 0)
        glEnd()
        glColor3f(0.1, 0.1, 0.15)

    cx2, cy2 = W//2, (H + BOT) // 2
    glColor3f(0.0, 1.0, 0.6)
    glBegin(GL_QUADS)
    glVertex3f(cx2-28, cy2-2, 0); glVertex3f(cx2+28, cy2-2, 0)
    glVertex3f(cx2+28, cy2+2, 0); glVertex3f(cx2-28, cy2+2, 0)
    glEnd()
    glBegin(GL_QUADS)
    glVertex3f(cx2-2, cy2-28, 0); glVertex3f(cx2+2, cy2-28, 0)
    glVertex3f(cx2+2, cy2+28, 0); glVertex3f(cx2-2, cy2+28, 0)
    glEnd()
    glColor3f(1.0, 1.0, 0.0)
    glBegin(GL_QUADS)
    glVertex3f(cx2-4, cy2-4, 0); glVertex3f(cx2+4, cy2-4, 0)
    glVertex3f(cx2+4, cy2+4, 0); glVertex3f(cx2-4, cy2+4, 0)
    glEnd()

    glEnable(GL_DEPTH_TEST)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    draw_steering_wheel()


# ═══════════════════════════════════════════════
#  Feature 1: CAMERA
# ═══════════════════════════════════════════════


#  three gluLookAt configurations — multiplayer top-down, third-person behind ship,
#            first-person inside cockpit looking forward along heading
def setup_camera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(90, 1.25, 0.1, 8000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if multiplayer:
        # Fixed high top-down 2D-style view so both players are always visible
        mid_x = (ship_x + p2_x) / 2.0
        mid_y = (ship_y + p2_y) / 2.0   # no z axis for 2d 
        gluLookAt(mid_x, mid_y - 200, 1500,   # eye: a bit lower
                  mid_x, mid_y,       0,       # look at midpoint of both ships
                  0,     1,           0)       # up = +y (north)
    elif camera_mode == 0: # 3d angle in the normal mode
        dx, dy = get_forward(ship_angle)
        cam_x = ship_x - dx * 450
        cam_y = ship_y - dy * 450
        gluLookAt(cam_x, cam_y, 320,
                  ship_x, ship_y, ship_z,
                  0, 0, 1)
    else:
        dx, dy = get_forward(ship_angle)
        gluLookAt(ship_x,          ship_y,          ship_z + 50,
                  ship_x + dx*500, ship_y + dy*500, ship_z + 20,
                  0, 0, 1)


# ═══════════════════════════════════════════════
#  HUD
# ═══════════════════════════════════════════════
def draw_hud():
    if camera_mode == 1:
        draw_cockpit_overlay()
        draw_text_col(135, 100, "HEALTH", 0.4, 1.0, 0.4, GLUT_BITMAP_HELVETICA_12)
        draw_bar(130, 80, 120, 14, player_hp / 10.0, 0.2, 0.9, 0.2)
        draw_text_col(135, 65, f"{player_hp}/10", 0.7, 1.0, 0.7, GLUT_BITMAP_HELVETICA_12)
        draw_text_col(730, 100, "FUEL", 1.0, 0.75, 0.1, GLUT_BITMAP_HELVETICA_12)
        draw_bar(725, 80, 120, 14, fuel / 100.0, 0.9, 0.65, 0.1)
        draw_text_col(730, 65, f"{fuel:.0f}%", 1.0, 0.85, 0.4, GLUT_BITMAP_HELVETICA_12)
        draw_text_col(780, 745, f"SCORE  {score}", 1.0, 1.0, 0.5)
        if invincible:
            draw_text_col(350, 745, f"*** INVINCIBLE {invincible_timer}s ***", 0.3, 1.0, 1.0)
        if boost_active:
            draw_text_col(430, 745, ">>> BOOST <<<", 1.0, 0.6, 0.1)
        draw_text_col(340, 20, "[RMB]=3rd  SPACE=Boost  V=Auto  C=Invincible", 0.6, 0.6, 0.7,
                      GLUT_BITMAP_HELVETICA_12)
    else:
        bx = 60
        draw_bar(bx, 762, 170, 15, player_hp / 10.0,        0.2, 0.9, 0.2, "HP",   True)
        draw_bar(bx, 740, 170, 15, fuel / 100.0,             0.9, 0.65, 0.1,"FUEL", True)
        draw_bar(bx, 718, 170, 15, bullet_count/MAX_BULLETS, 0.1, 0.75, 1.0,"AMMO", True)
        draw_bar(bx, 696, 170, 15, laser_uses/MAX_LASERS,    0.9, 0.2, 0.8, "LASR", True)

        if boost_cooldown > 0:
            draw_bar(bx, 674, 170, 15,
                     1.0 - boost_cooldown / BOOST_COOLDOWN,
                     0.9, 0.45, 0.0, "BOST", False)
        elif boost_active:
            draw_bar(bx, 674, 170, 15,
                     boost_timer / BOOST_DURATION,
                     1.0, 0.7, 0.0, "BOST", False)

        draw_text_col(840, 775, f"SCORE", 0.7, 0.7, 0.8)
        draw_text_col(830, 748, f"{score}", 1.0, 1.0, 0.4, GLUT_BITMAP_TIMES_ROMAN_24)

        if invincible:
            draw_text_col(240, 762, f"INVINCIBLE  {invincible_timer}s", 0.3, 1.0, 1.0)
        if boost_active:
            draw_text_col(240, 740, ">>> BOOST <<<", 1.0, 0.6, 0.0)
        if auto_fire:
            draw_text_col(240, 718, "[AUTO-FIRE ON]", 1.0, 0.9, 0.2)

        draw_text_col(10, 20,
            "ARROWS=Move  A/S/D/F=Guns  SPACE=Boost  V=Auto  C=Invincible  B=+Ammo  P=Pause",
            0.5, 0.5, 0.6, GLUT_BITMAP_HELVETICA_12)

    if paused:
        draw_text_col(390, 420, "-- PAUSED --", 1.0, 1.0, 0.5, GLUT_BITMAP_TIMES_ROMAN_24)

    # Multiplayer HUD (always drawn when MP active)
    draw_mp_hud()

    if game_over:
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, 1000, 0, 800)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glDisable(GL_DEPTH_TEST)
        glColor3f(0.0, 0.0, 0.05)
        glBegin(GL_QUADS)
        glVertex3f(280, 290, 0); glVertex3f(720, 290, 0)
        glVertex3f(720, 490, 0); glVertex3f(280, 490, 0)
        glEnd()
        glColor3f(0.8, 0.1, 0.1)
        glBegin(GL_LINES)
        glVertex3f(280, 290, 0); glVertex3f(720, 290, 0)
        glVertex3f(720, 290, 0); glVertex3f(720, 490, 0)
        glVertex3f(720, 490, 0); glVertex3f(280, 490, 0)
        glVertex3f(280, 490, 0); glVertex3f(280, 290, 0)
        glEnd()
        glEnable(GL_DEPTH_TEST)
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        draw_text_col(345, 450, "GAME  OVER", 1.0, 0.2, 0.2, GLUT_BITMAP_TIMES_ROMAN_24)
        draw_text_col(310, 410, f"Final Score :  {score}", 1.0, 1.0, 0.4, GLUT_BITMAP_TIMES_ROMAN_24)
        draw_text_col(355, 368, "Press  R  to Restart", 0.8, 0.8, 0.9)
        draw_text_col(360, 340, "Press  ESC  to Quit",  0.6, 0.6, 0.7)


# ═══════════════════════════════════════════════
#  Feature 6: MULTIPLAYER (Player 2 — mini support ship)
# ═══════════════════════════════════════════════
# All P2 state lives here — touches nothing in P1 code
multiplayer        = False          # M toggles this
p2_active          = False          # False once P2 HP hits 0
p2_x               = 200.0          # start offset from P1
p2_y               = -300.0
p2_z               = 30.0
p2_angle           = 90.0
p2_tilt            = 0.0
p2_target_tilt     = 0.0
p2_hp              = 6              # P2 has 6 HP
p2_bullet_count    = 150
p2_bullets         = []             # separate bullet list
P2_BULLET_SPEED    = 14
P2_SHIP_SPEED      = 12
MP_DURATION        = 40             # seconds P2 stays
mp_timer_start     = 0              # glutGet time when MP activated
mp_seconds_left    = MP_DURATION


def draw_p2_ship(x, y, z, angle, tilt):
        #Mini support ship for Player 2.
        #Same shape as P1 but scaled to 0.45 (smaller) and coloured orange/gold.
    
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(angle - 90, 0, 0, 1)
    glRotatef(tilt, 0, 1, 0)
    glScalef(0.45, 0.45, 0.45)          # noticeably smaller than P1 (0.75)

    q = gluNewQuadric()

    # Fuselage — orange tint
    glColor3f(1.0, 0.55, 0.1)
    glPushMatrix()
    glRotatef(90, 1, 0, 0)
    gluCylinder(q, 12, 8, 80, 14, 5)
    glPopMatrix()

    glColor3f(0.9, 0.5, 0.1)
    glBegin(GL_QUADS)
    glVertex3f(-8, -30, 12); glVertex3f(8, -30, 12)
    glVertex3f(8,   50, 10); glVertex3f(-8, 50, 10)
    glEnd()

    # Cockpit — yellow
    glColor3f(1.0, 0.9, 0.3)
    glPushMatrix()
    glTranslatef(0, 55, 8)
    gluSphere(q, 11, 12, 10)
    glPopMatrix()

    # Nose
    glColor3f(0.95, 0.75, 0.3)
    glPushMatrix()
    glTranslatef(0, 75, 5)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(q, 8, 0.5, 35, 12, 4)
    glPopMatrix()

    # Left wing — amber
    glColor3f(0.85, 0.45, 0.05)
    glBegin(GL_QUADS)
    glVertex3f(-12,  40,  4); glVertex3f(-90,  -5,  1)
    glVertex3f(-90, -25,  1); glVertex3f(-12, -30,  4)
    glEnd()
    glColor3f(0.7, 0.35, 0.05)
    glBegin(GL_QUADS)
    glVertex3f(-12,  40,  3); glVertex3f(-90,  -5,  0)
    glVertex3f(-90, -25,  0); glVertex3f(-12, -30,  3)
    glEnd()

    # Right wing
    glColor3f(0.85, 0.45, 0.05)
    glBegin(GL_QUADS)
    glVertex3f( 12,  40,  4); glVertex3f( 90,  -5,  1)
    glVertex3f( 90, -25,  1); glVertex3f( 12, -30,  4)
    glEnd()
    glColor3f(0.7, 0.35, 0.05)
    glBegin(GL_QUADS)
    glVertex3f( 12,  40,  3); glVertex3f( 90,  -5,  0)
    glVertex3f( 90, -25,  0); glVertex3f( 12, -30,  3)
    glEnd()

    # Left booster
    glColor3f(0.8, 0.5, 0.15)
    glPushMatrix()
    glTranslatef(-22, 10, 2)
    glRotatef(90, 1, 0, 0)
    gluCylinder(q, 7, 5, 65, 10, 3)
    glPopMatrix()

    # Right booster
    glPushMatrix()
    glTranslatef(22, 10, 2)
    glRotatef(90, 1, 0, 0)
    gluCylinder(q, 7, 5, 65, 10, 3)
    glPopMatrix()

    # Engine block
    glColor3f(0.3, 0.18, 0.05)
    glPushMatrix()
    glTranslatef(0, -28, 2)
    glutSolidCube(22)
    glPopMatrix()

    # Nozzles + idle fire
    glColor3f(0.45, 0.3, 0.1)
    for ex in [-9, 0, 9]:
        glPushMatrix()
        glTranslatef(ex, -40, 2)
        glRotatef(90, 1, 0, 0)
        gluCylinder(q, 6, 4, 14, 8, 2)
        glPopMatrix()
    # Tiny flame
    glColor3f(1.0, 0.55, 0.0)
    for ex in [-9, 0, 9]:
        glPushMatrix()
        glTranslatef(ex, -54, 2)
        glRotatef(180, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 4, 0, 14, 6, 2)
        glPopMatrix()

    # Single forward gun (TAB key)
    glColor3f(0.6, 0.4, 0.1)
    glPushMatrix()
    glTranslatef(0, 70, 2)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(q, 2.5, 1.5, 40, 7, 2)
    glPopMatrix()
    glColor3f(1.0, 0.8, 0.0)
    glPushMatrix()
    glTranslatef(0, 110, 2)
    gluSphere(q, 3.5, 6, 6)
    glPopMatrix()

    glPopMatrix()

#  TAB fires P2 bullet using P2's current heading
def fire_p2_gun():   #TAB — P2 fires a single bullet forward.
    global p2_bullet_count
    if p2_bullet_count <= 0 or not p2_active:
        return
    p2_bullet_count -= 1
    dx, dy = get_forward(p2_angle)
    p2_bullets.append({
        'x': p2_x + dx * 40, 'y': p2_y + dy * 40, 'z': p2_z,
        'dx': dx, 'dy': dy, 'dz': 0,
        'life': 120
    })

#  P2 bullets moved independently; hit shared aliens/asteroids lists, add to score
def update_p2_bullets():
    dead = []
    for b in p2_bullets:
        b['x'] += b['dx'] * P2_BULLET_SPEED
        b['y'] += b['dy'] * P2_BULLET_SPEED
        b['z'] += b['dz'] * P2_BULLET_SPEED
        b['life'] -= 1
        if b['life'] <= 0:      #if bullet gets ouside range appends on used bullet list
            dead.append(b)
    for b in dead:
        if b in p2_bullets:
            p2_bullets.remove(b)

    # P2 bullets hit aliens
    global score
    for al in aliens[:]:
        for b in p2_bullets[:]:
            if dist2d(al['x'], al['y'], b['x'], b['y']) < 40 and abs(al['z'] - b['z']) < 40:
                al['hp'] -= 1      #euledian helps to check collsion beyween bullet and alien
                if b in p2_bullets:
                    p2_bullets.remove(b)
                if al['hp'] <= 0:
                    if al in aliens:
                        aliens.remove(al)
                    score += 10      #hitting increases score
                break

    # P2 bullets hit asteroids
    for ast in asteroids[:]:
        for b in p2_bullets[:]:
            if dist2d(ast['x'], ast['y'], b['x'], b['y']) < 50 and abs(ast['z'] - b['z']) < 40:
                ast['hits'] += 1  #euledian helps to check collsion beyween bullet and alien
                if b in p2_bullets:
                    p2_bullets.remove(b)
                if ast['hits'] >= 3:
                    if ast in asteroids:
                        asteroids.remove(ast)
                    score += 5
                break


def draw_p2_bullets():
    q = gluNewQuadric()
    for b in p2_bullets:
        glPushMatrix()
        glTranslatef(b['x'], b['y'], b['z'])
        glColor3f(1.0, 0.85, 0.0)    # gold bullets — distinct from P1 orange
        ang = math.degrees(math.atan2(b['dy'], b['dx']))
        glPushMatrix()
        glRotatef(ang - 90, 0, 0, 1)
        glRotatef(90, 1, 0, 0)
        gluCylinder(q, 4, 2.5, 40, 8, 2)
        glPopMatrix()
        gluSphere(q, 6, 6, 6)
        glPopMatrix()

# Feature 6: 40s countdown via glutGet; P2 collision damages p2_hp; timer end auto-deactivates
def update_multiplayer():
    #Called every idle frame when multiplayer is active.
    #Counts down the 40-second timer.
    #P2 takes damage from alien/asteroid collisions.
    #If timer runs out or M pressed again → deactivate.
    global multiplayer, p2_active, p2_hp, mp_seconds_left, game_over

    if not multiplayer:   # multiplayer not active
        return

    elapsed_ms = glutGet(GLUT_ELAPSED_TIME) - mp_timer_start #elapsed time used so that time goes naturally,not in a instant
    mp_seconds_left = max(0, MP_DURATION - int(elapsed_ms / 1000))

    # Time's up → end multiplayer
    if mp_seconds_left <= 0:
        deactivate_multiplayer()
        return

    if not p2_active:
        return

    # Alien collisions with P2
    for al in aliens[:]:
        if dist2d(al['x'], al['y'], p2_x, p2_y) < 40: #euledian helps to check collsion beyween ship and alien
            p2_hp -= 1
            if al in aliens:
                aliens.remove(al)
            if p2_hp <= 0:  #p2 health 0,it dissapears
                p2_active = False   # P2 disappears; P1 continues
            return

    # Asteroid collisions with P2
    for ast in asteroids[:]:
        if dist2d(ast['x'], ast['y'], p2_x, p2_y) < 45: #euledian helps to check collsion beyween ship and astroid
            p2_hp -= 2
            if ast in asteroids:
                asteroids.remove(ast)
            if p2_hp <= 0:
                p2_active = False
            return

#  spawns P2 beside P1; resets P2 state
def activate_multiplayer():
    global multiplayer, p2_active, p2_x, p2_y, p2_z
    global p2_angle, p2_tilt, p2_target_tilt
    global p2_hp, p2_bullet_count, mp_timer_start, mp_seconds_left
    multiplayer      = True
    p2_active        = True
    p2_x             = ship_x + 200
    p2_y             = ship_y
    p2_z             = ship_z
    p2_angle         = ship_angle
    p2_tilt          = 0.0
    p2_target_tilt   = 0.0
    p2_hp            = 6
    p2_bullet_count  = 150
    p2_bullets.clear()
    mp_timer_start   = glutGet(GLUT_ELAPSED_TIME)
    mp_seconds_left  = MP_DURATION

#  clears P2 state and bullets
def deactivate_multiplayer():
    global multiplayer, p2_active
    multiplayer = False
    p2_active   = False
    p2_bullets.clear()


def draw_mp_hud():
    #Extra HUD bars for Player 2 — shown on right side when multiplayer active
    if not multiplayer:
        return
    rx = 820   # right-side x for P2 bars (label sits right of bar, so shift left)
    draw_text_col(rx - 20, 762, "P2", 1.0, 0.75, 0.2, GLUT_BITMAP_HELVETICA_12)
    if p2_active:
        draw_bar(rx, 762, 120, 14, p2_hp / 6.0,               1.0, 0.6, 0.1, "", True)
        draw_bar(rx, 740, 120, 14, p2_bullet_count / 150.0,    0.9, 0.8, 0.1, "", True)
        draw_text_col(rx - 20, 740, "BU", 1.0, 0.75, 0.2, GLUT_BITMAP_HELVETICA_12)
        draw_text_col(rx - 20, 762, "HP", 1.0, 0.75, 0.2, GLUT_BITMAP_HELVETICA_12)
    else:
        draw_text_col(rx, 762, "P2 DOWN", 0.9, 0.3, 0.1)

    # Timer countdown
    draw_text_col(rx, 718, f"MP: {mp_seconds_left}s", 1.0, 0.85, 0.3, GLUT_BITMAP_HELVETICA_12)


# ═══════════════════════════════════════════════
#  RESET
# ═══════════════════════════════════════════════
def reset_game():
    global ship_x, ship_y, ship_z, ship_angle, ship_tilt, target_tilt
    global bullet_count, laser_uses, bullets, bullet_add_count
    global score, player_hp, game_over, paused
    global aliens, alien_timer, alien_speed_multiplier
    global asteroids, asteroid_timer
    global fuel, fuel_containers, fuel_spawn_timer
    global boost_active, boost_timer, boost_cooldown
    global auto_fire, auto_fire_timer
    global invincible, invincible_timer, invincible_pulse, invincible_start_time
    global canon_cooldown, game_state

    ship_x, ship_y, ship_z = 0.0, -300.0, 30.0
    ship_angle  = 90.0
    ship_tilt   = 0.0
    target_tilt = 0.0
    bullet_count     = MAX_BULLETS
    laser_uses       = MAX_LASERS
    bullet_add_count = 0
    bullets.clear()
    score     = 0
    player_hp = 10
    game_over = False
    paused    = False
    aliens.clear()
    alien_timer            = 0
    alien_speed_multiplier = 1.0
    asteroids.clear()
    asteroid_timer        = 0
    fuel                  = 100.0
    fuel_containers.clear()
    fuel_spawn_timer      = 0
    boost_active          = False
    boost_timer           = 0
    boost_cooldown        = 0
    auto_fire             = False
    auto_fire_timer       = 0
    invincible            = False
    invincible_timer      = 0
    invincible_pulse      = 0
    invincible_start_time = 0
    canon_cooldown        = 0
    game_state            = 'playing'
    # reset multiplayer
    deactivate_multiplayer()
    global p2_hp, p2_bullet_count, mp_seconds_left
    p2_hp           = 6
    p2_bullet_count = 150
    mp_seconds_left = MP_DURATION


# ═══════════════════════════════════════════════
#  GLUT CALLBACKS
# ═══════════════════════════════════════════════
def keyboard_listener(key, x, y):
    global paused, game_over, bullet_count, bullet_add_count, auto_fire, game_state

    # ── Intro screen: only ENTER starts the game ──
    if game_state == 'intro':
        if key == b'\r' or key == b'\n':   # Enter
            game_state = 'playing'
        elif key == b'\x1b':
            glutLeaveMainLoop()
        glutPostRedisplay()
        return

    if key == b'r':
        reset_game()
    elif key == b'p':
        paused = not paused
    elif key == b'\x1b':
        glutLeaveMainLoop()
    elif not game_over and not paused:
        if key == b'a':
            fire_left_gun()
        elif key == b's':
            fire_middle_gun()
        elif key == b'd':
            fire_right_gun()
        elif key == b'f':
            fire_canon()
        elif key == b' ':
            activate_boost()
        elif key == b'v':
            auto_fire = not auto_fire
        elif key == b'b':
            if bullet_add_count < 4:
                bullet_count = min(MAX_BULLETS, bullet_count + 10)
                bullet_add_count += 1
        elif key == b'c':
            toggle_invincible()
        elif key == b'm':
            if multiplayer:
                deactivate_multiplayer()
            else:
                activate_multiplayer()
        elif key == b'\t':          # TAB — P2 shoots
            fire_p2_gun()
        # ── Player 2 movement (I/J/K/L) ──
        elif key == b'i' and multiplayer and p2_active:
            global p2_x, p2_y, p2_angle, p2_tilt, p2_target_tilt
            dx2, dy2 = get_forward(p2_angle)
            A2 = ARENA_SIZE - 60
            p2_x = max(-A2, min(A2, p2_x + dx2 * P2_SHIP_SPEED))
            p2_y = max(-A2, min(A2, p2_y + dy2 * P2_SHIP_SPEED))
        elif key == b'k' and multiplayer and p2_active:
            dx2, dy2 = get_forward(p2_angle)
            A2 = ARENA_SIZE - 60
            p2_x = max(-A2, min(A2, p2_x - dx2 * P2_SHIP_SPEED))
            p2_y = max(-A2, min(A2, p2_y - dy2 * P2_SHIP_SPEED))
        elif key == b'j' and multiplayer and p2_active:
            p2_angle += 8
        elif key == b'l' and multiplayer and p2_active:
            p2_angle -= 8
    glutPostRedisplay()


def special_key_listener(key, x, y):
    global ship_x, ship_y, ship_angle, ship_tilt, target_tilt
    if game_state == 'intro':
        return
    if game_over or paused:
        return
    A = ARENA_SIZE - 60
    spd = SHIP_SPEED * 3 if boost_active else SHIP_SPEED

    if key == GLUT_KEY_LEFT:
        ship_angle += 8
        target_tilt = -20
    elif key == GLUT_KEY_RIGHT:
        ship_angle -= 8
        target_tilt = 20
    elif key == GLUT_KEY_UP:
        dx, dy = get_forward(ship_angle)
        ship_x = max(-A, min(A, ship_x + dx * spd))
        ship_y = max(-A, min(A, ship_y + dy * spd))
        target_tilt = 0
    elif key == GLUT_KEY_DOWN:
        dx, dy = get_forward(ship_angle)
        ship_x = max(-A, min(A, ship_x - dx * spd))
        ship_y = max(-A, min(A, ship_y - dy * spd))
        target_tilt = 0
    else:
        target_tilt = 0

    ship_tilt += (target_tilt - ship_tilt) * 0.3
    glutPostRedisplay()


def mouse_listener(button, state, x, y):
    global camera_mode
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        if not multiplayer:   # block camera switch in multiplayer mode
            camera_mode = 1 - camera_mode
    glutPostRedisplay()


def idle():
    global ship_tilt, target_tilt
    ship_tilt += (target_tilt - ship_tilt) * 0.08
    if game_state == 'playing' and not game_over and not paused:
        update_bullets()
        update_aliens()
        update_asteroids()
        update_fuel()
        update_boost()
        update_auto_fire()
        update_invincible()
        if multiplayer:
            update_multiplayer()
            update_p2_bullets()
    glutPostRedisplay()


def show_screen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    glLoadIdentity()
    glViewport(0, 0, 1600, 850)

    setup_camera()

    # Always draw the world (intro shows it behind the overlay)
    draw_stars()
    draw_floor()
    draw_walls()
    draw_planets()

    if game_state == 'intro':
        # Draw a lone ship at default position for the intro background
        draw_ship(ship_x, ship_y, ship_z, ship_angle, ship_tilt)
        draw_intro()
    else:
        # ── INVINCIBLE: hide ship, show ground ring zone ──
        if invincible:
            draw_invincible_zone(invincible_pulse)
        else:
            if not game_over:
                draw_ship(ship_x, ship_y, ship_z, ship_angle, ship_tilt)

        draw_bullets()
        draw_aliens()
        draw_asteroids()
        draw_fuel_containers()
        # Draw Player 2 if multiplayer active
        if multiplayer and p2_active:
            draw_p2_ship(p2_x, p2_y, p2_z, p2_angle, p2_tilt)
            draw_p2_bullets()
        draw_hud()

    glutSwapBuffers()


# ═══════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(3000, 4000)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Nova Seige")

    glutDisplayFunc(show_screen)
    glutKeyboardFunc(keyboard_listener)
    glutSpecialFunc(special_key_listener)
    glutMouseFunc(mouse_listener)
    glutIdleFunc(idle)

    glutMainLoop()


if __name__ == "__main__":
    main()