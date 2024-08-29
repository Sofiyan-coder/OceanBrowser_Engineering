#Drawing to the Screen
---
A web browser doesn’t just download a web page; it also has to show that page to the user. In the twenty-first century, that means a graphical application. So in this chapter we’ll equip our browser with a graphical user interface.

1.Creating Windows
---
Desktop and laptop computers run operating systems that provide desktop environments: windows, buttons, and a mouse. So responsibility ends up split: programs control their windows, but the desktop environment controls the screen. Therefore:

• The program asks for a new window and the desktop environment actually displays it.
• The program draws to its window and the desktop environment puts that on the screen.
• The desktop environment tells the program about clicks and key presses, and the program        responds and redraws its window.
Doing all of this by hand is a bit of a drag, so programs usually use a graphical toolkit to simplify these steps. Python comes with a graphical toolkit called Tk in the Python package tkinter. Using it is quite simple:
```ruby
import tkinter
window = tkinter.Tk()
tkinter.mainloop()
```
Here, tkinter.Tk() asks the desktop environment to create a window and returns an object that you can use to draw to the window. The tkinter.mainloop() call enters a loop that looks like this:

```ruby
while True:
    for evt in pendingEvents():
        handleEvent(evt)
    drawScreen()
```
![image](https://github.com/user-attachments/assets/2a9bc4f2-9080-4b6e-81c2-319c21bbf3e3)

Figure 1: Flowchart of an event-handling cycle.

Here, pendingEvents first asks the desktop environment for recent mouse clicks or key presses, then handleEvent calls your application to update state, and then drawScreen redraws the window. This event loop pattern (see Figure 1) is common in many applications, from web browsers to video games, because in complex graphical applications it ensures that all events are eventually handled and the screen is eventually updated.

2.Drawing to the Window
---
Our browser will draw the web page text to a canvas, a rectangular Tk widget that you can draw circles, lines, and text on. For example, you can create a canvas with Tk like this:
```ruby
window = tkinter.Tk()
canvas = tkinter.Canvas(window, width=800, height=600)
canvas.pack()
```
The first line creates the window, and the second creates the Canvas inside that window. We pass the window as an argument, so that Tk knows where to display the canvas. The other arguments define the canvas’s size; I chose 800 × 600 because that was a common old-timey monitor size. The third line is a Tk peculiarity, which positions the canvas inside the window. Tk also has widgets like buttons and dialog boxes, but our browser won’t use them: we will need finer-grained control over appearance, which a canvas provides.

To keep it all organized let’s put this code in a class:
```ruby
WIDTH, HEIGHT = 800, 600

class Browser:
    def __init__(self):
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(
            self.window, 
            width=WIDTH,
            height=HEIGHT
        )
        self.canvas.pack()
```
Once you’ve made a canvas, you can call methods that draw shapes on the canvas. Let’s do that inside load, which we’ll move into the new Browser class:
```ruby
class Browser:
    def load(self, url):
        # ...
        self.canvas.create_rectangle(10, 20, 400, 300)
        self.canvas.create_oval(100, 100, 150, 150)
        self.canvas.create_text(200, 150, text="Hi!")
```
To run this code, create a Browser, call load, and then start the Tk mainloop:
```ruby
if __name__ == "__main__":
    import sys
    Browser().load(URL(sys.argv[1]))
    tkinter.mainloop()
```
You ought to see: a rectangle, starting near the top-left corner of the canvas and ending at its center; then a circle inside that rectangle; and then the text “Hi!” next to the circle, as in Figure 2.

![image](https://github.com/user-attachments/assets/5d2cb96c-36d5-48fe-8f1b-9c031968b5f4)

Figure 2: The expected example output with a rectangle, circle, and text.


Coordinates in Tk refer to x positions from left to right and y positions from top to bottom. In other words, the bottom of the screen has larger y values, the opposite of what you might be used to from math. Play with the coordinates above to figure out what each argument refers to.

3.Laying Out Text
---
Let’s draw a simple web page on this canvas. So far, our browser steps through the web page source code character by character and prints the text (but not the tags) to the console window. Now we want to draw the characters on the canvas instead.

To start, let’s change the show function from the previous chapter into a function that I’ll call lex which just returns the textual content of an HTML document without printing it:
```ruby
def lex(body):
    text = ""
    # ...
    for c in body:
        # ...
        elif not in_tag:
            text += c
    return text
```
Then, load will draw that text, character by character:
```ruby
def load(self, url):
    # ...
    for c in text:
        self.canvas.create_text(100, 100, text=c)
```
Let’s test this code on a real web page. For reasons that might seem inscrutable, let’s test it on the first chapter of Journey to the West (https://browser.engineering/examples/xiyouji.html), a classic Chinese novel about a monkey. Run this URL through request, lex, and load. You should see a window with a big blob of black pixels inset a little from the top left corner of the window.

Why a blob instead of letters? Well, of course, because we are drawing every letter in the same place, so they all overlap! Let’s fix that:
```ruby
HSTEP, VSTEP = 13, 18
cursor_x, cursor_y = HSTEP, VSTEP
for c in text:
    self.canvas.create_text(cursor_x, cursor_y, text=c)
    cursor_x += HSTEP
```
The variables cursor_x and cursor_y point to where the next character will go, as if you were typing the text into a word processor. I picked the magic numbers—13 and 18—by trying a few different values and picking one that looked most readable.

The text now forms a line from left to right. But with an 800-pixel-wide canvas and 13 pixels per character, one line only fits about 60 characters. You need more than that to read a novel, so we also need to wrap the text once we reach the edge of the screen:
```ruby
for c in text:
    # ...
    if cursor_x >= WIDTH - HSTEP:
        cursor_y += VSTEP
        cursor_x = HSTEP
```
The code increases cursor_y and resets cursor_x once cursor_x goes past 787 pixels. The sequence is shown in Figure 3. Wrapping the text this way makes it possible to read more than a single line.

At this point you should be able to load up our example page (https://browser.engineering/examples/xiyouji.html) in your browser and have it look something like Figure 4.

![image](https://github.com/user-attachments/assets/725252f7-7964-4fb6-9157-dfebd562dcfd)

Figure 4: The first chapter of Journey to the West rendered in our browser.

Now we can read a lot of text, but still not all of it: if there’s enough text, not all of the lines will fit on the screen. We want users to scroll the page to look at different parts of it.

4.Scrolling Text
---
Scrolling introduces a layer of indirection between page coordinates (this text is 132 pixels from the top of the page) and screen coordinates (since you’ve scrolled 60 pixels down, this text is 72 pixels from the top of the screen)—see Figure 5. Generally speaking, a browser lays out the page—determines where everything on the page goes—in terms of page coordinates and then rasters the page—draws everything—in terms of screen coordinates.

![image](https://github.com/user-attachments/assets/8b613542-4454-4b59-8a32-ec20638f596b)

Figure 5: The difference between page and screen coordinates.

Our browser will have the same split. Right now load computes both the position of each character and draws it: layout and rendering. Let’s instead have a layout function to compute and store the position of each character, and a separate draw function to then draw each character based on the stored position. This way, layout can operate with page coordinates and only draw needs to think about screen coordinates.

Let’s start with layout. Instead of calling canvas.create_text on each character, let’s add it to a list, together with its position. Since layout doesn’t need to access anything in Browser, it can be a standalone function:
```ruby
def layout(text):
    display_list = []
    cursor_x, cursor_y = HSTEP, VSTEP
    for c in text:
        display_list.append((cursor_x, cursor_y, c))
        # ...
    return display_list
```
The resulting list of things to display is called a display list. Since layout is all about page coordinates, we don’t need to change anything else about it to support scrolling.

Once the display list is computed, draw needs to loop through it and draw each character. Since draw does need access to the canvas, we make it a method on Browser:
```ruby
class Browser:
    def draw(self):
        for x, y, c in self.display_list:
            self.canvas.create_text(x, y, text=c)
```
Now load just needs to call layout followed by draw:
```ruby
class Browser:
    def load(self, url):
        body = url.request()
        text = lex(body)
        self.display_list = layout(text)
        self.draw()
```
Now we can add scrolling. Let’s add a field for how far you’ve scrolled:
```ruby
class Browser:
    def __init__(self):
        # ...
        self.scroll = 0
```
The page coordinate y then has screen coordinate y - self.scroll:
```ruby
def draw(self):
    for x, y, c in self.display_list:
        self.canvas.create_text(x, y - self.scroll, text=c)
```
If you change the value of scroll the page will now scroll up and down. But how does the user change scroll?

Most browsers scroll the page when you press the up and down keys, rotate the scroll wheel, drag the scroll bar, or apply a touch gesture to the screen. To keep things simple, let’s just implement the down key.

Tk allows you to bind a function to a key, which instructs Tk to call that function when the key is pressed. For example, to bind to the down arrow key, write:
```ruby
def __init__(self):
    # ...
    self.window.bind("<Down>", self.scrolldown)
```
Here, self.scrolldown is an event handler, a function that Tk will call whenever the down arrow key is pressed. All it needs to do is increment scroll and redraw the canvas:
```ruby
SCROLL_STEP = 100

def scrolldown(self, e):
    self.scroll += SCROLL_STEP
    self.draw()
```
If you try this out, you’ll find that scrolling draws all the text a second time. That’s because we didn’t erase the old text before drawing the new text. Call canvas.delete to clear the old text:
```ruby
def draw(self):
    self.canvas.delete("all")
    # ...
```
Scrolling should now work!

5.Faster Rendering
---
Applications have to redraw page contents quickly for interactions to feel fluid, and must respond quickly to clicks and key presses so the user doesn’t get frustrated. “Feel fluid” can be made more precise. Graphical applications such as browsers typically aim to redraw at a speed equal to the refresh rate, or frame rate, of the screen, and/or a fixed 60 Hz. This means that the browser has to finish all its work in less than 1/60th of a second, or 16 ms, in order to keep up. For this reason, 16 ms is called the animation frame budget of the application.

But scrolling in our browser is pretty slow. Why? It turns out that loading information about the shape of a character, inside create_text, takes a while. To speed up scrolling we need to make sure to do it only when necessary (while at the same time ensuring the pixels on the screen are always correct).

Real browsers have a lot of quite tricky optimizations for this, but for our browser let’s limit ourselves to a simple improvement: skip drawing characters that are offscreen:
```ruby
for x, y, c in self.display_list:
    if y > self.scroll + HEIGHT: continue
    if y + VSTEP < self.scroll: continue
    # ...
```
The first if statement skips characters below the viewing window; the second skips characters above it. In that second if statement, y + VSTEP is the bottom edge of the character, because characters that are halfway inside the viewing window still have to be drawn.

Scrolling should now be pleasantly fast, and hopefully close to the 16 ms animation frame budget. And because we split layout and draw, we don’t need to change layout at all to implement this optimization.

6.Summary
---
This chapter went from a rudimentary command-line browser to a graphical user interface with text that can be scrolled. The browser now:

• talks to your operating system to create a window;
• lays out the text and draws it to that window;
• listens for keyboard commands;
• scrolls the window in response.
And here is our browser rendering this very web page (it’s fullly interactive—after clicking on it to focus, you should be able to scroll with the down arrow):


Next, we’ll make this browser work on English text, handling complexities like variable-width characters, line layout, and formatting.


7.Outline
---
The complete set of functions, classes, and methods in our browser should look something like this:
```ruby
class URL:
    def __init__(url)        WIDTH, HEIGHT        SCROLL_STEP
    def request()            HSTEP, VSTEP
    def lex(body)            def layout(text)


class Browser:
    def __init__()
    def draw()
    def load(url)
    def scrolldown(e)
```


Next, we’ll make this browser work on English text, handling complexities like variable-width characters, line layout, and formatting.
---
