import os
from pathlib import Path
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox


# print(exeData)

class Gui():
    def __init__(self):

        # Variables
        self.heatSig = Path()
        self.exeData = bytearray
        self.texturePack = Path()
        self.packData = bytearray
        self.maxImageSize = [83385, 1622889, 5944, 580560, 939562, 747030, 217503, 1161250, 106770, 6210880, 7982484,
                             6618635, 6720609, 2828709]
        self.imageOffsets = [17737437, 18704740, 20982270, 21096616, 21830321, 22948902, 23833913, 24221384, 32663352,
                             33163764, 39374708, 47357300, 53976052, 60696692]
        self.imageStartPositions = []
        self.imageEndPositions = []
        self.imageSizes = []

        # Root
        self.root = Tk()
        self.root.title("")
        self.root.resizable(False, False)
        self.root.geometry("500x165")

        # Buttons
        self.pointToGameButton = Button(self.root, text="Point To Game", command=self.pointToGame)
        self.pointToGameButton.place(x=10, y=10)

        self.loadTexturePackButton = Button(self.root, text="Load Texture Pack", command=self.loadTexturePack)
        self.loadTexturePackButton.place(x=10, y=50)
        self.loadTexturePackButton["state"] = "disabled"

        self.applyButton = Button(self.root, text="Apply Texture Pack", command=self.installTexturePack)
        self.applyButton.place(x=10, y=90)
        self.applyButton["state"] = "disabled"

        self.removeButton = Button(self.root, text="Remove Texture Pack",
                                   command=self.uninstallTexturePack)
        self.removeButton.place(x=10, y=130)
        self.removeButton["state"] = "disabled"

        # Labels
        self.gameDirTextLabel = Label(self.root, text="Game Dir: Not Loaded")
        self.gameDirTextLabel.place(x=100, y=13)
        self.gameDirLabel = Label(self.root, text="", wraplength=390, justify="left")
        self.gameDirLabel.place(x=0, y=13)

        self.texturePackDirTextLabel = Label(self.root, text="Texture Pack Dir: Not Loaded")
        self.texturePackDirTextLabel.place(x=120, y=53)
        self.texturePackDirLabel = Label(self.root, text="", wraplength=280, justify="left")
        self.texturePackDirLabel.place(x=0, y=53)

        self.root.mainloop()

    def pointToGame(self):
        self.heatSig = filedialog.askopenfilename(filetypes=[("Heat Signature Executable", "*.exe")])
        if self.heatSig is not None:
            self.pointedToGame()
        else:
            messagebox.showerror("I'm broken", "The code broke. I dunno how.")
            self.disableEverything()

    def pointedToGame(self):
        self.heatSig = Path(self.heatSig)
        self.exeData = self.heatSig.read_bytes()
        self.pointToGameButton["state"] = "disabled"
        self.gameDirTextLabel["text"] = "Game Dir: "
        self.gameDirLabel["text"] = str(self.heatSig)
        self.gameDirLabel.place(x=155, y=13)
        self.loadTexturePackButton["state"] = "normal"
        self.removeButton["state"] = "normal"

        # Uncomment to save all the texture pages
        # for o in self.imageOffsets:
        #     newFile = Path(filedialog.asksaveasfilename(filetypes=[("Image", "*.png")]) + ".png")
        #     newFile.write_bytes(self.exeData[o: o + self.maxImageSize[self.imageOffsets.index(o)]])

    def loadTexturePack(self):
        self.texturePack = filedialog.askopenfilename(filetypes=[("Heat Signature Texture Pack", "*.HSPack")])
        if self.texturePack is not None:
            self.texturePackDirTextLabel["text"] = "Texture Pack Dir: "
            self.texturePackDirLabel["text"] = str(self.texturePack)
            self.texturePackDirLabel.place(x=210, y=53)
            self.verifyTexturePack()
        else:
            messagebox.showerror("I'm broken", "The code broke. I dunno how.")
            self.disableEverything()

    def verifyTexturePack(self):
        self.texturePack = Path(self.texturePack)
        self.packData = self.texturePack.read_bytes()

        startPattern = b"\x89\x50\x4E\x47\x0D\x0A\x1A\x0A"
        endPattern = b"\x49\x45\x4E\x44\xAE\x42\x60\x82"

        imageAmount = re.findall(endPattern, self.packData)
        startMatches = re.finditer(startPattern, self.packData)
        endMatches = re.finditer(endPattern, self.packData)
        self.imageStartPositions = []
        self.imageEndPositions = []
        self.imageSizes = []

        self.applyButton["state"] = "normal"

        if not len(imageAmount) == 14:
            messagebox.showerror("Invalid texture pack", "The loaded texture pack is invalid")
            self.disableEverything()

        for f in startMatches:
            self.imageStartPositions.append(f.start())
        for f in endMatches:
            self.imageEndPositions.append(f.start() + 7)
        for i in range(0, 14):
            self.imageSizes.append(self.imageEndPositions[i] - self.imageStartPositions[i])

        for s in self.imageSizes:
            if s > self.maxImageSize[self.imageSizes.index(s)]:
                messagebox.showerror("Invalid texture pack",
                                     "Texture #" + str(self.imageSizes.index(s) + 1) + " is too large.")
                self.disableEverything()



    def installTexturePack(self):
        heatSigDir = self.heatSig
        images = []
        for i in range(0, 14):
            startPos = self.imageStartPositions[i]
            endPos = self.imageEndPositions[i]
            images.append(self.packData[startPos:endPos])

        os.rename(heatSigDir, str(heatSigDir) + ".original")
        patchedHeatSig = Path(heatSigDir)

        toWrite = b""
        print(self.exeData[0:self.imageOffsets[0]])
        toWrite += self.exeData[0:self.imageOffsets[0]]
        for i in range(0, 13):
            toWrite += images[i]
            if self.imageSizes[i] is not self.maxImageSize[i]:
                bytesLeftOver = self.maxImageSize[i] - self.imageSizes[i]
                toWrite += b"\x00" * bytesLeftOver
            toWrite += self.exeData[self.imageOffsets[i] + self.maxImageSize[i]:self.imageOffsets[i + 1]]
        toWrite += self.exeData[self.imageOffsets[13]:self.imageOffsets[13] + self.maxImageSize[13]]
        toWrite += self.exeData[self.imageOffsets[13] + self.maxImageSize[13]:]

        patchedHeatSig.write_bytes(toWrite)

        messagebox.showinfo("Success!", "Successfully applied texture pack.")

    def uninstallTexturePack(self):
        heatSigDir = self.heatSig
        if Path.exists(Path(str(heatSigDir) + ".original")):
            os.remove(heatSigDir)
            os.rename(Path(str(heatSigDir) + ".original"), str(heatSigDir))
            messagebox.showinfo("Success!", "Successfully removed texture pack.")
        else:
            messagebox.showerror("Can't find the original game",
                                 "The program can't find the original game. If you very integrity of game files, " +
                                 "it'll remove any texture pack.")

    def disableEverything(self):
        self.loadTexturePackButton["state"] = "disabled"
        self.pointToGameButton["state"] = "disabled"
        self.applyButton["state"] = "disabled"
        self.removeButton["state"] = "disabled"


Gui()
