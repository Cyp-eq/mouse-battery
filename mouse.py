# Import the essential modules
import rivalcfg
import pystray
from PIL import Image, ImageDraw
import os, time, threading

# Our state variables
battery_level = None
icon = None
stopped = False

# Change the time_delta to your liking
time_delta = 60 * 10  # 60s * 10 = 600s = 10min

directory = f"{os.path.dirname(os.path.realpath(__file__))}/"
image_directory = f"{directory}images/"


def get_battery():
    global stopped
    while not stopped:
        mouse = rivalcfg.get_first_mouse()
        battery = mouse.battery

        if battery["level"] is not None:
            # print(f"Mouse got {battery['level']}% juice left")
            global battery_level, icon
            battery_level = battery["level"]
            icon.icon = create_battery_icon()
            icon.menu = pystray.Menu(
                pystray.MenuItem(
                    f"Battery: {str(f'{battery_level}%' if battery_level is not None else 'N/A')}",
                    lambda: None,
                ),
                pystray.MenuItem("Quit", quit_app),
            )
            icon.title = f"Battery: {str(f'{battery_level}%' if battery_level is not None else 'N/A')}"
            icon.update_menu()
            time.sleep(time_delta)
        else:
            time.sleep(1 / 20)
    print("Stopping thread")


def create_battery_icon():
    global battery_level
    image = Image.new("RGB", (100, 100), color="white")
    draw = ImageDraw.Draw(image)

    if battery_level is not None:
        draw.rectangle((0, 0, 100, 100), fill="black")
        draw.rectangle((0, 100, 100, 100 - battery_level), fill="green")
    else:
        draw.rectangle((0, 0, 100, 100), fill="black")
        error = Image.open(f"{image_directory}error.png")
        image.paste(error, (0, 0), error)

    # load image error.png and put on top
    if battery_level is not None and battery_level < 20:
        error = Image.open(f"{image_directory}error.png")
    else:
        error = Image.open(f"{image_directory}no_error.png")
    image.paste(error, (0, 0), error)

    # replace color black with transparent
    image = image.convert("RGBA")
    data = image.getdata()
    new_data = []
    for item in data:
        if item[0] == 0 and item[1] == 0 and item[2] == 0:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)
    image.putdata(new_data)

    return image


def quit_app(icon, item):
    global stopped
    icon.stop()
    stopped = True


def main():
    global icon
    image = create_battery_icon()
    icon = pystray.Icon("Battery", icon=image, title="Battery: N/A")
    thread = threading.Thread(target=get_battery)
    thread.start()
    icon.menu = pystray.Menu(
        pystray.MenuItem(
            f"Battery: {str(f'{battery_level}%' if battery_level is not None else 'N/A')}",
            lambda: None,
        ),
        pystray.MenuItem("Quit", quit_app),
    )

    icon.run()


if __name__ == "__main__":
    main()
