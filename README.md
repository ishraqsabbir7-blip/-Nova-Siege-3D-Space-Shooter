🚀 Nova Siege — 3D Space Shooter
Nova Siege is a 3D space shooter game developed using Python and PyOpenGL with the GLUT toolkit. The game features a fully modeled spaceship, 3D space environment, enemy aliens, asteroids, multiple weapons, fuel management, boost mechanics, temporary invincibility, auto-fire, multiple camera perspectives, and a temporary multiplayer support mode.

The project was developed as a Computer Graphics project to demonstrate concepts such as 3D transformations, camera systems, object rendering, collision detection, animation, lighting-style visual effects, HUD rendering, and real-time game loops.

🎮 Features
🌌 3D Space Environment
Large 3D combat arena

Procedurally positioned star field with multiple depth layers

Grid-based arena floor

Arena boundary walls

Multiple 3D planets:

Saturn
Neptune
Mars
Jupiter
🚀 Player Spaceship
Fully modeled 3D spaceship using OpenGL primitives
Rotational movement
Forward and backward movement
Smooth spaceship tilting while turning
Animated engine fire
Arena boundary constraints
🔫 Multiple Weapon Systems
The player has several different weapons:

Key	Weapon	Description
A	Left Laser	Fires a laser from the left side of the ship
S	Middle Shot	Fires the primary forward projectile
D	Triple Shot	Fires multiple projectiles
F	Cannon Arc	Fires a cannon-style attack
The game starts with a large ammunition pool and a separate limited supply of laser uses.

👾 Enemy Aliens
Aliens spawn dynamically inside the arena
Enemies move through the environment
Enemy collisions affect player health
Destroying an alien increases the player's score
☄️ Asteroids
Asteroids spawn dynamically
Asteroids require multiple hits to destroy
Asteroids use collision detection against the player and projectiles
Destroying an asteroid awards points
⛽ Fuel System
Player fuel continuously decreases during gameplay
Fuel containers spawn inside the arena
Shooting a fuel container restores fuel
Running out of fuel ends the game
⚡ Boost System
Temporary high-speed movement
Automatically moves the spaceship forward
Has a limited duration
Consumes fuel faster while active
Includes a cooldown period
🛡️ Invincibility Mode
Temporarily protects the player
Hides the spaceship while active
Displays a pulsing energy ring around the player
Includes a countdown timer
🔄 Auto-Fire
Toggle auto-fire with V
Automatically fires the middle weapon at regular intervals
👥 Multiplayer Support
The game includes a temporary Player 2 support mode.

Player 2:

Appears as a smaller support spaceship
Has independent movement
Has separate ammunition
Can shoot enemies and asteroids
Has its own HP
Shares the main player's score
Automatically disappears when the multiplayer timer expires or Player 2 loses all HP
Multiplayer mode lasts for 40 seconds per activation.

🎥 Camera Modes
Two camera perspectives are available:

Third-person / chase-style camera
Cockpit-style camera
The right mouse button switches between camera modes during normal gameplay.

🕹️ Controls
Player 1
Key	Action
↑	Move forward
↓	Move backward
←	Rotate left
→	Rotate right
A	Left laser
S	Middle shot
D	Triple shot
F	Cannon arc
SPACE	Activate boost
V	Toggle auto-fire
C	Toggle invincibility
B	Add ammunition
P	Pause / Resume
R	Restart game
M	Toggle multiplayer
ESC	Quit
Player 2
Player 2 becomes available after pressing M.

Key	Action
I	Move forward
K	Move backward
J	Rotate left
L	Rotate right
TAB	Fire weapon
Camera
Input	Action
Right Mouse Button	Switch camera mode
🧮 Game Mechanics
Player Health
The player starts with:

HP = 10
Collisions with enemies and environmental hazards reduce health. When the player's health reaches zero, the game ends.

Score
Destroying enemies and asteroids increases the score:

Alien destroyed     → +10 points
Asteroid destroyed  → +5 points
Player 2 also contributes to the shared score.

Ammunition
The player starts with:

Ammo  = 500
Lasers = 300
Additional ammunition can be collected using the B key, subject to the game's ammunition limits.

🛠️ Technologies Used
Python 3
PyOpenGL
OpenGL
GLUT / FreeGLUT
OpenGL Utility Library (GLU)
math
random
The project uses OpenGL primitives such as:

GL_QUADS
GL_LINES
GL_POINTS
OpenGL transformations
GLUquadric objects
Spheres
Cylinders
Cubes
🧠 Computer Graphics Concepts
This project demonstrates several fundamental computer graphics concepts:

3D Transformations
The game uses:

Translation
Rotation
Scaling
These transformations are used to construct and animate spaceships, planets, weapons, projectiles, and other objects.

Camera Transformation
The camera uses gluLookAt() to create different viewpoints around the player spaceship.

Perspective Rendering
The game renders a 3D environment with depth testing enabled, creating a spatial combat environment.

Collision Detection
The game uses Euclidean distance calculations for collision detection between:

Player and aliens
Player and asteroids
Bullets and aliens
Bullets and asteroids
Player 2 and enemies
Animation
Real-time animation is handled through the GLUT idle callback and continuously updates:

Projectiles
Enemy movement
Asteroids
Fuel
Boost
Invincibility effects
Player movement
Multiplayer state
HUD Rendering
A 2D HUD is rendered over the 3D environment to display:

HP
Fuel
Ammunition
Laser count
Boost status
Score
Invincibility timer
Auto-fire status
Multiplayer information
📁 Project Structure
The main Python file contains the complete game implementation, including rendering, game state management, player controls, weapons, enemies, collision detection, multiplayer functionality, HUD, and GLUT callbacks.

⚙️ Installation
1. Clone the Repository- https://github.com/ishraqsabbir7-blip/-Nova-Siege-3D-Space-Shooter/tree/main

cd PyOpenGL-Space-Shooter-Game
2. Install Python
Make sure Python 3 is installed.

Check your version:

python3 --version
3. Install PyOpenGL
pip install PyOpenGL PyOpenGL_accelerate
On Linux, you may also need FreeGLUT:

sudo apt update
sudo apt install freeglut3-dev
4. Run the Game
Because the Python filename contains spaces, run it using:

🎯 How to Play
Launch the game.

The Nova Siege intro screen will appear.

Press ENTER to start.

Use the arrow keys to navigate the spaceship.

Use the different weapon keys to attack aliens and asteroids.

Monitor your:

Health
Fuel
Ammunition
Laser supply
Collect fuel containers when necessary.

Use boost strategically to move quickly through the arena.

Activate invincibility when you need temporary protection.

Enable multiplayer with M to spawn Player 2.

Try to survive as long as possible while increasing your score.

🏆 Objective
The primary objective is to survive in the space arena, destroy enemy aliens and asteroids, manage limited resources, and achieve the highest possible score.

The game ends when the player runs out of health or fuel.

🎓 Academic Context
This project was developed as part of a Computer Graphics course project.

It focuses on applying theoretical graphics concepts to an interactive real-time application, including:

3D object modeling
Coordinate systems
Transformations
Camera manipulation
Projection
Collision detection
Animation
Real-time rendering
Interactive input handling
2D HUD over 3D scenes


📌 Project Highlights
3D Graphics
     ↓
PyOpenGL + GLUT
     ↓
3D Space Arena
     ↓
Spaceship + Enemies + Asteroids
     ↓
Weapons + Collision Detection
     ↓
Fuel + Boost + Invincibility
     ↓
Multiplayer Support
     ↓
Real-Time Gameplay
📄 License
This project is intended primarily as an academic and educational project.
