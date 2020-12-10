# viewport-raytracer
Kansas State University Senior Project

https://github.com/calepovilonis/viewport-raytracer

Instructions to run:
  - install all required libaries in main.py, shapes.py with 'pip install ..." ie 'pip install pandas'.
  - when installing PyOpenGL, run 'pip install' and then the files PyOpenGL-3.1.5-cp36-cp36m-win_amd64.whl and PyOpenGL_accelerate-3.1.5-cp36-cp36m-win_amd64.whl.
    - these files may be Windows only versions, check for compatability.
  - to run, type the command 'python main.py'
  
Controls:
   - 'p' - creates plane
   - 'o' - creates sphere
   - 'c' - creates cube
   - 'r' - renders to image
   - Scroll Wheel - to change selected object
   - Middle Mouse Click - to deselect objects
   - 'm' - to enable movement
   - ',' - to enable rotations (doesn't effect ray tracing, just in viewport mode)
   - ↑ , ↓ , ← , → - to either move or rotate object, depending on the mode
   - SHIFT ↑ , ↓ - to move object up or down
   - WASD - to move the camera around the scene
   - Space - to move camera up
   - SHIFT + Space - to move camera down
   - Left mouse click and drag - to rotate camera (doesn't effect raytracing camera, just in viewport mode)
   - 'n' - to change selected object material
   - 'l' - to change light position
   - [ , ] , - , + to change scale of selected object
   - ESC - to exit program
